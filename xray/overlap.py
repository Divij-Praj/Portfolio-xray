"""Look-through analysis for mutual fund portfolios.

Input: {fund_name: {stock: weight_fraction}} taken from AMC monthly disclosures.
"""
from __future__ import annotations

import itertools

import pandas as pd


def pair_overlap(a: dict[str, float], b: dict[str, float]) -> float:
    """Sum of min weights over shared stocks (0 = nothing shared, 1 = identical)."""
    return sum(min(a[s], b[s]) for s in a.keys() & b.keys())


def overlap_matrix(funds: dict[str, dict[str, float]]) -> pd.DataFrame:
    names = list(funds)
    m = pd.DataFrame(1.0, index=names, columns=names)
    for x, y in itertools.combinations(names, 2):
        m.loc[x, y] = m.loc[y, x] = pair_overlap(funds[x], funds[y])
    return m


def look_through(funds: dict[str, dict[str, float]], amounts: dict[str, float]) -> pd.DataFrame:
    """True stock exposure across all funds, weighted by rupees invested in each."""
    total = sum(amounts.values())
    exposure: dict[str, float] = {}
    for fund, holdings in funds.items():
        w_fund = amounts[fund] / total
        for stock, w in holdings.items():
            exposure[stock] = exposure.get(stock, 0.0) + w_fund * w
    s = pd.Series(exposure, name="exposure").sort_values(ascending=False)
    return s.to_frame()


def concentration(exposure: pd.Series) -> dict:
    """HHI and 'effective number of stocks' (1/HHI) on renormalised weights."""
    w = exposure / exposure.sum()
    hhi = float((w ** 2).sum())
    return {"hhi": hhi, "effective_stocks": 1.0 / hhi,
            "top5_share": float(w.nlargest(5).sum())}
