# Team 4 — Preprocessing & Feature Engineering Plan (Week 1)

## 1. Dataset Overview
We are working with the **Credit Risk Dataset**. It contains approximately 32,000 rows and 12 features, including both numerical and categorical data. The target variable is `loan_status` (Binary Classification: Default vs. Non-Default).

## 2. Expected Data Issues
Based on our initial review of the dataset, we expect the following challenges:
* **Missing Values:** Commonly found in columns like `person_emp_length` (Employment length) and `loan_int_rate` (Interest rate).
* **Duplicates:** Potential exact row duplicates that need to be removed.
* **Outliers:** Extreme and illogical values, particularly in `person_age` (e.g., ages > 100) and `person_emp_length` (e.g., > 60 years).
* **Categorical Columns:** Columns like `person_home_ownership`, `loan_intent`, `loan_grade`, and `cb_person_default_on_file` need to be converted to numerical formats.
* **Imbalanced Scaling:** High variance between features (e.g., `person_income` in the thousands vs. `person_age` in the tens).

## 3. Proposed Cleaning & Preprocessing Steps
To prepare the data for the Machine Learning models (Team 5), we plan to apply the following steps:
1.  **Handling Missing Data:** Use **Median Imputation** for numerical columns like `loan_int_rate` and `person_emp_length` as it is robust to outliers.
2.  **Handling Duplicates:** Drop all exact full-row duplicates to prevent data leakage.
3.  **Handling Outliers:** Filter out illogical values (e.g., remove rows where age > 100 or employment length > 60). 
4.  **Encoding Categorical Data:**
    * *Binary Encoding:* Map `cb_person_default_on_file` (Y/N) to (1/0).
    * *Ordinal Encoding:* Convert `loan_grade` (A-G) to sequential numbers (0-6) to preserve risk order.
    * *One-Hot Encoding:* Apply to nominal features (`person_home_ownership`, `loan_intent`) using `drop_first=True`.
5.  **Feature Scaling:** Apply `StandardScaler` or `RobustScaler` to ensure all numerical features contribute equally to the model.

## 4. Feature Engineering Ideas
To extract deeper insights and help the model, we propose creating the following new features:
* **`loan_to_income_ratio`:** (loan_amnt / person_income) to measure the borrower's debt burden.
* **`age_to_emp_length_ratio`:** (person_emp_length / person_age) to understand employment stability relative to age.