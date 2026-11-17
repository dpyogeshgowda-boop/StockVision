from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models.lstm_model import train_lstm_model
from backend.models.garch_model import train_garch_model
from pathlib import Path
from datetime import datetime
from backend.analysis_service import generate_market_analysis
from backend.analysis_service import run_backtest

from backend.data_service import (
    load_stock_data,
    get_stock_summary,
    get_historical_data,
    get_available_stocks
)

import pandas as pd
import numpy as np

app = FastAPI(
    title="Stock Market Forecaster API",
    description="AI-powered Stock Market Analytics",
    version="2.0"
)

# React frontend & Android WebView connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------
# HOME
# -----------------------------------------

@app.get("/")
def home():

    return {
        "message": "Stock Market Forecaster Backend Running!",
        "status": "Success"
    }


# -----------------------------------------
# HEALTH CHECK
# -----------------------------------------

@app.get("/health")
def health():

    return {
        "backend": "Active",
        "status": "Healthy"
    }


# -----------------------------------------
# DASHBOARD INFORMATION
# -----------------------------------------

@app.get("/dashboard")
def dashboard():

    return {
        "project": "Stock Market Trend & Volatility Forecaster",
        "market": "NIFTY 50",
        "models": ["LSTM", "GARCH"],
        "indicators": [
            "SMA",
            "RSI",
            "Bollinger Bands"
        ]
    }


# -----------------------------------------
# API 1: GET ALL AVAILABLE COMPANIES
# -----------------------------------------

@app.get("/stocks")
def available_stocks():

    try:

        return {
            "total_stocks": len(get_available_stocks()),
            "stocks": get_available_stocks()
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------------------
# API 2: STOCK SUMMARY
# -----------------------------------------

@app.get("/market-summary")
def market_summary(symbol: str = "NIFTY50"):

    try:

        return get_stock_summary(symbol.upper())

    except (ValueError, FileNotFoundError) as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------------------
# API 3: HISTORICAL STOCK DATA
# -----------------------------------------

@app.get("/market-data")
def market_data(
    symbol: str = "NIFTY50",
    limit: int = 250
):

    try:

        df = get_historical_data(symbol.upper())

        df = df.tail(min(max(limit, 1), 2000)).copy()

        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

        df = df.astype(object).where(
            pd.notna(df),
            None
        )

        return {
            "symbol": symbol.upper(),
            "total_records": len(df),
            "data": df.to_dict(orient="records")
        }

    except (ValueError, FileNotFoundError) as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------------------
# TECHNICAL INDICATOR CALCULATION
# -----------------------------------------

def calculate_indicators(df):

    df = df.copy()

    # Simple Moving Average
    df["SMA_20"] = df["Close"].rolling(
        window=20
    ).mean()

    df["SMA_50"] = df["Close"].rolling(
        window=50
    ).mean()

    # RSI Calculation
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI_14"] = 100 - (
        100 / (1 + rs)
    )

    # Bollinger Bands
    rolling_mean = df["Close"].rolling(20).mean()

    rolling_std = df["Close"].rolling(20).std()

    df["Upper_Band"] = (
        rolling_mean + (2 * rolling_std)
    )

    df["Lower_Band"] = (
        rolling_mean - (2 * rolling_std)
    )

    return df


# -----------------------------------------
# API 4: TECHNICAL INDICATORS
# -----------------------------------------

@app.get("/technical-indicators")
def technical_indicators(symbol: str = "NIFTY50"):

    try:

        df = get_historical_data(symbol.upper())

        df = calculate_indicators(df)

        columns = [
            "Date",
            "Close",
            "SMA_20",
            "SMA_50",
            "RSI_14",
            "Upper_Band",
            "Lower_Band"
        ]

        df = df[columns].tail(250).copy()

        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

        df = df.astype(object).where(
            pd.notna(df),
            None
        )

        return {
            "symbol": symbol.upper(),
            "indicators": df.to_dict(
                orient="records"
            )
        }

    except (ValueError, FileNotFoundError) as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------------------
# SERVER INFORMATION
# -----------------------------------------

@app.get("/about")
def about():

    return {
        "application": "StockVision",
        "backend": "FastAPI",
        "machine_learning": "LSTM",
        "volatility_model": "GARCH",
        "data_processing": "Pandas",
        "technical_analysis": [
            "SMA 20",
            "SMA 50",
            "RSI 14",
            "Bollinger Bands"
        ]
    }
@app.get("/lstm-prediction")
def lstm_prediction(symbol: str = "TCS"):

    try:
        result = train_lstm_model(symbol.upper())
        return result

    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # -----------------------------------------
# API: GARCH VOLATILITY FORECAST
# -----------------------------------------

@app.get("/garch-forecast")
def garch_forecast(symbol: str = "TCS"):

    try:

        result = train_garch_model(
            symbol.upper()
        )

        return result

    except (ValueError, FileNotFoundError) as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    # ==========================================
# API: STOCK DATA UPDATE STATUS
# ==========================================

@app.get("/data-status")
def data_status():

    try:
        base_dir = Path(__file__).resolve().parent.parent
        stock_dir = base_dir / "data" / "stocks"

        files = list(stock_dir.glob("*.csv"))

        if not files:
            return {
                "status": "No Data",
                "total_files": 0,
                "last_updated": None
            }

        # Find the oldest and newest file update times
        file_times = [
            file.stat().st_mtime
            for file in files
        ]

        oldest_update = min(file_times)
        newest_update = max(file_times)

        oldest_datetime = datetime.fromtimestamp(
            oldest_update
        ).astimezone()

        newest_datetime = datetime.fromtimestamp(
            newest_update
        ).astimezone()

        return {
            "status": "Available",
            "total_files": len(files),
            "last_updated": newest_datetime.strftime(
                "%d %b %Y, %I:%M %p"
            ),
            "oldest_file_updated": oldest_datetime.strftime(
                "%d %b %Y, %I:%M %p"
            ),
            "newest_file_updated": newest_datetime.strftime(
                "%d %b %Y, %I:%M %p"
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
       # -----------------------------------------
# API: AI MARKET ANALYSIS
# -----------------------------------------

@app.get("/market-analysis")
def market_analysis(symbol: str = "NIFTY50"):

    try:
        return generate_market_analysis(symbol.upper())

    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/backtest")
def backtest(symbol: str = "TCS"):

    try:
        return run_backtest(symbol.upper())

    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )