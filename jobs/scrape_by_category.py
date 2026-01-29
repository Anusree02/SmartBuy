from config.category_mapping import CATEGORY_WEBSITES
from scrapers.flipkart_scraper import scrape_flipkart
from scrapers.amazon_scraper import scrape_amazon
import argparse

CHROMEDRIVER_PATH = r"C:\Users\mvanu\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

def scrape_by_category(category: str, query: str):
    # Normalize category to lowercase for lookup
    websites = CATEGORY_WEBSITES.get(category.lower(), [])
    print(f"🔍 Scraping '{query}' in category '{category}' from {websites}")

    # Amazon scraper
    if "amazon" in websites:
        scrape_amazon(query, category, CHROMEDRIVER_PATH, max_pages=3)

    # Flipkart scraper
    if "flipkart" in websites:
        scrape_flipkart(query, category, CHROMEDRIVER_PATH, max_pages=3)

    # TODO: Add other scrapers (myntra, ajio, etc.)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape a category and query from e-commerce sites")
    parser.add_argument("--category", required=True, help="Product category (e.g., electronics)")
    parser.add_argument("--query", required=True, help="Search query (e.g., laptop)")
    args = parser.parse_args()

    scrape_by_category(args.category, args.query)
