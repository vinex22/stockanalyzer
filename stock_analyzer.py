"""
Stock Price Analyzer using Google Finance and Azure OpenAI
Fetches stock data and generates AI-powered summary
"""

import requests
from bs4 import BeautifulSoup
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import re
from datetime import datetime, timedelta
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO

# Load environment variables
load_dotenv()


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


# Azure OpenAI Configuration
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT2_NAME")  # Using gpt-4.1 for summaries


def fetch_company_logo(stock_symbol):
    """
    Fetch company logo from external API
    
    Args:
        stock_symbol: Stock ticker symbol
    
    Returns:
        BytesIO object with logo image or None
    """
    try:
        # Try Clearbit Logo API (free, no key required)
        company_name = stock_symbol.lower()
        # Map common symbols to company domains
        domain_map = {
            'aapl': 'apple.com',
            'msft': 'microsoft.com',
            'googl': 'google.com',
            'goog': 'google.com',
            'amzn': 'amazon.com',
            'meta': 'meta.com',
            'tsla': 'tesla.com',
            'nvda': 'nvidia.com',
            'nflx': 'netflix.com',
            'dis': 'disney.com',
            'baba': 'alibaba.com',
            'v': 'visa.com',
            'jpm': 'jpmorganchase.com',
            'wmt': 'walmart.com',
            'pg': 'pg.com',
            'ma': 'mastercard.com',
            'hd': 'homedepot.com',
            'ko': 'coca-cola.com',
            'pep': 'pepsi.com',
            'cost': 'costco.com'
        }
        
        domain = domain_map.get(company_name, f"{company_name}.com")
        logo_url = f"https://logo.clearbit.com/{domain}"
        
        response = requests.get(logo_url, timeout=5)
        if response.status_code == 200:
            return BytesIO(response.content)
        
        return None
        
    except Exception as e:
        print(f"⚠️  Could not fetch logo: {e}")
        return None


def fetch_news_urls(stock_symbol, max_articles=10):
    """
    Fetch news article URLs from StockAnalysis.com
    
    Args:
        stock_symbol: Stock ticker symbol
        max_articles: Maximum number of articles to fetch
    
    Returns:
        List of dictionaries with article title and URL
    """
    try:
        stock_symbol = stock_symbol.strip().upper()
        url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_articles = []
        
        # Find news section links
        news_links = soup.find_all('a', href=True)
        
        for link in news_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # Filter for news article URLs
            if (href and title and len(title) > 20 and 
                any(domain in href for domain in ['marketwatch.com', 'cnbc.com', 'reuters.com', 
                                                   'forbes.com', 'barrons.com', 'benzinga.com',
                                                   'fool.com', 'bloomberg.com', 'invezz.com'])):
                
                news_articles.append({
                    'title': title,
                    'url': href,
                    'source': href.split('/')[2] if '/' in href else 'Unknown'
                })
                
                if len(news_articles) >= max_articles:
                    break
        
        print(f"✅ Found {len(news_articles)} news articles")
        return news_articles
        
    except Exception as e:
        print(f"❌ Error fetching news URLs: {e}")
        return []


def fetch_article_content(url):
    """
    Fetch article content from a news URL
    
    Args:
        url: Article URL
    
    Returns:
        Article text content or None
    """
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
        return None


