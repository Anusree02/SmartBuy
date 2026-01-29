# main.py

from product_matching.query_handler import load_all_processed_data
from product_matching.grouping import group_variants
from product_matching.presenter import show_grouped_results_table

def run_query(category: str, query: str):
    """
    Run a product matching query by loading all processed files,
    filtering by query, grouping variants, and showing results in table format.
    """
    print(f"\n🔍 Running query: '{query}' in category: '{category}'")

    # Step 1: Load all processed CSVs and filter by query
    df = load_all_processed_data(query)

    if df.empty:
        print("⚠️ No products found for this query.")
        return

    # Step 2: Group variants
    grouped = group_variants(df, query)

    # Step 3: Show table-style output
    show_grouped_results_table(grouped)


if __name__ == "__main__":
    # Example query: change as needed
    run_query("electronics", "macbook air")
