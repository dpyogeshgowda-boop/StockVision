import yfinance as yf
import pandas as pd

# Step 1: Select NIFTY 50
stock_symbol = "^NSEI"

# Step 2: Download historical data
stock_data = yf.download(
    stock_symbol,
    period="5y",
    interval="1d"
)

# Step 3: Display the first 5 records
print("\nNIFTY 50 Historical Data")

print(stock_data.head())

# Step 4: Display dataset information
print("\nDataset Information")

print(stock_data.info())

# Step 5: Save data into CSV
stock_data.to_csv("nifty50_data.csv")

print("\nData saved successfully!")