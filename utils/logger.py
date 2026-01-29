# utils/data_cleaning.py

import os
import pandas as pd
import re


def clean_price(price):
    try:
        return int(re.sub(r"[^\d]", "", str(price)))
    except:
        return None


def clean_discount(discount):
    try:
        match = re.search(r"(\d+)", str(discount))
        return int(match.group(1)) if match else None
    except:
        return None


def clean_rating(rating):
    try:
        if isinstance(rating, str) and "out of" in rating:
            return float(rating.split(" ")[0])
        return float(rating)
    except:
        return None


def clean_reviews(reviews):
    try:
        return int(re.sub(r"[^\d]", "", str(reviews)))
    except:
        return None


def preprocess_file(input_file, output_file):
    """Clean a single raw CSV file and save to processed folder."""
    df = pd.read_csv(input_file)

    # === Clean Columns ===
    if "Price" in df.columns:
        df["Price"] = df["Price"].apply(clean_price)

    if "Discount" in df.columns:
        df["Discount"] = df["Discount"].apply(clean_discount)

    if "Ratings" in df.columns:
        df["Ratings"] = df["Ratings"].apply(clean_rating)

    if "Reviews Count" in df.columns:
        df["Reviews Count"] = df["Reviews Count"].apply(clean_reviews)

    if "Product" in df.columns:
        df["Product"] = df["Product"].astype(str).str.lower().str.strip()

    # === Handle Missing Values ===
    # Drop rows with missing Price (essential field)
    if "Price" in df.columns:
        df = df.dropna(subset=["Price"])

    # Fill NaN for optional fields
    for col in ["Discount", "Ratings", "Reviews Count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # === Remove duplicates ===
    subset_cols = [c for c in ["Product", "Link"] if c in df.columns]
    if subset_cols:
        df = df.drop_duplicates(subset=subset_cols, keep="first")

    # === Save processed data ===
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"✅ Processed: {input_file} → {output_file}")


def preprocess_all():
    """Process all raw CSV files in data/raw → data/processed"""
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    processed_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

    os.makedirs(processed_dir, exist_ok=True)

    for file in os.listdir(raw_dir):
        if file.endswith(".csv"):
            input_file = os.path.join(raw_dir, file)
            output_file = os.path.join(processed_dir, file)  # keep same name
            preprocess_file(input_file, output_file)


if __name__ == "__main__":
    preprocess_all()
