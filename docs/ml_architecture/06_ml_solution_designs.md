# AdPilot Pro – ML Solution Designs (Phase 4)

This document contains the engineering designs for the specialized Machine Learning solutions integrated with all 15 agents in the AdPilot Pro ecosystem.

---

## 1. Strategy Agent
* **Candidate Models**: LightGBM, XGBoost, CatBoost
* **Why**: The strategy agent solves a multi-label classification problem (selecting channels like LinkedIn, Instagram, etc.). Gradient boosted trees excel on tabular campaign inputs with high categorical feature cardinality. LightGBM is chosen for its fast training and low memory usage.
* **Input**: User campaign parameters: `budget_usd`, `goals` (one-hot), `tone_of_voice` (one-hot), `target_market` (embeddings), `campaign_duration_days`.
* **Output**: Vector of probability scores for each channel (e.g., `[0.82, 0.45, 0.12]`).
* **Training**: Trained using Binary Cross Entropy loss (Multi-Label Classification) with time-based cross-validation.
* **Evaluation**: Micro-F1 Score, ROC-AUC, and Mean Average Precision.
* **Serving**: Loaded on startup via `lightgbm` native wrapper and cached features.

---

## 2. Audience Agent
* **Candidate Models**: K-Means, HDBSCAN, Agglomerative Clustering
* **Why**: Demographic segment grouping is an unsupervised task. HDBSCAN is preferred as it doesn't require predefining cluster counts, automatically filters noise, and groups users into organic cohorts.
* **Input**: Demographic attributes: `age_group`, `annual_income`, `purchasing_power_index`, `geographic_region_id`.
* **Output**: Cluster ID assignment (int) representing the target persona group.
* **Training**: Fit on processed CRM datasets; model hyperparameters optimized using grid search over Silhouette score.
* **Evaluation**: Silhouette Coefficient, Calinski-Harabasz Index, and Davies-Bouldin Index.
* **Serving**: Executed offline to generate segment vectors which are saved in Redis; online checks perform low-latency closest-centroid lookups.

---

## 3. Research Agent
* **Candidate Models**: BERT, Sentence-BERT, RoBERTa
* **Why**: The Research Agent extracts entities and classifies competitor texts. Pretrained Transformer encoders (Sentence-BERT) capture contextual semantics and generate high-quality text embeddings.
* **Input**: Scraped text fragments from competitor web pages.
* **Output**: Dense semantic embedding vectors (768 dimensions) and classified topic weights.
* **Training**: Fine-tuned using PyTorch and HuggingFace on AG News or custom business categorization datasets.
* **Evaluation**: Accuracy, Macro-Precision, and Macro-Recall.
* **Serving**: Inference via HuggingFace `transformers` pipeline, cached locally.

---

## 4. Content Agent
* **Candidate Models**: LLaMA-3-8B-Instruct (PEFT/LoRA), Mistral-7B, GPT-4o-mini
* **Why**: Drafting marketing copy is a generative text task. A local 8B parameter model fine-tuned via PEFT/LoRA allows generation of brand-aligned copy while protecting user prompt privacy.
* **Input**: Strategy output, research personas, and analytics feedback hints (e.g. "Headline is too salesy").
* **Output**: Text sequences representing ad creatives, emails, or posts.
* **Training**: Quantized LoRA (QLoRA) parameter-efficient training using HuggingFace `peft` library.
* **Evaluation**: BLEU, ROUGE-L, perplexity, and quality gate score.
* **Serving**: Served locally using local inference engine (e.g. Ollama or HuggingFace pipeline).

---

