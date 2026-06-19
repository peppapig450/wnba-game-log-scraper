from curl_cffi import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

def fetch_html(session: requests.Session, url: str) -> str:
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestsError as e:
        print(f"Network error while fetching URL: {e}")
        raise

teams = ["NYL"]
years = [2026]

session = requests.Session(impersonate="chrome")

for year in years:
    for team in teams:
        team_log_url = f"https://www.basketball-reference.com/wnba/teams/{team}/{year}/gamelog/"


