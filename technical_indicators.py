import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# STEP 1: Load cleaned dataset

df = pd.read_csv(
    "cleaned_nifty50_data.csv",
    header=[0, 1],
    index_col=0
)

df.index = pd.to_datetime(df.index)

# Extract closing price
close = df[("Close", "^NSEI")]

# STEP 2: Calculate SMA

df[("SMA_20", "^NSEI")] = close.rolling(window=20).mean()

df[("SMA_50", "^NSEI")] = close.rolling(window=50).mean()


# STEP 3: Calculate RSI

delta = close.diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

average_gain = gain.ewm(
    alpha=1/14,
    min_periods=14,
    adjust=False
).mean()

average_loss = loss.ewm(
    alpha=1/14,
    min_periods=14,
    adjust=False
).mean()

rs = average_gain / average_loss

df[("RSI_14", "^NSEI")] = 100 - (100 / (1 + rs))


# STEP 4: Calculate Bollinger Bands

middle_band = close.rolling(window=20).mean()

standard_deviation = close.rolling(window=20).std()

df[("Upper_Band", "^NSEI")] = (
    middle_band + (2 * standard_deviation)
)

df[("Lower_Band", "^NSEI")] = (
    middle_band - (2 * standard_deviation)
)


# STEP 5: Display results

print("\nTECHNICAL INDICATORS")

print(df.tail(10))


# STEP 6: Plot SMA

plt.figure(figsize=(12, 6))

plt.plot(close, label="NIFTY 50 Closing Price")

plt.plot(
    df[("SMA_20", "^NSEI")],
    label="SMA 20"
)

plt.plot(
    df[("SMA_50", "^NSEI")],
    label="SMA 50"
)

plt.title("NIFTY 50 - Moving Average Analysis")

plt.xlabel("Date")
plt.ylabel("Price")

plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("sma_analysis.png")
plt.show()
plt.close()


# STEP 7: Plot RSI

plt.figure(figsize=(12, 6))

plt.plot(
    df[("RSI_14", "^NSEI")],
    label="RSI 14"
)

plt.axhline(70, linestyle="--", label="Overbought (70)")
plt.axhline(30, linestyle="--", label="Oversold (30)")

plt.title("NIFTY 50 - RSI Analysis")

plt.xlabel("Date")
plt.ylabel("RSI")

plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("rsi_analysis.png")
plt.show()
plt.close()


# STEP 8: Plot Bollinger Bands

plt.figure(figsize=(12, 6))

plt.plot(close, label="Closing Price")

plt.plot(
    df[("Upper_Band", "^NSEI")],
    label="Upper Band"
)

plt.plot(
    middle_band,
    label="Middle Band"
)

plt.plot(
    df[("Lower_Band", "^NSEI")],
    label="Lower Band"
)

plt.title("NIFTY 50 - Bollinger Bands Analysis")

plt.xlabel("Date")
plt.ylabel("Price")

plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("bollinger_bands.png")
plt.show()
plt.close()


# STEP 9: Save final dataset

df.to_csv("nifty50_technical_data.csv")

print("\nTechnical Indicators Calculated Successfully!")
print("Dataset saved successfully!")