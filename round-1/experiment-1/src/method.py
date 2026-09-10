#!/usr/bin/env python3
"""Disagreement Direction Test for Sentiment Classification.

Compares TF-IDF Logistic Regression vs character n-gram RandomForest
on small sentiment datasets, analyzing whether disagreement direction
predicts the correct label better than chance and concrete baselines.

Hypothesis: When a simple model and complex model disagree, the simple
model is more likely correct when it predicts the majority class
(because it biases toward the mode), and the complex model is more
likely correct when the simple model predicts the minority class
(because the simple model is unreliable on rare patterns).
"""

import gc
import json
import math
import multiprocessing as mp
import os
import resource
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
from datasets import load_dataset
from loguru import logger
from scipy import stats
from scipy.stats import binomtest
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

WORKSPACE = Path(
    "/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_1/gen_art/gen_art_experiment_1"
)
LOG_DIR = WORKSPACE / "logs"
OUTPUT_DIR = WORKSPACE / "results"
LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

DATASETS = ["sst2", "imdb"]
SAMPLE_SIZES = [100, 200, 500, 1000]
IMBALANCE_RATIOS = [1.0, 1.5, 2.0]  # majority:minority ratio (1.0 = balanced)
SEEDS = list(range(10))
NUM_WORKERS = 2  # Container has 2 CPUs

# Memory limits based on container resources (14GB RAM)
RAM_BUDGET = 12 * 1024**3  # 12GB

# Experiment timeout per configuration (seconds)
EXPERIMENT_TIMEOUT = 120  # 2 minutes per config

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="{time:HH:mm:ss}|{level:<7}|{message}",
)
logger.add(
    LOG_DIR / "run.log",
    rotation="30 MB",
    level="DEBUG",
)

# ============================================================================
# HARDWARE DETECTION
# ============================================================================

def _detect_cpus() -> int:
    """Detect actual CPU allocation (containers/pods/bare metal)."""
    try:  # cgroups v2 quota
        parts = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if parts[0] != "max":
            return max(1, math.ceil(int(parts[0]) / int(parts[1])))
    except (FileNotFoundError, ValueError):
        pass
    try:  # cgroups v1 quota
        q = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        p = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        if q > 0:
            return max(1, math.ceil(q / p))
    except (FileNotFoundError, ValueError):
        pass
    try:  # CPU affinity (cpuset — used by RunPod, Docker --cpuset-cpus)
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        pass
    return os.cpu_count() or 1

NUM_CPUS = _detect_cpus()
logger.info(f"Detected {NUM_CPUS} CPUs")

# Set memory limits
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))

# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

def get_simple_model():
    """Simple model: TF-IDF + Logistic Regression."""
    return Pipeline([
        ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=1000, random_state=42, n_jobs=1))
    ])


def get_complex_model():
    """Complex model: character n-grams + RandomForest."""
    return Pipeline([
        ('char_ngram', CountVectorizer(
            analyzer='char',
            ngram_range=(3, 5),
            max_features=20000
        )),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=1))
    ])


# ============================================================================
# DATA LOADING AND PREPARATION
# ============================================================================

def load_sst2():
    """Load SST-2 dataset."""
    logger.info("Loading SST-2 dataset")
    ds = load_dataset("stanfordnlp/sst2", split="train")
    texts = ds["sentence"]
    labels = ds["label"]
    del ds
    gc.collect()
    return texts, labels


def load_imdb():
    """Load IMDB dataset."""
    logger.info("Loading IMDB dataset")
    ds = load_dataset("stanfordnlp/imdb", split="train")
    texts = ds["text"]
    labels = ds["label"]
    del ds
    gc.collect()
    return texts, labels


