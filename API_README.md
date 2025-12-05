# Stock Analyzer API

A Flask-based REST API that provides AI-powered stock analysis and PDF report generation using Azure OpenAI.

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
python stock_analyzer_api.py
```

The API will start on `http://localhost:5000`

## 📡 API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00"
}
```

---

### 2. Full Stock Analysis
**POST** `/api/analyze`

Get comprehensive AI-powered stock analysis.

**Request Body:**
```json
{
  "symbol": "NVDA",
  "include_pdf": false
}
```

**Parameters:**
- `symbol` (required): Stock ticker symbol (e.g., "NVDA", "AAPL", "MSFT")
- `include_pdf` (optional): Set to `true` to indicate PDF is available for download

**Response:**
```json
{
  "symbol": "NVDA",
  "timestamp": "2025-12-05T10:30:00",
  "stock_data": {
    "symbol": "NVDA",
    "price": "$500.25",
    "market_cap": "$1.2T",
    "pe_ratio": "45.2",
    "dividend_yield": "0.5%"
  },
  "historical_data": [
    {
      "date": "Dec 04, 2025",
      "open": "$498.50",
      "high": "$502.00",
      "low": "$495.00",
      "close": "$500.25"
    }
  ],
  "forecast_data": {
    "analyst_count": "42",
    "consensus": "Buy",
    "price_target": "$550"
  },
  "news_count": 15,
  "analyses": {
    "short_summary": "...",
    "executive_summary": "...",
    "detailed_analysis": "...",
    "recommendations": "...",
    "analyst_ratings": "..."
  },
  "pdf_available": true,
  "pdf_endpoint": "/api/analyze/NVDA/pdf"
}
```

---

### 3. Download PDF Report
**GET** `/api/analyze/<symbol>/pdf`

Generate and download a comprehensive PDF report for the specified stock.

**Example:**
```
GET http://localhost:5000/api/analyze/NVDA/pdf
```

**Response:**
- Downloads a PDF file: `stock_analysis_NVDA_20251205_103000.pdf`

---

### 4. Quick Summary
**GET** `/api/quick-summary/<symbol>`

Get basic stock information quickly without full AI analysis.

**Example:**
```
GET http://localhost:5000/api/quick-summary/NVDA
```

**Response:**
```json
{
  "symbol": "NVDA",
  "timestamp": "2025-12-05T10:30:00",
  "current_price": "$500.25",
  "market_cap": "$1.2T",
  "pe_ratio": "45.2",
  "recent_prices": [
    {
      "date": "Dec 04, 2025",
      "open": "$498.50",
      "close": "$500.25"
    }
  ]
}
```

## 🧪 Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Quick summary
curl http://localhost:5000/api/quick-summary/NVDA

# Full analysis
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NVDA", "include_pdf": true}'

# Download PDF
curl http://localhost:5000/api/analyze/NVDA/pdf --output nvda_report.pdf
```

### Using Python

```python
import requests

# Full analysis
response = requests.post('http://localhost:5000/api/analyze', 
                        json={'symbol': 'NVDA', 'include_pdf': True})
data = response.json()
print(data['analyses']['short_summary'])

# Download PDF
response = requests.get('http://localhost:5000/api/analyze/NVDA/pdf')
with open('nvda_report.pdf', 'wb') as f:
    f.write(response.content)
```

### Using JavaScript/Fetch

```javascript
// Full analysis
fetch('http://localhost:5000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbol: 'NVDA', include_pdf: true })
})
.then(response => response.json())
.then(data => console.log(data.analyses.short_summary));

// Quick summary
fetch('http://localhost:5000/api/quick-summary/NVDA')
.then(response => response.json())
.then(data => console.log(data));
```

## 🏗️ Architecture

```
Client Request
    ↓
Flask API Server
    ↓
├── Data Collection Layer
│   ├── Google Finance (Current Price)
│   ├── StockAnalysis.com (Historical & Forecast)
│   └── News Sources (15 articles)
    ↓
├── AI Analysis Layer
│   └── Azure OpenAI GPT-4
│       ├── Short Summary
│       ├── Executive Summary
│       ├── Detailed Analysis
│       ├── Investment Recommendations
│       └── Analyst Ratings
    ↓
├── Response Layer
│   ├── JSON Response
│   └── PDF Generation (Optional)
    ↓
Client Response
```

## 📊 Features

