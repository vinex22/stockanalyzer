# Testing Stock Analyzer API with Insomnia

## 📥 Quick Start with Insomnia

### Step 1: Start the API Server

```bash
# Navigate to the project folder
cd c:\Users\vinayjain\learn\llm_engineering\rough

# Activate your conda environment
conda activate llms

# Install Flask dependencies if not already installed
pip install flask flask-cors

# Start the API server
python stock_analyzer_api.py
```

You should see:
```
Starting Stock Analyzer API...
API Endpoints:
  POST /api/analyze - Full stock analysis
  GET /api/analyze/<symbol>/pdf - Download PDF report
  GET /api/quick-summary/<symbol> - Quick stock summary
  GET /api/health - Health check
 * Running on http://0.0.0.0:5000
```

### Step 2: Import Collection into Insomnia

1. **Open Insomnia** desktop app
2. Click on **Create** → **Import From** → **File**
3. Select the file: `Insomnia_Stock_Analyzer_API.json`
4. The collection "Stock Analyzer API" will be imported with all endpoints

### Step 3: Test the Endpoints

The collection is organized into 5 folders:

---

## 📁 Folder 1: Basic Endpoints

### ✅ Health Check
**Method:** GET  
**URL:** `http://localhost:5000/api/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00"
}
```

**How to Test:**
1. Click "Health Check" in Insomnia
2. Click "Send"
3. Should return 200 OK with status

---

### ⚡ Quick Summary
**Method:** GET  
**URL:** `http://localhost:5000/api/quick-summary/NVDA`

**Expected Response:**
```json
{
  "symbol": "NVDA",
  "timestamp": "2025-12-05T10:30:00",
  "current_price": "$500.25",
  "market_cap": "$1.2T",
  "pe_ratio": "45.2",
  "recent_prices": [...]
}
```

**How to Test:**
1. Click "Quick Summary"
2. Click "Send"
3. Returns basic data in ~2-3 seconds

**💡 Tip:** Change the stock symbol in the environment variable `stock_symbol` to test different stocks

---

## 📁 Folder 2: Full Analysis

### 🔬 Full Analysis (JSON)
**Method:** POST  
**URL:** `http://localhost:5000/api/analyze`

**Request Body:**
```json
{
  "symbol": "NVDA",
  "include_pdf": false
}
```

**Expected Response:**
```json
{
  "symbol": "NVDA",
  "timestamp": "2025-12-05T10:30:00",
  "stock_data": {...},
  "historical_data": [...],
  "forecast_data": {...},
  "news_count": 15,
  "analyses": {
    "short_summary": "...",
    "executive_summary": "...",
    "detailed_analysis": "...",
    "recommendations": "...",
    "analyst_ratings": "..."
  }
}
```

**How to Test:**
1. Click "Full Analysis (JSON)"
2. Click "Send"
3. Wait 30-45 seconds for complete analysis
4. Explore the 5 different analysis sections in the response

---

### 📄 Full Analysis (with PDF indicator)
Same as above but with `"include_pdf": true`

**Expected Response includes:**
```json
{
  ...
  "pdf_available": true,
  "pdf_endpoint": "/api/analyze/NVDA/pdf"
}
```

---

## 📁 Folder 3: PDF Reports

### 📥 Download PDF Report
**Method:** GET  
**URL:** `http://localhost:5000/api/analyze/NVDA/pdf`

**How to Test:**
1. Click "Download PDF Report"
2. Click "Send"
3. Wait ~40-50 seconds (generates full analysis + PDF)
4. In Insomnia, click the **Preview** tab
5. You should see a PDF preview or download option

**Save PDF to File:**
1. After sending the request
2. Click the dropdown next to "Send" → "Download"
3. Save as `nvda_report.pdf`

---

## 📁 Folder 4: Stock Examples

Pre-configured requests for popular stocks:

### 📊 Analyze NVDA
- Symbol: NVDA (NVIDIA)
- PDF: Enabled

### 🍎 Analyze AAPL
- Symbol: AAPL (Apple)
- PDF: Disabled (faster response)

### 💻 Analyze MSFT
- Symbol: MSFT (Microsoft)
- PDF: Enabled

### 🚗 Analyze TSLA
- Symbol: TSLA (Tesla)
- PDF: Disabled

**How to Test:**
1. Click any stock example
2. Click "Send"
3. Compare analysis between different stocks

---

## 📁 Folder 5: Error Cases

### ❌ Error: Missing Symbol
Tests the 400 Bad Request error

**Request Body:**
```json
{
  "include_pdf": false
}
```

**Expected Response:**
```json
{
  "error": "Stock symbol is required"
}
```
**Status Code:** 400

