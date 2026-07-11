# AdPilot Pro – Dataset Research & Selection (Phase 3)

This document contains the researched and proposed datasets for all 15 specialized machine learning models within the AdPilot Pro ecosystem.

---

## 1. Strategy Agent
* **Dataset Proposed**: *Kaggle Bank Marketing Dataset*
* **Download Link**: [Kaggle Bank Marketing](https://www.kaggle.com/datasets/janiobachmann/bank-marketing-dataset)
* **Justification**: Contains demographic features (job, education, marital status) and campaign touches (channel, duration) to predict user conversion response.
* **Labels**: `deposit` (binary outcome representing successful conversion).
* **Features**: `age`, `job`, `marital`, `education`, `default`, `balance`, `housing`, `loan`, `contact_channel`, `day`, `month`, `duration`, `campaign`, `pdays`, `previous`, `poutcome`.
* **Target**: `deposit` (0 or 1).
* **Expected Performance**: AUC-ROC ~0.88 - 0.92 using gradient boosted trees (LightGBM).
* **Limitations**: Highly domain-specific to financial services; needs feature engineering to generalize to multi-channel digital marketing.
* **Licensing**: Public Domain (CC0).
* **Data Size**: 11,162 rows, 17 columns (~1 MB).

---

## 2. Audience Agent
* **Dataset Proposed**: *Kaggle Customer Segmentation / Mall Customers*
* **Download Link**: [Mall Customer Segmentation](https://www.kaggle.com/datasets/vjchoudhary7/customer-segmentation-tutorial-in-python)
* **Justification**: Perfect for unsupervised clustering models to group demographic profiles into distinct target cohorts.
* **Labels**: None (unsupervised clustering).
* **Features**: `CustomerID`, `Gender`, `Age`, `Annual Income (k$)`, `Spending Score (1-100)`.
* **Target**: Clustering cohorts (e.g., Silhouette score validation).
* **Expected Performance**: Silhouette Score > 0.55 using HDBSCAN or K-Means.
* **Limitations**: Small size and synthetic attributes; will require scaling for larger demographic features.
* **Licensing**: Public Domain (CC0).
* **Data Size**: 200 rows (~4 KB).

---

## 3. Research Agent
* **Dataset Proposed**: *HuggingFace AG News Topic Classification*
* **Download Link**: [HuggingFace AG News](https://huggingface.co/datasets/ag_news)
* **Justification**: Text classification dataset mapping unstructured texts to categories, allowing the Research Agent to classify competitor website pages and trends.
* **Labels**: `Class Index` (1-World, 2-Sports, 3-Business, 4-Sci/Tech).
* **Features**: `text` (news title and content).
* **Target**: `label` (topic class).
* **Expected Performance**: Accuracy ~94% using BERT-style models or Sentence-Transformers + Logistic Regression.
* **Limitations**: Limited to four broad news categories; requires fine-tuning on digital marketing web pages.
* **Licensing**: Creative Commons Attribution-ShareAlike 4.0.
* **Data Size**: 120,000 training rows, 7,600 test rows (~30 MB).

---

## 4. Content Agent
* **Dataset Proposed**: *HuggingFace E-Commerce product descriptions / Ad Copy*
* **Download Link**: [HuggingFace E-Commerce Dataset](https://huggingface.co/datasets/Lumiere/ecommerce-product-descriptions)
* **Justification**: Maps key-value specifications and names of products directly to detailed marketing descriptions.
* **Labels**: Text sequences.
* **Features**: `product_name`, `brand`, `specifications`, `keywords`.
* **Target**: `description` (marketing ad copy).
* **Expected Performance**: BLEU > 28 / ROUGE-L > 45 after fine-tuning.
* **Limitations**: E-commerce focused; requires customization for social media ad copy and email newsletters.
* **Licensing**: MIT License.
* **Data Size**: 15,000 pairs (~10 MB).

---

## 5. Analytics Agent
* **Dataset Proposed**: *Kaggle Ad Click Prediction (Criteo)*
* **Download Link**: [Criteo Display Advertising Challenge](https://www.kaggle.com/c/criteo-display-ad-challenge)
* **Justification**: Large-scale click/no-click events to score predicted CTR based on user demographics and campaign attributes.
* **Labels**: `click` (binary conversion indicator).
* **Features**: 13 numerical features and 26 categorical features (hashed values representing advertiser IDs, page zones, and timestamps).
* **Target**: `click` (0 or 1).
* **Expected Performance**: Log Loss < 0.44 using deep CTR models or LightGBM.
* **Limitations**: Highly anonymized categorical features, making text interpretability direct mapping difficult.
* **Licensing**: For Research and Academic use only (Criteo).
* **Data Size**: 45 Million rows (~11 GB raw, subsetted for local training to ~100MB).

---

## 6. Budget Agent
* **Dataset Proposed**: *Kaggle Advertising Budget Dataset*
* **Download Link**: [Kaggle Advertising](https://www.kaggle.com/datasets/tawfikhaji/advertising-dataset)
* **Justification**: Simple dataset relating ad budget spends (TV, Radio, Newspaper) to product sales, ideal for evaluating optimization algorithms.
* **Labels**: Continuous sales target.
* **Features**: `TV`, `Radio`, `Newspaper`.
* **Target**: `Sales`.
* **Expected Performance**: R² Score > 0.89 using Linear/Nonlinear Regression.
* **Limitations**: Small dataset representing legacy offline channels; must be modeled conceptually for modern digital channels.
* **Licensing**: Public Domain (CC0).
* **Data Size**: 200 rows (~5 KB).

---

## 7. Trend Agent
* **Dataset Proposed**: *Kaggle Walmart Store Sales Forecasting*
* **Download Link**: [Kaggle Walmart Recruiting Store Sales](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting)
* **Justification**: Historical weekly sales tracking with promotion multipliers, holidays, and temperature data, ideal for trend and seasonal forecasting.
* **Labels**: Continuous sales values.
* **Features**: `Store`, `Dept`, `Date`, `IsHoliday`, `Temperature`, `Fuel_Price`, `MarkDown1-5`, `CPI`, `Unemployment`.
* **Target**: `Weekly_Sales`.
* **Expected Performance**: WMAE (Weighted Mean Absolute Error) < 1800 using Prophet or XGBoost.
* **Limitations**: Retail store sales trend; needs trend index normalization.
* **Licensing**: For competition use only (Walmart).
* **Data Size**: 421,570 rows (~15 MB).

---

## 8. Recommendation Agent
* **Dataset Proposed**: *Kaggle E-Commerce Item Recommendation*
* **Download Link**: [E-Commerce Purchases](https://www.kaggle.com/datasets/carrie1/ecommerce-data)
* **Justification**: Maps user transaction items and invoice dates, allowing the system to recommend optimal CTA shapes, ad dimensions, and layout configurations.
* **Labels**: Implicit interactions (purchase history).
* **Features**: `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`.
* **Target**: Recommended `StockCode` (ad items/features).
* **Expected Performance**: Mean Average Precision @ K (MAP@K) > 0.15 using matrix factorization.
* **Limitations**: E-commerce transactions; requires mapping transaction items to visual styling properties.
* **Licensing**: Public Domain (CC0).
* **Data Size**: 541,909 rows (~45 MB).

---

## 9. Forecast Agent
* **Dataset Proposed**: *Kaggle Store Item Demand Forecasting*
* **Download Link**: [Store Item Demand Forecasting](https://www.kaggle.com/c/demand-forecasting-kernels-only)
* **Justification**: Maps 5 years of daily store item sales, perfect for training forecast models on future ad impressions and conversion metrics over time.
* **Labels**: Continuous daily volume.
* **Features**: `date`, `store`, `item`.
* **Target**: `sales` (predictive daily impressions/conversions).
* **Expected Performance**: SMAPE < 13.5% using Prophet or LightGBM.
* **Limitations**: Highly stable demand curves; might not fully capture sudden digital ad volatility.
* **Licensing**: Public Domain (CC0).
* **Data Size**: 913,000 rows (~12 MB).

---

## 10. Fraud Agent
* **Dataset Proposed**: *Kaggle Credit Card Fraud Detection*
* **Download Link**: [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
* **Justification**: Extremely imbalanced dataset of transactions, allowing training of unsupervised anomaly detectors to flag click-fraud and lead-fraud.
* **Labels**: `Class` (0 = Normal, 1 = Fraud).
* **Features**: `Time`, `V1-V28` (PCA transformed numerical features), `Amount`.
* **Target**: `Class`.
* **Expected Performance**: Precision > 0.80 / Recall > 0.78 on the fraud minority class.
* **Limitations**: Anonymized features; will require custom mapping to web traffic telemetry.
* **Licensing**: Database Contents License (ODbL).
* **Data Size**: 284,807 rows (~150 MB).

---

## 11. Lead Scoring Agent
* **Dataset Proposed**: *Kaggle Lead Scoring Dataset*
* **Download Link**: [Kaggle Lead Scoring](https://www.kaggle.com/datasets/ashydv/leads-dataset)
* **Justification**: CRM sales data containing lead details, time spent on site, source, and total website page views.
* **Labels**: `Converted` (binary conversion result).
* **Features**: `Lead Source`, `TotalVisits`, `Total Time Spent on Website`, `Page Views Per Visit`, `Last Activity`, `Specialization`.
* **Target**: `Converted` (0 or 1).
* **Expected Performance**: F1-score > 0.85 using XGBoost.
* **Limitations**: Contains some missing values and string features that require categorical preprocessing.
* **Licensing**: Public Domain (CC0).
* **Data Size**: 9,240 rows (~1.2 MB).

---

## 12. Sentiment Agent
* **Dataset Proposed**: *HuggingFace Twitter Sentiment Analysis (Sentiment140)*
* **Download Link**: [HuggingFace Sentiment140](https://huggingface.co/datasets/sentiment140)
* **Justification**: Maps user social comments directly to positive, negative, or neutral sentiment scores, ideal for validating audience feedback.
* **Labels**: `polarity` (0 = negative, 4 = positive).
* **Features**: `text`, `date`, `user`, `query`.
* **Target**: `polarity`.
* **Expected Performance**: Accuracy > 84% using DistilRoBERTa.
* **Limitations**: Highly informal language/slang; requires custom cleaning and vocabulary alignment.
* **Licensing**: Public Domain (CC0).
* **Data Size**: 1.6 Million rows (~300 MB).

---

## 13. Vision Agent
* **Dataset Proposed**: *Kaggle Image Popularity / Aesthetic Evaluator (AVA)*
* **Download Link**: [AVA Aesthetic Visual Analysis](https://www.kaggle.com/datasets/nandodefreitas/ava-dataset)
* **Justification**: Massive collection of images evaluated by professional photographers, rating their visual aesthetic appeal on a 1-10 scale.
* **Labels**: Array of rating scores from 1 to 10.
* **Features**: `image_id`, `tag_indices`, semantic tags.
* **Target**: Average aesthetic rating (1.0 to 10.0).
* **Expected Performance**: Pearson Correlation > 0.65 using Deep CNNs or CLIP features.
* **Limitations**: File download is extremely large; subsetting or pretrained feature extraction (e.g. CLIP embeddings) is required for local serving.
* **Licensing**: For academic and research use only.
* **Data Size**: 250,000 image references (~30 GB image zip, metadata ~50 MB).

---

## 14. Knowledge Agent
* **Dataset Proposed**: *HuggingFace MS MARCO passage retrieval*
* **Download Link**: [HuggingFace MS MARCO](https://huggingface.co/datasets/ms_marco)
* **Justification**: The standard dataset for information retrieval, mapping user search queries to relevant document paragraphs.
* **Labels**: Relevant (0 or 1).
* **Features**: `query`, `passages` (passage text, URL).
* **Target**: `is_selected` (ranking relevance).
* **Expected Performance**: Mean Reciprocal Rank (MRR@10) > 0.35 using dense retrievers.
* **Limitations**: Passages are extracted from search engines; requires indexing localized brand PDFs for RAG.
* **Licensing**: Creative Commons Attribution 4.0.
* **Data Size**: 8.2 Million passages (~2.1 GB).

---

## 15. Optimizer Agent
* **Dataset Proposed**: *Kaggle Real-Time Bidding (RTB) Dataset*
* **Download Link**: [iPinYou RTB Dataset](https://www.kaggle.com/datasets/saurabhbagchi/ipinyou-rtb-dataset)
* **Justification**: Historical RTB auction telemetry containing bid prices, win status, and conversions, ideal for testing reinforcement learning bidding strategies.
* **Labels**: Click status (Reward).
* **Features**: `bidprice`, `payprice`, `click`, `hour`, `weekday`, `useragent`, `adzone`, `slotprice`.
* **Target**: Click reward (0 or 1).
* **Expected Performance**: ECTR (expected CTR) evaluation within 12% of actual reward.
* **Limitations**: Historic logging data suffers from off-policy evaluation challenges in Reinforcement Learning.
* **Licensing**: For Research use only (iPinYou).
* **Data Size**: ~2.5 GB (splittable into small local episodes).
