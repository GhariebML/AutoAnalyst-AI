# AdPilot Pro – Optimizer Agent Dataset Catalog

This document compares and catalogs candidate public datasets for real-time bidding (RTB) auctions, marketing budget optimization, and reinforcement learning state parameters.

---

## 1. iPinYou RTB Dataset (Selected)
* **Dataset Name**: iPinYou Real-Time Bidding Dataset
* **URL**: [http://www.ipinyou.com/](http://www.ipinyou.com/) (adapted/mapped offline equivalent)
* **License**: Open for Research / Academic Use
* **Size**: 19.5 Million rows.
* **Features**: bid_price, paying_price, click_flag, impression_flag, bidding_strategy.
* **Target**: click_flag (conversion reward signal) and paying_price (cost/overspend signal).
* **Advantages**: The gold-standard dataset for modeling ad auction dynamics, bidding behaviors, and reward functions.
* **Disadvantages**: Lack of direct state vectors matching continuous Gymnasium structures.
* **Quality Score**: 96/100
* **Recommended Usage**: Primary target for training contextual bandits and Q-learning state environments.

---

## 2. Avazu Mobile Click-Through Rate Dataset (Alternative)
* **Dataset Name**: Avazu Mobile Click Prediction Challenge
* **URL**: [https://www.kaggle.com/c/avazu-ctr-prediction](https://www.kaggle.com/c/avazu-ctr-prediction)
* **License**: Competition License
* **Size**: 40 Million rows.
* **Features**: Click flags, device types, banner placements.
* **Target**: Click flag (binary click prediction indicator).
* **Advantages**: High-volume real-world mobile advertisement impression details.
* **Disadvantages**: Extremely high file size and memory footprint.
* **Quality Score**: 90/100
* **Recommended Usage**: Benchmarking click-through propensity prediction features.
