import os
import argparse
import joblib
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    roc_curve,
    auc,
    precision_recall_curve,
    confusion_matrix,
    accuracy_score,
    f1_score
)

# -----------------------------
# Argument parsing
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True, help="Path to trained model (.pkl)")
parser.add_argument("--outdir", default="reports/figs", help="Output directory")
args = parser.parse_args()

# -----------------------------
# Paths
# -----------------------------
X_TEST_PATH = "reports/X_test.npy"
Y_TEST_PATH = "reports/y_test.npy"

if not os.path.exists(X_TEST_PATH) or not os.path.exists(Y_TEST_PATH):
    raise FileNotFoundError(
        "❌ X_test.npy or y_test.npy not found. "
        "Make sure train_model.py saves them."
    )

os.makedirs(args.outdir, exist_ok=True)

# -----------------------------
# Load data & model
# -----------------------------
print(" Loading model and test data...")

model = joblib.load(args.model)
X_test = np.load(X_TEST_PATH)
y_test = np.load(Y_TEST_PATH)

# -----------------------------
# Predict probabilities
# -----------------------------
y_probs = model.predict_proba(X_test)[:, 1]

# =========================================================
# ROC CURVE
# =========================================================
fpr, tpr, _ = roc_curve(y_test, y_probs)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(6, 6))
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(args.outdir, "roc_curve.png"))
plt.close()

print(f" ROC AUC = {roc_auc:.3f}")

# =========================================================
# PRECISION–RECALL CURVE
# =========================================================
precision, recall, _ = precision_recall_curve(y_test, y_probs)

plt.figure(figsize=(6, 6))
plt.plot(recall, precision)
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision–Recall Curve")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(args.outdir, "pr_curve.png"))
plt.close()

# =========================================================
# METRICS VS THRESHOLD
# =========================================================
thresholds = np.linspace(0.01, 0.99, 50)
accuracies = []
f1_scores = []

for t in thresholds:
    y_pred = (y_probs >= t).astype(int)
    accuracies.append(accuracy_score(y_test, y_pred))
    f1_scores.append(f1_score(y_test, y_pred))

plt.figure(figsize=(7, 5))
plt.plot(thresholds, accuracies, label="Accuracy")
plt.plot(thresholds, f1_scores, label="F1-score")
plt.xlabel("Decision Threshold")
plt.ylabel("Score")
plt.title("Metrics vs Threshold")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(args.outdir, "threshold_metrics.png"))
plt.close()

# =========================================================
# CONFUSION MATRIX (default threshold = 0.5)
# =========================================================
y_pred_default = (y_probs >= 0.5).astype(int)
cm = confusion_matrix(y_test, y_pred_default)

plt.figure(figsize=(5, 4))
plt.imshow(cm, interpolation="nearest")
plt.title("Confusion Matrix (threshold = 0.5)")
plt.colorbar()
plt.xticks([0, 1], ["Benign", "Phishing"])
plt.yticks([0, 1], ["Benign", "Phishing"])

for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i, j], ha="center", va="center")

plt.xlabel("Predicted label")
plt.ylabel("True label")
plt.tight_layout()
plt.savefig(os.path.join(args.outdir, "confusion_matrix.png"))
plt.close()

print(" All diagnostic plots generated successfully!")
print(f" Saved to: {args.outdir}")
