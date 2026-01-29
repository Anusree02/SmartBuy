# product_matching/grouping.py
import pandas as pd
def group_variants(df, query):
    grouped_list = []
    for idx, row in df.iterrows():
        grouped_list.append({
            "title": row["Product"],   # ✅ capitalized
            "website": row["Website"], # ✅ capitalized
            "price": row.get("Price", None),
            "discount": row.get("Discount", None),
            "rating": row.get("Rating", None),
            "no_of_review": row.get("No_of_review", None),
            "category": row.get("Category", None),
            "link": row.get("Link", None)
        })
    return pd.DataFrame(grouped_list)
