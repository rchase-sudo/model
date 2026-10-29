"""Build a watermarked preview page for a warm lead.

    python3 tools/make_preview.py tools/leads/<slug>.json

Reads the lead config, watermarks the render and plan, and writes
p/<slug>/index.html + p/<slug>/img/. Live at
https://rchase-sudo.github.io/model/p/<slug>/ once pushed.
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from watermark import watermark  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAGES = "https://rchase-sudo.github.io/model/p/"
PAYMENT = "https://formadesigns.io/payment"

esc = html.escape


def emph(text):
    """*word* -> <em>word</em>, everything else escaped."""
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", esc(text))


def build(cfg_path):
    c = json.loads(Path(cfg_path).read_text())
    slug = c["slug"]
    out = ROOT / "p" / slug
    (out / "img").mkdir(parents=True, exist_ok=True)

    watermark(c["images"]["render"], out / "img" / "render.jpg")
    watermark(c["images"]["plan"], out / "img" / "plan.jpg", dark=c["images"].get("plan_dark", True))
    rw, rh = Image.open(out / "img" / "render.jpg").size
    pw, ph = Image.open(out / "img" / "plan.jpg").size

    a = c.get("agent", {})
    pay = {"address": c["address_full"]}
    for k in ("name", "email", "phone"):
        if a.get(k):
            pay[k] = a[k]
    payment_url = PAYMENT + "?" + urlencode(pay) + "#order"

    nums = "".join(
        f'<div><strong class="{"g" if n.get("gold") else ""}">{esc(n["value"])}</strong><span>{emph(n["label"]).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")}</span></div>'
        for n in c["numbers"]
    )
    rows = ""
    r = c.get("rlv")
    if r:
        value, steps = r["value"], [("Hard costs", r["hard"]), ("Soft costs + financing", r["soft"]), ("Developer profit", r["profit"])]
        residual = value - sum(v for _, v in steps)
        money = lambda n: ("−" if n < 0 else "") + "$" + f"{abs(round(n)):,}"
        pct = lambda n: max(0.0, n / value * 100)
        rows += f'<div class="wf-row"><span>Completed project value</span><i class="bar up" style="--w:100%"></i><b>{money(value)}</b></div>'
        left = value
        for label, v in steps:
            left -= v
            rows += f'<div class="wf-row"><span>{label}</span><i class="bar dn" style="--w:{pct(v):.1f}%; --o:{pct(left):.1f}%"></i><b>{money(-v)}</b></div>'
        rows += f'<div class="wf-row total"><span>Residual land value</span><i class="bar rl" style="--w:{pct(residual):.1f}%"></i><b>{money(residual)}</b></div>'
        if r.get("asking"):
            rows += f'<div class="wf-row"><span>Asking price</span><i class="bar" style="--w:{pct(r["asking"]):.1f}%"></i><b>{money(r["asking"])}</b></div>'
    vals = {
        "title": esc(c["title"]),
        "address_short": esc(c["address_short"]),
        "agent_name": esc(a.get("name", "you")),
        "agent_company_sep": esc(" · " + a["company"]) if a.get("company") else "",
        "headline_html": emph(c["headline"]),
        "facts_html": "".join(f"<span>{esc(f)}</span>" for f in c["facts"]),
        "note": esc(c["note"]),
        "use": esc(c["use"]),
        "numbers_html": nums,
        "plan_heading_html": emph(c["plan_heading"]),
        "plan_text": esc(c["plan_text"]),
        "payment_url": esc(payment_url),
        "rlv_rows_html": rows,
        "rlv_footnote": esc(c.get("rlv", {}).get("note", "Preliminary estimate. The full package shows every input behind it.")),
        "og_image": esc(PAGES + slug + "/img/render.jpg"),
        "render_w": str(rw), "render_h": str(rh), "plan_w": str(pw), "plan_h": str(ph),
    }
    page = (ROOT / "tools" / "preview_template.html").read_text()
    page = re.sub(r"\{\{(\w+)\}\}", lambda m: vals[m.group(1)], page)
    if not rows:   # no residual figures (or none that support the listing): leave the investor-math section out, keep everything else identical
        page = re.sub(r'\s*<section class="rlv".*?</section>', "", page, count=1, flags=re.S)
    (out / "index.html").write_text(page)
    print(PAGES + slug + "/")


if __name__ == "__main__":
    build(sys.argv[1])
