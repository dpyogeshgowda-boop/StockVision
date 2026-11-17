import pandas as pd
import numpy as np

# Step 1: Load the dataset
df = pd.read_csv("nifty50_data.csv", header=[0, 1], index_col=0)

print("Original Dataset:")
print(df.head())

# Step 2: Check dataset shape
print("\nDataset Shape:")
print(df.shape)

# Step 3: Check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Step 4: Remove duplicate records
df = df[~df.index.duplicated(keep="first")]

# Step 5: Handle missing values
df = df.dropna()

# Step 6: Convert index into date format
df.index = pd.to_datetime(df.index)

# Step 7: Sort dates
df = df.sort_index()

# Step 8: Save cleaned dataset
df.to_csv("cleaned_nifty50_data.csv")

print("\nCleaned Dataset:")
print(df.head())

print("\nFinal Dataset Shape:")
print(df.shape)

print("\nData Cleaning Completed Successfully!")