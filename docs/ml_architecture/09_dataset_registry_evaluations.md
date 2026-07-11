# AdPilot Pro – ML Dataset Selection & Integration Registry

This document lists the dataset evaluations, comparative rankings, preprocessing steps, and training/validation/test strategies for all 15 specialized ML models within AdPilot Pro.

---

## 1. Strategy Agent
* **Task Type**: Multi-Label Classification
* **Model Purpose**: Predict optimal advertising channels and tactics based on campaign metadata.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Bank Marketing (Kaggle/UCI)** | High | High | 11k | High | CC0 | High | **95 (Winner)** |
| 2. Marketing Campaign Response | Med | High | 2.2k | High | CC0 | Med | 88 |
| 3. IBM Marketing Analytics | Med | Med | 9k | High | Proprietary | Med | 78 |
| 4. Direct Marketing (OpenML) | Med | Med | 45k | Med | CC0 | Low | 72 |
| 5. KDD Cup 1998 (UCI) | High | Low | 95k | Low | Open Use | Low | 60 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Bank Marketing Dataset
* **Source**: UCI Machine Learning Repository
* **URL**: [https://archive.ics.uci.edu/ml/datasets/bank+marketing](https://archive.ics.uci.edu/ml/datasets/bank+marketing)
* **Size**: 11,162 samples (~1.2 MB)
* **Downsampling for Local Development**: Not required (already lightweight enough for fast execution).
* **Input Schema**: `age`, `job`, `marital`, `education`, `balance`, `housing`, `loan`, `contact`, `duration`.
* **Output Labels**: `deposit` (0 or 1).
* **Data Preparation**: One-hot encode string features (`job`, `marital`, `education`, `contact`). RobustScale numerical features (`balance`, `duration`) to handle outliers. Split dataset: 80% train, 20% test (stratified on conversion label).
* **Training & Validation Strategy**: Stratified 5-Fold Cross-Validation. Loss: Log Loss (Binary Cross-Entropy). Evaluation: F1-Macro, ROC-AUC.

---

## 2. Audience Agent
* **Task Type**: Clustering / Customer Segmentation
* **Model Purpose**: Group customer attributes into organic cohort target segments.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Mall Customers (Kaggle)** | High | High | 200 | High | CC0 | High | **96 (Winner)** |
| 2. CC General (Kaggle/OpenML) | High | Med | 8.9k | Med | CC0 | High | 87 |
| 3. Wholesale Customers (UCI) | Med | High | 440 | High | Open Use | Med | 80 |
| 4. Customer Personality Analysis | Med | Med | 2.2k | Med | CC0 | Med | 76 |
| 5. Online Retail II (UCI) | High | Low | 541k | Low | Open Use | High | 68 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Mall Customer Segmentation
* **Source**: Kaggle Datasets
* **URL**: [https://www.kaggle.com/datasets/vjchoudhary7/customer-segmentation-tutorial-in-python](https://www.kaggle.com/datasets/vjchoudhary7/customer-segmentation-tutorial-in-python)
* **Size**: 200 rows (~4 KB)
* **Input Schema**: `Age`, `Annual Income (k$)`, `Spending Score (1-100)`, `Gender`.
* **Output Labels**: None (Unsupervised cohort clustering).
* **Data Preparation**: Scale numerical columns with `StandardScaler`. Encode `Gender` with LabelEncoder. Deduplicate rows.
* **Training & Validation Strategy**: Fit HDBSCAN or K-Means. Validate clusters using Silhouette Coefficient, Calinski-Harabasz Index, and Davies-Bouldin Index.

---

## 3. Research Agent
* **Task Type**: NLP / Topic Classification
* **Model Purpose**: Categorize competitor headlines and web pages into marketing domains.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. AG News (Hugging Face)** | High | High | 127k | High | CC0 | High | **97 (Winner)** |
| 2. DBpedia Classes (HF) | High | High | 630k | Med | CC-BY-SA | High | 90 |
| 3. Yahoo Answers (HF) | Med | Med | 1.4M | Low | CC0 | Med | 78 |
| 4. 20 Newsgroups (UCI) | Med | Med | 18k | High | Open Use | High | 74 |
| 5. Reuters-21578 (UCI) | Low | Low | 21k | Low | Open Use | Med | 55 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: AG News Dataset
* **Source**: Hugging Face Datasets
* **URL**: [https://huggingface.co/datasets/ag_news](https://huggingface.co/datasets/ag_news)
* **Size**: 120k train, 7.6k test (~30 MB)
* **Downsampling for Local Development**: Subset training set to 10k random samples to ensure fast local execution.
* **Input Schema**: Raw string text.
* **Output Labels**: `Class Index` (1-World, 2-Sports, 3-Business, 4-Sci/Tech).
* **Data Preparation**: Lowercase, strip HTML tags, extract Sentence-BERT embedding vectors (384 dimensions).
* **Training & Validation Strategy**: 80/20 train/test split. Cross-entropy loss function. Metric: Accuracy, F1-Score.

---

## 4. Content Agent
* **Task Type**: Generative AI / Text Translation
* **Model Purpose**: Convert campaign attributes into high-converting copywriting descriptions.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. E-Commerce product descriptions (HF)** | High | High | 15k | High | MIT | High | **94 (Winner)** |
| 2. WebRef Ad Copy (HF) | High | Med | 8k | High | Open Use | Med | 86 |
| 3. Multi-News Summarization | Med | High | 56k | Med | Apache-2.0 | High | 78 |
| 4. Wikihow Text Generation | Med | Med | 1.5M | Low | GPL-3.0 | Med | 70 |
| 5. Common Crawl Marketing Webpages | High | Low | 100GB | Low | Open Use | High | 50 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: E-Commerce product descriptions
* **Source**: Hugging Face Datasets
* **URL**: [https://huggingface.co/datasets/Lumiere/ecommerce-product-descriptions](https://huggingface.co/datasets/Lumiere/ecommerce-product-descriptions)
* **Size**: 15,000 text pairs (~10 MB)
* **Input Schema**: `product_name`, `brand`, `specifications`, `keywords`.
* **Output Labels**: `description` (creative ad copywriting).
* **Data Preparation**: Standardize JSON strings, strip whitespace, format prompt with special tokens (e.g. `<s>[INST]`).
* **Training & Validation Strategy**: Fine-tune via QLoRA (PEFT) using causal language modeling loss. Validate with BLEU, ROUGE-L.

---

## 5. Analytics Agent
* **Task Type**: Click-Through Rate (CTR) Regression Scoring
* **Model Purpose**: Score creative drafts against predicted conversion/click outcomes.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Criteo Display Advertising (Criteo)** | High | High | 45M | Med | Research Only | High | **92 (Winner)** |
| 2. Avazu Click Prediction | High | Med | 40M | Med | CC0 | High | 86 |
| 3. Tencent App Click Log | Med | Med | 10M | Low | Research Only | Med | 74 |
| 4. Yahoo! Ad Click Telemetry | Med | Low | 100M | Low | Request Required | Low | 60 |
| 5. Outbrain Click Prediction | Low | Med | 80M | Low | Research Only | Med | 55 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Criteo Display Advertising Challenge
* **Source**: Criteo Academic Research / Kaggle
* **URL**: [https://www.kaggle.com/c/criteo-display-ad-challenge](https://www.kaggle.com/c/criteo-display-ad-challenge)
* **Size**: 45M rows (~11 GB)
* **Downsampling for Local Development**: Subset to 50k rows for rapid local validation.
* **Input Schema**: 13 numerical columns, 26 categorical hashed columns.
* **Output Labels**: `click` (0 or 1).
* **Data Preparation**: Impute numerical missing values with median, log-transform skewed distributions. Hash categorical values.
* **Training & Validation Strategy**: Chronological split (80% train, 20% test). Loss: Log Loss. Metrics: ROC-AUC, Log Loss.

---

## 6. Budget Agent
* **Task Type**: Constrained Optimization (Regression Attribution)
* **Model Purpose**: Allocate campaign budgets across channels to maximize expected sales volume.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. ISLR Advertising Dataset (Springer)** | High | High | 200 | High | Open Use | High | **96 (Winner)** |
| 2. Media Spends Attribution | Med | High | 1k | High | CC0 | Med | 88 |
| 3. Retail Marketing Spends | Med | Med | 5k | Med | CC0 | Med | 76 |
| 4. Direct Marketing Budget Opt | Med | Med | 45k | Med | CC0 | Low | 70 |
| 5. Marketing Mix Modeling (MML) | High | Low | 12k | Low | Open Source | Low | 62 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: ISLR Advertising Dataset
* **Source**: Springer ISLR Book Repository
* **URL**: [https://www.kaggle.com/datasets/tawfikhaji/advertising-dataset](https://www.kaggle.com/datasets/tawfikhaji/advertising-dataset)
* **Size**: 200 rows (~5 KB)
* **Input Schema**: `TV`, `Radio`, `Newspaper`.
* **Output Labels**: `Sales` (revenue).
* **Data Preparation**: Normalize variables. Define cost bounds and expected return multipliers.
* **Training & Validation Strategy**: Fit Ridge regression to determine spend elasticity slopes. Pass output parameters to SciPy linear programming solver. Validate against historical ROAS.

---

## 7. Trend Agent
* **Task Type**: Time-Series Forecasting
* **Model Purpose**: Predict monthly Google search interest multipliers and seasonal spikes.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Walmart Store Sales (Kaggle)** | High | High | 421k | High | Competition | High | **95 (Winner)** |
| 2. Rossmann Store Sales | High | High | 1M | Med | Competition | High | 90 |
| 3. Google Trends interest indexes | Med | Med | 500 | High | CC0 | High | 85 |
| 4. M5 Forecasting Retail | High | Low | 5M | Low | CC-BY-SA | High | 72 |
| 5. Wikipedia Web Traffic | Med | Low | 150k | Low | CC0 | Med | 58 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Walmart Recruiting Store Sales Forecasting
* **Source**: Kaggle Datasets
* **URL**: [https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting)
* **Size**: 421k samples (~15 MB)
* **Downsampling for Local Development**: Subset to a single store/department (e.g. Store 1, Dept 1) to keep local test iterations quick.
* **Input Schema**: `Store`, `Dept`, `Date`, `IsHoliday`, `Temperature`, `CPI`, `Unemployment`.
* **Output Labels**: `Weekly_Sales` (trend multiplier target).
* **Data Preparation**: Parse date objects, extract year, month, and day-of-week. Impute markdown gaps with zero.
* **Training & Validation Strategy**: Split: chronological train/test (shuffle=False). Fit Prophet and XGBoost. Metric: Weighted Mean Absolute Error (WMAE).

---

## 8. Recommendation Agent
* **Task Type**: Recommendation System (Collaborative Filtering)
* **Model Purpose**: Recommend layout sizes, color palettes, and CTAs for specific channels.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Instacart Market Basket (Kaggle)** | High | High | 3M | High | Open Use | High | **94 (Winner)** |
| 2. Online Retail Transactions | High | Med | 541k | High | Open Use | High | 88 |
| 3. Movielens 100k (GroupLens) | Med | High | 100k | High | Research | High | 82 |
| 4. Amazon E-commerce Reviews | Med | Med | 10M | Low | Apache-2.0 | High | 74 |
| 5. H&M Personalized Recs | High | Low | 30M | Low | Competition | High | 60 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Instacart Market Basket Analysis
* **Source**: Instacart Research / Kaggle
* **URL**: [https://www.kaggle.com/c/instacart-market-basket-analysis](https://www.kaggle.com/c/instacart-market-basket-analysis)
* **Size**: 3M orders (~45 MB)
* **Downsampling for Local Development**: Subset transactions to top 5,000 users.
* **Input Schema**: `user_id`, `product_id`, `order_dow`, `order_hour_of_day`.
* **Output Labels**: Recommended product categories ( CTA formats).
* **Data Preparation**: One-hot encode user interactions, generate implicit interaction matrix (users x layouts).
* **Training & Validation Strategy**: Split: hold out last order for test. Fit LightFM model. Metric: MAP@K, Precision@K.

---

## 9. Forecast Agent
* **Task Type**: Regression / Time-Series Forecasting
* **Model Purpose**: Predict impressions, clicks, and conversion curves over a campaign's lifecycle.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Store Item Demand Forecasting** | High | High | 913k | High | CC0 | High | **96 (Winner)** |
| 2. Rossmann Daily Sales | High | High | 1M | Med | Competition | High | 89 |
| 3. Hourly Energy Consumption | Med | Med | 145k | High | CC0 | Med | 78 |
| 4. NYC Taxi Traffic | Med | Low | 10M | Low | Open Data | High | 72 |
| 5. Air Passenger Time Series | Low | High | 144 | High | Open Use | High | 60 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Store Item Demand Forecasting
* **Source**: Kaggle Datasets
* **URL**: [https://www.kaggle.com/c/demand-forecasting-kernels-only](https://www.kaggle.com/c/demand-forecasting-kernels-only)
* **Size**: 913,000 samples (~12 MB)
* **Downsampling for Local Development**: Slice data to a single store's history.
* **Input Schema**: `date`, `store`, `item`.
* **Output Labels**: `sales` (clicks/impressions trajectory).
* **Data Preparation**: Extract temporal attributes, compute rolling window means (7-day, 30-day lags).
* **Training & Validation Strategy**: Walk-forward validation (shuffle=False). Fit XGBoost Regressor. Metric: SMAPE.

---

## 10. Fraud Agent
* **Task Type**: Anomaly Detection
* **Model Purpose**: Identify lead-fraud and click-fraud patterns in active telemetry.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Credit Card Fraud (Kaggle)** | High | High | 284k | High | ODbL | High | **97 (Winner)** |
| 2. IP Click Fraud (TalkingData) | High | Med | 185M | Low | Competition | High | 88 |
| 3. IEEE-CIS Fraud Detection | High | Low | 590k | Low | Competition | High | 74 |
| 4. Synthetic Financial Trans | Med | Med | 6M | Med | CC0 | Med | 70 |
| 5. Anomaly Ingestion logs | Low | Med | 10k | High | OpenML | Low | 62 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Credit Card Fraud Detection
* **Source**: ULB ML Group / Kaggle
* **URL**: [https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
* **Size**: 284,807 rows (~150 MB)
* **Downsampling for Local Development**: Extract all fraud cases (492) and mix with 10k normal cases to preserve the anomaly signal while reducing size.
* **Input Schema**: `Time`, PCA numerical features `V1-V28`, `Amount`.
* **Output Labels**: `Class` (0 = Normal, 1 = Fraud).
* **Data Preparation**: Standardize `Amount`, drop `Time`.
* **Training & Validation Strategy**: Semi-supervised split: train model on 100% normal cases. Fit Isolation Forest. Metric: Recall, Precision-Recall AUC (PR-AUC).

---

## 11. Lead Scoring Agent
* **Task Type**: Binary Classification
* **Model Purpose**: Predict prospect conversion probability based on CRM interaction logs.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Leads Dataset (X Education)** | High | High | 9.2k | High | CC0 | High | **98 (Winner)** |
| 2. Bank Marketing Conversion | High | High | 11k | High | CC0 | High | 92 |
| 3. IBM Watson Customer Value | Med | Med | 9k | High | Proprietary | Med | 80 |
| 4. Portuguese Bank Telemarketing | Med | Med | 45k | Med | CC0 | Low | 74 |
| 5. CRM Lead Telemetry (UCI) | Low | Low | 3k | High | Open Use | Low | 58 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Leads Dataset
* **Source**: X Education Marketing / Kaggle
* **URL**: [https://www.kaggle.com/datasets/ashydv/leads-dataset](https://www.kaggle.com/datasets/ashydv/leads-dataset)
* **Size**: 9,240 samples (~1.2 MB)
* **Input Schema**: `Lead Source`, `TotalVisits`, `Total Time Spent on Website`, `Page Views Per Visit`, `Last Activity`.
* **Output Labels**: `Converted` (0 or 1).
* **Data Preparation**: Impute null values, group infrequent categorical values under `Other`, apply `StandardScaler`.
* **Training & Validation Strategy**: Stratified 5-Fold Split. Fit XGBoost. Metric: F1-Score, Brier Score (for probability calibration).

---

## 12. Sentiment Agent
* **Task Type**: Sequence Classification (NLP)
* **Model Purpose**: Classify user social comments into positive, negative, or neutral sentiment.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Sentiment140 Twitter (HF)** | High | High | 1.6M | High | CC0 | High | **96 (Winner)** |
| 2. IMDb Movie Reviews (HF) | High | High | 50k | High | Open Use | High | 88 |
| 3. Yelp Reviews (HF) | Med | Med | 700k | Med | Open Use | High | 80 |
| 4. SST-2 Sentiment (Stanford) | High | High | 67k | High | Academic | High | 78 |
| 5. Amazon Polarity Reviews | Med | Low | 3.6M | Low | CC0 | Med | 64 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: Sentiment140 Dataset
* **Source**: Stanford University / Hugging Face
* **URL**: [https://huggingface.co/datasets/sentiment140](https://huggingface.co/datasets/sentiment140)
* **Size**: 1.6M rows (~300 MB)
* **Downsampling for Local Development**: Slice training text set to 20k rows.
* **Input Schema**: Raw string text.
* **Output Labels**: `polarity` (0 = Negative, 4 = Positive).
* **Data Preparation**: Clean Twitter-specific characters (@ usernames, RT retweets), tokenize strings.
* **Training & Validation Strategy**: Split: 80% train, 20% validation. Fine-tune DistilRoBERTa. Metric: Accuracy, F1-Macro.

---

## 13. Vision Agent
* **Task Type**: Image Regression (Aesthetics)
* **Model Purpose**: Evaluate display creatives and banners against aesthetic score targets.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. AVA Aesthetic Visual (Kaggle)** | High | High | 250k | Med | Research Only | High | **94 (Winner)** |
| 2. Image Popularity Assessment | Med | Med | 10k | High | CC0 | Med | 84 |
| 3. Flickr Aesthetic Assessment | Med | Med | 8k | High | Research | Med | 76 |
| 4. Photo Aesthetics Ranking | Low | Med | 5k | Med | Open Use | Low | 68 |
| 5. Banner Quality Scorer | High | Low | 2k | Low | Roboflow | Low | 55 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: AVA (Aesthetic Visual Analysis)
* **Source**: Academic Research / Kaggle
* **URL**: [https://www.kaggle.com/datasets/nandodefreitas/ava-dataset](https://www.kaggle.com/datasets/nandodefreitas/ava-dataset)
* **Size**: 250,000 images + metadata (~30 GB raw, metadata ~50 MB)
* **Downsampling for Local Development**: Train only on pre-extracted CLIP embedding features (512-dim vectors) of images, reducing size to ~40 MB.
* **Input Schema**: Static image files (PNG/JPG) or pre-extracted CLIP embedding vectors.
* **Output Labels**: Average rating score (1.0 to 10.0).
* **Data Preparation**: Resize images to 224x224, apply random horizontal flips, extract embeddings.
* **Training & Validation Strategy**: Split: 80/20. Fit Ridge regression on CLIP vectors. Metric: Spearman Rank Correlation, MSE.

---

## 14. Knowledge Agent
* **Task Type**: Dense Passage Retrieval (RAG / NLP)
* **Model Purpose**: Retrieve relevant context passages for campaign briefs from vector store.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. MS MARCO Passage (HF)** | High | High | 8.2M | Med | CC-BY-4.0 | High | **96 (Winner)** |
| 2. SQuAD 2.0 (Stanford) | High | High | 100k | High | CC-BY-SA | High | 90 |
| 3. Natural Questions (Google) | Med | High | 300k | Med | CC-BY-4.0 | High | 82 |
| 4. CoQA Conversation QA | Med | Med | 120k | High | CC-BY-SA | Med | 78 |
| 5. HotpotQA (Academic) | High | Low | 110k | Low | CC-BY-SA | Med | 64 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: MS MARCO
* **Source**: Microsoft Research / Hugging Face
* **URL**: [https://huggingface.co/datasets/ms_marco](https://huggingface.co/datasets/ms_marco)
* **Size**: 8.2M passages (~2.1 GB)
* **Downsampling for Local Development**: Subset to 50k query-passage pairs.
* **Input Schema**: `query`, `passages` (passage text, URL).
* **Output Labels**: Binary selection indicator `is_selected` (relevance label).
* **Data Preparation**: Strip special symbols, tokenize text inputs.
* **Training & Validation Strategy**: Contrastive training of Bi-Encoder model. Metric: MRR@10.

---

## 15. Optimizer Agent
* **Task Type**: Reinforcement Learning (Real-Time Bidding)
* **Model Purpose**: Adjust ad bidding actions sequentially based on cost and conversion feedback.

### 📊 Dataset Rankings
| Dataset Name | Accuracy Potential | Data Quality | Size | Ease of Use | License | Popularity | Suitability Score (0-100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. iPinYou RTB (iPinYou)** | High | High | 19M | Med | Research Only | High | **95 (Winner)** |
| 2. YOYI RTB Log Dataset | High | Med | 5M | Low | Research Only | Med | 85 |
| 3. Multi-Armed Bandit Logs | Med | Med | 1M | High | CC0 | Low | 78 |
| 4. Yahoo RTB Auction | Med | Low | 50M | Low | Request Req | Low | 62 |
| 5. AdExchange Bid Event Logs | Low | Med | 200k | High | MIT | Low | 58 |

### 🛠️ Selected Dataset Details
* **Dataset Name**: iPinYou RTB Dataset
* **Source**: iPinYou / Kaggle
* **URL**: [https://www.kaggle.com/datasets/saurabhbagchi/ipinyou-rtb-dataset](https://www.kaggle.com/datasets/saurabhbagchi/ipinyou-rtb-dataset)
* **Size**: 19.5M samples (~2.5 GB)
* **Downsampling for Local Development**: Subset to a single advertiser log (e.g. Advertiser 1458).
* **Input Schema**: `bidprice`, `payprice`, `click`, `hour`, `weekday`, `useragent`, `slotprice`.
* **Output Labels**: Click reward (0 or 1).
* **Data Preparation**: Scale bids, define state representation vector based on remaining budget.
* **Training & Validation Strategy**: Off-policy RL environment training (Stable-Baselines3 PPO). Metric: Expected CPA, Win Rate.