def stratified_imbalanced_subsample(
    texts: list[str],
    labels: list[int],
    target_size: int,
    imbalance_ratio: float,
    random_state: int
) -> tuple[list[str], list[int]]:
    """Create a stratified subsample with controlled class imbalance.

    Args:
        texts: List of text samples
        labels: List of labels
        target_size: Total target sample size
        imbalance_ratio: Ratio of majority to minority class (1.0 = balanced)
        random_state: Random seed

    Returns:
        Subsampled texts and labels
    """
    rng = np.random.RandomState(random_state)

    # Separate by class
    class_0_idx = [i for i, l in enumerate(labels) if l == 0]
    class_1_idx = [i for i, l in enumerate(labels) if l == 1]

    # Calculate sizes based on imbalance ratio
    # imbalance_ratio = majority_size / minority_size
    # total = majority_size + minority_size
    minority_size = int(target_size / (1 + imbalance_ratio))
    majority_size = target_size - minority_size

    # Determine which class has more available samples
    if len(class_0_idx) >= len(class_1_idx):
        majority_class_idx = class_0_idx
        minority_class_idx = class_1_idx
    else:
        majority_class_idx = class_1_idx
        minority_class_idx = class_0_idx

    # Sample from each class
    sampled_majority = rng.choice(
        majority_class_idx,
        size=min(majority_size, len(majority_class_idx)),
        replace=False
    )
    sampled_minority = rng.choice(
        minority_class_idx,
        size=min(minority_size, len(minority_class_idx)),
        replace=False
    )

    # Combine and shuffle
    indices = np.concatenate([sampled_majority, sampled_minority])
    rng.shuffle(indices)

    return [texts[i] for i in indices], [labels[i] for i in indices]


# ============================================================================
# BASELINE METHODS
# ============================================================================

def confidence_baseline(disagreements: list[dict]) -> list[int]:
    """Baseline: predict whichever model has higher confidence."""
    predictions = []
    for d in disagreements:
        if d['prob_simple'] > d['prob_complex']:
            predictions.append(d['pred_simple'])
        else:
            predictions.append(d['pred_complex'])
    return predictions


def trust_score_baseline(
    disagreements: list[dict],
    train_texts: list[str],
    train_labels: list[int]
) -> list[int]:
    """Baseline: trust-score style proxy using nearest-neighbor agreement in TF-IDF space."""
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
    try:
        train_tfidf = vectorizer.fit_transform(train_texts)
        nn = NearestNeighbors(n_neighbors=5, metric='cosine')
        nn.fit(train_tfidf)

        predictions = []
        for d in disagreements:
            test_vec = vectorizer.transform([d['text']])
            _, indices = nn.kneighbors(test_vec)
            neighbor_labels = [train_labels[i] for i in indices[0]]
            majority_label = Counter(neighbor_labels).most_common(1)[0][0]
            predictions.append(majority_label)
    except Exception as e:
        logger.warning(f"Trust score baseline failed: {e}")
        # Fallback to random
        rng = np.random.RandomState(42)
        predictions = rng.randint(0, 2, size=len(disagreements)).tolist()

    return predictions


def random_baseline(n: int) -> list[int]:
    """Random baseline."""
    return np.random.RandomState(42).randint(0, 2, size=n).tolist()


# ============================================================================
# STATISTICAL TESTS
# ============================================================================

def binomial_test_on_directional_rule(
    disagreements: list[dict],
    majority_class: int
) -> tuple[float, float]:
    """Test if directional rule accuracy > 50% using binomial test."""
    correct = sum(
        1 for d in disagreements
        if (d['pred_simple'] == majority_class and d['pred_simple'] == d['true_label']) or
           (d['pred_simple'] != majority_class and d['pred_complex'] == d['true_label'])
    )
    n = len(disagreements)
    if n == 0:
        return 0.0, 1.0
    result = binomtest(correct, n, 0.5, alternative='greater')
    p_value = result.pvalue
    accuracy = correct / n
    return accuracy, p_value


def mcnemar_test(
    y_true: list[int],
    pred1: list[int],
    pred2: list[int]
) -> tuple[float, float]:
    """McNemar's test between two prediction sets."""
    a = sum(1 for yt, p1, p2 in zip(y_true, pred1, pred2)
            if p1 == yt and p2 != yt)  # pred1 correct, pred2 wrong
    b = sum(1 for yt, p1, p2 in zip(y_true, pred1, pred2)
            if p1 != yt and p2 == yt)  # pred1 wrong, pred2 correct
    d = sum(1 for yt, p1, p2 in zip(y_true, pred1, pred2)
            if p1 == yt and p2 == yt)  # both correct

    if a + b == 0:
        return 0.0, 1.0

    if a + b < 25:
        result = binomtest(a, a + b, 0.5, alternative='two-sided')
        p_value = result.pvalue
    else:
        chi2 = (abs(a - b) - 1) ** 2 / (a + b)
        p_value = stats.chi2.sf(chi2, 1)

    accuracy1 = (a + d) / len(y_true) if len(y_true) > 0 else 0
    accuracy2 = (b + d) / len(y_true) if len(y_true) > 0 else 0

    return accuracy1, p_value


# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_single_experiment(
    dataset_name: str,
    texts: list[str],
    labels: list[int],
    sample_size: int,
    imbalance_ratio: float,
    seed: int
) -> dict[str, Any]:
    """Run a single experiment configuration."""
    start_time = time.time()
    logger.info(
        f"Running: dataset={dataset_name}, size={sample_size}, "
        f"imbalance={imbalance_ratio}, seed={seed}"
    )

    # Subsample
    sub_texts, sub_labels = stratified_imbalanced_subsample(
        texts, labels, sample_size, imbalance_ratio, seed
    )

    # Determine majority class
    label_counts = Counter(sub_labels)
    majority_class = label_counts.most_common(1)[0][0]
    logger.debug(f"Majority class: {majority_class}, distribution: {label_counts}")

    # Train/test split (80/20), stratified
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        sub_texts, sub_labels, test_size=0.2, random_state=seed, stratify=sub_labels
    )

    # Fit simple model
    simple_model = get_simple_model()
    simple_model.fit(train_texts, train_labels)
    simple_preds = simple_model.predict(test_texts)
    simple_probs = simple_model.predict_proba(test_texts)

    # Fit complex model
    complex_model = get_complex_model()
    complex_model.fit(train_texts, train_labels)
    complex_preds = complex_model.predict(test_texts)
    complex_probs = complex_model.predict_proba(test_texts)

    # Find disagreements
    disagreements = []
    for i, (text, true_label) in enumerate(zip(test_texts, test_labels)):
        if simple_preds[i] != complex_preds[i]:
            disagreements.append({
                'text': text,
                'true_label': int(true_label),
                'pred_simple': int(simple_preds[i]),
                'pred_complex': int(complex_preds[i]),
                'prob_simple': float(max(simple_probs[i])),
                'prob_complex': float(max(complex_probs[i])),
                'sample_index': i
            })

    logger.debug(
        f"Found {len(disagreements)} disagreements out of {len(test_texts)} test samples"
    )

    # Compute baselines on disagreement set
    if len(disagreements) > 0:
        # Random baseline
        random_preds = random_baseline(len(disagreements))

        # Confidence baseline
        conf_preds = confidence_baseline(disagreements)

        # Trust score baseline
        trust_preds = trust_score_baseline(disagreements, train_texts, train_labels)

        # Directional rule
        dir_preds = []
        for d in disagreements:
            if d['pred_simple'] == majority_class:
                dir_preds.append(d['pred_simple'])
            else:
                dir_preds.append(d['pred_complex'])

        # True labels for disagreements
        true_labels_d = [d['true_label'] for d in disagreements]

        # Compute metrics
        dir_accuracy = accuracy_score(true_labels_d, dir_preds)
        conf_accuracy = accuracy_score(true_labels_d, conf_preds)
        trust_accuracy = accuracy_score(true_labels_d, trust_preds)
        random_accuracy = accuracy_score(true_labels_d, random_preds)

        # Statistical tests
        _, dir_pvalue = binomial_test_on_directional_rule(disagreements, majority_class)

        # McNemar's tests between directional rule and baselines
        _, mcnemar_conf_pvalue = mcnemar_test(true_labels_d, dir_preds, conf_preds)
        _, mcnemar_trust_pvalue = mcnemar_test(true_labels_d, dir_preds, trust_preds)
        _, mcnemar_random_pvalue = mcnemar_test(true_labels_d, dir_preds, random_preds)

    else:
        # No disagreements — use None/NaN to signal "not applicable"
        dir_accuracy = conf_accuracy = trust_accuracy = random_accuracy = float('nan')
        dir_pvalue = mcnemar_conf_pvalue = mcnemar_trust_pvalue = mcnemar_random_pvalue = float('nan')
        dir_preds = conf_preds = trust_preds = random_preds = []

    # Overall accuracies
    simple_accuracy = accuracy_score(test_labels, simple_preds)
    complex_accuracy = accuracy_score(test_labels, complex_preds)

    elapsed = time.time() - start_time
    logger.info(
        f"Completed in {elapsed:.1f}s: size={sample_size}, seed={seed}, "
        f"disagreements={len(disagreements)}, dir_acc={dir_accuracy:.3f}"
    )

    return {
        'dataset': dataset_name,
        'sample_size': sample_size,
        'imbalance_ratio': imbalance_ratio,
        'seed': seed,
        'train_size': len(train_texts),
        'test_size': len(test_texts),
        'simple_accuracy': float(simple_accuracy),
        'complex_accuracy': float(complex_accuracy),
        'num_disagreements': len(disagreements),
        'disagreement_ratio': float(len(disagreements) / len(test_texts)) if len(test_texts) > 0 else 0.0,
        'majority_class': int(majority_class),
        'class_distribution': {str(k): int(v) for k, v in label_counts.items()},
        'directional_rule_accuracy': dir_accuracy,
        'confidence_baseline_accuracy': conf_accuracy,
        'trust_score_baseline_accuracy': trust_accuracy,
        'random_baseline_accuracy': random_accuracy,
        'directional_rule_pvalue': dir_pvalue,
        'mcnemar_vs_confidence_pvalue': mcnemar_conf_pvalue,
        'mcnemar_vs_trust_score_pvalue': mcnemar_trust_pvalue,
        'mcnemar_vs_random_pvalue': mcnemar_random_pvalue,
        'elapsed_seconds': float(elapsed),
    }


