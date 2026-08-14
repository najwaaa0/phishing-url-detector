import os
import argparse
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from phishing_detector.features import extract_features

def train_and_save(data_path: str, out_path: str):
    df = pd.read_csv(data_path)
    X = [extract_features(u) for u in df['url']]
    X = pd.DataFrame(X)
    y = df['label'].astype(int)

    # If dataset is very small, skip stratified split or use all data
    try:
        if len(df) < 10:
            # fit on all data for tiny datasets
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X, y)
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            clf = RandomForestClassifier(n_estimators=200, random_state=42)
            clf.fit(X_train, y_train)
    except Exception as e:
        print(f"Warning during split/train: {e}. Training on all data as fallback.")
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X, y)

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    joblib.dump(clf, out_path)
    print(f"Saved model to {out_path}")

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Train a RandomForest model from labeled URLs')
    p.add_argument('--data', required=True, help='CSV with columns url,label')
    p.add_argument('--out', default='models/phishing_model.pkl', help='Output model path')
    args = p.parse_args()
    train_and_save(args.data, args.out)