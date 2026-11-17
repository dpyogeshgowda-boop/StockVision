import numpy as np
import pandas as pd

from backend.data_service import load_stock_data, STOCKS


def calculate_indicators(df):
    """Calculate technical indicators for historical stock data."""

    df = df.copy()

    # Simple Moving Averages
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()

    # RSI calculation
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI_14"] = 100 - (100 / (1 + rs))

    # Handle periods with gains but no losses
    df.loc[
        (avg_loss == 0) & (avg_gain > 0),
        "RSI_14"
    ] = 100

    # Bollinger Bands
    rolling_mean = df["Close"].rolling(20).mean()
    rolling_std = df["Close"].rolling(20).std()

    df["Upper_Band"] = rolling_mean + (2 * rolling_std)
    df["Lower_Band"] = rolling_mean - (2 * rolling_std)

    return df
def generate_market_analysis(symbol="NIFTY50"):

    symbol = symbol.upper()

    df = load_stock_data(symbol)
    df = calculate_indicators(df)

    latest = df.iloc[-1]

    close = float(latest["Close"])
    sma20 = latest["SMA_20"]
    sma50 = latest["SMA_50"]
    rsi = latest["RSI_14"]

    upper = latest["Upper_Band"]
    lower = latest["Lower_Band"]

    if pd.isna(sma20) or pd.isna(sma50):
        market_trend = "Insufficient Data"
        trend_description = "Not enough historical data to calculate moving averages."
    elif sma20 > sma50:
        market_trend = "Bullish"
        trend_description = "The 20-day moving average is above the 50-day moving average."
    elif sma20 < sma50:
        market_trend = "Bearish"
        trend_description = "The 20-day moving average is below the 50-day moving average."
    else:
        market_trend = "Sideways"
        trend_description = "The moving averages are nearly equal."

    if pd.isna(rsi):
        rsi_status = "Unavailable"
        rsi_description = "RSI could not be calculated."
    elif rsi >= 70:
        rsi_status = "Overbought"
        rsi_description = "RSI is above 70, indicating potentially overbought conditions."
    elif rsi <= 30:
        rsi_status = "Oversold"
        rsi_description = "RSI is below 30, indicating potentially oversold conditions."
    else:
        rsi_status = "Neutral"
        rsi_description = "RSI is between 30 and 70."

    if pd.isna(upper) or pd.isna(lower):
        bollinger_status = "Unavailable"
        bollinger_description = "Bollinger Bands could not be calculated."
    elif close > upper:
        bollinger_status = "Above Upper Band"
        bollinger_description = "The closing price is above the upper Bollinger Band."
    elif close < lower:
        bollinger_status = "Below Lower Band"
        bollinger_description = "The closing price is below the lower Bollinger Band."
    else:
        bollinger_status = "Within Bands"
        bollinger_description = "The closing price is within the Bollinger Bands."

    return {
        "symbol": symbol,
        "company": STOCKS[symbol]["name"],
        "latest_date": str(latest["Date"].date()),
        "latest_price": close,
        "market_trend": market_trend,
        "trend_description": trend_description,
        "technical_indicators": {
            "SMA_20": None if pd.isna(sma20) else round(float(sma20), 2),
            "SMA_50": None if pd.isna(sma50) else round(float(sma50), 2),
            "RSI_14": None if pd.isna(rsi) else round(float(rsi), 2),
            "RSI_status": rsi_status,
            "RSI_description": rsi_description,
            "upper_bollinger_band": None if pd.isna(upper) else round(float(upper), 2),
            "lower_bollinger_band": None if pd.isna(lower) else round(float(lower), 2),
            "bollinger_status": bollinger_status,
            "bollinger_description": bollinger_description
        },
        "overall_interpretation": (
            f"The technical indicators currently show a {market_trend.lower()} trend "
            f"with an RSI status of {rsi_status.lower()}. "
            "These indicators describe historical market conditions."
        ),
        "disclaimer": (
            "This analysis uses historical technical indicators. "
            "It is not a guaranteed prediction or investment recommendation."
        )
    }


