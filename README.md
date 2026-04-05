# LLM Exposure Index – Schweizer Arbeitsmarkt

**Masterarbeit | ZHAW School of Management and Law**  
Ayumi Nojima | Mai 2026  
Betreuung: Dr. Stefan Koruna

---

## Überblick

Dieses Repository enthält den vollständigen Analysecode zur Masterarbeit
*«LLM-spezifischer Exposure-Index für den Schweizer Arbeitsmarkt»*.

Die Arbeit entwickelt und validiert einen fähigkeitsbasierten Index, der
das technische Beeinflussungspotenzial moderner Large Language Models
(LLMs) auf wissensintensive Schweizer Berufsgruppen (CH-ISCO-19
Hauptgruppen 1–3) quantifiziert. Der Index unterscheidet systematisch
zwischen Substitutions- und Augmentationsanteilen der Exposition und wird
gegen BFS-Beschäftigungsdaten (2022–2024) empirisch validiert.

**Forschungsfrage:**
> Wie stark variiert das LLM-spezifische Exposure-Potenzial zwischen und
> innerhalb wissensintensiver Berufsgruppen (CH-ISCO-19, HG 1–3) in der
> Schweiz, und inwiefern korreliert die Höhe dieses Exposures mit
> beobachtbaren Beschäftigungsveränderungen (BFS 2022–2024)?

---

## Zentrale Ergebnisse

| Hypothese | Befund | Statistik |
|---|---|---|
| **H1** – Gruppenunterschiede | ✓ Bestätigt | ANOVA F=41.80, p<0.001, Eta²=moderat |
| **H1 Sektoral** | ✓ Bestätigt | F=4.10, p=0.002, Eta²=0.116 |
| **H2** – Fähigkeitsprädiktoren | ~ Adoptionslücke | CV R²=−0.088 |
| **H3** – OLS Beschäftigungseffekt | ~ Nicht signifikant | β=+7.12, p=0.137 |
| **H3 Panel FE** | ~ Tendenz | β_DiD=−18.07, p=0.122 |
| **Validierung** vs. Kuprecht (2025) | ⚠ Schwache Korrelation | Pearson r=0.072, p=0.481 |

**Exposure-Rangliste nach Hauptgruppe:**
HG 2 Akademisch (Ø 0.30) > HG 3 Techniker (Ø 0.17) > HG 1 Führungskräfte (Ø 0.06)

**Exposure-Rangliste nach Sektor:**
ICT & Technik > Ingenieurwesen & Naturwiss. > Finanz & Beratung > Recht, Soziales & Kreativ > Gesundheit & Bildung > Führung & Management

---

## Repository-Struktur

```
/
├── data/
│   ├── raw/                          # Rohdaten (nicht versioniert, s. Datenzugang)
│   │   ├── onet/                     # O*NET 30.2 (Skills, Abilities, Work Activities, Knowledge)
│   │   ├── CH_ISCO19.xlsx            # BFS Strukturerhebung 2019–2024 (Einzeljahres-Sheets)
│   │   ├── ESCO_to_ONET-SOC.xlsx     # ESCO→O*NET Crosswalk (onetcenter.org)
│   │   └── stage3_completed.csv      # Manuell kodierte Mapping-Korrekturen (Stufe 3)
│   ├── processed/                    # Bereinigte Zwischendatensätze
│   │   ├── onet_pivot.csv            # O*NET Fähigkeitsmatrix (normiert, w_ij)
│   │   ├── ch_isco_clean.csv         # CH-ISCO-19 HG 1–3
│   │   ├── bfs_clean.csv             # BFS ΔBFS_j 2022→2024
│   │   ├── bfs_panel_2021_2024.csv   # Panel-BFS 3 Jahresschritte
│   │   ├── onet_chisco_mapping.csv   # Vollständiges dreistufiges Mapping
│   │   └── analysis_prep/
│   │       ├── final_sample.csv      # Masterdatensatz (alle Indexwerte)
│   │       ├── mu_weights.csv        # LLM-Gewichte μ_i
│   │       └── skill_vectors_standardized.csv
│   └── output/                       # Analyseergebnisse und Abbildungen
│       ├── dataset_H1.csv
│       ├── dataset_H2.csv
│       ├── dataset_H3.csv
│       ├── dataset_H3_panel.csv      # Long-Format Panel (3 Perioden × 155 ISCO-Codes)
│       ├── dataset_validation.csv
│       ├── EDA/                      # Abbildungen Explorative Datenanalyse
│       └── Hypothesen/               # Abbildungen Hypothesentestung
├── notebooks/
│   ├── 01_llm_exposure_data_preparation.ipynb   # O*NET, CH-ISCO, BFS laden & bereinigen
│   ├── 02_Analysis_preparation.ipynb            # μ_i-Kalibrierung, E_j-Berechnung, Datensätze
│   ├── 03_eda.ipynb                             # Explorative Datenanalyse + Terzil-Analyse
│   ├── 04_hypothesen.ipynb                      # H1–H3 + Panel FE + DiD
│   └── 05_validierung.ipynb                     # Konvergente Validierung vs. Kuprecht (2025)
├── requirements.txt
└── README.md
```

---

## Ausführungsreihenfolge

Die Notebooks müssen **in Reihenfolge** ausgeführt werden, da jedes die
Outputs des Vorgängers lädt:

