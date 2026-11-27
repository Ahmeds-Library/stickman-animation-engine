#!/usr/bin/env python3
"""index_stickers.py: Validates sticker PNG alpha/dimensions, builds tags, writes CATALOG.tsv, and provides tiered search."""

import os
import re
import csv
import sys
import json
import shutil
import argparse
import numpy as np
from PIL import Image

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
FLOW_VAULT_DIR = os.path.join(ASSETS_DIR, "flow_vault")
CC0_LIB_DIR = os.path.join(ASSETS_DIR, "cc0_library")
CATALOG_PATH = os.path.join(SKILL_DIR, "CATALOG.tsv")

CATEGORIES = (
    "history_ancient",
    "science_space",
    "nature_animals",
    "money_economy",
    "modern_daily",
    "editorial_accents",
)

CATEGORY_KEYWORDS = {
    "history_ancient": {
        "sword", "shield", "helmet", "scroll", "tablet", "cuneiform", "column", "ruin", "pillar",
        "warship", "prow", "roman", "soldier", "groma", "milestone", "trench", "basalt", "flint",
        "spear", "crown", "ancient", "fossil", "chariot", "catapult", "empire", "bronze", "stone", "blade",
    },
    "science_space": {
        "dna", "helix", "atom", "orbit", "planet", "saturn", "globe", "earth", "volcano", "thermometer",
        "freeze", "rocket", "brain", "beaker", "flask", "microscope", "telescope", "neuron", "cell",
    },
    "nature_animals": {
        "tree", "fire", "flame", "torch", "spark", "lightning", "bolt", "water", "droplet", "snow",
        "gorilla", "skull", "sabertooth", "cat", "wheat", "grain", "seashell", "mussel", "ash", "cloud",
        "mountain", "leaf", "animal", "camp", "campfire",
    },
    "money_economy": {
        "coin", "gold", "tin", "ingot", "metal", "chart", "trend", "scale", "balance", "clock", "gear",
        "map", "compass", "trade", "price", "dollar", "clipboard", "graph", "money",
    },
    "modern_daily": {
        "alarm", "bulb", "lightbulb", "phone", "car", "house", "book", "coffee", "bed", "mattress",
        "flute", "badge", "channel", "megaphone", "microphone", "camera", "magnifying",
        "soda", "cola", "pop", "fizzy", "can", "drink", "beverage", "sugar",
    },
    "editorial_accents": {
        "arrow", "cross", "check", "checkmark", "burst", "star", "bubble", "speech", "warning",
        "triangle", "circle", "ring", "highlight", "stamp", "badge", "swoosh", "line", "accent",
    },
}

STOP_WORDS = {
    "a", "an", "the", "with", "and", "in", "of", "to", "for", "on", "by", "or", "is", "are",
    "one", "single", "isolated", "2d", "cartoon", "style", "clean", "dark", "ink", "outlines",
    "outline", "flat", "color", "colors", "solid", "pure", "magenta", "background", "ff00ff",
    "no", "shadows", "shadow", "clutter", "text", "sticker", "prop", "png",
}

SYNONYMS = {
    "sword": {"blade", "weapon", "gladius", "knife", "dagger"},
    "spear": {"lance", "javelin", "pike", "harpoon", "flint"},
    "shield": {"buckler", "scutum", "armor", "defense"},
    "helmet": {"galea", "helm", "headgear", "warrior"},
    "scroll": {"tablet", "document", "archive", "record", "parchment", "cuneiform"},
    "fire": {"flame", "torch", "campfire", "blaze", "ember", "ash"},
    "grain": {"wheat", "crop", "harvest", "food", "famine", "drought"},
    "ship": {"warship", "prow", "boat", "galley", "fleet", "vessel"},
    "ruin": {"column", "pillar", "temple", "stone", "wreck", "collapse"},
    "coin": {"currency", "money", "wealth"},
    "ingot": {"tin", "copper", "bronze", "ore", "smelt"},
    "skull": {"fossil", "bone", "skeleton", "sabertooth"},
    "thermometer": {"cold", "freeze", "ice", "temperature", "frost"},
    "dna": {"helix", "gene", "genetic", "genome"},
    "arrow": {"pointer", "direction", "vector", "curved"},
    "check": {"checkmark", "verified", "confirm"},
    "cross": {"x", "myth", "false", "wrong", "reject", "stop"},
    "soda": {"cola", "fizzy", "softdrink", "beverage"},
}

