#!/usr/bin/env python3
"""
Inverted Disagreement Asymmetry Experiment for Sentiment Classification.

Tests whether the direction of disagreement between dissimilar classifiers
(LR vs RF, NB vs SVM) systematically predicts which model is correct.

Hypothesis (INVERTED rule):
  - Trust the SIMPLER model (LR/NB) when it predicts the MINORITY class
  - Trust the MORE COMPLEX model (RF/SVM) when it predicts the MAJORITY class

Baselines:
  1. Random guessing (50%)
  2. Calibrated confidence-based selection
  3. Always trust the more accurate model on disagreement set
  4. Majority-class prior
  5. ORIGINAL directional rule (opposite of inverted)
"""

from loguru import logger
from pathlib import Path
import json
import sys
import math
import gc
import resource
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

import numpy as np
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelBinarizer

# ── Logging ──────────────────────────────────────────────────────────────────
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

# ── Hardware Detection ───────────────────────────────────────────────────────
def _detect_cpus() -> int:
    try:
        parts = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if parts[0] != "max":
            return math.ceil(int(parts[0]) / int(parts[1]))
    except (FileNotFoundError, ValueError):
        pass
    try:
        q = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        p = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        if q > 0:
            return math.ceil(q / p)
    except (FileNotFoundError, ValueError):
        pass
    try:
        return len(__import__('os').sched_getaffinity(0))
    except (AttributeError, OSError):
        pass
    return __import__('os').cpu_count() or 1

NUM_CPUS = _detect_cpus()
logger.info(f"Detected {NUM_CPUS} CPUs")

# Set memory limit: 14 GB container, use 12 GB
RAM_BUDGET_BYTES = 12 * 1024**3
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET_BYTES * 3, RAM_BUDGET_BYTES * 3))

# ── Constants ────────────────────────────────────────────────────────────────
DATA_PATH = Path("/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_1/gen_art/gen_art_dataset_1/full_data_out.json")
OUTPUT_PATH = Path("method_out.json")
SUMMARY_PATH = Path("summary_results.json")
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

SAMPLE_SIZES = [100, 200, 500, 1000]
IMBALANCE_RATIOS = [1.0, 1.5, 2.0]
SEEDS = list(range(10))  # 10 seeds
MODEL_PAIRS = ["lr_vs_rf", "nb_vs_svm"]

# Simple vs complex mapping
SIMPLE_MODEL = {"lr_vs_rf": "lr", "nb_vs_svm": "nb"}
COMPLEX_MODEL = {"lr_vs_rf": "rf", "nb_vs_svm": "svm"}


