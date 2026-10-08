import logging

import pandas as pd

logger = logging.getLogger(__name__)


def transform_to_dataframe(data) -> pd.DataFrame | None:
    """
    Load data from a parquet file into a pandas DataFrame.

    Args:
        data: File path or file-like object pointing to the parquet dataset to load.

    Returns:
        pd.DataFrame | None: DataFrame containing the stored data, or None if the file cannot be read.
    """
    try:
        df = pd.read_parquet(data)
        logger.info("Read %s as dataframe.", data)
        return df
    except (FileNotFoundError, OSError) as e:
        logger.error("An error occured: %s", e)
        return None


def strip_and_lowercase_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize dataframe column names so they are consistent and easy to reference.

    Args:
        df (pd.DataFrame): DataFrame whose column names need to be cleaned.

    Returns:
        pd.DataFrame: A copy of the DataFrame with stripped and lowercase column names.
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    logger.info("Convert columns to lower case: %s", df.columns)
    return df


def strip_player_and_team(df: pd.DataFrame) -> pd.DataFrame:
    """
    Split the combined player and team field into two separate columns.

    Args:
        df (pd.DataFrame): DataFrame containing a single "player" column with a newline-separated player/team value.

    Returns:
        pd.DataFrame: DataFrame with new "player_name" and "team" columns added.
    """
    df[["player_name", "team"]] = df["player"].str.split("\n", expand=True)
    return df


def rename_and_filter_columns(df: pd.DataFrame):
    """
    Rename raw stat columns to the project's canonical names and keep only relevant fields.

    Args:
        df (pd.DataFrame): DataFrame containing raw scraped player statistics.

    Returns:
        pd.DataFrame: DataFrame with standardized column names and only the selected analysis columns retained.
    """
    rename_columns = {
        # "agents_list": "",
        # "agents": "",
        "maps": "maps_played",
        "rnd": "rounds_played",
        "r": "rating",
        "acs": "avg_combat_score",
        "k:d": "kills_deaths",
        # "kast": "",
        "adr": "avg_damage_per_round",
        "kpr": "kills_per_round",
        "apr": "assists_per_round",
        "fk:fd": "first_kills_first_deaths",
        "fk%": "first_kills_percentage",
        "fd%": "first_deaths_percentage",
        "hs%": "headshot_pct",
        "cl%": "clutch_pct",
        "cl": "clutch_won",
        "kmax": "most_kills_in_map",
        "k": "total_kills",
        "d": "total_deaths",
        "a": "total_assists",
        "fk": "total_first_kills",
        "fd": "total_first_deaths",
    }
    df = df.rename(columns=rename_columns)

    filter_columns = [
        "player_name",
        "team",
        "agents_list",
        # "player",
        # "agents",
        "maps_played",
        "rounds_played",
        "rating",
        "avg_combat_score",
        "kills_deaths",
        "kast",
        "avg_damage_per_round",
        "kills_per_round",
        "assists_per_round",
        "first_kills_first_deaths",
        "first_kills_percentage",
        "first_deaths_percentage",
        "headshot_pct",
        "clutch_pct",
        "clutch_won",
        "most_kills_in_map",
        "total_kills",
        "total_deaths",
        "total_assists",
        "total_first_kills",
        "total_first_deaths",
    ]

    df = df[filter_columns]
    logger.info("Succesfully rename and filter columns: %s", df.columns)
    return df


def to_numeric_safe(series, strip_percent=False):
    """
    Convert a messy series of scraped values into numeric data while handling missing entries.

    Args:
        series: Series containing values such as percentages, dashes, or text placeholders.
        strip_percent (bool, optional): If True, removes '%' symbols before conversion. Defaults to False.

    Returns:
        pd.Series: Numeric series with invalid values converted to NaN.
    """
    s = series.astype(str).str.strip()
    if strip_percent:
        s = s.str.replace("%", "", regex=False)

    s = s.replace(
        {
            "—": pd.NA,
            "–": pd.NA,
            "-": pd.NA,
            "--": pd.NA,
            "N/A": pd.NA,
            "n/a": pd.NA,
            "NaN": pd.NA,
        }
    )
    s = s.str.replace(",", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


def cast_data_types(df):
    """
    Convert cleaned columns into the appropriate data types for downstream analysis.

    Args:
        df (pd.DataFrame): DataFrame containing cleaned player statistics.

    Returns:
        pd.DataFrame: DataFrame with string and numeric columns converted to their final target dtypes.
    """

    df["player_name"] = df["player_name"].fillna("").astype(str).str.strip()
    df["team"] = df["team"].fillna("").astype(str).str.strip()
    df["agents_list"] = df["agents_list"].fillna("").astype(str).str.strip()
    df["maps_played"] = to_numeric_safe(df["maps_played"]).astype("Int64")
    df["rounds_played"] = to_numeric_safe(df["rounds_played"]).astype("Int64")
    df["rating"] = to_numeric_safe(df["rating"])
    df["avg_combat_score"] = to_numeric_safe(df["avg_combat_score"]).astype("Int64")
    df["kills_deaths"] = to_numeric_safe(df["kills_deaths"])
    df["kast"] = to_numeric_safe(df["kast"], strip_percent=True).astype("Int64")
    df["avg_damage_per_round"] = to_numeric_safe(df["avg_damage_per_round"])
    df["kills_per_round"] = to_numeric_safe(df["kills_per_round"])
    df["assists_per_round"] = to_numeric_safe(df["assists_per_round"])
    df["first_kills_first_deaths"] = to_numeric_safe(df["first_kills_first_deaths"])
    df["first_kills_percentage"] = to_numeric_safe(
        df["first_kills_percentage"], strip_percent=True
    )
    df["first_deaths_percentage"] = to_numeric_safe(
        df["first_deaths_percentage"], strip_percent=True
    )
    df["headshot_pct"] = to_numeric_safe(df["headshot_pct"], strip_percent=True)
    df["clutch_pct"] = to_numeric_safe(df["clutch_pct"], strip_percent=True)
    df["clutch_won"] = df["clutch_won"].fillna("").astype(str)
    df["most_kills_in_map"] = to_numeric_safe(df["most_kills_in_map"]).astype("Int64")
    df["total_kills"] = to_numeric_safe(df["total_kills"]).astype("Int64")
    df["total_deaths"] = to_numeric_safe(df["total_deaths"]).astype("Int64")
    df["total_assists"] = to_numeric_safe(df["total_assists"]).astype("Int64")
    df["total_first_kills"] = to_numeric_safe(df["total_first_kills"]).astype("Int64")
    df["total_first_deaths"] = to_numeric_safe(df["total_first_deaths"]).astype("Int64")

    return df


def clean_scraped_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the complete cleaning pipeline on scraped player statistics.

    Args:
        df (pd.DataFrame): Raw scraped DataFrame before preprocessing.

    Returns:
        pd.DataFrame: Cleaned DataFrame ready for analysis and reporting.
    """
    return (
        df.pipe(strip_and_lowercase_column_names)
        .pipe(strip_player_and_team)
        .pipe(rename_and_filter_columns)
        .pipe(cast_data_types)
    )