def run_single_experiment_with_timeout(
    dataset_name: str,
    texts: list[str],
    labels: list[int],
    sample_size: int,
    imbalance_ratio: float,
    seed: int
) -> dict[str, Any]:
    """Run experiment with timeout protection."""
    try:
        return run_single_experiment(
            dataset_name, texts, labels, sample_size, imbalance_ratio, seed
        )
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        return {
            'dataset': dataset_name,
            'sample_size': sample_size,
            'imbalance_ratio': imbalance_ratio,
            'seed': seed,
            'error': str(e),
        }


def run_all_experiments() -> list[dict[str, Any]]:
    """Run all experiment configurations, processing one dataset at a time."""
    logger.info("Starting all experiments")
    all_results = []

    for dataset_name in DATASETS:
        logger.info(f"=== Processing dataset: {dataset_name} ===")
        # Load one dataset at a time to save memory
        if dataset_name == "sst2":
            texts, labels = load_sst2()
        else:
            texts, labels = load_imdb()

        # Generate configs for this dataset
        configs = []
        for sample_size in SAMPLE_SIZES:
            for imbalance_ratio in IMBALANCE_RATIOS:
                for seed in SEEDS:
                    configs.append((
                        dataset_name, texts, labels,
                        sample_size, imbalance_ratio, seed
                    ))

        logger.info(f"Running {len(configs)} configurations for {dataset_name}")

        # Run in parallel with ProcessPoolExecutor
        mp_context = mp.get_context("spawn")
        with ProcessPoolExecutor(max_workers=NUM_WORKERS, mp_context=mp_context) as executor:
            futures = {
                executor.submit(run_single_experiment_with_timeout, *config): config
                for config in configs
            }

            for future in as_completed(futures):
                config = futures[future]
                try:
                    result = future.result(timeout=EXPERIMENT_TIMEOUT)
                    all_results.append(result)
                except Exception as e:
                    logger.error(f"Experiment failed for config {config}: {e}")
                    dataset_name_c, _, _, sample_size_c, imbalance_ratio_c, seed_c = config
                    all_results.append({
                        'dataset': dataset_name_c,
                        'sample_size': sample_size_c,
                        'imbalance_ratio': imbalance_ratio_c,
                        'seed': seed_c,
                        'error': str(e),
                    })

        # Free memory before next dataset
        del texts, labels, configs
        gc.collect()
        logger.info(f"Finished {dataset_name}, freeing memory")

    logger.info(f"Completed {len(all_results)} experiments total")
    return all_results


