import sys
from pathlib import Path

from config import RAW_DATA
from utils.data import build_week_panel, load_data


def main() -> int:
    if not RAW_DATA.exists():
        print(f"Missing data file: {RAW_DATA}")
        return 1

    df = load_data(RAW_DATA)
    panel = build_week_panel(df)

    seasons = panel["season"].nunique(dropna=True)
    print(f"Loaded {len(df)} contestants, panel rows: {len(panel)}, seasons: {seasons}")
    print("Next: implement fan vote estimation and scheme simulation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
