from config.category_mapping import CATEGORY_WEBSITES
from scrapers.flipkart_scraper import scrape_flipkart
from scrapers.amazon_scraper import scrape_amazon

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
        scraper = scrape_flipkart(query, category, CHROMEDRIVER_PATH, max_pages=3)

    # TODO: Add other scrapers (myntra, ajio, etc.)

if __name__ == "__main__":
    scrape_by_category("electronics", "laptop")
