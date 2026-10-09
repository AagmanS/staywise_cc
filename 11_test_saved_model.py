import pandas as pd
import joblib


# ==========================================
# 1. LOAD SAVED MODEL COMPONENTS
# ==========================================

preprocessor = joblib.load(
    "models/churn_preprocessor.pkl"
)

model = joblib.load(
    "models/churn_logistic_model.pkl"
)

threshold = joblib.load(
    "models/churn_threshold.pkl"
)


# ==========================================
# 2. CREATE SAMPLE CUSTOMER
# ==========================================

customer = {
    "Gender": "Female",
    "Senior Citizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "Tenure Months": 2,
    "Phone Service": "Yes",
    "Multiple Lines": "No",
    "Internet Service": "Fiber optic",
    "Online Security": "No",
    "Online Backup": "No",
    "Device Protection": "No",
    "Tech Support": "No",
    "Streaming TV": "No",
    "Streaming Movies": "No",
    "Contract": "Month-to-month",
    "Paperless Billing": "Yes",
    "Payment Method": "Electronic check",
    "Monthly Charges": 70.50,
    "Total Charges": 141.00
}

customer_df = pd.DataFrame([customer])


# ==========================================
# 3. FORCE SAME DATA TYPES AS TRAINING DATA
# ==========================================

categorical_features = [
    "Gender",
    "Senior Citizen",
    "Partner",
    "Dependents",
    "Phone Service",
    "Multiple Lines",
    "Internet Service",
    "Online Security",
    "Online Backup",
    "Device Protection",
    "Tech Support",
    "Streaming TV",
    "Streaming Movies",
    "Contract",
    "Paperless Billing",
    "Payment Method"
]

numerical_features = [
    "Tenure Months",
    "Monthly Charges",
    "Total Charges"
]


# Convert categorical values to strings
for col in categorical_features:
    customer_df[col] = customer_df[col].astype(str)


# Convert numerical values to numeric
for col in numerical_features:
    customer_df[col] = pd.to_numeric(
        customer_df[col],
        errors="coerce"
    )


# ==========================================
# 4. PREPROCESS CUSTOMER
# ==========================================

customer_processed = preprocessor.transform(
    customer_df
)


print("\nPreprocessing successful.")
print("Processed Customer Shape:", customer_processed.shape)


# ==========================================
# 5. PREDICT CHURN PROBABILITY
# ==========================================

churn_probability = model.predict_proba(
    customer_processed
)[0][1]


# ==========================================
# 6. APPLY THRESHOLD
# ==========================================

prediction = (
    churn_probability >= threshold
)


# ==========================================
# 7. DISPLAY RESULT
# ==========================================

print("\n==========================================")
print("        CHURNSENSE CUSTOMER PREDICTION")
print("==========================================")

print("\nCustomer Information:")
print("------------------------------------------")

for key, value in customer.items():
    print(f"{key}: {value}")

print("\n------------------------------------------")
print("MODEL RESULT")
print("------------------------------------------")

print(
    f"Churn Probability: {churn_probability * 100:.2f}%"
)

print(
    f"Threshold Used: {threshold}"
)

if prediction:
    print("Prediction: HIGH CHURN RISK")
else:
    print("Prediction: LOW CHURN RISK")

print("\n==========================================")
