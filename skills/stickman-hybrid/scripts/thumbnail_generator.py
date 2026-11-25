#!/usr/bin/env python3
"""thumbnail_generator.py: Stage 2 Intelligent Post-Flow Composition & CTR Polish Engine
Refines raw thumbnail artwork (from Google Flow or high-contrast candidates) into broadcast-quality,
high-clickthrough-rate thumbnails for YouTube 16:9 and Shorts 9:16.

Features:
1. Spatial Negative-Space & Safe-Zone Solver:
   - Analyzes raw artwork edge density / luminance to locate optimal negative space away from faces.
   - Enforces strict YouTube timestamp exclusion (16:9 bottom-right 18% W x 14% H).
   - Enforces Shorts mobile safe margins (avoids top header, bottom ticker, right buttons).
2. High-Impact Typography & Contrast Guard:
   - 2-4 word punchy curiosity hooks pulled from METADATA.json / viral_seo_intelligence.
   - 2x Supersampled rendering (LANCZOS downsampling) for razor-sharp vector-grade clarity.
   - Curated font hierarchy: PermanentMarker-Regular.ttf / Bangers-Regular.ttf / Caveat-Bold.ttf.
   - Auto-Contrast Guard: Measures background luminance behind text, automatically applying
     adaptive dark ink pill, heavy charcoal stroke, or deep comic drop shadows.
3. Selective Editorial Polish (3-Element Rule):
   - Element 1: High-emotion character.
   - Element 2: Visual anomaly / monumental prop.
   - Element 3: Bold 2-4 word curiosity text.
   - Look-aligned subtle vignette (warm, night, bright, oversimplified).
   - At most 1 purposeful curiosity accent (e.g. curiosity badge pill).
4. Dual Export:
   - 16:9 Landscape (1280x720) in UPLOAD_PACK/thumbnail_16x9.png
   - 9:16 Vertical (1080x1920) in UPLOAD_PACK/thumbnail_9x16.png
   - Generates STAGE2_CTR_AUDIT.json decision log.
"""

import os
import sys
import math
import json
import glob
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat, ImageOps
import numpy as np

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

SKILL_ROOT = os.path.dirname(SKILL_SCRIPTS)
FONTS_DIR = os.path.join(SKILL_ROOT, "fonts")
if not os.path.exists(FONTS_DIR):
    FONTS_DIR = "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/fonts"

PERMANENT_MARKER = os.path.join(FONTS_DIR, "PermanentMarker-Regular.ttf")
BANGERS = os.path.join(FONTS_DIR, "Bangers-Regular.ttf")
CAVEAT = os.path.join(FONTS_DIR, "Caveat-Bold.ttf")
LUCKIEST_GUY = os.path.join(FONTS_DIR, "LuckiestGuy-Regular.ttf")
MONTSERRAT = os.path.join(FONTS_DIR, "Montserrat-Black.ttf")
KALAM = os.path.join(FONTS_DIR, "Kalam-Bold.ttf")
SEDGWICK = os.path.join(FONTS_DIR, "SedgwickAve-Regular.ttf")
PATRICK = os.path.join(FONTS_DIR, "PatrickHand-Regular.ttf")

FONT_MAP = {
    "hero": PERMANENT_MARKER,
    "permanent": PERMANENT_MARKER,
    "badge": BANGERS,
    "stamp": BANGERS,
    "bangers": BANGERS,
    "sublabel": CAVEAT,
    "annotation": CAVEAT,
    "caveat": CAVEAT,
    "display": LUCKIEST_GUY,
    "luckiest": LUCKIEST_GUY,
    "modern": MONTSERRAT,
    "montserrat": MONTSERRAT,
    "sketch": KALAM,
    "kalam": KALAM,
    "title": SEDGWICK,
    "sedgwick": SEDGWICK,
    "caption": PATRICK,
    "patrick": PATRICK,
}


