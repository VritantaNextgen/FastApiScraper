from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import sys
import re
import time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ProductRequest(BaseModel):
    product_name: str

@app.post("/scrape/")
async def scrape_product_post(product_request: ProductRequest):
    result = get_product_details(product_request.product_name)
    if result is None:
        return {"error": "Failed to scrape data"}
    return {"products": result}

def get_product_details(product_name: str):
    try:
        # Selenium Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/115.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(options=chrome_options)

        url = f"https://www.flipkart.com/search?q={product_name}"
        driver.get(url)

        debug_filename = f"debug_flipkart_{product_name.replace(' ', '_')}.html"
        with open(debug_filename, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"[DEBUG] Saved page HTML to {debug_filename}")

        # Wait for page to load
        time.sleep(3)

        product_data = []

        # Find all product cards by XPath (original class 'tUxRFH')
        products = driver.find_elements(By.XPATH, "//div[contains(@class,'tUxRFH')]")

        for product in products:
            try:
                # Name
                try:
                    name = product.find_element(By.XPATH, ".//div[contains(@class,'KzDlHZ')]").text.strip()
                except:
                    name = "Name not found"

                # Rating
                try:
                    rating = product.find_element(By.XPATH, ".//div[contains(@class,'XQDdHH')]").text.strip()
                except:
                    rating = "Rating not found"

                # Reviews
                try:
                    reviews_text = product.find_element(By.XPATH, ".//div[contains(@class,'_5OesEi')]").text.strip()
                    reviews_re = re.findall(r'(\d+\s*Reviews)', reviews_text)
                    reviews = reviews_re[0] if len(reviews_re)>0 else "Reviews not found"
                except:
                    reviews = "Reviews not found"

                # Price
                try:
                    price = product.find_element(By.XPATH, ".//div[contains(@class,'Nx9bqj')]").text.strip()
                except:
                    price = "Price not found"

                # Description
                try:
                    desc_elements = product.find_elements(By.XPATH, ".//li[contains(@class,'J+igdf')]")
                    description = " ".join([d.text.strip() for d in desc_elements]) if desc_elements else "Description not found"
                except:
                    description = "Description not found"

                product_data.append({
                    "name": name,
                    "reviews": reviews,
                    "rating": rating,
                    "price": price,
                    "description": description
                })

            except Exception as inner_e:
                print(f"Error parsing product: {inner_e}")

        driver.quit()
        return product_data

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        line_number = exc_traceback.tb_lineno
        file_name = exc_traceback.tb_frame.f_code.co_filename
        error_message = str(e)
        print(f"Error: {error_message} (Type: {exc_type.__name__})")
        print(f"Occurred in file: {file_name}, line: {line_number}")
        traceback.print_exc()
        return None
    

