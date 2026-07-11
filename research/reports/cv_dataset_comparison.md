# AdPilot Pro – Computer Vision Agent Dataset Catalog

This document compares and catalogs candidate public datasets for computer vision models, aesthetic scoring, logo detection, and marketing creative quality evaluation.

---

## 1. Aesthetic Visual Analysis (AVA) Dataset (Selected)
* **Dataset Name**: AVA (Aesthetic Visual Analysis)
* **URL**: [https://github.com/img-sg/ava-dataset](https://github.com/img-sg/ava-dataset)
* **License**: Non-commercial / Research use only
* **Size**: 250,000 images.
* **Features**: RGB pixel arrays, aspect ratios, semantic annotations.
* **Target**: `aesthetic_score` (continuous rating index from 1.0 to 10.0 representing estimated image appeal).
* **Advantages**: The gold-standard dataset for image aesthetic prediction.
* **Disadvantages**: Large size (~30 GB) requires downsampling for local execution.
* **Quality Score**: 98/100
* **Recommended Usage**: Primary target for training creative quality score regressor.

---

## 2. LogoDet-3K Dataset (Alternative)
* **Dataset Name**: LogoDet-3K
* **URL**: [https://github.com/WangJian10/LogoDet-3K](https://github.com/WangJian10/LogoDet-3K)
* **License**: Research use only
* **Size**: 3,000 logo categories, 158,000 images.
* **Features**: Bounding box coordinates for logo detections.
* **Target**: Class category labels and coordinates.
* **Advantages**: High variety of corporate and product logos.
* **Disadvantages**: Dominated by product packaging rather than display banners.
* **Quality Score**: 91/100
* **Recommended Usage**: Benchmarking multi-label corporate logo detection models.
