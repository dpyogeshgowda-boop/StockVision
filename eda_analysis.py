import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned dataset
df = pd.read_csv("cleaned_nifty50_data.csv", header=[0, 1], index_col=0)

# Convert date index
df.index = pd.to_datetime(df.index)

# Display basic statistics
print("STATISTICAL ANALYSIS")

print(df.describe())

# Plot 1: Closing Price
plt.figure(figsize=(12, 6))

plt.plot(df.index, df[("Close", "^NSEI")])

plt.title("NIFTY 50 Historical Closing Prices")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.grid()

plt.show()

# Plot 2: Trading Volume
plt.figure(figsize=(12, 6))

plt.plot(df.index, df[("Volume", "^NSEI")])

plt.title("NIFTY 50 Trading Volume")
plt.xlabel("Date")
plt.ylabel("Volume")
plt.grid()

plt.show()