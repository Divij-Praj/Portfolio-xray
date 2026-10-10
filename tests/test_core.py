from datetime import date

import numpy as np
import pandas as pd
import pytest

from xray.xirr import xirr
from xray.tax import TaxRules, realized_gains, tax_summary, open_lots, whatif_sale_tax
from xray.risk import max_drawdown, historical_var, parametric_var
from xray.overlap import pair_overlap, look_through, concentration
from xray.stress import run_scenario
from xray.parsers import load_transactions


def test_xirr_one_year_ten_percent():
    r = xirr([(date(2023, 1, 1), -1000), (date(2024, 1, 1), 1100)])
    assert r == pytest.approx(0.10, abs=1e-4)


def test_xirr_requires_both_signs():
    with pytest.raises(ValueError):
        xirr([(date(2023, 1, 1), -1000), (date(2024, 1, 1), -5)])


def _tx(rows):
    df = pd.DataFrame(rows, columns=["date", "asset", "side", "quantity", "price"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_fifo_and_term_classification():
    tx = _tx([("2022-01-01", "X", "BUY", 10, 100), ("2023-06-01", "X", "BUY", 10, 200),
              ("2023-07-01", "X", "SELL", 15, 300)])
    g = realized_gains(tx)
    assert len(g) == 2
    first, second = g.iloc[0], g.iloc[1]
    assert first.quantity == 10 and first.term == "LTCG" and first.gain == 2000
    assert second.quantity == 5 and second.term == "STCG" and second.gain == 500


def test_exactly_365_days_is_short_term():
    tx = _tx([("2023-01-01", "X", "BUY", 1, 100), ("2024-01-01", "X", "SELL", 1, 150)])
    assert realized_gains(tx).iloc[0].term == "STCG"


def test_oversell_raises():
    tx = _tx([("2023-01-01", "X", "BUY", 1, 100), ("2023-02-01", "X", "SELL", 2, 150)])
    with pytest.raises(ValueError):
        realized_gains(tx)


def test_tax_summary_applies_exemption():
    tx = _tx([("2021-01-01", "X", "BUY", 1000, 100), ("2023-01-02", "X", "SELL", 1000, 300)])
    s = tax_summary(realized_gains(tx), TaxRules())
    assert s.iloc[0].ltcg == 200_000
    assert s.iloc[0].est_tax == pytest.approx((200_000 - 125_000) * 0.125)


def test_open_lots_and_whatif():
    tx = _tx([("2022-01-01", "X", "BUY", 10, 100), ("2024-01-01", "X", "BUY", 10, 200),
              ("2024-02-01", "X", "SELL", 5, 250)])
    lots = open_lots(tx)
    assert sum(l.quantity for l in lots) == 15
    res = whatif_sale_tax(lots, "X", 10, 300, pd.Timestamp("2024-03-01"))
    assert res["ltcg"] == 5 * 200 and res["stcg"] == 5 * 100


def test_max_drawdown_and_recovery():
    idx = pd.date_range("2020-01-01", periods=6)
    p = pd.Series([100, 120, 60, 80, 121, 130], index=idx)
    d = max_drawdown(p)
    assert d["max_drawdown"] == pytest.approx(-0.5)
    assert d["peak"] == idx[1] and d["trough"] == idx[2]
    assert d["recovery_days"] == 2


def test_var_orderings():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.0005, 0.01, 5000))
    assert historical_var(r) == pytest.approx(parametric_var(r), abs=0.002)
    assert historical_var(r, 0.99) > historical_var(r, 0.95)


def test_overlap_and_lookthrough():
    a = {"A": 0.5, "B": 0.5}
    b = {"B": 0.25, "C": 0.75}
    assert pair_overlap(a, b) == 0.25
    lt = look_through({"f1": a, "f2": b}, {"f1": 100, "f2": 100})
    assert lt.loc["B", "exposure"] == pytest.approx(0.375)
    c = concentration(lt["exposure"])
    assert c["effective_stocks"] > 1


def test_stress_scenario():
    idx = pd.date_range("2020-01-01", periods=10)
    v = pd.Series([100, 100, 90, 80, 70, 75, 90, 100, 105, 110], index=idx)
    res = run_scenario(v, "2020-01-01", "2020-01-05")
    assert res["window_return"] == pytest.approx(-0.30)
    assert res["worst_drawdown"] == pytest.approx(-0.30)
    assert res["days_to_recover"] == 3


def test_parser_zerodha_columns(tmp_path):
    f = tmp_path / "tb.csv"
    f.write_text("symbol,trade_date,trade_type,quantity,price\nINFY,2023-01-02,buy,5,1500\n")
    df = load_transactions(f)
    assert list(df.columns) == ["date", "asset", "side", "quantity", "price"]
    assert df.iloc[0].side == "BUY"


def test_inr_formatting():
    from xray.format import inr
    assert inr(0) == "₹0"
    assert inr(1000) == "₹1,000"
    assert inr(123456) == "₹1,23,456"
    assert inr(12345678) == "₹1,23,45,678"
    assert inr(-2500.4) == "-₹2,500"
