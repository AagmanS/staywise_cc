import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ==========================================
# 1. LOAD DATASET
# ==========================================

file_path = "data/Telco_customer_churn.xlsx"

df = pd.read_excel(file_path)


# ==========================================
# 2. BASIC TARGET ANALYSIS
# ==========================================

print("\n========== CHURN COUNTS ==========")
print(df["Churn Label"].value_counts())

print("\n========== CHURN PERCENTAGES ==========")
print(
    df["Churn Label"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ==========================================
# 3. CHURN DISTRIBUTION
# ==========================================

plt.figure(figsize=(7, 5))

sns.countplot(
    data=df,
    x="Churn Label"
)

plt.title("Customer Churn Distribution")
plt.xlabel("Churn")
plt.ylabel("Number of Customers")

plt.tight_layout()
plt.show()


# ==========================================
# 4. CHURN VS CONTRACT
# ==========================================

plt.figure(figsize=(9, 5))

sns.countplot(
    data=df,
    x="Contract",
    hue="Churn Label"
)

plt.title("Churn Distribution by Contract Type")
plt.xlabel("Contract Type")
plt.ylabel("Number of Customers")

plt.tight_layout()
plt.show()


# ==========================================
# 5. CHURN VS TENURE
# ==========================================

plt.figure(figsize=(8, 5))

sns.boxplot(
    data=df,
    x="Churn Label",
    y="Tenure Months"
)

plt.title("Tenure Distribution by Churn Status")
plt.xlabel("Churn")
plt.ylabel("Tenure (Months)")

plt.tight_layout()
plt.show()


# ==========================================
# 6. CHURN VS MONTHLY CHARGES
# ==========================================

plt.figure(figsize=(8, 5))

sns.boxplot(
    data=df,
    x="Churn Label",
    y="Monthly Charges"
)

plt.title("Monthly Charges by Churn Status")
plt.xlabel("Churn")
plt.ylabel("Monthly Charges")

plt.tight_layout()
plt.show()


# ==========================================
# 7. CHURN RATE BY IMPORTANT CATEGORICAL FEATURES
# ==========================================

categorical_features = [
    "Contract",
    "Internet Service",
    "Online Security",
    "Tech Support",
    "Payment Method",
    "Paperless Billing"
]

for feature in categorical_features:

    churn_rate = (
        df.groupby(feature)["Churn Value"]
        .mean()
        .sort_values(ascending=False)
        * 100
    )

    print(f"\n========== CHURN RATE: {feature} ==========")
    print(churn_rate.round(2))


# ==========================================
# 8. CHURN VS SENIOR CITIZEN
# ==========================================

plt.figure(figsize=(7, 5))

sns.countplot(
    data=df,
    x="Senior Citizen",
    hue="Churn Label"
)

plt.title("Churn by Senior Citizen Status")
plt.xlabel("Senior Citizen")
plt.ylabel("Number of Customers")

plt.tight_layout()
plt.show()
