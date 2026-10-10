"""FIFO tax-lot engine for listed equity / equity mutual funds (India).

Rates are CONFIGURABLE on purpose: they have changed in recent Budgets.
Defaults reflect the post-July-2024 regime (STCG 20%, LTCG 12.5% above a
Rs 1.25 lakh yearly exemption, long-term = held more than 12 months).
VERIFY against the current Income Tax rules before relying on any number.
Ignores surcharge, cess, STT, brokerage, grandfathering of pre-Feb-2018 lots.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class TaxRules:
    stcg_rate: float = 0.20
    ltcg_rate: float = 0.125
    ltcg_exemption: float = 125_000.0
    long_term_days: int = 365  # held MORE than this => long term


@dataclass
class Lot:
    asset: str
    buy_date: pd.Timestamp
    quantity: float
    price: float


def fy_label(d: pd.Timestamp) -> str:
    start = d.year if d.month >= 4 else d.year - 1
    return f"FY{start}-{str(start + 1)[-2:]}"


def realized_gains(tx: pd.DataFrame, rules: TaxRules | None = None) -> pd.DataFrame:
    """Match each SELL against earliest BUY lots (FIFO) and classify the gain."""
    rules = rules or TaxRules()
    lots: dict[str, list[Lot]] = {}
    rows = []
    for r in tx.sort_values("date", kind="stable").itertuples():
        book = lots.setdefault(r.asset, [])
        if r.side == "BUY":
            book.append(Lot(r.asset, r.date, r.quantity, r.price))
            continue
        remaining = r.quantity
        while remaining > 1e-9:
            if not book:
                raise ValueError(f"Selling more {r.asset} than held on {r.date.date()}")
            lot = book[0]
            take = min(lot.quantity, remaining)
            days = (r.date - lot.buy_date).days
            rows.append({
                "asset": r.asset, "buy_date": lot.buy_date, "sell_date": r.date,
                "quantity": take, "buy_price": lot.price, "sell_price": r.price,
                "gain": take * (r.price - lot.price), "holding_days": days,
                "term": "LTCG" if days > rules.long_term_days else "STCG",
                "fy": fy_label(r.date),
            })
            lot.quantity -= take
            remaining -= take
            if lot.quantity <= 1e-9:
                book.pop(0)
    return pd.DataFrame(rows)


def open_lots(tx: pd.DataFrame) -> list[Lot]:
    """Lots still held after applying all sells FIFO."""
    lots: dict[str, list[Lot]] = {}
    for r in tx.sort_values("date", kind="stable").itertuples():
        book = lots.setdefault(r.asset, [])
        if r.side == "BUY":
            book.append(Lot(r.asset, r.date, r.quantity, r.price))
        else:
            remaining = r.quantity
            while remaining > 1e-9 and book:
                take = min(book[0].quantity, remaining)
                book[0].quantity -= take
                remaining -= take
                if book[0].quantity <= 1e-9:
                    book.pop(0)
    return [l for book in lots.values() for l in book]


def tax_summary(gains: pd.DataFrame, rules: TaxRules | None = None) -> pd.DataFrame:
    """Per-financial-year STCG/LTCG and estimated tax. Losses offset within a class
    only (simplified: no cross-set-off, no carry-forward)."""
    rules = rules or TaxRules()
    if gains.empty:
        return pd.DataFrame(columns=["fy", "stcg", "ltcg", "taxable_ltcg", "est_tax"])
    out = []
    for fy, g in gains.groupby("fy"):
        stcg = g.loc[g.term == "STCG", "gain"].sum()
        ltcg = g.loc[g.term == "LTCG", "gain"].sum()
        taxable_ltcg = max(0.0, ltcg - rules.ltcg_exemption)
        tax = max(0.0, stcg) * rules.stcg_rate + taxable_ltcg * rules.ltcg_rate
        out.append({"fy": fy, "stcg": stcg, "ltcg": ltcg,
                    "taxable_ltcg": taxable_ltcg, "est_tax": tax})
    return pd.DataFrame(out).sort_values("fy").reset_index(drop=True)


def whatif_sale_tax(lots: list[Lot], asset: str, quantity: float, price: float,
                    on: pd.Timestamp, rules: TaxRules | None = None) -> dict:
    """Tax cost of selling `quantity` of `asset` today (FIFO), ignoring the exemption."""
    rules = rules or TaxRules()
    remaining, stcg, ltcg = quantity, 0.0, 0.0
    for lot in [l for l in lots if l.asset == asset]:
        if remaining <= 1e-9:
            break
        take = min(lot.quantity, remaining)
        g = take * (price - lot.price)
        if (on - lot.buy_date).days > rules.long_term_days:
            ltcg += g
        else:
            stcg += g
        remaining -= take
    if remaining > 1e-9:
        raise ValueError("Not enough units held")
    tax = max(0.0, stcg) * rules.stcg_rate + max(0.0, ltcg) * rules.ltcg_rate
    return {"stcg": stcg, "ltcg": ltcg, "est_tax_before_exemption": tax}
