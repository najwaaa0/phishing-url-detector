import os
import argparse
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report


from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    accuracy_score,
    f1_score,
)

sns.set_theme(style="whitegrid")


# =========================
# Helpers
# =========================
def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


# =========================
# Plot functions
# =========================
def plot_confusion(y_true, y_pred, out):
    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(4, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=["Safe", "Phishing"],
        yticklabels=["Safe", "Phishing"],
    )
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()


def plot_roc_pr(y_true, y_score, roc_out, pr_out):
    # ROC
    fpr, tpr, _ = roc_curve(y_true, y_score)
    auc = roc_auc_score(y_true, y_score)

    plt.figure(figsize=(5, 4))
    plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
    plt.plot([0, 1], [0, 1], "--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(roc_out, dpi=200)
    plt.close()

    # Precision–Recall
    prec, rec, _ = precision_recall_curve(y_true, y_score)

    plt.figure(figsize=(5, 4))
    plt.plot(rec, prec)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision–Recall Curve")
    plt.tight_layout()
    plt.savefig(pr_out, dpi=200)
    plt.close()


def plot_threshold_metrics(y_true, y_score, out):
    thresholds = np.linspace(0.01, 0.99, 99)
    accs, f1s = [], []

    for t in thresholds:
        preds = (y_score >= t).astype(int)
        accs.append(accuracy_score(y_true, preds))
        f1s.append(f1_score(y_true, preds, zero_division=0))

    plt.figure(figsize=(6, 3))
    plt.plot(thresholds, accs, label="Accuracy")
    plt.plot(thresholds, f1s, label="F1-score")
    plt.xlabel("Decision Threshold")
    plt.title("Metrics vs Threshold")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()


# =========================
# Main
# =========================
def main(args):
    ensure_dir(args.outdir)

    # Load saved test split
    X_test = np.load("reports/X_test.npy")
    y_test = np.load("reports/y_test.npy")

    model = joblib.load(args.model)

    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, "decision_function"):
        y_score = model.decision_function(X_test)
    else:
        raise RuntimeError("Model does not support probability output")

    y_pred = (y_score >= 0.5).astype(int)


    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred))

    print("✅ Model saved to models/phishing_model.pkl")


    plot_confusion(
        y_test,
        y_pred,
        os.path.join(args.outdir, "confusion_matrix.png"),
    )

    plot_roc_pr(
        y_test,
        y_score,
        os.path.join(args.outdir, "roc_curve.png"),
        os.path.join(args.outdir, "pr_curve.png"),
    )

    plot_threshold_metrics(
        y_test,
        y_score,
        os.path.join(args.outdir, "threshold_metrics.png"),
    )

    print(f"✅ Diagnostics saved to {args.outdir}")


# =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/phishing_model.pkl")
    parser.add_argument("--outdir", default="reports/figs")
    main(parser.parse_args())
