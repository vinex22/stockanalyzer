"""
Multi-Agent Stock Analyzer API
A Flask-based REST API exposing 11 specialized AI agents as individual endpoints.
Perfect for demonstrating agentic AI architecture.
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
import json
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

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
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT2_NAME")


# ============================================================================
# HELPER FUNCTIONS - Data Fetching
# ============================================================================

def fetch_financial_data(stock_symbol):
    """
    Fetch comprehensive financial data from StockAnalysis.com
    
    Args:
        stock_symbol: Stock ticker symbol
    
    Returns:
        Dictionary with financial metrics from income statement, balance sheet, and ratios
    """
    financial_data = {
        'income_statement': {},
        'balance_sheet': {},
        'ratios': {}
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Fetch Income Statement
        income_url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/financials/"
        response = requests.get(income_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all table rows
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    metric_name = cells[0].get_text(strip=True)
                    # Get the first value column (most recent year)
                    value_text = cells[1].get_text(strip=True)
                    financial_data['income_statement'][metric_name] = value_text
        
        # Fetch Balance Sheet
        balance_url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/financials/balance-sheet/"
        response = requests.get(balance_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    metric_name = cells[0].get_text(strip=True)
                    value_text = cells[1].get_text(strip=True)
                    financial_data['balance_sheet'][metric_name] = value_text
        
        # Fetch Ratios
        ratios_url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/financials/ratios/"
        response = requests.get(ratios_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    metric_name = cells[0].get_text(strip=True)
                    value_text = cells[1].get_text(strip=True)
                    financial_data['ratios'][metric_name] = value_text
        
        return financial_data
        
    except Exception as e:
        print(f"Error fetching financial data: {e}")
        return financial_data


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
        revenue_this_year_match = re.search(r'revenue.*?this year.*?\$([\d,\.]+[BMK]?)', text, re.IGNORECASE)
        if revenue_this_year_match:
            forecast_data['revenue_this_year'] = revenue_this_year_match.group(1)
        
        revenue_next_year_match = re.search(r'revenue.*?next year.*?\$([\d,\.]+[BMK]?)', text, re.IGNORECASE)
        if revenue_next_year_match:
            forecast_data['revenue_next_year'] = revenue_next_year_match.group(1)
        
        # Extract EPS forecast
        eps_this_year_match = re.search(r'EPS.*?this year.*?\$([\d,\.]+)', text, re.IGNORECASE)
        if eps_this_year_match:
            forecast_data['eps_this_year'] = eps_this_year_match.group(1)
        
        eps_next_year_match = re.search(r'EPS.*?next year.*?\$([\d,\.]+)', text, re.IGNORECASE)
        if eps_next_year_match:
            forecast_data['eps_next_year'] = eps_next_year_match.group(1)
        
        # Extract upside percentage
        upside_match = re.search(r'([\d\.]+)%\s+upside', text)
        if upside_match:
            forecast_data['upside_percent'] = upside_match.group(1)
        
        if forecast_data:
            return forecast_data
        else:
            return None
        
    except Exception as e:
        print(f"Error fetching forecast data: {e}")
        return None


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
            'symbol': stock_symbol,
            'current_price': price,
            'exchange': 'NASDAQ'
        }
        
        # Get additional data
        divs = soup.find_all('div', {'class': 'P6K39c'})
        for div in divs:
            text = div.get_text(strip=True)
            if 'Market cap' in text:
                stock_data['market_cap'] = text.split('Market cap')[1].strip()
            elif 'P/E ratio' in text:
                stock_data['pe_ratio'] = text.split('P/E ratio')[1].strip()
            elif 'Dividend yield' in text:
                stock_data['dividend_yield'] = text.split('Dividend yield')[1].strip()
        
        return stock_data
    except Exception as e:
        return {"error": str(e)}


def fetch_historical_data(stock_symbol, days=30):
    """Fetch historical price data from StockAnalysis.com."""
    try:
        url = f"https://stockanalysis.com/stocks/{stock_symbol.lower()}/history/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
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
                    date = cols[0].get_text(strip=True)
                    open_price = float(cols[1].get_text(strip=True).replace('$', '').replace(',', ''))
                    high = float(cols[2].get_text(strip=True).replace('$', '').replace(',', ''))
                    low = float(cols[3].get_text(strip=True).replace('$', '').replace(',', ''))
                    close = float(cols[4].get_text(strip=True).replace('$', '').replace(',', ''))
                    volume = cols[5].get_text(strip=True) if len(cols) > 5 else 'N/A'
                    
                    historical_data.append({
                        'date': date,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'close': close,
                        'volume': volume
                    })
                except (ValueError, IndexError):
                    continue
        
        return historical_data
    except Exception as e:
        return []


def fetch_news_articles(stock_symbol, max_articles=10):
    """
    Fetch news article URLs from StockAnalysis.com
    
    Args:
        stock_symbol: Stock ticker symbol
        max_articles: Maximum number of articles to fetch
    
    Returns:
        List of dictionaries with article title, URL, and source
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


# ============================================================================
# AGENT 1: Technical Analysis Agent
# ============================================================================

