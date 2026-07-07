# FINDING: momentum control + MC-weight coefficient distribution

## Momentum control (reviewer: momentum confounding)

The Fear & Greed Index is 25% market-momentum, and extreme greed coincides with
high trailing momentum, so the extremity premium could be a momentum artefact.
Test: does the premium (extreme vs neutral uncertainty) survive a trailing
20-day momentum control alongside the volatility control the paper already
applies? Extended sample, N=1,342 (888 extreme, 454 neutral).
Script: `analysis/momentum_control.py` → `results/momentum_control_results.csv`.

| spec | Cohen's d | Welch p | block-perm p |
|------|-----------|---------|--------------|
| raw extreme-vs-neutral | +0.954 | 5e-77 | 0.0002 |
| resid: vol + vol² | +0.320 | 7e-11 | 0.032 |
| **resid: vol+vol²+mom+mom²** | **+0.254** | 1.8e-7 | **0.100** |
| resid: +log_volume | +0.255 | 1.6e-7 | 0.090 |
| **demean within vol-quintile × mom-tercile** | **+0.272** | 2.6e-9 | **0.083** |

**Honest reading:** the premium's **effect size is robust** to momentum
(d≈0.25–0.27, close to the volatility-only d≈0.32 and the paper's headline
vol-controlled d=0.21), and it remains significant under the iid Welch test
(p<10⁻⁶). But under a serial-dependence-respecting moving-block permutation,
adding the momentum control roughly triples the p-value and pushes it from
significant (vol-only p≈0.03) to **marginal (p≈0.08–0.10)**. Momentum therefore
accounts for **part but not all** of the premium. This directly answers the
referee and reinforces the point-5 fragility: the effect is directionally robust
but its significance is sensitive to controls once serial dependence is respected.

(NB: the moving-block permutation here is more conservative than the paper's
headline block-shuffle p<10⁻⁴; report the momentum result primarily via the
effect size + iid p, with the block permutation as the serial-dependence caveat.)

## Monte-Carlo weight coefficient distribution (reviewer: show coefficients, not just ranking, survive random weights)

From `mc_weight_robustness_results.csv` (1,000 Dirichlet(1,1,1,1) draws) — the
extreme-minus-neutral **gaps** themselves, not just their sign:

| coefficient | median | IQR | min | % > 0 |
|-------------|--------|-----|-----|-------|
| greed gap | +0.257 | [0.247, 0.264] | +0.203 | 100% |
| fear gap | +0.111 | [0.101, 0.114] | +0.090 | 100% |

The gaps are tightly distributed and strictly positive across every draw (min
greed gap 0.203, min fear gap 0.090, both well above zero) — so the coefficient
magnitudes, not merely the binary ranking, are weight-invariant.
