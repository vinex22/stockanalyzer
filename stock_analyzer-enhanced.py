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
        
        print(f"✅ Fetched financial data from StockAnalysis.com")
        return financial_data
        
    except Exception as e:
        print(f"⚠️  Error fetching financial data: {e}")
        return financial_data


def calculate_technical_indicators_with_llm(historical_data):
    """
    Use LLM to calculate technical indicators from historical price data
    
    Args:
        historical_data: List of dictionaries with 'close', 'open', 'high', 'low' prices (most recent first)
    
    Returns:
        Dictionary with all technical indicators calculated by LLM
    """
    if not historical_data or len(historical_data) < 2:
        return None
    
    try:
        # Prepare price data for LLM
        price_data_text = "HISTORICAL PRICE DATA (Most Recent First):\n"
        price_data_text += "Date | Open | High | Low | Close | Volume\n"
        price_data_text += "-" * 80 + "\n"
        
        for day in historical_data:
            volume_str = day.get('volume', 'N/A')
            price_data_text += f"{day['date']} | ${day['open']} | ${day['high']} | ${day['low']} | ${day['close']} | {volume_str}\n"
        
        current_price = historical_data[0]['close']
        
        # Create prompt for LLM to calculate technical indicators
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

        print(f"\nAnalyzing {len(historical_data)} days of price data...")
        
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": technical_prompt},
                {"role": "user", "content": price_data_text}
            ],
            max_completion_tokens=1000,
            temperature=0  # Use 0 for mathematical calculations
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response (in case LLM adds markdown)
        import json
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(0)
        
        indicators = json.loads(result_text)
        
        print("✅ Technical indicators calculated by LLM")
        return indicators
        
    except Exception as e:
        print(f"⚠️  Error calculating technical indicators with LLM: {e}")
        print(f"   Response: {result_text if 'result_text' in locals() else 'No response'}")
        return None


def calculate_fundamental_metrics_with_llm(stock_data, historical_data, forecast_data, financial_data=None):
    """
    Use LLM to calculate fundamental analysis metrics from stock data
    Now enhanced with real financial data from StockAnalysis.com
    
    Args:
        stock_data: Current stock information
        historical_data: Historical price data for revenue growth calculations
        forecast_data: Analyst forecasts including revenue/EPS
        financial_data: Dictionary with income statement, balance sheet, and ratios from StockAnalysis.com
    
    Returns:
        Dictionary with fundamental metrics calculated by LLM
    """
    if not stock_data:
        return None
    
    try:
        # Prepare data for LLM
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
        
        # Create prompt for LLM to calculate fundamental metrics
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

        print(f"\nCalculating fundamental metrics with real financial data...")
        
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
        import json
        import re
        
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(0)
        
        metrics = json.loads(result_text)
        
        print("✅ Fundamental metrics calculated from real financial data")
        return metrics
        
    except Exception as e:
        print(f"⚠️  Error calculating fundamental metrics: {e}")
        print(f"   Response: {result_text if 'result_text' in locals() else 'No response'}")
        return None


def calculate_fraud_indicators(historical_data, stock_data, news_data=None):
    """
    Calculate fraud detection indicators:
    - Volume Spike Ratio (TVR): Detects unusual trading volume
    - Abnormal Return (AR): Detects unusual price movements
    - Cumulative Abnormal Return (CAR): Multi-day abnormal returns
    
    Args:
        historical_data: List of daily price/volume data
        stock_data: Current stock information
        news_data: Optional news data to identify news days
    
    Returns:
        Dictionary with fraud indicators and alerts
    """
    if not historical_data or len(historical_data) < 20:
        return None
    
    try:
        fraud_indicators = {
            'volume_spikes': [],
            'abnormal_returns': [],
            'cumulative_abnormal_return': 0,
            'red_flags': []
        }
        
        # Calculate average volume (excluding most recent 5 days to avoid bias)
        volumes = []
        for i, day in enumerate(historical_data):
            if 'volume' in day and day['volume']:
                try:
                    vol = float(str(day['volume']).replace(',', ''))
                    if i >= 5:  # Only use older data for baseline
                        volumes.append(vol)
                except:
                    continue
        
        if len(volumes) < 10:
            return None
        
        avg_volume = sum(volumes) / len(volumes)
        
        # Calculate Volume Spike Ratio (TVR) for recent days
        for i, day in enumerate(historical_data[:10]):  # Check last 10 days
            if 'volume' in day and day['volume']:
                try:
                    current_vol = float(str(day['volume']).replace(',', ''))
                    tvr = current_vol / avg_volume
                    
                    # Flag if TVR > 3 (volume is 3x normal)
                    if tvr > 3.0:
                        fraud_indicators['volume_spikes'].append({
                            'date': day.get('date', 'Unknown'),
                            'tvr': round(tvr, 2),
                            'volume': day['volume'],
                            'avg_volume': f"{int(avg_volume):,}",
                            'severity': 'HIGH' if tvr > 5 else 'MEDIUM'
                        })
                        
                        if i < 5:  # Recent spike
                            fraud_indicators['red_flags'].append(
                                f"⚠️  Volume spike detected on {day.get('date', 'recent day')}: {tvr:.1f}x normal volume"
                            )
                except:
                    continue
        
        # Calculate Abnormal Returns (AR)
        # Simple approach: Compare daily return to average daily return
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
            return fraud_indicators
        
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
                
                fraud_indicators['abnormal_returns'].append({
                    'date': date,
                    'actual_return': round(day_return, 2),
                    'expected_return': round(expected_return, 2),
                    'abnormal_return': round(abnormal_return, 2),
                    'severity': 'HIGH' if abs(abnormal_return) > 5 else 'MEDIUM'
                })
                
                if i < 5:  # Recent AR
                    direction = "gain" if abnormal_return > 0 else "drop"
                    fraud_indicators['red_flags'].append(
                        f"📊 Abnormal {direction} on {date}: {abs(abnormal_return):.2f}% (expected {expected_return:.2f}%)"
                    )
                
                cumulative_ar += abnormal_return
        
        fraud_indicators['cumulative_abnormal_return'] = round(cumulative_ar, 2)
        
        # Check for concerning patterns
        if len(fraud_indicators['volume_spikes']) >= 3:
            fraud_indicators['red_flags'].append(
                f"🚨 Multiple volume spikes detected ({len(fraud_indicators['volume_spikes'])} days) - potential manipulation"
            )
        
        if abs(cumulative_ar) > 10:
            fraud_indicators['red_flags'].append(
                f"🚨 High Cumulative Abnormal Return ({cumulative_ar:.2f}%) - unusual price pattern"
            )
        
        # Check for volume spike + abnormal return on same day (strong indicator)
        for vs in fraud_indicators['volume_spikes']:
            for ar in fraud_indicators['abnormal_returns']:
                if vs['date'] == ar['date']:
                    fraud_indicators['red_flags'].append(
                        f"🔴 CRITICAL: Volume spike + Abnormal return on {vs['date']} - possible insider trading"
                    )
                    break
        
        return fraud_indicators
        
    except Exception as e:
        print(f"⚠️  Error calculating fraud indicators: {e}")
        return None


