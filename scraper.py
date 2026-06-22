import io

import pandas as pd
import soupsieve as sv
from bs4 import BeautifulSoup
from curl_cffi import requests

from downloader import get_html_stream


def fetch_html(session: requests.Session, url: str) -> str:
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestsError as e:
        print(f"Network error while fetching URL: {e}")
        raise


def parse_team_gamelog(html_stream: io.StringIO) -> pd.DataFrame:
    soup = BeautifulSoup(html_stream, "lxml")

    table = soup.select_one('table:has(caption:-soup-contains("Regular Season"))')

    if not table:
        print("Warning: Regular season not found.")
        return pd.DataFrame()

    header_selector = sv.compile(
        "thead tr:not(.over_header) th[data-stat]:not([data-stat='DUMMY'])"
    )
    header_cells = header_selector.select(table)

    stat_keys = [th["data-stat"] for th in header_cells]

    all_games_data = []

    cell_selector = sv.compile(
        "th[data-stat]:not([data-stat='DUMMY']), td[data-stat]:not([data-stat='DUMMY'])"
    )

    for row in table.select("tbody tr:has([data-stat='ranker'])"):
        # we extract all non-DUMMY metric cells in this row
        cells = cell_selector.select(row)

        # We then zip the pre-calculated keys directly with the ordered cells
        # this allows to skip scanning the DOM in our nested loop.
        game_metrics = {
            key: cell.get_text(strip=True) for key, cell in zip(stat_keys, cells)
        }
        all_games_data.append(game_metrics)

    gamelog_df = pd.DataFrame(all_games_data, columns=stat_keys)

    return gamelog_df


def main():
    teams = ["NYL"]
    years = [2026]

    session = requests.Session(impersonate="chrome")

    for year in years:
        for team in teams:
            team_log_url = f"https://www.basketball-reference.com/wnba/teams/{team}/{year}/gamelog/"

            cache_filename = f"wnba_{team}_{year}_gamelog.html"

            try:
                html_stream = get_html_stream(session, team_log_url, cache_filename)

                table_df = parse_team_gamelog(html_stream)

                print(
                    f"Successfully processed {team} ({year}). Shape: {table_df.shape}"
                )
                print(table_df.info(verbose=True))

            except Exception as e:
                raise RuntimeError("Caught fatal error") from e


if __name__ == "__main__":
    main()
