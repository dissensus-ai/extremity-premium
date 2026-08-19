"""
ETH Alt-Asset Robustness Row: Trace and Replacement (EXT-2 / reviewer3 C-26)

The paper's measurement-robustness table (Table tab:robustness_measurement)
carried the row:

    Alt Asset & CS (ETH) & Parkinson Vol & +0.032 & <0.001

That coefficient matches NO committed script or output. This script documents
why, and produces a correct, fully traceable replacement from the committed
main-sample ETH artifact (results/eth_spread_data.csv, 739 days,
2024-01-01 to 2026-01-08), offline (no API fetch).

Findings it encodes:
1. The committed cs_spread column in eth_spread_data.csv is degenerate
   (~98% exact zeros): it was built with a single-day beta term, under which
   the Corwin-Schultz alpha is almost always negative and gets clipped to
   zero. "CS (ETH)" was therefore never a usable regressor in the committed
   main-sample ETH data. (The estimator in eth_cross_asset_validation.py is
   now fixed to the canonical 2-day beta; this script recomputes the
   corrected spread from the committed OHLC columns.)
2. The committed results/eth_extremity_premium_volatility.csv (the Figure 6
   ETH panel) is the regression Parkinson_vol ~ regime dummies with NO
   volatility control (OLS, HC3): extreme_greed +0.00715 (p=0.0014),
   extreme_fear +0.01153 (p=0.0004). This script reproduces it exactly.
3. No specification on the committed ETH data yields +0.032 with p<0.001.

Replacement candidates written to results/eth_t14_replacement.csv, all
"extreme regime vs neutral, controlling for volatility" per the table
caption:
  - spec eth_parkinson_ctrl_realized: DV = ETH Parkinson vol, control =
    5-day realized vol (the main-sample-consistent alt-asset row).
  - spec eth_cs_canonical_ctrl_parkinson: DV = corrected 2-day-beta CS
    spread, control = Parkinson vol (what the original row claimed to be).
  - spec eth_parkinson_uncontrolled: the committed Figure 6 numbers, kept
    for traceability (NOT volatility-controlled; does not fit the caption).

Author: Murad Farzulla
Date: August 2026
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

REGIMES = ['extreme_greed', 'extreme_fear', 'fear', 'greed']


def load_committed_eth():
    """Load the committed main-sample ETH artifact."""
    df = pd.read_csv('results/eth_spread_data.csv', parse_dates=['date'])
    print(f"Committed ETH data: {len(df)} rows, "
          f"{df['date'].min().date()} to {df['date'].max().date()}")

    zero_frac = (df['cs_spread'] == 0).mean()
    print(f"Committed cs_spread column: {zero_frac:.1%} exact zeros "
          f"(single-day-beta degeneracy)")
    return df


def recompute_canonical_cs(df):
    """
    Recompute the Corwin-Schultz spread with the canonical 2-day beta
    (matches full_sample_extension.compute_corwin_schultz_spread, kept in
    fractional units rather than bps).
    """
    df = df.copy()
    log_hl_sq = np.log(df['high'] / df['low']) ** 2
    beta = log_hl_sq.rolling(2).sum()
    gamma = np.log(df['high'].rolling(2).max() /
                   df['low'].rolling(2).min()) ** 2

    denom = 3 - 2 * np.sqrt(2)
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / denom - np.sqrt(gamma / denom)
    alpha = alpha.clip(lower=0)

    df['cs_spread_canonical'] = (2 * (np.exp(alpha) - 1) /
                                 (1 + np.exp(alpha))).clip(lower=0)
    return df


def regime_regression(df, dv, control, spec_id):
    """
    OLS of dv on regime dummies (neutral reference) with optional volatility
    control, HC3 standard errors — the same shape as the BTC baseline row
    (uncertainty ~ volatility + regime dummies).
    """
    cols = [dv, 'regime'] + ([control] if control else [])
    d = df.dropna(subset=cols).copy()

    X = pd.DataFrame(index=d.index)
    if control:
        X[control] = d[control]
    for reg in REGIMES:
        X[f'is_{reg}'] = (d['regime'] == reg).astype(float)

    model = sm.OLS(d[dv], sm.add_constant(X)).fit(cov_type='HC3')

    print(f"\n[{spec_id}] DV={dv}, control={control or 'NONE'}, "
          f"n={int(model.nobs)}, R²={model.rsquared:.4f}")

    rows = []
    for reg in REGIMES:
        coef = model.params[f'is_{reg}']
        pval = model.pvalues[f'is_{reg}']
        sig = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
        print(f"  {reg:15s}: {coef:+.5f} (p={pval:.4f}) {sig}")
        rows.append({
            'spec': spec_id,
            'dv': dv,
            'control': control or 'none',
            'estimator': 'OLS_HC3',
            'n': int(model.nobs),
            'regime': reg,
            'coefficient': coef,
            'p_value': pval,
        })
    return rows


def main():
    print("=" * 70)
    print("ETH ALT-ASSET ROW: TRACE + REPLACEMENT (offline, committed data)")
    print("=" * 70)

    df = load_committed_eth()
    df = recompute_canonical_cs(df)

    all_rows = []

    # 1. Main-sample-consistent, volatility-controlled alt-asset spec
    all_rows += regime_regression(df, 'parkinson_vol', 'realized_vol',
                                  'eth_parkinson_ctrl_realized')

    # 2. What the retracted row claimed to be: ETH CS spread (corrected
    #    estimator), volatility-controlled
    all_rows += regime_regression(df, 'cs_spread_canonical', 'parkinson_vol',
                                  'eth_cs_canonical_ctrl_parkinson')

    # 3. The committed Figure 6 spec (reproduces
    #    eth_extremity_premium_volatility.csv; NOT volatility-controlled)
    all_rows += regime_regression(df, 'parkinson_vol', None,
                                  'eth_parkinson_uncontrolled')

    results = pd.DataFrame(all_rows)
    results.to_csv('results/eth_t14_replacement.csv', index=False)
    print("\nSaved: results/eth_t14_replacement.csv")

    # Verdict on the retracted number
    near = results[(results['coefficient'] - 0.032).abs() < 0.003]
    strong = near[near['p_value'] < 0.001]
    print("\n" + "=" * 70)
    if len(strong) == 0:
        print("VERDICT: no committed-data specification yields +0.032 with "
              "p<0.001.")
        print("The 'Alt Asset / CS (ETH) / +0.032 / <0.001' row is "
              "untraceable and must be replaced or deleted.")
    else:
        print("Specifications matching +0.032, p<0.001:")
        print(strong.to_string(index=False))

    return results


if __name__ == '__main__':
    results = main()
