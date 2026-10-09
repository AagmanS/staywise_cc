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
# 2. GET CUSTOMER INPUT
# ==========================================

print("\n==========================================")
print("        CHURNSENSE CUSTOMER INPUT")
print("==========================================")
print("Enter the customer details below.\n")


gender = input("Gender (Male/Female): ")

senior_citizen = int(
    input("Senior Citizen (0/1): ")
)

partner = input("Partner (Yes/No): ")

dependents = input("Dependents (Yes/No): ")

tenure_months = float(
    input("Tenure Months: ")
)

phone_service = input(
    "Phone Service (Yes/No): "
)

multiple_lines = input(
    "Multiple Lines (Yes/No/No phone service): "
)

internet_service = input(
    "Internet Service (DSL/Fiber optic/No): "
)

online_security = input(
    "Online Security (Yes/No/No internet service): "
)

online_backup = input(
    "Online Backup (Yes/No/No internet service): "
)

device_protection = input(
    "Device Protection (Yes/No/No internet service): "
)

tech_support = input(
    "Tech Support (Yes/No/No internet service): "
)

streaming_tv = input(
    "Streaming TV (Yes/No/No internet service): "
)

streaming_movies = input(
    "Streaming Movies (Yes/No/No internet service): "
)

contract = input(
    "Contract (Month-to-month/One year/Two year): "
)

paperless_billing = input(
    "Paperless Billing (Yes/No): "
)

payment_method = input(
    "Payment Method "
    "(Electronic check/Mailed check/"
    "Bank transfer (automatic)/"
    "Credit card (automatic)): "
)

monthly_charges = float(
    input("Monthly Charges: ")
)

total_charges = float(
    input("Total Charges: ")
)


# ==========================================
# 3. CREATE CUSTOMER DATAFRAME
# ==========================================

customer = {
    "Gender": gender,
    "Senior Citizen": senior_citizen,
    "Partner": partner,
    "Dependents": dependents,
    "Tenure Months": tenure_months,
    "Phone Service": phone_service,
    "Multiple Lines": multiple_lines,
    "Internet Service": internet_service,
    "Online Security": online_security,
    "Online Backup": online_backup,
    "Device Protection": device_protection,
    "Tech Support": tech_support,
    "Streaming TV": streaming_tv,
    "Streaming Movies": streaming_movies,
    "Contract": contract,
    "Paperless Billing": paperless_billing,
    "Payment Method": payment_method,
    "Monthly Charges": monthly_charges,
    "Total Charges": total_charges
}

customer_df = pd.DataFrame([customer])


# ==========================================
# 4. MAKE SURE DATA TYPES MATCH TRAINING
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


for col in categorical_features:
    customer_df[col] = customer_df[col].astype(str)


for col in numerical_features:
    customer_df[col] = pd.to_numeric(
        customer_df[col],
        errors="coerce"
    )


# ==========================================
# 5. PREPROCESS CUSTOMER
# ==========================================

customer_processed = preprocessor.transform(
    customer_df
)


# ==========================================
# 6. PREDICT CHURN PROBABILITY
# ==========================================

churn_probability = model.predict_proba(
    customer_processed
)[0][1]


# ==========================================
# 7. APPLY SELECTED THRESHOLD
# ==========================================

prediction = (
    churn_probability >= threshold
)


# ==========================================
# 8. DISPLAY RESULT
# ==========================================

print("\n\n==========================================")
print("       CHURNSENSE PREDICTION RESULT")
print("==========================================")

print(
    f"\nChurn Probability: "
    f"{churn_probability * 100:.2f}%"
)

print(
    f"Decision Threshold: "
    f"{threshold * 100:.0f}%"
)

print("------------------------------------------")

if prediction:
    print("Prediction: HIGH CHURN RISK")
    print("Recommended Action: RETENTION INTERVENTION")
else:
    print("Prediction: LOW CHURN RISK")
    print("Recommended Action: NORMAL CUSTOMER MANAGEMENT")

print("==========================================\n")
