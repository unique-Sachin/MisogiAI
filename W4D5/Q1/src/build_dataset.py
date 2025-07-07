"""Build combined news article dataset for Smart Article Categorizer.

This script downloads AG News and BBC News datasets via the 🤗 Datasets library,
remaps their native labels to the 6 target categories specified in the PRD,
performs basic text cleaning, and generates stratified train/val/test splits.

Output files:
    data/raw_articles.csv      # full cleaned dataset
    data/train.csv             # 70% train split
    data/val.csv               # 15% validation split
    data/test.csv              # 15% test split

Run:
    python -m src.build_dataset
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd  # type: ignore
from datasets import load_dataset, DatasetDict  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
import io  # type: ignore
import zipfile  # type: ignore
import requests  # type: ignore

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TARGET_CATEGORIES: List[str] = [
    "Tech",
    "Finance",
    "Healthcare",
    "Sports",
    "Politics",
    "Entertainment",
]

# Mapping for AG News dataset (World, Sports, Business, Sci/Tech)
AG_NEWS_MAPPING: Dict[str, str] = {
    "World": "Politics",  # approximate mapping
    "Sports": "Sports",
    "Business": "Finance",
    "Sci/Tech": "Tech",
}

# Mapping for BBC dataset (business, entertainment, politics, sport, tech)
BBC_MAPPING: Dict[str, str] = {
    "business": "Finance",
    "entertainment": "Entertainment",
    "politics": "Politics",
    "sport": "Sports",
    "tech": "Tech",
}

CLEAN_RE = re.compile(r"[^a-zA-Z0-9\s]")


def clean_text(text: str) -> str:
    """Lower-case, strip, and remove non-alphanumeric characters."""
    text = text.lower()
    text = CLEAN_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_ag_news() -> pd.DataFrame:
    ds: DatasetDict = load_dataset("ag_news")  # train/test splits
    frames: List[pd.DataFrame] = []
    for split_name, split_ds in ds.items():
        df = split_ds.to_pandas()
        # Rename columns for consistency
        df = df.rename(columns={"text": "text", "label": "label"})
        # Map integer label to string category
        label_mapping = {
            0: "World",
            1: "Sports",
            2: "Business",
            3: "Sci/Tech",
        }
        df["label"] = df["label"].map(label_mapping)
        df["category"] = df["label"].map(AG_NEWS_MAPPING)
        frames.append(df[["text", "category"]])
    ag_df = pd.concat(frames, ignore_index=True)
    return ag_df.dropna(subset=["category"])


def fetch_bbc_news() -> pd.DataFrame:
    """Download BBC full-text ZIP and parse into DataFrame."""
    url = "http://mlg.ucd.ie/files/datasets/bbc-fulltext.zip"
    print("Downloading BBC News archive …")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    rows: List[Dict[str, str]] = []
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for member in zf.namelist():
            if not member.endswith(".txt"):
                continue
            # Path format: "business/123.txt"
            category_dir = member.split("/")[0].lower()
            mapped = BBC_MAPPING.get(category_dir)
            if mapped is None:
                # Skip classes we don't map (e.g., sports subdir variations)
                continue
            text_bytes = zf.read(member)
            try:
                text = text_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = text_bytes.decode("latin1")
            rows.append({"text": text, "category": mapped})

    bbc_df = pd.DataFrame(rows)
    return bbc_df


def build_dataset() -> None:
    print("Downloading datasets …")
    ag_df = fetch_ag_news()
    bbc_df = fetch_bbc_news()

    combined = pd.concat([ag_df, bbc_df], ignore_index=True)
    print(f"Combined dataset size: {len(combined):,} articles")

    # Clean text
    print("Cleaning text …")
    combined["clean_text"] = combined["text"].astype(str).apply(clean_text)

    # Note: Healthcare category currently missing; flagging for later augmentation.
    missing_healthcare = combined[combined["category"] == "Healthcare"].empty
    if missing_healthcare:
        print("Warning: No Healthcare articles found — will need supplemental data (e.g., NewsAPI).")

    # Save raw dataset
    raw_path = DATA_DIR / "raw_articles.csv"
    combined.to_csv(raw_path, index=False)
    print(f"Saved raw dataset to {raw_path.relative_to(Path.cwd())}")

    # Train/val/test split (stratified by category)
    train_val, test = train_test_split(
        combined,
        test_size=0.15,
        stratify=combined["category"],
        random_state=42,
    )
    train, val = train_test_split(
        train_val,
        test_size=0.1765,  # 0.1765 * 0.85 ≈ 0.15 overall
        stratify=train_val["category"],
        random_state=42,
    )

    for df, name in [(train, "train"), (val, "val"), (test, "test")]:
        out_path = DATA_DIR / f"{name}.csv"
        df.to_csv(out_path, index=False)
        print(f"Saved {name} split ({len(df):,}) to {out_path.relative_to(Path.cwd())}")

    print("Dataset build complete.")


if __name__ == "__main__":
    build_dataset() 