### Data Collection
- **Real-time Pricing**: Current stock price from Google Finance
- **Historical Data**: 30-day price history (Open, High, Low, Close)
- **Analyst Forecasts**: Consensus ratings and price targets
- **News Analysis**: 15 recent articles from major financial news sources
- **Company Logos**: Automatic logo fetching for 20+ major companies

### AI Analysis (5 Reports)
1. **Short Summary**: 2-3 sentence overview
2. **Executive Summary**: 8-12 sentence comprehensive summary
3. **Detailed Analysis**: In-depth news impact assessment
4. **Investment Recommendations**: 1-week, 6-month, 2-year outlook
5. **Analyst Ratings**: Consensus from major firms

### PDF Reports
- Professional formatting with company logo
- Custom color scheme and typography
- Stock data tables and historical charts
- All AI analyses included
- Timestamped and source-attributed

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
# In stock_analyzer_api.py

# Change port
app.run(debug=True, host='0.0.0.0', port=8080)

# Disable debug mode for production
app.run(debug=False, host='0.0.0.0', port=5000)

# Customize article count
news_urls = fetch_news_urls(stock_symbol, max_articles=20)
```

## 🛡️ Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Missing or invalid stock symbol
- **404 Not Found**: Stock symbol not found or data unavailable
- **500 Internal Server Error**: Analysis generation or PDF creation failed

**Example Error Response:**
```json
{
  "error": "Stock symbol is required"
}
```

## 🚀 Deployment

### Development
```bash
python stock_analyzer_api.py
```

### Production (Using Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 stock_analyzer_api:app
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY stock_analyzer_api.py .
COPY .env .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "stock_analyzer_api:app"]
```

## 📝 Rate Limiting

The API implements rate limiting for external data sources:
- 1 second delay between news article fetches
- 10-15 second timeouts for web scraping
- Graceful error handling for failed requests

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **API Keys**: Use separate keys for dev/prod
3. **CORS**: Configure allowed origins in production
4. **Input Validation**: Stock symbols are validated and sanitized
5. **Timeouts**: All external requests have timeouts

## ⚡ Performance

- **Quick Summary**: ~2-3 seconds (basic data only)
- **Full Analysis**: ~30-45 seconds (includes AI generation)
- **PDF Generation**: +5-10 seconds (adds to full analysis time)

## 🧩 Integration Examples

### React Frontend

```javascript
const StockAnalyzer = ({ symbol }) => {
  const [analysis, setAnalysis] = useState(null);
  
  useEffect(() => {
    fetch('http://localhost:5000/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol })
    })
    .then(res => res.json())
    .then(data => setAnalysis(data));
  }, [symbol]);
  
  return (
    <div>
      {analysis && (
        <>
          <h2>{analysis.symbol} - {analysis.stock_data.price}</h2>
          <p>{analysis.analyses.short_summary}</p>
          <a href={`/api/analyze/${symbol}/pdf`}>Download PDF</a>
        </>
      )}
    </div>
  );
};
```

### Python Script

```python
import requests

def analyze_portfolio(symbols):
    results = {}
    for symbol in symbols:
        response = requests.post('http://localhost:5000/api/analyze',
                               json={'symbol': symbol})
        if response.status_code == 200:
            results[symbol] = response.json()
    return results

portfolio = analyze_portfolio(['NVDA', 'AAPL', 'MSFT'])
```

## 🐛 Troubleshooting

### API Won't Start
- Check if port 5000 is available
- Verify `.env` file exists with correct credentials
- Ensure all dependencies are installed

### Analysis Fails
- Verify Azure OpenAI credentials
- Check stock symbol is valid (NASDAQ listed)
- Ensure internet connection for data fetching

### PDF Generation Errors
- Install reportlab: `pip install reportlab`
- Check disk space for temporary files
- Verify logo URLs are accessible

## 🔮 Future Enhancements

- [ ] Authentication & API keys
- [ ] Rate limiting per user
- [ ] Caching for repeated requests
- [ ] WebSocket support for real-time updates
- [ ] Batch analysis endpoint
- [ ] Technical indicators (RSI, MACD, SMA)
- [ ] Multi-exchange support (NYSE, LSE, etc.)
- [ ] Email delivery of PDF reports

## 📄 License

MIT License - feel free to use and modify for your needs.

## 👤 Author

**Vinay Jain**
- Email: vinex22@gmail.com, vinayjain@microsoft.com

## ⚠️ Disclaimer

**This API is for informational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions. Past performance is not indicative of future results.**

---

**Built with:**
- Flask & Flask-CORS
- Azure OpenAI GPT-4
- Python 3.8+
- BeautifulSoup4
- ReportLab
