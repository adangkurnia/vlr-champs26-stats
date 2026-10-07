import pandas as pd
import requests
from bs4 import BeautifulSoup


def extract_table(
    url: str = "https://www.vlr.gg/event/stats/2766/valorant-champions-2026",
    tag: str = "table",
    class_tag: str = "st-table mod-hide-maps mod-hide-fbpr mod-hide-fdpr mod-hide-fk mod-hide-fd",
) -> pd.DataFrame:
    try:
        print(f"Acessing {url}...")
        response = requests.get(url, timeout=5)
        # Explicitly raise an error for 4xx or 5xx status codes
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Catches ConnectionError, Timeout, HTTPError, etc.
        print(f"A requests error occurred: {e}")

    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find(
        tag,
        class_=class_tag,
    )

    # Get headers of the table
    headers = [header.text.strip().lower() for header in table.find_all("th")]
    headers.append("agents_list")

    print(f"Get table headers: {headers}")
    # Initiate dataframe to store headers and data
    df = pd.DataFrame(columns=headers)

    # Looping through each row to get data
    for row in table.find_all("tr")[1:]:
        data = row.find_all("td")
        row_data = [td.text.strip() for td in data]

        # Skip empty rows (like header rows inside tbody)
        if not row_data:
            continue

        agents_list = row.find_all("img")
        agents = [img["src"].split("/")[-1].split(".")[0] for img in agents_list]
        agents_str = ", ".join(agents)

        # Combine text data and agents into a single row
        full_row = row_data + [agents_str]
        print(f"adding {full_row} to dataframe.")
        # Append to DataFrame
        df.loc[len(df)] = full_row

    print(f"total rows added: {len(df)}")
    print(df.head())
    return df
