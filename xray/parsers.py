"""Load transaction files into one canonical shape.

Canonical columns: date, asset, side (BUY/SELL), quantity, price.
Supported inputs for now:
  * generic CSV with columns date, asset, side, quantity, price
  * Zerodha tradebook CSV (symbol, trade_date, trade_type, quantity, price)
TODO: CAMS/KFintech CAS PDF parsing (hardest part: layouts vary by provider).
"""
from __future__ import annotations

import pandas as pd

CANONICAL = ["date", "asset", "side", "quantity", "price"]

_ZERODHA_MAP = {"symbol": "asset", "trade_date": "date", "trade_type": "side"}


def load_transactions(path_or_buffer) -> pd.DataFrame:
    df = pd.read_csv(path_or_buffer)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={k: v for k, v in _ZERODHA_MAP.items() if k in df.columns})

    missing = [c for c in CANONICAL if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns {missing}. Expected {CANONICAL} or a Zerodha tradebook.")

    out = df[CANONICAL].copy()
    out["date"] = pd.to_datetime(out["date"])
    out["side"] = out["side"].str.strip().str.upper()
    bad = set(out["side"]) - {"BUY", "SELL"}
    if bad:
        raise ValueError(f"Unknown side values: {bad}")
    out["quantity"] = out["quantity"].astype(float)
    out["price"] = out["price"].astype(float)
    return out.sort_values("date", kind="stable").reset_index(drop=True)


def cashflows_for_xirr(tx: pd.DataFrame, current_values: dict[str, float], as_of) -> list:
    """Buys are outflows, sells inflows, plus current holdings value as a final inflow."""
    flows = []
    for r in tx.itertuples():
        amt = r.quantity * r.price
        flows.append((r.date.date(), -amt if r.side == "BUY" else amt))
    flows.append((pd.Timestamp(as_of).date(), float(sum(current_values.values()))))
    return flows