def get_curated_font(role="hero", size=72):
    """Loads appropriate bundled font by editorial role."""
    fpath = None
    role_key = (role or "").strip().lower()
    if os.path.exists(role_key):
        fpath = role_key
    elif role_key in FONT_MAP:
        fpath = FONT_MAP[role_key]
    elif "montserrat" in role_key or "modern" in role_key:
        fpath = MONTSERRAT
    elif "luckiest" in role_key or "display" in role_key:
        fpath = LUCKIEST_GUY
    elif "kalam" in role_key or "sketch" in role_key:
        fpath = KALAM
    elif "caveat" in role_key or "sublabel" in role_key:
        fpath = CAVEAT
    elif "bangers" in role_key or "badge" in role_key or "stamp" in role_key:
        fpath = BANGERS
    elif "sedgwick" in role_key or "title" in role_key:
        fpath = SEDGWICK
    else:
        fpath = PERMANENT_MARKER

    if fpath and os.path.exists(fpath):
        try:
            return ImageFont.truetype(fpath, size)
        except Exception:
            pass

    # Fallbacks
    for cand in [PERMANENT_MARKER, BANGERS, LUCKIEST_GUY, MONTSERRAT, KALAM, SEDGWICK]:
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, size)
            except Exception:
                pass
    return ImageFont.load_default()