def analyze_fraud_risk_with_llm(fraud_indicators, stock_data, news_data=None):
    """
    Use LLM to provide expert analysis of fraud indicators and risk assessment.
    
    Args:
        fraud_indicators: Dictionary with calculated fraud metrics (TVR, AR, CAR)
        stock_data: Current stock information
        news_data: Optional news articles for context
    
    Returns:
        String with LLM's fraud risk assessment
    """
    if not fraud_indicators:
        return None
    
    try:
        # Prepare fraud data for LLM
        fraud_summary = f"""FRAUD DETECTION ANALYSIS FOR {stock_data.get('symbol', 'STOCK')}:

Current Price: {stock_data.get('current_price', 'N/A')}
Market Cap: {stock_data.get('market_cap', 'N/A')}

FRAUD INDICATORS DETECTED:
"""
        
        # Add volume spikes
        if fraud_indicators.get('volume_spikes'):
            fraud_summary += f"\n📊 VOLUME SPIKE RATIO (TVR) - {len(fraud_indicators['volume_spikes'])} instances:\n"
            for spike in fraud_indicators['volume_spikes']:
                fraud_summary += f"  • {spike['date']}: {spike['tvr']}x normal volume (Severity: {spike['severity']})\n"
                fraud_summary += f"    Volume: {spike['volume']} vs Avg: {spike['avg_volume']}\n"
        else:
            fraud_summary += "\n📊 VOLUME SPIKE RATIO (TVR): No significant spikes detected\n"
        
        # Add abnormal returns
        if fraud_indicators.get('abnormal_returns'):
            fraud_summary += f"\n📈 ABNORMAL RETURNS (AR) - {len(fraud_indicators['abnormal_returns'])} instances:\n"
            for ar in fraud_indicators['abnormal_returns']:
                fraud_summary += f"  • {ar['date']}: {ar['abnormal_return']:+.2f}% abnormal (Severity: {ar['severity']})\n"
                fraud_summary += f"    Actual: {ar['actual_return']:+.2f}% | Expected: {ar['expected_return']:+.2f}%\n"
        else:
            fraud_summary += "\n📈 ABNORMAL RETURNS (AR): No significant abnormalities detected\n"
        
        # Add CAR
        car = fraud_indicators.get('cumulative_abnormal_return', 0)
        fraud_summary += f"\n📊 CUMULATIVE ABNORMAL RETURN (CAR): {car:+.2f}%\n"
        
        # Add red flags
        if fraud_indicators.get('red_flags'):
            fraud_summary += "\n🚨 RED FLAGS:\n"
            for flag in fraud_indicators['red_flags']:
                fraud_summary += f"  • {flag}\n"
        else:
            fraud_summary += "\n✅ No critical red flags identified\n"
        
        # Add recent news context if available
        if news_data and len(news_data) > 0:
            fraud_summary += "\n📰 RECENT NEWS HEADLINES (for context):\n"
            for article in news_data[:5]:
                fraud_summary += f"  • {article.get('title', 'N/A')} ({article.get('date', 'N/A')})\n"
        
        # Create expert analysis prompt
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
        
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert securities fraud analyst specializing in market manipulation detection and forensic analysis of trading patterns."},
                {"role": "user", "content": fraud_prompt}
            ],
            max_tokens=2000,
            temperature=0.3  # Lower temperature for more analytical, less creative output
        )
        
        result_text = response.choices[0].message.content.strip()
        
        print("✅ LLM fraud risk assessment completed")
        return result_text
        
    except Exception as e:
        print(f"⚠️  Error analyzing fraud risk with LLM: {e}")
        return None


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


def prepare_summary_text(stock_data, historical_data, news_data, forecast_data=None, technical_indicators=None, fundamental_metrics=None):
    """
    Prepare consolidated text summary of all data for LLM analysis
    
    Returns:
        Formatted string with all stock data, indicators, and news
    """
    try:
        # Format stock data
        summary_text = f"""STOCK: {stock_data.get('symbol', 'N/A')}
Current Price: {stock_data.get('current_price', 'N/A')}
Change: {stock_data.get('price_change', 'N/A')} ({stock_data.get('percent_change', 'N/A')})
Market Cap: {stock_data.get('market_cap', 'N/A')}
P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
"""
        
        # Add technical indicators
        if technical_indicators:
            summary_text += f"\nTECHNICAL INDICATORS:\n"
            
            # Moving Averages
            if 'sma_20' in technical_indicators:
                summary_text += f"20-Day SMA: ${technical_indicators['sma_20']:.2f} ({technical_indicators.get('sma_20_signal', 'N/A')})\n"
            if 'sma_50' in technical_indicators:
                summary_text += f"50-Day SMA: ${technical_indicators['sma_50']:.2f} ({technical_indicators.get('sma_50_signal', 'N/A')})\n"
            if 'golden_cross' in technical_indicators:
                cross_type = "Golden Cross (Bullish)" if technical_indicators['golden_cross'] else "Death Cross (Bearish)"
                summary_text += f"SMA Cross Signal: {cross_type}\n"
            
            # EMAs
            if 'ema_12' in technical_indicators:
                summary_text += f"12-Day EMA: ${technical_indicators['ema_12']:.2f}\n"
            if 'ema_26' in technical_indicators:
                summary_text += f"26-Day EMA: ${technical_indicators['ema_26']:.2f}\n"
            
            # RSI
            if 'rsi' in technical_indicators:
                summary_text += f"RSI (14-day): {technical_indicators['rsi']:.2f} ({technical_indicators.get('rsi_signal', 'N/A')})\n"
            
            # MACD
            if 'macd' in technical_indicators:
                macd_data = technical_indicators['macd']
                summary_text += f"MACD Line: {macd_data['macd_line']:.2f}\n"
                summary_text += f"MACD Signal: {technical_indicators.get('macd_signal', 'N/A')}\n"
            
            # Bollinger Bands
            if 'bollinger_bands' in technical_indicators:
                bb = technical_indicators['bollinger_bands']
                summary_text += f"Bollinger Bands (20-day, 2σ):\n"
                summary_text += f"  Upper: ${bb['upper']:.2f}\n"
                summary_text += f"  Middle: ${bb['middle']:.2f}\n"
                summary_text += f"  Lower: ${bb['lower']:.2f}\n"
                summary_text += f"  Signal: {technical_indicators.get('bollinger_signal', 'N/A')}\n"
        
        summary_text += "\n"
        
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
        
        # Add fundamental metrics
        if fundamental_metrics:
            summary_text += f"\nFUNDAMENTAL METRICS:\n"
            if fundamental_metrics.get('pe_ratio'):
                summary_text += f"P/E Ratio: {fundamental_metrics['pe_ratio']:.2f}\n"
            if fundamental_metrics.get('price_to_book'):
                summary_text += f"P/B Ratio: {fundamental_metrics['price_to_book']:.2f}\n"
            if fundamental_metrics.get('eps_current'):
                summary_text += f"EPS (Current): ${fundamental_metrics['eps_current']:.2f}\n"
            if fundamental_metrics.get('roe_percent'):
                summary_text += f"ROE: {fundamental_metrics['roe_percent']:.2f}%\n"
            if fundamental_metrics.get('revenue_growth_percent'):
                summary_text += f"Revenue Growth: {fundamental_metrics['revenue_growth_percent']:.2f}%\n"
            if fundamental_metrics.get('debt_to_equity'):
                summary_text += f"Debt-to-Equity: {fundamental_metrics['debt_to_equity']:.2f}\n"
            if fundamental_metrics.get('operating_margin_percent'):
                summary_text += f"Operating Margin: {fundamental_metrics['operating_margin_percent']:.2f}%\n"
            if fundamental_metrics.get('current_ratio'):
                summary_text += f"Current Ratio: {fundamental_metrics['current_ratio']:.2f}\n"
            if fundamental_metrics.get('free_cash_flow'):
                summary_text += f"Free Cash Flow: {fundamental_metrics['free_cash_flow']}\n"
            if fundamental_metrics.get('valuation_assessment'):
                summary_text += f"Valuation: {fundamental_metrics['valuation_assessment']}\n"
            if fundamental_metrics.get('quality_score'):
                summary_text += f"Quality Score: {fundamental_metrics['quality_score']}\n"
        
        # Add historical trend with all daily prices
        if historical_data and len(historical_data) > 0:
            summary_text += f"\n60-DAY PRICE HISTORY WITH VOLUME:\n"
            for day in historical_data:
                volume_str = f", Volume {day['volume']}" if 'volume' in day else ""
                summary_text += f"{day['date']}: Open ${day['open']}, Close ${day['close']}, High ${day['high']}, Low ${day['low']}{volume_str}\n"
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
        
        return summary_text
        
    except Exception as e:
        print(f"❌ Error preparing summary text: {e}")
        return None