```
01 → 02 → 03 → 04 → 05
```

Alle Pfade werden relativ zum Repository-Root aufgelöst. Das Notebook
erkennt den Root automatisch.

---

## Installation

```bash
# Repository klonen
git clone https://github.com/[REPOSITORY-URL]
cd llm-exposure-schweiz

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

**Zentrale Pakete:**

| Paket | Version | Zweck |
|---|---|---|
| pandas | ≥2.0 | Datenverwaltung |
| numpy | ≥1.26 | Numerik |
| scikit-learn | ≥1.4 | Random Forest, Clustering, PCA |
| statsmodels | ≥0.14 | OLS-Regression |
| linearmodels | ≥6.0 | Panel Fixed-Effects |
| matplotlib / seaborn | ≥3.8 / ≥0.13 | Visualisierungen |
| rapidfuzz | ≥3.0 | Fuzzy-Matching (Mapping) |
| openpyxl | ≥3.1 | Excel-Dateien lesen |

Getestet mit **Python 3.12.1**.

---

## Datenzugang

| Quelle | Zugang | Hinweis |
|---|---|---|
| **O\*NET 30.2** | Öffentlich | [onetcenter.org](https://www.onetcenter.org/database.html) → *Complete Database* |
| **ESCO→O\*NET Crosswalk** | Öffentlich | [onetcenter.org/crosswalks](https://www.onetcenter.org/crosswalks.html) |
| **CH_ISCO19.xlsx** | BFS | BFS Strukturerhebung, Einzeljahres-Sheets 2019–2024 | (https://www.bfs.admin.ch/bfs/de/home/statistiken/arbeit-erwerb/erwerbstaetigkeit-arbeitszeit/erwerbsbevoelkerung/auslaendische-arbeitskraefte.assetdetail.36346663.html)

Die O\*NET-Rohdaten sind öffentlich zugänglich und können direkt vom
O\*NET Resource Center des U.S. Department of Labor heruntergeladen
werden. Die BFS-Daten (CH_ISCO19.xlsx) wurden über den
Forschungsdatenzugang des Bundesamts für Statistik bezogen. Eine
Replikation erfordert eine eigene Datenanfrage beim BFS.

Alle verarbeiteten Datensätze (`data/processed/`, `data/output/`) sind
im Repository enthalten, sodass die Analyse ab Notebook 02 ohne erneuten
Rohdaten-Download nachvollzogen werden kann.

---

## Indexformel

$$E_j = \sum_{i=1}^{n} \mu_i \cdot w_{ij} \cdot s_{ij}$$

| Parameter | Beschreibung |
|---|---|
| **μ_i** | LLM-Gewicht für Fähigkeit i (Skala 0.1–0.9), kalibriert an Eloundou et al. (2023) |
| **w_ij** | Min-Max-normalisierter Importance-Wert aus O\*NET |
| **s_ij** | Skill-Overlap-Koeffizient (Pearson-Korrelation, kontinuierlich [0,1]) |
| **E^sub_j** | Substitutionsanteil: Summe Dimensionen mit μ_i > 0.7 |
| **E^aug_j** | Augmentationsanteil: Summe Dimensionen mit 0.3 ≤ μ_i ≤ 0.7 |

---

## Mapping-Verfahren (O\*NET → CH-ISCO-19)

Das dreistufige Mapping verbindet amerikanische O\*NET-SOC-Codes mit
Schweizer CH-ISCO-19-Berufsklassen:

| Stufe | Methode | Ergebnis |
|---|---|---|
| **1** | ESCO-Crosswalk (hierarchisches Matching via ISCO-08 als Brücke) | Direktzuordnung der Mehrheit |
| **2** | Kategorisierung nicht gemappter Codes (A: HG 4–9, korrekt ausgeschlossen; B: manuell zu prüfen) | Kein automatisches Matching |
| **3** | Manuelle Kodierung durch zwei unabhängige Kodierer | 4 Codes, Krippendorff-α > 0.80 |

---

## Reproduzierbarkeit

Alle Zufallsprozesse sind mit `random_state=42` fixiert. Die
Monte-Carlo-Simulation (n=1000 Iterationen) zur Mapping-Konfidenz
verwendet `np.random.seed(42)`.

Erwartete Laufzeiten (Apple M2, 16 GB):

| Notebook | Laufzeit |
|---|---|
| 01 Datenvorbereitung | ~2 min |
| 02 Indexberechnung | ~3 min (inkl. Monte-Carlo) |
| 03 EDA | ~5 min |
| 04 Hypothesen | ~10 min (RF 300 Bäume, 50 Permutations-Iterationen) |
| 05 Validierung | <2 min |

---

## Zitation

```bibtex
@mastersthesis{nojima2026,
  author  = {Nojima, Ayumi},
  title   = {LLM-spezifischer Exposure-Index für den Schweizer Arbeitsmarkt},
  school  = {ZHAW School of Management and Law},
  year    = {2026},
  type    = {Masterarbeit},
  advisor = {Koruna, Stefan}
}
```

---

## Lizenz

Der Code ist unter der MIT-Lizenz veröffentlicht. Die verwendeten
Rohdaten (O\*NET, BFS) unterliegen den jeweiligen Nutzungsbedingungen
der Datenlieferanten.
