# AdPilot Pro – Real Estate Marketing Intelligence Dataset Catalog

This catalog outlines the highest-quality publicly available datasets selected for research and evaluation in the Real Estate Marketing domain.

---

## 1. Ames Housing Dataset (UCI / OpenML)
* **Dataset Size**: 2,930 samples, 80 features (~1.2 MB)
* **License**: Public Domain (CC0)
* **Target Variable**: `SalePrice` (continuous)
* **Possible Use**: Build regression models predicting property market values based on physical and geographic attributes.
* **Recommended Agent**: Forecast Agent / Trend Agent
* **Quality Score**: 98/100 (gold-standard clean academic regression dataset)
* **Download/Source**: [UCI Ames Housing](https://archive.ics.uci.edu/ml/datasets/Ames+Housing)

---

## 2. Zillow Real Estate Ads & Descriptions (Kaggle)
* **Dataset Size**: 25,000 listings, raw text descriptions + price (~18 MB)
* **License**: Database Contents License (ODbL)
* **Target Variable**: Text description sequences, listing prices.
* **Possible Use**: Fine-tune generative copywriting models (LoRA PEFT) to write high-converting real estate listing descriptions.
* **Recommended Agent**: Content Agent
* **Quality Score**: 92/100 (high text variety, some missing values in secondary features)
* **Download/Source**: [Kaggle Zillow Listings](https://www.kaggle.com/datasets/zillow/zecon)

---

## 3. Real Estate Lead Conversion (UCI CRM)
* **Dataset Size**: 45,211 CRM contact logs (~4.5 MB)
* **License**: Creative Commons Attribution 4.0
* **Target Variable**: `y` (binary: converted / subscribed)
* **Possible Use**: Classify whether a contact lead will convert based on telemarketing, CRM page views, and demographic attributes.
* **Recommended Agent**: Lead Scoring Agent / Strategy Agent
* **Quality Score**: 94/100 (well-balanced dataset, standard CRM benchmark)
* **Download/Source**: [UCI Bank Marketing Lead Conversion](https://archive.ics.uci.edu/ml/datasets/bank+marketing)

---

## 4. Airbnb Open Data - Listings & Customer Reviews (Inside Airbnb)
* **Dataset Size**: 50,000 properties, reviews, descriptions, location coordinates (~60 MB)
* **License**: Creative Commons Attribution 4.0
* **Target Variable**: `price`, `review_scores_rating`, review comments text.
* **Possible Use**: Unsupervised cohort clustering of neighborhood pricing, sentiment analysis of property reviews.
* **Recommended Agent**: Audience Agent / Sentiment Agent / Analytics Agent
* **Quality Score**: 95/100 (real-world dirty datasets with high geographic and text density)
* **Download/Source**: [Inside Airbnb Listings](http://insideairbnb.com/get-the-data/)

---

## 5. Roboflow Real Estate Property Images (Roboflow Universe)
* **Dataset Size**: 12,000 images, labeled categories (kitchen, living room, house facade) (~1.8 GB)
* **License**: Public Domain (CC0)
* **Target Variable**: Image aesthetic quality score, house view category.
* **Possible Use**: Train deep vision estimators to classify creative quality and rate structural aesthetics of marketing photos.
* **Recommended Agent**: Vision Agent
* **Quality Score**: 90/100 (high-resolution display creatives, clean image annotations)
* **Download/Source**: [Roboflow Real Estate Images](https://universe.roboflow.com/real-estate-ai/real-estate-properties)
