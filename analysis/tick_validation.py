#!/usr/bin/env python3
"""
Calculate realized spreads from tick data and validate against uncertainty
"""
import gzip
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = Path(__file__).parent.parent / 'data' / 'lob' / 'btcusdt'
RESULTS_DIR = Path(__file__).parent.parent / 'results'

print("="*60)
print("CALCULATING REALIZED SPREADS FROM TICK DATA")
print("="*60)

files = sorted(DATA_DIR.glob('*_orderbook.csv.gz'))
print(f"Found {len(files)} trade files")

daily_results = []

for i, filepath in enumerate(files):
    try:
        # Extract date
        date_str = filepath.stem.split('_')[0].replace('BTCUSDT', '')

        # Read sample
        df = pd.read_csv(filepath, compression='gzip', nrows=300000)
        df.columns = df.columns.str.lower().str.strip()

        if 'price' not in df.columns or 'side' not in df.columns:
            print(f"[{i+1}/{len(files)}] {date_str}: Missing columns")
            continue

        df['is_buy'] = df['side'].str.lower() == 'buy'

        buy_prices = df.loc[df['is_buy'], 'price']
        sell_prices = df.loc[~df['is_buy'], 'price']

        if len(buy_prices) > 1000 and len(sell_prices) > 1000:
            mean_ask = buy_prices.mean()
            mean_bid = sell_prices.mean()
            midpoint = (mean_ask + mean_bid) / 2
            simple_spread_bps = (mean_ask - mean_bid) / midpoint * 10000

            df['effective_spread'] = np.where(
                df['is_buy'],
                2 * (df['price'] - midpoint) / midpoint * 10000,
                2 * (midpoint - df['price']) / midpoint * 10000
            )

            valid = (df['effective_spread'] > -50) & (df['effective_spread'] < 50)

            daily_results.append({
                'date': pd.to_datetime(date_str, format='%Y%m%d'),
                'effective_spread_mean': df.loc[valid, 'effective_spread'].mean(),
                'simple_spread_bps': simple_spread_bps,
                'n_trades': len(df),
                'buy_pct': df['is_buy'].mean() * 100
            })

            if (i+1) % 10 == 0:
                print(f"[{i+1}/{len(files)}] Processed, spread={simple_spread_bps:.2f} bps")

    except Exception as e:
        print(f"[{i+1}/{len(files)}] Error: {e}")

print(f"\nProcessed {len(daily_results)} days")

if daily_results:
    tick_df = pd.DataFrame(daily_results).set_index('date').sort_index()

    print(f"\nTick Summary:")
    print(f"  Effective spread mean: {tick_df['effective_spread_mean'].mean():.3f} bps")
    print(f"  Simple spread mean: {tick_df['simple_spread_bps'].mean():.3f} bps")

    tick_df.to_csv(RESULTS_DIR / 'tick_daily_spreads_90d.csv')

    # Validation against CS and uncertainty
    cs_df = pd.read_csv(RESULTS_DIR / 'real_spread_data.csv', parse_dates=['date']).set_index('date')
    common = tick_df.index.intersection(cs_df.index)
    print(f"\nOverlapping days with CS: {len(common)}")

    if len(common) > 20:
        tick_aligned = tick_df.loc[common]
        cs_aligned = cs_df.loc[common]

        # Tick vs CS spread
        cs_valid = ~cs_aligned['cs_spread'].isna() & (cs_aligned['cs_spread'] > 0)
        if cs_valid.sum() > 10:
            corr, p = stats.pearsonr(tick_aligned.loc[cs_valid, 'effective_spread_mean'],
                                      cs_aligned.loc[cs_valid, 'cs_spread'])
            spearman, sp_p = stats.spearmanr(tick_aligned.loc[cs_valid, 'effective_spread_mean'],
                                              cs_aligned.loc[cs_valid, 'cs_spread'])
            print(f"\n=== TICK vs CS SPREAD ===")
            print(f"  Pearson r: {corr:.3f} (p={p:.4f})")
            print(f"  Spearman r: {spearman:.3f} (p={sp_p:.4f})")
            print(f"  Tick mean: {tick_aligned['effective_spread_mean'].mean():.3f} bps")
            print(f"  CS mean: {cs_aligned.loc[cs_valid, 'cs_spread'].mean():.2f} bps")

        # Tick vs uncertainty
        print(f"\n=== TICK SPREAD vs UNCERTAINTY ===")
        for col in ['total_uncertainty', 'aleatoric_proxy', 'epistemic_proxy']:
            if col in cs_aligned.columns:
                valid = ~cs_aligned[col].isna()
                if valid.sum() > 20:
                    corr, p = stats.pearsonr(tick_aligned.loc[valid, 'effective_spread_mean'],
                                             cs_aligned.loc[valid, col])
                    spearman, sp_p = stats.spearmanr(tick_aligned.loc[valid, 'effective_spread_mean'],
                                                      cs_aligned.loc[valid, col])
                    print(f"  vs {col}:")
                    print(f"    Pearson r: {corr:.3f} (p={p:.4f})")
                    print(f"    Spearman r: {spearman:.3f} (p={sp_p:.4f})")

        # Tick vs volatility
        print(f"\n=== TICK SPREAD vs VOLATILITY ===")
        for col in ['parkinson_vol', 'realized_vol']:
            if col in cs_aligned.columns:
                valid = ~cs_aligned[col].isna()
                if valid.sum() > 20:
                    corr, p = stats.pearsonr(tick_aligned.loc[valid, 'effective_spread_mean'],
                                             cs_aligned.loc[valid, col])
                    print(f"  vs {col}: r={corr:.3f} (p={p:.4f})")

print("\nDone!")
