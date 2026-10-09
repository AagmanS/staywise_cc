import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression


# ==========================================
# 1. LOAD CLEANED DATA
# ==========================================

df = pd.read_csv("data/telco_cleaned.csv")

print("Dataset Shape:", df.shape)


# ==========================================
# 2. SEPARATE FEATURES AND TARGET
# ==========================================

X = df.drop("Churn Label", axis=1)
y = df["Churn Label"].map({"No": 0, "Yes": 1})


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
# 4. DEFINE FEATURES
# ==========================================

numerical_features = [
    "Tenure Months",
    "Monthly Charges",
    "Total Charges"
]

categorical_features = [
    col for col in X.columns
    if col not in numerical_features
]


# ==========================================
# 5. CREATE PREPROCESSOR
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
# 6. FIT PREPROCESSOR ON TRAINING DATA
# ==========================================

X_train_processed = preprocessor.fit_transform(X_train)


# ==========================================
# 7. TRAIN BALANCED LOGISTIC REGRESSION
# ==========================================

model = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    random_state=42
)

model.fit(X_train_processed, y_train)

print("Logistic Regression training completed.")


# ==========================================
# 8. SELECTED THRESHOLD
# ==========================================

best_threshold = 0.20


# ==========================================
# 9. CREATE MODEL DIRECTORY
# ==========================================

os.makedirs("models", exist_ok=True)


# ==========================================
# 10. SAVE PREPROCESSOR
# ==========================================

joblib.dump(
    preprocessor,
    "models/churn_preprocessor.pkl"
)


# ==========================================
# 11. SAVE LOGISTIC REGRESSION MODEL
# ==========================================

joblib.dump(
    model,
    "models/churn_logistic_model.pkl"
)


# ==========================================
# 12. SAVE THRESHOLD
# ==========================================

joblib.dump(
    best_threshold,
    "models/churn_threshold.pkl"
)


# ==========================================
# 13. SAVE FEATURE INFORMATION
# ==========================================

feature_info = {
    "numerical_features": numerical_features,
    "categorical_features": categorical_features,
    "target": "Churn Label",
    "threshold": best_threshold,
    "model": "Balanced Logistic Regression"
}

joblib.dump(
    feature_info,
    "models/churn_feature_info.pkl"
)


# ==========================================
# 14. CONFIRMATION
# ==========================================

print("\n==========================================")
print("MODEL SAVING COMPLETED")
print("==========================================")

print("Preprocessor saved to:")
print("models/churn_preprocessor.pkl")

print("\nLogistic Regression model saved to:")
print("models/churn_logistic_model.pkl")

print("\nThreshold saved to:")
print("models/churn_threshold.pkl")

print("\nFeature information saved to:")
print("models/churn_feature_info.pkl")

print("\nSelected Threshold:", best_threshold)
print("\nChurnSense model is ready for deployment.")
