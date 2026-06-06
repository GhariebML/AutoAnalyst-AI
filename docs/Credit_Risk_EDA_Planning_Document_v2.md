# Credit Risk EDA Planning Document

> Confidential — Internal Use Only

**Version 1.0**  |  **Data Science Division**  |  **Prepared for Internal Use**

## 1. Project Overview & Objectives

- **Dataset Goal:** Analyze credit risk data to understand the factors driving loan defaults (`loan_status`).
- **Primary Objective:** Clean the dataset, explore variable distributions, uncover latent patterns, and identify relationships between borrower characteristics and loan outcomes to inform future predictive modeling.

## 2. Data Understanding & Dictionary

Each row in the dataset represents an individual record for a distinct borrower. Each column encodes a specific borrower attribute or loan characteristic.

### Borrower Personal & Financial Data

| Variable | Description |
| --- | --- |
| `person_age` | Age of the loan applicant, expressed in years. |
| `person_income` | Annual gross income of the applicant. |
| `person_home_ownership` | Housing status of the applicant (`RENT`, `OWN`, `MORTGAGE`, or `OTHER`). |
| `person_emp_length` | Total years of employment history reported by the applicant. Note: the value `123` in the first row is almost certainly a data-entry error and must be treated as an outlier. |

### Loan Request Data

| Variable | Description |
| --- | --- |
| `loan_intent` | Stated purpose of the loan (e.g., `PERSONAL`, `EDUCATION`, `MEDICAL`, `VENTURE`, `HOMEIMPROVEMENT`, `DEBTCONSOLIDATION`). |
| `loan_grade` | Credit-risk classification assigned to the loan, represented by letter grades (`A–E`). Grade A denotes the lowest risk level; risk increases toward E. |
| `loan_amnt` | Total loan amount requested by the applicant. |
| `loan_int_rate` | Annual interest rate applied to the loan. |
| `loan_status` | Target variable — current repayment status: `0 = fully paid or compliant`, `1 = defaulted`. |
| `loan_percent_income` | Loan amount expressed as a proportion of the borrower's annual income (e.g., `0.59` means the loan equals 59% of annual income). |

### Credit History Data

| Variable | Description |
| --- | --- |
| `cb_person_default_on_file` | Indicates whether the borrower has a historical record of default or financial delinquency (`Y = Yes`, `N = No`). |
| `cb_person_cred_hist_length` | Duration of the borrower's credit history in years, measured from their first interaction with a lender or credit facility. |

## 3. Key EDA Questions & Hypotheses

The following questions frame the analytical scope of the EDA phase and drive visualization and feature-selection decisions.

1. **What is the baseline default rate in the dataset?**
   - Target-class imbalance check.
2. **Does a lower annual income (`person_income`) significantly increase the likelihood of default?**
3. **How does the interest rate (`loan_int_rate`) affect a borrower's ability to repay?**
4. **Are specific loan intents (e.g., `Medical` vs. `Venture`) more strongly associated with defaults?**
5. **Is there a strong correlation between a borrower's historical default record (`cb_person_default_on_file`) and current loan status?**

## 4. Data Cleaning & Preprocessing Plan

Initial data inspection revealed anomalies that must be addressed prior to in-depth visualization. The three focus areas below define the preprocessing actions required.

> Critical Notice — Resolve all items below before proceeding to the visualization phase.

- **Outliers:** `person_emp_length` contains physically impossible values (e.g., `123` years). Inspect the full distribution and apply capping or removal as appropriate.
- **Outliers:** Examine `person_age` for unrealistic values (e.g., ages below 18 or above 100).
- **Missing Values:** Scan `loan_int_rate` and `person_emp_length` for null or missing values. Define an imputation strategy (`mean` or `median`) based on each variable's distribution and skewness.

## 5. Visualization Strategy

The table below serves as the chart blueprint for the EDA phase. Each row maps an analysis type to the appropriate visualization and articulates its analytical objective.

| Analysis Type | Chart Type | Description & Goal |
| --- | --- | --- |
| Target Distribution | Bar / Pie Chart | Visualize the ratio of Default (`1`) vs. Non-Default (`0`) cases to assess class imbalance. |
| Univariate — Numerical | Histograms | Plot `person_income`, `loan_amnt`, and `person_age` to assess distribution shape and skewness. |
| Univariate — Categorical | Bar Charts | Display loan counts segmented by `loan_intent`, `loan_grade`, and `person_home_ownership`. |
| Multivariate Relationships | Correlation Heatmap | Construct a correlation matrix of all numerical features to identify multicollinearity (e.g., Age vs. Credit History Length). |
| Feature vs. Target (Numerical) | Box Plots | Compare distributions of `loan_int_rate` and `person_income` across `loan_status` groups. |
| Feature vs. Target (Categorical) | Stacked Bar Charts | Show the default rate within each `loan_grade` and `person_home_ownership` category. |
