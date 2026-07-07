# Statistical Consistency Audit Report

**Paper:** Sentiment-Microstructure ABM
**File:** `/arxiv-submission/main.tex`
**Audit Date:** 2026-01-29
**Auditor:** Janus (Claude Opus 4.5)

---

## Executive Summary

The paper contains **NO TRUE INCONSISTENCIES**. The apparent contradictions flagged by the reviewer arise from **legitimate different-sample statistics** that are properly contextualized in the paper. However, clarity improvements are recommended to prevent reviewer confusion.

---

## Detailed Findings

### 1. F-Statistic Discrepancy: F=12.79 vs F=211

**VERDICT: NOT AN INCONSISTENCY - Different Samples**

| Location | F-value | Sample | Context |
|----------|---------|--------|---------|
| Line 133 (Abstract) | F = 12.79 | Main (739 days) | 3-lag Granger, Unc → Spreads |
| Line 896 (Results) | F = 12.79 | Main (739 days) | 3-lag Granger, explicit |
| Line 900 (Results) | F = 0.82 | Main (739 days) | 3-lag Granger, reverse direction |
| Line 917-921 (Table) | F = 31.28 to 7.07 | Main (739 days) | Full lag structure (1-5 lags) |
| Line 1327 (Extended) | F = 211.30 | Extended (2,896 days) | 1-lag Granger |
| Line 1752 (Summary) | F = 12.79 | Main (739 days) | Summary of main findings |
| Line 1770 (Conclusion) | F = 211 | Extended (2,896 days) | Extended sample conclusion |

**Explanation:** The paper explicitly presents two samples:
- **Main sample:** 739 days (Jan 2024 - Jan 2026)
- **Extended sample:** 2,896 days (Feb 2018 - Jan 2026)

The F=211 appears ONLY in the extended sample section (Table 10, line 1327) and the conclusion's extended sample summary (line 1770). The paper correctly states "Granger causality is 16x stronger with the larger sample (F = 211 vs. 31)" at line 1367.

**Recommendation:** In the Conclusion (line 1770), add "(extended sample)" after F=211 for clarity:
> "Granger causality: Uncertainty predicts spreads (F = 211, p < 0.0001, extended sample), not vice versa"

---

### 2. Sample Size Discrepancy: N=739 vs N=2,896 vs N=715 vs N=1,961

**VERDICT: NOT AN INCONSISTENCY - Multiple Legitimate Samples**

| N | Context | Lines |
|---|---------|-------|
| 739 | Main sample (full calendar days) | 100, 439, 451, 508, 514, 534, 541, 553, 767, 771, 799, 846, 1025, 1190, 1194, 1216, 1312, 1315, 1378, 1491, 1538, 1607 |
| 715 | Complete cases after dropping 24 obs with missing lags | 451, 599, 660, 1112, 1171 |
| 732/728 | Granger test df (varies by lag specification) | 896, 897, 900 |
| 740 | DVOL matched sample (slightly larger due to data alignment) | 1378 |
| 2,896 | Extended sample (Feb 2018 - Jan 2026) | 1299, 1307, 1312, 1315, 1767 |
| 1,961 | Extended sample days with positive CS spread estimates | 712, 716 |
| 345 | 2022 bear market out-of-sample | 1226 |
| 719 | 2024 bull market comparison sample | 1226 |

**Explanation:** The paper uses different sample sizes for different analyses:
1. **739 days:** Full calendar sample
2. **715 days:** After dropping 24 observations with missing lagged variables (stated at line 451)
3. **2,896 days:** Extended historical sample for robustness
4. **1,961 days:** Extended sample subset with positive spread estimates (kitchen-sink regression)

All sample sizes are explicitly documented with context. Line 451 clearly states:
> "For robustness analyses requiring lagged variables (Granger causality, regime transitions), we use N = 715 complete cases after dropping 24 observations with missing lags at series boundaries."

**Recommendation:** No changes needed - already well documented.

---

### 3. Spread Estimators: Abdi-Ranaldo Coverage

**VERDICT: PARTIAL ISSUE - Mentioned but not fully detailed**

