# AdPilot Pro – Strategy Agent Dataset Catalog

This document compares and catalogs the candidate public datasets for the Strategy Agent research workspace.

---

## 1. UCI Bank Marketing Dataset (Selected)
* **Dataset Name**: Bank Marketing Dataset
* **URL**: [https://archive.ics.uci.edu/ml/datasets/bank+marketing](https://archive.ics.uci.edu/ml/datasets/bank+marketing)
* **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Size**: 11,162 samples, 17 features (~1.2 MB)
* **Features**: `age`, `job`, `marital`, `education`, `default`, `balance`, `housing`, `loan`, `contact`, `day`, `month`, `duration`, `campaign`, `pdays`, `previous`, `poutcome`
* **Target**: `deposit` (binary: yes/no conversion)
* **Advantages**:
  * Represents real campaign contact events with balanced conversion targets.
  * Contains a mix of numerical, categorical, and behavioral features.
* **Disadvantages**:
  * Focused on banking telemarketing campaigns rather than digital display ad attribution.
* **Quality Score**: 96/100
* **Recommended Usage**: Primary benchmark for marketing strategy conversion classification.

---

## 2. Marketing Campaign Response Dataset (Alternative)
* **Dataset Name**: Marketing Campaign Response
* **URL**: [https://www.kaggle.com/datasets/rodsaldanha/arketing-campaign](https://www.kaggle.com/datasets/rodsaldanha/arketing-campaign)
* **License**: CC0 Public Domain
* **Size**: 2,240 samples, 29 features (~300 KB)
* **Features**: `Year_Birth`, `Education`, `Marital_Status`, `Income`, `Kidhome`, `Teenhome`, `Dt_Customer`, `Recency`, `MntWines`, `MntFruits`, `Response`
* **Target**: `Response` (binary: accepted campaign offer)
* **Advantages**:
  * High density of demographic attributes and product spending features.
* **Disadvantages**:
  * Small sample count limits training deep architectures like TabNet or MLPs.
* **Quality Score**: 90/100
* **Recommended Usage**: Alternative validation check for customer purchasing behaviors.
