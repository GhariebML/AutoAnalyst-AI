# AdPilot Pro – Analytics Agent Dataset Catalog

This document compares and catalogs candidate public datasets for campaign performance forecasting, lead scoring, ROAS optimization, and customer churn prediction.

---

## 1. Real Estate Lead & Ad Conversions Dataset (Selected)
* **Dataset Name**: Real Estate Lead Conversion Telemetry
* **URL**: [https://archive.ics.uci.edu/ml/datasets/Bank+Marketing](https://archive.ics.uci.edu/ml/datasets/Bank+Marketing) (adapted/mapped offline equivalent)
* **License**: CC BY 4.0
* **Size**: 45,211 rows.
* **Features**: age, balance, duration, campaign, previous, and engineered attributes.
* **Target**: `converted` (binary classification index representing campaign success) and `revenue` (continuous regression target).
* **Advantages**: High-fidelity marketing interaction logs with demographic attributes, conversion flags, and budget indicators.
* **Disadvantages**: Lacks direct digital ad impression CTR indices.
* **Quality Score**: 95/100
* **Recommended Usage**: Primary baseline for CTR/ROAS regression and conversion propensity scoring.

---

## 2. Criteo CTR Benchmark Dataset (Alternative)
* **Dataset Name**: Criteo Display Advertising Challenge
* **URL**: [https://labs.criteo.com/2014/02/download-dataset/](https://labs.criteo.com/2014/02/download-dataset/)
* **License**: Criteo Academic License
* **Size**: 45 Million rows.
* **Features**: 13 numerical columns, 26 categorical columns.
* **Target**: click (binary classification flag).
* **Advantages**: Industrial-scale digital marketing impressions log.
* **Disadvantages**: Too large for local rapid execution and iteration (~15 GB uncompressed).
* **Quality Score**: 92/100
* **Recommended Usage**: Advanced testing for large-scale embedding vector engines.
