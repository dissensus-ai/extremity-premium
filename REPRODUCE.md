# Reproduction guide — The Extremity Premium

Ordered pipeline, run convention, and data provenance for reproducing the
tables and figures in `paper/main.tex`.

## Environment

- Python 3.10–3.13 (`requirements.txt`). Core analysis needs
  `pandas>=2.2, numpy, scipy, statsmodels, matplotlib, seaborn`; the ABM needs
  `mesa==2.1.5`; the (optional) micro-layer needs `torch`/`transformers`.
- `pip install -r requirements.txt`

## Run convention (important)

**Run every analysis script from this `code/` directory**, e.g.
`python analysis/extremity_premium_analysis.py`. Most scripts resolve their
paths relative to `code/` or to their own location; the three that previously
required `code/analysis/` as the working directory
(`weight_robustness_montecarlo.py`, `expanding_window_robustness.py`,
`gmm_weight_estimation.py`) now self-normalise their working directory on import,
so they run from anywhere. All outputs land in `code/results/`.

> Note: `code/analysis/results/` is a legacy output directory from earlier runs
> that used a different working directory. Its unique files have been copied into
> the canonical `code/results/`; new runs write only to `code/results/`.

## Data provenance (no API keys committed)

All inputs are public:
- **Binance BTC/USDT OHLCV** (daily) — spreads via Corwin–Schultz (2012).
- **Crypto Fear & Greed Index** — Alternative.me (a proprietary composite; the
  raw component series are not published — see the paper's limitations).
- **Deribit DVOL** — crypto-native implied volatility (robustness only).
- **ETH/USDT OHLCV**, **Bybit/Binance L2** (spread validation).

The committed analysis inputs are `results/real_spread_data.csv` (740-row main
sample; `cs_spread` valid for 739 days, the uncertainty measure for 715 after a
24-day rolling warm-up) and `results/full_sample_btc_data.csv` (2,896-day
extended sample). `analysis/real_spread_validation.py` rebuilds the former from
the raw OHLCV + F&G series.

## Ordered pipeline

| Step | Script | Produces (paper element) |
|------|--------|--------------------------|
| 1 | `real_spread_validation.py` | `real_spread_data.csv`; empirical spread–uncertainty correlations (Table 1, r=0.24) |
| 2 | `var_diagnostics.py` | ADF/KPSS + Granger causality (`granger_causality.csv`; the primary-sample F=12.79 uses `total_uncertainty`, N≈716, statsmodels df_denom≈706) |
| 3 | `extremity_premium_analysis.py` | regime uncertainty means; pooled extremity premium (Table 6, N=715) |
| 4 | `volatility_matched_regimes.py` | within-volatility-quintile comparison (Table `tab:within_quintile`; Gap in index×100, not bps) |
| 5 | `comprehensive_regression_table.py` | comprehensive controls (regime effects absorbed — the functional-form sensitivity) |
| 6 | `volatility_decomposition.py` | variance/R² decomposition (regime incremental R²=1.3%) — **not** the 81.6/18.4 split |
| 7 | `dvol_regime_validation.py` | DVOL robustness (740-day sample; premium does not replicate under pure implied vol) |
| 8 | `momentum_control.py` | **momentum control** (`momentum_control_results.csv`; effect size robust d≈0.25, significance marginal under momentum+block-permutation) |
| 9 | `weight_sensitivity.py`, `weight_robustness_montecarlo.py`, `gmm_weight_estimation.py` | weight robustness (25 configs; 1000 Dirichlet draws with coefficient distribution; GMM J=75548 rejection + weak identification) |
| 10 | `expanding_window_robustness.py` | look-ahead-bias check (r=0.96) |
| 11 | `full_sample_extension.py` | extended-sample validation + extended within-quintile (Table `tab:extended_sample`, `tab:market_cycles`) |
| 12 | `placebo_tests.py`, `bootstrap_permutation_tests.py` | placebo + block-shuffle permutation inference |
| 13 | `eth_cross_asset_validation.py` | ETH replication (d=0.48) |
| 14 | `calibration.py`, `smm_validation.py` | ABM calibration + SMM (reduced-form model, J=0.83/p=0.36) |
| 15 | `ablation_analysis.py` | ABM δ-ablation |
| 16 | `run_analysis.py` / `generate_paper_figures.py` | figures |

Reviewer-response analyses added this round: `momentum_control.py` (momentum
confound + MC coefficient distribution); findings in
`results/momentum_control_FINDING.md`.

## Figure 5 note (uncertainty decomposition)

The 81.6% / 18.4% aleatoric/epistemic split in Figure 5 is a **hardcoded literal**
in `generate_paper_figures.py` (`sizes = [81.6, 18.4]`). It matches the paper's
decomposition **table** (aleatoric index mean 0.227 / total 0.278 = 81.6%;
epistemic 0.051 / 0.278 = 18.4%), which comes from the heuristic-weighted
`signals/uncertainty_decomposer.py`, **not** from the raw proxy-column means
(`aleatoric_proxy`≈0.206, `epistemic_proxy`≈0.282 — unnormalised, these do not
order the components the same way) and **not** from `volatility_decomposition.py`
(which reports the R²/variance decomposition). The paper flags the 81.6/18.4
split as conditional on the heuristic weights and not load-bearing. For a fully
reproducible figure, source the split from the decomposer output rather than the
hardcoded literal.

## Known external dependency

`signals/asri_adapter.py` references an external ASRI project path and is not on
the paper's reproduction path; the committed results do not depend on it.
