"""
Stock Analyzer REST API
A Flask-based API that provides AI-powered stock analysis and PDF report generation.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY2"),
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT2")
)
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT2_NAME")

# Company domain mapping for logo fetching
COMPANY_DOMAINS = {
    'AAPL': 'apple.com', 'MSFT': 'microsoft.com', 'GOOGL': 'google.com',
    'AMZN': 'amazon.com', 'NVDA': 'nvidia.com', 'META': 'meta.com',
    'TSLA': 'tesla.com', 'BRK.B': 'berkshirehathaway.com', 'JPM': 'jpmorganchase.com',
    'V': 'visa.com', 'WMT': 'walmart.com', 'MA': 'mastercard.com',
    'PG': 'pg.com', 'JNJ': 'jnj.com', 'UNH': 'unitedhealthgroup.com',
    'HD': 'homedepot.com', 'BAC': 'bankofamerica.com', 'XOM': 'exxonmobil.com',
    'CVX': 'chevron.com', 'DIS': 'disney.com', 'NFLX': 'netflix.com',
    'INTC': 'intel.com', 'AMD': 'amd.com', 'CSCO': 'cisco.com'
}


def validate_stock_symbol(stock_symbol):
    """Validate if stock symbol exists by checking Google Finance."""
    try:
        # Try both NASDAQ and NYSE
        for exchange in ['NASDAQ', 'NYSE']:
            url = f"https://www.google.com/finance/quote/{stock_symbol}:{exchange}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            # If we get a successful response and find price data, stock is valid
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                price_div = soup.find('div', {'class': 'YMlKec fxKbKc'})
                if price_div:
                    return True, exchange
        
        # Stock not found on either exchange
        return False, None
    except Exception as e:
        print(f"Error validating stock: {e}")
        return False, None


def fetch_company_logo(stock_symbol):
    """Fetch company logo from Clearbit Logo API."""
    try:
        domain = COMPANY_DOMAINS.get(stock_symbol.upper())
        if not domain:
            return None
        
        logo_url = f"https://logo.clearbit.com/{domain}"
        response = requests.get(logo_url, timeout=5)
        
        if response.status_code == 200:
            return BytesIO(response.content)
        return None
    except Exception as e:
        print(f"Error fetching logo: {e}")
        return None


def fetch_news_urls(stock_symbol, max_articles=10):
    """Fetch news article URLs from StockAnalysis.com."""
    try:
        stock_symbol = stock_symbol.strip().upper()
        url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # Filter for news article URLs
            if (href and title and len(title) > 20 and 
                any(domain in href for domain in ['marketwatch.com', 'cnbc.com', 'reuters.com', 
                                                   'forbes.com', 'barrons.com', 'benzinga.com',
                                                   'fool.com', 'bloomberg.com', 'invezz.com'])):
                
                source = href.split('/')[2].replace('www.', '') if '/' in href else 'Unknown'
                news_links.append({
                    'title': title,
                    'url': href,
                    'source': source
                })
                
                if len(news_links) >= max_articles:
                    break
        
        print(f"Found {len(news_links)} news articles")
        return news_links[:max_articles]
    except Exception as e:
        print(f"Error fetching news URLs: {e}")
        return []


def fetch_article_content(url):
    """Fetch and extract article content from URL."""
    try:
        # Use different headers for different sites
        if 'reuters.com' in url:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            }
        elif 'marketwatch.com' in url or 'barrons.com' in url:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text from paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        
        # Limit to first 2000 characters
        return text[:2000] if text else None
        
    except Exception as e:
        print(f"Error fetching article {url}: {e}")
        return None


def fetch_forecast_data(stock_symbol):
    """Fetch analyst forecast data from StockAnalysis.com."""
    try:
        url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/forecast/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content = response.text
        forecast_data = {}
        
        analyst_match = re.search(r'(\d+)\s+analysts', content, re.IGNORECASE)
        if analyst_match:
            forecast_data['analyst_count'] = analyst_match.group(1)
        
        consensus_match = re.search(r'consensus rating.*?(Buy|Hold|Sell)', content, re.IGNORECASE)
        if consensus_match:
            forecast_data['consensus'] = consensus_match.group(1)
        
        price_target_match = re.search(r'\$(\d+\.?\d*)\s*price target', content, re.IGNORECASE)
        if price_target_match:
            forecast_data['price_target'] = f"${price_target_match.group(1)}"
        
        return forecast_data if forecast_data else None
    except Exception as e:
        print(f"Error fetching forecast data: {e}")
        return None


def fetch_historical_data(stock_symbol, days=30):
    """Fetch historical stock data from StockAnalysis.com."""
    try:
        url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/history/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return []
        
        historical_data = []
        rows = table.find_all('tr')[1:days+1]
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                try:
                    historical_data.append({
                        'date': cols[0].get_text(strip=True),
                        'open': cols[1].get_text(strip=True),
                        'high': cols[2].get_text(strip=True),
                        'low': cols[3].get_text(strip=True),
                        'close': cols[4].get_text(strip=True)
                    })
                except Exception:
                    continue
        
        return historical_data
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return []


def fetch_stock_data(stock_symbol):
    """Fetch current stock data from Google Finance."""
    try:
        url = f"https://www.google.com/finance/quote/{stock_symbol}:NASDAQ"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        price_div = soup.find('div', {'class': 'YMlKec fxKbKc'})
        price = price_div.get_text(strip=True) if price_div else "N/A"
        
        stock_data = {
            'symbol': stock_symbol.upper(),
            'price': price,
            'change': 'N/A',
            'percent_change': 'N/A',
            'market_cap': 'N/A',
            'pe_ratio': 'N/A',
            'dividend_yield': 'N/A'
        }
        
        data_divs = soup.find_all('div', {'class': 'P6K39c'})
        for div in data_divs:
            text = div.get_text(strip=True)
            if 'Market cap' in text:
                stock_data['market_cap'] = text.split('Market cap')[1].strip()
            elif 'P/E ratio' in text:
                stock_data['pe_ratio'] = text.split('P/E ratio')[1].strip()
            elif 'Dividend yield' in text:
                stock_data['dividend_yield'] = text.split('Dividend yield')[1].strip()
        
        return stock_data
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None


def generate_analysis(stock_data, historical_data, news_data, forecast_data=None):
    """Generate AI-powered stock analysis using Azure OpenAI."""
    try:
        # Format comprehensive context
        summary_text = f"""STOCK: {stock_data.get('symbol', 'N/A')}
