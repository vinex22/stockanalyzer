# 📈 AI-Powered Stock Analyzer

A comprehensive **Multi-Agent AI System** that leverages 11 specialized AI agents powered by Azure OpenAI GPT-4 to provide intelligent insights, fraud detection, investment recommendations, and professional PDF reports for any NASDAQ-listed stock.

## ✨ Features

### 🤖 Multi-Agent AI Architecture (11 Specialized Agents)

This system employs **11 AI agents** working collaboratively to analyze stocks from multiple perspectives:

#### Data Analysis Agents
1. **Technical Analysis Agent**: Uses LLM to calculate technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
2. **Fundamental Analysis Agent**: Analyzes fundamental metrics (P/E ratios, ROE, growth rates, quality scores)
3. **Company Name Agent**: Identifies official company names and domains for accurate logo fetching

#### Risk Assessment Agents
4. **Fraud Detection Agent**: Mathematical analysis of volume spikes, abnormal returns, and pattern detection
5. **Fraud Analysis Agent**: LLM-based fraud risk assessment with news context and catalyst analysis

#### Summary & Insights Agents
6. **Summary Agent**: Generates concise 200-token summaries (2-3 sentences)
7. **Executive Summary Agent**: Creates 800-token executive overviews (8-12 sentences)
8. **Detailed Analysis Agent**: Produces 1500-token in-depth analysis with news impact assessment
9. **Investment Recommendation Agent**: Provides recommendations for 3 time horizons (1 week, 6 months, 2 years)
10. **Analyst Synthesis Agent**: Synthesizes analyst ratings, consensus, and price targets
11. **Meta-Analysis Agent**: Performs AI-powered meta-analysis (2000 tokens)

#### Orchestration
- **Multi-Agent Orchestrator**: Coordinates all 6 summary agents with shared data for comprehensive analysis

### 📊 Data Collection
- **Real-time Stock Data**: Fetches current price, market cap, P/E ratio, and more from Google Finance
- **30-Day Historical Prices**: Retrieves OHLC (Open, High, Low, Close) data from StockAnalysis.com
- **Analyst Forecasts**: Gathers consensus ratings, price targets, and revenue/EPS forecasts
- **Financial Statements**: Income statement, balance sheet, and financial ratios
- **News Analysis**: Scrapes and analyzes 15+ recent news articles from major financial sources (CNBC, Reuters, Forbes, MarketWatch, etc.)
- **AI-Powered Logo Fetching**: Uses Company Name Agent to determine official company names and fetch accurate logos

### 🚨 Fraud Detection System

Two-tier fraud detection approach:

1. **Mathematical Analysis** (Fraud Detection Agent)
   - Total Volume Ratio (TVR): Detects unusual volume spikes
   - Abnormal Return (AR): Identifies price movements deviating from market
   - Cumulative Abnormal Return (CAR): Tracks sustained suspicious patterns
   - Pattern detection with customizable thresholds

2. **AI Interpretation** (Fraud Analysis Agent - Temperature 0.3)
   - News-driven vs. no-catalyst activity distinction
   - Comprehensive risk assessment with 6 sections
   - Contextual analysis using up to 5 recent news headlines
   - Legitimate activity identification (earnings, announcements, etc.)

### 🤖 AI-Powered Analysis
Generates 6 comprehensive AI-driven reports using the Multi-Agent Orchestrator:

1. **Short Summary** (200 tokens, 2-3 sentences)
   - Quick snapshot of current stock status

2. **Executive Summary** (800 tokens, 8-12 sentences)
   - Stock performance and valuation
   - Price trends and volatility
   - News sentiment analysis
   - Risk factors and opportunities

3. **Detailed Analysis** (1500 tokens)
   - Week-by-week price movement analysis
   - News impact assessment with specific price correlations
   - Fundamental analysis (P/E ratios, market positioning)
   - Risk-reward analysis

4. **Investment Recommendations** (2000 tokens)
   - **1 Week** (Short-term trading): Entry/exit points, stop-loss levels, technical analysis
   - **6 Months** (Medium-term): Price targets, earnings milestones, portfolio allocation
   - **2 Years** (Long-term): Strategic positioning, growth drivers, DCA strategies

5. **Analyst Ratings & Recommendations** (1500 tokens)
   - Consensus overview with rating distribution
   - Price target analysis (bull/bear scenarios)
   - Representative analyst perspectives from major firms
   - Revenue and earnings outlook

6. **Meta-Analysis** (2000 tokens)
   - AI-powered synthesis of all analysis components
   - Cross-validation of insights
   - Confidence levels and uncertainty assessment

### 📄 PDF Report Generation
Creates professional, publication-ready PDF reports featuring:
- **AI-fetched company logo** on title page (using Company Name Agent)
- Color-coded sections and tables
- Historical price tables with volume formatting
- **Fraud risk assessment section** with detailed indicators
- Analyst forecast summaries
- Clean, narrative-style formatting
- Proper page breaks and section organization
- Smart bullet point parsing

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

