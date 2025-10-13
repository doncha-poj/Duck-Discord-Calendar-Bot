import requests
from bs4 import BeautifulSoup
import datetime

URL = "https://www.nationaldaycalendar.com/what-day-is-it"

def scrape_todays_day():
    """Scrapes the National Day Calendar website for today's national days"""
    print(f"Fetching national days from {URL} ...")

    try:
        # Use a User-Agent header to mimic a real browser visit
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers)
        # Raise an exception if the request was not successful (e.g., 404 Not Found)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: Could not fetch the webpage. {e}")
        return

scrape_todays_day()