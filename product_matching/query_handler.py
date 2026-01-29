import os
import pandas as pd

def load_all_processed_data(query: str, processed_dir="data/processed"):
    all_data = []

    for file in os.listdir(processed_dir):
        if file.endswith(".csv"):
            filepath = os.path.join(processed_dir, file)
            print(f"📄 Loading file: {filepath}")  # ← Added line to show which CSV is loading

            df = pd.read_csv(filepath)

            # standardize columns
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

            if 'product' not in df.columns:
                print(f"⚠️ 'product' column missing in {file}, skipping.")
                continue

            # Broad query filtering
            mask = df['product'].str.contains(query, case=False, na=False)
            filtered = df[mask].copy()

            # Extract website from filename
            site_name = os.path.basename(file).split("_")[0].lower()
            filtered["website"] = site_name

            all_data.append(filtered)

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df.drop_duplicates(subset=['product', 'website'], inplace=True)
        return combined_df

    return pd.DataFrame()
