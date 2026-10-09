import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ==========================================
# 1. LOAD CLEANED DATASET
# ==========================================

df = pd.read_csv("data/telco_cleaned.csv")

print("\nDataset Shape:", df.shape)


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
# 4. DEFINE FEATURES
# ==========================================

numerical_features = [
    "Tenure Months",
    "Monthly Charges",
    "Total Charges"
]

categorical_features = [
    column for column in X.columns
    if column not in numerical_features
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
# 6. FIT PREPROCESSING ON TRAINING DATA
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

model.fit(
    X_train_processed,
    y_train
)


print("\nLogistic Regression training completed.")


# ==========================================
# 8. GET VALIDATION PROBABILITIES
# ==========================================

val_probabilities = model.predict_proba(
    X_val_processed
)[:, 1]


# ==========================================
# 9. BUSINESS COSTS
# ==========================================

FP_COST = 500
FN_COST = 5000


# ==========================================
# 10. TEST DIFFERENT THRESHOLDS
# ==========================================

thresholds = [
    0.20,
    0.30,
    0.40,
    0.50,
    0.60,
    0.70
]


results = []


print("\n==========================================")
print("THRESHOLD ANALYSIS")
print("==========================================")


for threshold in thresholds:

    predictions = (
        val_probabilities >= threshold
    ).astype(int)

    # Confusion matrix

    tn, fp, fn, tp = confusion_matrix(
        y_val,
        predictions
    ).ravel()

    # Metrics

    precision = precision_score(
        y_val,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_val,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_val,
        predictions,
        zero_division=0
    )

    # Business cost

    business_cost = (
        fp * FP_COST
        +
        fn * FN_COST
    )

    print(f"\nThreshold: {threshold}")

    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TP: {tp}")

    print(f"Business Cost: ₹{business_cost:,}")

    results.append({

        "Threshold": threshold,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
        "Business Cost": business_cost

    })


# ==========================================
# 11. CREATE RESULTS TABLE
# ==========================================

results_df = pd.DataFrame(results)


print("\n\n==========================================")
print("COMPLETE THRESHOLD COMPARISON")
print("==========================================")

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ==========================================
# 12. FIND BEST THRESHOLD
# ==========================================

best_row = results_df.loc[
    results_df["Business Cost"].idxmin()
]


print("\n\n==========================================")
print("OPTIMAL THRESHOLD")
print("==========================================")

print(
    f"Best Threshold: {best_row['Threshold']}"
)

print(
    f"Minimum Business Cost: "
    f"₹{best_row['Business Cost']:,.0f}"
)

print(
    f"Precision: {best_row['Precision']:.4f}"
)

print(
    f"Recall: {best_row['Recall']:.4f}"
)

print(
    f"F1 Score: {best_row['F1']:.4f}"
)

print(
    f"False Positives: "
    f"{best_row['FP']:.0f}"
)

print(
    f"False Negatives: "
    f"{best_row['FN']:.0f}"
)
