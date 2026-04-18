# scraper/scrape_books.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import time

# Your Django server URL
API_URL = "http://127.0.0.1:8000/api/books/upload/"

def scrape_and_store(pages=5):
    options = Options()
    options.add_argument("--headless")  # run without opening browser window
    driver = webdriver.Chrome(options=options)

    for page in range(1, pages + 1):
        url = f"http://books.toscrape.com/catalogue/page-{page}.html"
        driver.get(url)
        time.sleep(2)  # wait for page to load

        items = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")

        for item in items:
            try:
                title = item.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("title")
                rating_class = item.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class")
                rating = convert_rating(rating_class)  # e.g "Three" → 3
                book_url = item.find_element(By.TAG_NAME, "a").get_attribute("href")

                # Build the data dict matching your Django model fields
                book_data = {
                    "title": title,
                    "author": "Unknown",        # books.toscrape doesn't show author on listing
                    "rating": str(rating),
                    "reviews": "",
                    "description": "",
                    "book_url": book_url,
                }

                # POST to your Django API
                response = requests.post(API_URL, json=book_data)

                if response.status_code == 201:
                    print(f"✅ Saved: {title}")
                else:
                    print(f"❌ Failed: {title} — {response.json()}")

            except Exception as e:
                print(f"Error scraping item: {e}")
                continue

    driver.quit()
    print("Scraping complete!")


def convert_rating(rating_class):
    # rating_class looks like "star-rating Three"
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for word, num in mapping.items():
        if word in rating_class:
            return num
    return 0


if __name__ == "__main__":
    scrape_and_store(pages=5)  # scrapes 5 pages = ~100 books