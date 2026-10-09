import pandas as pd

# ---------------------------------------
# STEP 1: LOAD DATASET
# ---------------------------------------

file_path = "data/Telco_customer_churn.xlsx"

df = pd.read_excel(file_path)

# ---------------------------------------
# STEP 2: BASIC INFORMATION
# ---------------------------------------

print("\n========== DATASET SHAPE ==========")
print(df.shape)

print("\n========== FIRST 5 ROWS ==========")
print(df.head())

print("\n========== COLUMN NAMES ==========")
print(df.columns.tolist())

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== DATASET INFORMATION ==========")
df.info()

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATE ROWS ==========")
print(df.duplicated().sum())

print("\n========== TARGET DISTRIBUTION ==========")
print(df["Churn Label"].value_counts())