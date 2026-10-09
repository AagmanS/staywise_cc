import pandas as pd
from sklearn.model_selection import train_test_split


# ==========================================
# 1. LOAD CLEANED DATASET
# ==========================================

df = pd.read_csv("data/telco_cleaned.csv")

print("\nOriginal Dataset Shape:")
print(df.shape)


# ==========================================
# 2. SEPARATE FEATURES AND TARGET
# ==========================================

X = df.drop("Churn Label", axis=1)

y = df["Churn Label"].map({
    "No": 0,
    "Yes": 1
})


print("\nFeatures Shape:")
print(X.shape)

print("\nTarget Shape:")
print(y.shape)


# ==========================================
# 3. FIRST SPLIT
#    70% TRAIN
#    30% TEMPORARY
# ==========================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=42
)


# ==========================================
# 4. SECOND SPLIT
#    15% VALIDATION
#    15% TEST
# ==========================================

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=42
)


# ==========================================
# 5. DISPLAY SHAPES
# ==========================================

print("\n========== DATA SPLIT ==========")

print("Training set:")
print(X_train.shape)

print("\nValidation set:")
print(X_val.shape)

print("\nTest set:")
print(X_test.shape)


# ==========================================
# 6. CHECK TARGET DISTRIBUTION
# ==========================================

print("\n========== TARGET DISTRIBUTION ==========")

print("\nTraining:")
print(y_train.value_counts(normalize=True).mul(100).round(2))

print("\nValidation:")
print(y_val.value_counts(normalize=True).mul(100).round(2))

print("\nTest:")
print(y_test.value_counts(normalize=True).mul(100).round(2))
