# Forma warm-lead preview pages

One page per targeted listing, sent by email to a listing agent I haven't talked to yet.
Every page is identical in layout and copy structure; only the property content changes.
The page is a teaser for the $949 package. It is **not** the scrollytelling property
website (that's the $1,000 add-on at /model).

Live example: https://rchase-sudo.github.io/model/p/pocahontas/

## What's in the repo (rchase-sudo/model, GitHub Pages from `main`)

| Path | What it is |
|---|---|
| `tools/preview_template.html` | The page. Every `{{placeholder}}` is filled by the generator. Don't edit per lead. |
| `tools/make_preview.py` | Generator: config JSON + two images -> `p/<slug>/index.html` + `p/<slug>/img/`. |
| `tools/watermark.py` | Bakes the FORMA · PREVIEW · NOT FOR MARKETING watermark + corner badge into images. |
| `tools/leads/<slug>.json` | Per-lead config. **Git-ignored** (contains agent contact info). Keep locally. |
| `p/<slug>/` | Generated, committed output. Live at `https://rchase-sudo.github.io/model/p/<slug>/`. |

Requirements: Python 3 + Pillow, and the Inter fonts at `/usr/share/fonts/opentype/inter/`
(used by `watermark.py`; change `FONT_BOLD` / `FONT_MED` if your machine has them elsewhere).
`pdftoppm` (poppler) if the plan comes as a PDF.

## Page structure (fixed, top to bottom)

1. Sticky bar: FORMA mark · "Preliminary preview" · "Call (978) 346-5818" (desktop) · **Order the package** button.
2. Hero: "Prepared for {agent} · {brokerage}", headline, fact chips, a short first-person note signed "Ryan Chase, Forma Designs".
3. The rendering, full width, watermarked.
4. Three teaser numbers.
5. Concept plan (watermarked) with a heading and one paragraph.
6. **The investor math** (residual land value): waterfall of completed value − hard costs − soft costs/financing − developer profit = residual land value, plus asking price, and a footnote.
7. Offer box: $949 per listing, two CTAs: **Order the full package** (prefilled checkout) and **Call me · (978) 346-5818**, then "nothing charged today / $159/mo", the 6-month guarantee, support email.
8. One line upsell: interactive property website -> https://formadesigns.io/model
9. Footer disclaimer (preliminary, not engineered, not for marketing until purchased).

The page is `noindex`, the images can't be right-clicked or dragged, and the watermark is in the image files themselves.

## Inputs you need per lead

1. **Rendering** (jpg/png, the photoreal render from the pipeline).
2. **Concept plan**: the actual concept plan I created (usually the F1 "Preliminary Development Plan" sheet PDF). Never substitute a drawing you made yourself.
3. Listing facts: address, town/state/county, acres, zoning, frontage, notable distances, asking price, program (uses, SF, parking, access), buildable/wetland acreage if known.
4. Agent: name, brokerage, email, phone (from the CRM `contacts` table or the listing).
5. Residual land value figures from the pro forma: completed value, hard costs, soft costs + financing, developer profit. Residual is calculated by the generator. Only use made-up figures if I explicitly say so, and then keep the "Illustrative figures" footnote.

### Preparing the concept plan from the PDF

Render at 200 dpi and crop off the title block on the right so only the drawing remains:

```bash
pdftoppm -r 200 -png "F1.pdf" plan
python3 - <<'EOF'
from PIL import Image
im = Image.open("plan-1.png"); W, H = im.size
# 24x36 sheet with the title block on the right: keep the drawing frame
im.crop((int(W*0.033), int(H*0.03), int(W*0.882), int(H*0.968))).convert("RGB").save("concept_crop.jpg", quality=93)
EOF
```

Look at the crop before using it; adjust the fractions if the sheet layout differs. Keep the small map attribution text.

## Config file: `tools/leads/<slug>.json`

`slug` is short, lowercase, hyphenated (`pocahontas`, `80-elm-st`). Text fields are plain text; `*word*`
marks the gold emphasis in `headline` and `plan_heading`; `<b>…</b>` is allowed only at the start of a number label.

```json
{
  "slug": "pocahontas",
  "title": "Lot 6 Pocahontas Trail",
  "address_short": "Lot 6 Pocahontas Trail",
  "address_full": "Lot 6 Pocahontas Trail, Quinton, VA",
  "agent": { "name": "Patricia Worth", "company": "BayFox Designs", "email": "agent@example.com", "phone": "(804) 555-0100" },
  "headline": "Lot 6 Pocahontas Trail, *built out.*",
  "facts": ["Quinton, VA · New Kent County", "15.01 ac", "Zoned B-1", "±590 ft on US 60", "2.5 mi to I-64"],
  "note": "I took a first pass at what a buyer could build on your listing: a two-bay car wash and a laundromat on the upland along US 60, with the wetlands left alone. Here's a preview of the plan and rendering.",
  "use": "car wash and laundromat",
  "numbers": [
    { "value": "±8 ac", "label": "<b>Buildable upland</b> out of 15.01 acres. The ±7.6 ac of mapped wetland stays untouched." },
    { "value": "8,225 SF", "label": "<b>Car wash + laundromat</b>, 28 parking spaces and one US 60 entrance.", "gold": true },
    { "value": "±6.5 ac", "label": "<b>Upland left over.</b> This project uses about 1.5 acres, leaving room for more pads." }
  ],
  "plan_heading": "Two buildings, *one entrance.*",
  "plan_text": "A two-bay car wash near the road and a laundromat behind it, both reached by a loop drive from a single US 60 entrance. The loop doubles as the car wash stacking lane, so queued cars wait on site.",
  "rlv": {
    "value": 4350000, "hard": 2140000, "soft": 495000, "profit": 405000, "asking": 1250000,
    "note": "Preliminary estimate. The full package shows every input behind it."
  },
  "images": {
    "render": "/path/to/render.jpg",
    "plan": "/path/to/concept_crop.jpg",
    "plan_dark": false
  }
}
```

- `plan_dark`: `false` for plans on a dark aerial (white watermark), `true` for plans on a light/paper background (dark watermark).
- `rlv.note`: use "Preliminary estimate. The full package shows every input behind it." for real figures; "Illustrative figures for this preview. The full package shows every input behind them." for made-up ones.
- `rlv` is optional; without it the waterfall has no rows, so always include it.

## Copy rules

- First person singular, always "I", never "we" (Forma is presented as one person). Sign the note as Ryan Chase.
- `headline`: "{Address}, *built out.*" unless there's a better property-specific line.
- `note`: 1–2 sentences, what I planned and why it fits this lot, ending with "Here's a preview of the plan and rendering."
- `facts`: 4–6 short chips: town/county, acres, zoning, frontage, a location hook.
- `numbers`: exactly 3. One about the land (buildable area / lot count / yield), one about the program (gold), one about upside (room left, extra pads, units). Use only figures that come from the plan, listing or package.
- `plan_heading` + `plan_text`: describe the layout in plain words (access, circulation, why it works).
- Never state the project will sell, or that the land does or doesn't pencil, beyond what the RLV figures show.

## Build, check, publish

```bash
cd model
python3 tools/make_preview.py tools/leads/<slug>.json   # prints the live URL
```

Check before pushing (open `p/<slug>/index.html` in a browser or headless Chromium at 1440 px and 390 px):
- No horizontal scroll at 390 px.
- Both images show the watermark; the plan is the real concept plan.
- Every "Order" link goes to `https://formadesigns.io/payment?address=…&name=…&email=…&phone=…#order`
  (URL-encoded full address; the generator builds it from `address_full` and `agent`).
- The waterfall math reads correctly and the footnote matches whether figures are real or illustrative.

Publish:

```bash
git add p/<slug>
git commit -m "Preview page: <address>"
git push origin HEAD:main      # GitHub Pages serves it within ~1 minute
```

Optional CRM step: store the page URL on the agent's contact (`contacts.website_url`) and log a touch
(`touches`: type `email`, note "Sent preview page <url>").

## Sending it

Email the agent the link (https://rchase-sudo.github.io/model/p/<slug>/). Pasting it into most email
clients shows the rendering as the preview image. To put a page on formadesigns.io instead, add a Framer
page with an iframe code component (must `export default` the component) pointing at the GitHub URL,
width Fill, height 100vh.

## Don't

- Don't edit `preview_template.html` for one lead; if the standard changes, change the template and rebuild every page.
- Don't commit `tools/leads/*.json` (agent contact info; the repo is public).
- Don't use the full scrollytelling property website here or add more sections; keep pages identical.
- Don't remove the watermark or ship clean images on a preview page.

## Automatic pages from Drafted (lite jobs)

Every lite Drafted job ends by building its own preview page with this same template (fetched from `main` at build time, so template edits apply to
all future pages). The worker uploads `p/<slug>/` to the public Supabase bucket `previews`; `.github/workflows/sync_previews.yml` runs every 5 minutes
(`tools/sync_previews.py`), copies new or changed pages into `p/` and pushes. Hand-built pages are never touched.

- Page goes live at `https://rchase-sudo.github.io/model/p/<slug>/`; Drafted stores it in the job `summary.preview` (`url`, `display`, `email_html`).
- In email, show the clean address and link to GitHub: `<a href="https://rchase-sudo.github.io/model/p/<slug>/">formadesigns.io/p/<slug></a>`.
- Pages are only built when the residual land value is positive and at least the asking price (otherwise `summary.preview.status = "held"`).
