'''
Percentiles for player profile, comparisons, and Explorer pages

Each value is ranked against a pool, by default the season's eligible players
(or those in the same position group). Players outside the pool still get a 
percentile against it. A percentile is the share of the pool below the value, 
counting ties as half on a 0-1 scale. 
'''

import numpy as np
import pandas as pd

MIN_POOL = 10

def _against_pool(values, pool):
    pool = np.sort(pool.dropna().to_numpy(dtype=float))
    if len(pool) < MIN_POOL: 
        return pd.Series(np.nan, index=values.index)
    v = values.to_numpy(dtype=float)
    below = np.searchsorted(pool, v, side='left')
    at_or_below = np.searchsorted(pool, v, side="right")
    pct = (below + at_or_below) / 2 / len(pool)
    return pd.Series(np.where(np.isnan(v), np.nan, pct), index=values.index)
def add_percentiles(df, columns, pool_mask=None, group_col=None):
    '''
    Return a df with a <column>_pctile for each column.
    '''
    out = df.copy()
    if pool_mask is None:
        pool_mask = out['is_eligible'].fillna(False).astype(bool) if "is_eligible" in out else pd.Series(True, index=out.index)
    groups = [(None, out.index)] if group_col is None else out.groupby(group_col, dropna=False).groups.items()
    for col in columns:
        result = pd.Series(np.nan, index=out.index)
        for _, idx in groups:
            idx = pd.Index(idx)
            result.loc[idx] = _against_pool(out.loc[idx, col], out.loc[idx, col][pool_mask.loc[idx]])
        out[f"{col}_pctile"] = result 
    return out 

def goodness(pctile, better=None):
    '''0-1 where 1 is best. Percentiles filip for lower is better stats. None if neutral.'''
    if pctile is None or pd.isna(pctile) or better is None:
        return None
    return pctile if better else 1 - pctile