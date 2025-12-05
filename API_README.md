# Stock Analyzer Multi-Agent API

A Flask-based REST API providing AI-powered stock analysis through 11 specialized agents using Azure OpenAI. Each agent focuses on a specific aspect of stock analysis, from technical indicators to fraud detection, delivering comprehensive insights.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables in .env file
AZURE_OPENAI_API_KEY2=your_api_key
AZURE_OPENAI_ENDPOINT2=your_endpoint
AZURE_OPENAI_DEPLOYMENT2_NAME=gpt-4.1
```

### Run the API

```bash
python stock_analyzer_agents_api.py
```

The API will start on `http://localhost:5000`

## 🤖 11 Specialized Agents

### Core Analysis Agents (1-5)

1. **Technical Analysis Agent**: Calculates SMA, EMA, RSI, MACD, Bollinger Bands with golden cross detection
2. **Fundamental Analysis Agent**: P/E, EPS, ROE, D/E ratios, quality score, valuation assessment
3. **Company Name Agent**: Identifies company name, domain, and fetches logo
4. **Fraud Detection Agent**: Mathematical analysis - TVR, AR, CAR calculations
5. **Fraud Analysis Agent**: LLM-based fraud risk assessment with 6-section structured analysis

### Summary & Synthesis Agents (6-11)

6. **Summary Agent** (200 tokens): 2-3 sentence overview
7. **Executive Summary Agent** (800 tokens): Comprehensive executive summary
8. **Detailed Analysis Agent** (1500 tokens): In-depth analysis
9. **Investment Recommendations Agent** (2000 tokens): 1-week, 6-month, 2-year outlook
10. **Analyst Synthesis Agent** (1500 tokens): Synthesized analyst consensus
11. **Meta-Analysis Agent** (2000 tokens): Cross-agent insights and confidence levels

## 📡 API Endpoints

### Utility Endpoints

#### Health Check
**GET** `/api/health`

```json
{
  "status": "healthy",
  "timestamp": "2025-12-06T10:30:00"
}
```

#### List All Agents
**GET** `/api/agents/list`

Returns all 11 agents with descriptions and endpoints.

---

### Individual Agent Endpoints

All agent endpoints use **POST** method with JSON body:

```json
{
  "stock_symbol": "AAPL"
}
```

#### 1. Technical Analysis
**POST** `/api/agents/technical-analysis`

**Response:**
```json
{
  "agent": "Technical Analysis Agent",
  "stock_symbol": "AAPL",
  "technical_indicators": {
    "sma_20": 185.25,
    "sma_20_signal": "Bullish",
    "sma_50": 180.50,
    "golden_cross": true,
    "ema_12": 186.00,
    "ema_26": 182.75,
    "rsi": 65.5,
    "rsi_signal": "Neutral",
    "macd": {
      "macd_line": 3.25,
      "signal_line": 2.90,
      "histogram": 0.35
    },
    "macd_signal": "Bullish",
    "bollinger_bands": {
      "upper": 190.50,
      "middle": 185.25,
      "lower": 180.00
    },
    "bollinger_signal": "Normal Range",
    "current_price": 187.50
  }
}
```

**Features:**
- Fetches 30-day historical data automatically
- Golden Cross/Death Cross detection
- Temperature 0 for mathematical precision
- Identical to main stock_analyzer.py

---

#### 2. Fundamental Analysis
**POST** `/api/agents/fundamental-analysis`

**Response:**
```json
{
  "agent": "Fundamental Analysis Agent",
  "stock_symbol": "AAPL",
  "fundamentals": {
    "pe_ratio": 28.5,
    "eps_current": 6.58,
    "eps_next_year": 7.20,
    "revenue_growth_percent": 8.5,
    "roe_percent": 45.2,
    "debt_to_equity": 1.85,
    "price_to_book": 12.8,
    "dividend_yield_percent": 0.5,
    "free_cash_flow": "$99.5B",
    "operating_margin_percent": 30.2,
    "current_ratio": 1.05,
    "quality_score": "Strong",
    "valuation_assessment": "Fair Value"
  }
}
```

**Features:**
- Fetches financial data from StockAnalysis.com
- Income statement, balance sheet, and ratios
- Analyst forecasts integration
- Real financial data (not estimates)
- Temperature 0 for analytical precision

---

#### 3. Company Name
**POST** `/api/agents/company-name`

**Response:**
```json
{
  "agent": "Company Name Agent",
  "stock_symbol": "AAPL",
  "company_name": "Apple Inc.",
  "domain": "apple.com",
  "logo_url": "https://logo.clearbit.com/apple.com"
}
```

---

#### 4. Fraud Detection (Mathematical)
**POST** `/api/agents/fraud-detection`

**Response:**
```json
{
  "agent": "Fraud Detection Agent",
  "stock_symbol": "AAPL",
  "fraud_indicators": {
    "volume_spikes": [
      {
        "date": "Dec 04, 2025",
        "tvr": 4.2,
        "volume": "125,000,000",
        "avg_volume": "29,761,905",
        "severity": "MEDIUM"
      }
    ],
    "abnormal_returns": [
      {
        "date": "Dec 04, 2025",
        "actual_return": 3.5,
        "expected_return": 0.5,
        "abnormal_return": 3.0,
        "severity": "HIGH"
      }
    ],
    "cumulative_abnormal_return": 5.2,
    "red_flags": [
      "⚠️  Volume spike detected on Dec 04, 2025: 4.2x normal volume",
      "📊 Abnormal gain on Dec 04, 2025: 3.00% (expected 0.50%)"
    ],
    "risk_level": "High"
  }
}
```

**Features:**
- Volume Spike Ratio (TVR) with 3x threshold
- Abnormal Return (AR) with standard deviation
- Cumulative Abnormal Return (CAR)
- Severity levels (HIGH/MEDIUM)
- Critical pattern detection

---

#### 5. Fraud Analysis (LLM-Based)
**POST** `/api/agents/fraud-analysis`

