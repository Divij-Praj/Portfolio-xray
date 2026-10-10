"""Replay a portfolio through historical Indian market shocks.

Windows are APPROXIMATE peak-to-trough dates for the Nifty 50. Check them
against index data before publishing any numbers, and document your choice.
"""
from __future__ import annotations

import pandas as pd

SCENARIOS = {
    "2008 global financial crisis": ("2008-01-08", "2009-03-09"),
    "2016 demonetisation": ("2016-11-08", "2016-12-26"),
    "2018 IL&FS / NBFC shock": ("2018-08-28", "2018-10-26"),
    "2020 COVID crash": ("2020-01-20", "2020-03-23"),
}


def run_scenario(value: pd.Series, start: str, end: str) -> dict | None:
    """Return over the window, worst drawdown inside it, and days to regain the start level."""
    w = value.loc[start:end]
    if len(w) < 2:
        return None
    start_val = w.iloc[0]
    dd = (w / w.cummax() - 1.0).min()
    after = value.loc[w.index[-1]:]
    back = after[after >= start_val]
    recovery = (back.index[0] - w.index[-1]).days if len(back) else None
    return {"window_return": float(w.iloc[-1] / start_val - 1.0),
            "worst_drawdown": float(dd), "days_to_recover": recovery}


def run_all(value: pd.Series, scenarios: dict | None = None) -> pd.DataFrame:
    rows = []
    for name, (s, e) in (scenarios or SCENARIOS).items():
        res = run_scenario(value, s, e)
        rows.append({"scenario": name, **(res or {"window_return": None,
                     "worst_drawdown": None, "days_to_recover": None})})
    return pd.DataFrame(rows)
