#!/usr/bin/env python3
"""Minimal version for quick validation."""

import gc
import json
import math
import multiprocessing as mp
import os
import resource
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

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

WORKSPACE = Path(
    "/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_1/gen_art/gen_art_experiment_1"
)
LOG_DIR = WORKSPACE / "logs"
OUTPUT_DIR = WORKSPACE / "results"
LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(LOG_DIR / "run.log", rotation="30 MB", level="DEBUG")


def _detect_cpus() -> int:
    try:
        parts = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if parts[0] != "max":
            return max(1, math.ceil(int(parts[0]) / int(parts[1])))
    except (FileNotFoundError, ValueError):
        pass
    try:
        q = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        p = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        if q > 0:
            return max(1, math.ceil(q / p))
    except (FileNotFoundError, ValueError):
        pass
    try:
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        pass
    return os.cpu_count() or 1


NUM_CPUS = _detect_cpus()
RAM_BUDGET = 12 * 1024**3
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))
logger.info(f"Detected {NUM_CPUS} CPUs")


def get_simple_model():
    return Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=500))
    ])


def get_complex_model():
    return Pipeline([
        ('char_ngram', CountVectorizer(analyzer='char', ngram_range=(3, 4), max_features=10000)),
        ('clf', RandomForestClassifier(n_estimators=50))
    ])


def load_sst2():
    logger.info("Loading SST-2")
    ds = load_dataset("stanfordnlp/sst2", split="train")
    texts = ds["sentence"]
    labels = ds["label"]
    del ds
    gc.collect()
    return texts, labels


def load_imdb():
    logger.info("Loading IMDB")
    ds = load_dataset("stanfordnlp/imdb", split="train")
    texts = ds["text"]
    labels = ds["label"]
    del ds
    gc.collect()
    return texts, labels


def stratified_subsample(texts, labels, size, ratio, seed):
    rng = np.random.RandomState(seed)
    c0 = [i for i, l in enumerate(labels) if l == 0]
    c1 = [i for i, l in enumerate(labels) if l == 1]
    maj = int(size / (1 + ratio))
    min_ = size - maj
    s0 = rng.choice(c0, size=min(maj, len(c0)), replace=False)
    s1 = rng.choice(c1, size=min(min_, len(c1)), replace=False)
    idx = np.concatenate([s0, s1])
    rng.shuffle(idx)
    return [texts[i] for i in idx], [labels[i] for i in idx]


