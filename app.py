"""
app.py — StayWise Flask API
============================
Serves two endpoints:

  POST /predict
      Accepts raw customer fields (JSON).
      Returns churn probability, risk level, SHAP risk/protective factors,
      and rule-based recommendations.
      Does NOT change threshold, model, or preprocessor.

  GET  /health
      Quick liveness check.

Start with:
    python app.py
"""

import os
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

from explain import explain_prediction

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)   # allow the frontend (served on :8000) to call the API on :5000

# ── Load model artifacts once at startup ─────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

preprocessor = joblib.load(os.path.join(BASE, "models", "churn_preprocessor.pkl"))
model        = joblib.load(os.path.join(BASE, "models", "churn_logistic_model.pkl"))
threshold    = joblib.load(os.path.join(BASE, "models", "churn_threshold.pkl"))
feature_info = joblib.load(os.path.join(BASE, "models", "churn_feature_info.pkl"))

# Build a representative background dataset from the training data
# for the SHAP LinearExplainer (used as mean baseline).
# We pre-transform the full cleaned CSV once at startup so every
# prediction request is fast.
_cleaned_csv = os.path.join(BASE, "data", "telco_cleaned.csv")
_df_bg       = pd.read_csv(_cleaned_csv)

_numerical_features   = feature_info["numerical_features"]
_categorical_features = feature_info["categorical_features"]

# Coerce types exactly as in training
for col in _categorical_features:
    _df_bg[col] = _df_bg[col].astype(str)
for col in _numerical_features:
    _df_bg[col] = pd.to_numeric(_df_bg[col], errors="coerce")

X_bg_raw         = _df_bg[_numerical_features + _categorical_features]
X_train_transformed = preprocessor.transform(X_bg_raw)   # (n_samples, 46)

# Pre-build the SHAP explainer once at startup — massive speedup
from explain import _build_explainer
_explainer = _build_explainer(model, preprocessor, X_train_transformed)

print(f"[StayWise] Models loaded | threshold={threshold} | "
      f"background rows={X_train_transformed.shape[0]} | explainer ready")

# ── Feature name → form field name mapping ────────────────────────────────────
# The form posts camelCase/snake_case names; we map them to the exact column
# names the preprocessor was trained on.
FIELD_TO_COLUMN = {
    "gender":            "Gender",
    "senior_citizen":    "Senior Citizen",
    "partner":           "Partner",
    "dependents":        "Dependents",
    "tenure_months":     "Tenure Months",
    "phone_service":     "Phone Service",
    "multiple_lines":    "Multiple Lines",
    "internet_service":  "Internet Service",
    "online_security":   "Online Security",
    "online_backup":     "Online Backup",
    "device_protection": "Device Protection",
    "tech_support":      "Tech Support",
    "streaming_tv":      "Streaming TV",
    "streaming_movies":  "Streaming Movies",
    "contract":          "Contract",
    "paperless_billing": "Paperless Billing",
    "payment_method":    "Payment Method",
    "monthly_charges":   "Monthly Charges",
    "total_charges":     "Total Charges",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_customer(payload: dict) -> pd.DataFrame:
    """
    Convert the JSON payload into a single-row DataFrame with the exact
    column names and dtypes the preprocessor expects.
    Raises ValueError with a descriptive message if required fields are missing.
    """
    row = {}
    missing = []

    for field, column in FIELD_TO_COLUMN.items():
        val = payload.get(field)
        if val is None or str(val).strip() == "":
            missing.append(field)
            continue
        row[column] = val

    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    df = pd.DataFrame([row])

    # Coerce dtypes
    for col in _categorical_features:
        if col in df.columns:
            df[col] = df[col].astype(str)
    for col in _numerical_features:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _risk_level(prob: float) -> str:
    if prob >= 0.60:   return "HIGH"
    if prob >= threshold: return "MEDIUM"
    return "LOW"


def _recommendations(prob: float) -> list:
    """Rule-based retention recommendations, unchanged from existing logic."""
    if prob >= 0.60:
        return [
            "Offer 10–20% loyalty discount on annual contract upgrade immediately.",
            "Schedule a proactive retention call within 48 hours.",
            "Bundle free tech support or online security for 3 months.",
            "Incentivize switch to auto-payment with a one-month bill credit.",
        ]
    if prob >= threshold:
        return [
            "Send a personalised email highlighting service value and benefits.",
            "Offer a complimentary 30-day service upgrade trial.",
            "Flag for quarterly review by the customer success team.",
        ]
    return [
        "Customer is stable — continue standard engagement cadence.",
        "Strong candidate for upsell or referral programme enrolment.",
        "Monitor monthly charges growth to detect future risk early.",
    ]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "threshold": threshold})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Request body (JSON):
        { "gender": "Male", "senior_citizen": "0", "tenure_months": "3", ... }

    Response (JSON):
        {
          "probability":   0.873,
          "probability_pct": "87.3",
          "risk_level":    "HIGH",
          "churn":         true,
          "threshold":     0.20,
          "risk_factors":       [ {label, value_label, impact, bar_pct}, ... ],
          "protective_factors": [ {label, value_label, impact, bar_pct}, ... ],
          "recommendations":    [ "...", ... ]
        }
    """
    try:
        payload = request.get_json(force=True, silent=True) or {}

        # 1. Parse + validate
        customer_df = _parse_customer(payload)

        # 2. Predict probability (real model — no simulation)
        X_transformed = preprocessor.transform(customer_df)
        prob          = float(model.predict_proba(X_transformed)[0][1])

        # 3. SHAP explanation (uses cached explainer — no rebuild per request)
        explanation = explain_prediction(
            model               = model,
            preprocessor        = preprocessor,
            feature_info        = feature_info,
            customer_df         = customer_df,
            X_train_transformed = X_train_transformed,
            explainer           = _explainer,
        )

        # 4. Build response
        response = {
            "probability":        round(prob, 4),
            "probability_pct":    f"{prob * 100:.1f}",
            "risk_level":         _risk_level(prob),
            "churn":              prob >= threshold,
            "threshold":          threshold,
            "risk_factors":       explanation["risk_factors"],
            "protective_factors": explanation["protective_factors"],
            "recommendations":    _recommendations(prob),
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Log full traceback server-side but return a clean message
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Prediction failed. Check server logs."}), 500


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
