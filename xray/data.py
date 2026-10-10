"""Network data fetchers. Kept separate so the maths stays testable offline."""
from __future__ import annotations

import pandas as pd
import requests


def mf_nav_history(scheme_code: int | str) -> pd.Series:
    """Daily NAV history from the free mfapi.in service."""
    r = requests.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=20)
    r.raise_for_status()
    rows = r.json()["data"]
    s = pd.Series(
        {pd.to_datetime(x["date"], format="%d-%m-%Y"): float(x["nav"]) for x in rows}
    ).sort_index()
    s.name = str(scheme_code)
    return s


def search_mf(query: str) -> list[dict]:
    r = requests.get("https://api.mfapi.in/mf/search", params={"q": query}, timeout=20)
    r.raise_for_status()
    return r.json()


def stock_history(symbol: str, start: str = "2007-01-01") -> pd.Series:
    """Daily close via yfinance. NSE tickers need the .NS suffix, e.g. RELIANCE.NS."""
    import yfinance as yf
    df = yf.download(symbol, start=start, progress=False, auto_adjust=True)
    s = df["Close"].squeeze()
    s.name = symbol
    return s
