# 05_statistical_analysis.R
# ─────────────────────────────────────────────────────────────────────────────
# Statistical analysis of the LLM-specific occupational exposure index for
# Switzerland.
#
# Topics covered:
#   1. Descriptive statistics of the exposure index
#   2. Distribution plots (histogram, density, box-plots by occupation group)
#   3. Correlation with employment share and wage proxies (if available)
#   4. Regression: exposure ~ occupation characteristics
#   5. Export summary tables to data/output/
# ─────────────────────────────────────────────────────────────────────────────

library(tidyverse)
library(arrow)          # read parquet files
library(ggplot2)
library(scales)
library(broom)

# ── Paths ────────────────────────────────────────────────────────────────────
output_dir  <- file.path("data", "output")
figures_dir <- file.path(output_dir, "figures")
dir.create(figures_dir, showWarnings = FALSE, recursive = TRUE)

# ── 1. Load data ──────────────────────────────────────────────────────────────
cat("Loading exposure index …\n")
exposure <- read_parquet(file.path(output_dir, "exposure_index.parquet"))
cat(sprintf("  Rows: %d | Columns: %s\n", nrow(exposure), paste(names(exposure), collapse = ", ")))

# ── 2. Descriptive statistics ────────────────────────────────────────────────
cat("\nDescriptive statistics (exposure_index):\n")
print(summary(exposure$exposure_index))

desc_stats <- exposure %>%
  summarise(
    n        = n(),
    mean     = mean(exposure_index, na.rm = TRUE),
    median   = median(exposure_index, na.rm = TRUE),
    sd       = sd(exposure_index, na.rm = TRUE),
    min      = min(exposure_index, na.rm = TRUE),
    max      = max(exposure_index, na.rm = TRUE),
    p25      = quantile(exposure_index, 0.25, na.rm = TRUE),
    p75      = quantile(exposure_index, 0.75, na.rm = TRUE)
  )
write_csv(desc_stats, file.path(output_dir, "descriptive_stats.csv"))
cat("  Saved → data/output/descriptive_stats.csv\n")

# ── 3. Distribution plot ──────────────────────────────────────────────────────
p_hist <- ggplot(exposure, aes(x = exposure_index)) +
  geom_histogram(binwidth = 0.05, fill = "#2166ac", colour = "white", alpha = 0.85) +
  geom_density(aes(y = after_stat(count) * 0.05), colour = "#d6604d", linewidth = 0.8) +
  labs(
    title    = "Distribution of LLM Exposure Index – Swiss Occupations",
    subtitle = "O*NET-based index mapped to CH-ISCO-19",
    x        = "Exposure Index (0 = low, 1 = high)",
    y        = "Number of Occupations"
  ) +
  theme_minimal(base_size = 13)

ggsave(file.path(figures_dir, "exposure_distribution.png"), p_hist,
       width = 8, height = 5, dpi = 150)
cat("  Saved → data/output/figures/exposure_distribution.png\n")

# ── 4. Major-group box-plot (ISCO 1-digit) ────────────────────────────────────
exposure <- exposure %>%
  mutate(isco1 = substr(as.character(isco4), 1, 1))

p_box <- ggplot(exposure, aes(x = isco1, y = exposure_index, fill = isco1)) +
  geom_boxplot(outlier.size = 1, alpha = 0.8) +
  scale_fill_brewer(palette = "Set3", guide = "none") +
  labs(
    title = "Exposure Index by ISCO-08 Major Group",
    x     = "ISCO Major Group (1-digit)",
    y     = "Exposure Index"
  ) +
  theme_minimal(base_size = 13)

ggsave(file.path(figures_dir, "exposure_by_isco_major_group.png"), p_box,
       width = 8, height = 5, dpi = 150)
cat("  Saved → data/output/figures/exposure_by_isco_major_group.png\n")

# ── 5. Employment-weighted exposure (if weight column present) ────────────────
if ("employment_weight" %in% names(exposure)) {
  cat("\nComputing employment-weighted mean exposure …\n")
  weighted_mean <- weighted.mean(
    exposure$exposure_index,
    w = replace_na(exposure$employment_weight, 0),
    na.rm = TRUE
  )
  cat(sprintf("  Employment-weighted mean exposure: %.4f\n", weighted_mean))
  write_csv(
    tibble(weighted_mean_exposure = weighted_mean),
    file.path(output_dir, "weighted_mean_exposure.csv")
  )
}

# ── 6. OLS regression: exposure ~ ISCO major group ────────────────────────────
cat("\nRunning OLS regression …\n")
model <- lm(exposure_index ~ factor(isco1), data = exposure)
tidy_model <- tidy(model)
print(tidy_model)
write_csv(tidy_model, file.path(output_dir, "regression_results.csv"))
cat("  Saved → data/output/regression_results.csv\n")

cat("\nAll done.\n")
