# ScamShield AI

ScamShield AI is an AI-powered email security platform designed to detect
phishing and spam emails using Natural Language Processing (NLP) and
Machine Learning.

The project combines a user-friendly frontend with an ML-based email
classification pipeline. The ML component processes email text, extracts
TF-IDF features, trains multiple classification algorithms, and compares
their performance to identify the most effective model.

---

## Project Status

🚧 **Currently under development**

### Completed

- Collected and analyzed multiple phishing/spam email datasets
- Combined datasets into a unified dataset
- Cleaned and standardized email text
- Validated the cleaned dataset
- Performed stratified train-test splitting
- Extracted TF-IDF features
- Trained four machine learning algorithms
- Compared model performance
- Saved baseline evaluation results

### Upcoming

- Hyperparameter tuning
- Cross-validation
- Detailed model evaluation
- Source-wise robustness analysis
- Explainable AI / feature analysis
- Final model selection
- Email prediction pipeline
- Backend API integration
- Frontend-backend integration
- Real-time email analysis
- Additional scam detection capabilities

---

## System Overview

                    ScamShield AI
                         |
          +--------------+--------------+
          |                             |
       Frontend                    ML Pipeline
          |                             |
     User Input                   Email Dataset
          |                             |
          |                       Data Cleaning
          |                             |
          |                       Data Validation
          |                             |
          |                     Train/Test Split
          |                             |
          |                         TF-IDF
          |                             |
          |              +--------------+--------------+
          |              |       |       |             |
          |             LR      MNB      RF            MLP
          |              |       |       |             |
          |              +-------+-------+-------------+
          |                              |
          |                       Model Comparison
          |                              |
          +------------------------------+
                         |
                  Final Prediction

## Machine Learning Pipeline

The current ML pipeline follows these stages:

```text
Raw Datasets
      ↓
Data Cleaning
      ↓
Dataset Validation
      ↓
Train-Test Split
      ↓
TF-IDF Feature Extraction
      ↓
Model Training
      ↓
Performance Evaluation
      ↓
Model Comparison
      ↓
Best Model Selection

```

## Datasets

The project uses multiple publicly available email datasets containing normal, spam, and phishing-related email samples.
Kaggle Dataset: https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset

Current datasets include:

- CEAS 2008
- Enron
- Ling
- Nazario
- Nigerian Fraud
- SpamAssassin
- Phishing Email Dataset

The original datasets are not stored in this repository because they are external datasets and may have individual licensing and redistribution requirements.The dataset preprocessing pipeline used to create the final training data is included in the project source code.

## Dataset Statistics

After cleaning and preprocessing:

- Total emails: 76,800
- Normal emails: 39,143
- Phishing/Spam emails: 37,657
- Label Distribution
- Label	Meaning	Count	Percentage
- 0	Normal	39,143	50.97%
- 1	Phishing	37,657	49.03%

The dataset was split using stratified sampling:

- Dataset	Samples
- Training	61,440
- Testing	15,360

This maintains approximately the same class distribution in both sets.

## Feature Extraction

Email text is converted into numerical features using TF-IDF (Term Frequency-Inverse Document Frequency).

The current configuration produces:

- Vocabulary size: 50,000
- Training samples: 61,440
- Testing samples: 15,360
- Features: 50,000

TF-IDF allows the machine learning algorithms to represent important words and terms in the email as numerical feature vectors.

## Machine Learning Models

Four different classification algorithms are currently being compared:

1. Logistic Regression: A linear classification algorithm used as a strong baseline forhigh-dimensional text classification.
2. Multinomial Naive Bayes: A probabilistic classifier commonly used for text classification problems.
3. Random Forest: An ensemble learning algorithm consisting of multiple decision trees.
4. MLP Neural Network: A Multi-Layer Perceptron neural network capable of learning nonlinear relationships in the extracted feature space.

## Baseline Results

The first baseline experiment produced the following results:

```text
Model	Accuracy	Precision	Recall	F1 Score
MLP Neural Network	99.12%	98.95%	99.26%	99.11%
Logistic Regression	98.59%	98.09%	99.06%	98.57%
Random Forest	98.20%	98.66%	97.65%	98.15%
Multinomial Naive Bayes	96.76%	98.70%	94.65%	96.63%
Current Best Baseline
```

The MLP Neural Network currently provides the best baseline performance with an F1 score of 99.11%. This is a preliminary result. Hyperparameter tuning and additional evaluation will be performed before selecting the final production model.

## Evaluation Metrics

The models are evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix

For phishing detection, Recall is particularly important because a false negative represents a phishing email incorrectly classified as normal.

## Project Structure

```text
ScamShield/
│
├── README.md
├── .gitignore
│
├── scamshield-ai/
│   └── Frontend files
│
└── scamshield-ML/
    │
    ├── src/
    │   ├── clean_dataset.py
    │   ├── validate_dataset.py
    │   ├── split_dataset.py
    │   ├── feature_extraction.py
    │   └── model_training.py
    │
    ├── results/
    │   └── model_comparison.csv
    │
    └── requirements.txt
```

Large datasets, generated TF-IDF features, trained model files, virtual environments, and other generated files are excluded from version control.

## Technologies Used: 

- Machine Learning
- Python
- Pandas
- NumPy
- Scikit-learn
- Joblib
- TF-IDF
- Logistic Regression
- Multinomial Naive Bayes
- Random Forest
- MLP Neural Network
- Frontend
- HTML
- CSS
- JavaScript
- React
- Development Tools
- Visual Studio Code
- Git
- GitHub
- GitHub Desktop

## Running the ML Pipeline

Clone the repository and navigate to the ML directory:

```text
cd scamshield-ML
```

Create and activate a virtual environment:

```text
python -m venv .venv
```

Activate it on Windows:

```text
.venv\Scripts\activate
```
Install the required dependencies:
```text
pip install -r requirements.txt
```

The ML pipeline can then be executed in the following order:

```text
python src/clean_dataset.py
python src/validate_dataset.py
python src/split_dataset.py
python src/feature_extraction.py
python src/model_training.py
```

The original datasets must be obtained separately and placed in the appropriate local dataset directory before running the pipeline.

## Future Development

ScamShield AI is planned to evolve into a complete email security platform with:

- Automated email analysis
- Real-time phishing detection
- Backend prediction API
- Frontend integration
- Explainable predictions
- URL and malicious-link analysis
- Additional scam detection capabilities
- Model optimization and tuning
- Robustness testing across different datasets
- Production-ready deployment

## Disclaimer

ScamShield AI is an academic software engineering and machine learning project intended for research and educational purposes. Model predictions should not be treated as a guaranteed determination of whether an email is malicious or legitimate.
