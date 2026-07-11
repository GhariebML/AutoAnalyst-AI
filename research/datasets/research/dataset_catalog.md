# AdPilot Pro – Research Agent Dataset Catalog

This document compares and catalogs candidate public datasets for topic classification, trend forecasting, and competitor research.

---

## 1. AG News Dataset (Selected)
* **Dataset Name**: AG News Dataset
* **URL**: [https://huggingface.co/datasets/ag_news](https://huggingface.co/datasets/ag_news)
* **License**: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
* **Size**: 120k train, 7.6k test samples (~30 MB)
* **Features**: `title`, `description` (raw text strings)
* **Target**: `label` (1-World, 2-Sports, 3-Business, 4-Sci/Tech)
* **Advantages**: Very clean topic definitions, well-balanced distributions, widely cited baseline for topic modeling and NLP research.
* **Disadvantages**: Large vocabulary requires text cleanup and vector feature selections.
* **Quality Score**: 97/100
* **Recommended Usage**: Primary benchmark for keyword ranking and topic clustering.

---

## 2. 20 Newsgroups Dataset (Alternative)
* **Dataset Name**: 20 Newsgroups
* **URL**: [https://archive.ics.uci.edu/ml/datasets/Twenty+Newsgroups](https://archive.ics.uci.edu/ml/datasets/Twenty+Newsgroups)
* **License**: Public Domain
* **Size**: 18,846 samples, 20 classes (~15 MB)
* **Features**: Email subject, header, raw body content.
* **Target**: 20 news categories.
* **Advantages**: High text length variety.
* **Disadvantages**: High vocabulary noise (email signatures, headers) requires extensive preprocessing.
* **Quality Score**: 80/100
* **Recommended Usage**: Evaluation of high-cardinality topic mapping models.
