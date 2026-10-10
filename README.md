# Portfolio X-Ray

Analytics for Indian retail investors that tutorials don't cover: true XIRR, FIFO tax lots under Indian rules, hidden fund overlap, and stress tests on Indian market events.

> Status: core engine done and tested (13 tests). The web app has a landing page, results dashboard, tax view and what-if sale tool. Risk, overlap and stress tests are built but not on screen yet. Not financial advice.

## What it does (and what's next)

| Module | Status | Notes |
|---|---|---|
| `xray/xirr.py` | done | Excel-compatible actual/365 XIRR |
| `xray/tax.py` | done | FIFO lots, STCG/LTCG, per-FY summary, what-if sale. Rates configurable, verify against current law |
| `xray/risk.py` | done | Volatility, max drawdown + recovery, historical and parametric VaR, Sharpe |
| `xray/overlap.py` | done | Pairwise overlap, look-through exposure, effective number of stocks |
| `xray/stress.py` | done | Replays value series through 2008, 2016, 2018, 2020 windows (verify dates) |
| `xray/data.py` | written, untested | mfapi.in NAVs, yfinance prices |
| `xray/format.py` | done | Indian digit grouping (lakh/crore) for rupee amounts |
| `xray/parsers.py` | CSV only | CAMS/KFintech CAS PDF parsing is the hard TODO |
| `app.py` + `xray/ui.py` | done (v1) | Landing explainer, sample portfolio, price editor, real vs total return, money-over-time chart, tax by year, what-if sale |

## Run locally

```bash
pip install -r requirements.txt
pytest
streamlit run app.py
```

Click "Try a sample portfolio", or upload `sample_data/sample_transactions.csv`.

## Put it online (free)

1. Push this repo to GitHub (public).
2. Go to share.streamlit.io, sign in with GitHub, choose the repo, set the main file to `app.py`, deploy.
3. Every push to GitHub redeploys the site.

Note: on a hosted app the file passes through the host's servers. The app does not save it, but do not claim it never leaves the user's device.

## Roadmap

1. Week 1: validate XIRR and gains against a real platform's reported numbers; document differences
2. Week 2: wire `data.py` into the app (live NAVs, auto current value); test against real mfapi responses
3. Week 3: AMC holdings ingestion for overlap; overlap heatmap in the UI
4. Week 4: stress tests UI with Nifty 50 benchmark; confirm scenario dates from index data
5. Week 5: deploy (Streamlit Community Cloud), screenshots, privacy note
6. Week 6: get 10+ real users, write the 2-page methodology note (assumptions, limits of VaR, tax simplifications)

## Known limitations (state these honestly in the write-up)

- Tax ignores surcharge, cess, STT, grandfathering of pre-2018 lots, and loss carry-forward
- Parametric VaR assumes normal returns and understates tail risk
- Stress windows are approximate peak-to-trough dates
- Funds with mergers/renames/IDCW payouts are not handled yet