def generate_executive_summary(stock_data, historical_data, news_data, forecast_data=None):
    """
    Generate comprehensive summaries using Azure OpenAI based on all collected data
    
    Args:
        stock_data: Current stock information
        historical_data: Historical price data
        news_data: News articles with content
        forecast_data: Analyst forecasts and price targets
    
    Returns:
        Dictionary with short_summary, executive_summary, and detailed_analysis
    """
    try:
        # Format stock data
        summary_text = f"""STOCK: {stock_data.get('symbol', 'N/A')}
Current Price: {stock_data.get('current_price', 'N/A')}
Change: {stock_data.get('price_change', 'N/A')} ({stock_data.get('percent_change', 'N/A')})
Market Cap: {stock_data.get('market_cap', 'N/A')}
P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
"""
        
        # Add analyst forecasts
        if forecast_data:
            summary_text += f"\nANALYST FORECASTS:\n"
            if 'num_analysts' in forecast_data:
                summary_text += f"Number of Analysts: {forecast_data['num_analysts']}\n"
            if 'analyst_consensus' in forecast_data:
                summary_text += f"Consensus Rating: {forecast_data['analyst_consensus']}\n"
            if 'avg_price_target' in forecast_data:
                summary_text += f"Average Price Target: ${forecast_data['avg_price_target']}"
                if 'upside_percent' in forecast_data:
                    summary_text += f" ({forecast_data['upside_percent']}% upside)\n"
                else:
                    summary_text += "\n"
            if 'low_price_target' in forecast_data and 'high_price_target' in forecast_data:
                summary_text += f"Price Target Range: ${forecast_data['low_price_target']} - ${forecast_data['high_price_target']}\n"
            if 'revenue_this_year' in forecast_data:
                summary_text += f"Revenue Forecast (This Year): {forecast_data['revenue_this_year']}\n"
            if 'revenue_next_year' in forecast_data:
                summary_text += f"Revenue Forecast (Next Year): {forecast_data['revenue_next_year']}\n"
            if 'eps_this_year' in forecast_data:
                summary_text += f"EPS Forecast (This Year): {forecast_data['eps_this_year']}\n"
            if 'eps_next_year' in forecast_data:
                summary_text += f"EPS Forecast (Next Year): {forecast_data['eps_next_year']}\n"
        
        # Add historical trend with all daily prices
        if historical_data and len(historical_data) > 0:
            summary_text += f"\n30-DAY PRICE HISTORY:\n"
            for day in historical_data:
                summary_text += f"{day['date']}: Open ${day['open']}, Close ${day['close']}, High ${day['high']}, Low ${day['low']}\n"
            first_close = historical_data[-1]['close']
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
        
        # Generate Short Summary (2-3 sentences)
        short_prompt = """You are a financial analyst. Create a very brief summary (2-3 sentences) of the stock's current status.
Focus only on: current price movement, market cap, and overall sentiment."""
        
        short_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": short_prompt},
                {"role": "user", "content": f"Summarize this stock data briefly:\n\n{summary_text[:1000]}"}
            ],
            max_completion_tokens=200
        )
        short_summary = short_response.choices[0].message.content
        
        # Generate Executive Summary (8-12 sentences)
        exec_prompt = """You are a senior financial analyst creating executive summaries for investors. 
Provide a comprehensive, professional summary that includes:
1. Current stock performance and valuation
2. Recent price trends and volatility analysis
3. Key news themes and market sentiment
4. Strategic implications and outlook
5. Risk factors and opportunities

IMPORTANT: Format for PDF export - use clear paragraphs, NO tables or special characters. Use simple bullet points with dashes (-) if needed.
Keep the summary concise (8-12 sentences) but insightful."""
        
        exec_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": exec_prompt},
                {"role": "user", "content": f"Create an executive summary for investors:\n\n{summary_text}"}
            ],
            max_completion_tokens=800
        )
        executive_summary = exec_response.choices[0].message.content
        
        # Generate Detailed Analysis with News Impact
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
        
        detailed_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": detailed_prompt},
                {"role": "user", "content": f"Provide a detailed analysis with news impact assessment:\n\n{summary_text}"}
            ],
            max_completion_tokens=1500
        )
        detailed_analysis = detailed_response.choices[0].message.content
        
        # Generate Buy/Sell Recommendations
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
        
        recommendation_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": recommendation_prompt},
                {"role": "user", "content": f"Provide comprehensive investment recommendations for different time horizons:\n\n{summary_text}"}
            ],
            max_completion_tokens=2000
        )
        recommendations = recommendation_response.choices[0].message.content
        
        # Generate Analyst Ratings Summary
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
   Since we don't have individual analyst names, create 3-5 representative institutional analyst perspectives:
   - Bullish Analyst View: Name a typical bullish firm (e.g., "Morgan Stanley", "Goldman Sachs") and their reasoning
   - Neutral Analyst View: Name a typical neutral firm (e.g., "J.P. Morgan", "Bank of America") and their reasoning  
   - Bearish Analyst View (if applicable): Name a typical bearish firm and their concerns
   
   For each perspective include:
   - Firm name (use realistic major investment banks/research firms)
   - Rating (Buy/Hold/Sell)
   - Price target
   - Key reasoning points
   - Main concerns or catalysts

4. REVENUE & EARNINGS OUTLOOK
   - Revenue forecasts for this year and next year
   - EPS forecasts for this year and next year
   - Growth expectations
   - How these compare to historical performance

