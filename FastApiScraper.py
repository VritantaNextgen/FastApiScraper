import re
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
        # Initialize the Selenium WebDriver (using Chrome)
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.flipkart.com/search?q="+product_name)
        
        # Wait for the page to load (adjust wait time if necessary)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

        ListOfProducts = []
        
        #Parent Container
        Product_Container_Element = driver.find_elements(By.XPATH, "//div [@class= 'tUxRFH']")
        
        if Product_Container_Element: #First View
            for Individual_Product in Product_Container_Element:
                Name_Element = Individual_Product.find_element(By.XPATH, ".//div [@class= 'KzDlHZ']")
                Product_Name = Name_Element.text.strip() if Name_Element else "Name not found"

                Price_Element = Individual_Product.find_element(By.XPATH, ".//div [@class= 'Nx9bqj _4b5DiR']")
                Product_Price = float(re.sub(r'[^\d.]', '', Price_Element.text)) if Price_Element else 0.0

                Rating_Element = Individual_Product.find_elements(By.XPATH, ".//div [@class= 'XQDdHH']")
                if Rating_Element:
                    Product_Rating = Rating_Element[0].text.strip()
                else:
                    Product_Rating = "Not Rated"

                Review_Element = Individual_Product.find_elements(By.XPATH, ".//span [@class='Wphh3N']/span")
                if Review_Element:
                    Product_Review = Review_Element[0].text
                else:
                    Product_Review = "No Reviews"

                Image_Element = Individual_Product.find_element(By.XPATH, ".//img [@class='DByuf4']")
                Product_Image_Link = Image_Element.get_attribute('src')

                Description_Elements = Individual_Product.find_elements(By.XPATH, ".//li [@class='J+igdf']")
                Product_Description = ""
                for description in Description_Elements:
                    Product_Description += description.text +"\n"


                ListOfProducts.append({"name": Product_Name, "price": Product_Price, "rating": Product_Rating, "reviews": Product_Review, "image_url": Product_Image_Link, "description": Product_Description})

        else:
            Product_Container_Element = driver.find_elements(By.XPATH, "//div [@class= 'slAVV4']")
            if Product_Container_Element:
                for Individual_Product in Product_Container_Element:
                    Name_Element = Individual_Product.find_element(By.XPATH, ".//a [@class= 'wjcEIp']")
                    Product_Name = Name_Element.text.strip() if Name_Element else "Name not found"

                    Price_Element = Individual_Product.find_element(By.XPATH, ".//div [@class= 'Nx9bqj']")
                    Product_Price = float(re.sub(r'[^\d.]', '', Price_Element.text)) if Price_Element else 0.0

                    Rating_Element = Individual_Product.find_elements(By.XPATH, ".//div [@class= 'XQDdHH']")
                    if Rating_Element:
                        Product_Rating = Rating_Element[0].text.strip()
                    else:
                        Product_Rating = "Not Rated"

                    Review_Element = Individual_Product.find_elements(By.XPATH, ".//span [@class='Wphh3N']")
                    if Review_Element:
                        Product_Review = Review_Element[0].text
                    else:
                        Product_Review = "No Reviews"

                    Image_Element = Individual_Product.find_element(By.XPATH, ".//img [@class='DByuf4']")
                    Product_Image_Link = Image_Element.get_attribute('src')

                    Description_Elements = Individual_Product.find_elements(By.XPATH, ".//div [@class='NqpwHC']")
                    Product_Description = ""
                    for description in Description_Elements:
                        Product_Description += description.text +"\n"


                    ListOfProducts.append({"name": Product_Name, "price": Product_Price, "rating": Product_Rating, "reviews": Product_Review, "image_url": Product_Image_Link, "description": Product_Description})

        return ListOfProducts

    except Exception as e:
        logging.error(f"An error occurred while scraping {product_name}: {e}")
        driver.quit() if 'driver' in locals() else None
        return None

# # Main driver code remains unchanged for now
# strProductName = input("Enter the product name: ")
# ListOfProducts = get_product_details(strProductName)
# json_string = json.dumps(ListOfProducts)
# print(json_string)
