---
name: stickman-stickers
description: Categorized, commercially safe transparent 2D sticker library for Stickman Hybrid documentaries and Shorts. Implements a 3-Tier Sticker Lookup & Compounding Vault: Tier 1 Google Flow Vault (flow_vault/) auto-harvested across every project, Tier 2 100% CC0 / Public Domain 2D vector & editorial stickers (cc0_library/) across 6 categories, and Tier 3 live Google Flow fallback that automatically cleans alpha, validates halos, and saves back into flow_vault/.
---

# Stickman Stickers Library (`skills/stickman-stickers`)

Reusable, halo-free transparent 2D PNG sticker library modeled after `vox-doc-sound/`. Every sticker in `CATALOG.tsv` is validated for genuine RGBA transparency (`alpha.min() == 0`), clean non-empty foreground framing, and 100% monetization clearance.

```text
skills/stickman-stickers/
├── SKILL.md                      # Standards, tiered lookup, & monetization clearance
├── CATALOG.tsv                   # Master searchable index (path, category, source, license, tags, alpha_ok, dims)
├── scripts/
│   ├── index_stickers.py         # Validates alpha/dims/tags & rebuilds CATALOG.tsv + search API
│   ├── harvest_project_stickers.py # Deduplicates & harvests clean Flow stickers from ~/StickmanHybrid/*
│   └── fetch_cc0_stickers.py     # Populates & normalizes 100% CC0 2D vector props & editorial accents
└── assets/
    ├── flow_vault/               # Tier 1: Auto-growing vault of owned Google Flow 2D cartoon stickers
    └── cc0_library/              # Tier 2: Categorized 100% CC0 / Public Domain fallback library
        ├── history_ancient/
        ├── science_space/
        ├── nature_animals/
        ├── money_economy/
        ├── modern_daily/
        └── editorial_accents/
```

## 3-Tier Sticker Resolution Order

When any project requests a sticker prop (`flow_smart_generator.py`, `validate_pipeline.py`, `render_pro.py`, `asset_registry.py`):

1. **Tier 0 — Project Local & Sibling (`short/` <-> `long/`):**
   Checks `elements/cut/` in the current directory and sibling format directory first.
2. **Tier 1 — Owned Google Flow Vault (`assets/flow_vault/`):**
   Searches `CATALOG.tsv` for matching semantic domain + token + trigram scores (`source == flow_vault`, `alpha_ok == True`). Highest visual consistency with 2D stickman Flow art; reuses instantly in 0 seconds instead of calling Google Flow again.
3. **Tier 2 — 100% CC0 Library (`assets/cc0_library/`):**
   If no `flow_vault/` match reaches threshold, searches categorized CC0 / Public Domain props and editorial accents (`X`, `✓`, arrows, bursts, coins, scrolls, flames, planets, etc.).
4. **Tier 3 — Live Google Flow Auto-Compounding Fallback:**
   If neither Tier 1 nor Tier 2 matches the requested subject, `flow_smart_generator.py` generates the isolated 2D sticker on `#FF00FF`, chroma-keys + erodes alpha fringe via `key.py` / `cutout.py`, copies it into the project, and **automatically registers it into `assets/flow_vault/` + `CATALOG.tsv`** so future videos compound forever.

## Monetization & Quality Rules

- **Strict License Purity:** Only `Owned-Flow` (`flow_vault/`) and `CC0-1.0` / `Public domain` (`cc0_library/`) assets are allowed. Never ingest `CC-BY-SA`, `NC`, or watermarked stock imagery.
- **Alpha & Halo Requirement:** Every cataloged PNG must be `RGBA` with `alpha.min() == 0`, opaque coverage between `2%` and `90%`, and zero white/magenta background fringe.
- **Multi-Sticker & Director Choreography Compatibility:** All cataloged stickers are normalized cleanly for Director-supervised motion (`director_supervisor.py` -> `DIRECTOR_PLAN.json`), supporting 6 context-aware physics entries (`drop_weight`, `peel_reveal`, `bloom_focus`, `swing_strike`, `slide_arc_left`/`right`), collision-free multi-sticker formations (`duo_converge`, `cause_effect` with animated arrows, `trio_cascade`, `quad_showcase`), and archetype cards (`card_stat`, `split_compare`, `bar_timeline`).

## CLI Quick Reference

```bash
# Search catalog from terminal or studio.py
python3 skills/stickman-stickers/scripts/index_stickers.py --search "bronze sword"
python3 studio.py stickers --search "bronze sword"

# Harvest & deduplicate clean Flow stickers from ~/StickmanHybrid/*
python3 skills/stickman-stickers/scripts/harvest_project_stickers.py
python3 studio.py stickers --harvest

# Populate / refresh 100% CC0 library & editorial accents
python3 skills/stickman-stickers/scripts/fetch_cc0_stickers.py
python3 studio.py stickers --fetch-cc0

# Rebuild CATALOG.tsv index
python3 skills/stickman-stickers/scripts/index_stickers.py
python3 studio.py stickers --index
```
