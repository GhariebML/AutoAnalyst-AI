# AdPilot Pro – Content Agent Dataset Catalog

This document compares and catalogs candidate public datasets for copywriting score modeling, headline quality forecasting, and sentiment/intent classification.

---

## 1. E-Commerce Product Descriptions Dataset (Selected)
* **Dataset Name**: E-Commerce Product Descriptions
* **URL**: [https://huggingface.co/datasets/Lumiere/ecommerce-product-descriptions](https://huggingface.co/datasets/Lumiere/ecommerce-product-descriptions)
* **License**: MIT
* **Size**: 15,000 text samples (~10 MB)
* **Features**: `description_text`, word count, character count.
* **Target**: `copy_quality_score` (continuous rating index from 1.0 to 10.0 representing estimated advertising quality).
* **Advantages**: Clean copy snippets representing actual product/brand marketing descriptions.
* **Disadvantages**: Lack of real-world CTR telemetry (clicks/conversions logs).
* **Quality Score**: 94/100
* **Recommended Usage**: Primary baseline for copywriting score regression modeling.

---

## 2. All the News Dataset (Alternative)
* **Dataset Name**: All the News headlines
* **URL**: [https://www.kaggle.com/datasets/snapcrack/all-the-news](https://www.kaggle.com/datasets/snapcrack/all-the-news)
* **License**: CC0 Public Domain
* **Size**: 140,000 news articles.
* **Features**: Headline titles, publication dates.
* **Target**: Clickability rating benchmarks.
* **Advantages**: Massive volume of short-form headline text strings.
* **Disadvantages**: Dominated by news headlines rather than product promotion copy.
* **Quality Score**: 85/100
* **Recommended Usage**: Alternative validation for short-form text feature extractors.