def generate_short_summary(summary_text):
    """LLM Call #4: Generate 2-3 sentence short summary"""
    try:
        short_prompt = """You are a financial analyst. Create a very brief summary (2-3 sentences) of the stock's current status.
Focus only on: current price movement, market cap, and overall sentiment."""
        
        short_user_message = f"Summarize this stock data briefly:\n\n{summary_text[:1000]}"
        
        short_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": short_prompt},
                {"role": "user", "content": short_user_message}
            ],
            max_completion_tokens=200
        )
        return short_response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating short summary: {e}")
        return None


def generate_exec_summary(summary_text):
    """LLM Call #5: Generate 8-12 sentence executive summary"""
    try:
        exec_prompt = """You are a senior financial analyst creating executive summaries for investors. 
Provide a comprehensive, professional summary that includes:
1. Current stock performance and valuation
2. Technical analysis signals (moving averages, RSI, MACD, Bollinger Bands)
3. Fundamental metrics (P/E, ROE, revenue growth, debt levels, quality score)
4. Recent price trends and momentum indicators
5. Key news themes and market sentiment
6. Strategic implications and outlook

Use the technical indicators and fundamental metrics provided to assess:
- Trend direction (SMA/EMA positioning)
- Momentum strength (RSI overbought/oversold)
- Potential reversals (MACD crossovers)
- Volatility conditions (Bollinger Bands)
- Valuation (P/E, P/B ratios vs industry)
- Financial health (ROE, debt-to-equity, current ratio)
- Growth potential (revenue growth, operating margin)

Format: Clear paragraphs, professional tone. 8-12 sentences total."""
        
        exec_user_message = f"Create an executive summary for investors:\n\n{summary_text}"
        
        exec_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": exec_prompt},
                {"role": "user", "content": exec_user_message}
            ],
            max_completion_tokens=800
        )
        return exec_response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating executive summary: {e}")
        return None


def generate_detailed_analysis(summary_text):
    """LLM Call #6: Generate detailed analysis with news impact"""
    try:
        detailed_prompt = """You are a senior equity research analyst. Provide a detailed analysis that includes:

1. TECHNICAL ANALYSIS
   - Moving Average Analysis: Assess trend direction using SMA (20-day, 50-day) and EMA (12-day, 26-day)
   - Identify Golden Cross (bullish) or Death Cross (bearish) signals if present
   - RSI Analysis: Evaluate momentum and identify overbought (>70) or oversold (<30) conditions
   - MACD Analysis: Examine momentum convergence/divergence and potential trend changes
   - Bollinger Bands: Assess volatility and identify potential breakouts or mean reversion setups
   - Overall technical trend: Bullish, Bearish, or Neutral based on indicators alignment

2. STOCK PERFORMANCE ANALYSIS
   - Detailed examination of price movements over the past 60 days
   - Correlation between technical signals and actual price action
   - Volatility patterns and trading ranges
   - Technical levels, support/resistance zones

3. NEWS IMPACT ASSESSMENT
   - Analyze each major news article (mention source name) and its specific impact on stock price
   - Identify correlation between news events and price movements
   - Assess market reaction and sentiment shifts
   - **IMPORTANT FOR PDF**: Write in narrative paragraph format, NOT tables
   - For each news event, write: "On [Date], [News Event from Source] caused [Price Movement], reflecting [Market Sentiment]"
   - Use actual dates and specific price changes (e.g., "+$3.09", "close $288.62")

4. FUNDAMENTAL ANALYSIS
   - Valuation metrics interpretation (P/E, market cap, etc.)
   - Comparison to sector peers and historical norms
   - Growth prospects and earnings outlook

5. RISK-REWARD ANALYSIS
   - Key risks: regulatory, competitive, macro-economic
   - Catalysts and opportunities
   - Near-term and long-term outlook
   - Technical risk levels (support/resistance)

IMPORTANT: Format for PDF export - use clear paragraphs and narrative style. NO tables, NO special formatting. Use simple dashes (-) for bullet points if needed.
Be specific about technical signals, how news events correlate with stock price changes, and actual price levels. Use actual dates and prices from the data."""
        
        detailed_user_message = f"Provide a detailed analysis with news impact assessment:\n\n{summary_text}"
        
        detailed_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": detailed_prompt},
                {"role": "user", "content": detailed_user_message}
            ],
            max_completion_tokens=1500
        )
        return detailed_response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating detailed analysis: {e}")
        return None


