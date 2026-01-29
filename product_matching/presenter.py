# product_matching/presenter.py
import pandas as pd

def show_grouped_results_table(grouped_results: dict):
    """
    Display grouped results in a table format:
    Each row = product variant, columns = websites with prices
    """
    for group_name, items in grouped_results.items():
        print(f"\n🔹 {group_name}\n")

        # Create a dataframe with product titles as rows and websites as columns
        data = {}
        for item in items:
            title = item['title']
            website = item['website']
            price = item['price']
            
            if title not in data:
                data[title] = {}
            data[title][website] = price

        df_table = pd.DataFrame.from_dict(data, orient='index').fillna("-")
        df_table.index.name = "Product Variant"
        print(df_table)
