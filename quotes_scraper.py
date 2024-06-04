import os

import requests
import psycopg2
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tqdm import tqdm

load_dotenv()

BASE_URL = "https://books.toscrape.com"

con = psycopg2.connect(os.getenv("DATABASE_URL"))

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

with con:
    with con.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books
            (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                price FLOAT NOT NULL,
                stock INT NOT NULL,
                rating NUMERIC NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

def get_product_links():
    product_links = []
    for pg in tqdm(range(1, 51)):
        response = requests.get(BASE_URL + f"/catalogue/page-{pg}.html")
        soup = BeautifulSoup(response.text, "html.parser")
        # #default > div > div > div > div > section > div:nth-child(2) > ol > li:nth-child(1) > article > h3 > a
        links = [x['href'] for x in soup.select("#default ol li article > h3 > a")]
        product_links.extend(links)
    return product_links

def get_product(product_link):
    response = requests.get(BASE_URL + f'/catalogue/{product_link}')
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.select_one(".product_main > h1").text
    price = float(soup.select_one(".price_color").text[2:])
    stock = int(soup.select_one(".instock.availability").text.split('(')[1].split()[0])
    rating = rating_map[soup.select_one(".star-rating")['class'][1]]
    description = soup.select_one("#product_description + p")
    description = description.text if description else ""

    with con:
        with con.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books (title, price, stock, rating, description) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (title, price, stock, rating, description)
            )

if __name__ == "__main__":
    #get_product('catalogue/a-light-in-the-attic_1000/index.html')
    product_links = get_product_links()
    for link in tqdm(product_links):
        try:
            get_product(link)
        except Exception as e:
            print(e)
            print(link)
    print("Done")
print(quotes)