def generate_recommendations(summary_text):
    """LLM Call #7: Generate investment recommendations for different time horizons"""
    try:
        recommendation_prompt = """You are a senior investment advisor. Based on all available data including technical indicators, provide detailed BUY/SELL/HOLD recommendations for three different time horizons.

IMPORTANT: Format for PDF export - use clear section headers and paragraphs. NO tables, NO complex formatting.

1. ONE WEEK (Short-term trading)
   - Recommendation: BUY/SELL/HOLD (with confidence level: High/Medium/Low)
   - Technical Setup: Analyze RSI, MACD, moving averages, Bollinger Bands for entry/exit signals
   - Detailed Reasoning: Include technical indicators, momentum analysis, news sentiment impact, short-term catalysts
   - Entry Price Target (if applicable) - use technical levels
   - Exit/Stop-Loss Levels - based on support/resistance
   - Position Size Suggestion (% of portfolio)
   - Key Triggers to Watch (specific events, price levels, technical breakouts)
   - Risk Assessment (what could go wrong, key technical invalidation levels)

2. SIX MONTHS (Medium-term investment)
   - Recommendation: BUY/SELL/HOLD (with confidence level: High/Medium/Low)
   - Technical Outlook: Medium-term trend assessment using 50-day SMA, RSI patterns
   - Detailed Reasoning: Include fundamental analysis, technical trend confirmation, analyst consensus alignment, business outlook, earnings expectations
   - Price Target Range (conservative to optimistic) - combine technical and fundamental targets
   - Critical Milestones (earnings dates, product launches, regulatory decisions)
   - Valuation Assessment (fair value vs current price)
   - Risk/Reward Ratio
   - Portfolio Allocation Suggestion

3. TWO YEARS (Long-term investment)
   - Recommendation: BUY/SELL/HOLD (with confidence level: High/Medium/Low)
   - Long-term Technical Trend: Overall trend direction assessment
   - Detailed Reasoning: Strategic positioning, competitive moat, growth trajectory, industry trends, management quality
   - Long-term Price Target Range
   - Major Risks and Mitigation Strategies
   - Key Opportunities and Growth Drivers
   - Competitive Advantage Assessment
   - Recommended Investment Approach (DCA, lump sum, etc.)

For each time horizon, provide comprehensive analysis with specific numbers, dates, and actionable insights.
Be highly specific and data-driven. Reference actual prices, technical signals, analyst forecasts, recent news events, and historical patterns.
Include what-if scenarios and contingency plans based on technical breakout/breakdown scenarios."""
        
        recommendation_user_message = f"Provide comprehensive investment recommendations for different time horizons:\n\n{summary_text}"
        
        recommendation_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": recommendation_prompt},
                {"role": "user", "content": recommendation_user_message}
            ],
            max_completion_tokens=2000
        )
        return recommendation_response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        return None


def generate_analyst_ratings(summary_text):
    """LLM Call #8: Generate analyst ratings summary"""
    try:
        analyst_prompt = """You are synthesizing analyst research. Based on the analyst forecast data provided, create a comprehensive analyst ratings summary.

IMPORTANT: Format for PDF export - use clear paragraphs and narrative style. NO tables, NO special formatting. Use simple dashes (-) for lists.

1. ANALYST CONSENSUS OVERVIEW
   - Overall consensus rating and what it means
   - Number of analysts covering the stock
   - Distribution of ratings (if available: Strong Buy, Buy, Hold, Sell, Strong Sell)
   - Recent changes in analyst sentiment
   - What the consensus tells us about market expectations

2. PRICE TARGET ANALYSIS
   - Average price target and implied upside/downside from current price
   - Price target range (low to high) and what this range indicates
   - How current price compares to analyst targets
   - Bull case scenario: what would drive the stock to high target
   - Bear case scenario: what risks could push it to low target
   - Historical accuracy of analyst targets for this stock (if pattern visible)

3. REVENUE & EARNINGS OUTLOOK
   - Revenue forecasts for this year and next year
   - EPS forecasts for this year and next year
   - Implied growth rates (YoY revenue growth, EPS growth)
   - How these forecasts compare to historical performance
   - Key assumptions driving these forecasts
   - Risks to forecast achievement

4. INVESTMENT IMPLICATIONS
   - What the analyst data suggests about market sentiment
   - Alignment or divergence between consensus and price action
   - How to interpret the data for investment decisions
   - Key metrics to monitor going forward

Be specific and data-driven. Focus on the actual numbers and what they mean. Do NOT create fictional analyst names or firms. Do NOT invent specific analyst commentary. Stick to analyzing the aggregate data provided."""
        
        analyst_user_message = f"Create analyst ratings summary:\n\n{summary_text}"
        
        analyst_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": analyst_prompt},
                {"role": "user", "content": analyst_user_message}
            ],
            max_completion_tokens=1500
        )
        return analyst_response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating analyst ratings: {e}")
        return None