Current Price: {stock_data.get('price', 'N/A')}
Market Cap: {stock_data.get('market_cap', 'N/A')}
P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}
"""
        
        # Add analyst forecasts
        if forecast_data:
            summary_text += f"\nANALYST FORECASTS:\n"
            for key, value in forecast_data.items():
                summary_text += f"{key}: {value}\n"
        
        # Add historical data with all daily prices
        if historical_data and len(historical_data) > 0:
            summary_text += f"\n30-DAY PRICE HISTORY:\n"
            for day in historical_data:
                summary_text += f"{day['date']}: Open ${day['open']}, Close ${day['close']}, High ${day['high']}, Low ${day['low']}\n"
            first_close = historical_data[-1]['close'] if len(historical_data) > 1 else historical_data[0]['close']
            last_close = historical_data[0]['close']
            summary_text += f"Month-over-month change: ${first_close} → ${last_close}\n"
        
        # Add news headlines and content
        if news_data:
            summary_text += f"\nRECENT NEWS ({len(news_data)} articles):\n"
            for i, article in enumerate(news_data, 1):
                summary_text += f"{i}. {article['title']}\n"
                summary_text += f"   Source: {article['source']}\n"
                if article.get('content'):
                    summary_text += f"   Content: {article['content'][:500]}...\n"
        
        # Generate all analyses
        analyses = {}
        
        # Short Summary (2-3 sentences)
        short_prompt = """You are a financial analyst. Create a very brief summary (2-3 sentences) of the stock's current status.
