import requests
from bs4 import BeautifulSoup

def scrape_webpage(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return ""  # Return an empty string if there's an error