import pandas as pd
from pathlib import Path
from typing import Optional

DATA_PATH = Path(__file__).parent.parent / "wine-ratings.csv"

_df: Optional[pd.DataFrame] = None


def get_data() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_PATH, index_col=0)
        _df = _df.drop(columns=["grape"], errors="ignore")
        _df["rating"] = pd.to_numeric(_df["rating"], errors="coerce")
    return _df


def reset_data():
    global _df
    _df = None