Be specific and professional. Use the actual forecast data provided but create realistic analyst perspectives around it."""
        
        analyst_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": analyst_prompt},
                {"role": "user", "content": f"Create analyst ratings summary:\n\n{summary_text}"}
            ],
            max_completion_tokens=1500
        )
        analyst_ratings = analyst_response.choices[0].message.content
        
        return {
            'short_summary': short_summary,
            'executive_summary': executive_summary,
            'detailed_analysis': detailed_analysis,
            'recommendations': recommendations,
            'analyst_ratings': analyst_ratings
        }
        
    except Exception as e:
        print(f"❌ Error generating summaries: {e}")
        return None


def fetch_forecast_data(stock_symbol):
    """
    Fetch analyst forecasts and price targets from StockAnalysis.com
    
    Args:
        stock_symbol: Stock ticker symbol
    
    Returns:
        Dictionary with forecast data or None
    """
    try:
        stock_symbol = stock_symbol.strip().upper()
        url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/forecast/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        forecast_data = {}
        
        # Try to extract key forecast metrics from the page text
        text = soup.get_text()
        
        # Extract price target
        price_target_match = re.search(r'average price target of \$([\d,\.]+)', text)
        if price_target_match:
            forecast_data['avg_price_target'] = price_target_match.group(1)
        
        # Extract price range
        low_target_match = re.search(r'lowest target is \$([\d,\.]+)', text)
        high_target_match = re.search(r'highest is \$([\d,\.]+)', text)
        if low_target_match:
            forecast_data['low_price_target'] = low_target_match.group(1)
        if high_target_match:
            forecast_data['high_price_target'] = high_target_match.group(1)
        
        # Extract analyst consensus
        consensus_match = re.search(r'consensus rating of "([^"]+)"', text)
        if consensus_match:
            forecast_data['analyst_consensus'] = consensus_match.group(1)
        
        # Extract number of analysts
        analysts_match = re.search(r'(\d+) analysts that cover', text)
        if analysts_match:
            forecast_data['num_analysts'] = analysts_match.group(1)
        
        # Extract revenue forecast
        revenue_this_year = re.search(r'Revenue This Year([\d\.]+)B', text)
        revenue_next_year = re.search(r'Revenue Next Year([\d\.]+)B', text)
        if revenue_this_year:
            forecast_data['revenue_this_year'] = revenue_this_year.group(1) + 'B'
        if revenue_next_year:
            forecast_data['revenue_next_year'] = revenue_next_year.group(1) + 'B'
        
        # Extract EPS forecast
        eps_this_year = re.search(r'EPS This Year([\d\.]+)', text)
        eps_next_year = re.search(r'EPS Next Year([\d\.]+)', text)
        if eps_this_year:
            forecast_data['eps_this_year'] = eps_this_year.group(1)
        if eps_next_year:
            forecast_data['eps_next_year'] = eps_next_year.group(1)
        
        # Extract upside percentage
        upside_match = re.search(r'forecasts a ([\d\.]+)% increase', text)
        if upside_match:
            forecast_data['upside_percent'] = upside_match.group(1)
        
        if forecast_data:
            print(f"✅ Fetched analyst forecast data")
            return forecast_data
        else:
            print("⚠️  Could not parse forecast data")
            return None
        
    except Exception as e:
        print(f"⚠️  Error fetching forecast data: {e}")
        return None


def fetch_historical_data(stock_symbol, days=7):
    """
    Fetch historical stock data for the last N days from StockAnalysis.com
    
    Args:
        stock_symbol: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
        days: Number of days of historical data to fetch
    
    Returns:
        List of dictionaries containing daily open/close data
    """
    try:
        stock_symbol = stock_symbol.strip().upper()
        
        # StockAnalysis.com historical prices URL
        url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/history/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for historical price table or data
        historical_data = []
        
        # Try to find table with historical data
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            # Check if this looks like a price history table
            if len(rows) > 1:
                header_row = rows[0]
                headers = [th.text.strip().lower() for th in header_row.find_all('th')]
                
                # Look for date, open, close columns
                if 'date' in headers or any('open' in h for h in headers):
                    for row in rows[1:days+1]:  # Skip header, get first N rows
                        cols = row.find_all('td')
                        if len(cols) >= 5:
                            try:
                                date = cols[0].text.strip()
                                open_price = cols[1].text.strip().replace('$', '').replace(',', '')
                                high_price = cols[2].text.strip().replace('$', '').replace(',', '')
                                low_price = cols[3].text.strip().replace('$', '').replace(',', '')
                                close_price = cols[4].text.strip().replace('$', '').replace(',', '')
                                
                                historical_data.append({
                                    'date': date,
                                    'open': open_price,
                                    'high': high_price,
                                    'low': low_price,
                                    'close': close_price
                                })
                            except (ValueError, IndexError, AttributeError):
                                continue
                    
                    if historical_data:
                        break
        
        if historical_data:
            print(f"✅ Fetched {len(historical_data)} days of historical data from StockAnalysis.com")
            return historical_data
        else:
            print("⚠️  Could not parse historical data from StockAnalysis.com")
            return None
        
    except Exception as e:
        print(f"⚠️  Error fetching from StockAnalysis.com: {e}")
        return None


def fetch_stock_data(stock_symbol):
    """
    Fetch stock price data from Google Finance
    
    Args:
        stock_symbol: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
    
    Returns:
        Dictionary containing stock data or None if failed
    """
    try:
        # Clean up stock symbol
        stock_symbol = stock_symbol.strip().upper()
        
        # Google Finance URL
        url = f"https://www.google.com/finance/quote/{stock_symbol}:NASDAQ"
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract stock data
        stock_data = {
            'symbol': stock_symbol,
            'url': url
        }
        
        # Try to find current price (Google Finance uses specific div classes)
        price_div = soup.find('div', class_='YMlKec fxKbKc')
        if price_div:
            stock_data['current_price'] = price_div.text.strip()
        
        # Try to find price change
        change_div = soup.find('div', class_='JwB6zf')
        if change_div:
            stock_data['price_change'] = change_div.text.strip()
        
        # Try to find percentage change
        percent_divs = soup.find_all('div', class_='NydbP tnNmPe')
        if len(percent_divs) >= 2:
            stock_data['percent_change'] = percent_divs[1].text.strip()
        
        # Try to extract additional metrics
        # Previous close
        prev_close = soup.find('div', string='Previous close')
        if prev_close:
            prev_value = prev_close.find_next('div', class_='P6K39c')
            if prev_value:
                stock_data['previous_close'] = prev_value.text.strip()
        
        # Day range
        day_range = soup.find('div', string='Day range')
        if day_range:
            range_value = day_range.find_next('div', class_='P6K39c')
            if range_value:
                stock_data['day_range'] = range_value.text.strip()
        
        # Year range
        year_range = soup.find('div', string='52-week range') or soup.find('div', string='52 week range')
        if year_range:
            year_value = year_range.find_next('div', class_='P6K39c')
            if year_value:
                stock_data['year_range'] = year_value.text.strip()
        
        # Market cap
        mkt_cap = soup.find('div', string='Market cap')
        if mkt_cap:
            cap_value = mkt_cap.find_next('div', class_='P6K39c')
            if cap_value:
                stock_data['market_cap'] = cap_value.text.strip()
        
        # PE Ratio
        pe_ratio = soup.find('div', string='P/E ratio')
        if pe_ratio:
            pe_value = pe_ratio.find_next('div', class_='P6K39c')
            if pe_value:
                stock_data['pe_ratio'] = pe_value.text.strip()
        
        # Dividend yield
        dividend = soup.find('div', string='Dividend yield')
        if dividend:
            div_value = dividend.find_next('div', class_='P6K39c')
            if div_value:
                stock_data['dividend_yield'] = div_value.text.strip()
        
        # Try to get company name
        title = soup.find('title')
        if title:
            # Extract company name from title (format: "AAPL - Apple Inc - NASDAQ Stock")
            title_text = title.text
            parts = title_text.split(' - ')
            if len(parts) >= 2:
                stock_data['company_name'] = parts[1].strip()
        
        return stock_data
    
    except requests.RequestException as e:
        print(f"❌ Error fetching stock data: {e}")
        return None
    except Exception as e:
        print(f"❌ Error parsing stock data: {e}")
        return None


def generate_stock_summary(stock_data, historical_data=None):
    """
    Use Azure OpenAI to generate a summary of the stock data
    
    Args:
        stock_data: Dictionary containing stock information
        historical_data: List of dictionaries containing historical data
    
    Returns:
        AI-generated summary string
    """
    try:
        # Format the stock data for the LLM
        data_text = f"Stock Symbol: {stock_data.get('symbol', 'N/A')}\n"
        
        if 'company_name' in stock_data:
            data_text += f"Company Name: {stock_data['company_name']}\n"
        
        if 'current_price' in stock_data:
            data_text += f"Current Price: {stock_data['current_price']}\n"
        
        if 'price_change' in stock_data:
            data_text += f"Price Change: {stock_data['price_change']}\n"
        
        if 'percent_change' in stock_data:
            data_text += f"Percentage Change: {stock_data['percent_change']}\n"
        
        if 'previous_close' in stock_data:
            data_text += f"Previous Close: {stock_data['previous_close']}\n"
        
        if 'day_range' in stock_data:
            data_text += f"Day Range: {stock_data['day_range']}\n"
        
        if 'year_range' in stock_data:
            data_text += f"52-Week Range: {stock_data['year_range']}\n"
        
        if 'market_cap' in stock_data:
            data_text += f"Market Cap: {stock_data['market_cap']}\n"
        
        if 'pe_ratio' in stock_data:
            data_text += f"P/E Ratio: {stock_data['pe_ratio']}\n"
        
        if 'dividend_yield' in stock_data:
            data_text += f"Dividend Yield: {stock_data['dividend_yield']}\n"
        
        # Add historical data if available
        if historical_data and len(historical_data) > 0:
            data_text += f"\nLast 7 Trading Days (Open -> Close):\n"
            for day in historical_data:
                data_text += f"{day['date']}: ${day['open']} -> ${day['close']} (High: ${day['high']}, Low: ${day['low']})\n"
        
        # Create the prompt
        system_prompt = """You are a financial analyst assistant. Provide a concise, insightful summary 