**Response:**
```json
{
  "agent": "Fraud Analysis Agent",
  "stock_symbol": "AAPL",
  "fraud_risk_assessment": "1. RISK LEVEL ASSESSMENT:\nOverall fraud risk: MODERATE\nConfidence level: 7/10\n\n2. KEY FINDINGS:\n• Volume spike on Dec 04 correlates with earnings announcement\n• Abnormal return justified by strong quarterly results\n• Pattern consistent with legitimate market reaction\n\n3. FRAUD TYPOLOGY:\nLegitimate Activity: Volume and price movement explained by public earnings beat\n\n4. REGULATORY CONSIDERATIONS:\n• No SEC investigation expected\n• Trading pattern within normal bounds for major announcements\n\n5. INVESTOR IMPLICATIONS:\n• Retail investors: No immediate concerns\n• Temporary volatility expected to normalize\n\n6. RECOMMENDATIONS:\n• Monitor for sustained volume patterns\n• Cross-reference with future earnings dates"
}
```

**Features:**
- Fetches stock data, fraud indicators, and news
- Detailed fraud summary with TVR/AR/CAR
- 6-section structured analysis
- News correlation analysis
- Temperature 0.3 for balanced assessment

---

#### 6-11. Summary Agents
**POST** `/api/agents/summary`
**POST** `/api/agents/executive-summary`
**POST** `/api/agents/detailed-analysis`
**POST** `/api/agents/investment-recommendations`
**POST** `/api/agents/analyst-synthesis`
**POST** `/api/agents/meta-analysis`

**Request Body:**
```json
{
  "stock_symbol": "AAPL",
  "context": "Technical Analysis: Bullish trend with SMA_20 at 185.25...\nFundamental Analysis: Strong quality score...\nFraud Analysis: Low risk..."
}
```

**Response:**
```json
{
  "agent": "Summary Agent",
  "stock_symbol": "AAPL",
  "summary": "Apple Inc. shows bullish technical momentum with price above key moving averages. Strong fundamentals with ROE of 45.2% and quality score 'Strong'. No fraud concerns detected."
}
```

---

### Orchestrator Endpoint

#### Full Multi-Agent Analysis
**POST** `/api/orchestrator/full-analysis`

**Request Body:**
```json
{
  "stock_symbol": "AAPL"
}
```

**Response:**
```json
{
  "orchestrator": "Multi-Agent Stock Analyzer",
  "stock_symbol": "AAPL",
  "timestamp": "2025-12-06T10:30:00",
  "stock_data": {
    "symbol": "AAPL",
    "current_price": "$187.50",
    "market_cap": "$2.9T",
    "pe_ratio": "28.5"
  },
  "company_info": {
    "company_name": "Apple Inc.",
    "domain": "apple.com",
    "logo_url": "https://logo.clearbit.com/apple.com"
  },
  "news_articles": [
    {
      "title": "Apple Reports Record Q4 Earnings",
      "url": "https://cnbc.com/...",
      "source": "CNBC"
    }
  ],
  "agents": {
    "technical_analysis": { ... },
    "fundamental_analysis": { ... },
    "fraud_detection": { ... },
    "fraud_analysis": { ... },
    "summary": { ... },
    "executive_summary": { ... },
    "detailed_analysis": { ... },
    "investment_recommendations": { ... },
    "analyst_synthesis": { ... },
    "meta_analysis": { ... }
  }
}
```

**Features:**
- Automatically fetches all data (stock, historical, news)
- Calls all 11 agents in sequence
- Builds context for summary agents
- Complete analysis in one request
- ~60-90 seconds total execution time

---

### PDF Generation

#### Generate PDF Report
**POST** `/api/pdf/generate`

**Request Body (Option 1 - Auto-fetch):**
```json
{
  "stock_symbol": "AAPL"
}
```

**Request Body (Option 2 - Use existing results):**
```json
{
  "stock_symbol": "AAPL",
  "analysis_results": { ... }
}
```

**Response:**
Downloads PDF file: `stock_analysis_AAPL_20251206_103000.pdf`

**Features:**
- Auto-calls orchestrator if no results provided
- Professional formatting with company logo
- Custom blue theme (#1f4788)
- All 11 agent analyses included
- Timestamped and source-attributed

## 🧪 Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:5000/api/health

# List all agents
curl http://localhost:5000/api/agents/list

# Technical analysis
curl -X POST http://localhost:5000/api/agents/technical-analysis \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol": "AAPL"}'

# Fundamental analysis
curl -X POST http://localhost:5000/api/agents/fundamental-analysis \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol": "AAPL"}'

# Fraud detection (mathematical)
curl -X POST http://localhost:5000/api/agents/fraud-detection \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol": "AAPL"}'

# Fraud analysis (LLM interpretation)
curl -X POST http://localhost:5000/api/agents/fraud-analysis \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol": "AAPL"}'

# Full multi-agent analysis
curl -X POST http://localhost:5000/api/orchestrator/full-analysis \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol": "AAPL"}'

# Generate PDF
curl -X POST http://localhost:5000/api/pdf/generate \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol": "AAPL"}' \
  --output aapl_report.pdf
```

### Using Python

```python
import requests

base_url = 'http://localhost:5000'

# Technical analysis
response = requests.post(f'{base_url}/api/agents/technical-analysis',
                        json={'stock_symbol': 'AAPL'})
tech_data = response.json()
print(f"RSI: {tech_data['technical_indicators']['rsi']}")
print(f"Signal: {tech_data['technical_indicators']['rsi_signal']}")

# Fundamental analysis
response = requests.post(f'{base_url}/api/agents/fundamental-analysis',
                        json={'stock_symbol': 'AAPL'})
fund_data = response.json()
print(f"P/E Ratio: {fund_data['fundamentals']['pe_ratio']}")
print(f"Quality Score: {fund_data['fundamentals']['quality_score']}")

# Fraud detection
response = requests.post(f'{base_url}/api/agents/fraud-detection',
                        json={'stock_symbol': 'AAPL'})
fraud_data = response.json()
print(f"Volume Spikes: {len(fraud_data['fraud_indicators']['volume_spikes'])}")
print(f"Risk Level: {fraud_data['fraud_indicators']['risk_level']}")

# Full orchestrator analysis
response = requests.post(f'{base_url}/api/orchestrator/full-analysis',
                        json={'stock_symbol': 'AAPL'})
full_data = response.json()
print(full_data['agents']['summary']['summary'])

# Generate PDF
response = requests.post(f'{base_url}/api/pdf/generate',
                        json={'stock_symbol': 'AAPL'})
with open('aapl_report.pdf', 'wb') as f:
    f.write(response.content)
```

### Using JavaScript/Fetch

```javascript
const baseUrl = 'http://localhost:5000';

// Technical analysis
fetch(`${baseUrl}/api/agents/technical-analysis`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ stock_symbol: 'AAPL' })
})
.then(response => response.json())
.then(data => {
  console.log('RSI:', data.technical_indicators.rsi);
  console.log('MACD Signal:', data.technical_indicators.macd_signal);
});

