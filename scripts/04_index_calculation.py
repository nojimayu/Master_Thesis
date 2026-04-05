"""
04_index_calculation.py
-----------------------
Compute the LLM-specific occupational exposure index for each CH-ISCO-19
occupation, using the calibrated μ weights from script 03.

The index combines task-level LLM substitutability scores (derived from
O*NET data and μ weights) into an occupation-level composite, optionally
employment-weighted for Swiss aggregate statistics.

Input  (data/processed/):
  - onet_ch_mapped.parquet
  - mu_weights.parquet

Output (data/output/):
  - exposure_index.parquet   – occupation-level exposure scores
  - exposure_index.csv       – same, human-readable
"""

import pathlib
import numpy as np
import pandas as pd

PROCESSED_DIR = pathlib.Path("data/processed")
OUTPUT_DIR = pathlib.Path("data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_inputs():
    mapped = pd.read_parquet(PROCESSED_DIR / "onet_ch_mapped.parquet")
    mu = pd.read_parquet(PROCESSED_DIR / "mu_weights.parquet")
    return mapped, mu


def compute_task_scores(mapped: pd.DataFrame, mu: pd.DataFrame) -> pd.DataFrame:
    """
    Join calibrated μ weights onto the O*NET task data and compute a
    weighted task-level LLM exposure score.
    """
    value_col = (
        "data_value"
        if "data_value" in mapped.columns
        else mapped.select_dtypes(include=np.number).columns[0]
    )
    element_col = "element_id" if "element_id" in mapped.columns else mapped.columns[0]

    # Average data_value per (isco4, element_id, onet_category)
    agg = (
        mapped.groupby(["isco4", element_col, "onet_category"], as_index=False)[value_col]
        .mean()
        .rename(columns={value_col: "task_score"})
    )

    # Merge μ weights
    task_df = agg.merge(mu, on=["onet_category", element_col], how="left")
    task_df["mu"].fillna(0.0, inplace=True)

    # Weighted score
    task_df["weighted_score"] = task_df["task_score"] * task_df["mu"]
    return task_df


def aggregate_to_occupation(
    task_df: pd.DataFrame, mapped: pd.DataFrame
) -> pd.DataFrame:
    """
    Aggregate task-level weighted scores to occupation level (isco4).
    Uses employment-weighted mean when weights are available.
    """
    occ_scores = (
        task_df.groupby("isco4", as_index=False)["weighted_score"]
        .sum()
        .rename(columns={"weighted_score": "raw_exposure"})
    )

    # Normalise to [0, 1]
    min_val = occ_scores["raw_exposure"].min()
    max_val = occ_scores["raw_exposure"].max()
    occ_scores["exposure_index"] = (
        (occ_scores["raw_exposure"] - min_val) / (max_val - min_val)
        if max_val > min_val
        else 0.0
    )

    # Attach employment weights and occupation labels if available
    emp_cols = [c for c in mapped.columns if c in ("employment_weight", "isco4")]
    if "employment_weight" in mapped.columns:
        emp = (
            mapped[["isco4", "employment_weight"]]
            .drop_duplicates("isco4")
        )
        occ_scores = occ_scores.merge(emp, on="isco4", how="left")

    # Attach occupation label if present
    label_col = next(
        (c for c in mapped.columns if "title" in c or "label" in c or "bezeichnung" in c),
        None,
    )
    if label_col:
        labels = mapped[["isco4", label_col]].drop_duplicates("isco4")
        occ_scores = occ_scores.merge(labels, on="isco4", how="left")

    return occ_scores


def main():
    print("=== 04 Index Calculation ===")

    mapped, mu = load_inputs()
    print(f"  Mapped rows: {len(mapped):,} | μ elements: {len(mu):,}")

    task_df = compute_task_scores(mapped, mu)
    print(f"  Task-level rows: {len(task_df):,}")

    occ_df = aggregate_to_occupation(task_df, mapped)
    print(f"  Occupations: {len(occ_df):,}")

    # Save outputs
    parquet_out = OUTPUT_DIR / "exposure_index.parquet"
    csv_out = OUTPUT_DIR / "exposure_index.csv"
    occ_df.to_parquet(parquet_out, index=False)
    occ_df.to_csv(csv_out, index=False)
    print(f"\nSaved → {parquet_out}")
    print(f"Saved → {csv_out}")

    # Quick summary
    print("\nExposure index summary:")
    print(occ_df["exposure_index"].describe().round(3).to_string())
    print("\nTop 10 most exposed occupations:")
    top10 = occ_df.nlargest(10, "exposure_index")[["isco4", "exposure_index"]]
    print(top10.to_string(index=False))
    print("\nDone.")


if __name__ == "__main__":
    main()
