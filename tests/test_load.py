import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load import load_to_parquet


def test_load_to_parquet(tmp_path):
    df = pd.DataFrame({"player": ["A"], "rating": [1.2]})
    path = tmp_path / "nested" / "stats.parquet"

    load_to_parquet(df, str(path))

    assert path.exists()
    result = pd.read_parquet(path)
    pd.testing.assert_frame_equal(result, df)
