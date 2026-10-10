"""Portfolio X-Ray: see what your broker app doesn't show you. Run: streamlit run app.py"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from xray import ui
from xray.format import inr, pct
from xray.parsers import cashflows_for_xirr, load_transactions
from xray.tax import TaxRules, open_lots, realized_gains, tax_summary, whatif_sale_tax
from xray.xirr import xirr

st.set_page_config(page_title="Portfolio X-Ray", page_icon=None, layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)

SAMPLE = Path(__file__).parent / "sample_data" / "sample_transactions.csv"
SAMPLE_PRICES = {"FUNDA": 80.0, "FUNDB": 45.0}
ACCENT = "#00D084"

# ---------------------------------------------------------------- landing
st.markdown(ui.brand_html(), unsafe_allow_html=True)

left, right = st.columns([1.05, 1], gap="large")
with left:
    st.markdown(ui.hero_title_html(), unsafe_allow_html=True)
    if st.button("Try a sample portfolio", type="primary"):
        st.session_state["sample"] = True
    uploaded = st.file_uploader("Or upload your own trades (CSV)", type="csv")
    with st.expander("What should my file look like?"):
        st.write(
            "One row per trade with the columns **date, asset, side, quantity, price**, "
            "where side is BUY or SELL. A Zerodha tradebook CSV also works."
        )
        st.download_button("Download the sample file", SAMPLE.read_bytes(),
                           file_name="sample_transactions.csv", mime="text/csv")
with right:
    st.markdown(ui.hero_panel_html(), unsafe_allow_html=True)

st.markdown(ui.marquee_html(), unsafe_allow_html=True)
st.markdown('<div class="xr-h2" role="heading" aria-level="2">How it works</div>', unsafe_allow_html=True)
st.markdown(ui.steps_html(), unsafe_allow_html=True)

# ---------------------------------------------------------------- data
is_sample = False
tx = None
if uploaded is not None:
    try:
        tx = load_transactions(uploaded)
    except Exception as e:  # noqa: BLE001 - show any parse problem to the user
        st.error(f"We could not read that file. {e}")
elif st.session_state.get("sample"):
    tx, is_sample = load_transactions(SAMPLE), True

if tx is not None:
    st.markdown(
        '<div class="xr-h2" role="heading" aria-level="2">Your portfolio'
        + ('<span class="xr-chip">Sample data</span>' if is_sample else "")
        + "</div>",
        unsafe_allow_html=True,
    )
    today = pd.Timestamp.today().normalize()

    with st.expander("Tax assumptions"):
        st.caption("Defaults follow the rules after July 2024. Check the current rules before you rely on any tax figure.")
        c1, c2, c3 = st.columns(3)
        stcg = c1.number_input("Short-term rate (%)", 0.0, 100.0, 20.0, 0.5)
        ltcg = c2.number_input("Long-term rate (%)", 0.0, 100.0, 12.5, 0.5)
        exempt = c3.number_input("Yearly long-term exemption (₹)", 0.0, 10_000_000.0, 125_000.0, 5_000.0)
    rules = TaxRules(stcg_rate=stcg / 100, ltcg_rate=ltcg / 100, ltcg_exemption=exempt)

    try:
        lots = open_lots(tx)
        gains = realized_gains(tx, rules)
    except ValueError as e:
        st.error(f"Your trades do not add up: {e}. Check the quantities on your SELL rows.")
        st.stop()

    held = sorted({l.asset for l in lots})
    holdings = pd.DataFrame({
        "Holding": held,
        "Units": [sum(l.quantity for l in lots if l.asset == a) for a in held],
        "Average cost": [
            sum(l.quantity * l.price for l in lots if l.asset == a) / sum(l.quantity for l in lots if l.asset == a)
            for a in held
        ],
        "Today's price": [SAMPLE_PRICES.get(a, 0.0) if is_sample else 0.0 for a in held],
    })

    prices = {}
    if held:
        st.markdown("**What is each holding worth today?** Type today's price per unit.")
        edited = st.data_editor(
            holdings, hide_index=True, width="stretch",
            key=f"prices-{'sample' if is_sample else 'upload'}-{'-'.join(held)}",
            disabled=["Holding", "Units", "Average cost"],
            column_config={
                "Units": st.column_config.NumberColumn(format="%.2f"),
                "Average cost": st.column_config.NumberColumn(format="₹%.2f"),
                "Today's price": st.column_config.NumberColumn(format="₹%.2f", min_value=0.0, required=True),
            },
        )
        prices = dict(zip(edited["Holding"], edited["Today's price"]))
    ready = bool(held) and all(p > 0 for p in prices.values())

    buys = float((tx.query("side == 'BUY'").eval("quantity * price")).sum())
    sells = float((tx.query("side == 'SELL'").eval("quantity * price")).sum())
    values = {a: sum(l.quantity for l in lots if l.asset == a) * prices.get(a, 0.0) for a in held}
    worth = float(sum(values.values()))

    if not ready:
        st.info("Enter today's price for every holding above to see your real return.")
    else:
        profit = sells + worth - buys
        simple = profit / buys * 100 if buys else 0.0
        try:
            real = xirr(cashflows_for_xirr(tx, values, today)) * 100
        except ValueError:
            real = None

        st.markdown(ui.stats_html([
            ("Real return per year", pct(real, 1) if real is not None else "n/a", "accent"),
            ("Money you put in", inr(buys), ""),
            ("Worth today", inr(worth), ""),
            ("Profit so far", inr(profit), "pos" if profit >= 0 else "neg"),
        ]), unsafe_allow_html=True)

        if real is not None and simple > 0 and real > 0:
            st.markdown('<div class="xr-h2" role="heading" aria-level="2" style="margin-top:1rem">Total gain is not the same as yearly return</div>',
                        unsafe_allow_html=True)
            st.markdown(ui.bars_html(simple, real, pct(simple, 1), pct(real, 1)), unsafe_allow_html=True)
            st.markdown(
                f'<p class="xr-sentence">You have made {pct(simple, 1)} on the money you put in. '
                f"Because it went in over time, that works out to {pct(real, 1)} a year.</p>",
                unsafe_allow_html=True,
            )
        elif real is not None:
            st.markdown(f'<p class="xr-sentence">Your real return works out to {pct(real, 1)} a year.</p>',
                        unsafe_allow_html=True)

        tab_time, tab_tax, tab_sell = st.tabs(["Money over time", "Tax", "If I sell"])

        with tab_time:
            t = tx.copy()
            t["flow"] = t.apply(lambda r: r.quantity * r.price * (1 if r.side == "BUY" else -1), axis=1)
            t["net"] = t["flow"].cumsum()
            line_df = pd.concat([
                pd.DataFrame({"date": [t["date"].min()], "net": [0.0]}),
                t[["date", "net"]],
                pd.DataFrame({"date": [today], "net": [t["net"].iloc[-1]]}),
            ])
            base = alt.Chart(line_df).encode(
                x=alt.X("date:T", title=None),
                y=alt.Y("net:Q", title="Net money put in (₹)", axis=alt.Axis(format=",.0f")),
            )
            area = base.mark_area(interpolate="step-after", color=ACCENT, opacity=0.14)
            line = base.mark_line(interpolate="step-after", color=ACCENT, strokeWidth=2)
            now = alt.Chart(pd.DataFrame({"date": [today], "value": [worth]})).mark_point(
                color="#FFFFFF", size=110, filled=True).encode(x="date:T", y="value:Q")
            chart = (area + line + now).properties(height=320).configure_axis(labelColor="#9A9A9A", titleColor="#9A9A9A", gridColor="#2A2A2A", domainColor="#2A2A2A", tickColor="#2A2A2A").configure_view(strokeWidth=0)
            st.altair_chart(chart, width="stretch")
            st.caption(f"Green line: money you have put in, net of sales. White dot: what your holdings are worth today ({inr(worth)}).")

        with tab_tax:
            summary = tax_summary(gains, rules)
            if summary.empty:
                st.write("You have not sold anything yet, so there is no tax to show.")
            else:
                shown = pd.DataFrame({
                    "Financial year": summary["fy"],
                    "Short-term gain": summary["stcg"].map(inr),
                    "Long-term gain": summary["ltcg"].map(inr),
                    "Long-term gain that is taxed": summary["taxable_ltcg"].map(inr),
                    "Estimated tax": summary["est_tax"].map(inr),
                })
                st.dataframe(shown, hide_index=True, width="stretch")
                with st.expander("See each sale, lot by lot"):
                    lots_view = gains.assign(
                        buy_date=gains["buy_date"].dt.date, sell_date=gains["sell_date"].dt.date,
                        gain=gains["gain"].map(inr),
                    )[["asset", "buy_date", "sell_date", "quantity", "holding_days", "term", "gain"]]
                    lots_view.columns = ["Holding", "Bought", "Sold", "Units", "Days held", "Type", "Gain"]
                    st.dataframe(lots_view, hide_index=True, width="stretch")
            st.caption("Estimates only. They ignore surcharge, cess, STT and loss carry-forward.")

        with tab_sell:
            if not held:
                st.write("You do not hold anything to sell.")
            else:
                s1, s2, s3 = st.columns(3)
                pick = s1.selectbox("Holding", held)
                max_units = float(sum(l.quantity for l in lots if l.asset == pick))
                units = s2.number_input("Units to sell", 0.0, max_units, min(max_units, 1.0), 1.0)
                sale_price = s3.number_input("Sale price per unit (₹)", 0.0, value=float(prices[pick]), step=1.0)
                if units > 0:
                    r = whatif_sale_tax(lots, pick, units, sale_price, today, rules)
                    st.markdown(ui.stats_html([
                        ("Short-term gain", inr(r["stcg"]), "pos" if r["stcg"] >= 0 else "neg"),
                        ("Long-term gain", inr(r["ltcg"]), "pos" if r["ltcg"] >= 0 else "neg"),
                        ("Estimated tax if you sell today", inr(r["est_tax_before_exemption"]), "accent"),
                    ], cols=3), unsafe_allow_html=True)
                    st.caption("Uses your oldest units first. Before the yearly long-term exemption, so the real bill can be lower.")

st.markdown('<div class="xr-h2" role="heading" aria-level="2">On the way</div>', unsafe_allow_html=True)
st.markdown(ui.next_html(), unsafe_allow_html=True)
st.markdown(ui.foot_html(), unsafe_allow_html=True)