def generate_llm_analytics(summary_text):
    """LLM Call #9: Generate comprehensive AI meta-analysis"""
    try:
        llm_analytics_prompt = """You are an AI-powered investment research platform providing advanced analytical insights. 
Perform a COMPREHENSIVE META-ANALYSIS synthesizing ALL available data points to generate unique insights that go beyond traditional analysis.

Your task is to:

1. **DATA SYNTHESIS & PATTERN RECOGNITION**
   - Cross-reference technical indicators with fundamental metrics to identify alignment or divergence
   - Analyze correlation patterns between news sentiment, price movements, and technical signals
   - Examine trading volume patterns: volume spikes, volume trends, price-volume divergence
   - Identify hidden trends or anomalies in the 60-day price history
   - Detect momentum shifts that may not be obvious from individual indicators
   - Assess volume confirmation of price movements (strong moves should have high volume)

2. **MULTI-DIMENSIONAL RISK ASSESSMENT**
   - Technical Risk: Evaluate support/resistance levels, volatility patterns, trend strength, volume patterns
   - Fundamental Risk: Assess valuation metrics, financial health ratios, growth sustainability
   - Sentiment Risk: Analyze news sentiment consistency, analyst consensus reliability
   - Market Risk: Consider broader market conditions reflected in the data
   - Liquidity Risk: Analyze trading volume trends and liquidity conditions
   - Calculate an overall risk score (Low/Medium/High) with specific reasoning

3. **OPPORTUNITY IDENTIFICATION**
   - Identify specific entry/exit price levels based on technical analysis
   - Flag potential catalysts from news or upcoming events
   - Detect value opportunities where fundamentals diverge from technical signals
   - Highlight momentum plays supported by both technicals and fundamentals
   - Assess risk-reward ratio for different investment timeframes

4. **PREDICTIVE INSIGHTS**
   - Based on historical patterns in the 60-day data, identify likely near-term price scenarios
   - Evaluate probability of technical breakouts/breakdowns
   - Assess likelihood of mean reversion vs trend continuation
   - Consider how current fundamentals support or contradict technical projections

5. **STRATEGIC RECOMMENDATIONS**
   - Optimal position sizing based on volatility and risk metrics
   - Suggested stop-loss levels using technical support zones
   - Price targets for profit-taking using resistance levels and fundamental valuation
   - Hedging strategies if warranted by risk assessment
   - Portfolio allocation suggestions (aggressive/moderate/conservative)

6. **KEY INSIGHTS SUMMARY**
   - 3-5 bullet points of the MOST IMPORTANT actionable insights
   - Unique observations that integrate multiple data sources
   - Critical alerts or warnings based on data analysis
   - Confidence level for the overall analysis (High/Medium/Low)

IMPORTANT: 
- Be specific with numbers, dates, and price levels
- Reference actual data points from technical indicators, fundamental metrics, news, and price history
- Identify contradictions or confirmations between different data sources
- Provide probabilistic assessments where appropriate (e.g., "70% probability of...")
- Format for PDF with clear sections and paragraphs (no tables)

This is an AI-enhanced analysis - leverage the full dataset to generate insights a human analyst might miss."""
        
        llm_analytics_user_message = f"Perform comprehensive AI-powered meta-analysis of all data:\n\n{summary_text}"
        
        llm_analytics_response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": llm_analytics_prompt},
                {"role": "user", "content": llm_analytics_user_message}
            ],
            max_completion_tokens=2000
        )
        return llm_analytics_response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating LLM analytics: {e}")
        return None


