#!/usr/bin/env python3
"""Load sentiment datasets from HuggingFace, standardize to exp_sel_data_out schema, save full_data_out.json."""

from loguru import logger
from pathlib import Path
import sys
import json
import hashlib

import numpy as np
from datasets import load_dataset

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

# Dataset configs: (hf_id, config, split, text_col, label_col, binary_map, domain)
# binary_map: dict mapping original labels to 0/1 (for multi-class → binary)
DATASET_CONFIGS = [
    # SST-2: binary sentence sentiment (movie review sentences)
    ("stanfordnlp/sst2", None, "train", "sentence", "label", None, "movie_review_sentences"),
    # IMDB: binary movie review sentiment
    ("stanfordnlp/imdb", "plain_text", "train", "text", "label", None, "movie_reviews"),
    # Twitter Financial News: 3-class → binary (bearish=0, bullish=1, drop neutral)
    ("zeroshot/twitter-financial-news-sentiment", None, "train", "text", "label",
     {0: 0, 1: 1}, "financial_tweets"),  # drop label 2 (neutral)
    # Emotion: 6-class → binary (sad/angry=0, happy/joy=1, drop others)
    # SKIPPED: derived binary from 6-class is less natural for sentiment asymmetry study
    # ("dair-ai/emotion", "split", "train", "text", "label",
    #  {0: 0, 1: 0, 2: 1, 3: 1, 4: None, 5: None}, "social_media_emotion"),
    # Financial News: 3-class → binary (0=negative→0, 1=positive→1, drop 2=neutral)
    # SKIPPED: too few samples after binarization (949, extremely imbalanced 49/900)
    # ("Jean-Baptiste/financial_news_sentiment", None, "train", "summary_detail_with_title", "labels",
    #  {0: 0, 1: 1}, "financial_news"),
]


@logger.catch(reraise=True)
def main():
    out_dir = Path(__file__).parent
    out_dir.mkdir(exist_ok=True)
    (out_dir / "logs").mkdir(exist_ok=True)

    all_datasets = []

    for hf_id, config, split, text_col, label_col, binary_map, domain in DATASET_CONFIGS:
        logger.info(f"Loading {hf_id} (config={config}, split={split})...")
        try:
            ds = load_dataset(hf_id, config, split=split, trust_remote_code=True)
        except Exception as e:
            logger.warning(f"Failed to load {hf_id}: {e}. Skipping.")
            continue

        raw_texts = ds[text_col]
        raw_labels = ds[label_col]
        logger.info(f"  Raw: {len(raw_texts)} samples, text_col={text_col}, label_col={label_col}")

        # Convert to binary if needed
        if binary_map is not None:
            texts, labels = [], []
            for t, l in zip(raw_texts, raw_labels):
                mapped = binary_map.get(l)
                if mapped is not None:
                    texts.append(t)
                    labels.append(mapped)
            logger.info(f"  After binarization: {len(texts)} samples (dropped {len(raw_texts) - len(texts)})")
        else:
            # Filter out -1 labels (SST-2 has undeveloped examples)
            texts, labels = [], []
            for t, l in zip(raw_texts, raw_labels):
                if l >= 0:
                    texts.append(t)
                    labels.append(l)
            logger.info(f"  After filtering -1: {len(texts)} samples")

        if len(texts) < 100:
            logger.warning(f"  Too few samples ({len(texts)}), skipping {hf_id}")
            continue

        # Compute label distribution
        label_counts = np.bincount(labels)
        logger.info(f"  Label distribution: {label_counts}")

        # Assign fold numbers (5-fold cross-validation)
        n_samples = len(texts)
        folds = np.arange(n_samples) % 5

        # Build examples list
        examples = []
        for i, (text, label, fold) in enumerate(zip(texts, labels, folds)):
            # Create a unique ID for this example
            ex_id = hashlib.md5(f"{hf_id}:{i}".encode()).hexdigest()[:8]

            example = {
                "input": str(text),
                "output": str(label),
                "metadata_fold": int(fold),
                "metadata_task_type": "classification",
                "metadata_n_classes": 2,
                "metadata_row_index": i,
                "metadata_domain": domain,
                "metadata_example_id": ex_id,
            }
            examples.append(example)

        dataset_entry = {
            "dataset": hf_id.replace("/", "_"),
            "examples": examples,
        }
        all_datasets.append(dataset_entry)
        logger.info(f"  ✓ Added {hf_id}: {len(examples)} examples")

    # Build output
    output = {
        "metadata": {
            "description": "Sentiment datasets for disagreement asymmetry experiment",
            "num_datasets": len(all_datasets),
            "total_examples": sum(len(d["examples"]) for d in all_datasets),
            "task": "binary_sentiment_classification",
        },
        "datasets": all_datasets,
    }

    out_path = out_dir / "full_data_out.json"
    out_path.write_text(json.dumps(output, indent=2))
    logger.info(f"Saved {out_path} ({out_path.stat().st_size / 1e6:.1f} MB)")
    logger.info(f"Total: {len(all_datasets)} datasets, {output['metadata']['total_examples']} examples")


if __name__ == "__main__":
    main()