---

### ❌ Error: Invalid Symbol
Tests the 404 Not Found error

**Request Body:**
```json
{
  "symbol": "INVALID123",
  "include_pdf": false
}
```

**Expected Response:**
```json
{
  "error": "Could not fetch data for INVALID123"
}
```
**Status Code:** 404

---

## 🎯 Environment Variables

The collection uses 2 environment variables that you can customize:

1. **base_url**: `http://localhost:5000`
   - Change if running on different host/port
   
2. **stock_symbol**: `NVDA`
   - Default symbol for parameterized requests
   - Change to test different stocks quickly

**How to Change:**
1. Click the environment dropdown (top-left)
2. Select "Base Environment"
3. Edit the values
4. Click "Done"

---

## 🧪 Testing Workflow

### Quick Test (30 seconds)
1. Health Check → Should return "healthy"
2. Quick Summary (NVDA) → Should return price data
3. Done!

### Full Test (2 minutes)
1. Health Check
2. Quick Summary
3. Full Analysis (JSON) → Wait for complete analysis
4. Check all 5 analysis sections in response
5. Done!

### Complete Test (5 minutes)
1. Health Check
2. Quick Summary (NVDA)
3. Full Analysis (NVDA) with PDF
4. Download PDF Report
5. Test other stocks (AAPL, MSFT, TSLA)
6. Test error cases
7. Done!

---

## 💡 Pro Tips

### 1. View JSON Response Better
- Click "Preview" tab for formatted JSON
- Use the search box to find specific fields
- Collapse/expand sections with arrow icons

### 2. Copy Analysis Text
- In the response, navigate to `analyses.short_summary`
- Right-click → Copy value
- Paste into your document

### 3. Test Multiple Stocks Quickly
- Change `stock_symbol` environment variable
- Use "Quick Summary" for fast testing
- Save responses for comparison

### 4. Download Multiple PDFs
- Send PDF request for each stock
- Download and rename each PDF
- Compare reports side-by-side

### 5. Monitor Performance
- Check response time in bottom-right corner
- Quick Summary: ~2-3 seconds
- Full Analysis: ~30-45 seconds
- PDF Generation: ~40-50 seconds

---

## 🔧 Troubleshooting

### Connection Refused
**Problem:** Can't connect to `localhost:5000`
**Solution:** 
1. Make sure API is running: `python stock_analyzer_api.py`
2. Check terminal for any errors
3. Verify port 5000 is not blocked

### Request Timeout
**Problem:** Request takes too long and times out
**Solution:**
1. Increase timeout in Insomnia: Settings → Request Timeout (set to 120000ms)
2. Check internet connection (needed for data fetching)
3. Try Quick Summary first to verify connection

### 400 Bad Request
**Problem:** Missing stock symbol
**Solution:** Make sure request body includes `"symbol": "NVDA"`

### 404 Not Found
**Problem:** Invalid stock symbol
**Solution:** Use valid NASDAQ symbols (NVDA, AAPL, MSFT, etc.)

### 500 Internal Server Error
**Problem:** Server error during analysis
**Solution:**
1. Check API terminal for error details
2. Verify Azure OpenAI credentials in `.env`
3. Check if stock exists on Google Finance

---

## 📊 Response Time Expectations

| Endpoint | Expected Time | What It Does |
|----------|---------------|--------------|
| Health Check | < 1 second | Simple status check |
| Quick Summary | 2-3 seconds | Basic stock data only |
| Full Analysis (JSON) | 30-45 seconds | Fetches data + 5 AI analyses |
| PDF Report | 40-50 seconds | Full analysis + PDF generation |

---

## 🎬 Complete Example Workflow

```
1. Start API Server
   ✓ python stock_analyzer_api.py

2. Test Health
   → GET /api/health
   ✓ Returns: {"status": "healthy"}

3. Quick Test
   → GET /api/quick-summary/NVDA
   ✓ Returns: Basic stock data in 2 seconds

4. Full Analysis
   → POST /api/analyze
   → Body: {"symbol": "NVDA", "include_pdf": true}
   ✓ Returns: Complete analysis in 40 seconds

5. Download PDF
   → GET /api/analyze/NVDA/pdf
   ✓ Downloads: stock_analysis_NVDA_20251205_103000.pdf

6. Test Another Stock
   → Change symbol to "AAPL"
   → Repeat steps 3-5

7. Compare Results
   → Review analyses side-by-side
   → Check recommendations for each stock
```

---

## 📚 Additional Resources

- **API Documentation:** See `API_README.md`
- **Source Code:** `stock_analyzer_api.py`
- **Original Script:** `stock_analyzer.py`

---

**Happy Testing! 🚀**
