import sys

from src.extract import extract_table
from src.load import load_to_parquet
from src.transform import clean_scraped_data, transform_to_dataframe

URL = "https://www.vlr.gg/event/stats/2766/valorant-champions-2026"


def main():
    raw_df = extract_table(url=URL)
    load_to_parquet(
        raw_df, r"data\raw\raw_data.parquet", compression="gzip", keep_index=False
    )
    silver_df = transform_to_dataframe(r"data\raw\raw_data.parquet")
    clean_df = clean_scraped_data(silver_df)
    load_to_parquet(
        clean_df,
        r"data\silver\silver_data.parquet",
        compression="gzip",
        keep_index=False,
    )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError:
        print("Failed to run pipleine.")
        sys.exit(1)
