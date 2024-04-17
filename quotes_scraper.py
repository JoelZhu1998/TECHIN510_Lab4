import os

import requests
from bs4 import BeautifulSoup
from db import Database
from dotenv import load_dotenv

load_dotenv()
URL = 'https://quotes.toscrape.com/page/{page}/'
mydb = Database(os.getenv('DATABASE_URL'))
mydb.create_table()
mydb.truncate_table()

quotes = []
page = 1
while True: 
    url = URL.format(page = page)
    print(f"Scraping {url}")
    response = requests.get(url)
      
    if 'No quotes found!' in response.text:
        break
  
    soup = BeautifulSoup(response.text, 'html.parser') #lxml
    quote_divs = soup.select('div.quote')

    for quote_div in quote_divs:
        quote = {}
        quote['content'] = quote_div.select_one('span.text').text
        quote['author'] = quote_div.select_one('small.author').text
        quote['author_link'] = quote_div.select('span')[1].select('a')[0]
        quote['tags'] = [tag.text for tag in quote_div.select('a.tag')]
        quote['tag_links'] = [tag['href'] for tag in quote_div.select('a.tag')]
        
        mydb.insert_quote(quote)
        quotes.append(quote)
    page += 1

print(quotes)
