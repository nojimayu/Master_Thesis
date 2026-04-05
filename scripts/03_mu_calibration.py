"""
03_mu_calibration.py
--------------------
Calibrate the μ (mu) exposure parameter that determines how strongly each
O*NET task dimension contributes to LLM-specific occupational exposure.

Approach
--------
Following Felten et al. (2023) and related literature, we estimate μ as a
vector of regression-based or manual weights over the O*NET task categories
(Skills, Abilities, Work Activities, Knowledge).  The calibration produces a
single weight per category that is later used in script 04 to compute the
composite exposure index.

Input  (data/processed/):
  - onet_ch_mapped.parquet

Output (data/processed/):
  - mu_weights.parquet   – calibrated weights per O*NET category & element
"""

import pathlib
import numpy as np
import pandas as pd

PROCESSED_DIR = pathlib.Path("data/processed")

# ── Default μ weights (can be overridden by expert elicitation) ──────────────
# These weights reflect the relative relevance of each O*NET dimension for
# LLM-task substitutability.  Adjust based on domain expertise or regression.
DEFAULT_MU = {
    "skills": 1.0,
    "abilities": 0.8,
    "work_activities": 1.2,
    "knowledge": 0.6,
}


def load_mapped() -> pd.DataFrame:
    return pd.read_parquet(PROCESSED_DIR / "onet_ch_mapped.parquet")


def compute_category_weights(df: pd.DataFrame, mu_map: dict) -> pd.DataFrame:
    """
    Build a DataFrame of per-element μ weights.

    For each O*NET element we multiply the category-level μ by a normalised
    'data_value' (importance × level score) to get an element-level weight.
    """
    records = []
    for category, cat_mu in mu_map.items():
        subset = df[df["onet_category"] == category].copy()
        if subset.empty:
            print(f"  Warning: no rows for category '{category}' – skipping")
            continue

        # Use 'data_value' if present; fall back to first numeric column
        value_col = (
            "data_value"
            if "data_value" in subset.columns
            else subset.select_dtypes(include=np.number).columns[0]
        )

        # Importance × level composite (if both present)
        if "scale_id" in subset.columns:
            importance = subset[subset["scale_id"] == "IM"][
                ["element_id", value_col]
            ].rename(columns={value_col: "importance"})
            level = subset[subset["scale_id"] == "LV"][
                ["element_id", value_col]
            ].rename(columns={value_col: "level"})
            combined = importance.merge(level, on="element_id", how="inner")
            combined["composite"] = combined["importance"] * combined["level"]
        else:
            element_col = "element_id" if "element_id" in subset.columns else subset.columns[0]
            combined = (
                subset[[element_col, value_col]]
                .groupby(element_col, as_index=False)
                .mean()
                .rename(columns={element_col: "element_id", value_col: "composite"})
            )

        # Normalise within category (0–1)
        max_val = combined["composite"].max()
        combined["mu"] = (combined["composite"] / max_val * cat_mu) if max_val > 0 else 0.0
        combined["onet_category"] = category
        records.append(combined[["onet_category", "element_id", "mu"]])

    return pd.concat(records, ignore_index=True)


def main():
    print("=== 03 μ Calibration ===")
    df = load_mapped()
    print(f"  Input rows: {len(df):,}")

    mu_df = compute_category_weights(df, DEFAULT_MU)
    print(f"  Calibrated weights for {len(mu_df):,} elements")

    out_path = PROCESSED_DIR / "mu_weights.parquet"
    mu_df.to_parquet(out_path, index=False)
    print(f"\nSaved → {out_path}")

    # Summary
    print("\nCategory-level μ summary:")
    print(
        mu_df.groupby("onet_category")["mu"].agg(["mean", "min", "max"]).round(3).to_string()
    )
    print("\nDone.")


if __name__ == "__main__":
    main()
