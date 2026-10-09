import pandas as pd

# ==========================================
# 1. LOAD DATASET
# ==========================================

file_path = "data/Telco_customer_churn.xlsx"

df = pd.read_excel(file_path)

print("\nOriginal Shape:", df.shape)


# ==========================================
# 2. REMOVE UNNECESSARY / LEAKAGE COLUMNS
# ==========================================

columns_to_remove = [
    "CustomerID",
    "Count",
    "Country",
    "State",
    "City",
    "Zip Code",
    "Lat Long",
    "Latitude",
    "Longitude",
    "Churn Value",
    "Churn Score",
    "CLTV",
    "Churn Reason"
]

df = df.drop(columns=columns_to_remove)

print("\nAfter Removing Columns:", df.shape)


# ==========================================
# 3. CONVERT TOTAL CHARGES TO NUMERIC
# ==========================================

df["Total Charges"] = pd.to_numeric(
    df["Total Charges"],
    errors="coerce"
)

print("\nMissing values after conversion:")
print(df["Total Charges"].isnull().sum())


# ==========================================
# 4. CHECK MISSING VALUES
# ==========================================

print("\nComplete Missing Value Report:")
print(df.isnull().sum())


# ==========================================
# 5. FILL MISSING TOTAL CHARGES
# ==========================================

median_total = df["Total Charges"].median()

df["Total Charges"] = df["Total Charges"].fillna(median_total)

print("\nMissing after imputation:")
print(df.isnull().sum().sum())


# ==========================================
# 6. SAVE CLEAN DATASET
# ==========================================

output_path = "data/telco_cleaned.csv"

df.to_csv(output_path, index=False)

print("\nCleaned dataset saved successfully!")

print("\nFinal Shape:", df.shape)

print("\nFinal Columns:")
print(df.columns.tolist())
