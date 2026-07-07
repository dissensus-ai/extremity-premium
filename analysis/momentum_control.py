"""
Momentum control for the extremity premium (reviewer point: momentum confounding).
====================================================================================

The Fear & Greed Index is 25% market-momentum; extreme greed tends to coincide
with high trailing momentum, so the extremity premium could be a momentum
artefact. We test whether the premium (extreme vs neutral uncertainty) survives
controlling for trailing momentum, ALONGSIDE the volatility control the paper
already applies.

Trailing momentum = sum of the previous 20 daily log returns (strictly lagged,
no look-ahead). Run on the extended sample (full_sample_btc_data.csv, N=2,896).

Two tests, paralleling the paper's two approaches:
  A. Parametric residual: uncertainty ~ vol + vol^2 + mom + mom^2 (+ log_volume);
     extreme-vs-neutral on the residuals. (Parallels the comprehensive regression.)
  B. Nonparametric double-stratification: demean uncertainty within joint
     (volatility-quintile x momentum-tercile) bins, then extreme-vs-neutral.
     (Parallels the paper's surviving within-quintile pooled-demeaned test.)

For each we report Cohen's d, Welch t/p, and a moving-block permutation p
(block length 20) that respects the strong serial dependence of daily spreads,
consistent with the paper's inference of record.

Also summarises the Monte-Carlo weight-robustness COEFFICIENT distribution
(reviewer point: show coefficients, not just the binary ranking, survive random
weights), from mc_weight_robustness_results.csv.

Outputs:
    results/momentum_control_results.csv
    prints a summary.
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "..", "results")
RNG = np.random.default_rng(42)
MOM_WINDOW = 20
NEUTRAL = "neutral"
EXTREMES = ("extreme_fear", "extreme_greed")


def cohens_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    return (np.mean(a) - np.mean(b)) / sp if sp > 0 else np.nan


def block_perm_p(series, is_extreme, is_neutral, block=20, n_perm=5000):
    """Moving-block permutation p for the extreme-vs-neutral mean difference in
    `series`. Circularly block-shuffle the series (breaking its alignment to the
    regime labels) and recompute the difference; two-sided p."""
    s = np.asarray(series, float)
    n = len(s)
    obs = s[is_extreme].mean() - s[is_neutral].mean()
    count = 0
    nblocks = int(np.ceil(n / block))
    idx0 = np.arange(n)
    for _ in range(n_perm):
        # circular shift by a random offset, then re-block (moving-block scheme)
        off = RNG.integers(0, n)
        shifted = s[(idx0 + off) % n]
        # rebuild in random block order for extra mixing
        order = RNG.permutation(nblocks)
        chunks = [shifted[b * block:(b + 1) * block] for b in order]
        perm = np.concatenate(chunks)[:n]
        d = perm[is_extreme].mean() - perm[is_neutral].mean()
        if abs(d) >= abs(obs):
            count += 1
    return (count + 1) / (n_perm + 1)


def main():
    df = pd.read_csv(os.path.join(RES, "full_sample_btc_data.csv"), parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    # trailing momentum: sum of previous MOM_WINDOW returns, strictly lagged
    df["momentum"] = df["returns"].shift(1).rolling(MOM_WINDOW).sum()
    d = df.dropna(subset=["uncertainty", "volatility", "momentum", "regime"]).copy()
    d = d[d["regime"].isin([NEUTRAL, *EXTREMES])].copy()
    ext = d["regime"].isin(EXTREMES).values
    neu = (d["regime"] == NEUTRAL).values
    print(f"N used = {len(d)}  (extreme={ext.sum()}, neutral={neu.sum()}); "
          f"momentum = trailing {MOM_WINDOW}-day return")

    rows = []

    # ---- baseline (no control) for reference ----
    u = d["uncertainty"].values
    d0 = cohens_d(u[ext], u[neu])
    t0, p0 = stats.ttest_ind(u[ext], u[neu], equal_var=False)
    rows.append({"spec": "raw extreme-vs-neutral", "cohens_d": d0, "welch_t": t0,
                 "welch_p": p0, "block_perm_p": block_perm_p(u, ext, neu)})

    # ---- A. parametric residual: control vol (+^2) and momentum (+^2), volume ----
    for label, controls in [
        ("resid: vol+vol^2", ["volatility", "vol2"]),
        ("resid: vol+vol^2+mom+mom^2", ["volatility", "vol2", "momentum", "mom2"]),
        ("resid: vol+vol^2+mom+mom^2+logvol", ["volatility", "vol2", "momentum", "mom2", "log_volume"]),
    ]:
        dd = d.copy()
        dd["vol2"] = dd["volatility"] ** 2
        dd["mom2"] = dd["momentum"] ** 2
        cols = [c for c in controls if c in dd.columns and dd[c].notna().any()]
        sub = dd.dropna(subset=cols + ["uncertainty"])
        X = sm.add_constant(sub[cols].values)
        resid = sm.OLS(sub["uncertainty"].values, X).fit().resid
        e = sub["regime"].isin(EXTREMES).values
        nn = (sub["regime"] == NEUTRAL).values
        dc = cohens_d(resid[e], resid[nn])
        tc, pc = stats.ttest_ind(resid[e], resid[nn], equal_var=False)
        bp = block_perm_p(resid, e, nn)
        rows.append({"spec": label, "cohens_d": dc, "welch_t": tc, "welch_p": pc,
                     "block_perm_p": bp})

    # ---- B. nonparametric double-stratification (vol quintile x mom tercile) ----
    dd = d.copy()
    dd["vq"] = pd.qcut(dd["volatility"], 5, labels=False, duplicates="drop")
    dd["mt"] = pd.qcut(dd["momentum"], 3, labels=False, duplicates="drop")
    dd["u_dm"] = dd.groupby(["vq", "mt"])["uncertainty"].transform(lambda x: x - x.mean())
    e = dd["regime"].isin(EXTREMES).values
    nn = (dd["regime"] == NEUTRAL).values
    ddm = cohens_d(dd["u_dm"].values[e], dd["u_dm"].values[nn])
    tdm, pdm = stats.ttest_ind(dd["u_dm"].values[e], dd["u_dm"].values[nn], equal_var=False)
    bpdm = block_perm_p(dd["u_dm"].values, e, nn)
    rows.append({"spec": "demean within vol-quintile x mom-tercile", "cohens_d": ddm,
                 "welch_t": tdm, "welch_p": pdm, "block_perm_p": bpdm})

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RES, "momentum_control_results.csv"), index=False)
    print("\n" + "=" * 74)
    print("MOMENTUM CONTROL — extremity premium (extreme vs neutral uncertainty)")
    print("=" * 74)
    for _, r in out.iterrows():
        print(f"  {r['spec']:42s} d={r['cohens_d']:+.3f}  welch_p={r['welch_p']:.2e}  "
              f"block-perm_p={r['block_perm_p']:.4f}")

    # ---- MC weight COEFFICIENT distribution (point 3) ----
    mc = pd.read_csv(os.path.join(RES, "mc_weight_robustness_results.csv"))
    print("\n" + "=" * 74)
    print("MONTE-CARLO WEIGHT ROBUSTNESS — coefficient (gap) distribution over 1000 draws")
    print("=" * 74)
    for col in ["greed_gap", "fear_gap"]:
        v = mc[col].values
        print(f"  {col}: median={np.median(v):+.3f}  IQR=[{np.percentile(v,25):+.3f},{np.percentile(v,75):+.3f}]  "
              f"min={v.min():+.3f}  %>0={(v>0).mean()*100:.1f}%")
    print("Saved: results/momentum_control_results.csv")


if __name__ == "__main__":
    main()
