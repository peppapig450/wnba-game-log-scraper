"""
This script either downloads the basketball-reference HTML to an HTML file locally, or
if that file already exists reads it and returns it in a function. This allows us to iterate
in `scraper.py` with our bs4 logic without getting IP blacklist
"""

import io
import time
from pathlib import Path

from curl_cffi import requests

CACHE_DIR = Path(__file__).parent / "html_cache"
CACHE_DIR.mkdir(exist_ok=True)


def get_html_stream(session: requests.Session, url: str, filename: str) -> io.StringIO:
    """
    Returns an io.StringIO stream of the HTML content.
    Fetches from the web if cached file doesn't exist; otherwise reads from disk.
    """
    cache_path = CACHE_DIR / filename

    if cache_path.exists():
        print(f"[CACHE] Reading {filename} from disk...")
        return io.StringIO(cache_path.read_text(encoding="utf-8"))

    print(f"[NETWORK] Fetching {url} via curl_cffi...")
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()

        time.sleep(4)

        cache_path.write_text(response.text, encoding="utf-8")

        return io.StringIO(response.text)

    except requests.RequestsError as e:
        raise RuntimeError(f"Error fetching {url}") from e

    except OSError as e:
        raise RuntimeError(f"Failed to write cache file {cache_path}") from e
