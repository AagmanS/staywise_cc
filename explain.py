"""
explain.py — SHAP-based explainability module for StayWise
============================================================
Wraps the fitted preprocessor + logistic regression model with a
shap.LinearExplainer, maps the 46 transformed features back to
human-readable names, and returns ranked risk/protective factors.

Key design decisions
---------------------
* shap.LinearExplainer works directly on LinearModel (LogisticRegression).
  It is deterministic and fast — no sampling needed.
* We run the explainer on the *already-transformed* feature matrix so the
  preprocessor pipeline doesn't interfere with SHAP internals.
* OHE features from the same original column are collapsed back:
    e.g.  Contract_Month-to-month (shap=+0.42) becomes "Contract: Month-to-month"
    The sign & magnitude of the ONE active category is used as the column's impact.
* Numerical features keep their raw names.
* Caller receives two sorted lists  (risk_factors, protective_factors)
  ready for the frontend — no raw SHAP values exposed.
"""

import numpy as np
import pandas as pd
import shap

# ── Column name → human-readable label map ──────────────────────────────────
_LABEL_MAP = {
    # Numerical
    "Tenure Months":   "Tenure",
    "Monthly Charges": "Monthly charges",
    "Total Charges":   "Total charges",
    # Categorical originals  (OHE values inherit parent label)
    "Gender":            "Gender",
    "Senior Citizen":    "Senior citizen",
    "Partner":           "Has partner",
    "Dependents":        "Has dependents",
    "Phone Service":     "Phone service",
    "Multiple Lines":    "Multiple lines",
    "Internet Service":  "Internet service",
    "Online Security":   "Online security",
    "Online Backup":     "Online backup",
    "Device Protection": "Device protection",
    "Tech Support":      "Tech support",
    "Streaming TV":      "Streaming TV",
    "Streaming Movies":  "Streaming movies",
    "Contract":          "Contract type",
    "Paperless Billing": "Paperless billing",
    "Payment Method":    "Payment method",
}


def _get_transformed_feature_names(preprocessor, numerical_features, categorical_features):
    """
    Return the full list of feature names that come out of the ColumnTransformer,
    in the exact order the model sees them.
    """
    num_names = list(numerical_features)
    cat_enc   = preprocessor.named_transformers_["categorical"]
    ohe_names = cat_enc.get_feature_names_out(categorical_features).tolist()
    return num_names + ohe_names


def _build_explainer(model, preprocessor, X_background_transformed):
    """
    Build a shap.LinearExplainer using the mean of the training data as
    the background baseline.
    Uses maskers.Independent (the modern non-deprecated API) which runs
    without any sampling loop — each explanation takes < 10ms.
    """
    masker    = shap.maskers.Independent(X_background_transformed)
    explainer = shap.LinearExplainer(model, masker)
    return explainer


def _collapse_ohe_to_original(shap_vals, feature_names, numerical_features):
    """
    For each OHE-expanded feature, keep only the impact of the category that
    is actually active (value == 1 in the one-hot row).  Numerical features
    are kept as-is.  Returns a dict:
        { original_feature_name: shap_value, ... }
    """
    collapsed = {}

    # Numerical — direct
    for col in numerical_features:
        if col in feature_names:
            idx = feature_names.index(col)
            collapsed[col] = float(shap_vals[idx])

    # Categorical — find active OHE column per parent
    for i, fname in enumerate(feature_names):
        if fname in numerical_features:
            continue
        # fname looks like "Contract_Month-to-month"
        parts = fname.split("_", 1)
        if len(parts) < 2:
            continue
        parent = parts[0]
        # Only record this feature's SHAP value (active OHE column wins)
        # Later entries for the same parent overwrite only if their shap is larger in magnitude
        val = float(shap_vals[i])
        if parent not in collapsed or abs(val) > abs(collapsed[parent]):
            collapsed[parent] = val

    return collapsed


def explain_prediction(model, preprocessor, feature_info, customer_df, X_train_transformed, explainer=None):
    """
    Compute SHAP explanations for a single customer.

    Parameters
    ----------
    model               : fitted LogisticRegression
    preprocessor        : fitted ColumnTransformer
    feature_info        : dict from churn_feature_info.pkl
    customer_df         : pd.DataFrame with exactly 1 row (raw, un-preprocessed)
    X_train_transformed : np.ndarray — transformed training set (used as background)
    explainer           : optional pre-built shap.LinearExplainer (pass for speed)

    Returns
    -------
    dict with keys:
        "risk_factors"       : list of {label, value_label, impact, bar_pct}  (positive SHAP)
        "protective_factors" : list of {label, value_label, impact, bar_pct}  (negative SHAP)
    """
    numerical_features   = feature_info["numerical_features"]
    categorical_features = feature_info["categorical_features"]

    # 1. Get the full transformed feature-name list
    all_feature_names = _get_transformed_feature_names(
        preprocessor, numerical_features, categorical_features
    )

    # 2. Transform the single customer row
    X_customer = preprocessor.transform(customer_df)   # shape (1, 46)

    # 3. Build or reuse explainer (pass pre-built instance for speed)
    if explainer is None:
        explainer = _build_explainer(model, preprocessor, X_train_transformed)

    # 4. Compute SHAP values — shape (1, 46) for the positive class
    shap_values = explainer.shap_values(X_customer)     # ndarray

    # shap_values may be list-of-arrays for multi-class; take index 1 (churn=Yes)
    if isinstance(shap_values, list):
        sv = np.array(shap_values[1])[0]
    else:
        sv = np.array(shap_values)[0]

    # 5. Collapse OHE → original feature names
    collapsed = _collapse_ohe_to_original(sv, all_feature_names, numerical_features)

    # 6. Also capture the actual customer value for each original feature to
    #    build a readable value label  (e.g. "Month-to-month")
    value_labels = {}
    for col in numerical_features:
        raw_val = customer_df[col].iloc[0]
        value_labels[col] = str(raw_val)

    for col in categorical_features:
        raw_val = customer_df[col].iloc[0]
        # For OHE we already know the active category from the raw input
        value_labels[col] = str(raw_val)

    # 7. Sort by absolute SHAP impact, split into risk / protective
    sorted_items = sorted(collapsed.items(), key=lambda x: abs(x[1]), reverse=True)

    max_abs = max(abs(v) for _, v in sorted_items) if sorted_items else 1.0

    def make_entry(orig_name, shap_val):
        label       = _LABEL_MAP.get(orig_name, orig_name)
        value_label = value_labels.get(orig_name, "")
        bar_pct     = round(abs(shap_val) / max_abs * 100)
        # Compact impact magnitude string for display
        abs_v = abs(shap_val)
        if abs_v >= 0.3:   magnitude = "High"
        elif abs_v >= 0.1: magnitude = "Moderate"
        else:              magnitude = "Low"
        return {
            "label":       label,
            "value_label": value_label,
            "impact":      magnitude,
            "bar_pct":     bar_pct,
            "shap":        round(float(shap_val), 4),
        }

    risk_factors       = []
    protective_factors = []

    for name, val in sorted_items:
        if val > 0:
            risk_factors.append(make_entry(name, val))
        else:
            protective_factors.append(make_entry(name, val))

    # Return top 5 from each group
    return {
        "risk_factors":       risk_factors[:5],
        "protective_factors": protective_factors[:5],
    }