Focus only on: current price movement, market cap, and overall sentiment."""
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": short_prompt},
                {"role": "user", "content": f"Summarize this stock data briefly:\n\n{summary_text[:1000]}"}
            ],
            max_completion_tokens=200
        )
        analyses['short_summary'] = response.choices[0].message.content
        
        # Executive Summary (8-12 sentences)
        exec_prompt = """You are a senior financial analyst creating executive summaries for investors. 
Provide a comprehensive, professional summary that includes:
1. Current stock performance and valuation
2. Recent price trends and volatility analysis
3. Key news themes and market sentiment
4. Strategic implications and outlook
5. Risk factors and opportunities

IMPORTANT: Format for PDF export - use clear paragraphs, NO tables or special characters. Use simple bullet points with dashes (-) if needed.
Keep the summary concise (8-12 sentences) but insightful."""
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": exec_prompt},
                {"role": "user", "content": f"Create an executive summary for investors:\n\n{summary_text}"}
            ],
            max_completion_tokens=800
        )
        analyses['executive_summary'] = response.choices[0].message.content
        
        # Detailed Analysis with News Impact
        detailed_prompt = """You are a senior equity research analyst. Provide a detailed analysis that includes:

1. STOCK PERFORMANCE ANALYSIS
   - Detailed examination of price movements over the past week
   - Volatility patterns and trading ranges
   - Technical levels and support/resistance

2. NEWS IMPACT ASSESSMENT
   - Analyze each major news article (mention source name) and its specific impact on stock price
   - Identify correlation between news events and price movements
   - Assess market reaction and sentiment shifts
   - **IMPORTANT FOR PDF**: Write in narrative paragraph format, NOT tables
   - For each news event, write: "On [Date], [News Event from Source] caused [Price Movement], reflecting [Market Sentiment]"
   - Use actual dates and specific price changes (e.g., "+$3.09", "close $288.62")

3. FUNDAMENTAL ANALYSIS
   - Valuation metrics interpretation (P/E, market cap, etc.)
   - Comparison to sector peers and historical norms
   - Growth prospects and earnings outlook

4. RISK-REWARD ANALYSIS
   - Key risks: regulatory, competitive, macro-economic
   - Catalysts and opportunities
   - Near-term and long-term outlook

IMPORTANT: Format for PDF export - use clear paragraphs and narrative style. NO tables, NO special formatting. Use simple dashes (-) for bullet points if needed.
Be specific about how news events correlate with stock price changes. Use actual dates and prices from the data."""
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": detailed_prompt},
                {"role": "user", "content": f"Provide a detailed analysis with news impact assessment:\n\n{summary_text}"}
            ],
            max_completion_tokens=1500
        )
        analyses['detailed_analysis'] = response.choices[0].message.content
        
        # Investment Recommendations
        recommendation_prompt = """You are a senior investment advisor. Based on all available data, provide detailed BUY/SELL/HOLD recommendations for three different time horizons.

IMPORTANT: Format for PDF export - use clear section headers and paragraphs. NO tables, NO complex formatting.

1. ONE WEEK (Short-term trading)
   - Recommendation: BUY/SELL/HOLD (with confidence level: High/Medium/Low)
   - Detailed Reasoning: Include technical indicators, momentum analysis, news sentiment impact, short-term catalysts
   - Entry Price Target (if applicable)
   - Exit/Stop-Loss Levels
   - Position Size Suggestion (% of portfolio)
   - Key Triggers to Watch (specific events, price levels)
   - Risk Assessment (what could go wrong)

