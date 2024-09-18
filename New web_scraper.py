# web_scraper.py

import requests
from bs4 import BeautifulSoup

def scrape_webpage(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()