from backend.data_service import (
    load_stock_data,
    get_stock_summary
)

df = load_stock_data()

print("\nDATASET SUMMARY")
print(get_stock_summary())

print("\nFIRST FIVE RECORDS")
print(df.head().to_string())

print("\nAVAILABLE COLUMNS")
print(df.columns.tolist())

print("\nDATA TYPES")
print(df.dtypes)

print("\nDATA LOADED SUCCESSFULLY!")