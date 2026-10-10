"""Visual layer for the Streamlit app.

Design system ported from the author's portfolio site (editorial black):
  void #0E0E0E / surface #1A1A1A / line #2A2A2A, mist #9A9A9A body copy, paper #FFFFFF headlines,
  Syne 800 uppercase display type, Inter body, JetBrains Mono for labels, tags and buttons,
  square corners and hairline borders. The site's ember-orange accent is swapped for a finance green.
Idea kept from the X-ray concept: the number apps show is a hollow ghost, the number that matters is solid.
"""
from __future__ import annotations

import html


def _h(s: str) -> str:
    """Collapse HTML to one line so Streamlit's markdown never treats it as code."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
:root{--void:#0E0E0E;--surface:#1A1A1A;--line:#2A2A2A;--signal:#00D084;--signal-dim:#00905C;--pulse:#6CFFC0;--mist:#9A9A9A;--paper:#FFFFFF;--neg:#FF5A4F;
--display:'Syne',system-ui,sans-serif;--body:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'JetBrains Mono',ui-monospace,Menlo,monospace;}
html,body,.stApp,[data-testid="stAppViewContainer"]{font-family:var(--body);color:var(--paper);}
.stApp{background:var(--void);}
::selection{background:rgba(0,208,132,.3);color:#fff;}
:focus-visible{outline:2px solid var(--signal)!important;outline-offset:2px;}
html{scroll-behavior:smooth;}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{visibility:hidden;height:0;}
header[data-testid="stHeader"]{background:transparent;height:0;}
.block-container{max-width:1120px;padding-top:2.4rem;padding-bottom:4rem;position:relative;z-index:2;}
.xr-glow{position:fixed;top:-180px;right:-140px;width:560px;height:560px;border-radius:50%;background:radial-gradient(circle,rgba(0,208,132,.16),rgba(14,14,14,0) 70%);pointer-events:none;z-index:0;}
.xr-brand{display:flex;align-items:center;gap:.7rem;margin-bottom:3rem;font-family:var(--display);font-weight:800;text-transform:uppercase;letter-spacing:.04em;font-size:.95rem;}
.xr-mark{width:22px;height:22px;border:1px solid var(--mist);position:relative;background:repeating-linear-gradient(135deg,rgba(154,154,154,.3) 0 3px,transparent 3px 6px);}
.xr-mark:after{content:"";position:absolute;left:0;top:0;bottom:0;width:60%;background:var(--signal);}
.xr-eyebrow{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.25em;color:rgba(0,208,132,.85);margin:0 0 1.2rem 0;}
.xr-h1{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(1.9rem,3.9vw,2.9rem);line-height:.95;letter-spacing:-.03em;margin:0 0 1.4rem 0;}
.xr-h1,.xr-h2,.xr-step h3{padding:0!important;}
.xr-h1 span{display:block;}
.xr-h1 .ghost{color:transparent;-webkit-text-stroke:1px rgba(255,255,255,.55);margin-bottom:.35rem;}
.xr-h1 .solid{color:var(--paper);}
.xr-h2{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(1.35rem,2.8vw,1.9rem);letter-spacing:-.02em;line-height:1;margin:3.6rem 0 1.3rem 0;}
.xr-lede{font-size:1.05rem;line-height:1.65;color:var(--mist);max-width:44ch;margin:0 0 1.8rem 0;}
.xr-panel{background:var(--surface);border:1px solid var(--line);padding:1.7rem 1.7rem 1.5rem;}
.xr-panel p{margin:0 0 1.3rem 0;color:var(--mist);line-height:1.6;}
.xr-panel .xr-kicker{margin:1.3rem 0 0 0;color:var(--paper);font-weight:500;}
.xr-bars{margin:.4rem 0 .9rem 0;}
.xr-track{position:relative;height:58px;}
.xr-ghost{position:absolute;left:0;top:0;bottom:0;border:1px solid var(--mist);background:repeating-linear-gradient(135deg,rgba(154,154,154,.22) 0 6px,transparent 6px 12px);}
.xr-solid{position:absolute;left:0;top:0;bottom:0;background:var(--signal);animation:xr-grow 1s cubic-bezier(.2,.7,.2,1) both;}
@keyframes xr-grow{from{width:0}}
.xr-legend{display:flex;flex-wrap:wrap;gap:.6rem 1.8rem;margin-top:1rem;font-size:.9rem;color:var(--mist);}
.xr-legend b{color:var(--paper);font-family:var(--display);font-weight:800;font-size:1.1rem;margin-left:.45rem;}
.sw{display:inline-block;width:14px;height:14px;margin-right:.55rem;vertical-align:-2px;box-sizing:border-box;}
.sw-ghost{border:1px solid var(--mist);background:repeating-linear-gradient(135deg,rgba(154,154,154,.3) 0 3px,transparent 3px 6px);}
.sw-solid{background:var(--signal);}
.xr-marquee{overflow:hidden;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:3rem 0 0 0;padding:.8rem 0;}
.xr-marquee-track{display:inline-flex;white-space:nowrap;width:max-content;animation:xr-marquee 30s linear infinite;}
.xr-marquee-track span{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:1.7rem;letter-spacing:-.02em;color:transparent;-webkit-text-stroke:1px rgba(255,255,255,.3);padding:0 1.2rem;}
.xr-marquee-track span.sep{color:var(--signal);-webkit-text-stroke:0;padding:0;}
@keyframes xr-marquee{to{transform:translateX(-50%)}}
.xr-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;}
.xr-step{border-top:1px solid var(--line);padding-top:1.1rem;}
.xr-step .n{font-family:var(--mono);font-size:.78rem;color:var(--signal);letter-spacing:.2em;display:block;margin-bottom:.9rem;}
.xr-step h3{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:1.1rem;letter-spacing:-.01em;line-height:1.1;margin:0 0 .6rem 0;}
.xr-step p{margin:0;color:var(--mist);line-height:1.6;max-width:34ch;}
.xr-stats{display:grid;grid-template-columns:repeat(var(--cols,4),1fr);gap:1.6rem;margin:.6rem 0 2.4rem 0;}
.xr-stat{border-top:1px solid var(--line);padding-top:.9rem;}
.xr-stat.accent{border-top:2px solid var(--signal);}
.xr-stat .v{font-family:var(--display);font-weight:800;font-size:clamp(1.6rem,3.2vw,2.5rem);letter-spacing:-.03em;font-variant-numeric:tabular-nums;line-height:1.05;color:var(--paper);}
.xr-stat.accent .v,.xr-stat .v.pos{color:var(--signal);}
.xr-stat .v.neg{color:var(--neg);}
.xr-stat .l{font-family:var(--mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.12em;color:var(--mist);margin-top:.5rem;}
.xr-chip{display:inline-block;font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--mist);background:var(--surface);border:1px solid var(--line);padding:.25rem .55rem;margin-left:.8rem;vertical-align:middle;font-weight:400;}
.xr-next{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;}
.xr-next div{border-top:1px solid var(--line);padding-top:1rem;}
.xr-next b{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:1rem;letter-spacing:-.01em;display:block;margin-bottom:.5rem;}
.xr-next span{color:var(--mist);line-height:1.6;display:block;}
.xr-foot{margin-top:3.6rem;padding-top:1.3rem;border-top:1px solid var(--line);color:var(--mist);font-size:.88rem;line-height:1.7;max-width:70ch;}
.xr-sentence{font-size:1.1rem;line-height:1.6;max-width:60ch;margin:1.3rem 0 2.4rem 0;color:var(--paper);}
/* Streamlit widgets in the same language: square, hairline, mono */
div[data-testid="stButton"] button,div[data-testid="stDownloadButton"] button,[data-testid="stFileUploader"] button{border-radius:0!important;font-family:var(--mono)!important;text-transform:uppercase;letter-spacing:.06em;font-size:.8rem!important;padding:.8rem 1.8rem!important;transition:background-color .2s,border-color .2s,color .2s;}
div[data-testid="stButton"] button[kind="primary"],div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]{background:var(--signal)!important;color:var(--void)!important;border:1px solid var(--signal)!important;font-weight:500;}
div[data-testid="stButton"] button[kind="primary"]:hover,div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover{background:var(--signal-dim)!important;border-color:var(--signal-dim)!important;color:var(--paper)!important;}
div[data-testid="stDownloadButton"] button,[data-testid="stFileUploader"] button{background:transparent!important;color:var(--paper)!important;border:1px solid var(--line)!important;}
div[data-testid="stDownloadButton"] button:hover,[data-testid="stFileUploader"] button:hover{border-color:var(--signal)!important;color:var(--paper)!important;}
[data-testid="stFileUploaderDropzone"]{background:var(--surface)!important;border:1px dashed var(--line)!important;border-radius:0!important;}
div[data-baseweb="input"],div[data-baseweb="base-input"]{background:var(--surface)!important;border-radius:0!important;border-color:var(--line)!important;}
div[data-baseweb="select"]>div{background:var(--surface)!important;border-radius:0!important;border:1px solid var(--line)!important;}
div[data-baseweb="input"]:focus-within,div[data-baseweb="select"]>div:focus-within{border-color:var(--signal)!important;}
[data-testid="stExpander"] details{border:1px solid var(--line)!important;border-radius:0!important;background:transparent!important;}
[data-testid="stExpander"] summary{font-family:var(--mono);font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;}
[data-testid="stAlert"]{border-radius:0!important;border:1px solid var(--line)!important;background:var(--surface)!important;}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:1px solid var(--line);}
button[role="tab"]{font-family:var(--mono)!important;text-transform:uppercase;letter-spacing:.08em;font-size:.78rem!important;}
[data-baseweb="tab-highlight"]{background-color:var(--signal)!important;}
[data-baseweb="tab-border"]{background-color:var(--line)!important;}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important;}}
@media (max-width:760px){.xr-steps,.xr-next{grid-template-columns:1fr;gap:1.6rem}.xr-stats{grid-template-columns:repeat(2,minmax(0,1fr));gap:1.2rem}.xr-brand{margin-bottom:2rem}}
</style>
"""


