# StayWise — Customer Churn Prediction

> **AI-powered churn risk scoring for telecom businesses.**  
> Know who's leaving before they go.

---

## Overview

**StayWise** is an end-to-end machine learning project that predicts customer churn in the telecom industry. Built on the IBM Telco Customer Churn dataset (7,043 records), it uses a **Logistic Regression** model achieving a **94.2% ROC-AUC score** on a held-out test set.

The project includes a full data science pipeline from raw data inspection through model deployment, plus a premium frontend web application for interactive customer risk assessment.

---

## Live Demo

Open `frontend/index.html` in your browser, or run the local server:

```bash
npx serve frontend -p 3050
```

Then visit: **http://localhost:3050**

---

## Project Structure

```
staywise/
│
├── data/
│   ├── Telco_customer_churn.xlsx     # Raw IBM dataset (7,043 records)
│   └── telco_cleaned.csv             # Cleaned dataset after preprocessing
│
├── models/
│   ├── churn_logistic_model.pkl      # Trained logistic regression model
│   ├── churn_preprocessor.pkl        # Fitted ColumnTransformer
│   └── churn_threshold.pkl           # Optimised decision threshold (0.30)
│
├── frontend/
│   ├── index.html                    # Landing page
│   ├── styles.css                    # Global styles (Navy + Orange theme)
│   ├── main.js                       # Landing page interactions
│   ├── predict.html                  # Churn predictor tool
│   ├── predict.css                   # Predictor page styles
│   └── predict.js                    # Prediction logic + UI
│
├── 01_data_inspection.py             # Dataset shape, types, missing values
├── 02_eda.py                         # Exploratory data analysis
├── 03_data_cleaning.py               # Data cleaning & feature engineering
├── 04_train_test_split.py            # Stratified train/val/test split
├── 05_preprocessing.py               # OneHotEncoder + StandardScaler pipeline
├── 06_class_imbalance.py             # SMOTE / class weighting strategies
├── 07_model_comparison.py            # Logistic Regression, RF, XGBoost, DT
├── 08_logistic_threshold.py          # Threshold optimisation (F1/Recall)
├── 09_final_test_evaluation.py       # Final held-out test set evaluation
├── 10_save_model.py                  # Pickle model artifacts
├── 11_test_saved_model.py            # Sanity-check saved model
├── 12_interactive_prediction.py      # CLI-based interactive predictor
│
└── README.md
```

---

## Dataset

| Property | Value |
|----------|-------|
| Source | IBM Telco Customer Churn (Kaggle) |
| Records | 7,043 customers |
| Features | 19 input features + 1 target |
| Target | `Churn Label` (Yes / No) |
| Churn Rate | 26.5% (class imbalance handled) |

### Key Features Used

| Feature | Type | Description |
|---------|------|-------------|
| `Tenure Months` | Numerical | Months with the company |
| `Monthly Charges` | Numerical | Monthly billing amount |
| `Total Charges` | Numerical | Total amount charged |
| `Contract` | Categorical | Month-to-month / One year / Two year |
| `Internet Service` | Categorical | DSL / Fiber optic / No |
| `Payment Method` | Categorical | Electronic check / Bank transfer / etc. |
| `Tech Support` | Categorical | Yes / No / No internet service |
| `Online Security` | Categorical | Yes / No / No internet service |
| `Senior Citizen` | Binary | 0 or 1 |
| `Partner` | Binary | Yes / No |
| `Dependents` | Binary | Yes / No |
| *(+ 8 more service features)* | | |

---

## Machine Learning Pipeline

### Step-by-Step

```
Raw Data → Cleaning → EDA → Splitting → Preprocessing → Model Training → Threshold Tuning → Evaluation → Deployment
```

### 1. Data Cleaning (`03_data_cleaning.py`)
- Removed irrelevant ID columns
- Converted `Total Charges` from string to float
- Encoded binary target (`Churn Label`: Yes=1, No=0)

### 2. Train / Val / Test Split (`04_train_test_split.py`)
```
Train:  70% (4,930 records)
Val:    15% (1,057 records)
Test:   15% (1,057 records)
Stratified on Churn Label to preserve 26.5% churn rate
```

### 3. Preprocessing (`05_preprocessing.py`)
```python
ColumnTransformer([
    ('numerical', StandardScaler(), ['Tenure Months', 'Monthly Charges', 'Total Charges']),
    ('categorical', OneHotEncoder(handle_unknown='ignore'), [...16 categorical features...])
])
```
Fitted on training data only — no data leakage.

### 4. Class Imbalance (`06_class_imbalance.py`)
- Evaluated SMOTE oversampling
- Selected `class_weight='balanced'` in Logistic Regression (best F1 on validation)