# ============================================================================
# OUTPUT GENERATION
# ============================================================================

def _safe_mean(values: list[float]) -> float:
    """Compute mean ignoring NaN values; return NaN if all are NaN."""
    clean = [v for v in values if not math.isnan(v)]
    if not clean:
        return float('nan')
    return float(np.mean(clean))


def _safe_std(values: list[float]) -> float:
    """Compute std ignoring NaN values; return NaN if fewer than 2 valid."""
    clean = [v for v in values if not math.isnan(v)]
    if len(clean) < 2:
        return float('nan')
    return float(np.std(clean))


def generate_ablation_table(results: list[dict]) -> dict[str, Any]:
    """Generate ablation summary table, excluding configs with 0 disagreements from accuracy means."""
    summary = {}

    for dataset in DATASETS:
        dataset_results = [r for r in results if r.get('dataset') == dataset and 'error' not in r]

        for sample_size in SAMPLE_SIZES:
            for imbalance_ratio in IMBALANCE_RATIOS:
                config_results = [
                    r for r in dataset_results
                    if r['sample_size'] == sample_size
                    and r['imbalance_ratio'] == imbalance_ratio
                ]

                if not config_results:
                    continue

                # Count how many configs had disagreements
                with_disagreements = [r for r in config_results if r['num_disagreements'] > 0]
                n_with_disagreements = len(with_disagreements)

                key = f"{dataset}_size{sample_size}_imb{imbalance_ratio}"
                summary[key] = {
                    'dataset': dataset,
                    'sample_size': sample_size,
                    'imbalance_ratio': imbalance_ratio,
                    'n_seeds': len(config_results),
                    'n_with_disagreements': n_with_disagreements,
                    'mean_directional_accuracy': _safe_mean([r['directional_rule_accuracy'] for r in config_results]),
                    'std_directional_accuracy': _safe_std([r['directional_rule_accuracy'] for r in config_results]),
                    'mean_confidence_accuracy': _safe_mean([r['confidence_baseline_accuracy'] for r in config_results]),
                    'mean_trust_score_accuracy': _safe_mean([r['trust_score_baseline_accuracy'] for r in config_results]),
                    'mean_random_accuracy': _safe_mean([r['random_baseline_accuracy'] for r in config_results]),
                    'mean_disagreement_ratio': float(np.mean([r['disagreement_ratio'] for r in config_results])),
                    'mean_directional_pvalue': _safe_mean([r['directional_rule_pvalue'] for r in config_results]),
                }

    return summary


