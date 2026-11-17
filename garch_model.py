import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from arch import arch_model

# STEP 1: Load historical stock data

df = pd.read_csv(
    "nifty50_technical_data.csv",
    header=[0, 1],
    index_col=0
)

df.index = pd.to_datetime(df.index)

close_prices = df[("Close", "^NSEI")]

# STEP 2: Calculate daily percentage returns

returns = close_prices.pct_change().dropna() * 100

print("Historical Stock Returns:")
print(returns.head())

# STEP 3: Build GARCH(1,1) model

model = arch_model(
    returns,
    vol="GARCH",
    p=1,
    q=1,
    mean="Constant",
    dist="Normal"
)

# STEP 4: Train the model

print("\nTraining GARCH Model...")

result = model.fit(disp="off")

print(result.summary())

# STEP 5: Calculate historical volatility

df["GARCH_Volatility"] = result.conditional_volatility.reindex(df.index)

# STEP 6: Forecast future volatility

forecast = result.forecast(horizon=5, reindex=False)

variance_forecast = forecast.variance.iloc[-1]

volatility_forecast = np.sqrt(variance_forecast)

print("\nNEXT 5 TRADING DAYS VOLATILITY FORECAST")

print(volatility_forecast)

# STEP 7: Plot historical volatility

plt.figure(figsize=(12, 6))

plt.plot(
    result.conditional_volatility,
    label="Historical GARCH Volatility"
)

plt.title("NIFTY 50 - Historical Market Volatility")

plt.xlabel("Date")
plt.ylabel("Daily Volatility (%)")

plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("historical_volatility.png")

plt.show()
plt.close()

# STEP 8: Plot future volatility forecast

plt.figure(figsize=(10, 5))

plt.plot(
    range(1, 6),
    volatility_forecast.values,
    marker="o",
    label="Forecast Volatility"
)

plt.title("NIFTY 50 - Five Day Volatility Forecast")

plt.xlabel("Future Trading Days")
plt.ylabel("Forecast Daily Volatility (%)")

plt.xticks(range(1, 6))

plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("volatility_forecast.png")

plt.show()
plt.close()

# STEP 9: Save dataset

df.to_csv("nifty50_garch_data.csv")

print("\nGARCH Volatility Forecasting Completed!")