### 5. Model Comparison (`07_model_comparison.py`)

| Model | Accuracy | Recall | Precision | F1 | ROC-AUC |
|-------|----------|--------|-----------|-----|---------|
| **Logistic Regression** | **80.6%** | **78%** | **67%** | **72%** | **94.2%** ★ |
| Random Forest | 79.4% | 71% | 66% | 68% | 91.8% |
| XGBoost | 78.2% | 68% | 65% | 66% | 90.1% |
| Decision Tree | 74.8% | 63% | 58% | 60% | 84.5% |

> **Logistic Regression selected** — highest ROC-AUC and best recall (most churners caught).

### 6. Threshold Optimisation (`08_logistic_threshold.py`)
Default threshold (50%) misses many churners. Optimised to **30%** to maximise recall:

```
Threshold: 30%
Recall:    78%   (catches 78 of every 100 churners)
Precision: 67%
F1 Score:  72%
```

---

## Model Performance

```
ROC-AUC Score:  94.2%
Recall:          78.0%   ← churners caught
Precision:       67.0%
F1 Score:        72.0%
Decision Threshold: 30%
Test Set Size:  1,057 records
```

---

## Frontend — StayWise Web App

### Pages

#### `index.html` — Landing Page
- No navigation bar — clean, immersive design
- Giant **STAYWISE** hero title (Barlow Condensed, 200px)
- Feature bullets, model stats, algorithm comparison
- Deep navy (`#1b3a5c`) + white + orange (`#e8732b`) colour scheme

#### `predict.html` — Churn Predictor
- Full 19-feature input form (matches ML model inputs exactly)
- Animated semicircle gauge showing churn probability
- Risk factor breakdown (what's driving the score)
- Personalised retention recommendations
- Sample profiles for quick testing

### Design System
| Token | Value |
|-------|-------|
| Background | `#1b3a5c` (navy) |
| Deep background | `#122944` |
| Accent | `#e8732b` (orange) |
| Text primary | `#ffffff` |
| Text secondary | `rgba(255,255,255,0.72)` |
| Display font | Barlow Condensed 900 |
| Body font | Barlow 400/500 |

---

## Running the Python Scripts

### Requirements

```bash
pip install pandas numpy scikit-learn xgboost imbalanced-learn joblib openpyxl
```

### Execution Order

```bash
python 01_data_inspection.py
python 02_eda.py
python 03_data_cleaning.py
python 04_train_test_split.py
python 05_preprocessing.py
python 06_class_imbalance.py
python 07_model_comparison.py
python 08_logistic_threshold.py
python 09_final_test_evaluation.py
python 10_save_model.py
python 11_test_saved_model.py

# Interactive CLI predictor:
python 12_interactive_prediction.py
```

### Interactive CLI Predictor

```bash
python 12_interactive_prediction.py
```

```
==========================================
        STAYWISE CUSTOMER INPUT
==========================================
Enter the customer details below.

Gender (Male/Female): Male
Senior Citizen (0/1): 0
Partner (Yes/No): No
...
Tenure Months: 3
Contract (Month-to-month/One year/Two year): Month-to-month
Payment Method: Electronic check
Monthly Charges: 95.70
Total Charges: 287.10

==========================================
       STAYWISE PREDICTION RESULT
==========================================

Churn Probability: 87.34%
Decision Threshold: 30%
------------------------------------------
Prediction: HIGH CHURN RISK
Recommended Action: RETENTION INTERVENTION
==========================================
```

---

## Key Insights from EDA

| Finding | Impact |
|---------|--------|
| Month-to-month contracts → 43% churn rate | Strongest predictor |
| Two-year contracts → 3% churn rate | Best retention |
| Fiber optic internet → 42% churn rate | High-risk segment |
| Electronic check payment → 45% churn | Payment friction |
| Tenure < 12 months → 50%+ churn rate | New customer risk |
| Tenure > 36 months → 8% churn rate | Loyalty indicator |

---

## Business Impact

If 1,869 high-risk customers each pay **$36.50/month average**:

```
Revenue at Risk (monthly): ~$68,200
If 60% retained via intervention: ~$40,920 saved per month
Annual retention value: ~$490,000+
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| ML Framework | Scikit-Learn |
| Boosting | XGBoost |
| Imbalance | Imbalanced-Learn (SMOTE) |
| Data | Pandas, NumPy |
| Serialisation | Joblib |
| Frontend | HTML5, Vanilla CSS, JavaScript |
| Fonts | Google Fonts — Barlow Condensed |

---

## Author

Built as a complete ML + frontend project demonstrating the full lifecycle of a churn prediction system — from raw data to an interactive web predictor.

---

*© 2026 StayWise · Trained on IBM Telco Customer Churn Dataset*
