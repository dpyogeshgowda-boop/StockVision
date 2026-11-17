# 📈 StockVision – Stock Market Trend & Volatility Forecaster

StockVision is a stock market analysis and forecasting application that combines Machine Learning, Deep Learning and statistical methods to analyze stock market trends and predict future price movements and volatility.

The project focuses on NIFTY 50 stocks and provides an interactive interface for exploring stock data, technical indicators and forecasting results.

## 🚀 Features

- **Stock Market Analysis:** Analyze historical stock market data.
- **LSTM Prediction:** Use Long Short-Term Memory networks for stock price forecasting.
- **GARCH Volatility Forecasting:** Estimate future market volatility using GARCH models.
- **Technical Indicators:** Analyze stocks using:
  - Simple Moving Average (SMA)
  - Relative Strength Index (RSI)
  - Bollinger Bands
- **Data Visualization:** Visualize historical prices, technical indicators and forecasting results.
- **Interactive Dashboard:** Explore stock information through a React-based interface.
- **Android Application:** Android support using Capacitor.

## 🛠️ Technologies Used

| Category | Technologies |
|---|---|
| Frontend | React.js, Vite, CSS, JavaScript |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn |
| Deep Learning | TensorFlow / Keras, LSTM |
| Statistical Modeling | GARCH |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Plotly, Seaborn |
| Stock Data | Yahoo Finance (yfinance) |
| Android | Android Studio, Capacitor |
| Version Control | Git, GitHub |

## 🏗️ Project Structure

```text
Stock-Market/
│
├── backend/
│   ├── main.py
│   ├── analysis_service.py
│   ├── data_service.py
│   ├── prediction_service.py
│   └── models/
│       ├── garch_model.py
│       └── lstm_model.py
│
├── data/
│   └── stocks/
│
├── frontend/
│   ├── android/
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       └── services/
│
├── collect_stocks.py
├── data_collection.py
├── data_preprocessing.py
├── technical_indicators.py
├── garch_model.py
├── lstm_model.py
├── eda_analysis.py
│
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/dpyogeshgowda-boop/StockVision.git
cd StockVision
```

### 2. Set Up Python Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install Backend Dependencies

Install the required Python packages:

```bash
pip install fastapi uvicorn pandas numpy matplotlib seaborn yfinance scikit-learn tensorflow arch
```

### 4. Start the Backend

From the project root directory:

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend address:

```text
http://127.0.0.1:8000
```

### 5. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your browser.

## 📱 Android Application

The frontend also supports Android through Capacitor.

To build the frontend:

```bash
cd frontend
npm run build
```

Synchronize the Android project:

```bash
npx cap sync android
```

Open the Android project in Android Studio:

```bash
npx cap open android
```

Build and run the application using Android Studio.

## 🧠 Machine Learning and Forecasting

### LSTM (Long Short-Term Memory)
LSTM is a type of recurrent neural network used to learn patterns from sequential data. In StockVision, it is used for stock price forecasting based on historical market data.

### GARCH (Generalized Autoregressive Conditional Heteroskedasticity)
GARCH is a statistical model used to estimate changing market volatility over time. It helps analyze periods of higher and lower market uncertainty.

### Technical Indicators
Technical indicators help analyze historical price movements and market trends.

## 🎯 Project Objective

The main objective of StockVision is to combine machine learning, deep learning and statistical forecasting techniques into a single platform to support stock market data analysis and visualization.

## ⚠️ Disclaimer

StockVision is an educational and analytical project. Predictions and forecasts are estimates based on historical data and are not guaranteed to be accurate. This application does not provide financial or investment advice.

## 👨‍💻 Author

Developed as a Computer Science and Engineering project.

GitHub: https://github.com/dpyogeshgowda-boop

---

⭐ If you find this project interesting, consider starring the repository!