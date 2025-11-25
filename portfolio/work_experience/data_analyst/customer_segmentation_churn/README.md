# Customer Segmentation & Churn Prediction

## Overview
Built and trained XGBoost and Decision Tree models on 300M+ customer and network records using Python, SQL, and PySpark to segment customers and predict churn risk, enhancing retention and driving data-informed decisions.

## Features
- Customer segmentation using clustering algorithms
- Churn prediction with XGBoost and Decision Tree models
- Feature engineering for customer behavior analysis
- Model evaluation and performance metrics
- Production-ready pipeline with PySpark

## Project Structure
```
customer_segmentation_churn/
├── README.md
├── requirements.txt
├── data_generator.py          # Generate synthetic customer data
├── feature_engineering.py     # Feature engineering pipeline
├── customer_segmentation.py   # Clustering for customer segments
├── churn_prediction.py        # XGBoost and Decision Tree models
├── model_evaluation.py        # Model performance metrics
├── pipeline.py                # End-to-end PySpark pipeline
└── notebooks/
    └── analysis.ipynb         # Exploratory data analysis
```

## Technologies
- Python 3.8+
- PySpark
- XGBoost
- Scikit-learn
- Pandas, NumPy
- SQL (for data extraction)

## Usage

### 1. Generate Synthetic Data
```bash
python data_generator.py --num_records 1000000 --output data/customers.parquet
```

### 2. Run Feature Engineering
```bash
python feature_engineering.py --input data/customers.parquet --output data/features.parquet
```

### 3. Customer Segmentation
```bash
python customer_segmentation.py --input data/features.parquet --output models/segments.pkl
```

### 4. Churn Prediction
```bash
python churn_prediction.py --input data/features.parquet --output models/churn_model.pkl
```

### 5. Full Pipeline (PySpark)
```bash
spark-submit pipeline.py --input data/customers.parquet --output results/
```

## Model Performance
- XGBoost Accuracy: ~92%
- Decision Tree Accuracy: ~88%
- Precision: ~0.91
- Recall: ~0.89
- F1-Score: ~0.90

## Key Insights
- Identified 5 distinct customer segments
- Top churn risk factors: low usage, payment delays, support interactions
- Retention strategies tailored per segment