def brand_html() -> str:
    return _h('<div class="xr-glow"></div><div class="xr-brand"><span class="xr-mark"></span>Portfolio X-Ray</div>')


def hero_title_html() -> str:
    return _h("""
    <div class="xr-eyebrow">Built for Indian retail investors</div>
    <div class="xr-h1" role="heading" aria-level="1"><span class="ghost">Your broker shows a green number.</span>
    <span class="solid">Here is what you actually earned.</span></div>
    <p class="xr-lede">Upload your trades. Portfolio X-Ray works out your real yearly return,
    your tax bill and what selling would cost, in plain rupees.</p>""")


def bars_html(simple_pct: float, real_pct: float, simple_label: str, real_label: str) -> str:
    """Hollow ghost bar (total gain) with a solid bar (real yearly return) inside it."""
    scale = max(simple_pct, real_pct, 1e-9)
    gw = max(simple_pct, 0) / scale * 100
    sw = max(real_pct, 0) / scale * 100
    label = html.escape(f"Total gain {simple_label}; real return {real_label} a year")
    return _h(f"""
    <div class="xr-bars">
      <div class="xr-track" role="img" aria-label="{label}">
        <div class="xr-ghost" style="width:{gw:.1f}%"></div>
        <div class="xr-solid" style="width:{sw:.1f}%"></div>
      </div>
      <div class="xr-legend">
        <span><i class="sw sw-ghost"></i>Total gain on money put in<b>{html.escape(simple_label)}</b></span>
        <span><i class="sw sw-solid"></i>Real return per year<b>{html.escape(real_label)}</b></span>
      </div>
    </div>""")


