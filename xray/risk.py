"""Risk metrics on a price (or portfolio value) series."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

TRADING_DAYS = 252


def returns(prices: pd.Series) -> pd.Series:
    return prices.pct_change().dropna()


def annualised_vol(rets: pd.Series) -> float:
    return float(rets.std(ddof=1) * np.sqrt(TRADING_DAYS))


def max_drawdown(prices: pd.Series) -> dict:
    """Largest peak-to-trough fall, with peak/trough dates and days to recover."""
    running_max = prices.cummax()
    dd = prices / running_max - 1.0
    trough = dd.idxmin()
    peak = prices.loc[:trough].idxmax()
    recovered = prices.loc[trough:]
    back = recovered[recovered >= prices.loc[peak]]
    recovery_days = (back.index[0] - trough).days if len(back) else None
    return {"max_drawdown": float(dd.min()), "peak": peak, "trough": trough,
            "recovery_days": recovery_days}


def historical_var(rets: pd.Series, confidence: float = 0.95) -> float:
    """One-day VaR as a positive loss fraction, from the empirical distribution."""
    return float(-np.percentile(rets, (1 - confidence) * 100))


def parametric_var(rets: pd.Series, confidence: float = 0.95) -> float:
    """One-day VaR assuming normal returns. Understates tail risk: real returns
    have fat tails, so compare against historical_var and say so in the write-up."""
    mu, sigma = rets.mean(), rets.std(ddof=1)
    return float(-(mu + sigma * norm.ppf(1 - confidence)))


def sharpe(rets: pd.Series, risk_free_annual: float = 0.065) -> float:
    rf_daily = (1 + risk_free_annual) ** (1 / TRADING_DAYS) - 1
    excess = rets - rf_daily
    return float(excess.mean() / excess.std(ddof=1) * np.sqrt(TRADING_DAYS))


def portfolio_value(units: dict[str, float], prices: pd.DataFrame) -> pd.Series:
    """Value of fixed holdings through time. Needs one price column per asset."""
    cols = list(units)
    return (prices[cols].ffill().dropna() * pd.Series(units)).sum(axis=1)
