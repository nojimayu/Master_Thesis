"""
01_data_cleaning.py
-------------------
Load and clean raw data sources:
  - O*NET 30.2 xlsx files (Skills, Abilities, Work Activities, Knowledge)
  - Swiss occupational classification with BFS employment data (CH_ISCO19.xlsx)
  - ISCO–SOC crosswalk (isco_soc_crosswalk.xls)

Outputs cleaned DataFrames saved to data/processed/.
"""

import pathlib
import pandas as pd

RAW_DIR = pathlib.Path("data/raw")
PROCESSED_DIR = pathlib.Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

ONET_DIR = RAW_DIR / "onet"

ONET_FILES = {
    "skills": "Skills.xlsx",
    "abilities": "Abilities.xlsx",
    "work_activities": "Work Activities.xlsx",
    "knowledge": "Knowledge.xlsx",
}

CH_ISCO_FILE = RAW_DIR / "CH_ISCO19.xlsx"
CROSSWALK_FILE = RAW_DIR / "isco_soc_crosswalk.xls"


def load_onet_table(name: str, filename: str) -> pd.DataFrame:
    """Load a single O*NET category file and apply basic cleaning."""
    path = ONET_DIR / filename
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    df["onet_category"] = name
    print(f"  Loaded {name}: {len(df):,} rows")
    return df


def load_ch_isco(path: pathlib.Path) -> pd.DataFrame:
    """Load Swiss ISCO-19 classification with BFS employment figures."""
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    print(f"  Loaded CH_ISCO19: {len(df):,} rows")
    return df


def load_crosswalk(path: pathlib.Path) -> pd.DataFrame:
    """Load ISCO–SOC crosswalk table."""
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    print(f"  Loaded crosswalk: {len(df):,} rows")
    return df


def main():
    print("=== 01 Data Cleaning ===")

    # --- O*NET tables ---
    print("\nLoading O*NET tables …")
    onet_frames = []
    for name, filename in ONET_FILES.items():
        onet_frames.append(load_onet_table(name, filename))
    onet_df = pd.concat(onet_frames, ignore_index=True)
    onet_out = PROCESSED_DIR / "onet_combined.parquet"
    onet_df.to_parquet(onet_out, index=False)
    print(f"  Saved → {onet_out}")

    # --- Swiss classification ---
    print("\nLoading CH_ISCO19 …")
    ch_df = load_ch_isco(CH_ISCO_FILE)
    ch_out = PROCESSED_DIR / "ch_isco19_clean.parquet"
    ch_df.to_parquet(ch_out, index=False)
    print(f"  Saved → {ch_out}")

    # --- ISCO–SOC crosswalk ---
    print("\nLoading ISCO–SOC crosswalk …")
    cw_df = load_crosswalk(CROSSWALK_FILE)
    cw_out = PROCESSED_DIR / "isco_soc_crosswalk_clean.parquet"
    cw_df.to_parquet(cw_out, index=False)
    print(f"  Saved → {cw_out}")

    print("\nDone – all cleaned files saved to data/processed/")


if __name__ == "__main__":
    main()