def hero_panel_html() -> str:
    # Worked example, verified: XIRR of -10000 (1 Jan 2023), -10000 (1 Jan 2024), +24000 (1 Jan 2025) = 12.76%.
    bars = bars_html(20.0, 12.76, "20%", "12.76%")
    return _h(f"""
    <div class="xr-panel">
      <p>Put in ₹10,000 in January 2023 and another ₹10,000 in January 2024.
      By January 2025 it is worth ₹24,000.</p>
      {bars}
      <p class="xr-kicker">Same money, two very different numbers. The second one is the one you can fairly compare with a bank deposit.</p>
    </div>""")


def marquee_html() -> str:
    items = ["True return", "Tax by lot", "Fund overlap", "Risk and falls", "Crash replays"]
    one = "".join(f"<span>{html.escape(i)}</span><span class='sep'>/</span>" for i in items)
    return _h(f'<div class="xr-marquee" aria-hidden="true"><div class="xr-marquee-track">{one}{one}</div></div>')


def steps_html() -> str:
    return _h("""
    <div class="xr-steps">
      <div class="xr-step"><span class="n">01</span><h3>Upload your trades</h3>
        <p>A simple CSV, or the tradebook you download from Zerodha. The app does not save your file.</p></div>
      <div class="xr-step"><span class="n">02</span><h3>We match every trade</h3>
        <p>Each rupee is weighed by how long it stayed invested, and each sale is matched to your oldest units first.</p></div>
      <div class="xr-step"><span class="n">03</span><h3>See what really happened</h3>
        <p>Your real yearly return, tax by financial year, and what selling today would cost.</p></div>
    </div>""")


def stats_html(items: list[tuple[str, str, str]], cols: int = 4) -> str:
    """items: (label, value, tone) with tone in {'accent','pos','neg',''}."""
    cells = []
    for label, value, tone in items:
        outer = " accent" if tone == "accent" else ""
        inner = f" {tone}" if tone in ("pos", "neg") else ""
        cells.append(f'<div class="xr-stat{outer}"><div class="v{inner}">{html.escape(value)}</div>'
                     f'<div class="l">{html.escape(label)}</div></div>')
    return _h(f'<div class="xr-stats" style="--cols:{cols}">' + "".join(cells) + "</div>")


def next_html() -> str:
    return _h("""
    <div class="xr-next">
      <div><b>Fund overlap</b><span>See how many different stocks sit behind your mutual funds. The calculation is built and tested; the screen is next.</span></div>
      <div><b>Risk and falls</b><span>How far your portfolio can drop, and how long it takes to recover. Built and tested; screen next.</span></div>
      <div><b>Crash replays</b><span>Your portfolio through 2008, 2016, 2018 and 2020. Built and tested; screen next.</span></div>
    </div>""")


def foot_html() -> str:
    return _h("""
    <div class="xr-foot">Portfolio X-Ray is an educational tool, not financial or tax advice.
    Tax figures are estimates that ignore surcharge, cess, STT and loss carry-forward.
    The app does not save your file. Built by Divij Prajapati.</div>""")