ALCOHOL_TOKENS = {"wine", "beer", "champagne", "ale", "liquor", "whiskey", "vodka"}
SODA_SPECIFIC_TOKENS = {"soda", "cola", "pop", "fizzy", "softdrink", "sprite", "coke", "pepsi"}
KNOWN_MINI_SCENE_SLUGS = {
    "skull_fossil",
    "scientific_field_researcher",
    "tribal_storytelling_pie",
    "campfire_circle",
}


def is_mini_scene_prop(png_path, name_or_tags=""):
    """Detects multi-character / multi-island mini-scene cutouts unsuitable for compact circular props."""
    base = os.path.splitext(os.path.basename(str(png_path or "")))[0].lower()
    if base in KNOWN_MINI_SCENE_SLUGS:
        return True
    txt = f"{base} {name_or_tags}".lower()
    if any(w in txt for w in ("stickman", "stickmen", "researcher", "excavat", "storytelling")):
        return True
    return False


def tokenize_text(txt):
    toks = [w.strip("_") for w in re.split(r"[^a-z0-9]+", str(txt or "").lower()) if len(w.strip("_")) >= 2]
    out = []
    for t in toks:
        if t in STOP_WORDS:
            continue
        if len(t) > 4 and t.endswith("s") and not t.endswith("ss"):
            out.append(t[:-1])
        out.append(t)
    return list(dict.fromkeys(out))


def expand_tags(tokens):
    exp = set(tokens)
    for t in list(tokens):
        for root, syns in SYNONYMS.items():
            if t == root or t in syns:
                exp.add(root)
                exp.update(syns)
    return sorted(exp)


def infer_category(name_and_tags):
    toks = set(tokenize_text(name_and_tags))
    best_cat = "history_ancient"
    best_hits = 0
    for cat, kws in CATEGORY_KEYWORDS.items():
        hits = len(toks & kws)
        if hits > best_hits:
            best_hits = hits
            best_cat = cat
    return best_cat


def inspect_png_alpha(png_path):
    """Verifies true RGBA transparency, non-empty subject, and low opaque border ratio."""
    try:
        with Image.open(png_path) as im_raw:
            w, h = im_raw.size
            if w < 48 or h < 48:
                return False, f"{w}x{h}", "too_small"
            im = im_raw.convert("RGBA") if png_path.lower().endswith((".webp", ".gif")) else im_raw
            if im.mode != "RGBA":
                return False, f"{w}x{h}", f"mode_{im.mode}"
            arr = np.array(im)
            a = arr[:, :, 3]
            if int(a.min()) > 10:
                return False, f"{w}x{h}", "no_transparency"
            opaque_ratio = float((a > 200).mean())
            if opaque_ratio < 0.015:
                return False, f"{w}x{h}", "nearly_empty"
            if opaque_ratio > 0.94:
                return False, f"{w}x{h}", "almost_opaque_square"
            # Check outer 4px rim opaque fraction (catch unkeyed rectangular borders)
            rim = np.concatenate([a[:4, :].ravel(), a[-4:, :].ravel(), a[:, :4].ravel(), a[:, -4:].ravel()])
            rim_opaque = float((rim > 200).mean())
            if rim_opaque > 0.25:
                return False, f"{w}x{h}", f"edge_clip_or_unkeyed_{rim_opaque:.2f}"
            return True, f"{w}x{h}", "ok"
    except Exception as e:
        return False, "0x0", str(e)


