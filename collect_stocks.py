import pandas as pd
import yfinance as yf
from pathlib import Path
import time

# Project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "stocks"
CSV_FILE = BASE_DIR / "ind_nifty50list.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Read official NIFTY 50 company list
stocks = pd.read_csv(CSV_FILE, sep="\t", encoding="utf-8-sig")
stocks.columns = stocks.columns.str.strip()

# Remove unwanted spaces from column names
stocks.columns = stocks.columns.str.strip()

print("CSV Columns:", stocks.columns.tolist())

if "Company Name" not in stocks.columns or "Symbol" not in stocks.columns:
    raise ValueError("Required columns not found. Check the CSV file.")

print("Total companies:", len(stocks))

print("NIFTY 50 STOCK DATA COLLECTION")
print("=" * 50)
print("Total companies:", len(stocks))

successful = []
failed = []

for index, row in stocks.iterrows():

    company = row["Company Name"]
    symbol = str(row["Symbol"]).strip()


    yahoo_symbol = symbol + ".NS"

    print(f"\nDownloading {index + 1}/50: {company}")
    print("Symbol:", yahoo_symbol)

    try:
        data = yf.download(
            yahoo_symbol,
            period="5y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False
        )

        if data.empty:
            print("No data available!")
            failed.append(symbol)
            continue

        # Handle Yahoo Finance multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.reset_index()

        # Save individual company dataset
        output_file = DATA_DIR / f"{symbol}.csv"
        data.to_csv(output_file, index=False)

        print("Saved:", output_file.name)
        print("Records:", len(data))

        successful.append(symbol)

    except Exception as error:
        print("Error:", error)
        failed.append(symbol)

    time.sleep(1)

print("\n" + "=" * 50)
print("COLLECTION COMPLETED")
print("Successful:", len(successful))
print("Failed:", len(failed))

if failed:
    print("Failed symbols:", failed)