2. SIX MONTHS (Medium-term investment)
   - Recommendation: BUY/SELL/HOLD (with confidence level: High/Medium/Low)
   - Detailed Reasoning: Include fundamental analysis, analyst consensus alignment, business outlook, earnings expectations
   - Price Target Range (conservative to optimistic)
   - Critical Milestones (earnings dates, product launches, regulatory decisions)
   - Valuation Assessment (fair value vs current price)
   - Risk/Reward Ratio
   - Portfolio Allocation Suggestion

3. TWO YEARS (Long-term investment)
   - Recommendation: BUY/SELL/HOLD (with confidence level: High/Medium/Low)
   - Detailed Reasoning: Strategic positioning, competitive moat, growth trajectory, industry trends, management quality
   - Long-term Price Target Range
   - Major Risks and Mitigation Strategies
   - Key Opportunities and Growth Drivers
   - Competitive Advantage Assessment
   - Recommended Investment Approach (DCA, lump sum, etc.)

For each time horizon, provide comprehensive analysis with specific numbers, dates, and actionable insights.
Be highly specific and data-driven. Reference actual prices, analyst forecasts, recent news events, and historical patterns.
Include what-if scenarios and contingency plans."""
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": recommendation_prompt},
                {"role": "user", "content": f"Provide comprehensive investment recommendations for different time horizons:\n\n{summary_text}"}
            ],
            max_completion_tokens=2000
        )
        analyses['recommendations'] = response.choices[0].message.content
        
        # Analyst Ratings
        analyst_prompt = """You are synthesizing analyst research. Based on the analyst forecast data provided, create a comprehensive analyst ratings summary.

IMPORTANT: Format for PDF export - use clear paragraphs and narrative style. NO tables, NO special formatting. Use simple dashes (-) for lists.

1. ANALYST CONSENSUS OVERVIEW
   - Overall consensus rating and what it means
   - Number of analysts covering the stock
   - Distribution of ratings (if available: Strong Buy, Buy, Hold, Sell, Strong Sell)
   - Recent changes in analyst sentiment

2. PRICE TARGET ANALYSIS
   - Average price target and implied upside/downside
   - Price target range (low to high)
   - How current price compares to targets
   - Bull case vs Bear case scenarios

3. KEY ANALYST PERSPECTIVES (create representative analyst views based on the data)
   Create 3-5 representative institutional analyst perspectives from major firms like:
   - Morgan Stanley, Goldman Sachs, J.P. Morgan, Bank of America, Citigroup, etc.
   For each perspective include: Firm name, Rating, Price Target, Key reasoning

4. REVENUE AND EARNINGS OUTLOOK
   - Revenue growth expectations
   - Earnings projections and growth rates
   - Key drivers of future performance
   - Consensus vs actual historical performance