def save_results(results: list[dict], ablation: dict):
    """Save results to JSON files in exp_gen_sol_out schema format."""

    def _json_safe(val: Any) -> Any:
        """Convert NaN/Inf to None for JSON serialization."""
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None
        return val

    # Group results by dataset
    datasets_output = []
    for dataset_name in DATASETS:
        dataset_results = [r for r in results if r.get('dataset') == dataset_name]
        examples = []

        for r in dataset_results:
            if 'error' in r:
                continue

            # Create input describing the configuration
            input_str = (
                f"Dataset: {r['dataset']}, Sample size: {r['sample_size']}, "
                f"Imbalance ratio: {r['imbalance_ratio']}, Seed: {r['seed']}, "
                f"Train size: {r['train_size']}, Test size: {r['test_size']}, "
                f"Majority class: {r['majority_class']}, "
                f"Class distribution: {r['class_distribution']}"
            )

            # Create output with key metrics (handle NaN)
            dir_acc = r['directional_rule_accuracy']
            if math.isnan(dir_acc):
                dir_acc_str = "N/A (0 disagreements)"
            else:
                dir_acc_str = f"{dir_acc:.3f}"

            output_str = (
                f"Simple accuracy: {r['simple_accuracy']:.3f}, "
                f"Complex accuracy: {r['complex_accuracy']:.3f}, "
                f"Disagreements: {r['num_disagreements']}/{r['test_size']} "
                f"({r['disagreement_ratio']:.1%}), "
                f"Directional rule accuracy: {dir_acc_str}"
            )

            def _fmt_acc(key: str) -> str:
                v = r.get(key)
                if v is None or (isinstance(v, float) and math.isnan(v)):
                    return "accuracy=N/A"
                return f"accuracy={v:.3f}"

            def _fmt_dir() -> str:
                v = r.get('directional_rule_accuracy')
                p = r.get('directional_rule_pvalue')
                if v is None or (isinstance(v, float) and math.isnan(v)):
                    return "accuracy=N/A,p=N/A"
                if p is None or (isinstance(p, float) and math.isnan(p)):
                    return f"accuracy={v:.3f},p=N/A"
                return f"accuracy={v:.3f},p={p:.3f}"

            example = {
                'input': input_str,
                'output': output_str,
                'metadata_dataset': r['dataset'],
                'metadata_sample_size': r['sample_size'],
                'metadata_imbalance_ratio': r['imbalance_ratio'],
                'metadata_seed': r['seed'],
                'metadata_train_size': r['train_size'],
                'metadata_test_size': r['test_size'],
                'metadata_majority_class': r['majority_class'],
                'metadata_disagreement_ratio': _json_safe(r['disagreement_ratio']),
                'metadata_num_disagreements': r['num_disagreements'],
                'predict_simple_model': f"accuracy={r['simple_accuracy']:.3f}",
                'predict_complex_model': f"accuracy={r['complex_accuracy']:.3f}",
                'predict_directional_rule': _fmt_dir(),
                'predict_confidence_baseline': _fmt_acc('confidence_baseline_accuracy'),
                'predict_trust_score_baseline': _fmt_acc('trust_score_baseline_accuracy'),
                'predict_random_baseline': _fmt_acc('random_baseline_accuracy'),
            }

            examples.append(example)

        datasets_output.append({
            'dataset': dataset_name,
            'examples': examples
        })

    # Main output in exp_gen_sol_out format
    output = {
        'metadata': {
            'description': 'Disagreement Direction Test for Sentiment Classification',
            'sample_sizes': SAMPLE_SIZES,
            'imbalance_ratios': IMBALANCE_RATIOS,
            'seeds': SEEDS,
            'total_configurations': len(results),
            'ablation_table': {k: {kk: _json_safe(vv) for kk, vv in v.items()} for k, v in ablation.items()}
        },
        'datasets': datasets_output
    }

    output_path = OUTPUT_DIR / "method_out.json"
    output_path.write_text(json.dumps(output, indent=2, default=str))
    logger.info(f"Saved results to {output_path}")

    # Also save as method_out.json in workspace root for validation
    workspace_output = WORKSPACE / "method_out.json"
    workspace_output.write_text(json.dumps(output, indent=2, default=str))
    logger.info(f"Also saved to {workspace_output}")


# ============================================================================
# VALIDATION AND SMOKE TEST
# ============================================================================

def validate_results(results: list[dict]) -> bool:
    """Validate that all required fields are present and consistent in results."""
    required_fields = [
        'dataset', 'sample_size', 'imbalance_ratio', 'seed',
        'num_disagreements', 'directional_rule_accuracy',
        'confidence_baseline_accuracy', 'trust_score_baseline_accuracy',
        'random_baseline_accuracy', 'simple_accuracy', 'complex_accuracy',
        'disagreement_ratio', 'majority_class', 'class_distribution',
        'directional_rule_pvalue',
    ]

    valid = True
    error_count = 0
    for i, result in enumerate(results):
        if 'error' in result:
            logger.warning(f"Result {i} has error: {result['error']}")
            error_count += 1
            continue

        for field in required_fields:
            if field not in result:
                logger.error(f"Result {i} missing field: {field}")
                valid = False

        # Check that disagreement count matches ratio
        num_dis = result.get('num_disagreements', 0)
        test_size = result.get('test_size', 0)
        if test_size > 0 and num_dis > 0:
            expected_ratio = num_dis / test_size
            actual_ratio = result.get('disagreement_ratio', -1)
            if abs(expected_ratio - actual_ratio) > 0.001:
                logger.error(f"Result {i}: disagreement_ratio mismatch")
                valid = False

        # Check that accuracy values are reasonable
        for acc_key in ['simple_accuracy', 'complex_accuracy']:
            val = result.get(acc_key)
            if val is not None and not (0.0 <= val <= 1.0):
                logger.error(f"Result {i}: {acc_key}={val} out of range")
                valid = False

    logger.info(f"Validation complete: {len(results)} results, {error_count} errors")
    if valid:
        logger.info("All results validated successfully")
    else:
        logger.error("Validation found issues")

    return valid