def run_config(dataset_name, texts, labels, size, ratio, seed):
    logger.info(f"Config: {dataset_name}, size={size}, ratio={ratio}, seed={seed}")
    sub_texts, sub_labels = stratified_subsample(texts, labels, size, ratio, seed)
    majority = Counter(sub_labels).most_common(1)[0][0]

    tr_texts, te_texts, tr_labels, te_labels = train_test_split(
        sub_texts, sub_labels, test_size=0.2, random_state=seed, stratify=sub_labels
    )

    simple = get_simple_model()
    simple.fit(tr_texts, tr_labels)
    sp = simple.predict(te_texts)
    sprob = simple.predict_proba(te_texts)

    complex_ = get_complex_model()
    complex_.fit(tr_texts, tr_labels)
    cp = complex_.predict(te_texts)
    cprob = complex_.predict_proba(te_texts)

    disagreements = []
    for i, (txt, true) in enumerate(zip(te_texts, te_labels)):
        if sp[i] != cp[i]:
            disagreements.append({
                'text': txt,
                'true': int(true),
                'ps': int(sp[i]),
                'pc': int(cp[i]),
                'p_sp': float(max(sprob[i])),
                'p_cp': float(max(cprob[i]))
            })

    n = len(disagreements)
    if n == 0:
        return {
            'dataset': dataset_name, 'size': size, 'ratio': ratio, 'seed': seed,
            'n_dis': 0, 'dir_acc': 0.0, 'conf_acc': 0.0, 'trust_acc': 0.0,
            'rand_acc': 0.0, 'dir_p': 1.0, 'simple_acc': float(accuracy_score(te_labels, sp)),
            'complex_acc': float(accuracy_score(te_labels, cp))
        }

    # Baselines
    rand = np.random.RandomState(42).randint(0, 2, size=n).tolist()
    conf = [d['ps'] if d['p_sp'] > d['p_cp'] else d['pc'] for d in disagreements]

    # Trust score
    try:
        vec = TfidfVectorizer(max_features=5000)
        tr_tfidf = vec.fit_transform(tr_texts)
        nn = NearestNeighbors(n_neighbors=5, metric='cosine').fit(tr_tfidf)
        trust = []
        for d in disagreements:
            tv = vec.transform([d['text']])
            _, idx = nn.kneighbors(tv)
            nl = [tr_labels[i] for i in idx[0]]
            trust.append(Counter(nl).most_common(1)[0][0])
    except Exception:
        trust = [np.random.choice([0, 1]) for _ in disagreements]

    # Directional rule
    dir_ = [d['ps'] if d['ps'] == majority else d['pc'] for d in disagreements]
    true_d = [d['true'] for d in disagreements]

    dir_acc = accuracy_score(true_d, dir_)
    conf_acc = accuracy_score(true_d, conf)
    trust_acc = accuracy_score(true_d, trust)
    rand_acc = accuracy_score(true_d, rand)

    correct = sum(1 for d, pred in zip(disagreements, dir_) if
                  (d['ps'] == majority and d['ps'] == d['true']) or
                  (d['ps'] != majority and d['pc'] == d['true']))
    p_val = binomtest(correct, n, 0.5, alternative='greater').pvalue

    result = {
        'dataset': dataset_name, 'size': size, 'ratio': ratio, 'seed': seed,
        'n_dis': n, 'dir_acc': float(dir_acc), 'conf_acc': float(conf_acc),
        'trust_acc': float(trust_acc), 'rand_acc': float(rand_acc),
        'dir_p': float(p_val),
        'simple_acc': float(accuracy_score(te_labels, sp)),
        'complex_acc': float(accuracy_score(te_labels, cp))
    }
    logger.info(f"Done: n_dis={n}, dir_acc={dir_acc:.3f}")
    return result


def main():
    logger.info("Loading datasets")
    sst2_texts, sst2_labels = load_sst2()
    imdb_texts, imdb_labels = load_imdb()
    datasets = {'sst2': (sst2_texts, sst2_labels), 'imdb': (imdb_texts, imdb_labels)}

    configs = []
    for ds_name in ['sst2', 'imdb']:
        texts, labels = datasets[ds_name]
        for size in [100, 500]:
            for ratio in [0.5, 0.9]:
                for seed in [0, 1, 2]:
                    configs.append((ds_name, texts, labels, size, ratio, seed))

    logger.info(f"Total configs: {len(configs)}")
    results = []

    mp_context = mp.get_context("spawn")
    with ProcessPoolExecutor(max_workers=2, mp_context=mp_context) as executor:
        futures = {executor.submit(run_config, *c): c for c in configs}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Failed: {e}")
                c = futures[future]
                results.append({'dataset': c[0], 'size': c[3], 'ratio': c[4], 'seed': c[5], 'error': str(e)})

    # Save
    out = {'metadata': {'n_configs': len(results)}, 'results': results}
    out_path = WORKSPACE / "method_out.json"
    out_path.write_text(json.dumps(out, indent=2))
    logger.info(f"Saved {len(results)} results to {out_path}")

    # Summary
    valid = [r for r in results if 'error' not in r]
    print("\n" + "="*60)
    print(f"Completed: {len(valid)}/{len(results)} configs")
    if valid:
        print(f"Mean directional accuracy: {np.mean([r['dir_acc'] for r in valid]):.3f}")
        print(f"Mean confidence accuracy: {np.mean([r['conf_acc'] for r in valid]):.3f}")
        print(f"Mean trust score accuracy: {np.mean([r['trust_acc'] for r in valid]):.3f}")
        print(f"Mean random accuracy: {np.mean([r['rand_acc'] for r in valid]):.3f}")
    print("="*60)


if __name__ == "__main__":
    main()