@app.route('/api/agents/technical-analysis', methods=['POST'])
def technical_analysis_agent_endpoint():
    """
    Technical Analysis Agent Endpoint
    
    POST Body:
    {
        "stock_symbol": "NVDA"
    }
    
    Returns: Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
    """
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        
        if not stock_symbol:
            return jsonify({"error": "stock_symbol required"}), 400
        
        # Always fetch fresh historical data
        print(f"Fetching historical data for {stock_symbol}...")
        historical_data = fetch_historical_data(stock_symbol)
        
        if not historical_data or len(historical_data) < 2:
            return jsonify({"error": "Insufficient historical data"}), 400
        
        # Prepare price data for LLM
        price_data_text = "HISTORICAL PRICE DATA (Most Recent First):\n"
        price_data_text += "Date | Open | High | Low | Close | Volume\n"
        price_data_text += "-" * 80 + "\n"
        
        for day in historical_data[:30]:  # Use last 30 days
            volume_str = day.get('volume', 'N/A')
            price_data_text += f"{day['date']} | ${day['open']} | ${day['high']} | ${day['low']} | ${day['close']} | {volume_str}\n"
        
        current_price = historical_data[0]['close']
        
        # Create prompt for LLM (matching main program)
        technical_prompt = f"""You are a technical analysis expert. Calculate the following technical indicators from the provided historical price data.

IMPORTANT: Return ONLY a valid JSON object with the calculated values. No explanation, no markdown, just the JSON.

Calculate these indicators:

1. **Simple Moving Averages (SMA)**:
   - 20-day SMA: Average of last 20 closing prices
   - 50-day SMA: Average of last 50 closing prices (if enough data)
   - For each SMA, indicate if current price is above (Bullish) or below (Bearish)
   - Identify Golden Cross (20-day SMA > 50-day SMA) or Death Cross (20-day SMA < 50-day SMA)

2. **Exponential Moving Averages (EMA)**:
   - 12-day EMA: Use multiplier = 2/(12+1) = 0.1538
   - 26-day EMA: Use multiplier = 2/(26+1) = 0.0741
   - Start with SMA as initial EMA, then apply: EMA = (Close * Multiplier) + (Previous EMA * (1 - Multiplier))

3. **Relative Strength Index (RSI)** - 14 periods:
   - Calculate average gains and average losses over 14 periods
   - RS = Average Gain / Average Loss
   - RSI = 100 - (100 / (1 + RS))
   - Signal: Overbought if RSI > 70, Oversold if RSI < 30, Neutral otherwise

4. **MACD (Moving Average Convergence Divergence)**:
   - MACD Line = 12-day EMA - 26-day EMA
   - Signal Line ≈ MACD Line * 0.9 (simplified)
   - Histogram = MACD Line - Signal Line
   - Signal: Bullish if Histogram > 0, Bearish otherwise

5. **Bollinger Bands** - 20-day, 2 standard deviations:
   - Middle Band = 20-day SMA
   - Calculate standard deviation of last 20 closing prices
   - Upper Band = Middle + (2 * Standard Deviation)
   - Lower Band = Middle - (2 * Standard Deviation)
   - Signal: "Overbought (Above Upper Band)" if price > upper, "Oversold (Below Lower Band)" if price < lower, "Normal Range" otherwise

Current Price: {current_price}

Return format (JSON only):
{{
    "sma_20": <number>,
    "sma_20_signal": "Bullish" or "Bearish",
    "sma_50": <number or null>,
    "sma_50_signal": "Bullish" or "Bearish" or null,
    "golden_cross": true or false or null,
    "ema_12": <number>,
    "ema_26": <number>,
    "rsi": <number>,
    "rsi_signal": "Overbought" or "Oversold" or "Neutral",
    "macd": {{
        "macd_line": <number>,
        "signal_line": <number>,
        "histogram": <number>
    }},
    "macd_signal": "Bullish" or "Bearish",
    "bollinger_bands": {{
        "upper": <number>,
        "middle": <number>,
        "lower": <number>
    }},
    "bollinger_signal": "Overbought (Above Upper Band)" or "Oversold (Below Lower Band)" or "Normal Range",
    "current_price": {current_price}
}}"""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": technical_prompt},
                {"role": "user", "content": price_data_text}
            ],
            max_completion_tokens=1000,
            temperature=0
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(0)
        
        indicators = json.loads(result_text)
        
        return jsonify({
            "agent": "Technical Analysis Agent",
            "stock_symbol": stock_symbol,
            "indicators": indicators,
            "data_points_analyzed": len(historical_data)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# AGENT 2: Fundamental Analysis Agent
# ============================================================================

@app.route('/api/agents/fundamental-analysis', methods=['POST'])
def fundamental_analysis_agent_endpoint():
    """
    Fundamental Analysis Agent Endpoint
    
    POST Body:
    {
        "stock_symbol": "NVDA"
    }
    
    Returns: Fundamental metrics (P/E, valuation, quality scores)
    """
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        
        if not stock_symbol:
            return jsonify({"error": "stock_symbol required"}), 400
        
        # Always fetch fresh stock data, historical data, financial data, and forecasts
        print(f"Fetching stock data for {stock_symbol}...")
        stock_data = fetch_stock_data(stock_symbol)
        
        if 'error' in stock_data:
            return jsonify({"error": "Could not fetch stock data"}), 400
        
        print(f"Fetching historical data for {stock_symbol}...")
        historical_data = fetch_historical_data(stock_symbol)
        
        print(f"Fetching financial data for {stock_symbol}...")
        financial_data = fetch_financial_data(stock_symbol)
        
        print(f"Fetching forecast data for {stock_symbol}...")
        forecast_data = fetch_forecast_data(stock_symbol)
        
        # Prepare data for LLM (matching main program)
        stock_info = f"""CURRENT STOCK DATA:
Symbol: {stock_data.get('symbol', 'N/A')}
Current Price: {stock_data.get('current_price', 'N/A')}
Market Cap: {stock_data.get('market_cap', 'N/A')}
P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}
Previous Close: {stock_data.get('previous_close', 'N/A')}
52-Week Range: {stock_data.get('year_range', 'N/A')}
"""
        
        # Add financial data from StockAnalysis.com if available
        if financial_data:
            stock_info += "\n\nFINANCIAL DATA FROM STOCKANALYSIS.COM:\n\n"
            
            # Income Statement highlights
            if financial_data.get('income_statement'):
                stock_info += "Income Statement (Most Recent Year):\n"
                income = financial_data['income_statement']
                for key in ['Revenue', 'Revenue Growth (YoY)', 'Net Income', 'EPS (Diluted)', 
                           'Gross Margin', 'Operating Margin', 'Profit Margin', 'Free Cash Flow']:
                    if key in income:
                        stock_info += f"  {key}: {income[key]}\n"
                stock_info += "\n"
            
            # Balance Sheet highlights
            if financial_data.get('balance_sheet'):
                stock_info += "Balance Sheet (Most Recent):\n"
                balance = financial_data['balance_sheet']
                for key in ['Total Assets', 'Total Liabilities', 'Shareholders\' Equity', 
                           'Total Debt', 'Total Current Assets', 'Total Current Liabilities',
                           'Working Capital']:
                    if key in balance:
                        stock_info += f"  {key}: {balance[key]}\n"
                stock_info += "\n"
            
            # Ratios highlights
            if financial_data.get('ratios'):
                stock_info += "Financial Ratios (Most Recent):\n"
                ratios = financial_data['ratios']
                for key in ['PE Ratio', 'PB Ratio', 'PS Ratio', 'Return on Equity (ROE)', 
                           'Return on Assets (ROA)', 'Debt / Equity Ratio', 'Current Ratio',
                           'Quick Ratio', 'Dividend Yield']:
                    if key in ratios:
                        stock_info += f"  {key}: {ratios[key]}\n"
                stock_info += "\n"
        
        if forecast_data:
            stock_info += f"\nANALYST FORECASTS:\n"
            if 'revenue_this_year' in forecast_data:
                stock_info += f"Revenue This Year: {forecast_data['revenue_this_year']}\n"
            if 'revenue_next_year' in forecast_data:
                stock_info += f"Revenue Next Year: {forecast_data['revenue_next_year']}\n"
            if 'eps_this_year' in forecast_data:
                stock_info += f"EPS This Year: {forecast_data['eps_this_year']}\n"
            if 'eps_next_year' in forecast_data:
                stock_info += f"EPS Next Year: {forecast_data['eps_next_year']}\n"
        
        # Create prompt for LLM to calculate fundamental metrics (matching main program)
        fundamental_prompt = f"""You are a financial analyst. Calculate the following fundamental metrics from the provided stock data.

IMPORTANT: Return ONLY a valid JSON object with the calculated values. No explanation, no markdown, just the JSON.

USE THE REAL FINANCIAL DATA FROM STOCKANALYSIS.COM when provided. Only estimate if specific data is missing.

Calculate these metrics:

1. **Price-to-Earnings (P/E) Ratio**: Use value from financial ratios or stock data

2. **Earnings Per Share (EPS)**: 
   - Current: Use "EPS (Diluted)" from income statement if available
   - Next Year: Use forecast data if available

3. **Revenue Growth (%)**: 
   - Use "Revenue Growth (YoY)" from income statement if available
   - Or calculate from forecasts

4. **Return on Equity (ROE)**: 
   - Use "Return on Equity (ROE)" from financial ratios if available
   - Otherwise estimate based on P/E ratio and industry

5. **Debt-to-Equity (D/E) Ratio**:
   - Use "Debt / Equity Ratio" from financial ratios if available
   - Otherwise estimate based on industry

6. **Price-to-Book (P/B) Ratio**:
   - Use "PB Ratio" from financial ratios if available
   - Otherwise estimate based on P/E and ROE

7. **Dividend Yield**: Use value from financial ratios or stock data

8. **Free Cash Flow (FCF)**:
   - Use "Free Cash Flow" from income statement if available
   - Otherwise estimate based on market cap

9. **Operating Margin**:
   - Use "Operating Margin" from income statement if available
   - Otherwise estimate based on industry

10. **Current Ratio**:
    - Use "Current Ratio" from financial ratios if available
    - Otherwise estimate based on company size

QUALITY SCORE:
- "Strong" if: ROE > 15%, Current Ratio > 1.5, D/E < 0.8, Operating Margin > 15%
- "Weak" if: ROE < 10%, Current Ratio < 1.2, D/E > 1.5, Operating Margin < 10%
- "Average" otherwise

VALUATION ASSESSMENT:
- Consider P/E, P/B, PS ratios vs industry norms
- Consider growth metrics (Revenue Growth, EPS Growth)
- "Undervalued" if ratios below industry average with strong fundamentals
- "Overvalued" if ratios significantly above industry average
- "Fair Value" otherwise

Return format (JSON only):
{{
    "pe_ratio": <number or null>,
    "eps_current": <number or null>,
    "eps_next_year": <number or null>,
    "revenue_growth_percent": <number or null>,
    "roe_percent": <number or null>,
    "debt_to_equity": <number or null>,
    "price_to_book": <number or null>,
    "dividend_yield_percent": <number or null>,
    "free_cash_flow": "<string with $ and units>" or null,
    "operating_margin_percent": <number or null>,
    "current_ratio": <number or null>,
    "quality_score": "Strong" or "Average" or "Weak",
    "valuation_assessment": "Undervalued" or "Fair Value" or "Overvalued"
}}"""

        print(f"\\nCalculating fundamental metrics with real financial data...")
        
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": fundamental_prompt},
                {"role": "user", "content": stock_info}
            ],
            max_completion_tokens=800,
            temperature=0
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(0)
        
        metrics = json.loads(result_text)
        
        print("✅ Fundamental metrics calculated from real financial data")
        
        return jsonify({
            "agent": "Fundamental Analysis Agent",
            "stock_symbol": stock_symbol,
            "fundamentals": metrics
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# AGENT 3: Company Name Agent
# ============================================================================

@app.route('/api/agents/company-name', methods=['POST'])
def company_name_agent_endpoint():
    """
    Company Name Agent Endpoint
    
    POST Body:
    {
        "stock_symbol": "NVDA"
    }
    
    Returns: Official company name and domain
    """
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        
        if not stock_symbol:
            return jsonify({"error": "stock_symbol required"}), 400
        
        # Get company name from LLM
        prompt = f"""You are a financial data expert. Given the stock ticker symbol '{stock_symbol}', provide ONLY the official company name.

Instructions:
1. Return ONLY the official full company name (e.g., "Microsoft Corporation", "Apple Inc.", "Tesla, Inc.")
2. Do NOT include any explanation, ticker symbol, or additional text
3. Return exactly one line with just the company name

Company name:"""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50
        )
        
        company_name = response.choices[0].message.content.strip()
        
        # Get domain from company name
        domain_prompt = f"""Given the company name "{company_name}", provide ONLY the main website domain.

Examples:
- "Microsoft Corporation" → microsoft.com
- "Apple Inc." → apple.com
- "Tesla, Inc." → tesla.com

Instructions:
1. Return ONLY the domain (e.g., "example.com")
2. Do NOT include http://, https://, www., or any other text
3. Return exactly one line

Domain:"""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": domain_prompt}],
            temperature=0.1,
            max_tokens=20
        )
        
        domain = response.choices[0].message.content.strip()
        
        return jsonify({
            "agent": "Company Name Agent",
            "stock_symbol": stock_symbol,
            "company_name": company_name,
            "domain": domain,
            "logo_url": f"https://logo.clearbit.com/{domain}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# AGENT 4 & 5: Fraud Detection & Analysis Agents
# ============================================================================

@app.route('/api/agents/fraud-detection', methods=['POST'])
def fraud_detection_agent_endpoint():
    """
    Fraud Detection Agent Endpoint (Mathematical Analysis)
    
    POST Body:
    {
        "stock_symbol": "NVDA"
    }
    
    Returns: Fraud indicators (TVR, AR, CAR, red flags)
    """
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        
        if not stock_symbol:
            return jsonify({"error": "stock_symbol required"}), 400
        
        # Always fetch fresh historical data
        print(f"Fetching historical data for fraud detection on {stock_symbol}...")
        historical_data = fetch_historical_data(stock_symbol)
        
        if not historical_data or len(historical_data) < 20:
            return jsonify({"error": "Insufficient historical data (need at least 20 days)"}), 400
        
        # Fetch stock data for context
        stock_data = fetch_stock_data(stock_symbol)
        
        # Calculate fraud indicators (matching main program algorithm)
        volume_spikes = []
        abnormal_returns = []
        red_flags = []
        
        # Calculate average volume (excluding most recent 5 days to avoid bias)
        volumes = []
        for i, day in enumerate(historical_data):
            if 'volume' in day and day['volume'] and day['volume'] != 'N/A':
                try:
                    vol = float(str(day['volume']).replace(',', ''))
                    if i >= 5:  # Only use older data for baseline
                        volumes.append(vol)
                except:
                    continue
        
        if len(volumes) < 10:
            return jsonify({"error": "Insufficient volume data"}), 400
        
        avg_volume = sum(volumes) / len(volumes)
        
        # Calculate Volume Spike Ratio (TVR) for recent days
        for i, day in enumerate(historical_data[:10]):  # Check last 10 days
            if 'volume' in day and day['volume'] and day['volume'] != 'N/A':
                try:
                    current_vol = float(str(day['volume']).replace(',', ''))
                    tvr = current_vol / avg_volume
                    
                    # Flag if TVR > 3 (volume is 3x normal)
                    if tvr > 3.0:
                        volume_spikes.append({
                            'date': day.get('date', 'Unknown'),
                            'tvr': round(tvr, 2),
                            'volume': day['volume'],
                            'avg_volume': f"{int(avg_volume):,}",
                            'severity': 'HIGH' if tvr > 5 else 'MEDIUM'
                        })
                        
                        if i < 5:  # Recent spike
                            red_flags.append(
                                f"⚠️  Volume spike detected on {day.get('date', 'recent day')}: {tvr:.1f}x normal volume"
                            )
                except:
                    continue
        
        # Calculate Abnormal Returns (AR)
        daily_returns = []
        for i in range(len(historical_data) - 1):
            try:
                close_today = float(str(historical_data[i].get('close', '0')).replace('$', '').replace(',', ''))
                close_yesterday = float(str(historical_data[i + 1].get('close', '0')).replace('$', '').replace(',', ''))
                
                if close_yesterday > 0:
                    daily_return = ((close_today - close_yesterday) / close_yesterday) * 100
                    daily_returns.append(daily_return)
            except:
                continue
        
        if len(daily_returns) < 10:
            return jsonify({"error": "Insufficient price data for AR calculation"}), 400
        
        # Calculate expected return (average of historical returns)
        expected_return = sum(daily_returns[5:]) / len(daily_returns[5:])
        std_dev = (sum((r - expected_return) ** 2 for r in daily_returns[5:]) / len(daily_returns[5:])) ** 0.5
        
        # Check recent days for abnormal returns
        cumulative_ar = 0
        for i, day_return in enumerate(daily_returns[:10]):
            abnormal_return = day_return - expected_return
            
            # Flag if AR > 2% and beyond 2 standard deviations
            if abs(abnormal_return) > 2.0 and abs(abnormal_return) > 2 * std_dev:
                date = historical_data[i].get('date', 'Unknown')
                
                abnormal_returns.append({
                    'date': date,
                    'actual_return': round(day_return, 2),
                    'expected_return': round(expected_return, 2),
                    'abnormal_return': round(abnormal_return, 2),
                    'severity': 'HIGH' if abs(abnormal_return) > 5 else 'MEDIUM'
                })
                
                if i < 5:  # Recent AR
                    direction = "gain" if abnormal_return > 0 else "drop"
                    red_flags.append(
                        f"📊 Abnormal {direction} on {date}: {abs(abnormal_return):.2f}% (expected {expected_return:.2f}%)"
                    )
                
                cumulative_ar += abnormal_return
        
        # Check for concerning patterns
        if len(volume_spikes) >= 3:
            red_flags.append(
                f"🚨 Multiple volume spikes detected ({len(volume_spikes)} days) - potential manipulation"
            )
        
        if abs(cumulative_ar) > 10:
            red_flags.append(
                f"🚨 High Cumulative Abnormal Return ({cumulative_ar:.2f}%) - unusual price pattern"
            )
        
        # Check for volume spike + abnormal return on same day (strong indicator)
        for vs in volume_spikes:
            for ar in abnormal_returns:
                if vs['date'] == ar['date']:
                    red_flags.append(
                        f"🔴 CRITICAL: Volume spike + Abnormal return on {vs['date']} - possible insider trading"
                    )
                    break
        
        return jsonify({
            "agent": "Fraud Detection Agent",
            "stock_symbol": stock_symbol,
            "fraud_indicators": {
                "volume_spikes": volume_spikes,
                "abnormal_returns": abnormal_returns,
                "cumulative_abnormal_return": round(cumulative_ar, 2),
                "red_flags": red_flags,
                "risk_level": "High" if len(red_flags) > 0 else "Low"
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/fraud-analysis', methods=['POST'])
def fraud_analysis_agent_endpoint():
    """
    Fraud Analysis Agent Endpoint (LLM Interpretation)
    
    POST Body:
    {
        "stock_symbol": "NVDA"
    }
    
    Returns: LLM-based fraud risk assessment
    """
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        
        if not stock_symbol:
            return jsonify({"error": "stock_symbol required"}), 400
        
        # Fetch stock data for context
        print(f"Fetching stock data for {stock_symbol}...")
        stock_data = fetch_stock_data(stock_symbol)
        
        # Always fetch fraud indicators from detection endpoint
        print(f"Fetching fraud indicators for {stock_symbol}...")
        with app.test_client() as test_client:
            response = test_client.post('/api/agents/fraud-detection', 
                                  json={"stock_symbol": stock_symbol})
            if response.status_code == 200:
                fraud_data = response.get_json()
                fraud_indicators = fraud_data.get('fraud_indicators', {})
            else:
                return jsonify({"error": "Could not fetch fraud indicators"}), 400
        
        # Always fetch news articles
        print(f"Fetching news articles for {stock_symbol}...")
        news_articles = fetch_news_articles(stock_symbol)
        
        # Prepare detailed fraud summary (matching main program)
        fraud_summary = f"""FRAUD DETECTION ANALYSIS FOR {stock_symbol}:

Current Price: {stock_data.get('current_price', 'N/A')}
Market Cap: {stock_data.get('market_cap', 'N/A')}

FRAUD INDICATORS DETECTED:
"""
        
        # Add volume spikes with details
        volume_spikes = fraud_indicators.get('volume_spikes', [])
        if volume_spikes:
            fraud_summary += f"\n📊 VOLUME SPIKE RATIO (TVR) - {len(volume_spikes)} instances:\n"
            for spike in volume_spikes:
                fraud_summary += f"  • {spike['date']}: {spike['tvr']}x normal volume (Severity: {spike['severity']})\n"
                fraud_summary += f"    Volume: {spike['volume']:,} vs Avg: {spike['avg_volume']:,}\n"
        else:
            fraud_summary += "\n📊 VOLUME SPIKE RATIO (TVR): No significant spikes detected\n"
        
        # Add abnormal returns with details
        abnormal_returns = fraud_indicators.get('abnormal_returns', [])
        if abnormal_returns:
            fraud_summary += f"\n📈 ABNORMAL RETURNS (AR) - {len(abnormal_returns)} instances:\n"
            for ar in abnormal_returns:
                fraud_summary += f"  • {ar['date']}: {ar['abnormal_return']:+.2f}% abnormal (Severity: {ar['severity']})\n"
                fraud_summary += f"    Actual: {ar['actual_return']:+.2f}% | Expected: {ar['expected_return']:+.2f}%\n"
        else:
            fraud_summary += "\n📈 ABNORMAL RETURNS (AR): No significant abnormalities detected\n"
        
        # Add CAR
        car = fraud_indicators.get('cumulative_abnormal_return', 0)
        fraud_summary += f"\n📊 CUMULATIVE ABNORMAL RETURN (CAR): {car:+.2f}%\n"
        
        # Add red flags
        red_flags = fraud_indicators.get('red_flags', [])
        if red_flags:
            fraud_summary += "\n🚨 RED FLAGS:\n"
            for flag in red_flags:
                fraud_summary += f"  • {flag}\n"
        else:
            fraud_summary += "\n✅ No critical red flags identified\n"
        
        # Add recent news context if available
        if news_articles and len(news_articles) > 0:
            fraud_summary += "\n📰 RECENT NEWS HEADLINES (for context):\n"
            for article in news_articles[:5]:
                fraud_summary += f"  • {article.get('title', 'N/A')} ({article.get('source', 'N/A')})\n"
        
        # Create expert analysis prompt (matching main program)
        fraud_prompt = f"""You are a securities fraud analyst and forensic accountant with expertise in detecting market manipulation, insider trading, and fraudulent activities.

Analyze the following fraud detection indicators and provide a comprehensive risk assessment:

{fraud_summary}

FRAUD DETECTION METRICS REFERENCE:
• Volume Spike Ratio (TVR) > 3x: Unusual trading activity, potential information leak or manipulation
• TVR > 5x: High severity, strong indicator of informed trading
• Abnormal Return (AR) > 2-3%: Unusual price movement without clear fundamental catalyst
• AR > 5%: High severity, potential insider trading or manipulation
• Volume Spike + Abnormal Return on same day: Critical indicator of insider activity
• Cumulative Abnormal Return (CAR) > 10%: Sustained abnormal performance suggesting manipulation

PROVIDE YOUR ANALYSIS IN THE FOLLOWING STRUCTURED FORMAT:

1. RISK LEVEL ASSESSMENT:
   Classify the overall fraud risk as: LOW / MODERATE / HIGH / CRITICAL
   Provide confidence level: 1-10 scale

2. KEY FINDINGS:
   • Summarize the most concerning indicators
   • Identify patterns (e.g., clustering of spikes, timing correlations)
   • Note any indicators that coincide with news events (legitimate) vs no-news days (suspicious)

3. FRAUD TYPOLOGY:
   Based on the patterns, identify the most likely fraud scenario(s):
   • Insider Trading: Trading on non-public information before announcements
   • Market Manipulation: Pump-and-dump, spoofing, or wash trading
   • Front-Running: Large institutional orders being anticipated
   • Information Leakage: Material information leaked before official disclosure
   • Legitimate Activity: Unusual but explainable by public events/news

4. REGULATORY CONSIDERATIONS:
   • Would this pattern trigger SEC/regulatory investigation?
   • Which specific regulations might be violated (e.g., Rule 10b-5, insider trading laws)?
   • Recommended actions for compliance officers or investors

5. INVESTOR IMPLICATIONS:
   • Should retail investors be cautious?
   • Is this a temporary anomaly or sustained risk?
   • Red flags for portfolio risk management

6. RECOMMENDATIONS:
   • Immediate actions (if any)
   • Monitoring priorities going forward
   • Additional data/investigation needed

Be specific, analytical, and provide actionable insights. Reference specific dates and metrics from the data."""

        llm_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert securities fraud analyst specializing in market manipulation detection and forensic analysis of trading patterns."},
                {"role": "user", "content": fraud_prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        analysis = llm_response.choices[0].message.content.strip()
        
        return jsonify({
            "agent": "Fraud Analysis Agent",
            "stock_symbol": stock_symbol,
            "fraud_risk_assessment": analysis
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# AGENT 6-11: Summary Agents
# ============================================================================

@app.route('/api/agents/summary', methods=['POST'])
def summary_agent_endpoint():
    """Summary Agent - 200 tokens, 2-3 sentences"""
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        summary_text = data.get('context', '')
        
        if not stock_symbol or not summary_text:
            return jsonify({"error": "stock_symbol and context required"}), 400
        
        prompt = """Generate a concise 2-3 sentence summary of the stock analysis.
Focus on current price, trend, and key takeaway."""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": summary_text[:2000]}
            ],
            max_completion_tokens=200
        )
        
        return jsonify({
            "agent": "Summary Agent",
            "stock_symbol": stock_symbol,
            "summary": response.choices[0].message.content.strip()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/executive-summary', methods=['POST'])
def executive_summary_agent_endpoint():
    """Executive Summary Agent - 800 tokens, 8-12 sentences"""
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        summary_text = data.get('context', '')
        
        if not stock_symbol or not summary_text:
            return jsonify({"error": "stock_symbol and context required"}), 400
        
        prompt = """Generate a professional executive summary (8-12 sentences) covering:
1. Stock performance and valuation
2. Price trends and volatility
3. News sentiment
4. Risk factors and opportunities"""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": summary_text}
            ],
            max_completion_tokens=800
        )
        
        return jsonify({
            "agent": "Executive Summary Agent",
            "stock_symbol": stock_symbol,
            "executive_summary": response.choices[0].message.content.strip()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/detailed-analysis', methods=['POST'])
def detailed_analysis_agent_endpoint():
    """Detailed Analysis Agent - 1500 tokens"""
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        summary_text = data.get('context', '')
        
        if not stock_symbol or not summary_text:
            return jsonify({"error": "stock_symbol and context required"}), 400
        
        prompt = """Generate detailed analysis (1500 tokens) including:
1. Week-by-week price movement
2. News impact assessment
3. Fundamental analysis
4. Risk-reward analysis"""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": summary_text}
            ],
            max_completion_tokens=1500
        )
        
        return jsonify({
            "agent": "Detailed Analysis Agent",
            "stock_symbol": stock_symbol,
            "detailed_analysis": response.choices[0].message.content.strip()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/investment-recommendation', methods=['POST'])
def investment_recommendation_agent_endpoint():
    """Investment Recommendation Agent - 2000 tokens, 3 time horizons"""
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        summary_text = data.get('context', '')
        
        if not stock_symbol or not summary_text:
            return jsonify({"error": "stock_symbol and context required"}), 400
        
        prompt = """Generate investment recommendations for 3 time horizons:
1. 1 Week (Short-term trading)
2. 6 Months (Medium-term)
3. 2 Years (Long-term)

Include entry/exit points, price targets, strategies."""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": summary_text}
            ],
            max_completion_tokens=2000
        )
        
        return jsonify({
            "agent": "Investment Recommendation Agent",
            "stock_symbol": stock_symbol,
            "recommendations": response.choices[0].message.content.strip()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/analyst-synthesis', methods=['POST'])
def analyst_synthesis_agent_endpoint():
    """Analyst Synthesis Agent - 1500 tokens"""
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        summary_text = data.get('context', '')
        
        if not stock_symbol or not summary_text:
            return jsonify({"error": "stock_symbol and context required"}), 400
        
        prompt = """Synthesize analyst ratings and price targets:
1. Consensus ratings
2. Price target analysis
3. Analyst perspectives
4. Revenue/earnings outlook"""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": summary_text}
            ],
            max_completion_tokens=1500
        )
        
        return jsonify({
            "agent": "Analyst Synthesis Agent",
            "stock_symbol": stock_symbol,
            "analyst_synthesis": response.choices[0].message.content.strip()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/meta-analysis', methods=['POST'])
def meta_analysis_agent_endpoint():
    """Meta-Analysis Agent - 2000 tokens"""
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        summary_text = data.get('context', '')
        
        if not stock_symbol or not summary_text:
            return jsonify({"error": "stock_symbol and context required"}), 400
        
        prompt = """Perform AI-powered meta-analysis:
1. Cross-validation of all insights
2. Confidence levels
3. Uncertainty assessment
4. Overall synthesis"""

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": summary_text}
            ],
            max_completion_tokens=2000
        )
        
        return jsonify({
            "agent": "Meta-Analysis Agent",
            "stock_symbol": stock_symbol,
            "meta_analysis": response.choices[0].message.content.strip()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ORCHESTRATOR: Multi-Agent Coordination
# ============================================================================

@app.route('/api/orchestrator/full-analysis', methods=['POST'])
def multi_agent_orchestrator_endpoint():
    """
    Multi-Agent Orchestrator - Coordinates all agents for comprehensive analysis
    
    POST Body:
    {
        "stock_symbol": "NVDA"
    }
    
    Returns: Complete analysis from all 11 agents
    """
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        
        if not stock_symbol:
            return jsonify({"error": "stock_symbol required"}), 400
        
        results = {
            "stock_symbol": stock_symbol,
            "timestamp": datetime.now().isoformat(),
            "agents_deployed": 11,
            "analysis": {}
        }
        
        # Fetch base data (for context building only, agents fetch their own data)
        stock_data = fetch_stock_data(stock_symbol)
        news_articles = fetch_news_articles(stock_symbol)
        
        if 'error' in stock_data:
            return jsonify({"error": "Could not fetch stock data"}), 400
        
        # Agent 1: Technical Analysis (fetches its own data)
        try:
            with app.test_client() as test_client:
                response = test_client.post('/api/agents/technical-analysis', 
                                           json={"stock_symbol": stock_symbol})
                results["analysis"]["technical_analysis"] = response.get_json()
        except Exception as e:
            results["analysis"]["technical_analysis"] = {"error": str(e)}
        
        # Agent 2: Fundamental Analysis (fetches its own data)
        try:
            with app.test_client() as test_client:
                response = test_client.post('/api/agents/fundamental-analysis', 
                                           json={"stock_symbol": stock_symbol})
                results["analysis"]["fundamental_analysis"] = response.get_json()
        except Exception as e:
            results["analysis"]["fundamental_analysis"] = {"error": str(e)}
        
        # Agent 3: Company Name
        try:
            with app.test_client() as test_client:
                response = test_client.post('/api/agents/company-name', 
                                           json={"stock_symbol": stock_symbol})
                results["analysis"]["company_info"] = response.get_json()
        except Exception as e:
            results["analysis"]["company_info"] = {"error": str(e)}
        
        # Agent 4: Fraud Detection
        try:
            with app.test_client() as test_client:
                response = test_client.post('/api/agents/fraud-detection', 
                                           json={"stock_symbol": stock_symbol})
                results["analysis"]["fraud_detection"] = response.get_json()
        except Exception as e:
            results["analysis"]["fraud_detection"] = {"error": str(e)}
        
        # Agent 5: Fraud Analysis
        try:
            with app.test_client() as test_client:
                response = test_client.post('/api/agents/fraud-analysis', 
                                           json={"stock_symbol": stock_symbol})
                results["analysis"]["fraud_analysis"] = response.get_json()
        except Exception as e:
            results["analysis"]["fraud_analysis"] = {"error": str(e)}
        
        # Prepare context for summary agents
        context = f"""Stock: {stock_symbol}
Price: {stock_data.get('current_price')}
Market Cap: {stock_data.get('market_cap')}
P/E Ratio: {stock_data.get('pe_ratio')}

Recent News:
"""
        for article in news_articles[:5]:
            context += f"- {article.get('title')} ({article.get('source')})\n"
        
        # Agents 6-11: Summary agents
        summary_agents = [
            ('summary', 'Summary Agent'),
            ('executive-summary', 'Executive Summary'),
            ('detailed-analysis', 'Detailed Analysis'),
            ('investment-recommendation', 'Investment Recommendations'),
            ('analyst-synthesis', 'Analyst Synthesis'),
            ('meta-analysis', 'Meta-Analysis')
        ]
        
        for endpoint, name in summary_agents:
            try:
                with app.test_client() as test_client:
                    response = test_client.post(f'/api/agents/{endpoint}', 
                                               json={"stock_symbol": stock_symbol, "context": context})
                    results["analysis"][endpoint.replace('-', '_')] = response.get_json()
            except Exception as e:
                results["analysis"][endpoint.replace('-', '_')] = {"error": str(e)}
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Multi-Agent Stock Analyzer API",
        "agents_available": 11,
        "version": "2.0"
    })


@app.route('/api/agents/list', methods=['GET'])
def list_agents():
    """List all available agents"""
    return jsonify({
        "agents": [
            {"id": 1, "name": "Technical Analysis Agent", "endpoint": "/api/agents/technical-analysis"},
            {"id": 2, "name": "Fundamental Analysis Agent", "endpoint": "/api/agents/fundamental-analysis"},
            {"id": 3, "name": "Company Name Agent", "endpoint": "/api/agents/company-name"},
            {"id": 4, "name": "Fraud Detection Agent", "endpoint": "/api/agents/fraud-detection"},
            {"id": 5, "name": "Fraud Analysis Agent", "endpoint": "/api/agents/fraud-analysis"},
            {"id": 6, "name": "Summary Agent", "endpoint": "/api/agents/summary"},
            {"id": 7, "name": "Executive Summary Agent", "endpoint": "/api/agents/executive-summary"},
            {"id": 8, "name": "Detailed Analysis Agent", "endpoint": "/api/agents/detailed-analysis"},
            {"id": 9, "name": "Investment Recommendation Agent", "endpoint": "/api/agents/investment-recommendation"},
            {"id": 10, "name": "Analyst Synthesis Agent", "endpoint": "/api/agents/analyst-synthesis"},
            {"id": 11, "name": "Meta-Analysis Agent", "endpoint": "/api/agents/meta-analysis"}
        ],
        "orchestrator": {
            "name": "Multi-Agent Orchestrator",
            "endpoint": "/api/orchestrator/full-analysis"
        },
        "pdf": {
            "name": "PDF Report Generator",
            "endpoint": "/api/pdf/generate"
        }
    })


# ============================================================================
# PDF GENERATION
# ============================================================================

def parse_text_to_paragraphs(text, bullet_style, body_style):
    """Parse text with bullet points into ReportLab paragraphs."""
    paragraphs = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line starts with a bullet point marker
        if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
            # Remove the bullet marker
            line_text = line[2:].strip()
            paragraphs.append(Paragraph(f"• {line_text}", bullet_style))
        elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            # Numbered list
            paragraphs.append(Paragraph(line, bullet_style))
        else:
            # Regular paragraph
            paragraphs.append(Paragraph(line, body_style))
    
    return paragraphs


@app.route('/api/pdf/generate', methods=['POST'])
def generate_pdf_endpoint():
    """
    PDF Generation Endpoint
    
    POST Body:
    {
        "stock_symbol": "NVDA",
        "analysis_results": {...}  // Optional - will fetch if not provided
    }
    
    Returns: PDF file
    """
    try:
        data = request.json
        stock_symbol = data.get('stock_symbol', '').upper()
        analysis_results = data.get('analysis_results')
        
        if not stock_symbol:
            return jsonify({"error": "stock_symbol required"}), 400
        
        # If no analysis results provided, call the orchestrator
        if not analysis_results:
            print(f"No analysis results provided, fetching data for {stock_symbol}...")
            with app.test_client() as client:
                response = client.post('/api/orchestrator/full-analysis', 
                                      json={"stock_symbol": stock_symbol})
                if response.status_code != 200:
                    return jsonify({"error": "Failed to fetch analysis data"}), 500
                analysis_results = response.get_json()
        
        # Fetch company info for logo if not in results
        company_info = analysis_results.get('analysis', {}).get('company_name', {})
        if not company_info:
            print(f"Fetching company info for logo...")
            with app.test_client() as client:
                response = client.post('/api/agents/company-name', 
                                      json={"stock_symbol": stock_symbol})
                if response.status_code == 200:
                    company_info = response.get_json()
        
        # Create PDF
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
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=14
        )
        
        bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=6,
            leading=13
        )
        
        # Title page with logo
        logo_url = company_info.get('logo_url')
        
        if logo_url:
            try:
                response = requests.get(logo_url, timeout=5)
                if response.status_code == 200:
                    logo_data = BytesIO(response.content)
                    logo = Image(logo_data, width=1.5*inch, height=1.5*inch)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 0.2*inch))
            except:
                pass
        
        story.append(Paragraph(f"Stock Analysis Report: {stock_symbol}", title_style))
        company_name = company_info.get('company_name', stock_symbol)
        if company_name:
            story.append(Paragraph(company_name, styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add all agent outputs
        sections = [
            ('technical_analysis', 'Technical Analysis', 'indicators'),
            ('fundamental_analysis', 'Fundamental Analysis', 'fundamentals'),
            ('fraud_detection', 'Fraud Detection', 'fraud_indicators'),
            ('fraud_analysis', 'Fraud Risk Assessment', 'fraud_risk_assessment'),
            ('summary', 'Executive Summary', 'summary'),
            ('executive_summary', 'Detailed Executive Summary', 'executive_summary'),
            ('detailed_analysis', 'Detailed Analysis', 'detailed_analysis'),
            ('investment_recommendation', 'Investment Recommendations', 'recommendations'),
            ('analyst_synthesis', 'Analyst Synthesis', 'analyst_synthesis'),
            ('meta_analysis', 'Meta-Analysis', 'meta_analysis')
        ]
        
        for section_key, section_title, data_key in sections:
            section_data = analysis_results.get('analysis', {}).get(section_key, {})
            
            if section_data and not section_data.get('error'):
                story.append(Paragraph(section_title, heading_style))
                
                # Get the actual content
                content = section_data.get(data_key)
                
                if content:
                    if isinstance(content, dict):
                        # Format dictionary as text
                        content_text = json.dumps(content, indent=2)
                        story.append(Paragraph(f"<pre>{content_text}</pre>", body_style))
                    elif isinstance(content, str):
                        # Parse text paragraphs
                        paragraphs = parse_text_to_paragraphs(content, bullet_style, body_style)
                        for para in paragraphs:
                            story.append(para)
                    elif isinstance(content, list):
                        for item in content:
                            story.append(Paragraph(f"• {item}", bullet_style))
                
                story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("🤖 MULTI-AGENT STOCK ANALYZER API")
    print("=" * 80)
    print("\n11 Specialized AI Agents Available:")
    print("  1. Technical Analysis Agent      - /api/agents/technical-analysis")
    print("  2. Fundamental Analysis Agent    - /api/agents/fundamental-analysis")
    print("  3. Company Name Agent            - /api/agents/company-name")
    print("  4. Fraud Detection Agent         - /api/agents/fraud-detection")
    print("  5. Fraud Analysis Agent          - /api/agents/fraud-analysis")
    print("  6. Summary Agent                 - /api/agents/summary")
    print("  7. Executive Summary Agent       - /api/agents/executive-summary")
    print("  8. Detailed Analysis Agent       - /api/agents/detailed-analysis")
    print("  9. Investment Recommendation     - /api/agents/investment-recommendation")
    print(" 10. Analyst Synthesis Agent       - /api/agents/analyst-synthesis")
    print(" 11. Meta-Analysis Agent           - /api/agents/meta-analysis")
    print("\nOrchestrator:")
    print("  🎼 Multi-Agent Orchestrator      - /api/orchestrator/full-analysis")
    print("\nUtility:")
    print("  ❤️  Health Check                  - /api/health")
    print("  📋 List Agents                   - /api/agents/list")
    print("\n" + "=" * 80)
    print("Starting Flask server on http://localhost:5000")
    print("=" * 80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
