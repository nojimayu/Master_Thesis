# Master's Thesis – LLM-Specific Labor Market Exposure in Switzerland

This repository contains the code and analysis pipeline for my Master's thesis, which
examines how large language models (LLMs) differentially affect occupational exposure
in the Swiss labor market.  The methodology builds on O\*NET 30.2 task data, the Swiss
occupational classification (CH-ISCO-19), and BFS employment statistics.

---

## Repository Structure

```
data/
├── raw/
│   ├── onet/                  # O*NET 30.2 xlsx files (Skills, Abilities, Work Activities, Knowledge)
│   ├── CH_ISCO19.xlsx         # Swiss occupational classification + BFS employment data
│   └── isco_soc_crosswalk.xls # ISCO–SOC crosswalk
├── processed/                 # Cleaned and mapped datasets (auto-generated)
└── output/                    # Index values and analysis datasets (auto-generated)
scripts/
├── 01_data_cleaning.py        # Load & clean all raw data sources
├── 02_mapping_onet_chisco.py  # Map O*NET SOC codes → CH-ISCO-19 via crosswalk
├── 03_mu_calibration.py       # Calibrate μ exposure weights per O*NET dimension
├── 04_index_calculation.py    # Compute occupation-level LLM exposure index
└── 05_statistical_analysis.R  # Descriptive stats, plots, and regressions
notebooks/
└── exploratory_analysis.ipynb # Interactive EDA sandbox
requirements.txt               # Python dependencies
README.md
```

---

## Data Sources

| File | Source | Notes |
|------|--------|-------|
| `data/raw/onet/Skills.xlsx` | [O\*NET 30.2](https://www.onetcenter.org/database.html) | Skills scores by SOC occupation |
| `data/raw/onet/Abilities.xlsx` | O\*NET 30.2 | Abilities scores |
| `data/raw/onet/Work Activities.xlsx` | O\*NET 30.2 | Work activity ratings |
| `data/raw/onet/Knowledge.xlsx` | O\*NET 30.2 | Knowledge domain scores |
| `data/raw/CH_ISCO19.xlsx` | [BFS](https://www.bfs.admin.ch) | Swiss ISCO-19 classification + employment counts |
| `data/raw/isco_soc_crosswalk.xls` | BLS / ILO | Crosswalk linking SOC codes to ISCO-08 |

> **Note:** Raw data files are **not** committed to this repository.  Download them from
> the sources listed above and place them in the paths shown before running the pipeline.

---

## Setup

### Python environment

```bash
pip install -r requirements.txt
```

### R environment

Open `scripts/05_statistical_analysis.R` in RStudio and install the required packages:

```r
install.packages(c("tidyverse", "arrow", "ggplot2", "scales", "broom"))
```

---

## Running the Pipeline

Execute the scripts in order from the repository root:

```bash
python scripts/01_data_cleaning.py
python scripts/02_mapping_onet_chisco.py
python scripts/03_mu_calibration.py
python scripts/04_index_calculation.py
Rscript scripts/05_statistical_analysis.R
```

Intermediate files are saved in `data/processed/`; final outputs (index, figures,
regression tables) are saved in `data/output/`.

---

## Exploratory Notebook

```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```

---

## Methodology Overview

1. **Data cleaning** – standardise column names, drop duplicates, handle missing values
   across O\*NET tables and the Swiss classification.
2. **Mapping** – link O\*NET SOC-based occupations to CH-ISCO-19 via the ISCO–SOC
   crosswalk; attach BFS employment weights.
3. **μ calibration** – estimate per-dimension exposure weights (μ) reflecting LLM
   task substitutability for each O\*NET category.
4. **Index calculation** – aggregate weighted task scores to an occupation-level
   exposure index, normalised to [0, 1].
5. **Statistical analysis** – descriptive statistics, distributional plots,
   employment-weighted means, and OLS regressions in R.

---

## License

This repository is for academic research purposes.  Please contact the author before
reusing any part of the code or analysis.