Run the analyzer:
```bash
python stock_analyzer.py
```

You'll be prompted to enter a stock symbol:
```
📈 STOCK PRICE ANALYZER
============================================================

Enter stock symbol (e.g., NVDA, AAPL, MSFT, TSLA): NVDA
```

The analyzer will:
1. ✅ Validate the stock symbol (checks NASDAQ/NYSE)
2. 📊 Fetch real-time data from Google Finance
3. 📅 Retrieve 30-day historical prices
4. 📰 Scrape 15+ recent news articles
5. 📈 Gather analyst forecasts
6. 🤖 Generate 5 AI-powered analysis reports
7. 📄 Create a professional PDF report

### Interactive Input

The tool now features interactive input - simply run the script and enter any valid stock symbol when prompted. No need to edit code!

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

🤖 MULTI-AGENT AI ANALYSIS SYSTEM (11 Specialized Agents)
============================================================

🔄 Deploying AI Agents:
  1️⃣  Technical Analysis Agent
  2️⃣  Fundamental Analysis Agent
  3️⃣  Summary Agent
  4️⃣  Executive Summary Agent
  5️⃣  Detailed Analysis Agent
  6️⃣  Investment Recommendation Agent
  7️⃣  Analyst Synthesis Agent
  8️⃣  Meta-Analysis Agent
  9️⃣  Fraud Detection Agent
  🔟 Fraud Analysis Agent
  1️⃣1️⃣ Company Name Agent

[AI-generated insights from all agents...]

📄 GENERATING PDF REPORT...
🏢 Getting company name from AI...
✅ Company name: NVIDIA Corporation
🌐 Using domain: nvidia.com
✅ PDF Report generated: stock_analysis_NVDA_20251205_010345.pdf
```

## 🛠️ Architecture

### Multi-Agent System Design
```
User Input → Stock Symbol
    ↓
[Data Collection Layer]
Google Finance → Current Stock Data
StockAnalysis.com → Historical Data + Forecasts + News URLs + Financial Statements
News Sites → Article Content
    ↓
[Agent Layer - 11 Specialized Agents]
Technical Analysis Agent → Technical Indicators (SMA, EMA, RSI, MACD)
Fundamental Analysis Agent → Fundamental Metrics (P/E, ROE, Growth Rates)
Fraud Detection Agent → Mathematical Fraud Indicators (TVR, AR, CAR)
Fraud Analysis Agent → LLM-based Risk Assessment (with news context)
Company Name Agent → Official Company Name & Domain
    ↓
[Multi-Agent Orchestrator]
Summary Agent → 200-token summary
Executive Summary Agent → 800-token overview
Detailed Analysis Agent → 1500-token deep dive
Investment Recommendation Agent → 2000-token recommendations (3 time horizons)
Analyst Synthesis Agent → 1500-token consensus analysis
Meta-Analysis Agent → 2000-token AI meta-analysis
    ↓
