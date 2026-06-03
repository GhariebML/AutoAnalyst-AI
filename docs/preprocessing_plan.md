# Preprocessing Plan - Credit Risk Dataset

## Team 4: Preprocessing & Feature Engineering

### Objective
Prepare the dataset for machine learning by cleaning data, handling missing values, encoding categorical features, scaling numerical features, and creating useful engineered features.

---

# Dataset Overview

Target Variable:

- loan_status
    - 0 = Non-default
    - 1 = Default

Dataset Size:

- Rows: 32,581
- Columns: 12

---

# Column Classification

## Numerical Columns

- person_age
- person_income
- person_emp_length
- loan_amnt
- loan_int_rate
- loan_percent_income
- cb_person_cred_hist_length

## Categorical Columns

- person_home_ownership
- loan_intent
- loan_grade
- cb_person_default_on_file

## Target Column

- loan_status

## Date/Time Columns

No date/time columns detected.

---

# Expected Data Quality Issues

## Missing Values

- loan_int_rate: 3116 missing values
- person_emp_length: 895 missing values

Expected handling:
- Fill numerical missing values using Median.

## Duplicate Records

- 165 duplicate rows detected

Expected handling:
- Remove duplicate rows before training.

## Outliers

Potential outliers may exist in:
- person_income
- loan_amnt
- person_age
- person_emp_length

---

# Encoding Strategy

## One-Hot Encoding

- person_home_ownership
- loan_intent

## Ordinal Encoding

- loan_grade

Order:
A < B < C < D < E < F < G

## Binary Encoding

- cb_person_default_on_file

Mapping:
- Y -> 1
- N -> 0

---

# Scaling Strategy

Recommended scaler:
- StandardScaler

Columns:
- person_age
- person_income
- person_emp_length
- loan_amnt
- loan_int_rate
- loan_percent_income
- cb_person_cred_hist_length

---

# Train-Test Split

Recommended:
- 80% Train
- 20% Test

---

# Feature Engineering Ideas

1. Income-to-Loan Ratio
2. Employment Stability Score
3. Credit History to Age Ratio
4. Interest Burden Feature
5. High Risk Flag

---

# Proposed Preprocessing Pipeline

1. Load dataset.
2. Remove duplicate rows.
3. Handle missing values.
4. Detect and treat outliers.
5. Encode categorical variables.
6. Split data into train/test.
7. Scale numerical features.
8. Apply feature engineering.
9. Save processed dataset.
