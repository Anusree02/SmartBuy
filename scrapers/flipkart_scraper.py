import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class FlipkartScraper:

    def __init__(self, search_query="laptop", category="electronics", chromedriver_path=None):
        self.search_query = search_query
        self.category = category
        self.url = f"https://www.flipkart.com/search?q={search_query}"

        options = Options()
        options.add_argument("--start-maximized")
        service = Service(chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)

        # Storage
        self.data = {
            "Product": [],
            "Price": [],
            "Discount": [],
            "Ratings": [],
            "Reviews Count": [],
            "Category": [],
            "Link": []
        }

    def page_load(self):
        self.driver.get(self.url)
        time.sleep(3)

    def data_scrap(self, max_pages=3):
        for page in range(1, max_pages + 1):
            paginated_url = f"{self.url}&page={page}"
            self.driver.get(paginated_url)
            time.sleep(3)

            page_html = self.driver.page_source
            soup = BeautifulSoup(page_html, "html.parser")
            products = soup.find_all("div", class_="tUxRFH")

            for product in products:
                # Name
                try:
                    name = product.find("div", class_="KzDlHZ").text.strip()
                except:
                    name = None

                # Price
                try:
                    price = product.find("div", class_="Nx9bqj").text.strip().replace("₹", "").replace(",", "")
                except:
                    price = None

                # Rating
                try:
                    rating_value = product.find("div", class_="XQDdHH").text.strip()
                    rating = f"{rating_value} out of 5 stars"
                except:
                    rating = None

                # Reviews Count
                try:
                    reviews_text = product.find("span", class_="Wphh3N").text.strip()
                    if "Reviews" in reviews_text:
                        reviews = reviews_text.split("&")[-1].replace("Reviews", "").strip()
                    else:
                        reviews = None
                except:
                    reviews = None

                # Discount
                try:
                    discount = product.find("div", class_="UkUFwK").text.strip()
                except:
                    discount = None

                # Link
                try:
                    link = "https://www.flipkart.com" + product.find("a", href=True)["href"]
                except:
                    link = None

                # Save
                self.data["Product"].append(name)
                self.data["Price"].append(price)
                self.data["Discount"].append(discount)
                self.data["Ratings"].append(rating)
                self.data["Reviews Count"].append(reviews)
                self.data["Category"].append(self.category)
                self.data["Link"].append(link)

            print(f"✅ Scraped page {page}")

    def save_csv(self):
        df = pd.DataFrame(self.data)

        # === save into /data/raw with format flipkart_category_query.csv ===
        raw_data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
        os.makedirs(raw_data_dir, exist_ok=True)

        file_name = f"flipkart_{self.category}_{self.search_query}.csv".replace(" ", "_")
        output_file = os.path.join(raw_data_dir, file_name)

        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"✅ Data saved to {output_file}")

    def tearDown(self):
        self.driver.quit()


# === Wrapper function for scrape_by_category ===
def scrape_flipkart(search_query, category, chromedriver_path, max_pages=3):
    scraper = FlipkartScraper(search_query=search_query, category=category, chromedriver_path=chromedriver_path)
    scraper.page_load()
    scraper.data_scrap(max_pages=max_pages)
    scraper.save_csv()
    scraper.tearDown()
    print("🎉 Flipkart scraping completed")
