import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.transform import (
    cast_data_types,
    clean_scraped_data,
    rename_and_filter_columns,
    strip_and_lowercase_column_names,
    strip_player_and_team,
    to_numeric_safe,
    transform_to_dataframe,
)


def test_transform_to_dataframe(tmp_path):
    df = pd.DataFrame({"player": ["A"], "rating": [1.2]})
    path = tmp_path / "stats.parquet"
    df.to_parquet(path, engine="pyarrow")

    result = transform_to_dataframe(path)

    pd.testing.assert_frame_equal(result, df)


def test_strip_and_lowercase_column_names():
    df = pd.DataFrame([[1, 2]], columns=[" Player ", " Map "])

    result = strip_and_lowercase_column_names(df)

    assert list(result.columns) == ["player", "map"]


def test_strip_player_and_team():
    df = pd.DataFrame({"player": ["trent\nG2", "Asuna\n100T"]})

    result = strip_player_and_team(df)

    assert list(result.columns) == ["player", "player_name", "team"]
    assert result["player_name"].tolist() == ["trent", "Asuna"]
    assert result["team"].tolist() == ["G2", "100T"]


def test_rename_and_filter_columns():
    df = pd.DataFrame(
        [
            {
                "player_name": "trent",
                "team": "G2",
                "agents_list": "sova, fade",
                "maps": 10,
                "rnd": 20,
                "r": 1.25,
                "acs": 180,
                "k:d": 1.1,
                "kast": 75,
                "adr": 120,
                "kpr": 0.8,
                "apr": 0.6,
                "fk:fd": 1.2,
                "fk%": 30,
                "fd%": 25,
                "hs%": 40,
                "cl%": 8,
                "cl": 4,
                "kmax": 18,
                "k": 35,
                "d": 20,
                "a": 15,
                "fk": 11,
                "fd": 7,
            }
        ]
    )

    result = rename_and_filter_columns(df)

    assert "maps_played" in result.columns
    assert "maps" not in result.columns
    assert "rating" in result.columns
    assert list(result.columns) == [
        "player_name",
        "team",
        "agents_list",
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
        "firsts_deaths_percentage",
        "headshot_pct",
        "clutch_pct",
        "clutch_won",
        "most_kilss_in_map",
        "total_kills",
        "total_deaths",
        "total_assists",
        "total_first_kills",
        "total_first_deaths",
    ]


def test_to_numeric_safe_handles_percentages_and_missing():
    series = pd.Series(["1.5", "20%", "N/A", "—", "1,000"])

    result = to_numeric_safe(series, strip_percent=True)

    assert result.iloc[0] == pytest.approx(1.5)
    assert result.iloc[1] == pytest.approx(20.0)
    assert pd.isna(result.iloc[2])
    assert pd.isna(result.iloc[3])
    assert result.iloc[4] == pytest.approx(1000.0)


def test_cast_data_types():
    df = pd.DataFrame(
        [
            {
                "player_name": "  Faker  ",
                "team": "  T1  ",
                "agents_list": "  Jett, Omen  ",
                "maps_played": "10",
                "rounds_played": "20",
                "rating": "1.37",
                "avg_combat_score": "150",
                "kills_deaths": "1.6",
                "kast": "72%",
                "avg_damage_per_round": "110",
                "kills_per_round": "0.7",
                "assists_per_round": "0.3",
                "first_kills_first_deaths": "1.2",
                "first_kills_percentage": "55%",
                "firsts_deaths_percentage": "40%",
                "headshot_pct": "36%",
                "clutch_pct": "5%",
                "clutch_won": "1",
                "most_kilss_in_map": "10",
                "total_kills": "25",
                "total_deaths": "11",
                "total_assists": "12",
                "total_first_kills": "7",
                "total_first_deaths": "4",
            }
        ]
    )

    result = cast_data_types(df)

    assert result["player_name"].iloc[0] == "Faker"
    assert result["team"].iloc[0] == "T1"
    assert result["agents_list"].iloc[0] == "Jett, Omen"
    assert str(result["maps_played"].dtype) == "Int64"
    assert result["rating"].iloc[0] == pytest.approx(1.37)
    assert result["kast"].iloc[0] == 72
    assert result["headshot_pct"].iloc[0] == pytest.approx(36.0)
    assert result["clutch_won"].iloc[0] == "1"


def test_clean_scraped_data():
    df = pd.DataFrame(
        [
            {
                "player": "FNC\nG2",
                "agents_list": "Jett, Omen",
                "maps": "10",
                "rnd": "20",
                "r": "1.3",
                "acs": "180",
                "k:d": "1.1",
                "kast": "75%",
                "adr": "120",
                "kpr": "0.9",
                "apr": "0.4",
                "fk:fd": "1.0",
                "fk%": "30%",
                "fd%": "25%",
                "hs%": "40%",
                "cl%": "8%",
                "cl": "4",
                "kmax": "18",
                "k": "30",
                "d": "20",
                "a": "16",
                "fk": "12",
                "fd": "7",
            }
        ]
    )

    result = clean_scraped_data(df)

    assert "player_name" in result.columns
    assert "team" in result.columns
    assert result["player_name"].iloc[0] == "FNC"
    assert result["team"].iloc[0] == "G2"
    assert result["maps_played"].iloc[0] == 10
    assert result["rating"].iloc[0] == pytest.approx(1.3)
    assert result["kast"].iloc[0] == 75
