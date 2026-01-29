import streamlit as st
import pandas as pd
import os
import glob
import re
from utils.data_cleaning import preprocess_all
from jobs.scrape_by_category import scrape_by_category

# --- Page Config ---
st.set_page_config(page_title="Product Price Comparison", layout="wide")
st.title("🖥 Product Price Comparison Dashboard")

# --- Sidebar input ---
category = st.selectbox("Select Category", ["electronics", "clothing", "home_appliances", "furniture"])
query = st.text_input("Enter Product Query", "")

# --- Helper: Cleanup function ---
def cleanup_data_folders():
    """Delete all CSV files in /data/raw and /data/processed"""
    raw_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
    processed_dir = os.path.join(os.path.dirname(__file__), "data/processed")
    for folder in [raw_dir, processed_dir]:
        files = glob.glob(os.path.join(folder, "*.csv"))
        for f in files:
            try:
                os.remove(f)
            except Exception as e:
                st.warning(f"Could not delete {f}: {e}")

# --- Category → Websites Mapping ---
CATEGORY_WEBSITES = {
    "electronics": ["amazon", "flipkart"],
    "computers": ["amazon", "flipkart"],
    "clothing": ["amazon", "flipkart"]
}

# --- Load processed files ---
def load_processed_data(category, query):
    websites = CATEGORY_WEBSITES.get(category, [])
    all_data = []

    for site in websites:
        file_pattern = f"data/processed/{site}_{category}_{query}.csv"
        for file in glob.glob(file_pattern):
            df_site = pd.read_csv(file)
            df_site.columns = [col.strip().capitalize() for col in df_site.columns]
            df_site["Website"] = site
            all_data.append(df_site)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()


# --- Step 1: Query Filtering ---
def filter_by_query(df, query):
    """Keep all products whose names contain all query words (case-insensitive)"""
    if df.empty or not query:
        return df

    query_tokens = set(query.lower().split())

    def matches(row):
        name_tokens = set(str(row["Product"]).lower().split())
        return query_tokens.issubset(name_tokens)

    return df[df.apply(matches, axis=1)]

#dynamic filtering
def apply_filters(df, original_df=None):
    """Apply dynamic filters using the sidebar"""
    if original_df is None:
        original_df = df.copy()  # fallback if not provided

    # --- Website filter ---
    if "Website" in df.columns:
        all_websites = []
        for val in df["Website"].dropna():
            if isinstance(val, list):
                all_websites.extend(val)
            else:
                all_websites.append(val)
        websites = sorted(list(set(all_websites)))
        selected_websites = st.sidebar.multiselect("Filter by Website", websites, key="website_filter")
        if selected_websites:
            df = df[df["Website"].apply(lambda x: any(w in x for w in selected_websites) if isinstance(x, list) else x in selected_websites)]

    # --- Price filter ---
    if "Price" in df.columns:
        full_prices = original_df["Price"]
        min_price, max_price = int(full_prices.min()), int(full_prices.max())
        selected_price = st.sidebar.slider("Filter by Price", min_price, max_price, (min_price, max_price), key="price_filter")
        df = df[(df["Price"] >= selected_price[0]) & (df["Price"] <= selected_price[1])]

    # --- Discount filter ---
    if "Discount" in df.columns:
        discounts = sorted(original_df["Discount"].dropna().unique().tolist())
        selected_discounts = st.sidebar.multiselect("Filter by Discount", discounts, key="discount_filter")
        if selected_discounts:
            df = df[df["Discount"].isin(selected_discounts)]

    # --- Rating filter ---
    if "Rating" in df.columns:
        ratings = sorted(original_df["Rating"].dropna().unique().tolist())
        selected_ratings = st.sidebar.multiselect("Filter by Rating", ratings, key="rating_filter")
        if selected_ratings:
            df = df[df["Rating"].isin(selected_ratings)]

    return df



# --- Step 3: Group Variants to Row ---
def group_variants_to_row(df):
    """Group products across websites into one logical row per product"""
    websites = df["Website"].unique()
    grouped_rows = []
    for _, group in df.groupby("Product"):
        row = {"Product": group.iloc[0]["Product"]}
        for w in websites:
            row[f"{w.capitalize()} Price"] = None
            row[f"{w.capitalize()} Link"] = None
            site_data = group[group["Website"] == w]
            if not site_data.empty:
                row[f"{w.capitalize()} Price"] = site_data.iloc[0].get("Price", None)
                row[f"{w.capitalize()} Link"] = site_data.iloc[0].get("Link", None)
        grouped_rows.append(row)
    df_grouped = pd.DataFrame(grouped_rows)
    price_cols = [col for col in df_grouped.columns if "Price" in col]
    return df_grouped, price_cols


# --- Step 4: Highlight lowest price ---
def highlight_lowest_price(df, price_cols):
    def style_row(row):
        styles = [""] * len(row)
        prices = row[price_cols].astype(float)
        min_price = prices.min(skipna=True)
        for i, col in enumerate(df.columns):
            if col in price_cols and row[col] == min_price:
                styles[i] = "background-color: #d4edda; font-weight: bold;"
        return styles
    return df.style.apply(style_row, axis=1)

# --- Run Pipeline Button ---
if st.button("Run Pipeline"):
    st.info(f"Starting pipeline for query '{query}' in category '{category}'...")

    if not query.strip():
        st.warning("❌ Please enter a product query before running the pipeline.")
    else:
        # #Step 1: Scraping (optional)
        # try:
        #     scrape_by_category(category, query)
        #     st.success("✅ Scraping completed.")
        # except Exception as e:
        #     st.error(f"❌ Scraping failed: {e}")

        # Step 2: Preprocessing
        st.subheader("⿢ Preprocessing")
        try:
            preprocess_all()
            st.success("✅ Preprocessing completed.")
        except Exception as e:
            st.error(f"❌ Preprocessing failed: {e}")
        
        # Step 2: Load processed data
        df_loaded = load_processed_data(category, query)
        st.session_state.df_loaded = df_loaded  # store globally


        # # Step 4: Cleanup (optional)
        # st.subheader("4️⃣ Cleanup")
        # try:
        #     cleanup_data_folders()
        #     st.success("✅ All raw and processed CSVs have been deleted.")
        # except Exception as e:
        #     st.error(f"❌ Cleanup failed: {e}")

# --- Reactive Filtering & Display ---
if "df_loaded" in st.session_state and not st.session_state.df_loaded.empty:
    df_filtered = filter_by_query(st.session_state.df_loaded, query)
    df_filtered = apply_filters(df_filtered, original_df=df_filtered)
    df_grouped, price_cols = group_variants_to_row(df_filtered)
    
    st.success(f"Found {len(df_grouped)} products!")
    st.dataframe(highlight_lowest_price(df_grouped, price_cols))
