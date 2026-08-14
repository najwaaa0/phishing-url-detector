import os, sys, re
from pathlib import Path
import argparse
from urllib.parse import urlparse, unquote
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix

# allow running from anywhere
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# optional: use any existing features if desired
# from phishing_detector.features import extract_features

sns.set(style="whitegrid")


SUSPICIOUS_WORDS = {'login', 'secure', 'update', 'verify', 'account', 'confirm', 'signin', 'bank', 'wp-admin'}


def has_ip(host: str) -> int:
    return 1 if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', host) else 0


def suspicious_count(url: str) -> int:
    u = url.lower()
    return sum(1 for w in SUSPICIOUS_WORDS if w in u)


def rule_flags(url: str):
    u = unquote(url.strip())
    if not u.startswith(('http://', 'https://')):
        u = 'https://' + u
    p = urlparse(u)
    host = p.hostname or ''
    path = p.path or ''
    flags = {}
    flags['has_ip'] = has_ip(host)
    flags['has_at'] = 1 if '@' in u else 0
    flags['suspicious_words_count'] = suspicious_count(u)
    flags['many_hyphens'] = 1 if u.count('-') > 3 else 0
    flags['long_url'] = 1 if len(u) > 75 else 0
    flags['many_subdomains'] = 1 if host.count('.') >= 3 else 0
    # binary verdict threshold: any positive flag -> phishing (you can choose threshold)
    flags['rule_score'] = (flags['has_ip'] + flags['has_at'] + flags['suspicious_words_count'] +
                           flags['many_hyphens'] + flags['long_url'] + flags['many_subdomains'])
    flags['rule_decision'] = 1 if flags['rule_score'] >= 1 else 0
    return flags


def main(args):
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.data)
    # compute rule flags
    flags = df['url'].apply(rule_flags).apply(pd.Series)
    df2 = pd.concat([df, flags], axis=1)
    # summary counts
    rule_cols = ['has_ip', 'has_at', 'many_hyphens', 'long_url', 'many_subdomains']
    # suspicious_words_count handle separately
    counts = {c: int(df2[c].sum()) for c in rule_cols}
    counts['suspicious_words_nonzero'] = int((df2['suspicious_words_count'] > 0).sum())
    counts['total'] = len(df2)

    # save CSV summary
    stats_df = pd.DataFrame.from_dict(counts, orient='index', columns=['count'])
    stats_df['percent'] = (stats_df['count'] / counts['total'] * 100).round(2)
    stats_df.to_csv(outdir / 'rule_trigger_counts.csv')

    # Bar chart: counts per rule
    plt.figure(figsize=(6,4))
    items = [('has_ip', counts['has_ip']), ('has_at', counts['has_at']),
             ('suspicious_words', counts['suspicious_words_nonzero']),
             ('many_hyphens', counts['many_hyphens']), ('long_url', counts['long_url']),
             ('many_subdomains', counts['many_subdomains'])]
    names, vals = zip(*items)
    sns.barplot(x=list(vals), y=list(names), palette='Set2')
    plt.xlabel('Count')
    plt.title('Rule triggers (count)')
    plt.tight_layout()
    plt.savefig(outdir / 'rule_trigger_counts.png', dpi=200)
    plt.close()

    # Histogram of suspicious_words_count
    plt.figure(figsize=(6,3))
    sns.histplot(df2['suspicious_words_count'], bins=range(0, max(df2['suspicious_words_count'])+2), color='#2563EB')
    plt.xlabel('Number of suspicious keywords in URL')
    plt.title('Distribution of suspicious word counts')
    plt.tight_layout()
    plt.savefig(outdir / 'suspicious_word_count_hist.png', dpi=200)
    plt.close()

    # Co-occurrence heatmap (correlation)
    # create explicit boolean column for "has suspicious word"
    df2['has_susp_word'] = (df2['suspicious_words_count'] > 0).astype(int)
    co_df = df2[['has_ip', 'has_at', 'many_hyphens', 'long_url', 'many_subdomains', 'has_susp_word']]
    corr = co_df.corr()
    plt.figure(figsize=(6,5))
    sns.heatmap(corr, annot=True, cmap='vlag', center=0)
    plt.title('Rule co-occurrence (correlation)')
    plt.tight_layout()
    plt.savefig(outdir / 'rule_cooccurrence_corr.png', dpi=200)
    plt.close()

    # Overlap (combination counts) - top combinations
    comb = co_df.astype(int).apply(lambda row: ''.join(row.astype(str)), axis=1)
    comb_counts = comb.value_counts().head(10)
    plt.figure(figsize=(6,4))
    sns.barplot(x=comb_counts.values, y=comb_counts.index, palette='magma')
    plt.xlabel('Count')
    plt.ylabel('Rule combo (has_ip, has_at, many_hyphens, long_url, many_subdomains, has_susp_word)')
    plt.title('Top rule combinations')
    plt.tight_layout()
    plt.savefig(outdir / 'rule_combinations_top.png', dpi=200)
    plt.close()

    # Rule ROC / AUC: use rule_score as continuous score
    y = df2['label'].astype(int).values
    score = df2['rule_score'].astype(float).values
    # If all labels or score are constant, skip ROC
    if len(np.unique(y)) > 1 and len(np.unique(score)) > 1:
        fpr, tpr, _ = roc_curve(y, score)
        auc = roc_auc_score(y, score)
        plt.figure(figsize=(5,4))
        plt.plot(fpr, tpr, label=f'AUC={auc:.3f}')
        plt.plot([0,1],[0,1],'--', color='gray')
        plt.xlabel('FPR'); plt.ylabel('TPR'); plt.title('Rule-based ROC')
        plt.legend()
        plt.tight_layout()
        plt.savefig(outdir / 'rule_roc.png', dpi=200)
        plt.close()
    else:
        auc = None

    # Stacked bar: actual label vs rule_decision
    cm = confusion_matrix(y, df2['rule_decision'])
    # Save confusion matrix image
    plt.figure(figsize=(4,4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Rule: Safe','Rule: Phish'], yticklabels=['True: Safe','True: Phish'])
    plt.ylabel('True label'); plt.xlabel('Rule decision')
    plt.title('Confusion matrix (rule decision vs label)')
    plt.tight_layout()
    plt.savefig(outdir / 'rule_confusion_matrix.png', dpi=200)
    plt.close()

    # Save processed dataframe with flags for audit/report
    df2.to_csv(outdir / 'dataset_rule_flags.csv', index=False)

    # Print short summary
    print("Rule trigger counts:")
    print(stats_df)
    if auc is not None:
        print(f"Rule-based AUC: {auc:.4f}")
    else:
        print("Rule-based AUC: not available (constant labels or scores)")

    print(f"Saved figures and CSV to {outdir}")

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data', required=True, help='CSV with url,label')
    p.add_argument('--outdir', default='reports/figs_rule', help='output directory for rule plots/csv')
    args = p.parse_args()
    main(args)