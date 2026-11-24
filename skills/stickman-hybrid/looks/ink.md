# ink

**When:** topics full of numbers, comparisons and "this vs that": psychology, money, the
body, "what happens if", and ancient human daily life explainers. This is the look of **Ink Explainer** (19.3M views) and **Quark** (1.97M views).

**STYLE** (paste this after `look: ink`):

hand-drawn 2D stick figure explainer illustration, clean black ink outlines of even weight (6-8px felt-tip pen stroke, #1A1A1A), warm vintage cream paper tone backdrop (#F7E8C0 to #ECD6B4 with subtle paper fiber texture and soft radial vignette), flat colour fills limited to clear focal accents (amber yellow, soft crimson, sky blue, skin beige), generous negative breathing space, 16:9 widescreen or 9:16 vertical. The protagonist is a classic minimalist stickman: perfectly round white head outlined in ink, expressive black dot eyes, thin black stick limbs, dynamic body gesture. Full-bleed background with simple architectural or landscape silhouettes.

**Palette & Canvas Tokens:**
- Backdrop Canvas: Vintage Cream `#F7E8C0` / Off-White Parchment `#ECD6B4`
- Primary Ink Stroke: Charcoal Ink `#1A1A1A` (6–8px weight)
- Character Head Fill: Opaque Pure White `#FFFFFF`
- Focal Accent Colors: Warning Crimson `#E63946`, Information Amber `#F4A261`, Sky Blue `#457B9D`

**Character sheet:**
- A classic stickman for "you": round plain white head, dot eyes, no clothes.
- One or two story characters, each with a single identifying feature, such as hair and a
  tunic, a hat, glasses, or stone-age tools.

**Notes:**
- Plain stark white backgrounds read as empty and digital. Always specify warm vintage paper grain backdrop.
- For props (clocks, phones, tools), keep them simplified 2D flat-vector cutouts with bold black outlines so they "pop" forward when audio J-cuts fire.
- If the reference is a combined sheet, Flow sometimes pastes the sheet's own line-up into
  the scene. Always split the sheet into one reference per character with
  `pictures.py refs`.

**The Plain Paper Palate Cleanser Standard (Rule 61):**
- In **Ink Explainer**, do NOT use lower-third title banners or digital cards.
- Instead, every 45–75 seconds, cut to a **Plain Off-White Paper Page** (`#FAF8F2`) featuring only a single bold felt-pen statement (e.g., *"WHAT SHOULD I DO TODAY?"*, *"1963 — RICHARD LEE"*, *"40,000 HOURS OF YOUR LIFE — WORKING"*).
- Accompany with an expressive reaction stickman in the corner (`shock`, `think`, or `point`) to anchor audience empathy and retention.
- Generate directly via:
  `python3 studio.py page "STATEMENT" --subtitle "CONTEXT" --pose think`
