#!/usr/bin/env python3
"""
RECONCILIATION (Jun 2026, deep-review fix): run BOTH extended within-quintile
pipelines on the SAME committed data file and emit the full
(gap, Cohen's d, p, Holm-p) vector from each, with neutral/extreme/qcut
definitions made explicit. Read-only on data; writes nothing except stdout.

Pipeline A = full_sample_extension.py:within_quintile_analysis
    qcut on realized_vol; neutral = regime=='neutral'; extreme = is_extreme

Pipeline B = flexible_volatility_controls.py within-quintile block
    qcut on parkinson_vol (rv); neutral = is_extreme==0 & 46<=fg<=55 ; extreme = is_extreme==1
    (this script ADDS the per-quintile Cohen's d the original B never computed)
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
DATA_FILE = os.path.join(RESULTS_DIR, 'full_sample_btc_data.csv')


def cohens_d(a, b):
    pooled = np.sqrt((a.var() + b.var()) / 2)
    return (a.mean() - b.mean()) / pooled if pooled > 0 else 0.0


def pipeline_A(df):
    """full_sample_extension.py logic, qcut realized_vol, regime=='neutral'."""
    df = df.copy()
    df = df.dropna(subset=['cs_spread', 'parkinson_vol', 'realized_vol', 'regime'])
    df['vol_quintile'] = pd.qcut(df['realized_vol'], 5, labels=[1, 2, 3, 4, 5])
    rows = []
    for q in [1, 2, 3, 4, 5]:
        qd = df[df['vol_quintile'] == q]
        ext = qd[qd['is_extreme']]['cs_spread']
        neu = qd[qd['regime'] == 'neutral']['cs_spread']
        if len(ext) < 5 or len(neu) < 5:
            continue
        t, p = ttest_ind(ext, neu, equal_var=False)
        rows.append(dict(quintile=q, n_ext=len(ext), n_neu=len(neu),
                         gap=ext.mean() - neu.mean(), t=t, p=p, d=cohens_d(ext, neu)))
    out = pd.DataFrame(rows)
    _, padj, _, _ = multipletests(out['p'], method='holm')
    out['p_holm'] = padj
    return out


def pipeline_B(df):
    """flexible_volatility_controls.py logic, qcut parkinson_vol, fg-band neutral."""
    df = df.copy()
    df = df.dropna(subset=['cs_spread', 'fear_greed_value', 'parkinson_vol'])
    df['rv'] = df['parkinson_vol']
    df['is_extreme'] = ((df['fear_greed_value'] <= 25) | (df['fear_greed_value'] > 75)).astype(int)
    df = df[df['cs_spread'] > 0].copy()
    df['vol_quintile'] = pd.qcut(df['rv'], 5, labels=False, duplicates='drop')
    rows = []
    for q in range(5):
        qd = df[df['vol_quintile'] == q]
        ext = qd[qd['is_extreme'] == 1]['cs_spread']
        neu = qd[(qd['is_extreme'] == 0) &
                 (qd['fear_greed_value'] >= 46) &
                 (qd['fear_greed_value'] <= 55)]['cs_spread']
        if len(ext) > 5 and len(neu) > 5:
            t, p = ttest_ind(ext, neu, equal_var=False)
            rows.append(dict(quintile=q + 1, n_ext=len(ext), n_neu=len(neu),
                             gap=ext.mean() - neu.mean(), t=t, p=p, d=cohens_d(ext, neu)))
    out = pd.DataFrame(rows)
    _, padj, _, _ = multipletests(out['p'], method='holm')
    out['p_holm'] = padj
    return out


def pooled_demeaned(df):
    """Pipeline B's pooled volatility-demeaned test (the published d=0.21 / p=0.0008)."""
    df = df.copy()
    df = df.dropna(subset=['cs_spread', 'fear_greed_value', 'parkinson_vol'])
    df['rv'] = df['parkinson_vol']
    df['is_extreme'] = ((df['fear_greed_value'] <= 25) | (df['fear_greed_value'] > 75)).astype(int)
    df = df[df['cs_spread'] > 0].copy()
    df['vol_quintile'] = pd.qcut(df['rv'], 5, labels=False, duplicates='drop')
    df['resid'] = df.groupby('vol_quintile')['cs_spread'].transform(lambda x: x - x.mean())
    ext = df[df['is_extreme'] == 1]['resid']
    neu = df[(df['is_extreme'] == 0) & (df['fear_greed_value'] >= 46) &
             (df['fear_greed_value'] <= 55)]['resid']
    t, p = stats.ttest_ind(ext, neu, equal_var=False)
    return dict(gap=ext.mean() - neu.mean(), t=t, p=p, d=cohens_d(ext, neu),
                n_ext=len(ext), n_neu=len(neu))


def fmt(out):
    lines = []
    for _, r in out.iterrows():
        lines.append(f"  Q{int(r.quintile)}: gap={r.gap:7.2f}bps  d={r.d:.3f}  "
                     f"t={r.t:5.2f}  p={r.p:.4f}  p_holm={r.p_holm:.4f}  "
                     f"(n_ext={int(r.n_ext)}, n_neu={int(r.n_neu)})")
    return "\n".join(lines)


if __name__ == '__main__':
    df = pd.read_csv(DATA_FILE, parse_dates=['date'])
    print(f"Loaded {len(df)} rows from {DATA_FILE}")
    print(f"date range {df.date.min().date()} .. {df.date.max().date()}\n")

    A = pipeline_A(df)
    print("=== PIPELINE A  (full_sample_extension.py: qcut realized_vol; neutral=regime=='neutral') ===")
    print(fmt(A))
    print(f"  median d = {A.d.median():.3f} ; n-weighted mean d = "
          f"{np.average(A.d, weights=(A.n_ext + A.n_neu)):.3f}")
    print(f"  d-vector = [{', '.join(f'{x:.3f}' for x in A.d)}]")
    print(f"  any Holm-sig: {(A.p_holm < 0.05).sum()}/{len(A)}\n")

    B = pipeline_B(df)
    print("=== PIPELINE B  (flexible_volatility_controls.py: qcut parkinson_vol; neutral=fg 46-55) ===")
    print(fmt(B))
    print(f"  median d = {B.d.median():.3f} ; n-weighted mean d = "
          f"{np.average(B.d, weights=(B.n_ext + B.n_neu)):.3f}")
    print(f"  d-vector = [{', '.join(f'{x:.3f}' for x in B.d)}]")
    print(f"  any Holm-sig: {(B.p_holm < 0.05).sum()}/{len(B)}\n")

    pd_res = pooled_demeaned(df)
    print("=== POOLED volatility-demeaned (published d=0.21 / t=3.36 / p=0.0008) ===")
    print(f"  gap={pd_res['gap']:.4f}  t={pd_res['t']:.3f}  p={pd_res['p']:.6f}  "
          f"d={pd_res['d']:.3f}  (n_ext={pd_res['n_ext']}, n_neu={pd_res['n_neu']})")
