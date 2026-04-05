"""
02_mapping_onet_chisco.py
-------------------------
Map O*NET occupations (SOC codes) to Swiss CH-ISCO-19 codes using the
ISCO–SOC crosswalk, and attach BFS employment weights from CH_ISCO19.

Input  (data/processed/):
  - onet_combined.parquet
  - ch_isco19_clean.parquet
  - isco_soc_crosswalk_clean.parquet

Output (data/processed/):
  - onet_ch_mapped.parquet   – O*NET task scores matched to CH-ISCO codes
"""

import pathlib
import pandas as pd

PROCESSED_DIR = pathlib.Path("data/processed")


def load_inputs():
    onet = pd.read_parquet(PROCESSED_DIR / "onet_combined.parquet")
    ch = pd.read_parquet(PROCESSED_DIR / "ch_isco19_clean.parquet")
    crosswalk = pd.read_parquet(PROCESSED_DIR / "isco_soc_crosswalk_clean.parquet")
    return onet, ch, crosswalk


def merge_crosswalk(onet: pd.DataFrame, crosswalk: pd.DataFrame) -> pd.DataFrame:
    """
    Join O*NET data (SOC-based) with the ISCO–SOC crosswalk to obtain
    corresponding ISCO-08 / CH-ISCO-19 codes.
    """
    # Normalise SOC code columns – adjust column names to match your files
    onet_soc_col = "o*net-soc_code" if "o*net-soc_code" in onet.columns else onet.columns[0]
    cw_soc_col = next(
        (c for c in crosswalk.columns if "soc" in c and "2019" in c), crosswalk.columns[0]
    )
    cw_isco_col = next(
        (c for c in crosswalk.columns if "isco" in c), crosswalk.columns[1]
    )

    merged = onet.merge(
        crosswalk[[cw_soc_col, cw_isco_col]].drop_duplicates(),
        left_on=onet_soc_col,
        right_on=cw_soc_col,
        how="left",
    )
    merged.rename(columns={cw_isco_col: "isco_code"}, inplace=True)
    unmapped = merged["isco_code"].isna().sum()
    print(f"  Crosswalk join: {len(merged):,} rows, {unmapped:,} unmatched SOC codes")
    return merged


def attach_employment_weights(mapped: pd.DataFrame, ch: pd.DataFrame) -> pd.DataFrame:
    """
    Attach BFS employment counts from the Swiss classification table so that
    later aggregation can be employment-weighted.
    """
    # Identify ISCO and employment columns – adjust if needed
    ch_isco_col = next((c for c in ch.columns if "isco" in c), ch.columns[0])
    ch_emp_col = next(
        (c for c in ch.columns if "employ" in c or "beschäftig" in c or "employed" in c),
        ch.columns[-1],
    )

    # Match at the 4-digit ISCO level
    mapped["isco4"] = mapped["isco_code"].astype(str).str[:4]
    ch["isco4"] = ch[ch_isco_col].astype(str).str[:4]

    result = mapped.merge(
        ch[["isco4", ch_emp_col]].drop_duplicates("isco4"),
        on="isco4",
        how="left",
    )
    result.rename(columns={ch_emp_col: "employment_weight"}, inplace=True)
    print(f"  After employment join: {len(result):,} rows")
    return result


def main():
    print("=== 02 Mapping O*NET → CH-ISCO ===")

    onet, ch, crosswalk = load_inputs()

    mapped = merge_crosswalk(onet, crosswalk)
    mapped = attach_employment_weights(mapped, ch)

    out_path = PROCESSED_DIR / "onet_ch_mapped.parquet"
    mapped.to_parquet(out_path, index=False)
    print(f"\nSaved → {out_path}")
    print("Done.")


if __name__ == "__main__":
    main()
