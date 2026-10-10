"""XIRR: annualised return for irregular cash flows (what SIP investors actually earn)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Tuple

from scipy.optimize import brentq

Cashflow = Tuple[date, float]


def _to_date(d) -> date:
    return d.date() if isinstance(d, datetime) else d


def xnpv(rate: float, cashflows: Iterable[Cashflow]) -> float:
    cfs = [(_to_date(d), a) for d, a in cashflows]
    t0 = min(d for d, _ in cfs)
    return sum(a / (1.0 + rate) ** ((d - t0).days / 365.0) for d, a in cfs)


def xirr(cashflows: Iterable[Cashflow]) -> float:
    """Money invested is negative, money received (or current value) is positive.

    Same day-count convention as Excel's XIRR (actual/365), so results can be
    cross-checked against a spreadsheet.
    """
    cfs = [(_to_date(d), float(a)) for d, a in cashflows]
    if len(cfs) < 2:
        raise ValueError("Need at least two cash flows")
    if not (any(a < 0 for _, a in cfs) and any(a > 0 for _, a in cfs)):
        raise ValueError("Cash flows need at least one negative and one positive amount")
    return brentq(lambda r: xnpv(r, cfs), -0.999999, 1000.0, maxiter=500)
