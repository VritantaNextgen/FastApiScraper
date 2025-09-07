import requests
from bs4 import BeautifulSoup
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import sys

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
        url = f"https://www.flipkart.com/search?q={product_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        html_content = response.text

        # If you need to reference the existing HTML file, uncomment the following line:
        # with open('flipkart_page.html', 'r', encoding='utf-8') as file:
        #     html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all product cards
        # (Note: The class 'product-card' may need to be adjusted based on actual HTML)
        products = soup.find_all('div', class_='tUxRFH')

        product_data = []
        for product in products:
            # Extract Name
            # This assumes the structure from the flipkart_page.html reference
            name_element = product.find('div', class_='KzDlHZ')
            name = name_element.text.strip() if name_element else 'Name not found'
            
            # Extract Rating and Reviews
            rating_element = product.find('div', class_='XQDdHH')
            reviews_element = product.find('div', class_='_5OesEi')
            
            rating = rating_element.text.strip() if rating_element else 'Rating not found'
            reviews_re = re.findall(r'\xa0(\d+\s*Reviews)', reviews_element.text.strip())
            reviews = reviews_re if len(reviews_re)>0 else 'Reviews not found'
            
            # Extract Price
            price_element = product.find('div', class_='Nx9bqj _4b5DiR')
            price = price_element.text.strip() if price_element else 'Price not found'
            
            # Extract Description
            description_elements = product.find_all('li', class_='J+igdf')
            description = ' '.join([elem.text.strip() for elem in description_elements]) if description_elements else 'Description not found'

            product_data.append({
                'name': name,
                'reviews': reviews,
                'rating': rating,
                'price': price,
                'description': description
            })

        return product_data
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        line_number = exc_traceback.tb_lineno
        file_name = exc_traceback.tb_frame.f_code.co_filename
        error_message = str(e)
        print(f"Error: {error_message} (Type: {exc_type.__name__})")
        print(f"Occurred in file: {file_name}, line: {line_number}")
        # Optional: print full traceback
        traceback.print_exc()
        return None