Use the provided forecast data to make this analysis realistic and data-driven."""
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": analyst_prompt},
                {"role": "user", "content": f"Generate comprehensive analyst ratings summary:\n\n{summary_text}"}
            ],
            max_completion_tokens=1500
        )
        analyses['analyst_ratings'] = response.choices[0].message.content
        
        return analyses
    except Exception as e:
        print(f"Error generating analysis: {e}")
        return None


def clean_text_for_pdf(text):
    """Clean text for PDF export by removing markdown tables and escaping HTML."""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        if not line.strip().startswith('|'):
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    
    return text


def generate_pdf_report(stock_data, historical_data, forecast_data, analyses, stock_symbol):
    """Generate PDF report of the stock analysis."""
    try:
        filename = f"stock_analysis_{stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Add logo if available
        logo_data = fetch_company_logo(stock_symbol)
        if logo_data:
            logo = Image(logo_data, width=1.5*inch, height=1.5*inch)
            story.append(logo)
            story.append(Spacer(1, 0.2*inch))
        
        # Title
        story.append(Paragraph(f"Stock Analysis Report: {stock_symbol}", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Stock Data Table
        story.append(Paragraph("Current Stock Information", heading_style))
        stock_table_data = [
            ['Metric', 'Value'],
            ['Symbol', stock_data['symbol']],
            ['Current Price', stock_data['price']],
            ['Market Cap', stock_data['market_cap']],
            ['P/E Ratio', stock_data['pe_ratio']],
            ['Dividend Yield', stock_data['dividend_yield']]
        ]
        
        stock_table = Table(stock_table_data, colWidths=[2.5*inch, 3.5*inch])
        stock_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(stock_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Forecast Data
        if forecast_data:
            story.append(Paragraph("Analyst Forecast", heading_style))
            forecast_text = ", ".join([f"{k}: {v}" for k, v in forecast_data.items()])
            story.append(Paragraph(forecast_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Historical Data (First 10 days)
        if historical_data:
            story.append(Paragraph("Recent Historical Data (Last 10 Days)", heading_style))
            hist_table_data = [['Date', 'Open', 'High', 'Low', 'Close']]
            for day in historical_data[:10]:
                hist_table_data.append([day['date'], day['open'], day['high'], day['low'], day['close']])
            
            hist_table = Table(hist_table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            hist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(hist_table)
            story.append(Spacer(1, 0.3*inch))
        
        # AI Analyses
        for title, key in [
            ("Short Summary", "short_summary"),
            ("Executive Summary", "executive_summary"),
            ("Detailed Analysis", "detailed_analysis"),
            ("Investment Recommendations", "recommendations"),
            ("Analyst Ratings", "analyst_ratings")
        ]:
            if key in analyses:
                story.append(Paragraph(title, heading_style))
                cleaned_text = clean_text_for_pdf(analyses[key])
                
                # Wrap Short and Executive summaries in KeepTogether
                if key in ["short_summary", "executive_summary"]:
                    content = KeepTogether([Paragraph(cleaned_text, styles['BodyText'])])
                    story.append(content)
                else:
                    story.append(Paragraph(cleaned_text, styles['BodyText']))
                
                story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer, filename
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None, None


# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """
    Analyze a stock and return JSON analysis.
    
    Request body:
    {
        "symbol": "NVDA",
        "include_pdf": false  // optional, default false
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'symbol' not in data:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        stock_symbol = data['symbol'].upper()
        include_pdf = data.get('include_pdf', False)
        
        # Validate stock symbol first (before using LLM)
        print(f"Validating stock symbol {stock_symbol}...")
        is_valid, exchange = validate_stock_symbol(stock_symbol)
        
        if not is_valid:
            return jsonify({
                'error': f'Invalid stock symbol: {stock_symbol}',
                'message': 'Please provide a valid NASDAQ or NYSE stock symbol',
                'examples': ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'GOOGL']
            }), 404
        
        print(f"✓ Valid stock found on {exchange}")
        
        # Fetch all data
        print(f"Fetching data for {stock_symbol}...")
        stock_data = fetch_stock_data(stock_symbol)
        
        if not stock_data:
            return jsonify({'error': f'Could not fetch data for {stock_symbol}'}), 404
        
        historical_data = fetch_historical_data(stock_symbol, days=30)
        news_urls = fetch_news_urls(stock_symbol, max_articles=15)
        
        # Fetch news content
        news_data = []
        for article in news_urls[:15]:
            content = fetch_article_content(article['url'])
            if content:
                news_data.append({
                    'title': article['title'],
                    'url': article['url'],
                    'source': article['source'],
                    'content': content[:500]  # First 500 chars for API response
                })
                time.sleep(1)  # Rate limiting
        
        forecast_data = fetch_forecast_data(stock_symbol)
        
        # Generate analysis
        print(f"Generating AI analysis for {stock_symbol}...")
        analyses = generate_analysis(stock_data, historical_data, news_data, forecast_data)
        
        if not analyses:
            return jsonify({'error': 'Failed to generate analysis'}), 500
        
        # Prepare response
        response_data = {
            'symbol': stock_symbol,
            'timestamp': datetime.now().isoformat(),
            'stock_data': stock_data,
            'historical_data': historical_data[:10],  # First 10 days
            'forecast_data': forecast_data,
            'news_count': len(news_data),
            'analyses': analyses
        }
        
        # Generate PDF if requested
        if include_pdf:
            pdf_buffer, pdf_filename = generate_pdf_report(
                stock_data, historical_data, forecast_data, analyses, stock_symbol
            )
            if pdf_buffer:
                response_data['pdf_available'] = True
                response_data['pdf_endpoint'] = f"/api/analyze/{stock_symbol}/pdf"
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error in analyze_stock: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze/<symbol>/pdf', methods=['GET'])
def get_stock_pdf(symbol):
    """
    Generate and download PDF report for a stock.
    """
    try:
        stock_symbol = symbol.upper()
        
        # Validate stock symbol first
        print(f"Validating stock symbol {stock_symbol}...")
        is_valid, exchange = validate_stock_symbol(stock_symbol)
        
        if not is_valid:
            return jsonify({
                'error': f'Invalid stock symbol: {stock_symbol}',
                'message': 'Please provide a valid NASDAQ or NYSE stock symbol',
                'examples': ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'GOOGL']
            }), 404
        
        print(f"✓ Valid stock found on {exchange}")
        
        # Fetch all data
        print(f"Generating PDF for {stock_symbol}...")
        stock_data = fetch_stock_data(stock_symbol)
        
        if not stock_data:
            return jsonify({'error': f'Could not fetch data for {stock_symbol}'}), 404
        
        historical_data = fetch_historical_data(stock_symbol, days=30)
        news_urls = fetch_news_urls(stock_symbol, max_articles=15)
        
        # Fetch news content
        news_data = []
        for article in news_urls[:15]:
            content = fetch_article_content(article['url'])
            if content:
                news_data.append({
                    'title': article['title'],
                    'url': article['url'],
                    'source': article['source'],
                    'content': content
                })
                time.sleep(1)
        
        forecast_data = fetch_forecast_data(stock_symbol)
        analyses = generate_analysis(stock_data, historical_data, news_data, forecast_data)
        
        if not analyses:
            return jsonify({'error': 'Failed to generate analysis'}), 500
        
        # Generate PDF
        pdf_buffer, pdf_filename = generate_pdf_report(
            stock_data, historical_data, forecast_data, analyses, stock_symbol
        )
        
        if not pdf_buffer:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_filename
        )
        
    except Exception as e:
        print(f"Error in get_stock_pdf: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/quick-summary/<symbol>', methods=['GET'])
def quick_summary(symbol):
    """
    Get a quick summary of a stock without full analysis.
    Faster endpoint for basic information.
    """
    try:
        stock_symbol = symbol.upper()
        
        # Validate stock symbol first
        is_valid, exchange = validate_stock_symbol(stock_symbol)
        
        if not is_valid:
            return jsonify({
                'error': f'Invalid stock symbol: {stock_symbol}',
                'message': 'Please provide a valid NASDAQ or NYSE stock symbol',
                'examples': ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'GOOGL']
            }), 404
        
        stock_data = fetch_stock_data(stock_symbol)
        if not stock_data:
            return jsonify({'error': f'Could not fetch data for {stock_symbol}'}), 404
        
        historical_data = fetch_historical_data(stock_symbol, days=7)
        
        return jsonify({
            'symbol': stock_symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': stock_data['price'],
            'market_cap': stock_data['market_cap'],
            'pe_ratio': stock_data['pe_ratio'],
            'recent_prices': historical_data[:7]
        }), 200
        
    except Exception as e:
        print(f"Error in quick_summary: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Stock Analyzer API...")
    print("API Endpoints:")
    print("  POST /api/analyze - Full stock analysis")
    print("  GET /api/analyze/<symbol>/pdf - Download PDF report")
    print("  GET /api/quick-summary/<symbol> - Quick stock summary")
    print("  GET /api/health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000)
