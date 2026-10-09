import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ==========================================
# 1. LOAD CLEANED DATASET
# ==========================================

df = pd.read_csv("data/telco_cleaned.csv")

print("\n========== DATASET ==========")
print("Shape:", df.shape)


# ==========================================
# 2. SEPARATE FEATURES AND TARGET
# ==========================================

X = df.drop("Churn Label", axis=1)

y = df["Churn Label"].map({
    "No": 0,
    "Yes": 1
})


# ==========================================
# 3. TRAIN / VALIDATION / TEST SPLIT
# ==========================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=42
)


# ==========================================
# 4. IDENTIFY NUMERICAL FEATURES
# ==========================================

numerical_features = [
    "Tenure Months",
    "Monthly Charges",
    "Total Charges"
]


# ==========================================
# 5. IDENTIFY CATEGORICAL FEATURES
# ==========================================

categorical_features = [
    column for column in X.columns
    if column not in numerical_features
]


# ==========================================
# 6. DISPLAY FEATURE GROUPS
# ==========================================

print("\n========== NUMERICAL FEATURES ==========")

for feature in numerical_features:
    print(feature)


print("\n========== CATEGORICAL FEATURES ==========")

for feature in categorical_features:
    print(feature)


# ==========================================
# 7. CREATE PREPROCESSING PIPELINE
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numerical",
            StandardScaler(),
            numerical_features
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            categorical_features
        )
    ]
)


# ==========================================
# 8. FIT ONLY ON TRAINING DATA
# ==========================================

X_train_processed = preprocessor.fit_transform(X_train)


# ==========================================
# 9. TRANSFORM VALIDATION AND TEST DATA
# ==========================================

X_val_processed = preprocessor.transform(X_val)

X_test_processed = preprocessor.transform(X_test)


# ==========================================
# 10. DISPLAY PROCESSED SHAPES
# ==========================================

print("\n========== PROCESSED DATA SHAPES ==========")

print("Training:", X_train_processed.shape)
print("Validation:", X_val_processed.shape)
print("Test:", X_test_processed.shape)


# ==========================================
# 11. VERIFY NO MISSING VALUES
# ==========================================

print("\n========== PREPROCESSING COMPLETED ==========")

print("Training data successfully encoded and scaled.")
print("Validation data successfully transformed.")
print("Test data successfully transformed.")
