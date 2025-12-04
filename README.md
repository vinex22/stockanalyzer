# 📈 AI-Powered Stock Analyzer

A comprehensive stock analysis tool that leverages Azure OpenAI GPT-4 to provide intelligent insights, investment recommendations, and professional PDF reports for any NASDAQ-listed stock.

## ✨ Features

### 📊 Data Collection
- **Real-time Stock Data**: Fetches current price, market cap, P/E ratio, and more from Google Finance
- **30-Day Historical Prices**: Retrieves OHLC (Open, High, Low, Close) data from StockAnalysis.com
- **Analyst Forecasts**: Gathers consensus ratings, price targets, and revenue/EPS forecasts
- **News Analysis**: Scrapes and analyzes 15+ recent news articles from major financial sources (CNBC, Reuters, Forbes, MarketWatch, etc.)
- **Company Logos**: Automatically fetches company logos for professional branding

### 🤖 AI-Powered Analysis
Generates 5 comprehensive AI-driven reports using Azure OpenAI GPT-4:

1. **Short Summary** (2-3 sentences)
   - Quick snapshot of current stock status

2. **Executive Summary** (8-12 sentences)
   - Stock performance and valuation
   - Price trends and volatility
   - News sentiment analysis
   - Risk factors and opportunities

3. **Detailed Analysis**
   - Week-by-week price movement analysis
   - News impact assessment with specific price correlations
   - Fundamental analysis (P/E ratios, market positioning)
   - Risk-reward analysis

4. **Investment Recommendations**
   - **1 Week** (Short-term trading): Entry/exit points, stop-loss levels, technical analysis
   - **6 Months** (Medium-term): Price targets, earnings milestones, portfolio allocation
   - **2 Years** (Long-term): Strategic positioning, growth drivers, DCA strategies

5. **Analyst Ratings & Recommendations**
   - Consensus overview with rating distribution
   - Price target analysis (bull/bear scenarios)
   - Representative analyst perspectives from major firms
   - Revenue and earnings outlook

### 📄 PDF Report Generation
Creates professional, publication-ready PDF reports featuring:
- Company logo on title page
- Color-coded sections and tables
- Historical price tables
- Analyst forecast summaries
- Clean, narrative-style formatting
- Proper page breaks and section organization

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Azure OpenAI API access

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/vinex22/stockanalyzer.git
cd stockanalyzer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Azure OpenAI**

Create a `.env` file in the project root:
```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT2_NAME=gpt-4.1
```

## 📦 Dependencies

```
requests>=2.31.0
beautifulsoup4>=4.12.0
openai>=1.0.0
python-dotenv>=1.0.0
reportlab>=4.0.0
```

## 💻 Usage

### Basic Usage

Run the analyzer (currently configured for NVDA):
```bash
python stock_analyzer.py
```

### Customize Stock Symbol

Edit line 1284 in `stock_analyzer.py`:
```python
stock_symbol = "NVDA"  # Change to your desired stock symbol
```

Supported stocks: Any NASDAQ-listed company (AAPL, MSFT, GOOGL, TSLA, META, AMZN, etc.)

### Output

The script generates:
1. **Console Output**: Formatted analysis with sections, tables, and insights
2. **PDF Report**: `stock_analysis_SYMBOL_TIMESTAMP.pdf` in the current directory

## 📊 Sample Output

```
============================================================
📈 STOCK PRICE ANALYZER
============================================================

🔍 Fetching data for NVDA...

📊 STOCK DATA:
------------------------------------------------------------
Company: NVIDIA Corporation
Symbol: NVDA
Current Price: $140.15
Change: 📈 +2.34%
Market Cap: 3.45T USD
P/E Ratio: 68.42

📅 LAST 30 TRADING DAYS:
[Historical price table...]

📈 ANALYST FORECASTS & PRICE TARGETS
------------------------------------------------------------
Analyst Coverage: 42 analysts
Consensus Rating: Strong Buy
Average Price Target: $165.50 (18.1% upside potential)

📰 FETCHING NEWS ARTICLES...
✅ Found 15 news articles
[News analysis...]

📊 GENERATING COMPREHENSIVE ANALYSIS
[AI-generated insights...]

📄 GENERATING PDF REPORT...
✅ PDF Report generated: stock_analysis_NVDA_20251205_010345.pdf
```

