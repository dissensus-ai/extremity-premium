# The Extremity Premium — analysis code

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.17989810-blue.svg)](https://doi.org/10.5281/zenodo.17989810)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Status](https://img.shields.io/badge/Status-Under_Review-yellow.svg)](https://doi.org/10.5281/zenodo.17989810)
**Working Paper DAI-2510** | [Dissensus AI](https://dissensus.ai)

Code and data-analysis pipeline for:

**The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets**
Preprint: arXiv:2602.07018 · Status: under review at *Computational Economics*.

The paper documents an "extremity premium" — extreme Fear & Greed sentiment
regimes exhibit higher spread-setting uncertainty than neutral periods, beyond
what realized volatility predicts — and stress-tests it against volatility,
momentum, functional-form, and multiple-testing controls. An agent-based model
is included as an *illustrative* device only; because its spread–uncertainty link
is coded rather than emergent it does no inferential work, and the paper's
inferential weight rests entirely on the empirical analysis.

## Reproduction

See **[REPRODUCE.md](REPRODUCE.md)** for the ordered pipeline (script → paper
table/figure), the run convention, and data provenance. In short: install
`requirements.txt` (Python 3.10–3.13; **not** 3.14 — it segfaults pandas 2.3.1),
and run the analysis scripts from this `code/` directory.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # pandas, numpy, scipy, statsmodels, arch, mesa, matplotlib, seaborn
python analysis/real_spread_validation.py   # builds results/real_spread_data.csv
python analysis/extremity_premium_analysis.py
# ... see REPRODUCE.md for the full ordered list
```

## What the pipeline actually does

1. **Spread estimation** — daily Corwin–Schultz spreads from Binance BTC/USDT
   OHLCV (Abdi–Ranaldo and LOB validation as robustness).
2. **Uncertainty construction** — a heuristic aleatoric/epistemic decomposition
   over market observables (`signals/`); the epistemic proxy is cross-exchange
   dispersion, not Bayesian model uncertainty.
3. **Regime / extremity-premium tests** — extreme vs neutral sentiment regimes,
   volatility-quintile stratification, momentum control, extended-sample
   validation, placebo and permutation inference, ETH cross-asset replication
   (`analysis/`).
4. **Agent-based model** — a Mesa ABM (`simulation/`, `agents/`) used for a
   consistency check and an SMM moment-matching validation on a reduced-form
   chartist–fundamentalist model (not the full agent specification).

## Data provenance (public; no API keys committed)

- **Binance** BTC/USDT and ETH/USDT daily OHLCV (spreads, returns, volatility).
- **Alternative.me** Crypto Fear & Greed Index (sentiment regimes) — a
  proprietary composite; raw component series are not published (see the paper's
  limitations). Note: sentiment is the F&G index, **not** Reddit/social text.
- **Deribit DVOL** implied-volatility index (robustness).
- **Bybit / Binance** L2 order-book snapshots (spread validation).

The large raw trees (`data/lob/`, `data/data2/`, `data/binance/`, ~16 GB) are
gitignored; the committed analysis inputs live in `results/`
(`real_spread_data.csv`, `full_sample_btc_data.csv`).

## Repository layout

```
code/
├── analysis/        # the paper's analysis scripts (spreads, extremity premium, robustness, SMM)
├── signals/         # uncertainty decomposer
├── simulation/      # Mesa market environment, order book, matching engine (ABM)
├── agents/          # market maker / informed / noise trader agents
├── data_ingestion/  # OHLCV / F&G / DVOL fetchers
├── config/          # configuration
├── results/         # committed analysis inputs + outputs
├── tests/           # unit / validation tests
└── REPRODUCE.md     # ordered reproduction pipeline
```

(`feature_engineering/` and `monitoring/` contain scaffolding from an earlier
real-time design that the paper's offline daily-frequency pipeline does not use.)

## Citation

```bibtex
@article{farzulla_extremity_premium,
  title  = {The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets},
  author = {Farzulla, Murad},
  year   = {2026},
  note   = {Preprint arXiv:2602.07018; under review, Computational Economics}}
```

## Authors

- **Murad Farzulla** -- [Dissensus AI](https://dissensus.ai) & King's College London
  - ORCID: [0009-0002-7164-8704](https://orcid.org/0009-0002-7164-8704)
  - Email: murad@dissensus.ai

## License

Paper content: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). Code: MIT --- see `LICENSE`.