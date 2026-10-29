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
        "og_image": esc(PAGES + slug + "/img/render.jpg"),
        "render_w": str(rw), "render_h": str(rh), "plan_w": str(pw), "plan_h": str(ph),
    }
    page = (ROOT / "tools" / "preview_template.html").read_text()
    page = re.sub(r"\{\{(\w+)\}\}", lambda m: vals[m.group(1)], page)
    (out / "index.html").write_text(page)
    print(PAGES + slug + "/")


if __name__ == "__main__":
    build(sys.argv[1])
