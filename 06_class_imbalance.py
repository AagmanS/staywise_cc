import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)


# ==========================================
# 1. LOAD CLEANED DATASET
# ==========================================

df = pd.read_csv("data/telco_cleaned.csv")


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
# 6. FIT PREPROCESSOR ONLY ON TRAINING DATA
# ==========================================

X_train_processed = preprocessor.fit_transform(X_train)

X_val_processed = preprocessor.transform(X_val)

X_test_processed = preprocessor.transform(X_test)


# ==========================================
# 7. FUNCTION TO EVALUATE MODEL
# ==========================================

def evaluate_model(model, name):

    model.fit(X_train_processed, y_train)

    # Probability of churn
    probabilities = model.predict_proba(
        X_test_processed
    )[:, 1]

    # Default threshold = 0.50
    predictions = (
        probabilities >= 0.50
    ).astype(int)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    pr_auc = average_precision_score(
        y_test,
        probabilities
    )

    cm = confusion_matrix(
        y_test,
        predictions
    )

    print("\n======================================")
    print(name)
    print("======================================")

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")
    print(f"PR-AUC    : {pr_auc:.4f}")

    print("\nConfusion Matrix:")
    print(cm)


# ==========================================
# 8. BASELINE MODEL
# ==========================================

baseline_model = LogisticRegression(
    max_iter=1000,
    random_state=42
)

evaluate_model(
    baseline_model,
    "BASELINE LOGISTIC REGRESSION"
)


# ==========================================
# 9. BALANCED MODEL
# ==========================================

balanced_model = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    random_state=42
)

evaluate_model(
    balanced_model,
    "BALANCED LOGISTIC REGRESSION"
)