def run_backtest(symbol="TCS"):

    symbol = symbol.upper()

    df = load_stock_data(symbol)

    if len(df) < 60:
        raise ValueError("At least 60 historical records are required.")

    df = calculate_indicators(df)

    df = df.dropna(subset=["SMA_20", "SMA_50"]).copy()

    # Daily returns
    df["Daily_Return"] = df["Close"].pct_change()

    # Trading signal:
    # 1 = Hold stock
    # 0 = Stay out of market
    df["Signal"] = (df["SMA_20"] > df["SMA_50"]).astype(int)

    # Use yesterday's signal to avoid look-ahead bias.
    df["Position"] = df["Signal"].shift(1).fillna(0)

    # Assume transaction cost of 0.1% per position change.
    transaction_cost = 0.001

    df["Trades"] = df["Position"].diff().abs().fillna(
        df["Position"].abs()
    )

    df["Strategy_Return"] = (
        df["Position"] * df["Daily_Return"]
        - df["Trades"] * transaction_cost
    )

    df["Buy_Hold_Return"] = df["Daily_Return"]

    df = df.dropna(subset=["Strategy_Return", "Buy_Hold_Return"])

    if df.empty:
        raise ValueError("Not enough valid data to perform backtesting.")

    df["Strategy_Equity"] = (
        1 + df["Strategy_Return"]
    ).cumprod()

    df["Buy_Hold_Equity"] = (
        1 + df["Buy_Hold_Return"]
    ).cumprod()

    total_return = (
        df["Strategy_Equity"].iloc[-1] - 1
    ) * 100

    buy_hold_return = (
        df["Buy_Hold_Equity"].iloc[-1] - 1
    ) * 100

    daily_volatility = df["Strategy_Return"].std()

    annualized_volatility = (
        daily_volatility * np.sqrt(252) * 100
        if pd.notna(daily_volatility)
        else 0
    )

    mean_return = df["Strategy_Return"].mean()

    std_return = df["Strategy_Return"].std()

    sharpe_ratio = (
        (mean_return / std_return) * np.sqrt(252)
        if pd.notna(std_return) and std_return != 0
        else 0
    )

    running_max = df["Strategy_Equity"].cummax()

    drawdown = (
        df["Strategy_Equity"] / running_max
    ) - 1

    max_drawdown = drawdown.min() * 100

    winning_days = (
        df["Strategy_Return"] > 0
    ).sum()

    total_days = len(df)

    win_rate = (
        winning_days / total_days
    ) * 100

    total_trades = int(
        (df["Trades"] > 0).sum()
    )

    return {
        "symbol": symbol,
        "company": STOCKS[symbol]["name"],
        "strategy": "SMA 20 / SMA 50 Crossover",
        "backtest_period": {
            "start_date": str(df["Date"].min().date()),
            "end_date": str(df["Date"].max().date())
        },
        "total_records": len(df),
        "performance": {
            "strategy_return_percent": round(float(total_return), 2),
            "buy_and_hold_return_percent": round(float(buy_hold_return), 2),
            "annualized_volatility_percent": round(float(annualized_volatility), 2),
            "sharpe_ratio": round(float(sharpe_ratio), 2),
            "maximum_drawdown_percent": round(float(max_drawdown), 2),
            "win_rate_percent": round(float(win_rate), 2),
            "total_position_changes": total_trades
        },
        "equity_curve": [
    {
        "date": row["Date"].strftime("%Y-%m-%d"),
        "strategy_value": round(float(row["Strategy_Equity"]), 4),
        "buy_hold_value": round(float(row["Buy_Hold_Equity"]), 4)
    }
    for _, row in df.tail(250).iterrows()
],
        "disclaimer": (
            "Historical backtest results do not guarantee future performance. "
            "Transaction costs are assumed to be 0.1% per position change. "
            "Taxes, slippage and other trading expenses are not included."
        )
    }