def _sidecar_tags(png_path):
    meta_p = os.path.splitext(png_path)[0] + ".meta.json"
    if os.path.exists(meta_p):
        try:
            with open(meta_p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def rebuild_catalog(skill_dir=None):
    sdir = skill_dir or SKILL_DIR
    fvault = os.path.join(sdir, "assets", "flow_vault")
    cc0dir = os.path.join(sdir, "assets", "cc0_library")
    cat_path = os.path.join(sdir, "CATALOG.tsv")
    os.makedirs(fvault, exist_ok=True)
    for c in CATEGORIES:
        os.makedirs(os.path.join(cc0dir, c), exist_ok=True)

    rows = []

    # 1. Scan Tier 1: flow_vault (Owned-Flow)
    for root, _, files in os.walk(fvault):
        for fn in sorted(files):
            if not fn.lower().endswith((".png", ".webp", ".gif")):
                continue
            fp = os.path.join(root, fn)
            meta = _sidecar_tags(fp)
            base = os.path.splitext(fn)[0]
            raw_tags = meta.get("tags", "")
            toks = tokenize_text(f"{base} {raw_tags}")
            cat = meta.get("category") or infer_category(f"{base} {raw_tags}")
            alpha_ok, dims, _ = inspect_png_alpha(fp)
            rel_p = os.path.relpath(fp, sdir).replace(os.sep, "/")
            rows.append({
                "path": rel_p,
                "category": cat,
                "source": "flow_vault",
                "license": meta.get("license", "Owned-Flow"),
                "tags": ", ".join(expand_tags(toks)),
                "alpha_ok": "True" if alpha_ok else "False",
                "dims": dims,
                "origin": meta.get("origin", "Google Flow"),
            })

    # 2. Scan Tier 2: cc0_library/<category> (CC0-1.0 / Public Domain / MIT)
    for cat in CATEGORIES:
        cdir = os.path.join(cc0dir, cat)
        if not os.path.isdir(cdir):
            continue
        for fn in sorted(os.listdir(cdir)):
            if not fn.lower().endswith((".png", ".webp", ".gif")):
                continue
            fp = os.path.join(cdir, fn)
            meta = _sidecar_tags(fp)
            base = os.path.splitext(fn)[0]
            raw_tags = meta.get("tags", "")
            toks = tokenize_text(f"{base} {raw_tags}")
            alpha_ok, dims, _ = inspect_png_alpha(fp)
            rel_p = os.path.relpath(fp, sdir).replace(os.sep, "/")
            rows.append({
                "path": rel_p,
                "category": cat,
                "source": "cc0_library",
                "license": meta.get("license", "CC0-1.0"),
                "tags": ", ".join(expand_tags(toks)),
                "alpha_ok": "True" if alpha_ok else "False",
                "dims": dims,
                "origin": meta.get("origin", "CC0-1.0 Local/Open"),
            })

    with open(cat_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["path", "category", "source", "license", "tags", "alpha_ok", "dims", "origin"],
            delimiter="\t",
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return rows


def _trigram_cos(a, b):
    a_s = f"  {a.lower()}  "
    b_s = f"  {b.lower()}  "
    ta = {a_s[i:i+3] for i in range(max(0, len(a_s) - 2))}
    tb = {b_s[i:i+3] for i in range(max(0, len(b_s) - 2))}
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / ((len(ta) * len(tb)) ** 0.5)


def search_stickers(query, min_score=0.35, require_alpha_ok=True, single_object_only=False, skill_dir=None):
    """Searches CATALOG.tsv prioritizing Tier 1 flow_vault over Tier 2 cc0_library."""
    sdir = skill_dir or SKILL_DIR
    cat_path = os.path.join(sdir, "CATALOG.tsv")
    if not os.path.exists(cat_path):
        rebuild_catalog(sdir)
    if not os.path.exists(cat_path):
        return []

    q_toks = set(tokenize_text(query))
    q_exp = set(expand_tags(q_toks))
    if not q_toks:
        return []

    wants_alcohol = bool(q_toks & ALCOHOL_TOKENS)
    wants_soda = bool(q_toks & SODA_SPECIFIC_TOKENS)

    matches = []
    with open(cat_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if require_alpha_ok and row.get("alpha_ok") != "True":
                continue
            rel_p = row.get("path", "")
            abs_p = os.path.join(sdir, rel_p)
            if not os.path.exists(abs_p):
                continue

            base = os.path.splitext(os.path.basename(rel_p))[0]
            if single_object_only and is_mini_scene_prop(abs_p, row.get("tags", "")):
                continue

            c_toks = set(tokenize_text(f"{base} {row.get('tags', '')}"))
            c_exp = set(expand_tags(c_toks))
            if not c_toks:
                continue

            # Never pick alcohol (e.g. wine bottle) for soda/coffee/soft-drink/water queries
            if not wants_alcohol and (c_toks & ALCOHOL_TOKENS):
                continue
            # If user asked specifically for soda/cola, require concrete soda/can/fizzy token match
            if wants_soda and not (c_toks & (SODA_SPECIFIC_TOKENS | {"can", "beverage"})):
                continue

            direct_hits = len(q_toks & c_toks)
            exp_hits = len(q_exp & c_exp)
            jacc = exp_hits / max(1, len(q_exp | c_exp))
            trig = _trigram_cos(query, base.replace("_", " "))

            if direct_hits == 0 and exp_hits == 0 and trig < 0.65:
                continue

            score = (0.45 * (direct_hits / max(1, len(q_toks)))) + (0.35 * jacc) + (0.20 * trig)
            if row.get("source") == "flow_vault":
                score += 0.25  # Tier 1 Google Flow style priority

            if score >= min_score:
                matches.append({
                    "path": abs_p,
                    "rel_path": rel_p,
                    "name": base,
                    "category": row.get("category", ""),
                    "source": row.get("source", ""),
                    "license": row.get("license", ""),
                    "dims": row.get("dims", ""),
                    "score": round(score, 4),
                })

    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches


def register_flow_sticker(src_png, slug_name, tags="", category=None, skill_dir=None):
    """Auto-ingests a newly created transparent Flow cutout into Tier 1 flow_vault and rebuilds CATALOG.tsv."""
    sdir = skill_dir or SKILL_DIR
    fvault = os.path.join(sdir, "assets", "flow_vault")
    os.makedirs(fvault, exist_ok=True)
    ok, _, reason = inspect_png_alpha(src_png)
    if not ok:
        return None

    clean_slug = re.sub(r"[^a-z0-9_]+", "_", str(slug_name or "sticker").lower()).strip("_") or "sticker"
    dst_png = os.path.join(fvault, f"{clean_slug}.png")
    shutil.copy2(src_png, dst_png)
    meta_p = os.path.join(fvault, f"{clean_slug}.meta.json")
    with open(meta_p, "w", encoding="utf-8") as mf:
        json.dump({
            "tags": tags or clean_slug.replace("_", " "),
            "category": category or infer_category(f"{clean_slug} {tags}"),
            "source": "flow_vault",
            "license": "Owned-Flow",
        }, mf, indent=2)
    rebuild_catalog(sdir)
    return dst_png


def main():
    parser = argparse.ArgumentParser(description="Stickman Stickers Catalog Indexer & Search")
    parser.add_argument("--search", "-s", default=None, help="Search stickers by concept or keyword")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.search:
        res = search_stickers(args.search)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Search '{args.search}' -> {len(res)} match(es):")
            for r in res[:10]:
                print(f"  [{r['source']}] {r['name']} ({r['category']}, {r['dims']}, score={r['score']}) -> {r['rel_path']}")
    else:
        rows = rebuild_catalog()
        fv = sum(1 for r in rows if r["source"] == "flow_vault")
        cc = sum(1 for r in rows if r["source"] == "cc0_library")
        ok_n = sum(1 for r in rows if r["alpha_ok"] == "True")
        print(f"Rebuilt CATALOG.tsv: {len(rows)} stickers ({fv} flow_vault, {cc} cc0_library, {ok_n} alpha_ok=True) -> {CATALOG_PATH}")


if __name__ == "__main__":
    main()