The paper mentions multiple spread estimators but coverage varies:

| Estimator | Lines | Coverage Level |
|-----------|-------|----------------|
| Corwin-Schultz (CS) | 139, 453, 457-465, 473, 508, 514, etc. | **Primary** - fully detailed with formula |
| Roll | 467-473, 1686 | **Secondary** - formula provided, limitations discussed |
| Abdi-Ranaldo (AR) | 139, 981-1020 | **Robustness** - correlation reported, coefficient in table |

**Abdi-Ranaldo Details Found:**
- Line 139: Mentioned as providing "consistent uncertainty correlations"
- Lines 981-1020: Full robustness section with:
  - Formula reference (citet{abdi2017simple})
  - Correlation: r = 0.368 (vs CS r = 0.235)
  - Extremity premium coefficient: +0.048 (p = 0.003) in Table 6
  - Interpretation: "The higher AR correlation suggests this estimator may be more sensitive to information asymmetry effects"

**Recommendation:** The paper DOES detail Abdi-Ranaldo (Section 5.2.3, lines 981-1020). If reviewer missed this, consider adding a forward reference in the abstract/intro that points to Section 5.2.3.

---

## All F-Statistics in Paper

| Line | F-value | Context |
|------|---------|---------|
| 133 | F = 12.79 | Granger Unc→Spread, 3-lag, main sample |
| 133 | F = 0.82 | Granger Spread→Unc, 3-lag, main sample |
| 896 | F = 12.79 | Granger 3-lag explicit |
| 897 | F = 7.07 | Granger 5-lag |
| 900 | F = 0.82 | Reverse direction |
| 917 | F = 31.28 | Lag 1 |
| 918 | F = 17.31 | Lag 2 |
| 919 | F = 12.79 | Lag 3 |
| 920 | F = 9.13 | Lag 4 |
| 921 | F = 7.07 | Lag 5 |
| 934 | F = 4.14 | IV first-stage (weak instruments) |
| 1275 | F = 10.1 | Joint regime significance |
| 1275 | F = 11.0 | Heteroscedasticity test |
| 1327 | F = 211.30 | Extended sample Granger |
| 1709 | F = 10.1 | Variance decomposition |
| 1752 | F = 12.79 | Summary (main sample) |
| 1770 | F = 211 | Conclusion (extended sample) |

---

## All Sample Sizes Mentioned

| N | Description | Lines |
|---|-------------|-------|
| 739 | Main sample days | Multiple |
| 715 | Complete cases (lagged analysis) | 451, 599, 660, 1112, 1171 |
| 732 | Granger df (3-lag) | 896, 900 |
| 728 | Granger df (5-lag) | 897 |
| 710 | Regression df | 1275 |
| 713 | T-test df | 1162, 1163, 1180-1183 |
| 740 | DVOL matched | 1378 |
| 2,896 | Extended sample | 1299, 1307, 1315, 1767 |
| 1,961 | Extended + positive spreads | 712 |
| 888 | Extended extreme regimes | 1317 |
| 457 | Extended neutral regimes | 1318 |
| 170 | Main extreme regimes | 1317 |
| 116 | Main neutral regimes | 1318, 1031, 1033, 1194, 1207 |
| 345 | 2022 bear market | 1226 |
| 719 | 2024 bull comparison | 1226 |
| 366 | Training set (2024) | 829 |
| 373 | Test set (2025-26) | 829 |
| 311 | Bullish regime days | 1031 |
| 140 | Bearish regime days | 1032 |
| 90 | Bybit LOB days | 1044 |
| 61 | Binance effective spread days | 1044, 1058 |
| 89 | LOB-uncertainty validation | 1061-1063 |
| 33 | Binance LOB-CS comparison | 1069 |
| 18 | Rolling windows | 1025 |

---

## All Correlation Coefficients