[Output Layer]
ReportLab → Professional PDF with AI-fetched logo
Console → Formatted analysis with all agent outputs
```

### Key Agent Functions

#### Data Collection Agents
- `fetch_stock_data()`: Scrapes Google Finance for current metrics
- `fetch_historical_data()`: Retrieves 30-day OHLC data
- `fetch_forecast_data()`: Extracts analyst forecasts
- `fetch_financial_data()`: Gathers income statement, balance sheet, ratios
- `fetch_news_urls()`: Finds relevant news articles
- `fetch_article_content()`: Scrapes article text with site-specific headers

#### AI Analysis Agents
- `technical_analysis_agent()`: LLM calculates technical indicators
- `fundamental_analysis_agent()`: LLM analyzes fundamental metrics
- `fraud_detection_agent()`: Python-based fraud indicator calculations
- `fraud_analysis_agent()`: LLM interprets fraud risk with news context
- `get_company_name_from_llm()`: LLM determines official company name
- `summary_agent()`: LLM generates short summary
- `executive_summary_agent()`: LLM creates executive overview
- `detailed_analysis_agent()`: LLM produces detailed analysis
- `investment_recommendation_agent()`: LLM generates recommendations
- `analyst_synthesis_agent()`: LLM synthesizes analyst data
- `meta_analysis_agent()`: LLM performs meta-analysis

#### Orchestration
- `multi_agent_orchestrator()`: Coordinates all 6 summary agents with shared data
- `generate_pdf_report()`: Creates professional PDF with all agent outputs

## 🎯 Use Cases

- **Agentic AI Hackathons**: Showcase multi-agent architecture with 11 specialized agents working collaboratively
- **Individual Investors**: Get comprehensive analysis with fraud detection before making investment decisions
- **Financial Advisors**: Generate professional reports with risk assessments for clients
- **Research Analysts**: Quickly synthesize information from multiple sources with AI-powered insights
- **Educational**: Learn about stock analysis, fraud detection, and multi-agent AI systems
- **Portfolio Management**: Track and analyze multiple stocks systematically with automated agents
- **Risk Assessment**: Identify potential fraud patterns and suspicious trading activity

## 🔒 Security & Best Practices

- ✅ Environment variables for API keys (never commit `.env`)
- ✅ Rate limiting (1 second between article fetches)
- ✅ Error handling for all API calls
- ✅ Site-specific headers to respect website policies
- ✅ Timeout configurations (5-15 seconds)

## 🌟 Advanced Features

### Multi-Agent Collaboration
- **Orchestrator Pattern**: Centralized coordinator manages 6 summary agents
- **Shared Data**: All agents work with pre-prepared summary text for consistency
- **Specialized Roles**: Each agent has a single, well-defined responsibility
- **Temperature Control**: Different temperatures for analytical (0.3 for fraud) vs. creative tasks

### AI-Powered Logo Fetching
- **Company Name Agent**: LLM identifies official company names from stock symbols
- **Domain Discovery**: LLM determines correct website domains
- **Fallback System**: Manual mapping for 20+ major companies if LLM fails
- **Clearbit Integration**: Fetches high-quality logos from company domains

### Fraud Detection Intelligence
- **Mathematical Indicators**: Volume spikes, abnormal returns, cumulative patterns
- **News Context Analysis**: Distinguishes legitimate (news-driven) from suspicious (no-catalyst) activity
- **Multi-dimensional Assessment**: 6-section comprehensive risk evaluation
- **Red Flag Detection**: Pattern recognition with customizable thresholds

### News Source Filtering
Prioritizes reputable financial news sources:
- CNBC, Reuters, Bloomberg
- MarketWatch, Barron's, Forbes
- Motley Fool, Benzinga, Invezz

### PDF Formatting
- AI-fetched company logo on cover
- Color-coded sections (blue theme)
- Professional tables with alternating row colors
- Fraud risk assessment section with detailed metrics
- Proper text wrapping and pagination
- KeepTogether sections to prevent awkward breaks
- Smart bullet point parsing for narrative formatting

## 🐛 Troubleshooting

### Common Issues

**"Invalid stock symbol"**
- Stock symbol is validated before analysis begins (no LLM usage for invalid symbols)
- Only NASDAQ and NYSE symbols are supported
- Use uppercase symbols (e.g., NVDA, not nvda)

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

- [ ] Support for additional exchanges beyond NASDAQ
- [x] Interactive CLI with stock symbol prompt
- [x] Stock symbol validation before LLM usage
- [x] Multi-agent architecture with 11 specialized agents
- [x] Fraud detection system (mathematical + LLM-based)
- [x] AI-powered company name and logo fetching
- [x] Multi-agent orchestrator pattern
- [ ] Multiple stock comparison reports
- [ ] Additional technical indicators (Fibonacci retracements, Ichimoku Cloud)
- [ ] Real-time fraud alert notifications
- [ ] Agent performance metrics and monitoring
- [ ] Email delivery of reports
- [ ] Scheduled analysis (daily/weekly)
- [ ] Web dashboard interface with agent visualization
- [ ] Export to Excel/CSV
- [ ] REST API version with agent endpoints (see `stock_analyzer_api.py`)

## 🌐 API Version

A Flask-based REST API version is also available! See:
- **API Code**: `stock_analyzer_api.py`
- **API Documentation**: `API_README.md`
- **Insomnia Collection**: `Insomnia_Stock_Analyzer_API.json`
- **Testing Guide**: `INSOMNIA_GUIDE.md`

The API provides endpoints for:
- Full stock analysis (POST `/api/analyze`)
- PDF report download (GET `/api/analyze/<symbol>/pdf`)
- Quick summary (GET `/api/quick-summary/<symbol>`)
- Health check (GET `/api/health`)

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
- **Multi-Agent AI Architecture**: 11 specialized agents working collaboratively
- **Azure OpenAI GPT-4**: Powering all 11 AI agents
- **Python**: Core programming language
- **BeautifulSoup4**: Web scraping for financial data
- **ReportLab**: Professional PDF generation
- **Google Finance & StockAnalysis.com**: Real-time and historical data sources
- **Clearbit Logo API**: AI-powered company logo fetching

**Agent Architecture Highlights:**
- 🎯 **Single Responsibility**: Each agent has one well-defined task
- 🔄 **Orchestrator Pattern**: Multi-agent coordinator for summary generation
- 🤝 **Collaboration**: Shared data between agents for consistency
- 🎨 **Specialization**: Technical, fundamental, fraud, summary, and meta-analysis agents
- 🧠 **Intelligence**: 10 LLM calls per stock analysis for comprehensive insights
