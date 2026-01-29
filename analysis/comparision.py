import os
import re
import pandas as pd
from rapidfuzz import fuzz
from config.category_mapping import CATEGORY_WEBSITES
from sentence_transformers import SentenceTransformer, util

# Load embedding model
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def load_processed_data(category, query):
    """Load all processed CSVs for a given category and query."""
    platforms = CATEGORY_WEBSITES.get(category.lower(), [])
    dfs = []
    for platform in platforms:
        file_path = f"data/processed/{platform}_{category}_{query}.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['platform'] = platform
            dfs.append(df)
        else:
            print(f"[WARN] File not found: {file_path}")
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def extract_screen_size(title):
    """Extract numeric screen size from product title, e.g., '14' or '15.6'."""
    match = re.search(r'(\d{2,2}(\.\d)?)\s*(inch|")', title.lower())
    if match:
        return match.group(1)
    # Fallback: look for patterns like "14", "15" at start or after model
    match2 = re.search(r'\b(\d{2})\b', title)
    return match2.group(1) if match2 else None

def extract_model_code(title):
    """Extract model code from title (common patterns like e1404fa-nk5542ws)."""
    match = re.search(r'([a-zA-Z0-9\-]{5,})', title)
    return match.group(1) if match else None

def same_model(row1, row2):
    """Check if two products are likely the same model."""
    size1 = extract_screen_size(row1['Product'])
    size2 = extract_screen_size(row2['Product'])
    model1 = extract_model_code(row1['Product'])
    model2 = extract_model_code(row2['Product'])

    if model1 and model2:
        return model1.lower() == model2.lower()
    elif size1 and size2:
        return size1 == size2
    return False

def match_products(df, text_threshold=85, semantic_threshold=0.75):
    """Match products using fuzzy + semantic embeddings, with model/size filter."""
    df = df.reset_index(drop=True)
    df['group_id'] = None
    df['matched'] = False
    group_counter = 0

    embeddings = MODEL.encode(df['Product'].tolist(), convert_to_tensor=True)

    for i, row in df.iterrows():
        if df.at[i, 'group_id'] is not None:
            continue

        df.at[i, 'group_id'] = group_counter
        df.at[i, 'matched'] = False
        current_platform = row['platform']

        for j, other_row in df.iloc[i+1:].iterrows():
            if df.at[j, 'group_id'] is not None:
                continue
            if other_row['platform'] == current_platform:
                continue

            # Only match if model/size matches
            if same_model(row, other_row):
                # Fuzzy matching
                ratio = fuzz.token_sort_ratio(row['Product'], other_row['Product'])
                if ratio >= text_threshold:
                    df.at[j, 'group_id'] = group_counter
                    df.at[j, 'matched'] = True
                    df.at[i, 'matched'] = True
                else:
                    # Semantic fallback
                    sim_score = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()
                    if sim_score >= semantic_threshold:
                        df.at[j, 'group_id'] = group_counter
                        df.at[j, 'matched'] = True
                        df.at[i, 'matched'] = True

        group_counter += 1

    return df

def save_matched_products(df, category, query):
    os.makedirs("data/matched", exist_ok=True)
    file_path = f"data/matched/{category}_{query}_matched.csv"
    df.to_csv(file_path, index=False)
    print(f"[INFO] Matched products saved to {file_path}")
    print(f"[INFO] Total matched products: {df['matched'].sum()} / {len(df)}")

def main(category, query):
    df = load_processed_data(category, query)
    if df.empty:
        print("[WARN] No products found for this query/category.")
        return
    df_matched = match_products(df)
    save_matched_products(df_matched, category, query)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Match products across platforms")
    parser.add_argument("--category", required=True, help="Product category")
    parser.add_argument("--query", required=True, help="Search query")
    args = parser.parse_args()

    main(args.category, args.query)