## 🛠️ Architecture

### Data Flow
```
User Input → Stock Symbol
    ↓
Google Finance → Current Stock Data
StockAnalysis.com → Historical Data + Forecasts + News URLs
News Sites → Article Content
    ↓
Data Aggregation → Comprehensive Summary
    ↓
Azure OpenAI GPT-4 → 5 AI-Generated Reports
    ↓
ReportLab → Professional PDF
```

### Key Functions

- `fetch_stock_data()`: Scrapes Google Finance for current metrics
- `fetch_historical_data()`: Retrieves 30-day OHLC data
- `fetch_forecast_data()`: Extracts analyst forecasts
- `fetch_news_urls()`: Finds relevant news articles
- `fetch_article_content()`: Scrapes article text with site-specific headers
- `generate_executive_summary()`: Orchestrates 5 AI analysis generations
- `generate_pdf_report()`: Creates professional PDF with tables and formatting

## 🎯 Use Cases

- **Individual Investors**: Get comprehensive analysis before making investment decisions
- **Financial Advisors**: Generate professional reports for clients
- **Research Analysts**: Quickly synthesize information from multiple sources
- **Educational**: Learn about stock analysis and AI-powered insights
- **Portfolio Management**: Track and analyze multiple stocks systematically

## 🔒 Security & Best Practices

- ✅ Environment variables for API keys (never commit `.env`)
- ✅ Rate limiting (1 second between article fetches)
- ✅ Error handling for all API calls
- ✅ Site-specific headers to respect website policies
- ✅ Timeout configurations (5-15 seconds)

## 🌟 Advanced Features

### Logo Support
Automatically fetches company logos for 20+ major companies:
- AAPL (Apple), MSFT (Microsoft), GOOGL (Google)
- AMZN (Amazon), META (Meta), TSLA (Tesla)
- NVDA (Nvidia), NFLX (Netflix), DIS (Disney)
- And more...

### News Source Filtering
Prioritizes reputable financial news sources:
- CNBC, Reuters, Bloomberg
- MarketWatch, Barron's, Forbes
- Motley Fool, Benzinga, Invezz

### PDF Formatting
- Company logo on cover
- Color-coded sections (blue theme)
- Professional tables with alternating row colors
- Proper text wrapping and pagination
- KeepTogether sections to prevent awkward breaks

## 🐛 Troubleshooting

### Common Issues

**"Could not fetch data for SYMBOL"**
- Verify stock is listed on NASDAQ
- Check internet connection
- Ensure stock symbol is correct (uppercase)

**"Error generating summaries"**
- Verify Azure OpenAI credentials in `.env`
- Check API quota and rate limits
- Ensure deployment name matches your Azure setup

**"Could not fetch logo"**
- Logo service may be temporarily unavailable
- Script continues without logo (non-critical)

**PDF generation fails**
- Check reportlab installation: `pip install reportlab`
- Ensure write permissions in current directory

## 📈 Future Enhancements

- [ ] Support for NYSE and other exchanges
- [ ] Interactive CLI with argument parsing
- [ ] Multiple stock comparison reports
- [ ] Technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Email delivery of reports
- [ ] Scheduled analysis (daily/weekly)
- [ ] Web dashboard interface
- [ ] Export to Excel/CSV

## 📝 License

MIT License - feel free to use and modify for your needs.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 👤 Author

**Vinay Jain**
- Email: vinex22@gmail.com, vinayjain@microsoft.com

Created with ❤️ using Azure OpenAI GPT-4 and Python

## ⚠️ Disclaimer

**This tool is for informational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions. Past performance is not indicative of future results.**

---

**Built with:**
- Azure OpenAI GPT-4
- Python
- BeautifulSoup4
- ReportLab
- Google Finance & StockAnalysis.com APIs