// Full analysis
fetch(`${baseUrl}/api/orchestrator/full-analysis`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ stock_symbol: 'AAPL' })
})
.then(response => response.json())
.then(data => {
  console.log('Summary:', data.agents.summary.summary);
  console.log('Recommendations:', data.agents.investment_recommendations.recommendations);
});

// Download PDF
fetch(`${baseUrl}/api/pdf/generate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ stock_symbol: 'AAPL' })
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'aapl_report.pdf';
  a.click();
});
```

### Using Insomnia or Postman

An Insomnia collection is provided: `Insomnia_Stock_Analyzer_API.json`

**Features:**
- Pre-configured requests for all 11 agents
- Organized folders (Technical, Fundamental, Fraud, Summary, Utilities)
- Example requests for NVDA, AAPL, MSFT, TSLA
- Error test cases
- Environment variables support

**Import Steps:**
1. Open Insomnia
2. Import → From File
3. Select `Insomnia_Stock_Analyzer_API.json`
4. All requests ready to use

## 🏗️ Architecture

```
Client Request
    ↓
Flask API Server (Port 5000)
    ↓
├── Individual Agent Endpoints (11 specialized agents)
│   ├── Agent 1: Technical Analysis (SMA, EMA, RSI, MACD, Bollinger)
│   ├── Agent 2: Fundamental Analysis (P/E, ROE, Quality Score)
│   ├── Agent 3: Company Name (Logo, Domain)
│   ├── Agent 4: Fraud Detection (TVR, AR, CAR - Mathematical)
│   ├── Agent 5: Fraud Analysis (LLM Risk Assessment)
│   ├── Agent 6: Summary (200 tokens)
│   ├── Agent 7: Executive Summary (800 tokens)
│   ├── Agent 8: Detailed Analysis (1500 tokens)
│   ├── Agent 9: Investment Recommendations (2000 tokens)
│   ├── Agent 10: Analyst Synthesis (1500 tokens)
│   └── Agent 11: Meta-Analysis (2000 tokens)
    ↓
├── Multi-Agent Orchestrator
│   └── Coordinates all 11 agents + builds context
    ↓
├── Data Fetching Layer
│   ├── fetch_stock_data() - Google Finance (current price, market cap, P/E)
│   ├── fetch_historical_data() - StockAnalysis.com (30-day OHLCV)
│   ├── fetch_financial_data() - Income, Balance Sheet, Ratios
│   ├── fetch_forecast_data() - Analyst forecasts, price targets
│   └── fetch_news_articles() - News from major sources (10 articles)
    ↓
├── Azure OpenAI Integration
│   ├── GPT-4 for all LLM-based agents
│   ├── Temperature 0 for mathematical/analytical tasks
│   ├── Temperature 0.3 for risk assessment
│   └── Variable max_tokens per agent (200-2000)
    ↓
├── Response Generation
│   ├── JSON responses for all endpoints
│   └── PDF generation with ReportLab
    ↓
Client Response
```

## 📊 Data Sources & Features

### Real-Time Data Collection
- **Google Finance**: Current price, market cap, P/E ratio, dividend yield, 52-week range
- **StockAnalysis.com**: 
  - Historical OHLCV data (30 days)
  - Income statement (revenue, margins, FCF)
  - Balance sheet (assets, debt, working capital)
  - Financial ratios (ROE, ROA, D/E, current ratio)
  - Analyst forecasts (revenue, EPS, price targets)
- **News Sources**: Articles from MarketWatch, CNBC, Reuters, Bloomberg, Forbes, Barrons, Benzinga, Motley Fool, Invezz

### Agent-Specific Features

**Technical Analysis:**
- 20-day and 50-day Simple Moving Averages
- 12-day and 26-day Exponential Moving Averages
- 14-period Relative Strength Index
- MACD with signal line and histogram
- Bollinger Bands (20-day, 2 standard deviations)
- Golden Cross / Death Cross detection

**Fundamental Analysis:**
- Real financial data from StockAnalysis.com
- 10+ fundamental metrics
- Quality score algorithm
- Valuation assessment (undervalued/fair/overvalued)

**Fraud Detection:**
- Volume Spike Ratio (TVR) > 3x threshold
- Abnormal Return (AR) with statistical significance
- Cumulative Abnormal Return (CAR) tracking
- Severity classification (HIGH/MEDIUM)
- Critical pattern detection (volume spike + AR same day)

**Fraud Analysis:**
- 6-section structured analysis
- News correlation
- Fraud typology identification
- Regulatory considerations
- SEC investigation likelihood
- Investor implications

### PDF Report Features
- Professional formatting with company logo
- Custom color scheme (#1f4788 blue theme)
- All 11 agent analyses included
- Stock data summary table
- News headlines section
- Timestamped and branded
- Downloadable as attachment

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY2=your_api_key_here
AZURE_OPENAI_ENDPOINT2=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT2_NAME=gpt-4.1
```

### API Configuration

```python
# In stock_analyzer_agents_api.py

# Change port
app.run(debug=True, host='0.0.0.0', port=8080)

# Disable debug mode for production
app.run(debug=False, host='0.0.0.0', port=5000)

# Customize article count
news_articles = fetch_news_articles(stock_symbol, max_articles=20)

# Adjust agent token limits
max_completion_tokens=500  # For shorter summaries
max_completion_tokens=3000  # For longer analyses
```

### Agent Temperature Settings

Each agent uses optimized temperature settings:

```python
# Mathematical/Analytical agents (precise calculations)
temperature=0  # Technical Analysis, Fundamental Analysis

# Risk assessment agents (balanced judgment)
temperature=0.3  # Fraud Analysis

# Summary agents (default creativity)
# Uses default temperature for natural language generation
```

## 🛡️ Error Handling

The API includes comprehensive error handling:

**HTTP Status Codes:**
- **200 OK**: Successful request
- **400 Bad Request**: Missing or invalid stock symbol
- **404 Not Found**: Stock symbol not found or data unavailable
- **500 Internal Server Error**: Analysis generation, data fetching, or PDF creation failed

**Example Error Responses:**
```json
{
  "error": "stock_symbol required"
}
```

```json
{
  "error": "Insufficient historical data (need at least 20 days)"
}
```

```json
{
  "error": "Could not fetch fraud indicators"
}
```

## ⚡ Performance & Timing

**Individual Agent Endpoints:**
- Technical Analysis: ~5-8 seconds
- Fundamental Analysis: ~8-12 seconds (includes financial data fetch)
- Company Name: ~2-3 seconds
- Fraud Detection: ~3-5 seconds
- Fraud Analysis: ~10-15 seconds (includes fraud detection + news fetch)
- Summary Agents: ~3-5 seconds each

**Orchestrator Endpoint:**
- Full 11-agent analysis: ~60-90 seconds
- Breakdown:
  - Data fetching (stock, historical, financial, forecast, news): ~15-20 seconds
  - Agent 1-5 (core analysis): ~30-40 seconds
  - Agent 6-11 (summaries): ~15-20 seconds
  - Context building and orchestration: ~5-10 seconds

**PDF Generation:**
- With existing results: ~2-3 seconds
- Auto-fetch via orchestrator: ~65-95 seconds (orchestrator time + PDF rendering)

**Optimization Tips:**
- Use individual agent endpoints for specific analyses
- Cache orchestrator results for PDF generation
- Implement Redis caching for repeated stock queries
- Use async/await for parallel data fetching (future enhancement)

## 🚀 Deployment

### Development
```bash
# Activate environment
conda activate llms

# Run API
python stock_analyzer_agents_api.py
```

### Production (Using Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 stock_analyzer_agents_api:app

# With increased timeout for long-running orchestrator
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 180 stock_analyzer_agents_api:app
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY stock_analyzer_agents_api.py .
COPY .env .

EXPOSE 5000

# Use gunicorn with longer timeout for orchestrator
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "180", "stock_analyzer_agents_api:app"]
```

```bash
# Build image
docker build -t stock-analyzer-api .

# Run container
docker run -p 5000:5000 --env-file .env stock-analyzer-api
```

### Azure App Service Deployment

```bash
# Login to Azure
az login

# Create resource group
az group create --name stock-analyzer-rg --location eastus

# Create App Service plan
az appservice plan create --name stock-analyzer-plan \
  --resource-group stock-analyzer-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group stock-analyzer-rg \
  --plan stock-analyzer-plan --name stock-analyzer-api \
  --runtime "PYTHON:3.9"

# Configure environment variables
az webapp config appsettings set --resource-group stock-analyzer-rg \
  --name stock-analyzer-api --settings \
  AZURE_OPENAI_API_KEY2="your_key" \
  AZURE_OPENAI_ENDPOINT2="your_endpoint" \
  AZURE_OPENAI_DEPLOYMENT2_NAME="gpt-4.1"

# Deploy code
az webapp up --resource-group stock-analyzer-rg \
  --name stock-analyzer-api --runtime "PYTHON:3.9"
```

## 🔒 Security Best Practices

1. **Environment Variables**: 
   - Never commit `.env` file to version control
   - Add `.env` to `.gitignore`
   - Use separate keys for dev/staging/production

2. **API Keys**: 
   - Rotate Azure OpenAI keys regularly
   - Use Azure Key Vault for production
   - Implement key expiration monitoring

3. **CORS Configuration**:
   ```python
   # Development (permissive)
   CORS(app)
   
   # Production (restrictive)
   CORS(app, origins=["https://yourdomain.com"])
   ```

4. **Input Validation**: 
   - Stock symbols validated and sanitized
   - Upper case enforcement
   - SQL injection protection (no DB queries, but good practice)

5. **Rate Limiting**: 
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @limiter.limit("10 per minute")
   @app.route('/api/orchestrator/full-analysis', methods=['POST'])
   def orchestrator_endpoint():
       ...
   ```

6. **Timeouts**: 
   - All external requests have 10-15 second timeouts
   - Prevents hanging connections
   - Graceful error handling

7. **Authentication** (Future):
   ```python
   # API key authentication
   @app.before_request
   def check_api_key():
       if request.endpoint not in ['health', 'list_agents']:
           api_key = request.headers.get('X-API-Key')
           if api_key != os.getenv('API_KEY'):
               return jsonify({"error": "Unauthorized"}), 401
   ```

## 🧩 Integration Examples

### React Frontend

```javascript
import React, { useState, useEffect } from 'react';

const MultiAgentStockAnalyzer = ({ symbol }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState('technical');
  
  // Fetch individual agent analysis
  const fetchAgent = async (agentType) => {
    setLoading(true);
    const response = await fetch(`http://localhost:5000/api/agents/${agentType}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stock_symbol: symbol })
    });
    const data = await response.json();
    setAnalysis(data);
    setLoading(false);
  };
  
  // Fetch full orchestrator analysis
  const fetchFullAnalysis = async () => {
    setLoading(true);
    const response = await fetch('http://localhost:5000/api/orchestrator/full-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stock_symbol: symbol })
    });
    const data = await response.json();
    setAnalysis(data);
    setLoading(false);
  };
  
  return (
    <div className="stock-analyzer">
      <h1>{symbol} Stock Analysis</h1>
      
      <div className="agent-tabs">
        <button onClick={() => fetchAgent('technical-analysis')}>Technical</button>
        <button onClick={() => fetchAgent('fundamental-analysis')}>Fundamental</button>
        <button onClick={() => fetchAgent('fraud-detection')}>Fraud Detection</button>
        <button onClick={() => fetchAgent('fraud-analysis')}>Fraud Analysis</button>
        <button onClick={fetchFullAnalysis}>Full Analysis (All 11 Agents)</button>
      </div>
      
      {loading && <div className="spinner">Loading...</div>}
      
      {analysis && (
        <div className="results">
          <h2>{analysis.agent}</h2>
          <pre>{JSON.stringify(analysis, null, 2)}</pre>
          
          {analysis.agents && (
            <div className="summary">
              <h3>Summary</h3>
              <p>{analysis.agents.summary.summary}</p>
              
              <h3>Investment Recommendations</h3>
              <p>{analysis.agents.investment_recommendations.recommendations}</p>
            </div>
          )}
          
          <button onClick={() => downloadPDF(symbol)}>Download PDF Report</button>
        </div>
      )}
    </div>
  );
};

const downloadPDF = async (symbol) => {
  const response = await fetch('http://localhost:5000/api/pdf/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stock_symbol: symbol })
  });
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${symbol}_analysis.pdf`;
  a.click();
};

export default MultiAgentStockAnalyzer;
```

### Python Portfolio Analyzer

```python
import requests
import pandas as pd
from datetime import datetime

class MultiAgentPortfolioAnalyzer:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
    
    def analyze_stock(self, symbol, agents=None):
        """
        Analyze a stock using specific agents or all agents.
        
        Args:
            symbol: Stock ticker
            agents: List of agent names or None for all
        
        Returns:
            Dictionary with agent results
        """
        if agents is None:
            # Use orchestrator for all agents
            response = requests.post(
                f'{self.base_url}/api/orchestrator/full-analysis',
                json={'stock_symbol': symbol}
            )
            return response.json()
        
        # Fetch specific agents
        results = {'stock_symbol': symbol, 'agents': {}}
        for agent in agents:
            response = requests.post(
                f'{self.base_url}/api/agents/{agent}',
                json={'stock_symbol': symbol}
            )
            if response.status_code == 200:
                results['agents'][agent] = response.json()
        
        return results
    
    def analyze_portfolio(self, symbols):
        """Analyze multiple stocks and return DataFrame."""
        data = []
        for symbol in symbols:
            print(f"Analyzing {symbol}...")
            result = self.analyze_stock(symbol, 
                agents=['technical-analysis', 'fundamental-analysis', 'fraud-detection'])
            
            row = {
                'Symbol': symbol,
                'RSI': result['agents']['technical-analysis']['technical_indicators']['rsi'],
                'RSI_Signal': result['agents']['technical-analysis']['technical_indicators']['rsi_signal'],
                'MACD_Signal': result['agents']['technical-analysis']['technical_indicators']['macd_signal'],
                'P/E': result['agents']['fundamental-analysis']['fundamentals']['pe_ratio'],
                'Quality': result['agents']['fundamental-analysis']['fundamentals']['quality_score'],
                'Fraud_Risk': result['agents']['fraud-detection']['fraud_indicators']['risk_level']
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def generate_pdf_reports(self, symbols, output_dir='reports'):
        """Generate PDF reports for multiple stocks."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for symbol in symbols:
            print(f"Generating PDF for {symbol}...")
            response = requests.post(
                f'{self.base_url}/api/pdf/generate',
                json={'stock_symbol': symbol}
            )
            
            if response.status_code == 200:
                filename = f"{output_dir}/{symbol}_analysis_{datetime.now().strftime('%Y%m%d')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Saved: {filename}")

# Usage
analyzer = MultiAgentPortfolioAnalyzer()

# Analyze single stock with all agents
aapl_full = analyzer.analyze_stock('AAPL')
print(aapl_full['agents']['summary']['summary'])

# Analyze portfolio with specific agents
portfolio = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA']
df = analyzer.analyze_portfolio(portfolio)
print(df)

# Generate PDF reports
analyzer.generate_pdf_reports(portfolio)
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="Stock Analyzer Gateway")

class StockRequest(BaseModel):
    symbol: str
    agents: list[str] = None

ANALYZER_URL = 'http://localhost:5000'

@app.post("/analyze")
async def analyze_stock(request: StockRequest):
    """Gateway endpoint that aggregates multi-agent analysis."""
    
    if request.agents is None:
        # Full orchestrator analysis
        response = requests.post(
            f'{ANALYZER_URL}/api/orchestrator/full-analysis',
            json={'stock_symbol': request.symbol}
        )
    else:
        # Fetch specific agents
        results = {'stock_symbol': request.symbol, 'agents': {}}
        for agent in request.agents:
            response = requests.post(
                f'{ANALYZER_URL}/api/agents/{agent}',
                json={'stock_symbol': request.symbol}
            )
            if response.status_code == 200:
                results['agents'][agent] = response.json()
        return results
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, 
                          detail=response.json().get('error'))
    
    return response.json()

@app.get("/health")
async def health_check():
    """Check if analyzer API is reachable."""
    try:
        response = requests.get(f'{ANALYZER_URL}/api/health')
        return response.json()
    except:
        raise HTTPException(status_code=503, detail="Analyzer API unavailable")
```

### Node.js / Express Integration

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const ANALYZER_URL = 'http://localhost:5000';

// Analyze stock with all agents
app.post('/api/stock/:symbol/full-analysis', async (req, res) => {
  try {
    const { symbol } = req.params;
    const response = await axios.post(
      `${ANALYZER_URL}/api/orchestrator/full-analysis`,
      { stock_symbol: symbol }
    );
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Analyze with specific agents
app.post('/api/stock/:symbol/agents', async (req, res) => {
  try {
    const { symbol } = req.params;
    const { agents } = req.body; // Array of agent names
    
    const results = { stock_symbol: symbol, agents: {} };
    
    for (const agent of agents) {
      const response = await axios.post(
        `${ANALYZER_URL}/api/agents/${agent}`,
        { stock_symbol: symbol }
      );
      results.agents[agent] = response.data;
    }
    
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Download PDF
app.get('/api/stock/:symbol/pdf', async (req, res) => {
  try {
    const { symbol } = req.params;
    const response = await axios.post(
      `${ANALYZER_URL}/api/pdf/generate`,
      { stock_symbol: symbol },
      { responseType: 'arraybuffer' }
    );
    
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=${symbol}_analysis.pdf`);
    res.send(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Gateway running on port 3000');
});
```

## 🐛 Troubleshooting

### API Won't Start
**Problem**: `Address already in use` error
```bash
# Solution: Find and kill process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Or use a different port
python stock_analyzer_agents_api.py --port 8080
```

**Problem**: `ModuleNotFoundError` for packages
```bash
# Solution: Install all requirements
pip install -r requirements.txt

# Verify installations
pip list | grep -E "flask|openai|beautifulsoup4|reportlab"
```

**Problem**: Azure OpenAI credentials not found
```bash
# Solution: Check .env file exists
ls -la .env

# Verify variables are set
cat .env

# Ensure proper format (no spaces around =)
AZURE_OPENAI_API_KEY2=your_key_here
AZURE_OPENAI_ENDPOINT2=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT2_NAME=gpt-4.1
```

### Agent Analysis Fails

**Problem**: Technical analysis returns error
```
Error: Insufficient historical data
```
```bash
# Solution: Stock may be newly listed or delisted
# Try a well-established stock like AAPL, MSFT, NVDA
# Verify stock symbol is valid on StockAnalysis.com
```

**Problem**: Fundamental analysis missing financial data
```
Error: Could not fetch stock data
```
```bash
# Solution: 
# 1. Check internet connection
# 2. Verify StockAnalysis.com is accessible
# 3. Stock may be on different exchange (only NASDAQ/NYSE supported)
```

**Problem**: Fraud detection insufficient data
```
Error: Insufficient historical data (need at least 20 days)
```
```bash
# Solution: Stock needs 20+ days of trading history
# Use established stocks with sufficient trading history
```

**Problem**: News fetching returns 0 articles
```
DEBUG: Found 0 news articles
```
```bash
# Solution: 
# 1. Stock may not have recent news coverage
# 2. News sources may have changed their URL structure
# 3. Check fetch_news_articles() function scraping logic
# 4. Verify major news domains are accessible
```

### PDF Generation Errors

**Problem**: `ReportLab not found`
```bash
# Solution: Install reportlab
pip install reportlab

# Verify installation
python -c "import reportlab; print(reportlab.Version)"
```

**Problem**: Logo not loading in PDF
```bash
# Solution: 
# 1. Logo URL may be unreachable (Clearbit API)
# 2. Check company_info has valid domain
# 3. Ensure internet connection for logo fetch
# 4. PDF will still generate without logo
```

**Problem**: PDF download fails with 500 error
```bash
# Solution: Check orchestrator endpoint works first
curl -X POST http://localhost:5000/api/orchestrator/full-analysis \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol": "AAPL"}'

# If orchestrator works, PDF should work
# Check console logs for specific error
```

### Performance Issues

**Problem**: Orchestrator takes too long (>2 minutes)
```bash
# Solution: Normal for first run (data fetching + 11 agents)
# Expected time: 60-90 seconds
# If longer:
# 1. Check internet connection speed
# 2. Verify Azure OpenAI endpoint latency
# 3. Consider caching results
```

**Problem**: Timeout errors from Azure OpenAI
```bash
# Solution: Increase timeout in client initialization
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY2"),
    api_version="2024-10-21",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT2"),
    timeout=60.0  # Increase from default 30 seconds
)
```

### Data Quality Issues

**Problem**: Technical indicators seem inaccurate
```bash
# Solution: 
# 1. Verify historical data is correctly fetched
# 2. Temperature is set to 0 for mathematical precision
# 3. Check if LLM is using correct formulas
# 4. Compare with main stock_analyzer.py results
```

**Problem**: Fundamental metrics missing or null
```bash
# Solution:
# 1. Not all stocks have complete financial data
# 2. Check if financial_data fetch succeeded
# 3. LLM may return null for unavailable metrics
# 4. Verify stock has filed recent 10-K/10-Q
```

**Problem**: Fraud detection shows no spikes but visually see spikes
```bash
# Solution:
# 1. TVR threshold is 3x (adjust if needed)
# 2. Recent 5 days excluded from baseline calculation
# 3. Check volume data quality (may have 'N/A' values)
# 4. Verify abnormal return standard deviation calculation
```

## 🔬 Testing & Validation

### Unit Testing Individual Agents

```python
import unittest
import requests

class TestStockAnalyzerAPI(unittest.TestCase):
    BASE_URL = 'http://localhost:5000'
    TEST_SYMBOL = 'AAPL'
    
    def test_health_endpoint(self):
        response = requests.get(f'{self.BASE_URL}/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_technical_analysis(self):
        response = requests.post(
            f'{self.BASE_URL}/api/agents/technical-analysis',
            json={'stock_symbol': self.TEST_SYMBOL}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('technical_indicators', data)
        self.assertIn('rsi', data['technical_indicators'])
        self.assertIsInstance(data['technical_indicators']['rsi'], (int, float))
    
    def test_fundamental_analysis(self):
        response = requests.post(
            f'{self.BASE_URL}/api/agents/fundamental-analysis',
            json={'stock_symbol': self.TEST_SYMBOL}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('fundamentals', data)
        self.assertIn('quality_score', data['fundamentals'])
    
    def test_fraud_detection(self):
        response = requests.post(
            f'{self.BASE_URL}/api/agents/fraud-detection',
            json={'stock_symbol': self.TEST_SYMBOL}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('fraud_indicators', data)
        self.assertIn('risk_level', data['fraud_indicators'])
    
    def test_orchestrator(self):
        response = requests.post(
            f'{self.BASE_URL}/api/orchestrator/full-analysis',
            json={'stock_symbol': self.TEST_SYMBOL}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('agents', data)
        self.assertEqual(len(data['agents']), 11)
    
    def test_invalid_symbol(self):
        response = requests.post(
            f'{self.BASE_URL}/api/agents/technical-analysis',
            json={'stock_symbol': 'INVALID999'}
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
```

### Load Testing

```python
import concurrent.futures
import requests
import time

def test_agent(agent_type, symbol):
    """Test individual agent performance."""
    start = time.time()
    response = requests.post(
        f'http://localhost:5000/api/agents/{agent_type}',
        json={'stock_symbol': symbol}
    )
    duration = time.time() - start
    return {
        'agent': agent_type,
        'symbol': symbol,
        'status': response.status_code,
        'duration': duration
    }

# Test concurrent requests
symbols = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA']
agents = ['technical-analysis', 'fundamental-analysis', 'fraud-detection']

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for symbol in symbols:
        for agent in agents:
            futures.append(executor.submit(test_agent, agent, symbol))
    
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

# Analyze results
import pandas as pd
df = pd.DataFrame(results)
print(df.groupby('agent')['duration'].describe())
```

## 🔮 Future Enhancements

### Planned Features

- [ ] **Authentication & Authorization**
  - API key-based authentication
  - User-specific rate limiting
  - Role-based access control (admin, premium, free tier)

- [ ] **Caching Layer**
  - Redis caching for repeated stock queries
  - TTL-based cache invalidation (5-15 minutes)
  - Cache warming for popular stocks

- [ ] **WebSocket Support**
  - Real-time updates for stock prices
  - Live agent execution progress
  - Streaming LLM responses

- [ ] **Batch Analysis**
  - Multi-stock batch endpoint
  - Portfolio-level analysis
  - Comparative analysis across stocks

- [ ] **Advanced Technical Indicators**
  - Fibonacci retracements
  - Ichimoku Cloud
  - Elliott Wave patterns
  - Volume-weighted indicators

- [ ] **Multi-Exchange Support**
  - NYSE, LSE, TSE, HKEX
  - Cryptocurrency (BTC, ETH)
  - Forex pairs

- [ ] **Enhanced Fraud Detection**
  - Machine learning models
  - Pattern recognition algorithms
  - Historical fraud case database
  - Regulatory filing analysis

- [ ] **Email & Notifications**
  - Automated email delivery of PDF reports
  - Price alert notifications
  - Fraud alert notifications
  - Daily/weekly digest emails

- [ ] **Database Integration**
  - PostgreSQL for historical analysis storage
  - MongoDB for unstructured data (news, articles)
  - TimescaleDB for time-series price data

- [ ] **Advanced Analytics**
  - Options analysis (Greeks, IV)
  - Sentiment analysis from social media
  - Insider trading detection
  - SEC filing analysis

- [ ] **UI Dashboard**
  - React-based frontend
  - Interactive charts (Chart.js, D3.js)
  - Real-time updates
  - Mobile responsive

### Contribution Guidelines

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Coding Standards:**
- Follow PEP 8 for Python code
- Add docstrings to all functions
- Include unit tests for new features
- Update README with new endpoints

## 📄 License

MIT License - feel free to use and modify for your needs.

## 👤 Author

**Vinay Jain**
- Email: vinex22@gmail.com, vinayjain@microsoft.com
- GitHub: [Stock Analyzer Multi-Agent API](https://github.com/yourusername/stock-analyzer-api)

## 🙏 Acknowledgments

- **Azure OpenAI**: GPT-4 powers all LLM-based agents
- **StockAnalysis.com**: Financial data, historical prices, analyst forecasts
- **Google Finance**: Real-time stock prices
- **News Sources**: MarketWatch, CNBC, Reuters, Bloomberg, Forbes, Barrons, Benzinga, Motley Fool, Invezz
- **Clearbit Logo API**: Company logo fetching

## 📚 Technical Stack

**Backend:**
- Flask 2.3+
- Flask-CORS
- Python 3.8+

**AI/ML:**
- Azure OpenAI GPT-4
- OpenAI Python SDK 1.0+

**Data Processing:**
- BeautifulSoup4 (web scraping)
- Requests (HTTP client)
- JSON (data serialization)
- Regular Expressions (text parsing)

**PDF Generation:**
- ReportLab (PDF creation)
- PIL/Pillow (image processing for logos)

**Development:**
- Python dotenv (environment management)
- Datetime (timestamp handling)
- BytesIO (in-memory file handling)

## 🎯 Use Cases

### For Individual Investors
- **Quick Analysis**: Get instant technical and fundamental insights
- **Fraud Detection**: Identify potential manipulation or insider trading
- **Investment Decisions**: 1-week, 6-month, 2-year recommendations
- **PDF Reports**: Professional reports for records/sharing

### For Financial Advisors
- **Portfolio Screening**: Batch analyze multiple client holdings
- **Risk Assessment**: Fraud detection across portfolio
- **Client Reports**: Generate branded PDF reports
- **Due Diligence**: Comprehensive 11-agent analysis

### For Researchers
- **Academic Research**: Study fraud detection algorithms
- **Backtesting**: Compare technical indicators vs actual performance
- **Pattern Analysis**: Identify market manipulation patterns
- **API Integration**: Build custom research tools

### For Developers
- **Integration**: Embed stock analysis in applications
- **Automation**: Schedule daily/weekly analysis
- **Custom Dashboards**: Build real-time monitoring tools
- **Learning**: Study multi-agent AI architectures

## 📊 Agent Comparison Matrix

| Agent | Type | Temperature | Max Tokens | Execution Time | Data Sources |
|-------|------|-------------|------------|----------------|--------------|
| Technical Analysis | LLM | 0 | 1000 | ~5-8s | Historical prices (30d) |
| Fundamental Analysis | LLM | 0 | 800 | ~8-12s | Financial data, ratios, forecasts |
| Company Name | LLM | Default | 50 | ~2-3s | Stock symbol |
| Fraud Detection | Mathematical | N/A | N/A | ~3-5s | Historical prices + volume |
| Fraud Analysis | LLM | 0.3 | 2000 | ~10-15s | Fraud indicators + news |
| Summary | LLM | Default | 200 | ~3-5s | All core agents |
| Executive Summary | LLM | Default | 800 | ~3-5s | All core agents |
| Detailed Analysis | LLM | Default | 1500 | ~4-6s | All core agents |
| Investment Recommendations | LLM | Default | 2000 | ~4-6s | All core agents |
| Analyst Synthesis | LLM | Default | 1500 | ~4-6s | All core agents |
| Meta-Analysis | LLM | Default | 2000 | ~4-6s | All core agents |

**Total Orchestrator Time**: ~60-90 seconds (includes data fetching: ~15-20s)

## 🔍 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT REQUEST                        │
│              POST /api/orchestrator/full-analysis        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              DATA FETCHING LAYER (Parallel)              │
├─────────────────────────────────────────────────────────┤
│  • fetch_stock_data() → Google Finance                  │
│  • fetch_historical_data() → StockAnalysis.com          │
│  • fetch_financial_data() → StockAnalysis.com           │
│  • fetch_forecast_data() → StockAnalysis.com            │
│  • fetch_news_articles() → News aggregation             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            CORE ANALYSIS AGENTS (Sequential)             │
├─────────────────────────────────────────────────────────┤
│  Agent 1: Technical Analysis                             │
│    ├─ Input: historical_data (30 days OHLCV)            │
│    ├─ LLM: Calculate SMA, EMA, RSI, MACD, BB            │
│    └─ Output: Technical indicators with signals          │
│                                                          │
│  Agent 2: Fundamental Analysis                           │
│    ├─ Input: stock_data + financial_data + forecasts    │
│    ├─ LLM: Calculate P/E, ROE, D/E, quality score       │
│    └─ Output: Fundamental metrics + valuation            │
│                                                          │
│  Agent 3: Company Name                                   │
│    ├─ Input: stock_symbol                                │
│    ├─ LLM: Identify company name and domain             │
│    └─ Output: Company info + logo URL                    │
│                                                          │
│  Agent 4: Fraud Detection (Mathematical)                 │
│    ├─ Input: historical_data (20+ days)                  │
│    ├─ Calculate: TVR, AR, CAR, red flags                │
│    └─ Output: Fraud indicators with severity            │
│                                                          │
│  Agent 5: Fraud Analysis (LLM)                           │
│    ├─ Input: fraud_indicators + stock_data + news       │
│    ├─ LLM: 6-section structured risk assessment         │
│    └─ Output: Comprehensive fraud analysis              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              CONTEXT BUILDING                            │
├─────────────────────────────────────────────────────────┤
│  Aggregate results from Agents 1-5 into context string  │
│  Include: technical signals, fundamentals, fraud status  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         SUMMARY & SYNTHESIS AGENTS (Sequential)          │
├─────────────────────────────────────────────────────────┤
│  Agent 6: Summary (200 tokens)                           │
│  Agent 7: Executive Summary (800 tokens)                 │
│  Agent 8: Detailed Analysis (1500 tokens)                │
│  Agent 9: Investment Recommendations (2000 tokens)       │
│  Agent 10: Analyst Synthesis (1500 tokens)               │
│  Agent 11: Meta-Analysis (2000 tokens)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  JSON RESPONSE                           │
├─────────────────────────────────────────────────────────┤
│  {                                                       │
│    "orchestrator": "Multi-Agent Stock Analyzer",        │
│    "stock_symbol": "AAPL",                               │
│    "timestamp": "2025-12-06T10:30:00",                   │
│    "stock_data": { ... },                                │
│    "company_info": { ... },                              │
│    "news_articles": [ ... ],                             │
│    "agents": {                                           │
│      "technical_analysis": { ... },                      │
│      "fundamental_analysis": { ... },                    │
│      "fraud_detection": { ... },                         │
│      "fraud_analysis": { ... },                          │
│      "summary": { ... },                                 │
│      "executive_summary": { ... },                       │
│      "detailed_analysis": { ... },                       │
│      "investment_recommendations": { ... },              │
│      "analyst_synthesis": { ... },                       │
│      "meta_analysis": { ... }                            │
│    }                                                     │
│  }                                                       │
└─────────────────────────────────────────────────────────┘
```

## ⚠️ Disclaimer

**IMPORTANT - READ CAREFULLY:**

This API is provided for **informational and educational purposes only**. It does **NOT** constitute:
- Financial advice
- Investment recommendations
- Professional consultation
- Trading signals

**Key Points:**
1. **No Financial Advice**: The analyses, recommendations, and insights provided by this API are generated by AI models and mathematical algorithms. They are not personalized financial advice tailored to your specific situation.

2. **Not a Substitute for Professional Advice**: Always consult with a qualified financial advisor, CPA, or investment professional before making any investment decisions.

3. **Past Performance**: Historical data and backtested results do not guarantee future performance. Markets are unpredictable and subject to numerous factors.

4. **Risk of Loss**: All investments carry risk, including the potential loss of principal. Never invest more than you can afford to lose.

5. **No Guarantees**: The fraud detection algorithms may produce false positives or miss actual fraudulent activity. No system is perfect.

6. **Data Accuracy**: While we strive for accuracy, data fetched from external sources may be incomplete, delayed, or incorrect. Always verify information from official sources.

7. **AI Limitations**: LLM-generated analyses may contain errors, biases, or hallucinations. Use critical thinking and cross-reference with multiple sources.

8. **Regulatory Compliance**: Users are responsible for ensuring their use of this API complies with all applicable securities laws and regulations in their jurisdiction.

9. **Not for High-Frequency Trading**: This API is not designed or suitable for algorithmic trading or high-frequency trading strategies.

10. **Use at Your Own Risk**: By using this API, you acknowledge and accept all risks associated with investment decisions based on the information provided.

**For Professional Use**: If you are a financial advisor or institution using this API, ensure you have proper compliance procedures and disclosures in place.

---

**Built with:**
- Flask & Flask-CORS
- Azure OpenAI GPT-4
- Python 3.8+
- BeautifulSoup4
- ReportLab
- StockAnalysis.com API (unofficial scraping)
- Google Finance (unofficial scraping)

**Version**: 2.0.0 (Multi-Agent Architecture)  
**Last Updated**: December 6, 2025  
**API Status**: Production Ready
