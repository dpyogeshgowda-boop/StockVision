import React, { useEffect, useState } from "react";

import {
  LayoutDashboard,
  TrendingUp,
  Activity,
  BrainCircuit,
  ChartNoAxesCombined,
  Settings,
  Search,
  Bell,
  RefreshCw,
  AlertCircle
} from "lucide-react";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
  AreaChart
} from "recharts";

import axios from "axios";
import "./App.css";

const getApiBaseUrl = () => {
  if (import.meta.env?.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== "undefined") {
    const isCapacitor = window.Capacitor && typeof window.Capacitor.isNativePlatform === "function" && window.Capacitor.isNativePlatform();
    const isAndroid = typeof navigator !== "undefined" && /android/i.test(navigator.userAgent);
    if (isCapacitor || isAndroid) {
      return "http://10.0.2.2:8000";
    }
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      return "http://127.0.0.1:8000";
    }
  }
  return "http://10.0.2.2:8000";
};

const API = getApiBaseUrl();

function App() {

  // ==========================================
  // 1. STATES
  // ==========================================

  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState("NIFTY50");

  const [summary, setSummary] = useState(null);
  const [marketData, setMarketData] = useState([]);
  const [technicalData, setTechnicalData] = useState([]);

  // LSTM prediction states
  const [lstmResult, setLstmResult] = useState(null);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [predictionError, setPredictionError] = useState("");

  // GARCH volatility forecast states
  const [garchResult, setGarchResult] = useState(null);
  const [garchLoading, setGarchLoading] = useState(false);
  const [garchError, setGarchError] = useState("");
  // Backtesting states
  const [backtestResult, setBacktestResult] = useState(null);
  const [backtestLoading, setBacktestLoading] = useState(false);
  const [backtestError, setBacktestError] = useState("");

  // AI-generated technical market analysis
  const [marketAnalysis, setMarketAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  // General application states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [connected, setConnected] = useState(false);
  // Stock data update status
  const [dataStatus, setDataStatus] = useState(null);
  const [statusLoading, setStatusLoading] = useState(false);

  const [period, setPeriod] = useState("1Y");
  const [activeSection, setActiveSection] = useState("Dashboard");

  // Technical indicator controls
  const [showSMA20, setShowSMA20] = useState(true);
  const [showSMA50, setShowSMA50] = useState(true);
  const [showBollinger, setShowBollinger] = useState(false);


  // ==========================================
  // 2. FETCH AVAILABLE COMPANIES
  // ==========================================

  const fetchStocks = async () => {
    try {
      console.log(`[StockVision] Fetching company list from ${API}/stocks ...`);
      const response = await axios.get(`${API}/stocks`);
      const loadedStocks = response.data.stocks || [];
      setStocks(loadedStocks);
      console.log("[StockVision] Companies loaded:", loadedStocks);
      setConnected(true);
      return loadedStocks;
    } catch (err) {
      console.error("[StockVision] Stock List Fetch Error:", err.message || err, {
        url: `${API}/stocks`,
        code: err.code,
        response: err.response
      });
      const detailMsg = err.response?.data?.detail || (err.code === "ERR_NETWORK" ? `Network error: Unable to connect to backend at ${API}` : err.message);
      setError(`Unable to retrieve company list: ${detailMsg}`);
      setConnected(false);
      return null;
    }
  };

  // ==========================================
  // FETCH DAILY DATA UPDATE STATUS
  // ==========================================

  const fetchDataStatus = async () => {
    try {
      setStatusLoading(true);
      console.log(`[StockVision] Fetching data status from ${API}/data-status ...`);
      const response = await axios.get(`${API}/data-status`);
      setDataStatus(response.data);
      console.log("[StockVision] Data status loaded:", response.data);
    } catch (err) {
      console.error("[StockVision] Data Status Fetch Error:", err.message || err, {
        url: `${API}/data-status`,
        code: err.code
      });
      setDataStatus(null);
    } finally {
      setStatusLoading(false);
    }
  };


  // ==========================================
  // 3. FETCH SELECTED COMPANY DATA
  // ==========================================

  const fetchMarketData = async (symbol = selectedStock) => {
    if (!symbol) return;

    try {
      setLoading(true);
      setAnalysisLoading(true);
      setAnalysisError("");
      setError("");
      console.log(`[StockVision] Fetching market data for ${symbol} from ${API} ...`);

      const [
        summaryResponse,
        marketResponse,
        indicatorResponse,
        analysisResponse
      ] = await Promise.all([

        axios.get(`${API}/market-summary`, {
          params: { symbol }
        }),

        axios.get(`${API}/market-data`, {
          params: {
            symbol,
            limit: 2000
          }
        }),

        axios.get(`${API}/technical-indicators`, {
          params: { symbol }
        }),

        axios.get(`${API}/market-analysis`, {
          params: { symbol },
          timeout: 60000
        })

      ]);

      setSummary(summaryResponse.data);

      setMarketData(
        marketResponse.data.data || []
      );

      setTechnicalData(
        indicatorResponse.data.indicators || []
      );

      setMarketAnalysis(analysisResponse.data);
      setAnalysisError("");

      // Clear previous company's prediction
      setLstmResult(null);
      setPredictionError("");
      setGarchResult(null);
      setGarchError("");

      setConnected(true);
      console.log(`[StockVision] Market data successfully loaded for ${symbol}`);

    } catch (err) {

      console.error(`[StockVision] Stock API Error for ${symbol}:`, err.message || err, {
        url: API,
        code: err.code,
        response: err.response
      });

      const detailMsg =
        err.response?.data?.detail ||
        (err.code === "ERR_NETWORK" ? `Network error: Cannot connect to backend at ${API}` : err.message) ||
        "Unable to retrieve stock information.";

      setError(detailMsg);

      setSummary(null);
      setMarketData([]);
      setTechnicalData([]);
      setMarketAnalysis(null);
      setAnalysisError(
        err.response?.data?.detail ||
        "Unable to retrieve market analysis."
      );

      setConnected(false);

    } finally {

      setLoading(false);
      setAnalysisLoading(false);

    }

  };


  // ==========================================
  // UNIFIED RETRY & REFRESH CONNECTION
  // ==========================================

  const handleRetry = async () => {
    console.log("[StockVision] Triggering retry for backend connection...");
    setError("");
    setLoading(true);

    let loadedStocks = stocks;
    if (!loadedStocks || loadedStocks.length === 0) {
      loadedStocks = await fetchStocks();
    } else {
      fetchStocks();
    }

    const symbolToLoad = selectedStock || (loadedStocks && loadedStocks[0]?.symbol) || "NIFTY50";
    await Promise.all([
      fetchMarketData(symbolToLoad),
      fetchDataStatus()
    ]);
  };


  // ==========================================
  // 4. GENERATE LSTM PREDICTION
  // ==========================================

  const generateLstmPrediction = async () => {

    try {

      setPredictionLoading(true);
      setPredictionError("");
      setLstmResult(null);

      if (selectedStock === "NIFTY50") {

        throw new Error(
          "Select an individual company to generate LSTM predictions."
        );

      }

      console.log(`[StockVision] Requesting LSTM prediction for ${selectedStock} from ${API}/lstm-prediction ...`);
      const response = await axios.get(
        `${API}/lstm-prediction`,
        {
          params: {
            symbol: selectedStock
          },
          timeout: 180000
        }
      );

      setLstmResult(response.data);
      console.log(`[StockVision] LSTM prediction received for ${selectedStock}`);

    } catch (err) {

      console.error("[StockVision] LSTM Prediction Error:", err.message || err, {
        url: `${API}/lstm-prediction`,
        code: err.code,
        response: err.response
      });

      setPredictionError(
        err.response?.data?.detail ||
        (err.code === "ERR_NETWORK" ? `Network Error: Cannot connect to ${API}` : err.message) ||
        "Unable to generate prediction."
      );

    } finally {

      setPredictionLoading(false);

    }

  };


  // ==========================================
  // 5. GENERATE GARCH VOLATILITY FORECAST
  // ==========================================

  const generateGarchForecast = async () => {

    try {
      setGarchLoading(true);
      setGarchError("");
      setGarchResult(null);

      if (selectedStock === "NIFTY50") {
        throw new Error(
          "Select an individual company to generate a GARCH forecast."
        );
      }

      console.log(`[StockVision] Requesting GARCH forecast for ${selectedStock} from ${API}/garch-forecast ...`);
      const response = await axios.get(
        `${API}/garch-forecast`,
        {
          params: { symbol: selectedStock },
          timeout: 180000
        }
      );

      setGarchResult(response.data);
      console.log(`[StockVision] GARCH forecast received for ${selectedStock}`);

    } catch (err) {
      console.error("[StockVision] GARCH Forecast Error:", err.message || err, {
        url: `${API}/garch-forecast`,
        code: err.code,
        response: err.response
      });

      setGarchError(
        err.response?.data?.detail ||
        (err.code === "ERR_NETWORK" ? `Network Error: Cannot connect to ${API}` : err.message) ||
        "Unable to generate the GARCH volatility forecast."
      );

    } finally {
      setGarchLoading(false);
    }
  };

  // ==========================================
  // GENERATE BACKTEST
  // ==========================================

  const generateBacktest = async () => {

    try {

      setBacktestLoading(true);
      setBacktestError("");
      setBacktestResult(null);

      console.log(`[StockVision] Requesting Backtest for ${selectedStock} from ${API}/backtest ...`);
      const response = await axios.get(
        `${API}/backtest`,
        {
          params: {
            symbol: selectedStock
          },
          timeout: 60000
        }
      );

      setBacktestResult(response.data);
      console.log(`[StockVision] Backtest results received for ${selectedStock}`);

    } catch (err) {

      console.error("[StockVision] Backtesting Error:", err.message || err, {
        url: `${API}/backtest`,
        code: err.code,
        response: err.response
      });

      setBacktestError(
        err.response?.data?.detail ||
        (err.code === "ERR_NETWORK" ? `Network Error: Cannot connect to ${API}` : err.message) ||
        "Unable to perform backtesting."
      );

    } finally {

      setBacktestLoading(false);

    }

  };


  // ==========================================
  // 6. LOAD COMPANY LIST ON STARTUP
  // ==========================================

  useEffect(() => {
    fetchStocks();
    fetchDataStatus();
  }, []);


  // ==========================================
  // 6. FETCH DATA WHEN COMPANY CHANGES
  // ==========================================

  useEffect(() => {

    if (selectedStock) {

      fetchMarketData(selectedStock);

    }

  }, [selectedStock]);


  // ==========================================
  // 7. FILTER HISTORICAL DATA
  // ==========================================

  const getFilteredData = () => {

    if (!marketData.length) return [];

    const days = {
      "1M": 30,
      "6M": 180,
      "1Y": 365,
      "5Y": 1825
    };

    return marketData.slice(-days[period]);

  };


  // ==========================================
  // 8. MERGE MARKET DATA AND INDICATORS
  // ==========================================

  const chartData = () => {

    const indicatorMap = new Map(

      technicalData.map(item => [
        item.Date,
        item
      ])

    );

    return getFilteredData().map(item => {

      const indicators =
        indicatorMap.get(item.Date) || {};

      return {

        date: item.Date,

        Close: item.Close,

        SMA_20: indicators.SMA_20,

        SMA_50: indicators.SMA_50,

        RSI_14: indicators.RSI_14,

        Upper_Band: indicators.Upper_Band,

        Lower_Band: indicators.Lower_Band

      };

    });

  };


  const displayData = chartData();


  // ==========================================
  // 9. CALCULATE PRICE CHANGES
  // ==========================================

  const latestPrice = summary?.latest_close;

  const previousPrice =
    marketData.length > 1
      ? marketData[marketData.length - 2]?.Close
      : null;

  const priceChange =
    latestPrice != null && previousPrice != null
      ? latestPrice - previousPrice
      : null;

  const priceChangePercent =
    priceChange != null && previousPrice
      ? (priceChange / previousPrice) * 100
      : null;


  // ==========================================
  // 10. FORMAT STOCK PRICE
  // ==========================================

  const formatPrice = (value) => {

    if (
      value == null ||
      !Number.isFinite(Number(value))
    ) {

      return "--";

    }

    return `₹${Number(value).toLocaleString("en-IN", {
      maximumFractionDigits: 2
    })}`;

  };


  // ==========================================
  // 11. SIDEBAR NAVIGATION
  // ==========================================

  const sections = [

    { name: "Dashboard", icon: LayoutDashboard },

    { name: "Market Trends", icon: TrendingUp },

    { name: "Technical Analysis", icon: ChartNoAxesCombined },

    { name: "AI Market Insights", icon: BrainCircuit },

    { name: "AI Prediction", icon: BrainCircuit },

    { name: "Volatility Analysis", icon: Activity },

    { name: "Backtesting", icon: ChartNoAxesCombined }

  ];


  const navigate = (section) => {

    setActiveSection(section);

    const target = document.getElementById(
      section.replaceAll(" ", "-").toLowerCase()
    );

    target?.scrollIntoView({
      behavior: "smooth"
    });

  };


  // ==========================================
  // 12. SELECTED COMPANY NAME
  // ==========================================

  const selectedCompany = stocks.find(
    stock => stock.symbol === selectedStock
  );
  const predictedChangePercent =
    lstmResult?.latest_actual_price
      ? (
          (lstmResult.predicted_next_price -
            lstmResult.latest_actual_price) /
          lstmResult.latest_actual_price
        ) * 100
      : null;

  // ==========================================
  // 13. USER INTERFACE
  // ==========================================

  return (

    <div className="app-container">


      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="logo">

          <Activity size={28} />

          <h2>StockVision</h2>

        </div>

        <p className="menu-label">MAIN MENU</p>

        <nav>

          {sections.map(({ name, icon: Icon }) => (

            <a
              key={name}
              className={
                activeSection === name ? "active" : ""
              }
              onClick={() => navigate(name)}
            >

              <Icon size={19} />

              {name}

            </a>

          ))}

        </nav>

        <div className="sidebar-bottom">

          <Settings size={19} />

          Settings

        </div>

      </aside>


      {/* MAIN CONTENT */}

      <main className="main-content">


        {/* HEADER */}

        <header className="topbar">

          <div>

            <h1>Market Overview</h1>

            <p>
              Stock Market Trend & Volatility Forecaster
            </p>

          </div>

          <div className="top-actions">

            <Search />

            <Bell />

            <div className="profile">Y</div>

          </div>

        </header>


        {/* ERROR MESSAGE */}

        {error && (

          <div className="error-box">

            <AlertCircle size={20} />

            {error}

            <button
              onClick={handleRetry}
              disabled={loading}
            >
              {loading ? "Connecting..." : "Retry"}
            </button>

          </div>

        )}


        {/* COMPANY SELECTOR */}

        <section className="market-selector">

          <div>

            <label>SELECT COMPANY</label>

            <select
              value={selectedStock}
              onChange={(e) => setSelectedStock(e.target.value)}
            >

              {stocks.map(stock => (

                <option
                  key={stock.symbol}
                  value={stock.symbol}
                >

                  {stock.name}

                </option>

              ))}

            </select>

          </div>


          <div className="market-status">

            <span
              className="status-dot"
              style={{
                background: connected
                  ? "#22c55e"
                  : "#ef4444"
              }}
            />

            {loading
              ? "Connecting to backend..."
              : connected
                ? "Backend Connected"
                : "Backend Disconnected"
            }

            <button
              className="refresh-button"
              onClick={handleRetry}
              disabled={loading}
              title="Retry Connection"
            >

              <RefreshCw size={16} />

            </button>

          </div>

          {/* DAILY DATA UPDATE STATUS */}

          <div
            style={{
              marginTop: "12px",
              padding: "12px 16px",
              background: "#0b1729",
              border: "1px solid #26364d",
              borderRadius: "8px",
              color: "#cbd5e1"
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "15px" }}>

              <div>
                <strong style={{ color: "#38bdf8" }}>
                  StockVision Daily Data Update
                </strong>

                <p style={{ margin: "6px 0 0", fontSize: "13px" }}>
                  {statusLoading
                    ? "Checking update status..."
                    : dataStatus
                      ? `${dataStatus.total_files} company datasets available`
                      : "Unable to retrieve update status"
                  }
                </p>

                {dataStatus?.last_updated && (
                  <p style={{ margin: "5px 0 0", fontSize: "12px" }}>
                    Last file update: {dataStatus.last_updated}
                  </p>
                )}
              </div>

              <button
                onClick={fetchDataStatus}
                disabled={statusLoading}
                style={{
                  padding: "9px 14px",
                  background: "#2563eb",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer"
                }}
              >
                {statusLoading ? "Checking..." : "Refresh"}
              </button>

            </div>
          </div>

        </section>


        {/* STATISTICS */}

        <section className="stats-grid">


          <div className="stat-card">

            <p>Latest Stock Price</p>

            <h2>

              {loading
                ? "Loading..."
                : formatPrice(latestPrice)
              }

            </h2>

            <span>
              {selectedCompany?.name || selectedStock}
            </span>

          </div>


          <div className="stat-card">

            <p>Daily Price Change</p>

            <h2
              style={{
                color: priceChange >= 0
                  ? "#4ade80"
                  : "#fb7185"
              }}
            >

              {priceChangePercent == null
                ? "--"
                : `${priceChangePercent >= 0 ? "+" : ""}${priceChangePercent.toFixed(2)}%`
              }

            </h2>

            <span>
              Compared with previous observation
            </span>

          </div>


          <div className="stat-card">

            <p>Volatility Model</p>

            <h2>GARCH</h2>

            <span>Risk Analysis</span>

          </div>


          <div className="stat-card">

            <p>Historical Records</p>

            <h2>
              {summary?.total_records ?? "--"}
            </h2>

            <span>
              Historical observations
            </span>

          </div>

        </section>


        {/* MARKET TRENDS */}

        <section
          className="chart-section"
          id="market-trends"
        >

          <div className="section-heading">

            <div>

              <h2>Market Analytics</h2>

              <p>

                {selectedCompany?.name || selectedStock}

                {" "}Historical Price Movements

              </p>

            </div>


            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >

              <option value="1M">1 Month</option>

              <option value="6M">6 Months</option>

              <option value="1Y">1 Year</option>

              <option value="5Y">5 Years</option>

            </select>

          </div>


          {/* INDICATOR CONTROLS */}

          <div className="chart-controls">

            <label>

              <input
                type="checkbox"
                checked={showSMA20}
                onChange={() => setShowSMA20(!showSMA20)}
              />

              SMA 20

            </label>


            <label>

              <input
                type="checkbox"
                checked={showSMA50}
                onChange={() => setShowSMA50(!showSMA50)}
              />

              SMA 50

            </label>


            <label>

              <input
                type="checkbox"
                checked={showBollinger}
                onChange={() => setShowBollinger(!showBollinger)}
              />

              Bollinger Bands

            </label>

          </div>


          {/* PRICE CHART */}

          {loading ? (

            <div className="loading-box">

              Loading historical stock data...

            </div>

          ) : displayData.length > 0 ? (

            <div className="chart-container">

              <ResponsiveContainer width="100%" height={380}>

                <LineChart data={displayData}>

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#273449"
                  />

                  <XAxis
                    dataKey="date"
                    stroke="#94a3b8"
                    tick={{ fontSize: 11 }}
                    minTickGap={35}
                  />

                  <YAxis
                    stroke="#94a3b8"
                    domain={["auto", "auto"]}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#111c30",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                      color: "#fff"
                    }}
                    formatter={(value) => formatPrice(value)}
                  />

                  <Legend />


                  <Line
                    type="monotone"
                    dataKey="Close"
                    stroke="#38bdf8"
                    strokeWidth={2}
                    dot={false}
                    name="Closing Price"
                    connectNulls
                  />


                  {showSMA20 && (

                    <Line
                      type="monotone"
                      dataKey="SMA_20"
                      stroke="#facc15"
                      dot={false}
                      strokeWidth={1.5}
                      name="SMA 20"
                      connectNulls
                    />

                  )}


                  {showSMA50 && (

                    <Line
                      type="monotone"
                      dataKey="SMA_50"
                      stroke="#c084fc"
                      dot={false}
                      strokeWidth={1.5}
                      name="SMA 50"
                      connectNulls
                    />

                  )}


                  {showBollinger && (

                    <>

                      <Line
                        type="monotone"
                        dataKey="Upper_Band"
                        stroke="#4ade80"
                        strokeDasharray="5 5"
                        dot={false}
                        name="Upper Band"
                        connectNulls
                      />

                      <Line
                        type="monotone"
                        dataKey="Lower_Band"
                        stroke="#fb7185"
                        strokeDasharray="5 5"
                        dot={false}
                        name="Lower Band"
                        connectNulls
                      />

                    </>

                  )}

                </LineChart>

              </ResponsiveContainer>

            </div>

          ) : (

            <div className="loading-box">

              No market data available.

            </div>

          )}

        </section>


        {/* TECHNICAL ANALYSIS */}

        <section
          className="chart-section"
          id="technical-analysis"
        >

          <div className="section-heading">

            <div>

              <h2>Technical Analysis</h2>

              <p>Relative Strength Index (RSI)</p>

            </div>

          </div>


          {!loading && displayData.length > 0 ? (

            <ResponsiveContainer width="100%" height={280}>

              <AreaChart data={displayData}>

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#273449"
                />

                <XAxis
                  dataKey="date"
                  stroke="#94a3b8"
                  minTickGap={35}
                />

                <YAxis
                  domain={[0, 100]}
                  stroke="#94a3b8"
                />

                <Tooltip />

                <Legend />

                <Area
                  type="monotone"
                  dataKey="RSI_14"
                  stroke="#38bdf8"
                  fill="#0ea5e9"
                  fillOpacity={0.15}
                  connectNulls
                  name="RSI 14"
                />

              </AreaChart>

            </ResponsiveContainer>

          ) : (

            <div className="loading-box">

              Waiting for RSI data...

            </div>

          )}

          <p className="indicator-note">

            RSI above 70 may indicate overbought conditions.

            RSI below 30 may indicate oversold conditions.

          </p>

        </section>



        {/* AI MARKET INSIGHTS */}

        <section
          className="chart-section"
          id="ai-market-insights"
        >
          <div className="section-heading">
            <div>
              <h2>AI Market Insights</h2>
              <p>
                Technical-indicator-based analysis for{" "}
                {marketAnalysis?.company || selectedCompany?.name || selectedStock}
              </p>
            </div>
            {analysisLoading && <span>Analysing...</span>}
          </div>

          {analysisError && (
            <div className="error-box">
              <AlertCircle size={18} />
              {analysisError}
              <button onClick={() => fetchMarketData(selectedStock)} disabled={analysisLoading}>
                Retry
              </button>
            </div>
          )}

          {!analysisError && !marketAnalysis && (
            <div className="loading-box">
              {loading || analysisLoading
                ? "Generating market insights..."
                : "Market analysis is not available yet."}
            </div>
          )}

          {marketAnalysis && (
            <>
              <div className="stats-grid">
                <div className="stat-card">
                  <p>Market Trend</p>
                  <h2 style={{
                    color:
                      marketAnalysis.market_trend === "Bullish" ? "#4ade80" :
                      marketAnalysis.market_trend === "Bearish" ? "#fb7185" :
                      "#facc15"
                  }}>
                    {marketAnalysis.market_trend || "--"}
                  </h2>
                  <span>{marketAnalysis.latest_date || ""}</span>
                </div>

                <div className="stat-card">
                  <p>RSI Status</p>
                  <h2>{marketAnalysis.technical_indicators?.RSI_status || "--"}</h2>
                  <span>
                    RSI 14: {marketAnalysis.technical_indicators?.RSI_14 != null
                      ? Number(marketAnalysis.technical_indicators.RSI_14).toFixed(2)
                      : "--"}
                  </span>
                </div>

                <div className="stat-card">
                  <p>Bollinger Band Position</p>
                  <h2 style={{ fontSize: "20px" }}>
                    {marketAnalysis.technical_indicators?.bollinger_status || "--"}
                  </h2>
                  <span>Based on the latest closing price</span>
                </div>

                <div className="stat-card">
                  <p>Latest Closing Price</p>
                  <h2>{formatPrice(marketAnalysis.latest_price)}</h2>
                  <span>{marketAnalysis.symbol}</span>
                </div>
              </div>

              <div className="analysis-card" style={{ marginTop: "18px" }}>
                <h3>Trend Analysis</h3>
                <p>
                  {marketAnalysis.trend_description ||
                    "No trend description is available."}
                </p>

                <h3 style={{ marginTop: "18px" }}>RSI Interpretation</h3>
                <p>
                  {marketAnalysis.technical_indicators?.RSI_description ||
                    "RSI interpretation is not available."}
                </p>

                <h3 style={{ marginTop: "18px" }}>Bollinger Band Analysis</h3>
                <p>
                  {marketAnalysis.technical_indicators?.bollinger_description ||
                    "Bollinger Band interpretation is not available."}
                </p>

                <h3 style={{ marginTop: "18px" }}>Overall Interpretation</h3>
                <p>
                  {marketAnalysis.overall_interpretation ||
                    "No overall interpretation is available."}
                </p>

                <small style={{ display: "block", marginTop: "16px", color: "#94a3b8" }}>
                  {marketAnalysis.disclaimer ||
                    "This analysis uses historical technical indicators. It is not a guaranteed prediction or investment recommendation."}
                </small>
              </div>
            </>
          )}
        </section>

        {/* AI PREDICTION */}

        <section
          className="bottom-grid"
          id="ai-prediction"
        >


          {/* LSTM PREDICTION CARD */}

          <div className="analysis-card">

            <BrainCircuit size={28} />

            <h3>LSTM Price Prediction</h3>

            <p>

              Deep learning model that analyses historical
              stock prices to predict the next trading day's
              closing price.

            </p>


            <button
              className="predict-button"
              onClick={generateLstmPrediction}
              disabled={
                predictionLoading ||
                selectedStock === "NIFTY50"
              }
            >

              {predictionLoading
                ? "Training LSTM Model..."
                : "Generate Prediction"
              }

            </button>


            {selectedStock === "NIFTY50" && (

              <p className="coming-soon">

                Select an individual company to generate predictions.

              </p>

            )}


            {predictionLoading && (

              <p className="coming-soon">

                TensorFlow is training the model. Please wait...

              </p>

            )}


            {predictionError && (

              <p style={{ color: "#fb7185" }}>

                {predictionError}

              </p>

            )}


            {/* LSTM RESULTS */}
            {lstmResult && (
              <div className="prediction-results">
                <h3>Prediction Results</h3>
                <p>
                  Company: <strong>{lstmResult.symbol}</strong>
                </p>

                <div className="stats-grid">
                  <div className="stat-card">
                    <p>Latest Closing Price</p>
                    <h2>{formatPrice(lstmResult.latest_actual_price)}</h2>
                  </div>
                  <div className="stat-card">
                    <p>Predicted Next Closing Price</p>
                    <h2 style={{ color: "#38bdf8" }}>
                      {formatPrice(lstmResult.predicted_next_price)}
                    </h2>
                  </div>
                  <div className="stat-card">
                    <p>Expected Price Change</p>
                    <h2 style={{
                      color: Number(lstmResult.expected_change_percent ?? predictedChangePercent) >= 0
                        ? "#4ade80" : "#fb7185"
                    }}>
                      {Number(lstmResult.expected_change_percent ?? predictedChangePercent).toFixed(2)}%
                    </h2>
                  </div>
                  <div className="stat-card">
                    <p>Directional Accuracy</p>
                    <h2>{Number(lstmResult.directional_accuracy_percent ?? 0).toFixed(2)}%</h2>
                  </div>
                </div>

                <h3 style={{ marginTop: "28px" }}>Actual vs Predicted Historical Prices</h3>
                <p style={{ color: "#94a3b8", fontSize: "13px" }}>
                  LSTM model evaluation on historical test data
                </p>
                {Array.isArray(lstmResult.evaluation_data) && lstmResult.evaluation_data.length > 0 ? (
                  <div style={{ width: "100%", height: 340, marginTop: "14px" }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={lstmResult.evaluation_data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#273449" />
                        <XAxis
                          dataKey="date"
                          stroke="#94a3b8"
                          tick={{ fontSize: 11 }}
                          minTickGap={35}
                        />
                        <YAxis
                          stroke="#94a3b8"
                          domain={["auto", "auto"]}
                          tickFormatter={(value) => `₹${Number(value).toLocaleString("en-IN")}`}
                        />
                        <Tooltip
                          labelFormatter={(label) => `Date: ${label}`}
                          formatter={(value, name) => [formatPrice(value), name]}
                          contentStyle={{
                            background: "#111c30",
                            border: "1px solid #334155",
                            borderRadius: "8px",
                            color: "#fff"
                          }}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="actual_price"
                          name="Actual Price"
                          stroke="#38bdf8"
                          strokeWidth={2}
                          dot={false}
                          connectNulls
                        />
                        <Line
                          type="monotone"
                          dataKey="predicted_price"
                          name="LSTM Predicted Price"
                          stroke="#facc15"
                          strokeWidth={2}
                          dot={false}
                          connectNulls
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="coming-soon">Historical evaluation chart is not available.</p>
                )}

                <h3 style={{ marginTop: "28px" }}>Model Evaluation Metrics</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <p>MAE</p>
                    <h2>{formatPrice(lstmResult.mae)}</h2>
                    <span>Mean Absolute Error</span>
                  </div>
                  <div className="stat-card">
                    <p>RMSE</p>
                    <h2>{formatPrice(lstmResult.rmse)}</h2>
                    <span>Root Mean Squared Error</span>
                  </div>
                  <div className="stat-card">
                    <p>MAPE</p>
                    <h2>{Number(lstmResult.mape ?? 0).toFixed(2)}%</h2>
                    <span>Mean Absolute Percentage Error</span>
                  </div>
                  <div className="stat-card">
                    <p>Training / Testing Records</p>
                    <h2>{lstmResult.training_records} / {lstmResult.testing_records}</h2>
                    <span>Epochs completed: {lstmResult.epochs_completed}</span>
                  </div>
                </div>

                {lstmResult.model_information && (
                  <div style={{
                    marginTop: "20px",
                    padding: "16px",
                    background: "#0b1729",
                    border: "1px solid #26364d",
                    borderRadius: "8px"
                  }}>
                    <h3>Model Information</h3>
                    <p>Model: <strong>{lstmResult.model_information.model || "LSTM"}</strong></p>
                    <p>Approach: {lstmResult.model_information.approach || "Deep Learning"}</p>
                    <p>Sequence length: {lstmResult.model_information.sequence_length ?? 60} trading days</p>
                    <p>Training split: {lstmResult.model_information.training_split || "80% training / 20% testing"}</p>
                  </div>
                )}

                <small style={{ display: "block", marginTop: "18px", color: "#94a3b8" }}>
                  The chart compares predictions with actual prices in the historical test set.
                  The next-day value is an experimental estimate, not a guaranteed future price
                  or investment recommendation. Directional accuracy below 50% indicates limited
                  ability to predict price direction.
                </small>
              </div>
            )}
          </div>


          {/* GARCH VOLATILITY CARD */}

          <div
            className="analysis-card"
            id="volatility-analysis"
          >

            <Activity size={28} />

            <h3>GARCH Volatility Forecast</h3>

            <p>
              GARCH(1,1) estimates changing market volatility
              using historical daily stock returns.
            </p>

            <button
              className="predict-button"
              onClick={generateGarchForecast}
              disabled={garchLoading || selectedStock === "NIFTY50"}
            >
              {garchLoading
                ? "Calculating Volatility..."
                : "Generate Volatility Forecast"
              }
            </button>

            {selectedStock === "NIFTY50" && (
              <p className="coming-soon">
                Select an individual company to generate a forecast.
              </p>
            )}

            {garchLoading && (
              <p className="coming-soon">
                Fitting the GARCH model. Please wait...
              </p>
            )}

            {garchError && (
              <p style={{ color: "#fb7185" }}>
                {garchError}
              </p>
            )}

            {garchResult && (
              <div className="prediction-results">

                <h3>Volatility Results</h3>

                <p>
                  Company: <strong>{garchResult.symbol}</strong>
                </p>

                <p>
                  Model: <strong>{garchResult.model}</strong>
                </p>

                <div className="prediction-value">
                  <span>Latest Closing Price</span>
                  <h2>{formatPrice(garchResult.latest_actual_price)}</h2>
                </div>

                <div className="prediction-value">
                  <span>Latest Daily Volatility</span>
                  <h2>
                    {Number(garchResult.latest_daily_volatility).toFixed(4)}%
                  </h2>
                </div>

                <div className="prediction-value">
                  <span>Annualized Forecast Volatility</span>
                  <h2 style={{ color: "#38bdf8" }}>
                    {Number(garchResult.annualized_forecast_volatility).toFixed(2)}%
                  </h2>
                </div>

                <p>
                  Risk Classification:{" "}
                  <strong
                    style={{
                      color:
                        garchResult.risk_level === "High"
                          ? "#fb7185"
                          : garchResult.risk_level === "Moderate"
                            ? "#facc15"
                            : "#4ade80"
                    }}
                  >
                    {garchResult.risk_level}
                  </strong>
                </p>

                <p>Forecast period: {garchResult.forecast_horizon}</p>
                <p>Training records: {garchResult.training_records}</p>

                <h4 style={{ marginTop: "18px" }}>
                  Five-Day Volatility Forecast
                </h4>

                <div style={{ width: "100%", height: 220, marginTop: 12 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={(garchResult.forecast_daily_volatility || []).map(
                        (value, index) => ({
                          day: `Day ${index + 1}`,
                          volatility: value
                        })
                      )}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#273449"
                      />
                      <XAxis dataKey="day" stroke="#94a3b8" />
                      <YAxis
                        stroke="#94a3b8"
                        unit="%"
                        domain={["auto", "auto"]}
                      />
                      <Tooltip
                        formatter={(value) => [
                          `${Number(value).toFixed(4)}%`,
                          "Daily volatility"
                        ]}
                        contentStyle={{
                          background: "#111c30",
                          border: "1px solid #334155",
                          borderRadius: "8px",
                          color: "#fff"
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="volatility"
                        name="Forecast volatility"
                        stroke="#38bdf8"
                        strokeWidth={2}
                        dot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <small>
                  Volatility estimates return variability, not whether
                  the stock price will rise or fall. Risk thresholds
                  are illustrative.
                </small>

              </div>
            )}

          </div>

        </section>

{/* ===================================== */}
{/* BACKTESTING MODULE */}
{/* ===================================== */}

<section
  className="chart-section"
  id="backtesting"
>

  <div className="section-heading">

    <div>
      <h2>Strategy Backtesting</h2>

      <p>
        Evaluate historical trading strategy performance
        for {selectedCompany?.name || selectedStock}
      </p>
    </div>

  </div>

  <div className="analysis-card">

    <h3>SMA 20 / SMA 50 Crossover Strategy</h3>

    <p>
      This strategy compares the 20-day and 50-day
      moving averages to generate historical trading
      signals.
    </p>

    <button
      className="predict-button"
      onClick={generateBacktest}
      disabled={backtestLoading || loading}
    >

      {backtestLoading
        ? "Running Backtest..."
        : "Run Strategy Backtest"
      }

    </button>

    {backtestLoading && (
      <p className="coming-soon">
        Evaluating historical trading performance...
      </p>
    )}

    {backtestError && (
      <p style={{ color: "#fb7185" }}>
        {backtestError}
      </p>
    )}

    {backtestResult && (

      <div className="prediction-results">

        <h3>Backtesting Results</h3>

        <p>
          Company: <strong>{backtestResult.company}</strong>
        </p>

        <p>
          Strategy: <strong>{backtestResult.strategy}</strong>
        </p>

        <p>
          Testing Period:{" "}
          {backtestResult.backtest_period.start_date}
          {" to "}
          {backtestResult.backtest_period.end_date}
        </p>

        <div className="stats-grid">

          <div className="stat-card">
            <p>Strategy Return</p>
            <h2>
              {backtestResult.performance.strategy_return_percent}%
            </h2>
          </div>

          <div className="stat-card">
            <p>Buy & Hold Return</p>
            <h2>
              {backtestResult.performance.buy_and_hold_return_percent}%
            </h2>
          </div>

          <div className="stat-card">
            <p>Sharpe Ratio</p>
            <h2>
              {backtestResult.performance.sharpe_ratio}
            </h2>
          </div>

          <div className="stat-card">
            <p>Maximum Drawdown</p>
            <h2>
              {backtestResult.performance.maximum_drawdown_percent}%
            </h2>
          </div>

          <div className="stat-card">
            <p>Annualized Volatility</p>
            <h2>
              {backtestResult.performance.annualized_volatility_percent}%
            </h2>
          </div>

          <div className="stat-card">
            <p>Win Rate</p>
            <h2>
              {backtestResult.performance.win_rate_percent}%
            </h2>
          </div>

        </div>

        <h3 style={{ marginTop: "25px" }}>
          Strategy vs Buy & Hold Performance
        </h3>

        <div style={{ width: "100%", height: 350 }}>

          <ResponsiveContainer width="100%" height="100%">

            <LineChart data={backtestResult.equity_curve}>

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#273449"
              />

              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                minTickGap={35}
              />

              <YAxis
                stroke="#94a3b8"
                domain={["auto", "auto"]}
              />

              <Tooltip />

              <Legend />

              <Line
                type="monotone"
                dataKey="strategy_value"
                name="SMA Strategy"
                stroke="#38bdf8"
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="buy_hold_value"
                name="Buy & Hold"
                stroke="#facc15"
                dot={false}
              />

            </LineChart>

          </ResponsiveContainer>

        </div>

        <p>
          Total position changes:{" "}
          {backtestResult.performance.total_position_changes}
        </p>

        <p>
          Historical records: {backtestResult.total_records}
        </p>

        <small>
          {backtestResult.disclaimer}
        </small>

      </div>

    )}

  </div>

</section>
        {/* FOOTER */}

        <footer>

          StockVision · AI Powered Financial Analytics

        </footer>


      </main>

    </div>

  );

}

export default App;