## 5. Analytics Agent
* **Candidate Models**: LightGBM Regressor, XGBoost Regressor, MLP Regressor
* **Why**: Predicting copy quality score and expected CTR/conversion rates is a regression task. LightGBM excels at modeling complex, non-linear relationships between text features and CTR.
* **Input**: Text embeddings of generated ad copy, target channel, budget, and persona segments.
* **Output**: Expected health score (0-100) and predicted CTR float.
* **Training**: MSE (Mean Squared Error) loss function optimized with early stopping.
* **Evaluation**: Mean Absolute Error (MAE), RMSE, and R² score.
* **Serving**: Ingested directly into the quality gate loop in [main.py](file:///d:/ADPilot_Pro/src/adpilot/api/main.py).

---

## 6. Budget Agent
* **Candidate Models**: Linear Programming (SciPy Optimize / PuLP), Quadratic Programming
* **Why**: Allocating budget is a constrained optimization problem. Linear Programming allows maximizing total conversion volume subject to max budget constraints and channel caps.
* **Input**: Channel cost-per-click (CPC) estimates, expected conversion rates, and total budget limits.
* **Output**: Optimal dollar allocations per channel (e.g. `{"linkedin": 3000, "facebook": 2000}`).
* **Training**: No model training; optimization parameters are updated continuously from live CTR and CPC inputs.
* **Evaluation**: Feasibility rate and predicted ROI/ROAS comparison.
* **Serving**: SciPy solver initialized inside `CampaignManagerAgent` pipeline.

---

## 7. Trend Agent
* **Candidate Models**: Prophet, SARIMAX, Holt-Winters
* **Why**: Trend detection requires time-series forecasting. Meta's Prophet handles seasonality, weekly/monthly patterns, and holidays automatically.
* **Input**: Historic daily/weekly search index volumes and sales volume time series.
* **Output**: Predicted trend multiplier indexes for the next 30 days.
* **Training**: Model fit on historical trends; parameters re-estimated periodically.
* **Evaluation**: Mean Absolute Percentage Error (MAPE) and MAE.
* **Serving**: Run offline daily, writing trend coefficients into SQLite database.

---

## 8. Recommendation Agent
* **Candidate Models**: Matrix Factorization, LightFM, Content-Based Filtering
* **Why**: Suggesting ad layouts, CTAs, and colors requires collaborative filtering. LightFM allows incorporating both user-item interactions and meta-features (like CTA text or color style).
* **Input**: Campaign target categories, historic performance of layout styles, and channel.
* **Output**: Ranked list of recommended layout structures and CTA models.
* **Training**: BPR (Bayesian Personalized Ranking) loss function on user interaction logs.
* **Evaluation**: Precision@K, Recall@K, and MAP@K.
* **Serving**: Online recommendations fetched via light-weight dot product calculations in Python.

---

## 9. Forecast Agent
* **Candidate Models**: XGBoost Regressor, Prophet, LSTM
* **Why**: Forecasting impressions and click trajectories over time is a seasonal time-series task. XGBoost with lagged features handles volatile traffic changes effectively.
* **Input**: Historical daily impressions, dates, and campaign budget parameters.
* **Output**: Forecasted daily click and impression floats for the campaign duration.
* **Training**: Trained on lagged time-series features with walk-forward validation.
* **Evaluation**: Symmetric MAPE (SMAPE) and RMSE.
* **Serving**: Run synchronously upon campaign creation to display forecasted performance charts.

---

## 10. Fraud Agent
* **Candidate Models**: Isolation Forest, Local Outlier Factor (LOF), One-Class SVM
* **Why**: Click/lead fraud detection is an anomaly detection task. Isolation Forest isolates anomalies by randomly partitioning features, making it highly effective at detecting novel fraud vectors.
* **Input**: Telemetry events: `ip_address`, `request_rate`, `device_fingerprint`, `time_delta_between_clicks`.
* **Output**: Anomaly score and binary classification (0 = Normal, 1 = Suspicious).
* **Training**: Semi-supervised training on clean baseline traffic logs.
* **Evaluation**: Precision, Recall, and F1-score on simulated fraud injection sets.
* **Serving**: Fast inference hook integrated within the Lead Ingestion API router.

---

## 11. Lead Scoring Agent
* **Candidate Models**: XGBoost Classifier, Logistic Regression, MLP
* **Why**: Predicting lead conversion is a binary classification task. XGBoost is standard for tabular lead inputs, scoring leads based on page views and CRM history.
* **Input**: Lead telemetry: `total_time_on_site`, `page_views_per_visit`, `source`, `country`, `lead_quality_score`.
* **Output**: Conversion probability score (float between 0.0 and 1.0).
* **Training**: Binary Cross Entropy loss with stratified k-fold cross-validation.
* **Evaluation**: F1-Score, Precision-Recall AUC, and Brier score (for calibration).
* **Serving**: Triggered synchronously when a lead interacts with the campaign funnel.

---

## 12. Sentiment Agent
* **Candidate Models**: RoBERTa, DistilBERT, FinBERT
* **Why**: Tracking user comments is a sentiment classification task. Pretrained transformer sequence classifiers (RoBERTa) provide state-of-the-art accuracy on informal social media text.
* **Input**: Audience comment strings.
* **Output**: Probabilities for three classes: `Positive`, `Negative`, `Neutral`.
* **Training**: PyTorch fine-tuning on Twitter Sentiment140 or custom ad feedback.
* **Evaluation**: F1-Score (macro) and Accuracy.
* **Serving**: Inference via HuggingFace pipeline runner.

---

## 13. Vision Agent
* **Candidate Models**: ResNet-50, CLIP + Linear Probing, ViT (Vision Transformer)
* **Why**: Evaluating ad creatives requires image classification and aesthetic scoring. Extracting embeddings via CLIP and training a lightweight linear regression probe (aesthetics scorer) ensures fast inference and robust generalized visual concepts.
* **Input**: Generated creative images (PNG/JPG).
* **Output**: Predicted aesthetic rating score (1.0 - 10.0).
* **Training**: Ridge Regression trained on CLIP image features using AVA dataset.
* **Evaluation**: Spearman Rank Correlation and MSE.
* **Serving**: Loaded in memory alongside the image generation pipeline in the backend.

---

## 14. Knowledge Agent
* **Dataset Proposed**: Bi-Encoder / Cross-Encoder (Dense Passage Retrieval)
* **Why**: RAG retrieval requires finding relevant text paragraphs. A Bi-encoder (Sentence-BERT) maps text query and passages to a shared space, allowing high-speed cosine similarity searching inside a vector database (Qdrant).
* **Input**: Natural language user search query.
* **Output**: Ordered list of relevant context paragraphs from local company files.
* **Training**: Contrastive loss trained on MS MARCO query-passage pairs.
* **Evaluation**: MRR@10 (Mean Reciprocal Rank) and NDCG@10.
* **Serving**: Direct integration with Qdrant Vector Store query pipeline.

---

## 15. Optimizer Agent
* **Candidate Models**: Deep Q-Network (DQN), Proximal Policy Optimization (PPO), Contextual Bandits
* **Why**: Real-time bid optimization is a sequential decision task. PPO optimizes policy actions directly based on performance rewards (clicks, budget consumption), avoiding instability.
* **Input**: Current bid, target campaign metrics, remaining budget, and time elapsed.
* **Output**: Adjusted bid value (e.g. increase bid by 15%).
* **Training**: Trained using RL environments with reward functions mapped to CPC/CPA efficiency.
* **Evaluation**: Average reward progression and cost efficiency curves.
* **Serving**: Runs on background schedule to fine-tune ongoing campaign parameters.