| r | Variables | Sample | Lines |
|---|-----------|--------|-------|
| 0.24 | CS Spread vs Total Uncertainty | Main (739) | 514, 529, 534, 541, 1150 |
| 0.235 | CS Spread vs Uncertainty | Main | 993 |
| 0.368 | AR Spread vs Uncertainty | Main | 994 |
| 0.64 | ABM Spread vs Uncertainty | Simulated | 557, 567, 1472 |
| 0.043 | Residual correlation | Volatility-purged | 1158 |
| 0.04 | Same | Rounded | 1707 |
| 0.21 | Spread-Unc in Bullish regime | n=311 | 1031 |
| 0.28 | Spread-Unc in Bearish regime | n=140 | 1032 |
| 0.31 | Spread-Unc in Neutral regime | n=116 | 1033 |
| 0.23 | Mean rolling correlation | 90-day windows | 1025 |
| 0.11 | LOB spread vs volatility | LOB sample | 1077 |
| 0.19 | LOB spread vs aleatoric | LOB sample | 1077 |
| 0.96 | Full-sample vs expanding-window uncertainty | Main | 1287 |
| 0.085 | Direction vs spreads | Main | 1746 |

---

## R-squared Values

| R^2 | Model | Lines |
|-----|-------|-------|
| 0.055 | CS Spread ~ Uncertainty (bivariate) | 541 |
| 0.77 | With volatility control | 611 |
| 0.755 | Model 1: Volatility only | 642, 695, 1270 |
| 0.768 | Model 2: Volatility + Regimes | 642, 695, 1271 |
| 0.772 | Model 3 | 695 |
| 0.763 | Model 5 | 695 |
| 0.048 | Model 1 (extended, no vol) | 746 |
| 0.217 | Model 2 (extended) | 746 |
| 0.275 | Model 3 (extended) | 746 |
| 0.298 | Model 4 (extended) | 746 |
| 0.314 | Model 5 (extended) | 746 |
| 0.76 | DVOL volatility explanatory power | 1384 |
| 0.870 | 2024 bull market model | 1240 |
| 0.840 | 2022 bear market model | 1240 |
| 0.198 | Regimes alone | 2150 |

**Incremental R^2:**
| Delta R^2 | Context | Lines |
|-----------|---------|-------|
| +0.013 | Regimes after volatility | 643, 696, 1272, 1277, 1709 |
| +0.003 | Epistemic decomposition | 131, 1636, 1748 |
| +0.004 | Model 3 increment | 696 |

---

## Potential Reviewer Confusion Points

### 1. Granger F-statistic at Lag 1 vs Lag 3
The abstract reports F=12.79 (lag 3) but the extended sample table uses lag 1 (F=211 vs F=31.28). This is consistent but could confuse readers comparing across sections.

**Suggestion:** Add a note that main sample results use 3-lag specification per BIC, while extended sample comparison uses 1-lag for comparability.

### 2. "N=715" Appears Without Context in Some Figures
Lines 599 and 660 reference N=715 in figure captions. While the main text explains this (line 451), figure captions could benefit from a brief note.

**Suggestion:** Add "(complete cases after lag exclusion)" to figure captions using N=715.

### 3. Multiple Spread Estimators with Different Correlations
CS gives r=0.235, AR gives r=0.368. This is discussed but could be misread as inconsistency.

**Existing clarity:** Line 995-996 explains "The higher AR correlation suggests this estimator may be more sensitive to information asymmetry effects"

---

## Conclusion

The paper maintains internal statistical consistency. All apparent discrepancies are:
1. **Different samples** (main vs extended)
2. **Different lag specifications** (properly documented)
3. **Different subsets** (complete cases, positive spreads, etc.)

**Minor clarity improvements recommended:**
1. Add "(extended sample)" qualifier after F=211 in conclusion
2. Consider forward-referencing AR robustness section in intro
3. Add brief "(complete cases)" notes to figure captions using N=715

No substantive corrections required.

---

## Appendix: Line-by-Line Reference

All statistics extracted from the paper manuscript (`paper/main.tex` in the parent paper directory; the canonical source is `extremity-abm/paper/main.tex`).

Audit methodology: Grep search for F-statistics, sample sizes, spread estimators, correlations, R-squared values, and p-values with manual contextual verification.
