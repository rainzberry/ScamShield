# ScamShield AI

### Intelligent Multi-Level Phishing, Spam & Malicious Content Detection Platform Using Explainable Machine Learning

ScamShield AI is a multi-modal security platform designed to identify potentially malicious digital content by analysing **emails, URLs, and QR codes**. It combines machine learning, URL analysis, QR-code decoding, risk assessment, and explainable detection results through a unified dashboard.

The project aims to help users recognise suspicious messages and links before interacting with them, while providing understandable reasons behind a threat assessment.

> **Project type:** Software Engineering & Machine Learning
> **Status:** Under active development
> **Primary goal:** Explainable, multi-level scam and phishing detection

---

## Table of Contents

* [Overview](#overview)
* [Key Features](#key-features)
* [System Architecture](#system-architecture)
* [Detection Pipelines](#detection-pipelines)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Installation and Setup](#installation-and-setup)
* [Testing and Validation](#testing-and-validation)
* [Security Considerations](#security-considerations)
* [Limitations](#limitations)
* [Future Enhancements](#future-enhancements)
* [Disclaimer](#disclaimer)

---

## Overview

Digital scams increasingly use deceptive emails, malicious URLs, impersonation, and QR codes to trick users into revealing sensitive information or visiting unsafe websites.

ScamShield AI approaches this problem through three analysis modules:

1. **Email Analysis** — examines email text for phishing, spam, scam-related language, and other suspicious indicators.
2. **URL Analysis** — evaluates URL characteristics and suspicious patterns to estimate potential risk.
3. **QR Code Analysis** — decodes a QR code from an uploaded image and analyses the extracted content, particularly URLs.

The analysis results are presented through a dashboard designed to make suspicious indicators and risk assessments easier to understand.

ScamShield AI is intended as a decision-support tool. It does not guarantee that every malicious item will be detected.

---

## Key Features

### 1. Email Threat Detection

* Analyse user-provided email content.
* Use natural language processing and machine learning to classify suspicious text.
* Identify indicators associated with phishing, spam, scams, and malicious content.
* Present a risk assessment and supporting evidence where available.

### 2. URL Threat Analysis

* Accept a URL for inspection.
* Extract lexical and structural URL characteristics.
* Evaluate suspicious patterns using a machine-learning model and applicable detection rules.
* Present a risk score and relevant warning indicators.

### 3. QR Code and Quishing Detection

Quishing is phishing conducted through QR codes.

* Accept a QR-code image as input.
* Use OpenCV-based QR detection and decoding.
* Extract the embedded text or URL.
* Pass extracted URLs to the URL-analysis module when applicable.
* Present the resulting assessment to the user.

**Important:** Decoding a QR code does not establish that its destination is safe. The decoded content must be inspected separately.

### 4. Explainable Risk Assessment

ScamShield AI is designed to make detection results more understandable by combining model predictions with identifiable risk indicators.

Depending on the analysis module, results may include:

* Classification or threat category.
* Risk score and severity level.
* Suspicious patterns or rule matches.
* Evidence supporting the assessment.

### 5. Security Dashboard

The frontend provides a central interface for interacting with the detection modules and viewing analysis results.

The intended interface uses a dark cybersecurity-inspired design, with high-visibility warnings and clear risk indicators.

### 6. Modular Architecture

The project separates the frontend, backend services, and machine-learning functionality to make the system easier to test, maintain, and extend.

---

## System Architecture

```text
                     USER
                      |
                      v
             SCAMSHIELD AI FRONTEND
                      |
                      v
                BACKEND API
                      |
           +----------+----------+
           |          |          |
           v          v          v
       EMAIL         URL         QR
      ANALYSIS     ANALYSIS    ANALYSIS
           |          |          |
           v          v          v
       Text ML     URL Model   OpenCV QR
       + Rules     + Rules     Decoding
           |          |          |
           +----------+----------+
                      |
                      v
             RISK ASSESSMENT
                      |
                      v
          EXPLANATION AND RESULTS
                      |
                      v
                DASHBOARD
```

### High-level workflow

1. The user submits email text, a URL, or a QR-code image.
2. The frontend sends the input to the appropriate backend endpoint.
3. The backend validates and routes the input to the relevant detection module.
4. The module performs machine-learning inference, rule-based checks, or QR decoding as appropriate.
5. The system assembles the available classification, risk assessment, and evidence.
6. The frontend displays the results.

The exact processing steps depend on the selected input type.

---

## Detection Pipelines

### A. Email Analysis Pipeline

```text
Email Text
    |
    v
Input Validation
    |
    v
Text Preprocessing
    |
    v
TF-IDF Feature Extraction
    |
    v
Machine-Learning Classification
    |
    v
Rule-Based Indicator Analysis
    |
    v
Risk Assessment
    |
    v
Classification + Evidence
```

The email machine-learning workflow uses TF-IDF to represent text numerically and Logistic Regression for text classification. The broader training experiments have also compared Logistic Regression, Multinomial Naive Bayes, Random Forest, and a Multi-Layer Perceptron (MLP).

The current prediction pipeline and the models used for offline experiments should be distinguished: a model being evaluated during training is not necessarily the model used for live predictions.

### B. URL Analysis Pipeline

```text
Submitted URL
     |
     v
URL Validation and Parsing
     |
     v
Lexical Feature Extraction
     |
     v
URL Classification Model
     |
     v
Rule-Based Risk Indicators
     |
     v
Risk Assessment
     |
     v
Result and Supporting Evidence
```

The URL module is designed to evaluate characteristics of a URL rather than relying solely on its appearance or domain name.

The machine-learning component uses lexical URL features with a Random Forest classifier. Relevant detection rules can contribute additional evidence to the final risk assessment.

### C. QR Code Analysis Pipeline

```text
Uploaded QR Image
        |
        v
Image Validation
        |
        v
OpenCV QR Detection
        |
        v
QR Content Decoding
        |
        v
Extracted Text or URL
        |
        v
URL Analysis (when applicable)
        |
        v
Risk Assessment
        |
        v
Displayed Result
```

OpenCV is used for QR-code detection and decoding. It is not, by itself, a phishing-classification model.

When a QR code contains a URL, the extracted URL can be analysed by the URL detection pipeline. Other QR payloads require appropriate handling based on their content type.

---

## Technology Stack

| Component            | Technologies                                        |
| -------------------- | --------------------------------------------------- |
| Frontend             | React, JavaScript, HTML, CSS                        |
| Backend              | Python, Flask                                       |
| Machine Learning     | scikit-learn                                        |
| Text Processing      | TF-IDF                                              |
| Email Classification | Logistic Regression and other evaluated classifiers |
| URL Classification   | Random Forest and lexical features                  |
| QR Processing        | OpenCV                                              |
| Data Processing      | NumPy, pandas                                       |
| Model Persistence    | Joblib                                              |
| Development          | Visual Studio Code, Git, GitHub                     |

---

## Project Structure

```text
ScamShield/
|
|-- README.md
|-- .gitignore
|
|-- scamshield-ai/
|   |-- Frontend application
|   |-- React components
|   |-- UI and styling
|   `-- Frontend configuration
|
|-- scamshield-backend/
|   |-- Flask application
|   |-- API endpoints
|   |-- Request validation
|   `-- Backend configuration
|
`-- scamshield-ML/
    |-- ml/
    |   |-- Email detection
    |   |-- URL detection
    |   |-- QR-related processing
    |   |-- Risk assessment
    |   `-- Tests
    |
    |-- Dataset and model resources
    |-- Evaluation outputs
    `-- Python dependencies
```

*This is a logical overview; individual filenames and subfolders may vary as the implementation evolves.*

---

## Installation and Setup

### Prerequisites

Install the following before running the project:

* Git
* Python 3
* Node.js and npm
* Visual Studio Code (recommended)

Clone the repository:

```bash
git clone https://github.com/rainzberry/ScamShield.git
cd ScamShield
```

### 1. Set Up the Frontend

Open a terminal in the project root:

```bash
cd scamshield-ai
npm install
npm run dev
```

Use the local URL printed by the development server to open the frontend in your browser.

### 2. Set Up the Backend

Open a separate terminal:

```bash
cd scamshield-backend
python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies using the requirements file provided in the backend directory:

```bash
pip install -r requirements.txt
```

Start the Flask application using the entry-point or startup command configured in the backend.

Keep the backend running while using the frontend. Ensure the frontend API configuration points to the correct backend address and port.

### 3. Set Up the Machine-Learning Environment

If the ML module has its own dependency file, use a separate terminal:

```bash
cd scamshield-ML
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

If the ML package requires a separate installation step or model artifacts, follow the instructions in its configuration and module documentation before starting the backend.

**Note:** The backend and ML components must use compatible dependencies and model paths. The exact startup commands depend on the entry-point files and configuration in the current checkout.

---

## Testing and Validation

Testing should cover individual detection modules as well as the integrated application.

### Suggested test categories

| Test category          | Example                                                         |
| ---------------------- | --------------------------------------------------------------- |
| Email input validation | Empty or malformed email text                                   |
| Email classification   | Benign-looking text and suspicious messages                     |
| URL validation         | Invalid or incomplete URL                                       |
| URL classification     | URLs with suspicious structural characteristics                 |
| QR decoding            | Valid QR code containing text                                   |
| QR-to-URL integration  | QR code containing a URL                                        |
| Invalid image handling | Unsupported or unreadable image                                 |
| API validation         | Missing fields or unsupported input types                       |
| Frontend integration   | Verify that submitted inputs produce the expected result format |
| Error handling         | Ensure failures return understandable messages                  |

### Machine-Learning Evaluation

Model evaluation should use held-out data and appropriate classification metrics:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion matrix

Recall is particularly important in phishing detection because a false negative occurs when a malicious item is incorrectly classified as benign.

Offline training metrics should be reported separately from end-to-end application testing. High performance on a test dataset does not guarantee equivalent results on new, real-world scams.

Run the project's existing automated tests using the test instructions supplied with the ML module. Do not interpret a successful application launch as proof that every detection module has passed its tests.

---

## Security Considerations

* Treat all user-submitted content as untrusted input.
* Validate uploaded images and enforce appropriate file-size limits.
* Do not automatically open, visit, or execute QR-decoded URLs.
* Avoid storing passwords, personal emails, or other sensitive content unnecessarily.
* Keep secrets and local configuration out of version control.
* Review dataset licences and redistribution terms before sharing datasets.
* Do not commit virtual environments, temporary files, or unnecessarily large generated artifacts.
* Never rely on a single model prediction as definitive proof that content is safe.

---

## Limitations

* Machine-learning models can produce false positives and false negatives.
* Previously unseen scams may not resemble the training data.
* URL characteristics alone cannot establish the reputation or current safety of a website.
* QR decoding extracts content but does not automatically establish whether that content is malicious.
* Detection quality depends on dataset quality, preprocessing, model validation, and integration correctness.
* Live website reputation checks require appropriate external services and are not implied by lexical URL analysis alone.

---

## Future Enhancements

Potential extensions include:

* Improved model tuning and cross-validation.
* Expanded evaluation against diverse, independent datasets.
* Additional explainability and feature-level analysis.
* More comprehensive QR payload handling.
* Improved API security, logging, and error handling.
* Browser or email-client integration.
* Additional integration and regression tests.
* Deployment with secure configuration and monitoring.

---

## Disclaimer

ScamShield AI is an academic Software Engineering and Machine Learning project intended for educational and research purposes.

Its predictions are estimates, not guarantees. Users should verify suspicious messages and links through trusted channels and should not treat a benign classification as proof of safety.

---

## Author and Repository

**Project:** ScamShield AI
**Repository:** [github.com/rainzberry/ScamShield](https://github.com/rainzberry/ScamShield)

Developed as a Software Engineering project exploring multi-modal threat detection, machine learning, backend integration, and explainable risk assessment.
