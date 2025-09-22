import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==== CONFIGURATION ====
search_query = "laptop"
chromedriver_path = r"C:\Users\mvanu\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# ==== CHROME DRIVER SETUP ====
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_service = Service(chromedriver_path)
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
wait = WebDriverWait(driver, 10)

# ==== SCRAPE SEARCH RESULTS PAGE ====
driver.get("https://www.amazon.in/")
wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))).send_keys(search_query + Keys.RETURN)
time.sleep(2)
items = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

products = []
prices = []
links = []

for item in items:
    # Product Name from search result
    try:
        name = item.find_element(By.XPATH, ".//span[@class='a-size-medium a-color-base a-text-normal']").text
    except:
        name = None
    products.append(name)

    # Price from search result
    try:
        price = item.find_element(By.XPATH, ".//span[@class='a-price-whole']").text
    except:
        price = None
    prices.append(price)

    # Product page link
    try:
        link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
    except:
        link = None
    links.append(link)

# ==== SCRAPE PRODUCT PAGES FOR DETAILS & Name Fallback ====
discounts = []
ratings = []
reviews_counts = []
categories = []

for idx, link in enumerate(links):
    if not link:
        discounts.append(None)
        ratings.append(None)
        reviews_counts.append(None)
        categories.append(None)
        continue

    driver.get(link)
    wait.until(EC.presence_of_element_located((By.ID, "productTitle")))

    # Fallback product name if missing
    if not products[idx]:
        try:
            products[idx] = driver.find_element(By.ID, "productTitle").text.strip()
        except:
            products[idx] = None

    # Discount
    try:
        discount = driver.find_element(By.CSS_SELECTOR, ".savingsPercentage").text.strip()
    except:
        discount = None
    discounts.append(discount)

    # Ratings
    try:
        ratings.append(driver.find_element(By.ID, "acrPopover").get_attribute("title"))
    except:
        ratings.append(None)

    # Review Count
    try:
        reviews_counts.append(driver.find_element(By.ID, "acrCustomerReviewText").text.strip())
    except:
        reviews_counts.append(None)

    # Category (breadcrumbs)
    try:
        cats = driver.find_elements(By.CSS_SELECTOR, "#wayfinding-breadcrumbs_feature_div ul li span.a-list-item")
        categories.append(" > ".join([c.text.strip() for c in cats if c.text.strip()]))
    except:
        categories.append(None)

driver.quit()

# ==== SAVE TO CSV ====
df = pd.DataFrame({
    "Product": products,
    "Price": prices,
    "Discount": discounts,
    "Ratings": ratings,
    "Reviews Count": reviews_counts,
    "Category": categories,
    "Link": links
})

df.to_csv("amazon_laptop_data.csv", index=False, encoding="utf-8-sig")
print("✅ Scraping complete! Saved to amazon_laptop_data.csv")
