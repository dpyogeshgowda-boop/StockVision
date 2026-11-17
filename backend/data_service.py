import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STOCK_DIR = BASE_DIR / "data" / "stocks"
CSV_FILE = BASE_DIR / "ind_nifty50list.csv"
NIFTY_FILE = BASE_DIR / "nifty50_technical_data.csv"


def load_stock_list():
    stocks = pd.read_csv(CSV_FILE, sep="\t", encoding="utf-8-sig")
    stocks.columns = stocks.columns.str.strip()

    stock_dict = {
        "NIFTY50": {
            "name": "NIFTY 50",
            "file": NIFTY_FILE
        }
    }

    for _, row in stocks.iterrows():
        symbol = str(row["Symbol"]).strip()

        stock_dict[symbol] = {
            "name": row["Company Name"],
            "file": STOCK_DIR / f"{symbol}.csv"
        }

    return stock_dict


STOCKS = load_stock_list()


def load_stock_data(symbol="NIFTY50"):
    symbol = symbol.upper()

    if symbol not in STOCKS:
        raise ValueError("Invalid stock symbol")

    file_path = STOCKS[symbol]["file"]

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found for {symbol}")

    df = pd.read_csv(file_path)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(col[0]).strip() for col in df.columns]

    df.columns = [str(col).strip() for col in df.columns]

    if "Price" in df.columns:
        df.rename(columns={"Price": "Date"}, inplace=True)

    df = df[df["Date"].astype(str).str.strip() != "Date"]

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
    df["Date"] = df["Date"].dt.tz_localize(None)

    df = df.dropna(subset=["Date"])

    for col in df.columns:
        if col != "Date":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Close"])
    df = df.drop_duplicates(subset=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    return df


def get_available_stocks():
    available = []

    for symbol, details in STOCKS.items():
        if details["file"].exists():
            available.append({
                "symbol": symbol,
                "name": details["name"]
            })

    return available


def get_stock_summary(symbol="NIFTY50"):
    symbol = symbol.upper()
    df = load_stock_data(symbol)

    return {
        "symbol": symbol,
        "name": STOCKS[symbol]["name"],
        "total_records": len(df),
        "latest_date": str(df["Date"].max().date()),
        "oldest_date": str(df["Date"].min().date()),
        "latest_close": float(df["Close"].iloc[-1])
    }


def get_historical_data(symbol="NIFTY50"):
    return load_stock_data(symbol)