# ── Data Loading ─────────────────────────────────────────────────────────────
@logger.catch(reraise=True)
def load_datasets(data_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load datasets from the full_data_out.json file."""
    logger.info(f"Loading data from {data_path}")
    with open(data_path, "r") as f:
        raw = json.load(f)

    datasets: Dict[str, List[Dict[str, Any]]] = {}
    for ds in raw["datasets"]:
        name = ds["dataset"]
        examples = ds["examples"]
        datasets[name] = examples
        logger.info(f"  {name}: {len(examples)} examples")

    logger.info(f"Loaded {len(datasets)} datasets, {sum(len(v) for v in datasets.values())} total examples")
    return datasets


def create_imbalanced_split(
    texts: List[str],
    labels: List[int],
    sample_size: int,
    imbalance_ratio: float,
    seed: int,
) -> Tuple[List[str], List[int]]:
    """
    Create a subsample with a given class imbalance ratio.

    imbalance_ratio = majority_count / minority_count
    For ratio 1.0: balanced (50/50)
    For ratio 2.0: 67% majority, 33% minority
    """
    rng = np.random.RandomState(seed)

    class_0_idx = [i for i, l in enumerate(labels) if l == 0]
    class_1_idx = [i for i, l in enumerate(labels) if l == 1]

    # Determine which is majority
    if len(class_0_idx) >= len(class_1_idx):
        majority_idx, minority_idx = class_0_idx, class_1_idx
    else:
        majority_idx, minority_idx = class_1_idx, class_0_idx

    # Calculate target counts
    # total = majority + minority, and majority / minority = ratio
    # So: majority = ratio * minority, total = (ratio + 1) * minority
    # minority = total / (ratio + 1), majority = total * ratio / (ratio + 1)
    target_minority = max(1, int(round(sample_size / (imbalance_ratio + 1.0))))
    target_majority = max(1, sample_size - target_minority)

    # Cap at available
    target_minority = min(target_minority, len(minority_idx))
    target_majority = min(target_majority, len(majority_idx))

    # Sample
    sampled_minority = rng.choice(minority_idx, size=target_minority, replace=False).tolist()
    sampled_majority = rng.choice(majority_idx, size=target_majority, replace=False).tolist()

    sampled_idx = sampled_minority + sampled_majority
    rng.shuffle(sampled_idx)

    sampled_texts = [texts[i] for i in sampled_idx]
    sampled_labels = [labels[i] for i in sampled_idx]

    return sampled_texts, sampled_labels


def build_tfidf(texts: List[str]) -> Tuple[Any, Any]:
    """Build and fit a single TF-IDF vectorizer on the training texts."""
    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        max_features=5000,
        min_df=2,
        sublinear_tf=True,
        dtype=np.float32,
    )
    X = vectorizer.fit_transform(texts)
    return vectorizer, X


# ── Model Training ───────────────────────────────────────────────────────────
def train_lr(X_train, y_train):
    model = LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs", random_state=42)
    model.fit(X_train, y_train)
    return model


def train_rf(X_train, y_train, seed: int):
    model = RandomForestClassifier(
        n_estimators=100, max_depth=None, random_state=seed, n_jobs=1
    )
    model.fit(X_train, y_train)
    return model


def train_nb(X_train, y_train):
    # MultinomialNB requires non-negative features
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train, y_train)
    return model


def train_svm(X_train, y_train):
    model = LinearSVC(C=1.0, max_iter=1000, dual="auto", random_state=42)
    model.fit(X_train, y_train)
    return model


def calibrate_model(model, X_train, y_train, X_val, y_val):
    """
    Calibrate model using Platt scaling.
    
    In sklearn >= 1.4, cv='prefit' was removed.
    We use a custom CV splitter that yields the specific train/val split.
    """
    try:
        from sklearn.model_selection import BaseCrossValidator
    except ImportError:
        from sklearn.model_selection import _BaseCrossValidator as BaseCrossValidator

    try:
        # Combine train and val for the calibration
        from scipy.sparse import vstack as sparse_vstack
        if hasattr(X_train, 'nnz'):
            X_all = sparse_vstack([X_train, X_val])
        else:
            X_all = np.vstack([X_train, X_val])
        y_all = np.concatenate([y_train, y_val])
        
        # Use a custom splitter that uses train for fitting and val for calibration
        n_train = len(y_train)
        n_val = len(y_val)
        
        class CustomPreFitCV(BaseCrossValidator):
            def split(self, X, y=None, groups=None):
                yield (np.arange(n_train), np.arange(n_train, n_train + n_val))
            
            def get_n_splits(self, X=None, y=None, groups=None):
                return 1
        
        calibrated = CalibratedClassifierCV(
            model, method="sigmoid", cv=CustomPreFitCV()
        )
        calibrated.fit(X_all, y_all)
        return calibrated
    except Exception:
        logger.warning("Calibration failed, returning raw model")
        return model


# ── Disagreement Analysis ────────────────────────────────────────────────────
def analyze_disagreements(
    model_a, model_b,
    X_test, y_test,
    texts_test,
    model_a_name: str,
    model_b_name: str,
    model_pair: str,
    dataset_name: str,
    sample_size: int,
    imbalance_ratio: float,
    seed: int,
    fold: int,
    majority_class: int,
    minority_class: int,
) -> List[Dict[str, Any]]:
    """Analyze disagreements between two models and apply the inverted rule."""

    pred_a = model_a.predict(X_test)
    pred_b = model_b.predict(X_test)

    # Get probabilities
    try:
        prob_a = model_a.predict_proba(X_test)
        prob_a_max = np.max(prob_a, axis=1)
        prob_a_pred = prob_a[np.arange(len(pred_a)), pred_a]
    except Exception:
        prob_a_max = np.zeros(len(pred_a))
        prob_a_pred = np.zeros(len(pred_a))

    try:
        prob_b = model_b.predict_proba(X_test)
        prob_b_max = np.max(prob_b, axis=1)
        prob_b_pred = prob_b[np.arange(len(pred_b)), pred_b]
    except Exception:
        prob_b_max = np.zeros(len(pred_b))
        prob_b_pred = np.zeros(len(pred_b))

    # Find disagreements
    disagree_mask = pred_a != pred_b
    disagree_indices = np.where(disagree_mask)[0]

    if len(disagree_indices) == 0:
        return []

    # Determine which is simple vs complex
    simple_name = SIMPLE_MODEL[model_pair]
    complex_name = COMPLEX_MODEL[model_pair]

    is_a_simple = (model_a_name == simple_name)
    is_b_simple = (model_b_name == simple_name)

    # Model accuracies on disagreement subset
    acc_a_disagree = accuracy_score(y_test[disagree_mask], pred_a[disagree_mask])
    acc_b_disagree = accuracy_score(y_test[disagree_mask], pred_b[disagree_mask])

    # Majority class prior on disagreement set
    majority_count_disagree = np.sum(y_test[disagree_mask] == majority_class)
    majority_prior_acc = majority_count_disagree / len(disagree_mask) if len(disagree_mask) > 0 else 0.5

    results = []
    for idx in disagree_indices:
        i = int(idx)  # Convert numpy int to Python int for list indexing
        true_label = int(y_test[i])
        pa = int(pred_a[i])
        pb = int(pred_b[i])
        pa_prob = float(prob_a_pred[i])
        pb_prob = float(prob_b_pred[i])

        # Determine who is simple/complex
        if is_a_simple:
            simple_pred = pa
            complex_pred = pb
            simple_prob = pa_prob
            complex_prob = pb_prob
        else:
            simple_pred = pb
            complex_pred = pa
            simple_prob = pb_prob
            complex_prob = pa_prob

        # INVERTED rule:
        # Trust simple when it predicts MINORITY class
        # Trust complex when it predicts MAJORITY class
        if simple_pred == minority_class:
            inverted_pred = simple_pred
            disagree_type = "simple_says_minority"
        elif complex_pred == majority_class:
            inverted_pred = complex_pred
            disagree_type = "complex_says_majority"
        elif simple_pred == majority_class:
            # Simple says majority -> trust complex (which must say minority)
            inverted_pred = complex_pred
            disagree_type = "simple_says_majority"
        else:
            # Complex says minority -> trust simple (which must say majority)
            inverted_pred = simple_pred
            disagree_type = "complex_says_minority"

        # ORIGINAL rule (opposite of inverted):
        # Trust simple when it predicts MAJORITY class
        # Trust complex when it predicts MINORITY class
        if simple_pred == majority_class:
            original_pred = simple_pred
        elif complex_pred == minority_class:
            original_pred = complex_pred
        elif simple_pred == minority_class:
            original_pred = complex_pred
        else:
            original_pred = simple_pred

        # Confidence-based: choose model with higher calibrated probability
        if pa_prob >= pb_prob:
            confidence_pred = pa
        else:
            confidence_pred = pb

        # Always trust more accurate model on disagreement set
        if acc_a_disagree >= acc_b_disagree:
            always_accurate_pred = pa
        else:
            always_accurate_pred = pb

        # Majority prior
        majority_pred = majority_class

        # Check correctness
        inverted_correct = (inverted_pred == true_label)
        original_correct = (original_pred == true_label)
        confidence_correct = (confidence_pred == true_label)
        always_accurate_correct = (always_accurate_pred == true_label)
        majority_correct = (majority_pred == true_label)

        example = {
            "input": texts_test[i] if i < len(texts_test) else "",
            "output": str(true_label),
            "metadata_fold": int(fold),
            "metadata_sample_size": int(sample_size),
            "metadata_imbalance_ratio": float(imbalance_ratio),
            "metadata_seed": int(seed),
            "metadata_model_pair": model_pair,
            "metadata_dataset": dataset_name,
            "metadata_majority_class": str(majority_class),
            "metadata_minority_class": str(minority_class),
            "metadata_disagreement_type": disagree_type,
            "metadata_acc_a_disagree": f"{acc_a_disagree:.4f}",
            "metadata_acc_b_disagree": f"{acc_b_disagree:.4f}",
            "metadata_majority_prior_acc": f"{majority_prior_acc:.4f}",
            "predict_model_a": str(pa),
            "predict_model_b": str(pb),
            "predict_inverted_rule": str(inverted_pred),
            "predict_original_rule": str(original_pred),
            "predict_confidence_based": str(confidence_pred),
            "predict_always_accurate": str(always_accurate_pred),
            "predict_majority_prior": str(majority_pred),
            "predict_correct": str(inverted_correct),
            "metadata_model_a_prob": f"{pa_prob:.4f}",
            "metadata_model_b_prob": f"{pb_prob:.4f}",
            "metadata_simple_pred": str(simple_pred),
            "metadata_complex_pred": str(complex_pred),
        }
        results.append(example)

    return results


# ── Single Configuration Runner ──────────────────────────────────────────────
def run_single_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single configuration: one dataset, sample size, imbalance, seed, model pair.
    This function is designed to run in a separate process.
    """
    dataset_name = config["dataset_name"]
    sample_size = config["sample_size"]
    imbalance_ratio = config["imbalance_ratio"]
    seed = config["seed"]
    model_pair = config["model_pair"]
    all_texts = config["all_texts"]
    all_labels = config["all_labels"]
    fold = config.get("fold", 0)

    try:
        # Create imbalanced subsample
        sampled_texts, sampled_labels = create_imbalanced_split(
            all_texts, all_labels, sample_size, imbalance_ratio, seed
        )

        if len(sampled_texts) < 10:
            return {"status": "skipped", "reason": "too_few_samples", "config": config}

        # Determine majority/minority class
        label_counts = np.bincount(sampled_labels)
        majority_class = int(np.argmax(label_counts))
        minority_class = int(np.argmin(label_counts))

        # Split: 60% train, 20% val, 20% test
        train_texts, temp_texts, y_train, y_temp = train_test_split(
            sampled_texts, sampled_labels,
            test_size=0.4, random_state=seed, stratify=sampled_labels
        )
        val_texts, test_texts, y_val, y_test = train_test_split(
            temp_texts, y_temp,
            test_size=0.5, random_state=seed, stratify=y_temp
        )

        # Convert labels to numpy arrays for indexing
        y_train = np.array(y_train)
        y_val = np.array(y_val)
        y_test = np.array(y_test)

        # Build single TF-IDF vectorizer (fit on train only)
        vectorizer, X_train = build_tfidf(train_texts)
        X_val = vectorizer.transform(val_texts)
        X_test = vectorizer.transform(test_texts)

        # Train models based on pair
        if model_pair == "lr_vs_rf":
            model_a = train_lr(X_train, y_train)
            model_b = train_rf(X_train, y_test if False else y_train, seed)
            model_a_name = "lr"
            model_b_name = "rf"
        elif model_pair == "nb_vs_svm":
            model_a = train_nb(X_train, y_train)
            model_b = train_svm(X_train, y_train)
            model_a_name = "nb"
            model_b_name = "svm"
        else:
            return {"status": "error", "reason": f"unknown model pair: {model_pair}"}

        # Calibrate
        try:
            model_a_cal = calibrate_model(model_a, X_train, y_train, X_val, y_val)
            model_b_cal = calibrate_model(model_b, X_train, y_train, X_val, y_val)
        except Exception:
            model_a_cal = model_a
            model_b_cal = model_b

        # Analyze disagreements
        results = analyze_disagreements(
            model_a_cal, model_b_cal,
            X_test, y_test,
            test_texts,
            model_a_name, model_b_name,
            model_pair, dataset_name,
            sample_size, imbalance_ratio,
            seed, fold,
            majority_class, minority_class,
        )

        # Compute aggregate stats for this config
        if len(results) > 0:
            inverted_correct = sum(1 for r in results if r["predict_correct"] == "True")
            inverted_acc = inverted_correct / len(results)

            original_correct = sum(1 for r in results if int(r["predict_original_rule"]) == int(r["output"]))
            original_acc = original_correct / len(results)

            confidence_correct = sum(1 for r in results if int(r["predict_confidence_based"]) == int(r["output"]))
            confidence_acc = confidence_correct / len(results)

            always_accurate_correct = sum(1 for r in results if int(r["predict_always_accurate"]) == int(r["output"]))
            always_accurate_acc = always_accurate_correct / len(results)

            majority_correct = sum(1 for r in results if int(r["predict_majority_prior"]) == int(r["output"]))
            majority_acc = majority_correct / len(results)

            # Binomial test: inverted rule vs majority prior
            if majority_acc > 0 and majority_acc < 1:
                try:
                    binom_result = stats.binomtest(
                        inverted_correct, len(results), p=majority_acc, alternative="greater"
                    )
                    p_value = binom_result.pvalue
                except Exception:
                    p_value = 1.0
            else:
                p_value = 1.0

            stats_dict = {
                "num_disagreements": len(results),
                "inverted_rule_acc": float(inverted_acc),
                "original_rule_acc": float(original_acc),
                "confidence_based_acc": float(confidence_acc),
                "always_accurate_acc": float(always_accurate_acc),
                "majority_prior_acc": float(majority_acc),
                "binomial_p_value": float(p_value),
                "majority_class": majority_class,
                "minority_class": minority_class,
                "actual_imbalance_ratio": float(label_counts[majority_class] / max(label_counts[minority_class], 1)),
            }
        else:
            stats_dict = {
                "num_disagreements": 0,
                "inverted_rule_acc": 0.0,
                "original_rule_acc": 0.0,
                "confidence_based_acc": 0.0,
                "always_accurate_acc": 0.0,
                "majority_prior_acc": 0.0,
                "binomial_p_value": 1.0,
                "majority_class": majority_class,
                "minority_class": minority_class,
                "actual_imbalance_ratio": float(label_counts[majority_class] / max(label_counts[minority_class], 1)),
            }

        return {
            "status": "success",
            "config": config,
            "stats": stats_dict,
            "examples": results,
        }

    except Exception as e:
        logger.error(f"Config failed: {config} -> {e}")
        return {
            "status": "error",
            "config": config,
            "error": str(e),
            "stats": {},
            "examples": [],
        }


# ── Main Pipeline ────────────────────────────────────────────────────────────
@logger.catch(reraise=True)
def main():
    logger.info("=" * 80)
    logger.info("INVERTED DISAGREEMENT ASYMMETRY EXPERIMENT")
    logger.info("=" * 80)

    # ── Phase 1: Load Data ───────────────────────────────────────────────────
    datasets = load_datasets(DATA_PATH)
    dataset_names = list(datasets.keys())
    logger.info(f"Datasets: {dataset_names}")

    # Prepare text/label arrays for each dataset
    data_arrays: Dict[str, Tuple[List[str], List[int]]] = {}
    for ds_name in dataset_names:
        texts = [ex["input"] for ex in datasets[ds_name]]
        labels = [int(ex["output"]) for ex in datasets[ds_name]]
        data_arrays[ds_name] = (texts, labels)
        logger.info(f"  {ds_name}: {len(texts)} samples, class balance: {np.bincount(labels)}")

    # ── Phase 2: Build Configuration Grid ────────────────────────────────────
    configs = []
    for ds_name in dataset_names:
        for ss in SAMPLE_SIZES:
            for ir in IMBALANCE_RATIOS:
                for seed in SEEDS:
                    for mp_name in MODEL_PAIRS:
                        # Check if dataset has enough samples
                        total_samples = len(data_arrays[ds_name][0])
                        if total_samples < ss:
                            continue
                        configs.append({
                            "dataset_name": ds_name,
                            "sample_size": ss,
                            "imbalance_ratio": ir,
                            "seed": seed,
                            "model_pair": mp_name,
                            "all_texts": data_arrays[ds_name][0],
                            "all_labels": data_arrays[ds_name][1],
                            "fold": 0,
                        })

    logger.info(f"Total configurations: {len(configs)}")

    # ── Phase 3: Gradual Scaling ─────────────────────────────────────────────
    # Step 1: Run 1 config as smoke test
    logger.info("STEP 1: Smoke test with 1 configuration")
    test_config = configs[0].copy()
    test_result = run_single_config(test_config)
    logger.info(f"Smoke test result: {test_result['status']}")
    if test_result["status"] != "success":
        logger.error(f"Smoke test failed: {test_result}")
        # Still continue - might be data issue

    # Step 2: Run 5 configs to estimate runtime
    logger.info("STEP 2: Runtime estimation with 5 configurations")
    import time
    start_time = time.time()
    small_batch = configs[1:6]
    small_results = []
    for cfg in small_batch:
        r = run_single_config(cfg)
        small_results.append(r)
    elapsed_5 = time.time() - start_time
    logger.info(f"5 configs took {elapsed_5:.1f}s, est. per config: {elapsed_5/5:.1f}s")

    estimated_total = elapsed_5 / 5 * len(configs)
    logger.info(f"Estimated total time: {estimated_total/60:.1f} minutes")

    # Step 3: Run remaining configs in parallel
    remaining_configs = configs[6:]
    if len(remaining_configs) > 0:
        logger.info(f"STEP 3: Running {len(remaining_configs)} remaining configs in parallel ({NUM_CPUS} workers)")

        all_results = small_results[:]
        completed = 0
        total_remaining = len(remaining_configs)

        with ProcessPoolExecutor(
            max_workers=min(NUM_CPUS, len(remaining_configs)),
            mp_context=mp.get_context("spawn")
        ) as pool:
            futures = {pool.submit(run_single_config, cfg): cfg for cfg in remaining_configs}
            for future in as_completed(futures):
                completed += 1
                result = future.result()
                all_results.append(result)
                if completed % 50 == 0 or completed == total_remaining:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 1
                    eta = (total_remaining - completed) / rate if rate > 0 else 0
                    logger.info(
                        f"Progress: {completed}/{total_remaining} "
                        f"({completed/total_remaining*100:.1f}%), "
                        f"ETA: {eta/60:.1f} min"
                    )
                gc.collect()
    else:
        all_results = small_results

    logger.info(f"All {len(all_results)} configurations completed")

    # ── Phase 4: Aggregate Results ───────────────────────────────────────────
    logger.info("Aggregating results...")

    successful = [r for r in all_results if r["status"] == "success"]
    failed = [r for r in all_results if r["status"] == "error"]
    skipped = [r for r in all_results if r["status"] == "skipped"]

    logger.info(f"Successful: {len(successful)}, Failed: {len(failed)}, Skipped: {len(skipped)}")

    # Collect all examples by dataset
    examples_by_dataset: Dict[str, List[Dict]] = {}
    for result in successful:
        ds_name = result["config"]["dataset_name"]
        if ds_name not in examples_by_dataset:
            examples_by_dataset[ds_name] = []
        examples_by_dataset[ds_name].extend(result["examples"])

    # Build output JSON
    output_datasets = []
    for ds_name in dataset_names:
        if ds_name in examples_by_dataset and len(examples_by_dataset[ds_name]) > 0:
            output_datasets.append({
                "dataset": ds_name,
                "examples": examples_by_dataset[ds_name],
            })

    # Compute summary statistics
    all_stats = []
    for result in successful:
        if result["stats"]:
            s = result["stats"].copy()
            s["dataset"] = result["config"]["dataset_name"]
            s["sample_size"] = result["config"]["sample_size"]
            s["imbalance_ratio"] = result["config"]["imbalance_ratio"]
            s["seed"] = result["config"]["seed"]
            s["model_pair"] = result["config"]["model_pair"]
            all_stats.append(s)

    # Aggregate across all configs
    if len(all_stats) > 0:
        stats_arr = np.array([s["inverted_rule_acc"] for s in all_stats if s["num_disagreements"] > 0])
        original_arr = np.array([s["original_rule_acc"] for s in all_stats if s["num_disagreements"] > 0])
        confidence_arr = np.array([s["confidence_based_acc"] for s in all_stats if s["num_disagreements"] > 0])
        always_acc_arr = np.array([s["always_accurate_acc"] for s in all_stats if s["num_disagreements"] > 0])
        majority_arr = np.array([s["majority_prior_acc"] for s in all_stats if s["num_disagreements"] > 0])
        p_values = np.array([s["binomial_p_value"] for s in all_stats if s["num_disagreements"] > 0])

        # Benjamini-Hochberg correction
        if len(p_values) > 0:
            sorted_idx = np.argsort(p_values)
            sorted_p = p_values[sorted_idx]
            n_tests = len(sorted_p)
            bh_thresholds = np.arange(1, n_tests + 1) / n_tests * 0.05
            significant = sorted_p <= bh_thresholds
            adjusted_p = np.minimum.accumulate(sorted_p * n_tests / np.arange(1, n_tests + 1))
            adjusted_p = np.minimum(adjusted_p, 1.0)
            # Reorder back
            final_adjusted_p = np.zeros(n_tests)
            final_adjusted_p[sorted_idx] = adjusted_p
        else:
            final_adjusted_p = np.array([])

        summary = {
            "total_configs": len(all_stats),
            "configs_with_disagreements": int(len(stats_arr)),
            "mean_inverted_rule_acc": float(np.mean(stats_arr)) if len(stats_arr) > 0 else 0.0,
            "std_inverted_rule_acc": float(np.std(stats_arr)) if len(stats_arr) > 0 else 0.0,
            "mean_original_rule_acc": float(np.mean(original_arr)) if len(original_arr) > 0 else 0.0,
            "mean_confidence_based_acc": float(np.mean(confidence_arr)) if len(confidence_arr) > 0 else 0.0,
            "mean_always_accurate_acc": float(np.mean(always_acc_arr)) if len(always_acc_arr) > 0 else 0.0,
            "mean_majority_prior_acc": float(np.mean(majority_arr)) if len(majority_arr) > 0 else 0.0,
            "mean_raw_p_value": float(np.mean(p_values)) if len(p_values) > 0 else 1.0,
            "frac_significant_raw": float(np.mean(p_values < 0.05)) if len(p_values) > 0 else 0.0,
            "frac_significant_bh": float(np.mean(final_adjusted_p < 0.05)) if len(final_adjusted_p) > 0 else 0.0,
            "mean_num_disagreements": float(np.mean([s["num_disagreements"] for s in all_stats])),
        }

        # Per-dataset breakdown
        per_dataset = {}
        for ds_name in dataset_names:
            ds_stats = [s for s in all_stats if s["dataset"] == ds_name and s["num_disagreements"] > 0]
            if len(ds_stats) > 0:
                per_dataset[ds_name] = {
                    "mean_inverted_acc": float(np.mean([s["inverted_rule_acc"] for s in ds_stats])),
                    "mean_original_acc": float(np.mean([s["original_rule_acc"] for s in ds_stats])),
                    "mean_confidence_acc": float(np.mean([s["confidence_based_acc"] for s in ds_stats])),
                    "num_configs": len(ds_stats),
                }

        # Per-model-pair breakdown
        per_model_pair = {}
        for mp_name in MODEL_PAIRS:
            mp_stats = [s for s in all_stats if s["model_pair"] == mp_name and s["num_disagreements"] > 0]
            if len(mp_stats) > 0:
                per_model_pair[mp_name] = {
                    "mean_inverted_acc": float(np.mean([s["inverted_rule_acc"] for s in mp_stats])),
                    "mean_original_acc": float(np.mean([s["original_rule_acc"] for s in mp_stats])),
                    "mean_confidence_acc": float(np.mean([s["confidence_based_acc"] for s in mp_stats])),
                    "num_configs": len(mp_stats),
                }

        # Per-sample-size breakdown
        per_sample_size = {}
        for ss in SAMPLE_SIZES:
            ss_stats = [s for s in all_stats if s["sample_size"] == ss and s["num_disagreements"] > 0]
            if len(ss_stats) > 0:
                per_sample_size[str(ss)] = {
                    "mean_inverted_acc": float(np.mean([s["inverted_rule_acc"] for s in ss_stats])),
                    "mean_original_acc": float(np.mean([s["original_rule_acc"] for s in ss_stats])),
                    "num_configs": len(ss_stats),
                }

        # Per-imbalance breakdown
        per_imbalance = {}
        for ir in IMBALANCE_RATIOS:
            ir_stats = [s for s in all_stats if s["imbalance_ratio"] == ir and s["num_disagreements"] > 0]
            if len(ir_stats) > 0:
                per_imbalance[str(ir)] = {
                    "mean_inverted_acc": float(np.mean([s["inverted_rule_acc"] for s in ir_stats])),
                    "mean_original_acc": float(np.mean([s["original_rule_acc"] for s in ir_stats])),
                    "num_configs": len(ir_stats),
                }

        summary["per_dataset"] = per_dataset
        summary["per_model_pair"] = per_model_pair
        summary["per_sample_size"] = per_sample_size
        summary["per_imbalance_ratio"] = per_imbalance

        # Correlation analysis
        if len(all_stats) > 10:
            imbalance_vals = np.array([s["actual_imbalance_ratio"] for s in all_stats])
            inverted_vals = np.array([s["inverted_rule_acc"] for s in all_stats])
            try:
                corr_imbalance_inverted, p_corr = stats.pearsonr(imbalance_vals, inverted_vals)
                summary["correlation_imbalance_vs_inverted_acc"] = float(corr_imbalance_inverted)
                summary["correlation_p_value"] = float(p_corr)
            except Exception:
                pass

            sample_size_vals = np.array([s["sample_size"] for s in all_stats])
            try:
                corr_size_inverted, p_corr2 = stats.pearsonr(sample_size_vals, inverted_vals)
                summary["correlation_sample_size_vs_inverted_acc"] = float(corr_size_inverted)
                summary["correlation_size_p_value"] = float(p_corr2)
            except Exception:
                pass

    else:
        summary = {"error": "No successful configurations with disagreements"}

    # ── Phase 5: Write Output ────────────────────────────────────────────────
    output = {
        "metadata": {
            "method_name": "inverted_disagreement_asymmetry_oracle",
            "description": "Testing inverted disagreement asymmetry hypothesis: trust simpler model when it predicts minority class, trust complex model when it predicts majority class",
            "parameters": {
                "sample_sizes": SAMPLE_SIZES,
                "imbalance_ratios": IMBALANCE_RATIOS,
                "seeds": SEEDS,
                "model_pairs": MODEL_PAIRS,
            },
            "datasets": dataset_names,
            "total_configs": len(configs),
            "successful_configs": len(successful),
            "failed_configs": len(failed),
        },
        "datasets": output_datasets,
    }

    logger.info(f"Writing output to {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Writing summary to {SUMMARY_PATH}")
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    # Log summary
    logger.info("=" * 80)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("=" * 80)
    for k, v in summary.items():
        if not isinstance(v, dict):
            logger.info(f"  {k}: {v}")
    logger.info("=" * 80)

    # Free memory
    del datasets, data_arrays, all_results, all_stats
    gc.collect()

    logger.info("Experiment complete!")


if __name__ == "__main__":
    main()