def extract_hook_and_badge(project_dir=".", text_override=None, tag_override=None):
    """Pulls punchiest 2-4 word curiosity hook and badge from project metadata."""
    slug = os.path.basename(os.path.abspath(project_dir))
    slug_clean = slug.replace("_", " ").lower()

    if text_override:
        text = text_override.strip()
    else:
        # Check METADATA.json in short or long or root
        meta_candidates = [
            os.path.join(project_dir, "UPLOAD_PACK", "METADATA.json"),
            os.path.join(project_dir, "short", "METADATA.json"),
            os.path.join(project_dir, "METADATA.json"),
            os.path.join(project_dir, "long", "METADATA.json")
        ]
        text = None
        for mp in meta_candidates:
            if os.path.exists(mp):
                try:
                    with open(mp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        tb = data.get("thumbnail_blueprint", {})
                        if "element_3_high_contrast_text" in tb:
                            raw = tb["element_3_high_contrast_text"]
                            # e.g. "3 WORDS MAX: 'THE NIGHT VOID' in bold yellow..."
                            import re
                            m = re.search(r"['\"]([^'\"]+)['\"]", raw)
                            if m:
                                text = m.group(1).strip()
                                break
                except Exception:
                    pass

        if not text:
            if "road" in slug_clean or "roman" in slug_clean:
                text = "NEVER DESTROYED?"
            elif "cold" in slug_clean or "ice" in slug_clean:
                text = "IMPOSSIBLE ICE?"
            elif "waking" in slug_clean or "alarm" in slug_clean:
                text = "NEVER WAKE UP?"
            elif "night" in slug_clean:
                text = "SURVIVING THE VOID"
            else:
                words = slug.replace("_", " ").split()[:3]
                text = " ".join(words).upper() + "?"

    if tag_override:
        badge = tag_override.strip().upper()
    else:
        if "road" in slug_clean or "roman" in slug_clean:
            badge = "2,000 YEAR SECRET"
        elif "cold" in slug_clean or "ice" in slug_clean:
            badge = "400 BC SECRET"
        elif "waking" in slug_clean or "alarm" in slug_clean:
            badge = "ANCIENT TRICK"
        elif "night" in slug_clean:
            badge = "50,000 BC"
        else:
            badge = "FORBIDDEN"

    return text.upper(), badge


def analyze_negative_space(image, safe_zones, bbox_w, bbox_h):
    """Scans candidate text placement zones and selects the optimal low-clutter negative space."""
    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_np = np.array(edges)
    gray_np = np.array(gray)
    h, w = edge_np.shape

    best_candidate = None
    min_clutter_score = float("inf")

    for cand in safe_zones:
        cx, cy = cand["cx"], cand["cy"]
        x1 = max(0, int(cx - bbox_w // 2))
        y1 = max(0, int(cy - bbox_h // 2))
        x2 = min(w, int(cx + bbox_w // 2))
        y2 = min(h, int(cy + bbox_h // 2))

        crop_edges = edge_np[y1:y2, x1:x2]
        crop_gray = gray_np[y1:y2, x1:x2]

        if crop_edges.size == 0:
            continue

        edge_density = float(np.mean(crop_edges))
        lum_variance = float(np.std(crop_gray))
        mean_lum = float(np.mean(crop_gray))

        # Clutter score: lower is cleaner negative space
        clutter_score = edge_density * 1.5 + lum_variance * 0.8
        
        # Priority penalty if specified in candidate
        clutter_score += cand.get("penalty", 0.0)

        if clutter_score < min_clutter_score:
            min_clutter_score = clutter_score
            best_candidate = {
                "cx": cx,
                "cy": cy,
                "name": cand.get("name", "custom"),
                "edge_density": edge_density,
                "mean_lum": mean_lum,
                "lum_variance": lum_variance,
                "clutter_score": clutter_score
            }

    return best_candidate or safe_zones[0]


def render_supersampled_tilted_text(
    canvas_2x, text, cx_2x, cy_2x, font_2x,
    fill_col=(255, 230, 0, 255),
    stroke_col=(12, 16, 24, 255),
    stroke_w=24,
    angle=-3.5,
    needs_ink_pill=False,
    pill_alpha=190
):
    """Renders tilted curiosity text at 2x resolution with adaptive ink pill and deep drop shadow."""
    dummy_im = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy_im)
    bbox = d.textbbox((0, 0), text, font=font_2x, stroke_width=stroke_w)
    tw = (bbox[2] - bbox[0]) + stroke_w * 4 + 80
    th = (bbox[3] - bbox[1]) + stroke_w * 4 + 60

    txt_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt_layer)

    # 1. Optional Adaptive Dark Ink Pill Backdrop (for noisy or high-luminance backgrounds)
    if needs_ink_pill:
        pill_pad_x = 36
        pill_pad_y = 18
        px1 = (tw - (bbox[2] - bbox[0])) // 2 - pill_pad_x
        py1 = (th - (bbox[3] - bbox[1])) // 2 - pill_pad_y
        px2 = px1 + (bbox[2] - bbox[0]) + pill_pad_x * 2
        py2 = py1 + (bbox[3] - bbox[1]) + pill_pad_y * 2
        td.rounded_rectangle(
            [px1, py1, px2, py2],
            radius=20,
            fill=(10, 14, 22, pill_alpha),
            outline=(255, 255, 255, 120),
            width=3
        )

    # 2. Multi-layer Deep Comic Drop Shadow
    shadow_col = (10, 14, 22, 230)
    for off_x, off_y in [(12, 14), (16, 18)]:
        td.text(
            (tw // 2 + off_x, th // 2 + off_y),
            text, font=font_2x,
            fill=shadow_col,
            anchor="mm",
            stroke_width=stroke_w + 8,
            stroke_fill=shadow_col
        )

    # 3. Heavy Charcoal Ink Stroke & Primary Fill
    td.text(
        (tw // 2, th // 2),
        text, font=font_2x,
        fill=fill_col,
        anchor="mm",
        stroke_width=stroke_w,
        stroke_fill=stroke_col
    )

    # 4. High-Quality Velocity Rotation
    rotated = txt_layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    canvas_2x.alpha_composite(rotated, (cx_2x - rotated.width // 2, cy_2x - rotated.height // 2))


def apply_look_vignette(canvas, look="bright"):
    """Applies a subtle, look-aligned edge vignette to focus viewer attention."""
    w, h = canvas.size
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    
    if look == "warm":
        base_col = (34, 22, 12)
        steps = int(min(w, h) * 0.16)
        max_alpha = 175
    elif look == "night":
        base_col = (10, 14, 28)
        steps = int(min(w, h) * 0.18)
        max_alpha = 200
    elif look == "oversimplified":
        base_col = (14, 18, 24)
        steps = int(min(w, h) * 0.12)
        max_alpha = 150
    else:  # bright / default
        base_col = (12, 16, 22)
        steps = int(min(w, h) * 0.14)
        max_alpha = 165

    for i in range(steps):
        alpha = int(((steps - i) / steps) * max_alpha)
        vd.rectangle((i, i, w - i, h - i), outline=(base_col[0], base_col[1], base_col[2], alpha), width=1)
        
    canvas.alpha_composite(vignette)


def render_16x9_thumbnail(raw_artwork_path, text, badge, out_path, look="bright", hero_font="hero", badge_font="badge"):
    """Renders 16:9 Landscape YouTube Thumbnail (1280x720) with strict timestamp exclusion."""
    W_FINAL, H_FINAL = 1280, 720
    W_2X, H_2X = W_FINAL * 2, H_FINAL * 2  # 2560 x 1440

    # 1. Load and scale base artwork to 2x resolution
    if raw_artwork_path and os.path.exists(raw_artwork_path):
        base_im = Image.open(raw_artwork_path).convert("RGBA")
        scale = max(W_2X / base_im.width, H_2X / base_im.height)
        sw, sh = int(base_im.width * scale), int(base_im.height * scale)
        base_fitted = base_im.resize((sw, sh), Image.Resampling.LANCZOS)
        cx = (sw - W_2X) // 2
        cy = (sh - H_2X) // 2
        canvas_2x = base_fitted.crop((cx, cy, cx + W_2X, cy + H_2X))
    else:
        canvas_2x = Image.new("RGBA", (W_2X, H_2X), (24, 28, 38, 255))

    # Apply look-aligned vignette
    apply_look_vignette(canvas_2x, look=look)

    # 2. Spatial Solver: Candidate Negative Space Zones (avoiding bottom-right timestamp)
    # Bottom-right timestamp exclusion zone: X: [2048, 2560], Y: [1210, 1440]
    safe_zones_16x9 = [
        {"name": "Top-Left (Hero)", "cx": int(W_2X * 0.38), "cy": int(H_2X * 0.32), "penalty": 0.0},
        {"name": "Center-Left", "cx": int(W_2X * 0.36), "cy": int(H_2X * 0.44), "penalty": 8.0},
        {"name": "Top-Center", "cx": int(W_2X * 0.50), "cy": int(H_2X * 0.24), "penalty": 12.0},
    ]

    hero_font_2x = get_curated_font(role=hero_font, size=172)
    badge_font_2x = get_curated_font(role=badge_font, size=68)

    # Multi-line handling if text is long
    words = text.split()
    if len(words) > 2:
        mid = (len(words) + 1) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [text]

    # Measure total text bounding box at 2x
    dummy_im = Image.new("RGBA", (10, 10))
    d_dummy = ImageDraw.Draw(dummy_im)
    max_line_w = 0
    total_line_h = 0
    line_bboxes = []
    for line in lines:
        bb = d_dummy.textbbox((0, 0), line, font=hero_font_2x, stroke_width=24)
        lw = bb[2] - bb[0]
        lh = bb[3] - bb[1]
        line_bboxes.append((lw, lh))
        max_line_w = max(max_line_w, lw)
        total_line_h += lh + 24

    best_zone = analyze_negative_space(canvas_2x, safe_zones_16x9, max_line_w, total_line_h)

    # Auto-Contrast Guard: Sample luminance behind text
    mean_lum = best_zone["mean_lum"]
    lum_var = best_zone["lum_variance"]
    needs_ink_pill = mean_lum > 155 or lum_var > 45

    # Render Badge Pill above text
    badge_x = best_zone["cx"] - max_line_w // 2 + 10
    badge_y = best_zone["cy"] - total_line_h // 2 - 110
    # Keep badge safely on screen
    badge_x = max(120, badge_x)
    badge_y = max(90, badge_y)

    d2 = ImageDraw.Draw(canvas_2x)
    b_bbox = d2.textbbox((0, 0), badge, font=badge_font_2x)
    bw = b_bbox[2] - b_bbox[0] + 64
    bh = b_bbox[3] - b_bbox[1] + 28
    d2.rounded_rectangle(
        [badge_x, badge_y, badge_x + bw, badge_y + bh],
        radius=20,
        fill=(255, 59, 48, 245),
        outline=(255, 255, 255, 240),
        width=5
    )
    d2.text(
        (badge_x + bw // 2, badge_y + bh // 2 - 2),
        badge,
        font=badge_font_2x,
        fill=(255, 255, 255),
        anchor="mm"
    )

    # Render Hero Text
    start_y = best_zone["cy"] - (len(lines) - 1) * 95
    for idx, line in enumerate(lines):
        line_cy = start_y + idx * 190
        render_supersampled_tilted_text(
            canvas_2x, line,
            cx_2x=best_zone["cx"],
            cy_2x=line_cy,
            font_2x=hero_font_2x,
            fill_col=(255, 230, 0, 255),
            stroke_col=(12, 16, 24, 255),
            stroke_w=26,
            angle=-3.5,
            needs_ink_pill=needs_ink_pill,
            pill_alpha=190
        )

    # Downsample 2x canvas to final 1280x720 using LANCZOS
    final_16x9 = canvas_2x.resize((W_FINAL, H_FINAL), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    final_16x9.convert("RGB").save(out_path, quality=95)

    return {
        "out_path": out_path,
        "resolution": f"{W_FINAL}x{H_FINAL}",
        "zone": best_zone["name"],
        "mean_lum": round(mean_lum, 1),
        "lum_var": round(lum_var, 1),
        "ink_pill_used": needs_ink_pill,
        "lines": lines,
        "badge": badge
    }


def render_9x16_thumbnail(raw_artwork_path, text, badge, out_path, look="bright", hero_font="hero", badge_font="badge"):
    """Renders 9:16 Vertical Shorts Cover (1080x1920) with strict mobile UI safe margins."""
    W_FINAL, H_FINAL = 1080, 1920
    W_2X, H_2X = W_FINAL * 2, H_FINAL * 2  # 2160 x 3840

    # 1. Load and scale base artwork to 2x resolution
    if raw_artwork_path and os.path.exists(raw_artwork_path):
        base_im = Image.open(raw_artwork_path).convert("RGBA")
        scale = max(W_2X / base_im.width, H_2X / base_im.height)
        sw, sh = int(base_im.width * scale), int(base_im.height * scale)
        base_fitted = base_im.resize((sw, sh), Image.Resampling.LANCZOS)
        cx = (sw - W_2X) // 2
        cy = (sh - H_2X) // 2
        canvas_2x = base_fitted.crop((cx, cy, cx + W_2X, cy + H_2X))
    else:
        canvas_2x = Image.new("RGBA", (W_2X, H_2X), (24, 28, 38, 255))

    # Apply look-aligned vignette
    apply_look_vignette(canvas_2x, look=look)

    # 2. Spatial Solver: Shorts Mobile Safe Margin Zones
    # Exclude top 14% (header Y < 538 at 2x)
    # Exclude bottom 22% (sound/ticker Y > 2995 at 2x)
    # Exclude right 18% (action buttons X > 1771 at 2x)
    safe_zones_9x16 = [
        {"name": "Upper-Center (Primary)", "cx": int(W_2X * 0.50), "cy": int(H_2X * 0.28), "penalty": 0.0},
        {"name": "Mid-Upper", "cx": int(W_2X * 0.50), "cy": int(H_2X * 0.36), "penalty": 6.0},
        {"name": "Left-Biased Upper", "cx": int(W_2X * 0.45), "cy": int(H_2X * 0.29), "penalty": 4.0},
    ]

    hero_font_2x = get_curated_font(role=hero_font, size=188)
    badge_font_2x = get_curated_font(role=badge_font, size=76)

    # Multi-line handling
    words = text.split()
    if len(words) > 2:
        mid = (len(words) + 1) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [text]

    dummy_im = Image.new("RGBA", (10, 10))
    d_dummy = ImageDraw.Draw(dummy_im)
    max_line_w = 0
    total_line_h = 0
    for line in lines:
        bb = d_dummy.textbbox((0, 0), line, font=hero_font_2x, stroke_width=28)
        max_line_w = max(max_line_w, bb[2] - bb[0])
        total_line_h += (bb[3] - bb[1]) + 28

    best_zone = analyze_negative_space(canvas_2x, safe_zones_9x16, max_line_w, total_line_h)

    # Auto-Contrast Guard
    mean_lum = best_zone["mean_lum"]
    lum_var = best_zone["lum_variance"]
    needs_ink_pill = mean_lum > 155 or lum_var > 45

    # Render Badge Pill centered above text
    d2 = ImageDraw.Draw(canvas_2x)
    b_bbox = d2.textbbox((0, 0), badge, font=badge_font_2x)
    bw = b_bbox[2] - b_bbox[0] + 76
    bh = b_bbox[3] - b_bbox[1] + 34
    badge_cx = best_zone["cx"]
    badge_cy = best_zone["cy"] - total_line_h // 2 - 130
    # Safe bound check
    badge_cy = max(int(H_2X * 0.16), badge_cy)

    d2.rounded_rectangle(
        [badge_cx - bw // 2, badge_cy - bh // 2, badge_cx + bw // 2, badge_cy + bh // 2],
        radius=24,
        fill=(255, 59, 48, 245),
        outline=(255, 255, 255, 240),
        width=6
    )
    d2.text(
        (badge_cx, badge_cy - 2),
        badge,
        font=badge_font_2x,
        fill=(255, 255, 255),
        anchor="mm"
    )

    # Render Hero Text
    start_y = best_zone["cy"] - (len(lines) - 1) * 110
    for idx, line in enumerate(lines):
        line_cy = start_y + idx * 220
        render_supersampled_tilted_text(
            canvas_2x, line,
            cx_2x=best_zone["cx"],
            cy_2x=line_cy,
            font_2x=hero_font_2x,
            fill_col=(255, 230, 0, 255),
            stroke_col=(12, 16, 24, 255),
            stroke_w=28,
            angle=-3.0,
            needs_ink_pill=needs_ink_pill,
            pill_alpha=190
        )

    # Downsample 2x canvas to final 1080x1920 using LANCZOS
    final_9x16 = canvas_2x.resize((W_FINAL, H_FINAL), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    final_9x16.convert("RGB").save(out_path, quality=95)

    return {
        "out_path": out_path,
        "resolution": f"{W_FINAL}x{H_FINAL}",
        "zone": best_zone["name"],
        "mean_lum": round(mean_lum, 1),
        "lum_var": round(lum_var, 1),
        "ink_pill_used": needs_ink_pill,
        "lines": lines,
        "badge": badge
    }


def execute_2stage_thumbnail_pipeline(
    project_dir=".",
    text=None,
    tag=None,
    look="bright",
    no_flow=False,
    out_16x9=None,
    out_9x16=None,
    hero_font=None,
    badge_font=None
):
    """Executes the complete 2-Stage Intelligent Thumbnail Pipeline:
    Stage 1: Dedicated Google Flow Base Artwork Generator (flow_thumbnail_generator.py)
    Stage 2: Spatial Negative-Space Solver & Supersampled CTR Polish (thumbnail_generator.py)
    """
    project_dir = os.path.abspath(project_dir)
    pack_dir = os.path.join(project_dir, "UPLOAD_PACK")
    os.makedirs(pack_dir, exist_ok=True)

    out_16x9 = out_16x9 or os.path.join(pack_dir, "thumbnail_16x9.png")
    out_9x16 = out_9x16 or os.path.join(pack_dir, "thumbnail_9x16.png")

    print("\n==================================================")
    print("🌟 2-STAGE INTELLIGENT THUMBNAIL PIPELINE START")
    print(f"   Project: {os.path.basename(project_dir)} | Look: {look}")
    print("==================================================")

    # --- STAGE 1: FLOW BASE ARTWORK ---
    import flow_thumbnail_generator
    stage1_res = flow_thumbnail_generator.generate_stage1_flow_artwork(
        project_dir=project_dir,
        out_dir=pack_dir,
        look=look,
        no_flow=no_flow
    )
    raw_16x9 = stage1_res["raw_16x9"]
    raw_9x16 = stage1_res["raw_9x16"]

    # --- STAGE 2: POST-FLOW COMPOSITION & CTR POLISH ---
    hook_text, badge_tag = extract_hook_and_badge(project_dir, text_override=text, tag_override=tag)
    print("\n==================================================")
    print("✨ STAGE 2: SPATIAL SOLVER & SUPERSAMPLED CTR POLISH")
    print(f"   Curiosity Hook: \"{hook_text}\" | Badge: [{badge_tag}]")
    print("==================================================")

    h_font_role = hero_font or "hero"
    b_font_role = badge_font or "badge"

    audit_16 = render_16x9_thumbnail(raw_16x9, hook_text, badge_tag, out_16x9, look=look, hero_font=h_font_role, badge_font=b_font_role)
    audit_9 = render_9x16_thumbnail(raw_9x16, hook_text, badge_tag, out_9x16, look=look, hero_font=h_font_role, badge_font=b_font_role)

    # Mirror to img/ for convenience
    img_dir = os.path.join(project_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    import shutil
    shutil.copy2(out_16x9, os.path.join(img_dir, "thumbnail_16x9.png"))
    shutil.copy2(out_9x16, os.path.join(img_dir, "thumbnail_9x16.png"))

    stage2_audit = {
        "project": os.path.basename(project_dir),
        "look": look,
        "fonts_used": {
            "hero": h_font_role,
            "badge": b_font_role
        },
        "stage1_flow": stage1_res["audit"],
        "stage2_ctr": {
            "thumbnail_16x9": audit_16,
            "thumbnail_9x16": audit_9
        }
    }

    audit_path = os.path.join(pack_dir, "STAGE2_CTR_AUDIT.json")
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(stage2_audit, f, indent=2)

    print("\n🏆 2-Stage Thumbnail Suite Generation Complete:")
    print(f"   • 16:9 Raw:      {raw_16x9}")
    print(f"   • 16:9 Polished: {out_16x9} (Zone: {audit_16['zone']}, Lum: {audit_16['mean_lum']})")
    print(f"   • 9:16 Raw:      {raw_9x16}")
    print(f"   • 9:16 Polished: {out_9x16} (Zone: {audit_9['zone']}, Lum: {audit_9['mean_lum']})")
    print(f"   • Decision Log:  {audit_path}")
    print("==================================================\n")

    return {
        "raw_16x9": raw_16x9,
        "out_16x9": out_16x9,
        "raw_9x16": raw_9x16,
        "out_9x16": out_9x16,
        "audit": stage2_audit
    }


def create_thumbnail(project_dir=".", text=None, tag=None, out_16x9="thumbnail_16x9.png", out_9x16="thumbnail_9x16.png", look="bright", hero_font=None, badge_font=None):
    """Backward compatibility wrapper for create_thumbnail."""
    return execute_2stage_thumbnail_pipeline(
        project_dir=project_dir,
        text=text,
        tag=tag,
        look=look,
        out_16x9=out_16x9,
        out_9x16=out_9x16,
        hero_font=hero_font,
        badge_font=badge_font
    )


def main():
    p = argparse.ArgumentParser(description="2-Stage Intelligent Thumbnail Pipeline")
    p.add_argument("project_dir", nargs="?", default=".", help="Target project root directory")
    p.add_argument("--text", default=None, help="Bold 2-4 word curiosity text (e.g. 'NEVER DESTROYED?')")
    p.add_argument("--tag", default=None, help="Top badge tag (e.g. '2,000 YEAR SECRET')")
    p.add_argument("--look", default="bright", help="Active look palette (warm, night, bright, etc.)")
    p.add_argument("--no-flow-thumb", action="store_true", help="Skip Flow generation, use high-contrast local base")
    p.add_argument("--hero-font", default=None, help="Font role or file for hero text (hero, permanent, luckiest, montserrat, modern, etc.)")
    p.add_argument("--badge-font", default=None, help="Font role or file for badge text (badge, bangers, montserrat, etc.)")
    p.add_argument("--out-16x9", default=None, help="Output path for 16:9 landscape thumbnail")
    p.add_argument("--out-9x16", default=None, help="Output path for 9:16 vertical shorts cover")
    args = p.parse_args()

    execute_2stage_thumbnail_pipeline(
        project_dir=args.project_dir,
        text=args.text,
        tag=args.tag,
        look=args.look,
        no_flow=args.no_flow_thumb,
        hero_font=args.hero_font,
        badge_font=args.badge_font,
        out_16x9=args.out_16x9,
        out_9x16=args.out_9x16
    )


if __name__ == "__main__":
    main()
