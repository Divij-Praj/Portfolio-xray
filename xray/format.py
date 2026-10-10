"""Display helpers: Indian digit grouping (lakh/crore) and rupee formatting."""
from __future__ import annotations


def group_indian(n: int) -> str:
    """12345678 -> '1,23,45,678'."""
    s = str(abs(int(n)))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts) + "," + tail


def inr(x: float, decimals: int = 0) -> str:
    """Rupee string with Indian grouping and a leading minus for negatives."""
    neg = x < 0
    x = abs(x)
    whole = int(x)
    frac = round(x - whole, decimals) if decimals else 0.0
    if decimals and frac >= 1:
        whole, frac = whole + 1, 0.0
    if not decimals:
        whole = int(round(x))
    out = group_indian(whole)
    if decimals:
        out += f"{frac:.{decimals}f}"[1:]
    return ("-" if neg else "") + "₹" + out


def pct(x: float, decimals: int = 1) -> str:
    return f"{x:.{decimals}f}%"
