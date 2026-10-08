import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_table(
    url: str = "https://www.vlr.gg/event/stats/2766/valorant-champions-2026",
    tag: str = "table",
    class_tag: str = "st-table mod-hide-maps mod-hide-fbpr mod-hide-fdpr mod-hide-fk mod-hide-fd",
) -> pd.DataFrame:
    """
    Extracting a table from website using requests and beautifulsoup4 modules.

    Args:
        url (str, optional): URL of the VLR statistics page to scrape. Defaults to "https://www.vlr.gg/event/stats/2766/valorant-champions-2026".
        tag (str, optional): HTML tag used to locate the target table. Defaults to "table".
        class_tag (str, optional): CSS class used to identify the relevant stats table. Defaults to "st-table mod-hide-maps mod-hide-fbpr mod-hide-fdpr mod-hide-fk mod-hide-fd".

    Returns:
        pd.DataFrame: Parsed table data as a pandas DataFrame ready for cleaning and analysis.
    """
    try:
        logger.info("Accessing %s...", url)
        response = requests.get(url, timeout=5)
        # Explicitly raise an error for 4xx or 5xx status codes
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Catches ConnectionError, Timeout, HTTPError, etc.
        logger.error("A requests error occurred: %s", e)
        raise RuntimeError(f"Unable to fetch data from {url}: {e}") from e

    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find(
        tag,
        class_=class_tag,
    )
    if table is None:
        raise RuntimeError(f"No table matching class '{class_tag}' was found on {url}.")

    # Get headers of the table
    headers = [header.text.strip().lower() for header in table.find_all("th")]
    # Add custom header to store agent lists
    headers.append("agents_list")

    logger.info("Get table headers: %s", headers)
    # Initiate dataframe to store headers and data
    df = pd.DataFrame(columns=headers)

    # Looping through each row to get data
    for row in table.find_all("tr")[1:]:
        data = row.find_all("td")
        row_data = [
            td.text.strip()
            for td in data
            if not (td.find("img") and not td.get_text(strip=True))
        ]

        # Skip empty rows (like header rows inside tbody)
        if not row_data:
            continue

        agents_list = row.find_all("img")
        agents = [img["src"].split("/")[-1].split(".")[0] for img in agents_list]
        agents_str = ", ".join(agents)

        # Combine text data and agents into a single row
        full_row = row_data + [agents_str]
        logger.info("Adding %s to dataframe.", full_row)
        # Append to DataFrame
        df.loc[len(df)] = full_row

    logger.info("Total rows added: %s", len(df))
    logger.info("DataFrame head: %s", df.head())
    return df
