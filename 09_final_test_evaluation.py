import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

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
# 5. PREPROCESSING
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
# 6. FIT PREPROCESSOR ONLY ON TRAINING DATA
# ==========================================

X_train_processed = preprocessor.fit_transform(X_train)

X_val_processed = preprocessor.transform(X_val)

X_test_processed = preprocessor.transform(X_test)


# ==========================================
# 7. TRAIN BALANCED LOGISTIC REGRESSION
# ==========================================

model = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    random_state=42
)

model.fit(X_train_processed, y_train)

print("\nLogistic Regression training completed.")


# ==========================================
# 8. GET TEST PROBABILITIES
# ==========================================

y_test_probability = model.predict_proba(
    X_test_processed
)[:, 1]


# ==========================================
# 9. FINAL THRESHOLD
# ==========================================

# Selected from validation-set analysis
best_threshold = 0.20

y_test_pred = (
    y_test_probability >= best_threshold
).astype(int)


# ==========================================
# 10. FINAL TEST METRICS
# ==========================================

accuracy = accuracy_score(y_test, y_test_pred)

precision = precision_score(
    y_test,
    y_test_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_test_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_test_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_test_probability
)

pr_auc = average_precision_score(
    y_test,
    y_test_probability
)


# ==========================================
# 11. CONFUSION MATRIX
# ==========================================

tn, fp, fn, tp = confusion_matrix(
    y_test,
    y_test_pred
).ravel()


# ==========================================
# 12. BUSINESS COST
# ==========================================

fp_cost = 500
fn_cost = 5000

business_cost = (
    fp * fp_cost +
    fn * fn_cost
)


# ==========================================
# 13. DISPLAY RESULTS
# ==========================================

print("\n==========================================")
print("FINAL TEST EVALUATION")
print("==========================================")

print(f"Final Threshold: {best_threshold}")

print(f"\nAccuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"ROC-AUC:   {roc_auc:.4f}")
print(f"PR-AUC:    {pr_auc:.4f}")

print("\n------------------------------------------")
print("CONFUSION MATRIX")
print("------------------------------------------")

print(f"True Negatives (TN):  {tn}")
print(f"False Positives (FP): {fp}")
print(f"False Negatives (FN): {fn}")
print(f"True Positives (TP):  {tp}")

print("\n------------------------------------------")
print("BUSINESS COST")
print("------------------------------------------")

print(f"False Positive Cost: ₹{fp_cost}")
print(f"False Negative Cost: ₹{fn_cost}")
print(f"Total Business Cost: ₹{business_cost:,}")


# ==========================================
# 14. CLASSIFICATION REPORT
# ==========================================

print("\n==========================================")
print("CLASSIFICATION REPORT")
print("==========================================")

print(
    classification_report(
        y_test,
        y_test_pred,
        target_names=["No Churn", "Churn"],
        zero_division=0
    )
)
