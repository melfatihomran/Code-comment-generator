"""
Data utilities for the Code Comment Generation project.

Dataset: sentence-transformers/codesearchnet (config="pair")
  - Columns: "comment" (str), "code" (str)
  - ONLY a "train" split exists (1,375,067 rows) -- there is no built-in
    validation/test split, so we create our own.
  - comment length: 16-255 chars | code length: 52 - 3.87M chars (raw text)

This module is imported by both the Kaggle training notebook and the
standalone evaluate.py / inference scripts so preprocessing logic is
defined exactly once.
"""

import random
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

# Heuristic bounds (character counts) to drop degenerate / unusable pairs
# before tokenization. These are intentionally generous -- the tokenizer's
# max_length + truncation handles the rest.
MIN_CODE_CHARS = 20
MAX_CODE_CHARS = 4000          # ~3.87M char outliers exist; drop them, they're noise (minified/generated code)
MIN_COMMENT_CHARS = 8
MAX_COMMENT_CHARS = 400

# Comments that are just boilerplate / non-informative and hurt a model
# trained to produce useful docstrings.
BOILERPLATE_COMMENT_PREFIXES = (
    "todo",
    "fixme",
    "xxx",
    "deprecated",
)


def is_valid_pair(example: Dict) -> bool:
    """Return True if a (code, comment) example should be kept."""
    code = example.get("code", "") or ""
    comment = example.get("comment", "") or ""

    if not (MIN_CODE_CHARS <= len(code) <= MAX_CODE_CHARS):
        return False
    if not (MIN_COMMENT_CHARS <= len(comment) <= MAX_COMMENT_CHARS):
        return False

    comment_lower = comment.strip().lower()
    if comment_lower.startswith(BOILERPLATE_COMMENT_PREFIXES):
        return False

    # Drop comments that are mostly punctuation/markup noise (e.g. stray
    # "----" separators seen in the raw dataset).
    alnum_chars = sum(c.isalnum() for c in comment)
    if alnum_chars < 0.3 * len(comment):
        return False

    return True


def filter_dataset(dataset, num_proc: int = 4):
    """Apply is_valid_pair as a HF datasets .filter() call."""
    return dataset.filter(is_valid_pair, num_proc=num_proc)


# ---------------------------------------------------------------------------
# Splitting (this dataset only ships a single "train" split)
# ---------------------------------------------------------------------------

def make_splits(
    dataset,
    train_size: int,
    val_size: int,
    test_size: int,
    seed: int = 42,
):
    """
    Build train/val/test splits out of a single HF `Dataset` (the "train"
    split of sentence-transformers/codesearchnet, post-filtering).

    Sampling is done by shuffling once and slicing, so the three splits
    are guaranteed disjoint.
    """
    total_needed = train_size + val_size + test_size
    shuffled = dataset.shuffle(seed=seed)

    if len(shuffled) < total_needed:
        raise ValueError(
            f"Requested {total_needed} examples but filtered dataset only "
            f"has {len(shuffled)}. Lower train/val/test sizes or loosen "
            f"the filters in is_valid_pair()."
        )

    subset = shuffled.select(range(total_needed))
    train = subset.select(range(0, train_size))
    val = subset.select(range(train_size, train_size + val_size))
    test = subset.select(
        range(train_size + val_size, train_size + val_size + test_size)
    )
    return train, val, test


# ---------------------------------------------------------------------------
# Tokenization
# ---------------------------------------------------------------------------

# CodeT5 was pretrained without requiring a task prefix for single-task
# fine-tuning, so we feed the raw code as the encoder input. Keeping this
# as a constant means you can experiment with a prefix later (e.g. for a
# multi-task model) without touching the rest of the pipeline.
SOURCE_PREFIX = ""

MAX_SOURCE_LEN = 256
MAX_TARGET_LEN = 64


def build_preprocess_fn(tokenizer, max_source_len=MAX_SOURCE_LEN, max_target_len=MAX_TARGET_LEN):
    """Return a function suitable for dataset.map(..., batched=True)."""

    def preprocess(batch):
        inputs = [SOURCE_PREFIX + c for c in batch["code"]]
        model_inputs = tokenizer(
            inputs,
            max_length=max_source_len,
            truncation=True,
            padding="max_length",
        )
        labels = tokenizer(
            text_target=batch["comment"],
            max_length=max_target_len,
            truncation=True,
            padding="max_length",
        )
        # Replace pad token id in labels with -100 so it's ignored by the loss.
        label_ids = []
        for ids in labels["input_ids"]:
            label_ids.append([
                (tok_id if tok_id != tokenizer.pad_token_id else -100)
                for tok_id in ids
            ])
        model_inputs["labels"] = label_ids
        return model_inputs

    return preprocess


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

def set_seed(seed: int = 42):
    import numpy as np
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