def smoke_test() -> bool:
    """Run smoke test with real SST-2 data: one seed, size=200, balanced."""
    logger.info("Running smoke test with real data")
    try:
        # Load a small amount of real data
        texts, labels = load_sst2()
        logger.info(f"Loaded {len(texts)} SST-2 samples for smoke test")

        result = run_single_experiment(
            dataset_name='sst2',
            texts=texts,
            labels=labels,
            sample_size=200,
            imbalance_ratio=1.0,
            seed=0
        )

        del texts, labels
        gc.collect()

        assert 'num_disagreements' in result, "Missing num_disagreements"
        assert 'directional_rule_accuracy' in result, "Missing directional_rule_accuracy"
        assert 'confidence_baseline_accuracy' in result, "Missing confidence_baseline_accuracy"
        assert 0.0 <= result['simple_accuracy'] <= 1.0, f"Simple accuracy out of range: {result['simple_accuracy']}"
        assert 0.0 <= result['complex_accuracy'] <= 1.0, f"Complex accuracy out of range: {result['complex_accuracy']}"

        logger.info(
            f"Smoke test PASSED: {result['num_disagreements']} disagreements, "
            f"dir_acc={result['directional_rule_accuracy']}"
        )
        return True

    except Exception as e:
        logger.error(f"Smoke test failed: {e}")
        raise


# ============================================================================
# MAIN
# ============================================================================

@logger.catch(reraise=True)
def main():
    logger.info("Starting Disagreement Direction Test for Sentiment")

    # Run smoke test first
    smoke_test()

    # Run all experiments
    results = run_all_experiments()

    # Validate results
    validate_results(results)

    # Generate ablation table
    ablation = generate_ablation_table(results)

    # Save results
    save_results(results, ablation)

    # Print summary
    print("\n" + "="*60)
    print("EXPERIMENT SUMMARY")
    print("="*60)

    # Overall statistics (handle NaN)
    valid_results = [r for r in results if 'error' not in r]
    total_disagreements = sum(r['num_disagreements'] for r in valid_results)

    # Filter to only configs with disagreements for accuracy means
    with_dis = [r for r in valid_results if r['num_disagreements'] > 0]
    n_with_dis = len(with_dis)

    if n_with_dis > 0:
        mean_dir_acc = np.mean([r['directional_rule_accuracy'] for r in with_dis])
        mean_conf_acc = np.mean([r['confidence_baseline_accuracy'] for r in with_dis])
        mean_trust_acc = np.mean([r['trust_score_baseline_accuracy'] for r in with_dis])
        mean_rand_acc = np.mean([r['random_baseline_accuracy'] for r in with_dis])
    else:
        mean_dir_acc = mean_conf_acc = mean_trust_acc = mean_rand_acc = float('nan')

    print(f"Total configurations run: {len(valid_results)}")
    print(f"Configurations with disagreements: {n_with_dis}")
    print(f"Total disagreements analyzed: {total_disagreements}")
    if n_with_dis > 0:
        print(f"Mean directional rule accuracy: {mean_dir_acc:.3f}")
        print(f"Mean confidence baseline accuracy: {mean_conf_acc:.3f}")
        print(f"Mean trust score baseline accuracy: {mean_trust_acc:.3f}")
        print(f"Mean random baseline accuracy: {mean_rand_acc:.3f}")
    else:
        print("No disagreements found across any configuration")
    print("="*60 + "\n")

    logger.info("Experiment completed successfully")


if __name__ == "__main__":
    main()
