# Phishing URL Detector

## Overview

Phishing URL Detector is a Flask web application that checks a submitted URL and returns a simple verdict: `Safe` or `Phishing/Not Safe`.

The application can use a trained scikit-learn model when `models/phishing_model.pkl` exists. If the model file is missing or cannot be loaded, the app continues to work by using its existing rule-based fallback.

## Key Features

- Web interface for submitting a URL.
- `/check_url` route with GET and POST support.
- URL feature extraction for model-based prediction.
- Random Forest training script for labeled URL datasets.
- Rule-based fallback detection when no trained model is available.
- Basic pytest coverage for the implemented Flask routes and feature extractor.
- Optional diagnostic scripts for plots and report artifacts.

## Machine Learning

The training pipeline in `scripts/train_model_clean.py` uses a scikit-learn `RandomForestClassifier`.

Feature extraction is implemented in `phishing_detector/features.py` and currently uses:

- URL length.
- Number of digits in the URL.
- Number of non-alphanumeric characters.
- Count of suspicious words: `login`, `secure`, `account`, `update`, `verify`.

The expected training dataset format is a CSV file with:

- `url`: URL string.
- `label`: `0` for safe and `1` for phishing.

Prediction flow:

1. `app.py` tries to load `models/phishing_model.pkl`.
2. If the model loads, the app extracts URL features and calls the model.
3. If the model is unavailable or prediction fails, the app uses the rule-based fallback in `app.py`.

## Technologies

- Python
- Flask
- scikit-learn
- pandas
- NumPy
- joblib
- matplotlib
- seaborn
- python-docx
- HTML/CSS
- pytest

## Project Structure

```text
phishing-url-detector/
├── app.py
├── phishing_detector/
│   ├── __init__.py
│   ├── features.py
│   ├── model.py
│   └── utils.py
├── scripts/
│   ├── generate_final_report_docx.py
│   ├── plot_diagnostics.py
│   ├── plot_rule_based.py
│   └── train_model_clean.py
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── index.html
│   └── result.html
├── tests/
│   ├── test_app.py
│   └── test_features.py
├── train_model.py
├── requirements.txt
├── .gitignore
└── README.md
```

Generated files such as `.venv/`, Python caches, `reports/`, and `models/phishing_model.pkl` are excluded from version control.

## Installation

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Train the Model

The trained model file is not committed because it is large. Generate it locally from a labeled dataset:

```bash
python scripts/train_model_clean.py --data path/to/your_dataset.csv --out models/phishing_model.pkl
```

The script creates the `models/` directory if needed and saves the trained Random Forest model there.

## Run the Flask Application

```bash
python app.py
```

Open the app at:

```text
http://127.0.0.1:5000/
```

You can also test a URL from the command line:

```bash
curl "http://127.0.0.1:5000/check_url?url=https://example.com"
```

## Run Tests

```bash
pytest -q
```

Run a Python syntax check with:

```bash
python -m compileall app.py phishing_detector scripts tests
```

## Dataset

The original local training dataset is not included in the public repository. URL datasets can contain sensitive-looking query strings, tokens, or email addresses, so dataset files are ignored by default.

To reproduce training, provide your own CSV with the same columns:

```bash
python scripts/train_model_clean.py --data path/to/your_dataset.csv --out models/phishing_model.pkl
```

## Project Work

This project implements a Flask-based phishing URL detection application with:

- URL feature extraction.
- Random Forest machine learning classification.
- Rule-based fallback detection.
- Model training and prediction workflow.
- Flask web interface.
- Automated tests for core functionality.

## Limitations

- Feature extraction uses simple URL string characteristics.
- The app does not perform live WHOIS, DNS, browser inspection, or domain reputation checks.
- The rule-based fallback can produce false positives or false negatives.
- The model quality depends on the dataset used for training.
- The result is an educational signal, not a complete security decision.

## Future Improvements

- Add richer URL parsing features such as hostname entropy and path depth.
- Save evaluation metrics during training.
- Add cross-validation and clearer dataset provenance.
- Add a JSON API endpoint for programmatic usage.
- Add CI for automated testing.

## Author

Najwa Aouaj