of stock data including recent trends from historical data. Focus on key metrics, price trends, and what they 
might indicate about the stock's performance. Keep the summary brief (4-6 sentences) and easy to understand."""
        
        user_prompt = f"""Please provide a brief summary and analysis of this stock data:

{data_text}

Include observations about:
- Current price performance (up or down)
- Week-over-week trend based on the 7-day data
- Price volatility (based on ranges and daily movements)
- Overall market positioning (if market cap available)
- Any notable patterns or metrics that stand out"""
        
        # Call Azure OpenAI
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=300
        )
        
        content = response.choices[0].message.content
        return content
    
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return None


def generate_pdf_report(stock_data, historical_data, forecast_data, summaries, stock_symbol):
    """
    Generate a professional PDF report of the stock analysis
    """
    def clean_text_for_pdf(text):
        """Clean and escape text for PDF generation, removing tables"""
        import html
        import re
        
        # Remove markdown tables (lines starting with |)
        lines = text.split('\n')
        cleaned_lines = []
        in_table = False
        
        for line in lines:
            stripped = line.strip()
            # Detect table rows
            if stripped.startswith('|') and '|' in stripped[1:]:
                in_table = True
                continue
            elif in_table and not stripped:
                in_table = False
                continue
            elif in_table:
                continue
            else:
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Escape HTML special characters first
        text = html.escape(text)
        # Replace **text** with <b>text</b>
        text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
        # Remove any remaining asterisks
        text = text.replace('*', '')
        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Replace newlines with <br/>
        text = text.replace('\n', '<br/>')
        return text
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_analysis_{stock_symbol}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=1*inch, bottomMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=8
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        )
        
        # Title
        # Try to add company logo
        logo_data = fetch_company_logo(stock_symbol)
        if logo_data:
            try:
                logo = Image(logo_data, width=1.5*inch, height=1.5*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"⚠️  Could not add logo to PDF: {e}")
        
        story.append(Paragraph(f"Stock Analysis Report: {stock_symbol}", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Stock Data Summary
        story.append(Paragraph("Stock Data Summary", heading_style))
        
        stock_info = [
            ['Metric', 'Value'],
            ['Symbol', stock_data.get('symbol', 'N/A')],
            ['Current Price', stock_data.get('current_price', 'N/A')],
            ['Change', f"{stock_data.get('price_change', 'N/A')} ({stock_data.get('percent_change', 'N/A')})"],
            ['Market Cap', stock_data.get('market_cap', 'N/A')],
            ['P/E Ratio', stock_data.get('pe_ratio', 'N/A')],
            ['Dividend Yield', stock_data.get('dividend_yield', 'N/A')]
        ]
        
        table = Table(stock_info, colWidths=[2.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Analyst Forecasts
        if forecast_data:
            story.append(Paragraph("Analyst Forecasts", heading_style))
            forecast_text = f"""
            <b>Analyst Coverage:</b> {forecast_data.get('num_analysts', 'N/A')} analysts<br/>
            <b>Consensus Rating:</b> {forecast_data.get('analyst_consensus', 'N/A')}<br/>
            <b>Average Price Target:</b> ${forecast_data.get('avg_price_target', 'N/A')} 
            ({forecast_data.get('upside_percent', 'N/A')}% upside)<br/>
            <b>Price Target Range:</b> ${forecast_data.get('low_price_target', 'N/A')} - 
            ${forecast_data.get('high_price_target', 'N/A')}
            """
            story.append(Paragraph(forecast_text, body_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Historical Data (first 10 days)
        if historical_data and len(historical_data) > 0:
            story.append(Paragraph("Recent Price History (Last 10 Days)", heading_style))
            hist_data = [['Date', 'Open', 'Close', 'High', 'Low']]
            for day in historical_data[:10]:
                hist_data.append([
                    day['date'],
                    f"${day['open']}",
                    f"${day['close']}",
                    f"${day['high']}",
                    f"${day['low']}"
                ])
            
            hist_table = Table(hist_data, colWidths=[1.3*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch])
            hist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
            ]))
            story.append(hist_table)
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Short Summary
        short_section = []
        short_section.append(Paragraph("Short Summary", heading_style))
        cleaned_short = clean_text_for_pdf(summaries['short_summary'])
        short_section.append(Paragraph(cleaned_short, body_style))
        short_section.append(Spacer(1, 0.2*inch))
        story.append(KeepTogether(short_section))
        
        story.append(PageBreak())
        
        # Executive Summary
        exec_section = []
        exec_section.append(Paragraph("Executive Summary", heading_style))
        exec_paragraphs = summaries['executive_summary'].split('\n\n')
        for para in exec_paragraphs:
            if para.strip():
                cleaned_para = clean_text_for_pdf(para)
                exec_section.append(Paragraph(cleaned_para, body_style))
        exec_section.append(Spacer(1, 0.2*inch))
        story.append(KeepTogether(exec_section))
        
        story.append(PageBreak())
        
        # Detailed Analysis
        story.append(Paragraph("Detailed Analysis - News Impact on Stock Price", heading_style))
        detail_paragraphs = summaries['detailed_analysis'].split('\n\n')
        for para in detail_paragraphs:
            if para.strip():
                cleaned_para = clean_text_for_pdf(para)
                story.append(Paragraph(cleaned_para, body_style))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Investment Recommendations
        story.append(Paragraph("Investment Recommendations", heading_style))
        rec_paragraphs = summaries['recommendations'].split('\n\n')
        for para in rec_paragraphs:
            if para.strip():
                cleaned_para = clean_text_for_pdf(para)
                story.append(Paragraph(cleaned_para, body_style))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Analyst Ratings
        story.append(Paragraph("Analyst Ratings & Recommendations", heading_style))
        analyst_paragraphs = summaries['analyst_ratings'].split('\n\n')
        for para in analyst_paragraphs:
            if para.strip():
                cleaned_para = clean_text_for_pdf(para)
                story.append(Paragraph(cleaned_para, body_style))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            f"Data Source: {stock_data.get('url', 'Google Finance')}",
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        print(f"\n✅ PDF Report generated: {filename}")
        return filename
        
    except Exception as e:
        print(f"\n❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to run the stock analyzer"""
    print("=" * 60)
    print("📈 STOCK PRICE ANALYZER")
    print("=" * 60)
    print()
    
    # Ask user for stock symbol
    stock_symbol = input("Enter stock symbol (e.g., NVDA, AAPL, MSFT, TSLA): ").strip().upper()
    
    if not stock_symbol:
        print("❌ No stock symbol entered. Exiting.")
        return
    
    print()
    print(f"🔍 Validating stock symbol {stock_symbol}...")
    
    # Validate stock symbol first (before using LLM)
    is_valid, exchange = validate_stock_symbol(stock_symbol)
    
    if not is_valid:
        print()
        print("=" * 60)
        print(f"❌ ERROR: Invalid stock symbol '{stock_symbol.upper()}'")
        print("=" * 60)
        print("Please use a valid NASDAQ or NYSE stock symbol.")
        print("Examples: NVDA, AAPL, MSFT, TSLA, GOOGL, META")
        print("=" * 60)
        return
    
    print(f"✅ Valid stock found on {exchange}")
    print()
    print(f"🔍 Fetching data for {stock_symbol.upper()}...")
    print()
    
    # Fetch current stock data
    stock_data = fetch_stock_data(stock_symbol)
    
    if not stock_data or 'current_price' not in stock_data:
        print(f"❌ Could not fetch data for {stock_symbol.upper()}")
        print("   Please verify the stock symbol is valid and traded on NASDAQ.")
        print("   Try popular stocks like: AAPL, MSFT, GOOGL, TSLA, NVDA, META")
        return
    
    # Fetch historical data
    print("📅 Fetching 30-day historical data...")
    historical_data = fetch_historical_data(stock_symbol, days=30)
    
    # Fetch analyst forecasts
    print("📊 Fetching analyst forecasts...")
    forecast_data = fetch_forecast_data(stock_symbol)
    
    # Display raw data
    print()
    print("📊 STOCK DATA:")
    print("-" * 60)
    
    if 'company_name' in stock_data:
        print(f"Company: {stock_data['company_name']}")
    
    print(f"Symbol: {stock_data['symbol']}")
    
    if 'current_price' in stock_data:
        print(f"Current Price: {stock_data['current_price']}")
    
    if 'price_change' in stock_data:
        change = stock_data['price_change']
        emoji = "📈" if not change.startswith('-') else "📉"
        print(f"Change: {emoji} {change}")
    
    if 'percent_change' in stock_data:
        print(f"Percentage Change: {stock_data['percent_change']}")
    
    if 'previous_close' in stock_data:
        print(f"Previous Close: {stock_data['previous_close']}")
    
    if 'day_range' in stock_data:
        print(f"Day Range: {stock_data['day_range']}")
    
    if 'year_range' in stock_data:
        print(f"52-Week Range: {stock_data['year_range']}")
    
    if 'market_cap' in stock_data:
        print(f"Market Cap: {stock_data['market_cap']}")
    
    if 'pe_ratio' in stock_data:
        print(f"P/E Ratio: {stock_data['pe_ratio']}")
    
    if 'dividend_yield' in stock_data:
        print(f"Dividend Yield: {stock_data['dividend_yield']}")
    
    # Display historical data
    if historical_data and len(historical_data) > 0:
        print()
        print(f"📅 LAST {len(historical_data)} TRADING DAYS:")
        print("-" * 60)
        print(f"{'Date':<12} {'Open':<12} {'Close':<12} {'High':<12} {'Low':<12}")
        print("-" * 60)
        # Show first 10 and last 10 if more than 20 days
        if len(historical_data) > 20:
            for day in historical_data[:10]:
                print(f"{day['date']:<12} ${day['open']:<11} ${day['close']:<11} ${day['high']:<11} ${day['low']:<11}")
            print(f"{'...':<12} {'...':<12} {'...':<12} {'...':<12} {'...':<12}")
            for day in historical_data[-10:]:
                print(f"{day['date']:<12} ${day['open']:<11} ${day['close']:<11} ${day['high']:<11} ${day['low']:<11}")
        else:
            for day in historical_data:
                print(f"{day['date']:<12} ${day['open']:<11} ${day['close']:<11} ${day['high']:<11} ${day['low']:<11}")
    else:
        print()
        print("⚠️  Could not fetch historical data")
    
    print()
    print("🤖 Generating AI Summary...")
    print()
    
    # Generate AI summary with historical data
    summary = generate_stock_summary(stock_data, historical_data)
    
    if summary and summary != "None":
        print("💡 AI ANALYSIS:")
        print("-" * 60)
        print(summary)
    else:
        print("❌ Could not generate AI summary")
        if summary == "None":
            print("   (Model returned 'None' - possible content filtering or refusal)")
    
    # Display analyst forecasts
    if forecast_data:
        print()
        print("=" * 60)
        print("📈 ANALYST FORECASTS & PRICE TARGETS")
        print("=" * 60)
        print()
        
        if 'num_analysts' in forecast_data and 'analyst_consensus' in forecast_data:
            print(f"Analyst Coverage: {forecast_data['num_analysts']} analysts")
            print(f"Consensus Rating: {forecast_data['analyst_consensus']}")
        
        if 'avg_price_target' in forecast_data:
            print(f"\\nAverage Price Target: ${forecast_data['avg_price_target']}", end='')
            if 'upside_percent' in forecast_data:
                print(f" ({forecast_data['upside_percent']}% upside potential)")
            else:
                print()
        
        if 'low_price_target' in forecast_data and 'high_price_target' in forecast_data:
            print(f"Price Target Range: ${forecast_data['low_price_target']} - ${forecast_data['high_price_target']}")
        
        if 'revenue_this_year' in forecast_data or 'revenue_next_year' in forecast_data:
            print(f"\\nRevenue Forecasts:")
            if 'revenue_this_year' in forecast_data:
                print(f"  This Year: {forecast_data['revenue_this_year']}")
            if 'revenue_next_year' in forecast_data:
                print(f"  Next Year: {forecast_data['revenue_next_year']}")
        
        if 'eps_this_year' in forecast_data or 'eps_next_year' in forecast_data:
            print(f"\\nEPS Forecasts:")
            if 'eps_this_year' in forecast_data:
                print(f"  This Year: ${forecast_data['eps_this_year']}")
            if 'eps_next_year' in forecast_data:
                print(f"  Next Year: ${forecast_data['eps_next_year']}")
    
    # Fetch and analyze news
    print()
    print("=" * 60)
    print("📰 FETCHING NEWS ARTICLES...")
    print("=" * 60)
    print()
    
    news_articles = fetch_news_urls(stock_symbol, max_articles=15)
    
    if news_articles:
        print()
        print(f"📄 Fetching content from {len(news_articles)} articles...")
        print()
        
        for i, article in enumerate(news_articles, 1):
            print(f"{i}. {article['title'][:80]}...")
            print(f"   Source: {article['source']}")
            
            # Fetch article content
            content = fetch_article_content(article['url'])
            if content:
                article['content'] = content
                print(f"   ✅ Content fetched ({len(content)} chars)")
            else:
                print(f"   ⚠️  Could not fetch content")
            print()
            time.sleep(1)  # Be polite to servers
        
        # Generate executive summary
        print()
        print("=" * 60)
        print("📊 GENERATING COMPREHENSIVE ANALYSIS")
        print("=" * 60)
        print()
        
        summaries = generate_executive_summary(stock_data, historical_data, news_articles, forecast_data)
        
        if summaries:
            # Display Short Summary
            print("\n" + "=" * 80)
            print("📝 SHORT SUMMARY")
            print("=" * 80)
            print()
            # Wrap text nicely
            summary_lines = summaries['short_summary'].split('\n')
            for line in summary_lines:
                if line.strip():
                    print(f"  {line}")
            print()
            
            # Display Executive Summary
            print("\n" + "=" * 80)
            print("📊 EXECUTIVE SUMMARY")
            print("=" * 80)
            print()
            # Format with indentation for readability
            exec_lines = summaries['executive_summary'].split('\n')
            for line in exec_lines:
                if line.strip():
                    if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                        print(f"\n{line}")
                    else:
                        print(f"  {line}")
            print()
            
            # Display Detailed Analysis
            print("\n" + "=" * 80)
            print("🔍 DETAILED ANALYSIS - NEWS IMPACT ON STOCK PRICE")
            print("=" * 80)
            print()
            # Format with proper sections and indentation
            detail_lines = summaries['detailed_analysis'].split('\n')
            for line in detail_lines:
                if line.strip():
                    # Headers and section titles
                    if any(header in line.upper() for header in ['STOCK PERFORMANCE', 'NEWS IMPACT', 'FUNDAMENTAL ANALYSIS', 'RISK-REWARD', 'TABLE', 'DATE']):
                        print(f"\n{line}")
                    # Numbered or bulleted points
                    elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '|')):
                        print(f"  {line}")
                    else:
                        print(f"    {line}")
            print()
            
            # Display Investment Recommendations
            print("\n" + "=" * 80)
            print("💡 INVESTMENT RECOMMENDATIONS")
            print("=" * 80)
            print()
            # Format recommendations with clear sections
            rec_lines = summaries['recommendations'].split('\n')
            for line in rec_lines:
                if line.strip():
                    # Time horizon headers
                    if any(horizon in line.upper() for horizon in ['ONE WEEK', 'SIX MONTHS', 'TWO YEARS', 'SHORT-TERM', 'MEDIUM-TERM', 'LONG-TERM']):
                        print(f"\n{'─' * 80}")
                        print(f"\n{line}")
                        print(f"{'─' * 80}")
                    # Sub-headers (Recommendation, Reasoning, etc.)
                    elif line.strip().startswith(('-', '•')) or ':' in line and len(line) < 100:
                        print(f"\n  {line}")
                    else:
                        print(f"    {line}")
            print()
            
            # Display Analyst Ratings
            print("\n" + "=" * 80)
            print("📊 ANALYST RATINGS & RECOMMENDATIONS")
            print("=" * 80)
            print()
            # Format analyst ratings with clear structure
            analyst_lines = summaries['analyst_ratings'].split('\n')
            for line in analyst_lines:
                if line.strip():
                    # Major section headers
                    if any(header in line.upper() for header in ['CONSENSUS OVERVIEW', 'PRICE TARGET', 'ANALYST PERSPECTIVES', 'REVENUE', 'EARNINGS']):
                        print(f"\n{'─' * 80}")
                        print(f"\n{line}")
                        print(f"{'─' * 80}")
                    # Firm names and ratings
                    elif any(firm in line for firm in ['Morgan Stanley', 'Goldman Sachs', 'J.P. Morgan', 'Bank of America', 'Analyst', 'Rating:', 'Price Target:']):
                        print(f"\n  {line}")
                    # Bulleted or numbered items
                    elif line.strip().startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')):
                        print(f"  {line}")
                    else:
                        print(f"    {line}")
            print()
        else:
            print("❌ Could not generate summaries")
    else:
        print("⚠️  No news articles found")

    
    print("\n" + "=" * 80)
    print(f"📍 Data Source: {stock_data.get('url', 'Google Finance')}")
    print(f"⏰ Analysis Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    # Generate PDF Report
    if summaries:
        print("\n" + "=" * 80)
        print("📄 GENERATING PDF REPORT...")
        print("=" * 80)
        pdf_file = generate_pdf_report(stock_data, historical_data, forecast_data, summaries, stock_symbol)
        if pdf_file:
            print(f"\n📊 PDF report saved successfully!")
            print(f"   Location: {os.path.abspath(pdf_file)}")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
