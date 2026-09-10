#!/usr/bin/env python3
"""
Compare two simple baselines for text classification on a small public dataset.

Baselines:
  1. Majority-class predictor (always predict the most common label)
  2. Logistic Regression with TF-IDF features

Dataset: 20newsgroups (two categories), a standard small text classification benchmark.
"""
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, classification_report
)
from sklearn.datasets import fetch_20newsgroups

# ── Load dataset ──────────────────────────────────────────────────────────────
print("Loading 20newsgroups (two categories)...")
categories = ["rec.sport.baseball", "rec.sport.hockey"]
data = fetch_20newsgroups(subset="all", categories=categories, shuffle=True, random_state=42)
X = data.data
y = data.target
class_names = data.target_names

print(f"Dataset size: {len(X)} samples")
print(f"Class distribution:")
for i, name in enumerate(class_names):
    count = np.sum(y == i)
    print(f"  {name}: {count}")

# ── Split data ────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

# ── Baseline 1: Majority-class predictor ─────────────────────────────────────
majority_class = int(np.bincount(y_train).argmax())
y_pred_majority = np.full(len(y_test), majority_class)

print("\n" + "=" * 60)
print("BASELINE 1: Majority-Class Predictor")
print("=" * 60)
print(f"Always predicts: {('positive' if majority_class == 1 else 'non-positive')}")
print(f"Accuracy:  {accuracy_score(y_test, y_pred_majority):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_majority):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred_majority):.4f}")
print(f"F1:        {f1_score(y_test, y_pred_majority):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_majority, target_names=["non-positive", "positive"]))

# ── Baseline 2: Logistic Regression with TF-IDF ───────────────────────────────
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True
)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

lr = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
lr.fit(X_train_tfidf, y_train)
y_pred_lr = lr.predict(X_test_tfidf)

print("\n" + "=" * 60)
print("BASELINE 2: Logistic Regression + TF-IDF")
print("=" * 60)
print(f"Accuracy:  {accuracy_score(y_test, y_pred_lr):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_lr):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred_lr):.4f}")
print(f"F1:        {f1_score(y_test, y_pred_lr):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_lr, target_names=["non-positive", "positive"]))

# ── Comparison ────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("COMPARISON")
print("=" * 60)
metrics = {
    "Accuracy":  accuracy_score,
    "Precision": precision_score,
    "Recall":    recall_score,
    "F1":        f1_score,
}
for name, func in metrics.items():
    score_majority = func(y_test, y_pred_majority)
    score_lr = func(y_test, y_pred_lr)
    diff = score_lr - score_majority
    print(f"{name:12s}: Majority={score_majority:.4f}  |  LR={score_lr:.4f}  |  Delta={diff:+.4f}")