def generate_all_summaries(stock_data, historical_data, news_data, forecast_data=None, 
                           technical_indicators=None, fundamental_metrics=None):
    """
    Orchestrator function: Generate all 6 types of summaries using dedicated LLM calls
    
    Returns:
        Dictionary with all summary types
    """
    try:
        # Prepare consolidated data text (used by all LLM calls)
        summary_text = prepare_summary_text(stock_data, historical_data, news_data, 
                                           forecast_data, technical_indicators, fundamental_metrics)
        
        if not summary_text:
            return None
        
        # Call each dedicated summary function
        return {
            'short_summary': generate_short_summary(summary_text),
            'executive_summary': generate_exec_summary(summary_text),
            'detailed_analysis': generate_detailed_analysis(summary_text),
            'recommendations': generate_recommendations(summary_text),
            'analyst_ratings': generate_analyst_ratings(summary_text),
            'llm_analytics': generate_llm_analytics(summary_text)
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
                                
                                # Extract volume if available (usually in column 7)
                                volume = None
                                if len(cols) >= 8:
                                    try:
                                        volume = cols[7].text.strip().replace(',', '')
                                    except:
                                        pass
                                
                                data_point = {
                                    'date': date,
                                    'open': open_price,
                                    'high': high_price,
                                    'low': low_price,
                                    'close': close_price
                                }
                                
                                if volume:
                                    data_point['volume'] = volume
                                
                                historical_data.append(data_point)
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


def generate_pdf_report(stock_data, historical_data, forecast_data, summaries, stock_symbol, technical_indicators=None, fundamental_metrics=None, fraud_analysis=None):
    """
    Generate a professional PDF report of the stock analysis
    """
    def clean_text_for_pdf(text):
        """Clean and escape text for PDF generation, removing tables and improving formatting"""
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
        
        # Format section headers (lines ending with :)
        text = re.sub(r'^([A-Z][A-Za-z\s&]+:)\s*$', r'<b>\1</b>', text, flags=re.MULTILINE)
        
        # Format numbered lists (1., 2., etc.)
        text = re.sub(r'^(\d+\.\s+[^\n]+)', r'<b>\1</b>', text, flags=re.MULTILINE)
        
        # Replace **text** with <b>text</b>
        text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
        
        # Format bullet points (-, •, *)
        text = re.sub(r'^(\s*[-•*]\s+)', r'&nbsp;&nbsp;&nbsp;• ', text, flags=re.MULTILINE)
        
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
            spaceAfter=10,
            leading=14
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            spaceBefore=10,
            leading=15,
            fontName='Helvetica-Bold'
        )
        
        bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=6,
            leading=13
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
        
        # Technical Indicators
        if technical_indicators:
            story.append(Paragraph("Technical Indicators", heading_style))
            
            tech_text = ""
            
            # Moving Averages
            if 'sma_20' in technical_indicators:
                tech_text += f"<b>20-Day SMA:</b> ${technical_indicators['sma_20']:.2f} ({technical_indicators.get('sma_20_signal', 'N/A')})<br/>"
            if 'sma_50' in technical_indicators:
                tech_text += f"<b>50-Day SMA:</b> ${technical_indicators['sma_50']:.2f} ({technical_indicators.get('sma_50_signal', 'N/A')})<br/>"
            if 'golden_cross' in technical_indicators:
                cross_type = "Golden Cross (Bullish)" if technical_indicators['golden_cross'] else "Death Cross (Bearish)"
                tech_text += f"<b>SMA Crossover:</b> {cross_type}<br/>"
            
            tech_text += "<br/>"
            
            # EMAs
            if 'ema_12' in technical_indicators:
                tech_text += f"<b>12-Day EMA:</b> ${technical_indicators['ema_12']:.2f}<br/>"
            if 'ema_26' in technical_indicators:
                tech_text += f"<b>26-Day EMA:</b> ${technical_indicators['ema_26']:.2f}<br/>"
            
            tech_text += "<br/>"
            
            # RSI
            if 'rsi' in technical_indicators:
                tech_text += f"<b>RSI (14-day):</b> {technical_indicators['rsi']:.2f} ({technical_indicators.get('rsi_signal', 'N/A')})<br/>"
            
            # MACD
            if 'macd' in technical_indicators:
                tech_text += f"<b>MACD Signal:</b> {technical_indicators.get('macd_signal', 'N/A')}<br/>"
            
            tech_text += "<br/>"
            
            # Bollinger Bands
            if 'bollinger_bands' in technical_indicators:
                bb = technical_indicators['bollinger_bands']
                tech_text += f"<b>Bollinger Bands (20-day, 2σ):</b><br/>"
                tech_text += f"  Upper: ${bb['upper']:.2f}<br/>"
                tech_text += f"  Middle: ${bb['middle']:.2f}<br/>"
                tech_text += f"  Lower: ${bb['lower']:.2f}<br/>"
                tech_text += f"  Signal: {technical_indicators.get('bollinger_signal', 'N/A')}<br/>"
            
            story.append(Paragraph(tech_text, body_style))
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
        
        # Fundamental Metrics
        if fundamental_metrics:
            story.append(Paragraph("Fundamental Analysis", heading_style))
            
            fund_text = "<b>Valuation Metrics:</b><br/>"
            if fundamental_metrics.get('pe_ratio'):
                fund_text += f"P/E Ratio: {fundamental_metrics['pe_ratio']:.2f}<br/>"
            if fundamental_metrics.get('price_to_book'):
                fund_text += f"P/B Ratio: {fundamental_metrics['price_to_book']:.2f}<br/>"
            if fundamental_metrics.get('valuation_assessment'):
                fund_text += f"Valuation: {fundamental_metrics['valuation_assessment']}<br/>"
            
            fund_text += "<br/><b>Profitability Metrics:</b><br/>"
            if fundamental_metrics.get('eps_current'):
                fund_text += f"EPS (Current): ${fundamental_metrics['eps_current']:.2f}<br/>"
            if fundamental_metrics.get('roe_percent'):
                fund_text += f"ROE: {fundamental_metrics['roe_percent']:.2f}%<br/>"
            if fundamental_metrics.get('operating_margin_percent'):
                fund_text += f"Operating Margin: {fundamental_metrics['operating_margin_percent']:.2f}%<br/>"
            
            fund_text += "<br/><b>Growth & Financial Health:</b><br/>"
            if fundamental_metrics.get('revenue_growth_percent'):
                fund_text += f"Revenue Growth: {fundamental_metrics['revenue_growth_percent']:.2f}%<br/>"
            if fundamental_metrics.get('debt_to_equity'):
                fund_text += f"Debt-to-Equity: {fundamental_metrics['debt_to_equity']:.2f}<br/>"
            if fundamental_metrics.get('current_ratio'):
                fund_text += f"Current Ratio: {fundamental_metrics['current_ratio']:.2f}<br/>"
            if fundamental_metrics.get('free_cash_flow'):
                fund_text += f"Free Cash Flow: {fundamental_metrics['free_cash_flow']}<br/>"
            
            if fundamental_metrics.get('quality_score'):
                fund_text += f"<br/><b>Overall Quality: {fundamental_metrics['quality_score']}</b><br/>"
            
            story.append(Paragraph(fund_text, body_style))
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
        story.append(Spacer(1, 0.1*inch))
        
        # Parse detailed analysis with better section handling
        detail_sections = summaries['detailed_analysis'].split('\n\n')
        for section in detail_sections:
            if not section.strip():
                continue
            
            # Check if it's a major section header (all caps or numbered)
            lines = section.strip().split('\n')
            first_line = lines[0].strip()
            
            if first_line.isupper() or (first_line and first_line[0].isdigit() and '.' in first_line[:3]):
                # Section header
                story.append(Paragraph(clean_text_for_pdf(first_line), section_style))
                if len(lines) > 1:
                    remaining = '\n'.join(lines[1:])
                    story.append(Paragraph(clean_text_for_pdf(remaining), body_style))
            else:
                # Regular paragraph
                cleaned_para = clean_text_for_pdf(section)
                story.append(Paragraph(cleaned_para, body_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Investment Recommendations
        story.append(Paragraph("Investment Recommendations", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Parse recommendations with time horizon sections
        rec_sections = summaries['recommendations'].split('\n\n')
        for section in rec_sections:
            if not section.strip():
                continue
            
            lines = section.strip().split('\n')
            first_line = lines[0].strip()
            
            # Check for time horizon headers (ONE WEEK, SIX MONTHS, etc.)
            if any(horizon in first_line.upper() for horizon in ['ONE WEEK', 'SIX MONTHS', 'TWO YEARS', 'SHORT-TERM', 'MEDIUM-TERM', 'LONG-TERM']):
                story.append(Spacer(1, 0.15*inch))
                story.append(Paragraph(clean_text_for_pdf(first_line), section_style))
                if len(lines) > 1:
                    remaining = '\n'.join(lines[1:])
                    story.append(Paragraph(clean_text_for_pdf(remaining), body_style))
            else:
                cleaned_para = clean_text_for_pdf(section)
                story.append(Paragraph(cleaned_para, body_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Analyst Ratings
        story.append(Paragraph("Analyst Ratings & Consensus", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        analyst_sections = summaries['analyst_ratings'].split('\n\n')
        for section in analyst_sections:
            if not section.strip():
                continue
            
            lines = section.strip().split('\n')
            first_line = lines[0].strip()
            
            # Check for section headers (numbered or all caps)
            if first_line.isupper() or (first_line and first_line[0].isdigit() and '.' in first_line[:3]):
                story.append(Paragraph(clean_text_for_pdf(first_line), section_style))
                if len(lines) > 1:
                    remaining = '\n'.join(lines[1:])
                    story.append(Paragraph(clean_text_for_pdf(remaining), body_style))
            else:
                cleaned_para = clean_text_for_pdf(section)
                story.append(Paragraph(cleaned_para, body_style))
        
        story.append(PageBreak())
        
        # Fraud Risk Analysis
        if fraud_analysis:
            story.append(Paragraph("🚨 Fraud Detection & Risk Analysis", heading_style))
            story.append(Spacer(1, 0.1*inch))
            fraud_paragraphs = fraud_analysis.split('\n\n')
            for para in fraud_paragraphs:
                if para.strip():
                    cleaned_para = clean_text_for_pdf(para)
                    story.append(Paragraph(cleaned_para, body_style))
            story.append(Spacer(1, 0.2*inch))
            story.append(PageBreak())
        
        # LLM Analytics - AI-Powered Meta-Analysis
        if 'llm_analytics' in summaries:
            story.append(Paragraph("🤖 LLM Analytics - AI-Powered Comprehensive Meta-Analysis", heading_style))
            story.append(Spacer(1, 0.1*inch))
            analytics_paragraphs = summaries['llm_analytics'].split('\n\n')
            for para in analytics_paragraphs:
                if para.strip():
                    cleaned_para = clean_text_for_pdf(para)
                    story.append(Paragraph(cleaned_para, body_style))
            story.append(Spacer(1, 0.2*inch))
        
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
    print("📅 Fetching 60-day historical data...")
    historical_data = fetch_historical_data(stock_symbol, days=60)
    
    # Fetch analyst forecasts
    print("📊 Fetching analyst forecasts...")
    forecast_data = fetch_forecast_data(stock_symbol)
    
    # Fetch financial data from StockAnalysis.com
    print("💰 Fetching financial data from StockAnalysis.com...")
    financial_data = fetch_financial_data(stock_symbol)
    
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
        print("-" * 100)
        print(f"{'Date':<12} {'Open':<12} {'Close':<12} {'High':<12} {'Low':<12} {'Volume':<15}")
        print("-" * 100)
        # Show first 10 and last 10 if more than 20 days
        if len(historical_data) > 20:
            for day in historical_data[:10]:
                volume_str = day.get('volume', 'N/A')
                print(f"{day['date']:<12} ${day['open']:<11} ${day['close']:<11} ${day['high']:<11} ${day['low']:<11} {volume_str:<15}")
            print(f"{'...':<12} {'...':<12} {'...':<12} {'...':<12} {'...':<12} {'...':<15}")
            for day in historical_data[-10:]:
                volume_str = day.get('volume', 'N/A')
                print(f"{day['date']:<12} ${day['open']:<11} ${day['close']:<11} ${day['high']:<11} ${day['low']:<11} {volume_str:<15}")
        else:
            for day in historical_data:
                volume_str = day.get('volume', 'N/A')
                print(f"{day['date']:<12} ${day['open']:<11} ${day['close']:<11} ${day['high']:<11} ${day['low']:<11} {volume_str:<15}")
    else:
        print()
        print("⚠️  Could not fetch historical data")
    
    # Calculate technical indicators
    print()
    print("📊 Calculating technical indicators using AI...")
    technical_indicators = calculate_technical_indicators_with_llm(historical_data)
    
    if technical_indicators:
        print()
        print("=" * 60)
        print("📈 TECHNICAL INDICATORS")
        print("=" * 60)
        print()
        
        # Display Moving Averages
        if 'sma_20' in technical_indicators:
            print(f"20-Day SMA: ${technical_indicators['sma_20']:.2f} - {technical_indicators.get('sma_20_signal', 'N/A')}")
        if 'sma_50' in technical_indicators:
            print(f"50-Day SMA: ${technical_indicators['sma_50']:.2f} - {technical_indicators.get('sma_50_signal', 'N/A')}")
        if 'golden_cross' in technical_indicators:
            cross_type = "🌟 Golden Cross (Bullish)" if technical_indicators['golden_cross'] else "💀 Death Cross (Bearish)"
            print(f"SMA Crossover: {cross_type}")
        
        print()
        if 'ema_12' in technical_indicators:
            print(f"12-Day EMA: ${technical_indicators['ema_12']:.2f}")
        if 'ema_26' in technical_indicators:
            print(f"26-Day EMA: ${technical_indicators['ema_26']:.2f}")
        
        # Display RSI
        if 'rsi' in technical_indicators:
            print()
            rsi_emoji = "🔥" if technical_indicators['rsi'] > 70 else "❄️" if technical_indicators['rsi'] < 30 else "⚖️"
            print(f"RSI (14-day): {rsi_emoji} {technical_indicators['rsi']:.2f} - {technical_indicators.get('rsi_signal', 'N/A')}")
        
        # Display MACD
        if 'macd' in technical_indicators:
            print()
            macd_emoji = "📈" if technical_indicators.get('macd_signal') == 'Bullish' else "📉"
            print(f"MACD: {macd_emoji} {technical_indicators.get('macd_signal', 'N/A')}")
            print(f"  MACD Line: {technical_indicators['macd']['macd_line']:.2f}")
        
        # Display Bollinger Bands
        if 'bollinger_bands' in technical_indicators:
            print()
            bb = technical_indicators['bollinger_bands']
            print(f"Bollinger Bands (20-day, 2σ):")
            print(f"  Upper: ${bb['upper']:.2f}")
            print(f"  Middle: ${bb['middle']:.2f}")
            print(f"  Lower: ${bb['lower']:.2f}")
            print(f"  Signal: {technical_indicators.get('bollinger_signal', 'N/A')}")
    
    # Calculate fundamental metrics
    print()
    print("📊 Calculating fundamental metrics using AI...")
    fundamental_metrics = calculate_fundamental_metrics_with_llm(stock_data, historical_data, forecast_data, financial_data)
    
    if fundamental_metrics:
        print()
        print("=" * 60)
        print("📊 FUNDAMENTAL ANALYSIS")
        print("=" * 60)
        print()
        
        # Valuation Metrics
        print("Valuation Metrics:")
        if fundamental_metrics.get('pe_ratio'):
            print(f"  P/E Ratio: {fundamental_metrics['pe_ratio']:.2f}")
        if fundamental_metrics.get('price_to_book'):
            print(f"  P/B Ratio: {fundamental_metrics['price_to_book']:.2f}")
        if fundamental_metrics.get('valuation_assessment'):
            print(f"  Assessment: {fundamental_metrics['valuation_assessment']}")
        
        print()
        print("Profitability Metrics:")
        if fundamental_metrics.get('eps_current'):
            print(f"  EPS (Current Year): ${fundamental_metrics['eps_current']:.2f}")
        if fundamental_metrics.get('eps_next_year'):
            print(f"  EPS (Next Year): ${fundamental_metrics['eps_next_year']:.2f}")
        if fundamental_metrics.get('roe_percent'):
            print(f"  ROE: {fundamental_metrics['roe_percent']:.2f}%")
        if fundamental_metrics.get('operating_margin_percent'):
            print(f"  Operating Margin: {fundamental_metrics['operating_margin_percent']:.2f}%")
        
        print()
        print("Growth Metrics:")
        if fundamental_metrics.get('revenue_growth_percent'):
            print(f"  Revenue Growth: {fundamental_metrics['revenue_growth_percent']:.2f}%")
        
        print()
        print("Financial Health:")
        if fundamental_metrics.get('debt_to_equity'):
            print(f"  Debt-to-Equity: {fundamental_metrics['debt_to_equity']:.2f}")
        if fundamental_metrics.get('current_ratio'):
            print(f"  Current Ratio: {fundamental_metrics['current_ratio']:.2f}")
        if fundamental_metrics.get('free_cash_flow'):
            print(f"  Free Cash Flow: {fundamental_metrics['free_cash_flow']}")
        
        print()
        print("Income Metrics:")
        if fundamental_metrics.get('dividend_yield_percent'):
            print(f"  Dividend Yield: {fundamental_metrics['dividend_yield_percent']:.2f}%")
        
        print()
        if fundamental_metrics.get('quality_score'):
            quality_emoji = "⭐" if fundamental_metrics['quality_score'] == 'Strong' else "⚖️" if fundamental_metrics['quality_score'] == 'Average' else "⚠️"
            print(f"Overall Quality: {quality_emoji} {fundamental_metrics['quality_score']}")
    
    # Fetch and analyze news
    print()
    print("=" * 60)
    print("📰 FETCHING NEWS ARTICLES...")
    print("=" * 60)
    print()
    
    news_articles = fetch_news_urls(stock_symbol, max_articles=15)
    
    # Calculate and display fraud indicators (after news_articles is defined)
    print()
    print("🔍 Analyzing fraud indicators...")
    fraud_indicators = calculate_fraud_indicators(historical_data, stock_data, news_articles)
    fraud_risk_analysis = None  # Initialize to None
    
    if fraud_indicators:
        print()
        print("="
 * 60)
        print("🚨 FRAUD DETECTION INDICATORS")
        print("=" * 60)
        print()
        
        # Display red flags first if any
        if fraud_indicators.get('red_flags'):
            print("⚠️  RED FLAGS DETECTED:")
            print()
            for flag in fraud_indicators['red_flags']:
                print(f"  {flag}")
            print()
        else:
            print("✅ No significant fraud indicators detected")
            print()
        
        # Display Volume Spikes
        if fraud_indicators.get('volume_spikes'):
            print("📊 VOLUME SPIKE RATIO (TVR) - Unusual Trading Activity:")
            print()
            for spike in fraud_indicators['volume_spikes']:
                severity_emoji = "🔴" if spike['severity'] == 'HIGH' else "🟡"
                print(f"  {severity_emoji} {spike['date']}: {spike['tvr']}x normal volume")
                print(f"     Volume: {spike['volume']} (Avg: {spike['avg_volume']})")
            print()
        
        # Display Abnormal Returns
        if fraud_indicators.get('abnormal_returns'):
            print("📈 ABNORMAL RETURNS (AR) - Unusual Price Movements:")
            print()
            for ar in fraud_indicators['abnormal_returns']:
                severity_emoji = "🔴" if ar['severity'] == 'HIGH' else "🟡"
                direction = "📈" if ar['abnormal_return'] > 0 else "📉"
                print(f"  {severity_emoji} {ar['date']}: {direction} {ar['abnormal_return']:+.2f}% abnormal")
                print(f"     Actual: {ar['actual_return']:+.2f}% | Expected: {ar['expected_return']:+.2f}%")
            print()
        
        # Display Cumulative Abnormal Return
        if fraud_indicators.get('cumulative_abnormal_return'):
            car = fraud_indicators['cumulative_abnormal_return']
            car_emoji = "🔴" if abs(car) > 10 else "🟡" if abs(car) > 5 else "✅"
            print(f"Cumulative Abnormal Return (CAR): {car_emoji} {car:+.2f}%")
            if abs(car) > 10:
                print("  ⚠️  High CAR may indicate sustained manipulation or insider activity")
            print()
        
        # Interpretation guide
        print("ℹ️  INTERPRETATION:")
        print("   • TVR > 3x: Unusual trading activity, potential information leak")
        print("   • AR > 2-3%: Abnormal price movement without clear catalyst")
        print("   • Volume spike + AR same day: Strong indicator of insider trading")
        print("   • High CAR: Sustained abnormal performance over multiple days")
        
        # Get LLM expert analysis of fraud risk
        print()
        print("🔍 Generating expert fraud risk assessment with AI...")
        fraud_risk_analysis = analyze_fraud_risk_with_llm(fraud_indicators, stock_data, news_articles)
        
        if fraud_risk_analysis:
            print()
            print("=" * 60)
            print("🎓 EXPERT FRAUD RISK ANALYSIS (AI-Powered)")
            print("=" * 60)
            print()
            print(fraud_risk_analysis)
    
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
    
    # Initialize summaries variable
    summaries = None
    
    # Continue with news content fetching (news_articles already fetched earlier)
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
    else:
        print("⚠️  No news articles found")
        print("   Proceeding with analysis using available data...")
    
    # Generate executive summary (with or without news)
    print()
    print("=" * 60)
    print("📊 GENERATING COMPREHENSIVE ANALYSIS (10 AI Analysis Calls)")
    print("=" * 60)
    print()
    print("🔄 Analyzing with AI:")
    print("  1️⃣  Technical Indicators Calculation")
    print("  2️⃣  Fundamental Metrics Calculation")
    print("  3️⃣  Short Summary")
    print("  4️⃣  Executive Summary") 
    print("  5️⃣  Detailed Analysis")
    print("  6️⃣  Investment Recommendations")
    print("  7️⃣  Analyst Ratings Synthesis")
    print("  8️⃣  LLM Analytics (Meta-Analysis)")
    print("  9️⃣  Fraud Risk Assessment")
    print()
    
    # Use news_articles if available, otherwise pass empty list
    summaries = generate_all_summaries(stock_data, historical_data, news_articles or [], forecast_data, technical_indicators, fundamental_metrics)
    
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
        
        # Display LLM Analytics
        if 'llm_analytics' in summaries:
            print("\n" + "=" * 80)
            print("🤖 LLM ANALYTICS - AI-POWERED COMPREHENSIVE META-ANALYSIS")
            print("=" * 80)
            print()
            # Format LLM analytics with clear structure
            analytics_lines = summaries['llm_analytics'].split('\n')
            for line in analytics_lines:
                if line.strip():
                    # Major section headers (numbered or all caps)
                    if any(header in line.upper() for header in ['DATA SYNTHESIS', 'PATTERN RECOGNITION', 'RISK ASSESSMENT', 
                                                                  'OPPORTUNITY', 'PREDICTIVE', 'STRATEGIC', 'KEY INSIGHTS',
                                                                  'TECHNICAL RISK', 'FUNDAMENTAL RISK', 'SENTIMENT RISK']):
                        print(f"\n{'─' * 80}")
                        print(f"\n{line}")
                        print(f"{'─' * 80}")
                    # Bulleted or numbered items
                    elif line.strip().startswith(('-', '•', '1.', '2.', '3.', '4.', '5.', '6.')):
                        print(f"  {line}")
                    # Sub-items or detailed points
                    elif line.strip().startswith(('*', '◦', 'o')):
                        print(f"    {line}")
                    else:
                        print(f"    {line}")
            print()
    else:
        print("❌ Could not generate summaries")

    
    print("\n" + "=" * 80)
    print(f"📍 Data Source: {stock_data.get('url', 'Google Finance')}")
    print(f"⏰ Analysis Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    # Generate PDF Report
    if summaries:
        print("\n" + "=" * 80)
        print("📄 GENERATING PDF REPORT...")
        print("=" * 80)
        pdf_file = generate_pdf_report(stock_data, historical_data, forecast_data, summaries, stock_symbol, technical_indicators, fundamental_metrics, fraud_risk_analysis)
        if pdf_file:
            print(f"\n📊 PDF report saved successfully!")
            print(f"   Location: {os.path.abspath(pdf_file)}")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
