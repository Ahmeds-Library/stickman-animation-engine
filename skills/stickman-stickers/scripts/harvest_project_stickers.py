#!/usr/bin/env python3
"""harvest_project_stickers.py: Harvests, validates, and deduplicates transparent Google Flow stickers from ~/StickmanHybrid/* into Tier 1 flow_vault."""

import os
import re
import csv
import sys
import json
import hashlib
import shutil
import argparse
import numpy as np
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
import index_stickers


def _load_elements_map(proj_root):
    """Maps sticker id -> object description across project ELEMENTS.tsv files."""
    mapping = {}
    for rel in ("ELEMENTS.tsv", os.path.join("short", "ELEMENTS.tsv"), os.path.join("long", "ELEMENTS.tsv")):
        ep = os.path.join(proj_root, rel)
        if os.path.exists(ep):
            try:
                with open(ep, "r", encoding="utf-8", errors="ignore") as f:
                    for row in csv.DictReader(f, delimiter="\t"):
                        eid = (row.get("id") or "").strip()
                        obj = (row.get("object") or "").strip()
                        if eid and obj:
                            mapping[eid] = obj
            except Exception:
                pass
    return mapping


def _semantic_slug(eid, obj_desc):
    base = re.sub(r"[^a-z0-9_]+", "_", eid.lower()).strip("_")
    # Replace generic numeric ids like 01, 02 with concise descriptive slug from ELEMENTS.tsv
    if (not base or base.isdigit() or re.match(r"^(?:stk|el|s)?\d+$", base)) and obj_desc:
        toks = index_stickers.tokenize_text(obj_desc)
        if toks:
            return "_".join(toks[:3])
    return base or "flow_sticker"


def _visual_hash(png_path):
    """Perceptual 16x16 alpha+luma signature to deduplicate near-identical cutouts."""
    with Image.open(png_path) as im:
        im_s = im.convert("RGBA").resize((16, 16), Image.LANCZOS)
        arr = np.array(im_s, dtype=np.uint8)
        # Quantize slightly so minor re-keying passes deduplicate cleanly
        q = (arr // 16).tobytes()
        return hashlib.sha256(q).hexdigest()[:16]


def harvest_all(hybrid_root=None, dry_run=False):
    hroot = os.path.expanduser(hybrid_root or "~/StickmanHybrid")
    fvault = index_stickers.FLOW_VAULT_DIR
    os.makedirs(fvault, exist_ok=True)

    seen_hashes = set()
    # Pre-seed hashes of existing vault items
    for fn in sorted(os.listdir(fvault)):
        if fn.lower().endswith(".png"):
            fp = os.path.join(fvault, fn)
            try:
                seen_hashes.add(_visual_hash(fp))
            except Exception:
                pass

    added = 0
    skipped_dup = 0
    skipped_bad = 0

    if not os.path.isdir(hroot):
        print(f"No StickmanHybrid workspace at {hroot}")
        return 0, 0, 0

    for proj_name in sorted(os.listdir(hroot)):
        proj_root = os.path.join(hroot, proj_name)
        if not os.path.isdir(proj_root):
            continue
        el_map = _load_elements_map(proj_root)

        cut_dirs = [
            os.path.join(proj_root, "elements", "cut"),
            os.path.join(proj_root, "short", "elements", "cut"),
            os.path.join(proj_root, "long", "elements", "cut"),
        ]
        for cdir in cut_dirs:
            if not os.path.isdir(cdir):
                continue
            for fn in sorted(os.listdir(cdir)):
                if not fn.lower().endswith(".png"):
                    continue
                src_p = os.path.join(cdir, fn)
                eid = os.path.splitext(fn)[0]
                ok, dims, reason = index_stickers.inspect_png_alpha(src_p)
                if not ok:
                    skipped_bad += 1
                    continue

                vh = _visual_hash(src_p)
                if vh in seen_hashes:
                    skipped_dup += 1
                    continue

                obj_desc = el_map.get(eid, eid.replace("_", " "))
                slug = _semantic_slug(eid, obj_desc)
                # Resolve slug collision if different artwork happens to share slug
                dst_p = os.path.join(fvault, f"{slug}.png")
                if os.path.exists(dst_p):
                    dst_p = os.path.join(fvault, f"{slug}_{proj_name}.png")
                    slug = f"{slug}_{proj_name}"

                seen_hashes.add(vh)
                if not dry_run:
                    shutil.copy2(src_p, dst_p)
                    meta_p = os.path.join(fvault, f"{slug}.meta.json")
                    with open(meta_p, "w", encoding="utf-8") as mf:
                        json.dump({
                            "tags": obj_desc,
                            "origin_project": proj_name,
                            "origin_id": eid,
                            "category": index_stickers.infer_category(f"{slug} {obj_desc}"),
                            "source": "flow_vault",
                            "license": "Owned-Flow",
                        }, mf, indent=2)
                added += 1

    if not dry_run:
        rows = index_stickers.rebuild_catalog()
        print(f"Harvest complete: +{added} unique Flow stickers added to flow_vault ({skipped_dup} duplicates, {skipped_bad} invalid alpha skipped). Catalog total: {len(rows)}.")
    else:
        print(f"[Dry-Run] Would add +{added} Flow stickers ({skipped_dup} duplicates, {skipped_bad} invalid alpha skipped).")
    return added, skipped_dup, skipped_bad


def main():
    parser = argparse.ArgumentParser(description="Harvest clean Google Flow stickers from ~/StickmanHybrid/* into Tier 1 flow_vault")
    parser.add_argument("--root", default="~/StickmanHybrid", help="StickmanHybrid projects directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview harvest without copying files")
    args = parser.parse_args()
    harvest_all(args.root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
