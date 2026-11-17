import numpy as np
import pandas as pd
from arch import arch_model

from backend.data_service import get_historical_data


def train_garch_model(symbol="TCS"):

    symbol = symbol.upper()

    # STEP 1: Load selected company's historical data
    df = get_historical_data(symbol)

    if len(df) < 100:
        raise ValueError(
            "At least 100 historical records are required for GARCH training."
        )

    # STEP 2: Calculate daily percentage returns
    returns = (
        df["Close"]
        .pct_change()
        .dropna() * 100
    )

    returns = returns.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    if len(returns) < 100:
        raise ValueError(
            "Insufficient valid returns for GARCH training."
        )

    # STEP 3: Build GARCH(1,1) model
    model = arch_model(
        returns,
        vol="GARCH",
        p=1,
        q=1,
        mean="Constant",
        dist="Normal"
    )

    # STEP 4: Train model
    result = model.fit(disp="off")

    # STEP 5: Calculate historical volatility
    historical_volatility = (
        result.conditional_volatility
    )

    latest_volatility = float(
        historical_volatility.iloc[-1]
    )

    # STEP 6: Forecast next five trading days
    forecast = result.forecast(
        horizon=5,
        reindex=False
    )

    variance_forecast = (
        forecast.variance.iloc[-1]
    )

    volatility_forecast = np.sqrt(
        variance_forecast
    )

    forecast_values = [
        round(float(value), 4)
        for value in volatility_forecast.values
    ]

    # STEP 7: Calculate annualized volatility
    average_daily_volatility = float(
        np.mean(forecast_values)
    )

    annualized_volatility = (
        average_daily_volatility * np.sqrt(252)
    )

    # STEP 8: Classify estimated risk
    # These are illustrative project thresholds.
    if annualized_volatility < 15:
        risk_level = "Low"
    elif annualized_volatility < 25:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    # STEP 9: Return results
    return {
        "symbol": symbol,
        "model": "GARCH(1,1)",
        "latest_actual_price": round(
            float(df["Close"].iloc[-1]), 2
        ),
        "latest_daily_volatility": round(
            latest_volatility, 4
        ),
        "annualized_forecast_volatility": round(
            float(annualized_volatility), 4
        ),
        "risk_level": risk_level,
        "forecast_horizon": "Next 5 trading days",
        "forecast_daily_volatility": forecast_values,
        "training_records": int(len(returns))
    }