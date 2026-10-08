import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.extract import extract_table


def test_extract_table_parses_html(monkeypatch):
    html = """
    <table class="st-table mod-hide-maps mod-hide-fbpr mod-hide-fdpr mod-hide-fk mod-hide-fd">
      <tr>
        <th>Player</th>
        <th>Maps</th>
        <th>Rating</th>
      </tr>
      <tr>
        <td>trent\nG2</td>
        <td>10</td>
        <td>1.25</td>
        <td><img src="/assets/agents/sova.png" /><img src="/assets/agents/fade.png" /></td>
      </tr>
    </table>
    """

    class DummyResponse:
        text = html

        def raise_for_status(self):
            return None

    def fake_get(url, timeout=5):
        return DummyResponse()

    monkeypatch.setattr("src.extract.requests.get", fake_get)

    df = extract_table(
        url="https://example.com",
        tag="table",
        class_tag="st-table mod-hide-maps mod-hide-fbpr mod-hide-fdpr mod-hide-fk mod-hide-fd",
    )

    assert list(df.columns) == ["player", "maps", "rating", "agents_list"]
    assert df.iloc[0]["player"] == "trent\nG2"
    assert df.iloc[0]["agents_list"] == "sova, fade"
