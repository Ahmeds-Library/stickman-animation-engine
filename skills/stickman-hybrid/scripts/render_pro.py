#!/usr/bin/env python3
"""render_pro.py: Next-Gen Stickman Explainer & 9:16 Shorts Renderer

Features:
- Dual Format: 16:9 Landscape (1920x1080) & 9:16 Vertical Shorts (1080x1920)
- Ken Burns Camera Engine: subtle organic push-in / pull-out / pan on all shots
- Damped Harmonic Spring Physics: bouncy sticker entries (pop, slideL, slideR, rise)
- Animated Dynamic Bar Charts: smooth growing bars synced to spoken percentages
- Dynamic Rolling Counters: smooth cubic roll-up for numbers (e.g. 1,000,000 YEARS)
- Kinetic Word-Level Subtitles: Alex Hormozi single-word kinetic pop in golden-amber
- Tactile Aesthetic: subtle paper grain and warm radial vignette
- Intelligent Anti-Occlusion Guard: automatically keeps overlays away from center focal points
- Automatic Text Label Deduplication: prevents displaying duplicate text across tags and banners
- Instant Single Frame Export: `--frame T --frame-out path.png` for rapid visual inspection
"""
import argparse, csv, os, shutil, subprocess, sys, math, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# Autonomous Zero-Setup Bootstrapper
try:
    import auto_bootstrap
    auto_bootstrap.ensure_environment()
except Exception:
    pass

# Active Reinforcement Learning Policy Engine Integration
try:
    import rl_memory
    ACTIVE_RL_POLICY = rl_memory.get_active_policy()
except Exception:
    ACTIVE_RL_POLICY = {}

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
FONTS = os.path.join(SKILL_ROOT, "fonts")
if not os.path.exists(FONTS):
    FONTS = "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/fonts"
FONT_PATH = os.path.join(FONTS, "PatrickHand-Regular.ttf")
FONT_CX_PATH = os.path.join(FONTS, "Kalam-Bold.ttf")

LOOKS = {
    "bright": ((255, 253, 246), (28, 32, 44), (252, 249, 238), (196, 222, 240)),
    "warm": ((252, 244, 222), (58, 34, 18), (236, 190, 105), (196, 132, 58)),
    "ink": ((255, 255, 255), (20, 20, 20), (252, 251, 247), (232, 229, 220)),
    "painted": ((246, 243, 236), (34, 36, 40), (226, 226, 222), (150, 158, 160)),
    "night": ((250, 242, 220), (24, 20, 30), (58, 62, 84), (18, 20, 32)),
}
PAPER, INK, CARD_IN, CARD_OUT = LOOKS["bright"]
CARD_INK = INK

def set_look(name):
    global PAPER, INK, CARD_IN, CARD_OUT, CARD_INK, _card_cache
    if name not in LOOKS:
        name = "bright"
    PAPER, INK, CARD_IN, CARD_OUT = LOOKS[name]
    CARD_INK = PAPER if name == "night" else INK
    _card_cache.clear()

FPS = 30
_text_cache = {}
_card_cache = {}
_sticker_cache = {}


def text_layer(text, size, colour):
    key = (text, size, colour)
    if key not in _text_cache:
        f = ImageFont.truetype(FONT_PATH, size)
        b = f.getbbox(text)
        w = max(1, b[2] - b[0] + 8)
        h = max(1, b[3] - b[1] + 8)
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).text((4 - b[0], 4 - b[1]), text, font=f, fill=255)
        im = Image.new("RGBA", m.size, colour + (0,))
        im.putalpha(m)
        _text_cache[key] = im
    return _text_cache[key]


def card_bg(w, h):
    key = (w, h)
    if key not in _card_cache:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.clip(np.hypot((x - w / 2) / (w * 0.62), (y - h / 2) / (h * 0.62)), 0, 1)[..., None]
        a = np.array(CARD_IN, np.float32) * (1 - r) + np.array(CARD_OUT, np.float32) * r
        a += np.random.default_rng(42).normal(0, 3.0, a.shape[:2]).astype(np.float32)[..., None]
        _card_cache[key] = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    return _card_cache[key].copy()


def tag_image(text, size=70):
    lines = [text_layer(ln, size, INK) for ln in text.split("|")]
    gap = int(size * 0.22)
    tw = max(l.width for l in lines) + 50
    th = sum(l.height for l in lines) + gap * (len(lines) - 1) + 30
    im = Image.new("RGBA", (tw + 12, th + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # shadow
    d.rounded_rectangle((6, 6, tw + 6, th + 6), radius=16, fill=(0, 0, 0, 45))
    d.rounded_rectangle((4, 4, tw + 4, th + 4), radius=16, fill=PAPER + (255,), outline=INK, width=4)
    y = 20
    for l in lines:
        im.alpha_composite(l, ((im.width - l.width) // 2, y))
        y += l.height + gap
    return im


def sticker(path, h):
    key = (path, h)
    if key not in _sticker_cache:
        if len(_sticker_cache) > 40:
            _sticker_cache.clear()
        im = Image.open(path).convert("RGBA")
        nw = max(1, round(im.width * h / im.height))
        im = im.resize((nw, h), Image.LANCZOS)
        b = max(5, h // 45)
        pad = b * 4
        big = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        big.paste(im, (pad, pad), im)
        ring = big.getchannel("A").filter(ImageFilter.MaxFilter(2 * b + 1))
        shadow = Image.new("RGBA", big.size, (0, 0, 0, 0))
        shadow.putalpha(ring.point(lambda v: int(v * 0.40)).filter(ImageFilter.GaussianBlur(b * 1.5)))
        out = Image.new("RGBA", big.size, (0, 0, 0, 0))
        out.alpha_composite(shadow, (b // 2, b + 2))
        white = Image.new("RGBA", big.size, (255, 255, 255, 0))
        white.putalpha(ring)
        out.alpha_composite(white)
        out.alpha_composite(big)
        _sticker_cache[key] = out
    return _sticker_cache[key]


def spring_p(p):
    """Tastefully damped spring: crisp tactile pop-in with controlled 1.05x overshoot (restrained elegance)."""
    p = max(0.0, min(1.0, p))
    return 1.0 - np.exp(-8.5 * p) * np.cos(8.0 * p)


def compute_negative_space_score(bg_im, x0, y0, x1, y1):
    """Computes visual clutter / edge density of a crop region on the background image.
    Lower score = clean negative space (ideal for sticker placement without occluding focal characters).
    """
    try:
        x0, y0 = max(0, int(x0)), max(0, int(y0))
        x1, y1 = min(bg_im.width, int(x1)), min(bg_im.height, int(y1))
        if x1 <= x0 + 10 or y1 <= y0 + 10:
            return 999.0
        crop = bg_im.crop((x0, y0, x1, y1)).convert("L")
        arr = np.array(crop, dtype=np.float32)
        grad_y = float(np.std(np.diff(arr, axis=0)))
        grad_x = float(np.std(np.diff(arr, axis=1)))
        return grad_y + grad_x
    except Exception:
        return 100.0


def calculate_intelligent_sticker_anchor(bg_im, item_w, item_h, requested_pos, is_shorts, W, H, occupied_boxes, sub_top_y):
    """Phase 2 Spatial Intelligence:
    Finds optimal (cx, cy) anchor with zero collisions against:
    1. Subtitles / captions
    2. Platform UI safe zones (Shorts 9:16 right-side icons & bottom overlay zone)
    3. Other active stickers in occupied_boxes
    4. Focal subjects in background shot (picks lowest edge density negative space)
    """
    spatial = ACTIVE_RL_POLICY.get("rule_24_spatial_hierarchy", {})
    right_ui_margin = spatial.get("shorts_margin_right_px", 220) if is_shorts else 54
    sub_buf = spatial.get("min_cutout_subtitle_buffer_px", 140 if is_shorts else 80)
    
    max_safe_y = sub_top_y - sub_buf - item_h // 2
    min_safe_y = (200 if is_shorts else 80) + item_h // 2
    min_safe_x = (48 if is_shorts else 54) + item_w // 2
    max_safe_x = W - right_ui_margin - item_w // 2
    
    if max_safe_y < min_safe_y:
        max_safe_y = min_safe_y + 40

    if is_shorts:
        candidates = [
            ("top_right", int(W * 0.65), int(min_safe_y + (max_safe_y - min_safe_y) * 0.22)),
            ("top_left", int(W * 0.28), int(min_safe_y + (max_safe_y - min_safe_y) * 0.22)),
            ("mid_right", int(W * 0.66), int(min_safe_y + (max_safe_y - min_safe_y) * 0.62)),
            ("mid_left", int(W * 0.26), int(min_safe_y + (max_safe_y - min_safe_y) * 0.62)),
            ("center_high", int(W * 0.50), int(min_safe_y)),
        ]
    else:
        candidates = [
            ("right_high", int(W * 0.78), int(H * 0.28)),
            ("right_mid", int(W * 0.76), int(H * 0.44)),
            ("left_high", int(W * 0.22), int(H * 0.28)),
            ("left_mid", int(W * 0.24), int(H * 0.44)),
            ("center_high", int(W * 0.50), int(H * 0.26)),
        ]

    req = str(requested_pos or "").lower()
    if "left" in req:
        candidates.sort(key=lambda c: 0 if "left" in c[0] else 1)
    elif "right" in req:
        candidates.sort(key=lambda c: 0 if "right" in c[0] else 1)
    elif "top" in req or "high" in req:
        candidates.sort(key=lambda c: 0 if ("top" in c[0] or "high" in c[0]) else 1)

    best_anchor = None
    best_score = float("inf")

    for name, cx, cy in candidates:
        cx = max(min_safe_x, min(cx, max_safe_x))
        cy = max(min_safe_y, min(cy, max_safe_y))
        bx0, by0, bx1, by1 = cx - item_w // 2, cy - item_h // 2, cx + item_w // 2, cy + item_h // 2
        
        collides = False
        for ox0, oy0, ox1, oy1 in occupied_boxes:
            if not (bx1 < ox0 - 20 or bx0 > ox1 + 20 or by1 < oy0 - 20 or by0 > oy1 + 20):
                collides = True
                break
        if collides:
            continue
            
        density_score = compute_negative_space_score(bg_im, bx0, by0, bx1, by1)
        if density_score < best_score:
            best_score = density_score
            best_anchor = (cx, cy)

    if best_anchor:
        return best_anchor[0], best_anchor[1], 1.0

    # Auto-scale fallback when space is dense
    fallback_cx = max(min_safe_x, min(candidates[0][1], max_safe_x))
    fallback_cy = max(min_safe_y, min(candidates[0][2], max_safe_y))
    return fallback_cx, fallback_cy, 0.82


def draw_bars(fr, spec, t_rel, w, h, is_shorts):
    """Dynamic animated bar chart."""
    items = [kv.split("=") for kv in spec.split(",")]
    n = len(items)
    d = ImageDraw.Draw(fr)
    if is_shorts:
        bx0, by0, bx1, by1 = 120, 1140, w - 120, 1380
    else:
        bx0, by0, bx1, by1 = 1300, 220, 1860, 980
    # box shadow + card
    d.rounded_rectangle((bx0 + 6, by0 + 6, bx1 + 6, by1 + 6), radius=24, fill=(0, 0, 0, 45))
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=24, fill=PAPER, outline=INK, width=5)
    
    cw = bx1 - bx0
    ch = by1 - by0
    base = by1 - 70
    maxh = ch - 160
    bw = min(150, (cw - 80) // n - 30)
    start_x = bx0 + (cw - (n * bw + (n - 1) * 30)) // 2
    
    for i, (name, val) in enumerate(items):
        target_val = float(val)
        grow_p = min(1.0, max(0.0, (t_rel - i * 0.35) / 0.50))
        cur_val = target_val * (grow_p * grow_p * (3 - 2 * grow_p))
        x0 = start_x + i * (bw + 30)
        top = base - maxh * (cur_val / 100.0)
        bar_fill = (235, 115, 55) if i == n - 1 else (160, 160, 160)
        d.rectangle((x0, top, x0 + bw, base), fill=bar_fill, outline=INK, width=4)
        
        # label
        if grow_p > 0.2:
            lbl_val = f"{int(round(cur_val))}%"
            l1 = text_layer(lbl_val, 48 if is_shorts else 58, INK)
            fr.paste(l1, (int(x0 + bw // 2 - l1.width // 2), int(top - l1.height - 8)), l1)
        l2 = text_layer(name, 38 if is_shorts else 46, INK)
        fr.paste(l2, (int(x0 + bw // 2 - l2.width // 2), int(base + 12)), l2)
    d.line((start_x - 15, base, start_x + n * bw + (n - 1) * 30 + 15, base), fill=INK, width=5)


def draw_label(fr, text, pos, w, h, is_shorts):
    big = pos == "big"
    size = (100 if is_shorts else 130) if big else (48 if is_shorts else 56)
    lines = [text_layer(ln, size, CARD_INK if big else INK) for ln in text.split("|")]
    gap = int(size * 0.22)
    tw = max(l.width for l in lines)
    th = sum(l.height for l in lines) + gap * (len(lines) - 1)
    
    if big:
        cx, cy = w // 2, (h // 2 - 80 if is_shorts else h // 2)
    else:
        if is_shorts:
            # Clean Upper Concept Pill in Shorts: positioned safely at y=230 (below top safe zone, above action)
            # Never defaults to 1180 which clashed with kinetic subtitles!
            cx = w // 2
            cy = 230
        else:
            # Broadcast Documentary Hierarchy in 16:9 widescreen:
            # Default is sleek Top-Left Chapter/Concept Slug (Kurzgesagt/Vox standard)
            # completely orthogonal from bottom kinetic subtitles!
            if "r" in pos or "right" in pos:
                cx = w - 140 - tw // 2
            elif "center" in pos or "c" in pos:
                cx = w // 2
            else:
                cx = 140 + tw // 2 # Default documentary chapter slug left-docked
            
            if "bottom" in pos or "b" in pos:
                cy = h - 220 - th // 2 # Safe above subtitles at 920
            else:
                cy = 100 + th // 2 # Top-Left documentary corner slug
            
    if not big:
        rect = (cx - tw // 2 - 26, cy - th // 2 - 14, cx + tw // 2 + 26, cy + th // 2 + 14)
        d = ImageDraw.Draw(fr)
        d.rounded_rectangle((rect[0] + 4, rect[1] + 4, rect[2] + 4, rect[3] + 4), radius=16, fill=(0, 0, 0, 40))
        d.rounded_rectangle(rect, radius=16, fill=PAPER, outline=INK, width=3)
        
    y = cy - th // 2
    for l in lines:
        fr.paste(l, (cx - l.width // 2, y), l)
        y += l.height + gap


def resolve_sticker_path(o_img):
    """Bulletproof multi-directory and semantic registry resolution."""
    if not o_img or not isinstance(o_img, str):
        return None
    s = o_img.strip()
    if not s or s in ("tag", "count") or s.startswith("bars:") or s in ("stamp_x", "stamp_check", "stamp_false", "stamp_true", "stamp_myth"):
        return None
    if os.path.exists(s) and os.path.getsize(s) > 500:
        return s
    name_base = os.path.basename(s)
    name_no_ext = os.path.splitext(name_base)[0]
    cands = [
        s,
        s + ".png" if not s.endswith(".png") else s,
        os.path.join("elements", "cut", f"{name_no_ext}.png"),
        os.path.join("elements", "cut", name_base),
        os.path.join("..", "elements", "cut", f"{name_no_ext}.png"),
        os.path.join("..", "elements", "cut", name_base),
        os.path.join("..", "short", "elements", "cut", f"{name_no_ext}.png"),
        os.path.join("..", "long", "elements", "cut", f"{name_no_ext}.png"),
    ]
    for cp in cands:
        if os.path.exists(cp) and os.path.getsize(cp) > 500:
            return cp
    try:
        import asset_registry
        p_root = asset_registry.resolve_project_root(os.getcwd())
        reg_m = asset_registry.find_reusable_sticker(name_no_ext, p_root)
        if reg_m and os.path.exists(reg_m["path"]) and os.path.getsize(reg_m["path"]) > 500:
            return reg_m["path"]
    except Exception:
        pass
    return None


def load_and_scale_sticker(path_or_im, target_h):
    """Loads a sticker, scales it keeping aspect ratio to target_h."""
    if path_or_im is None or target_h <= 0:
        return None
    if isinstance(path_or_im, Image.Image):
        raw = path_or_im.convert("RGBA") if path_or_im.mode != "RGBA" else path_or_im
    else:
        resolved = resolve_sticker_path(str(path_or_im))
        if not resolved or not os.path.exists(resolved):
            return None
        if resolved not in _sticker_cache:
            try:
                _sticker_cache[resolved] = Image.open(resolved).convert("RGBA")
            except Exception:
                return None
        raw = _sticker_cache[resolved]

    scale = target_h / max(1, raw.height)
    w = max(1, int(raw.width * scale))
    return raw.resize((w, target_h), Image.LANCZOS)


def add_sticker_drop_shadow(im, offset=(12, 16), shadow_color=(0, 0, 0, 45), blur_radius=8):
    """Applies a soft comic shadow behind a transparent cutout."""
    if im is None or im.mode != "RGBA":
        return im
    pad_x = abs(offset[0]) + blur_radius * 2 + 10
    pad_y = abs(offset[1]) + blur_radius * 2 + 10
    out_w = im.width + pad_x * 2
    out_h = im.height + pad_y * 2
    canvas = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))

    alpha = im.split()[3]
    shadow_mask = alpha.filter(ImageFilter.GaussianBlur(blur_radius))
    shadow_layer = Image.new("RGBA", im.size, shadow_color)
    shadow_layer.putalpha(shadow_mask)

    canvas.alpha_composite(shadow_layer, (pad_x + offset[0], pad_y + offset[1]))
    canvas.alpha_composite(im, (pad_x, pad_y))
    return canvas


def draw_card_stat(w, h, text, is_shorts=False, dt=0.0, sticker_im=None):
    """Archetype 3: Minimalist Kinetic Impact Card with 2x Supersampled Anti-Aliasing and Sticker Integration."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    parts = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else [text.strip()]
    stat_txt = parts[0] if parts else "100%"
    sub_txt = parts[1] if len(parts) > 1 else ""

    p = min(1.0, dt / 0.25)
    scale = 0.94 + 0.06 * spring_p(p)

    has_sticker = (sticker_im is not None)

    if not is_shorts:
        # Long (16:9) Layout:
        if has_sticker:
            card_w = int(W2 * 0.46 * scale)
            card_h = int(H2 * 0.50 * scale)
            cx = int(W2 * 0.30)
            cy = int(H2 * 0.46)

            stk_h2 = int(H2 * 0.48)
            stk_img = load_and_scale_sticker(sticker_im, stk_h2)
            if stk_img:
                stk_shadowed = add_sticker_drop_shadow(stk_img, offset=(14, 18), shadow_color=(0, 0, 0, 45), blur_radius=10)
                st_x = int(W2 * 0.72 - stk_shadowed.width // 2)
                st_y = int(H2 * 0.46 - stk_shadowed.height // 2)
                overlay2.alpha_composite(stk_shadowed, (st_x, st_y))
        else:
            card_w = int(W2 * 0.62 * scale)
            card_h = int(H2 * 0.46 * scale)
            cx = W2 // 2
            cy = int(H2 * 0.46)
    else:
        # Shorts (9:16) Layout:
        if has_sticker:
            stk_h2 = int(H2 * 0.22)
            stk_img = load_and_scale_sticker(sticker_im, stk_h2)
            if stk_img:
                stk_shadowed = add_sticker_drop_shadow(stk_img, offset=(10, 14), shadow_color=(0, 0, 0, 45), blur_radius=8)
                st_x = int(W2 // 2 - stk_shadowed.width // 2)
                st_y = int(H2 * 0.26 - stk_shadowed.height // 2)
                overlay2.alpha_composite(stk_shadowed, (st_x, st_y))

            card_w = int(W2 * 0.86 * scale)
            card_h = int(H2 * 0.30 * scale)
            cx = W2 // 2
            cy = int(H2 * 0.54)
        else:
            card_w = int(W2 * 0.86 * scale)
            card_h = int(H2 * 0.36 * scale)
            cx = W2 // 2
            cy = int(H2 * 0.42)

    x0, y0 = cx - card_w // 2, int(cy - card_h // 2)
    x1, y1 = cx + card_w // 2, int(cy + card_h // 2)

    # 1. Comic Offset Drop Shadow
    d2.rounded_rectangle((x0 + 16, y0 + 18, x1 + 16, y1 + 18), radius=52, fill=(0, 0, 0, 48))
    # 2. Main Card Body (warm parchment fill + bold dark ink outline)
    d2.rounded_rectangle((x0, y0, x1, y1), radius=52, fill=(254, 250, 242, 255), outline=INK, width=8)

    # 3. Top Decorative Accent Highlight Strip
    accent_w = int(card_w * 0.32)
    accent_x0 = cx - accent_w // 2
    d2.rounded_rectangle((accent_x0, y0 + 36, accent_x0 + accent_w, y0 + 52), radius=8, fill=(236, 120, 45, 255))

    # 4. Hero Stat Number (rendered at 2x)
    stat_layer = text_layer(stat_txt, 140 if is_shorts else 160, (218, 92, 42))
    stat_x = cx - stat_layer.width // 2
    stat_y = y0 + 72
    overlay2.alpha_composite(stat_layer, (stat_x, stat_y))

    # 5. Secondary Subtitle Typography with word-wrap
    if sub_txt:
        max_sub_w = card_w - 80
        words = sub_txt.split()
        sub_lines = []
        cur_line = []
        font_sz = 56 if is_shorts else 68
        for w_word in words:
            test_line = " ".join(cur_line + [w_word])
            test_l = text_layer(test_line, font_sz, INK)
            if test_l.width > max_sub_w and cur_line:
                sub_lines.append(" ".join(cur_line))
                cur_line = [w_word]
            else:
                cur_line.append(w_word)
        if cur_line:
            sub_lines.append(" ".join(cur_line))

        curr_sy = stat_y + stat_layer.height + 20
        for s_ln in sub_lines:
            sl_layer = text_layer(s_ln, font_sz, INK)
            overlay2.alpha_composite(sl_layer, (cx - sl_layer.width // 2, curr_sy))
            curr_sy += sl_layer.height + 10

    # Downsample overlay from 2x to 1x via LANCZOS anti-aliasing
    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    return fr


def draw_split_compare(w, h, text, is_shorts=False, dt=0.0, left_sticker=None, right_sticker=None, left_stamp=None, right_stamp=None):
    """Archetype 4: 50/50 Split-Screen Contrast Frame with 2x Supersampling and Dual-Sticker Integration."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    # Tonal tints for halves
    left_tint = Image.new("RGBA", (W2 // 2, H2), (255, 248, 235, 120))
    right_tint = Image.new("RGBA", (W2 - W2 // 2, H2), (235, 244, 252, 140))
    overlay2.alpha_composite(left_tint, (0, 0))
    overlay2.alpha_composite(right_tint, (W2 // 2, 0))

    # Center vertical dashed ink divider (rendered at 2x with rounded caps)
    div_x = W2 // 2
    dash_len, gap_len = 32, 22
    curr_y = 120
    end_y = H2 - (380 if is_shorts else 160)
    while curr_y < end_y:
        d2.line((div_x, curr_y, div_x, min(end_y, curr_y + dash_len)), fill=INK, width=8)
        curr_y += dash_len + gap_len

    # Parse labels
    parts = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else ["MYTH", "REALITY"]
    lbl_left = parts[0] if len(parts) > 0 else "MYTH"
    lbl_right = parts[1] if len(parts) > 1 else "REALITY"

    top_y = 360 if is_shorts else 160
    font_sz = 52 if is_shorts else 62

    # Left Pill (2x)
    l_txt = text_layer(lbl_left, font_sz, INK)
    if l_txt.width > (W2 // 2 - 100):
        l_txt = text_layer(lbl_left, int(font_sz * 0.78), INK)
    pw_l = l_txt.width + 64
    ph_l = l_txt.height + 26
    lx = W2 // 4 - pw_l // 2
    d2.rounded_rectangle((lx + 8, top_y + 8, lx + pw_l + 8, top_y + ph_l + 8), radius=28, fill=(0, 0, 0, 45))
    d2.rounded_rectangle((lx, top_y, lx + pw_l, top_y + ph_l), radius=28, fill=(254, 250, 242, 255), outline=INK, width=6)
    overlay2.alpha_composite(l_txt, (lx + 32, top_y + 13))

    # Right Pill (2x)
    r_txt = text_layer(lbl_right, font_sz, INK)
    if r_txt.width > (W2 // 2 - 100):
        r_txt = text_layer(lbl_right, int(font_sz * 0.78), INK)
    pw_r = r_txt.width + 64
    ph_r = r_txt.height + 26
    rx = (3 * W2) // 4 - pw_r // 2
    d2.rounded_rectangle((rx + 8, top_y + 8, rx + pw_r + 8, top_y + ph_r + 8), radius=28, fill=(0, 0, 0, 45))
    d2.rounded_rectangle((rx, top_y, rx + pw_r, top_y + ph_r), radius=28, fill=(254, 250, 242, 255), outline=INK, width=6)
    overlay2.alpha_composite(r_txt, (rx + 32, top_y + 13))

    # Stickers Positioning
    stk_cy = int(H2 * (0.42 if is_shorts else 0.50))
    stk_max_h = int(H2 * (0.28 if is_shorts else 0.44))

    # Left Sticker
    if left_sticker:
        l_img = load_and_scale_sticker(left_sticker, stk_max_h)
        if l_img:
            l_sh = add_sticker_drop_shadow(l_img, offset=(12, 16), shadow_color=(0, 0, 0, 45), blur_radius=10)
            overlay2.alpha_composite(l_sh, (W2 // 4 - l_sh.width // 2, stk_cy - l_sh.height // 2))

    # Right Sticker
    if right_sticker:
        r_img = load_and_scale_sticker(right_sticker, stk_max_h)
        if r_img:
            r_sh = add_sticker_drop_shadow(r_img, offset=(12, 16), shadow_color=(0, 0, 0, 45), blur_radius=10)
            overlay2.alpha_composite(r_sh, ((3 * W2) // 4 - r_sh.width // 2, stk_cy - r_sh.height // 2))

    # Optional Verdict Stamps Composited at 2x
    if left_stamp:
        st_l = draw_myth_stamp(left_stamp, dt, target_size=int(260 * (1.6 if is_shorts else 2.0)))
        overlay2.alpha_composite(st_l, (W2 // 4 - st_l.width // 2, stk_cy - st_l.height // 2))

    if right_stamp:
        st_r = draw_myth_stamp(right_stamp, dt, target_size=int(260 * (1.6 if is_shorts else 2.0)))
        overlay2.alpha_composite(st_r, ((3 * W2) // 4 - st_r.width // 2, stk_cy - st_r.height // 2))

    # Downsample via LANCZOS
    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    return fr


def draw_data_timeline(w, h, text, is_shorts=False, dt=0.0, accent_sticker=None):
    """Archetype 6: Programmatic Data Timeline Card with 2x Supersampling and Accent Sticker Integration."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    parts = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else ["PHASE 1", "PHASE 2", "PHASE 3"]
    n_blocks = len(parts)
    if n_blocks == 0:
        return card_bg(w, h).convert("RGBA")

    # Accent Sticker
    if accent_sticker:
        stk_h2 = int(H2 * (0.22 if is_shorts else 0.30))
        stk_img = load_and_scale_sticker(accent_sticker, stk_h2)
        if stk_img:
            stk_sh = add_sticker_drop_shadow(stk_img, offset=(10, 14), shadow_color=(0, 0, 0, 45), blur_radius=8)
            if not is_shorts:
                overlay2.alpha_composite(stk_sh, (int(W2 * 0.84 - stk_sh.width // 2), int(H2 * 0.22 - stk_sh.height // 2)))
            else:
                overlay2.alpha_composite(stk_sh, (W2 // 2 - stk_sh.width // 2, int(H2 * 0.18 - stk_sh.height // 2)))

    margin_x = 100 if is_shorts else 220
    total_w = W2 - 2 * margin_x
    block_gap = 22
    block_w = (total_w - (n_blocks - 1) * block_gap) // n_blocks
    block_h = 280 if is_shorts else 320
    base_y = int(H2 * (0.38 if is_shorts else 0.44))

    colors = [
        ((48, 56, 75), (255, 255, 255)),   # Slate Navy fill + white text
        ((236, 140, 45), (20, 24, 32)),   # Warm Amber fill + dark text
        ((35, 42, 60), (255, 255, 255)),   # Deep Indigo fill + white text
        ((210, 80, 50), (255, 255, 255)),  # Terracotta fill + white text
    ]

    prog = min(1.0, dt / 0.55)
    max_visible_idx = int(prog * n_blocks)

    for i, seg in enumerate(parts):
        if i > max_visible_idx and dt < 0.55:
            continue
        bx0 = margin_x + i * (block_w + block_gap)
        bx1 = bx0 + block_w
        by0 = base_y
        by1 = by0 + block_h

        fill_color, text_color = colors[i % len(colors)]

        d2.rounded_rectangle((bx0 + 12, by0 + 12, bx1 + 12, by1 + 12), radius=36, fill=(0, 0, 0, 48))
        d2.rounded_rectangle((bx0, by0, bx1, by1), radius=36, fill=fill_color + (255,), outline=INK, width=8)

        seg_parts = [sp.strip() for sp in seg.split(":") if sp.strip()]
        header_str = seg_parts[0] if len(seg_parts) > 1 else f"PART {i+1}"
        body_str = seg_parts[1] if len(seg_parts) > 1 else seg_parts[0]

        h_layer = text_layer(header_str, 54 if is_shorts else 64, text_color)
        b_layer = text_layer(body_str, 40 if is_shorts else 46, text_color)

        hx = bx0 + (block_w - h_layer.width) // 2
        hy = by0 + (block_h - (h_layer.height + b_layer.height + 16)) // 2
        overlay2.alpha_composite(h_layer, (hx, hy))
        overlay2.alpha_composite(b_layer, (bx0 + (block_w - b_layer.width) // 2, hy + h_layer.height + 16))

    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    return fr


def draw_stat_pie(w, h, text, is_shorts=False, dt=0.0, accent_sticker=None):
    """Archetype 6: Programmatic Donut Stat / Pie Card with 2x Supersampling and Accent Sticker Integration."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    parts = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else [text.strip(), "STATISTIC"]
    stat_val = parts[0]
    stat_desc = parts[1] if len(parts) > 1 else ""

    num_m = re.search(r"(\d+(?:\.\d+)?)", stat_val)
    pct = float(num_m.group(1)) if num_m else 75.0
    pct = min(100.0, max(0.0, pct))

    has_sticker = (accent_sticker is not None)

    if not is_shorts:
        cx = int(W2 * 0.32) if has_sticker else W2 // 2
        cy = int(H2 * 0.44)
        if has_sticker:
            stk_h2 = int(H2 * 0.48)
            stk_img = load_and_scale_sticker(accent_sticker, stk_h2)
            if stk_img:
                stk_sh = add_sticker_drop_shadow(stk_img, offset=(14, 18), shadow_color=(0, 0, 0, 45), blur_radius=10)
                overlay2.alpha_composite(stk_sh, (int(W2 * 0.72 - stk_sh.width // 2), cy - stk_sh.height // 2))
    else:
        cx = W2 // 2
        cy = int(H2 * 0.46)
        if has_sticker:
            stk_h2 = int(H2 * 0.22)
            stk_img = load_and_scale_sticker(accent_sticker, stk_h2)
            if stk_img:
                stk_sh = add_sticker_drop_shadow(stk_img, offset=(10, 14), shadow_color=(0, 0, 0, 45), blur_radius=8)
                overlay2.alpha_composite(stk_sh, (int(W2 * 0.76 - stk_sh.width // 2), int(H2 * 0.22 - stk_sh.height // 2)))

    radius = 280 if is_shorts else 320
    ring_thick = 48

    # Background track ring
    d2.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(218, 212, 202, 255), width=ring_thick)

    # Active progress arc
    prog = min(1.0, dt / 0.85)
    angle = int(360.0 * (pct / 100.0) * prog)
    if angle > 0:
        d2.arc((cx - radius, cy - radius, cx + radius, cy + radius), start=-90, end=-90 + angle, fill=(236, 120, 45, 255), width=ring_thick)

    # Center stat number (2x)
    num_txt = text_layer(stat_val, 120 if is_shorts else 140, (20, 24, 32))
    overlay2.alpha_composite(num_txt, (cx - num_txt.width // 2, cy - num_txt.height // 2))

    # Description Pill Below Ring (2x)
    if stat_desc:
        font_sz = 52 if is_shorts else 62
        desc_txt = text_layer(stat_desc, font_sz, INK)
        if desc_txt.width > (W2 // 2 - 80):
            desc_txt = text_layer(stat_desc, int(font_sz * 0.82), INK)
        dw = desc_txt.width + 64
        dh = desc_txt.height + 26
        dx0 = cx - dw // 2
        dy0 = cy + radius + 50
        d2.rounded_rectangle((dx0 + 8, dy0 + 8, dx0 + dw + 8, dy0 + dh + 8), radius=28, fill=(0, 0, 0, 45))
        d2.rounded_rectangle((dx0, dy0, dx0 + dw, dy0 + dh), radius=28, fill=(254, 250, 242, 255), outline=INK, width=6)
        overlay2.alpha_composite(desc_txt, (dx0 + 32, dy0 + 13))

    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    return fr


def draw_myth_stamp(token, dt, target_size=280):
    """Archetype 5: Animated Myth-Buster Verdict Stamp with 2x Supersampling."""
    target_size = max(180, min(600, target_size))
    sz2 = target_size * 2
    im2 = Image.new("RGBA", (sz2, sz2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(im2)

    is_x = ("x" in token or "false" in token or "myth" in token)
    col = (220, 35, 35, 255) if is_x else (35, 175, 75, 255)
    r = sz2 // 2 - 28

    # Double ring stamp outline at 2x
    d2.ellipse((28, 28, sz2 - 28, sz2 - 28), outline=col, width=16)
    d2.ellipse((38, 38, sz2 - 38, sz2 - 38), outline=(20, 24, 32, 200), width=4)

    cx, cy = sz2 // 2, sz2 // 2
    if is_x:
        off = r * 0.52
        d2.line((cx - off, cy - off, cx + off, cy + off), fill=col, width=32)
        d2.line((cx + off, cy - off, cx - off, cy + off), fill=col, width=32)
    else:
        d2.line((cx - r * 0.50, cy, cx - r * 0.10, cy + r * 0.45), fill=col, width=32)
        d2.line((cx - r * 0.10, cy + r * 0.45, cx + r * 0.55, cy - r * 0.45), fill=col, width=32)

    im = im2.resize((target_size, target_size), Image.LANCZOS)

    if dt < 0.16:
        p_stamp = dt / 0.16
        cur_scale = 1.35 - 0.35 * (p_stamp ** 2)
        nw = max(1, int(target_size * cur_scale))
        nh = max(1, int(target_size * cur_scale))
        im = im.resize((nw, nh), Image.LANCZOS)

    rot_angle = -8.0 if is_x else 6.0
    im = im.rotate(rot_angle, resample=Image.BILINEAR, expand=True)
    return im


def render_subtitles(fr, words_list, t, w, h, is_shorts):
    """Trending high-impact single-word kinetic subtitle display (Alex Hormozi / Viral Shorts style).
    Displays ONLY the exact word currently spoken by the voice, with zero preceding or trailing words.
    """
    cur_item = None
    for item in words_list:
        if item["start"] <= t <= item["end"] + 0.08:
            cur_item = item
            break
        elif item["start"] > t:
            break
            
    if cur_item is None:
        return # Natural pause / silence: keep screen clean

    txt = cur_item["word"].strip().upper()
    if not txt:
        return

    # Dynamic kinetic pop: first 80ms of word onset has a punchy spring
    dt = max(0.0, t - cur_item["start"])
    pop_scale = 1.0 + 0.16 * max(0.0, 1.0 - dt / 0.08)

    base_font_size = 110 if is_shorts else 88
    font_size = int(base_font_size * pop_scale)
    font = ImageFont.truetype(FONT_PATH, font_size)

    b = font.getbbox(txt)
    tw = max(1, b[2] - b[0])
    th = max(1, b[3] - b[1])

    pad_x, pad_y = 36, 18
    bw = tw + pad_x * 2
    bh = th + pad_y * 2

    sub_im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(sub_im)

    # Dynamic semantic color highlighting (Viral Trending Hormozi / Vox style)
    clean_w = txt.strip('.,!?:;"')
    GREEN_WORDS = {"MONEY", "GOLD", "MILLIONAIRE", "DOLLARS", "SURVIVE", "SURVIVAL", "FRESH", "RICH", "PROFIT", "WEEKS", "SUBSCRIBE"}
    RED_WORDS = {"DANGER", "PERIL", "STARVATION", "PANIC", "ROTTED", "BACTERIA", "WAR", "DEADLY", "IMPOSSIBLE", "BLACKOUT", "ATTACK"}
    CYAN_WORDS = {"ICE", "COLD", "FREEZING", "FROST", "SNOW", "WATER", "WIND", "PHYSICS", "SPACE", "VACUUM", "WINTER", "ZERO"}
    
    if clean_w in GREEN_WORDS or any(g in clean_w for g in ["DOLLAR", "MONEY", "PROFIT", "WIN"]):
        text_fill = (72, 235, 120, 255)
        border_col = (72, 235, 120, 240)
    elif clean_w in RED_WORDS or any(r in clean_w for r in ["DANGER", "DIE", "ROTT", "WAR", "PERIL"]):
        text_fill = (255, 75, 75, 255)
        border_col = (255, 75, 75, 240)
    elif clean_w in CYAN_WORDS or any(c in clean_w for c in ["ICE", "FROST", "SNOW", "FREEZ"]):
        text_fill = (75, 225, 255, 255)
        border_col = (75, 225, 255, 240)
    else:
        text_fill = (255, 215, 30, 255) # Classic golden-amber
        border_col = (255, 210, 30, 220)

    # Translucent dark pill with dynamically matched accent border
    d.rounded_rectangle((0, 0, bw, bh), radius=22, fill=(15, 12, 10, 220), outline=border_col, width=4)

    # Text coordinates
    tx = pad_x - b[0]
    ty = pad_y - b[1]

    # Heavy black drop-shadow & stroke with vibrant fill
    d.text((tx + 3, ty + 3), txt, font=font, fill=(0, 0, 0, 255), stroke_width=6, stroke_fill=(0, 0, 0, 255))
    d.text((tx, ty), txt, font=font, fill=text_fill, stroke_width=6, stroke_fill=(10, 8, 5, 255))

    # Eye-level position: dynamically calibrated via Reinforcement Learning policy
    pos_x = (w - bw) // 2
    spatial_policy = ACTIVE_RL_POLICY.get("rule_24_spatial_hierarchy", {})
    sub_y_short = spatial_policy.get("subtitles_center_y_shorts", 1180)
    sub_y_long = spatial_policy.get("subtitles_center_y_long", h - 150)
    pos_y = sub_y_short if is_shorts else sub_y_long

    if fr.mode != "RGBA":
        fr = fr.convert("RGBA")
    fr.alpha_composite(sub_im, (pos_x, pos_y))


def resolve_word_time(cue_raw, words_list, words_map, scene_t0=0.0, scene_t1=None):
    """Intelligently resolve spoken keyword timestamp from WORDS.tsv.
    Handles exact cues, multi-word stems (icecream -> ice), synonyms (fridge -> refrigerators),
    and relative scene windows. NEVER defaults to 0.0 unless scene actually starts at 0.0!
    """
    cue = cue_raw.strip().lstrip("+")
    if cue in words_map:
        return words_map[cue]

    cue_clean_num = cue.lstrip("@").replace(":", ".")
    try:
        return float(cue_clean_num)
    except ValueError:
        pass

    line_target = None
    search_term = cue.lower()
    if ":" in cue:
        prefix, _, search_term = cue.partition(":")
        line_target = prefix.lstrip("@")
    elif cue.startswith("@"):
        line_target = cue[1:]
        search_term = ""

    candidate_words = []
    if line_target:
        candidate_words = [w for w in words_list if w.get("line") == line_target or w.get("cue", "").startswith(line_target)]
    if not candidate_words and scene_t0 is not None:
        candidate_words = [w for w in words_list if scene_t0 <= w["start"] <= (scene_t1 or (scene_t0 + 10.0))]
    if not candidate_words:
        candidate_words = words_list

    if search_term:
        SYNONYMS = {
            "fridge": ["refrigerator", "refrigerators", "freezer", "electricity"],
            "icecream": ["ice", "cream", "sorbet", "sweet"],
            "pot": ["pots", "clay", "zeer", "terracotta"],
            "dome": ["yakhchal", "yakhchals", "vault", "structure", "wall"],
            "snow": ["alpine", "mountain", "runners", "ice"],
            "milk": ["camel", "fresh", "drink", "dairy"],
            "danger": ["spoil", "rot", "bacteria", "zone", "blackout", "peril"],
            "heat": ["desert", "sun", "hot", "degrees", "summer", "warm"],
            "cold": ["chill", "freeze", "frost", "subzero", "winter", "ice"],
            "persia": ["persian", "ancient", "kings", "desert"],
            "night": ["sky", "space", "stars", "dark", "radiation"],
            "sweat": ["evaporat", "cooling", "water", "sweating"],
            "sorbet": ["ice", "cream", "sweet", "royal"],
            "wall": ["canal", "shadow", "walls", "brick", "shade"],
            "sarooj": ["mortar", "egg", "ash", "goat", "hair"],
            "wine": ["chilled", "chalice", "goblet", "bottle", "drink"],
            "plow": ["wyeth", "plow", "harvest", "lake", "block"],
            "sawdust": ["pine", "sawdust", "insulat", "wood", "pack"],
            "icebox": ["zinc", "icebox", "wooden", "block", "kitchen"],
            "money": ["dollar", "cost", "price", "wealth", "expensive", "gold"],
        }

        # 1. Exact token match
        for w in candidate_words:
            w_txt = w["word"].lower().strip('.,!?":;')
            if w_txt == search_term:
                return w["start"]

        # 2. Substring match
        for w in candidate_words:
            w_txt = w["word"].lower().strip('.,!?":;')
            if (len(search_term) >= 3 and search_term in w_txt) or (len(w_txt) >= 3 and w_txt in search_term):
                return w["start"]

        # 3. Synonym dictionary match
        syns = SYNONYMS.get(search_term, [])
        for syn in syns:
            for w in candidate_words:
                w_txt = w["word"].lower().strip('.,!?":;')
                if syn in w_txt or w_txt in syn:
                    return w["start"]

        # 4. Fuzzy prefix stem (first 4 characters)
        if len(search_term) >= 4:
            stem = search_term[:4]
            for w in candidate_words:
                w_txt = w["word"].lower().strip('.,!?":;')
                if w_txt.startswith(stem):
                    return w["start"]

    # 5. Smart fallback: 0.6s after scene cut, NEVER 0.0
    if scene_t0 is not None:
        return scene_t0 + 0.6
    return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default="mix_pro.wav")
    ap.add_argument("--scenes", default="SCENES_HYBRID.tsv")
    ap.add_argument("--words", default="WORDS.tsv")
    ap.add_argument("--format", choices=["16:9", "9:16"], default="16:9")
    ap.add_argument("--out", default=None)
    ap.add_argument("--look", default=None, help="Color look: bright (default), warm, ink, painted, night")
    ap.add_argument("--kenburns", action="store_true", default=False, help="Enable subtle Ken Burns drift (default: disabled to preserve full uncropped image)")
    ap.add_argument("--captions", dest="subtitles", action="store_true", default=True, help="Render kinetic captions")
    ap.add_argument("--no-captions", dest="subtitles", action="store_false", help="Render without captions")
    ap.add_argument("--subtitles", action="store_true", default=True)
    ap.add_argument("--clip-seconds", type=float, default=None, help="Clip to first N seconds (e.g. short clip from long video)")
    ap.add_argument("--title", default=None, help="Header text for Shorts format")
    ap.add_argument("--scene-labels", action="store_true", default=False, help="Render floating scene label banners (default: False for clean modern sticker-focused visuals)")
    ap.add_argument("--header", action="store_true", default=False, help="Render top title banner in Shorts (default: False to avoid screen clutter)")
    ap.add_argument("--frame", type=float, default=None, help="Render a single still frame at timestamp T seconds and exit")
    ap.add_argument("--frame-out", default="frame.png", help="Output path for single still frame")
    args = ap.parse_args()

    # Determine look from STYLE.txt or CLI argument (default to 'bright' matching example target)
    active_look = args.look
    if not active_look:
        for sp in ["STYLE.txt", "../STYLE.txt"]:
            if os.path.exists(sp):
                try:
                    first = open(sp, encoding="utf-8").readline()
                    if first.lower().startswith("look:"):
                        active_look = first.split(":", 1)[1].strip()
                        break
                except Exception:
                    pass
    if not active_look or active_look not in LOOKS:
        active_look = "bright"
    set_look(active_look)

    slug = os.path.basename(os.getcwd())
    if args.title:
        title_text = args.title
    else:
        title_text = slug.replace("_", " ").replace("-", " ").upper()
        if os.path.exists("SCRIPT.md"):
            try:
                for line in open("SCRIPT.md", encoding="utf-8"):
                    line = line.strip()
                    if line.startswith("# "):
                        title_text = line[2:].strip().upper()
                        break
            except Exception:
                pass
    is_shorts = (args.format == "9:16")
    W, H = (1080, 1920) if is_shorts else (1920, 1080)
    out_file = args.out or (f"{slug}_shorts_9x16.mp4" if is_shorts else f"{slug}_master_16x9.mp4")

    # Load words
    words_map = {}
    words_list = []
    if os.path.exists(args.words):
        with open(args.words, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                cue_id = f"{r['line']}.{r['i']}" if "line" in r and "i" in r else r.get("cue", "")
                start_t = max(0.0, float(r["start"]))
                end_t = max(0.0, float(r["end"]))
                words_map[cue_id] = start_t
                line_id = r.get("line", "")
                if line_id:
                    if f"@{line_id}" not in words_map:
                        words_map[f"@{line_id}"] = start_t
                        words_map[line_id] = start_t
                    w_clean = r["word"].lower().strip('.,!?":;')
                    words_map[f"@{line_id}:{w_clean}"] = start_t
                    words_map[f"{line_id}:{w_clean}"] = start_t
                words_list.append({"cue": cue_id, "line": line_id, "start": start_t, "end": end_t, "word": r["word"]})
    words_list.sort(key=lambda x: x["start"])

    # High-impact spoken keywords for Dynamic Camera Shake (Rule 32)
    IMPACT_KEYWORDS = {
        "danger", "blackout", "peril", "starvation", "war", "explosion",
        "freezing", "collapse", "ruin", "crisis", "shock", "deadly", "zero"
    }
    impact_hit_times = set()
    for w in words_list:
        w_clean = w["word"].lower().strip('.,!?":;')
        if w_clean in IMPACT_KEYWORDS:
            impact_hit_times.add(w["start"])

    # Load shots metadata for space allocation (left/right/top)
    shots_space_map = {}
    if os.path.exists("SHOTS.tsv"):
        try:
            with open("SHOTS.tsv", encoding="utf-8") as sf:
                for sr in csv.DictReader(sf, delimiter="\t"):
                    sid = sr.get("id", "").strip().lstrip("0") or sr.get("id", "").strip()
                    shots_space_map[sid] = sr.get("space", "").strip().lower()
                    shots_space_map[sr.get("id", "").strip()] = sr.get("space", "").strip().lower()
        except Exception:
            pass

    # Load scenes
    scenes = []
    with open(args.scenes, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            cue = r["cue"].strip()
            if not cue or cue.startswith("#"):
                continue
            if cue.startswith("+"):
                # overlay row with smart word timestamp resolution
                last_t0 = scenes[-1]["t0"] if scenes else 0.0
                t_ov = resolve_word_time(cue, words_list, words_map, last_t0)
                if scenes:
                    scenes[-1]["ov"].append({
                        "t": t_ov,
                        "img": r["img"].strip(),
                        "text": r.get("text", "").strip(),
                        "pos": r.get("pos", "").strip() or "auto",
                        "extra": r.get("extra", "").strip() or "pop"
                    })
            else:
                t0 = words_map.get(cue, float(cue) if cue.replace(".", "", 1).isdigit() else 0.0)
                img_clean = r["img"].strip()
                shot_basename = os.path.basename(img_clean).split(".")[0]
                shot_space = r.get("space", "").strip().lower() or shots_space_map.get(shot_basename, "")
                scenes.append({
                    "t0": t0,
                    "img": img_clean,
                    "text": r.get("text", "").strip(),
                    "pos": r.get("pos", "").strip(),
                    "extra": r.get("extra", "").strip(),
                    "space": shot_space,
                    "ov": []
                })

    scenes.sort(key=lambda s: s["t0"])
    
    # Audio duration
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=noprint_wrappers=1:nokey=1", args.audio],
                           capture_output=True, text=True)
    audio_dur = float(probe.stdout.strip()) if probe.stdout.strip() else (scenes[-1]["t0"] + 3.0)
    total = min(audio_dur, args.clip_seconds) if args.clip_seconds else audio_dur

    for i in range(len(scenes)):
        scenes[i]["t1"] = scenes[i + 1]["t0"] if i + 1 < len(scenes) else total

    # Robust Overlay Re-Parenting Gate:
    # Guarantees that every overlay belongs to the scene active during its timestamp t_ov,
    # preventing overlays from ever being orphaned or lost if placed at the bottom of the TSV.
    all_overlays = []
    for sc in scenes:
        all_overlays.extend(sc["ov"])
        sc["ov"] = []

    for ov in all_overlays:
        t_target = ov["t"]
        parent = None
        for sc in scenes:
            if sc["t0"] - 0.05 <= t_target < sc["t1"]:
                parent = sc
                break
        if not parent and scenes:
            preceding = [sc for sc in scenes if sc["t0"] <= t_target]
            parent = max(preceding, key=lambda s: s["t0"]) if preceding else scenes[0]
        if parent:
            parent["ov"].append(ov)

    # Pre-calculate smooth exit pre-emption across timeline (Fix 4: Anti-Crowding)
    # Shorts (9:16) Max 1 active sticker; Long (16:9) Max 2 active stickers.
    all_overlays.sort(key=lambda o: o["t"])
    max_active_cap = 1 if is_shorts else 2
    for i in range(len(all_overlays)):
        if i + max_active_cap < len(all_overlays):
            next_t = all_overlays[i + max_active_cap]["t"]
            gap = max(0.1, next_t - all_overlays[i]["t"])
            all_overlays[i]["preempt_dur"] = gap

    for sc in scenes:
        sc["ov"].sort(key=lambda o: o["t"])

    # Pre-cache scene images and enforce layout purity guard
    img_cache = {}
    bg_cache = {}
    for s in scenes:
        p = s["img"]
        if p != "card" and os.path.exists(p) and p not in img_cache:
            im = Image.open(p).convert("RGBA")
            img_cache[p] = im
            if is_shorts:
                # Vertical layout guard check (reject non-vertical or letterboxed art)
                ratio = im.width / im.height
                if ratio > 0.65 or im.width >= im.height:
                    sys.exit(f"❌ [Render Guard Error] Scene image '{p}' is non-vertical ({im.width}x{im.height}, ratio={ratio:.2f} > 0.65)! Shorts must have dedicated native 9:16 portrait art.")

                # Pre-calculate blurred background for 9:16
                scale_bg = max(W / im.width, H / im.height)
                bg_w, bg_h = int(im.width * scale_bg), int(im.height * scale_bg)
                bg = im.resize((bg_w, bg_h), Image.BILINEAR)
                bg = bg.crop(((bg_w - W) // 2, (bg_h - H) // 2, (bg_w - W) // 2 + W, (bg_h - H) // 2 + H))
                bg = bg.filter(ImageFilter.GaussianBlur(32))
                # Darken background slightly for contrast
                dark = Image.new("RGBA", (W, H), (20, 16, 12, 130))
                bg.alpha_composite(dark)
                bg_cache[p] = bg

    # Pre-build stage card for Shorts
    if is_shorts:
        stage_w, stage_h = 980, 552
        stage_mask = Image.new("L", (stage_w, stage_h), 0)
        ImageDraw.Draw(stage_mask).rounded_rectangle((0, 0, stage_w, stage_h), radius=20, fill=255)
        stage_card_base = Image.new("RGBA", (stage_w + 24, stage_h + 24), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stage_card_base)
        sd.rounded_rectangle((8, 8, stage_w + 16, stage_h + 16), radius=24, fill=(0, 0, 0, 80))
        sd.rounded_rectangle((4, 4, stage_w + 20, stage_h + 20), radius=24, fill=PAPER + (255,), outline=INK, width=6)

    def draw_youtube_outro_slate(fr, W, H, dt):
        """Renders broadcast YouTube End Screen Slate with designated 16:9 video boxes and subscribe bubble."""
        d = ImageDraw.Draw(fr)
        slate_dark = Image.new("RGBA", (W, H), (14, 18, 26, 235))
        fr.alpha_composite(slate_dark)

        # Header
        header_im = text_layer("THANKS FOR WATCHING", 52, (255, 230, 80))
        fr.alpha_composite(header_im, ((W - header_im.width) // 2, 85))

        sub_im = text_layer("WATCH NEXT & SUBSCRIBE", 30, (220, 230, 245))
        fr.alpha_composite(sub_im, ((W - sub_im.width) // 2, 155))

        box_w, box_h = 610, 344
        box_y = 250
        left_x = 120
        right_x = W - box_w - 120

        p_card = min(1.0, dt / 0.5)
        q_card = spring_p(p_card)
        card_alpha = int(min(1.0, dt / 0.3) * 255)

        # Left Box
        d.rounded_rectangle((left_x + 6, box_y + 6, left_x + box_w + 6, box_y + box_h + 6), radius=20, fill=(0, 0, 0, 100))
        d.rounded_rectangle((left_x, box_y, left_x + box_w, box_y + box_h), radius=20, fill=(28, 34, 46, 240), outline=(255, 215, 30, card_alpha), width=3)
        lbl_left = text_layer("▶ WATCH NEXT", 36, (255, 215, 30))
        fr.alpha_composite(lbl_left, (left_x + (box_w - lbl_left.width) // 2, box_y + (box_h - lbl_left.height) // 2))

        # Right Box
        d.rounded_rectangle((right_x + 6, box_y + 6, right_x + box_w + 6, box_y + box_h + 6), radius=20, fill=(0, 0, 0, 100))
        d.rounded_rectangle((right_x, box_y, right_x + box_w, box_y + box_h), radius=20, fill=(28, 34, 46, 240), outline=(75, 225, 255, card_alpha), width=3)
        lbl_right = text_layer("★ BEST FOR YOU", 36, (75, 225, 255))
        fr.alpha_composite(lbl_right, (right_x + (box_w - lbl_right.width) // 2, box_y + (box_h - lbl_right.height) // 2))

        # Center Subscribe Circle
        cx_sub = W // 2
        cy_sub = box_y + box_h // 2
        r_sub = max(10, int(85 * q_card))
        d.ellipse((cx_sub - r_sub + 4, cy_sub - r_sub + 4, cx_sub + r_sub + 4, cy_sub + r_sub + 4), fill=(0, 0, 0, 80))
        d.ellipse((cx_sub - r_sub, cy_sub - r_sub, cx_sub + r_sub, cy_sub + r_sub), fill=(235, 45, 45, 245), outline=(255, 255, 255, 255), width=4)
        sub_txt = text_layer("SUB", 32, (255, 255, 255))
        fr.alpha_composite(sub_txt, (cx_sub - sub_txt.width // 2, cy_sub - sub_txt.height // 2))

        bot_im = text_layer("TAP THE CARDS TO CONTINUE THE STORY", 24, (180, 195, 215))
        fr.alpha_composite(bot_im, ((W - bot_im.width) // 2, H - 110))

    def draw_shorts_subscribe_callout(fr, W, H, dt):
        """Draws floating subscribe callout pill in lower safe area during Shorts closing."""
        p = min(1.0, dt / 0.4)
        d = ImageDraw.Draw(fr)
        pulse = 1.0 + 0.04 * math.sin(dt * 8.0)
        pill_w = int(620 * pulse)
        pill_h = int(90 * pulse)
        pill_x = (W - pill_w) // 2
        pill_y = 1360
        d.rounded_rectangle((pill_x + 4, pill_y + 4, pill_x + pill_w + 4, pill_y + pill_h + 4), radius=24, fill=(0, 0, 0, 90))
        d.rounded_rectangle((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h), radius=24, fill=(255, 215, 30, 245), outline=(20, 24, 32, 255), width=4)
        txt = text_layer("🔔 SUBSCRIBE FOR MORE", 38, (20, 24, 32))
        fr.alpha_composite(txt, ((W - txt.width) // 2, pill_y + (pill_h - txt.height) // 2 - 2))

    def compose_frame_at(t):
        si = 0
        while si + 1 < len(scenes) and t >= scenes[si + 1]["t0"]:
            si += 1
        sc = scenes[si]
        t0 = sc["t0"]
        t1 = sc["t1"]
        dt = max(0.0, t - t0)
        dt_scene = dt
        dur = max(0.1, t1 - t0)
        u = min(1.0, dt / dur)

        img_path = sc["img"]
        text = sc["text"]
        pos = sc["pos"]
        extra = sc["extra"]
        # Check extra, pos, and space columns for transition & VFX directives (Schema Robustness Gate)
        trans_type = f"{sc.get('extra', '')} {sc.get('pos', '')} {sc.get('space', '')}".strip().lower()

        is_vertical_img = is_shorts
        is_landscape_img = not is_shorts

        # Collect any active stickers and stamps for archetype compositing
        paired_stk = None
        left_stk = None
        right_stk = None
        left_stmp = None
        right_stmp = None
        natively_consumed_indices = set()

        for idx, o in enumerate(sc.get("ov", [])):
            o_img = o.get("img", "").strip()
            o_pos = str(o.get("pos", "")).lower()
            if t < o.get("t", 0.0):
                continue
            if o_img in ("stamp_x", "stamp_false", "stamp_myth"):
                if "left" in o_pos or not right_stmp:
                    left_stmp = o_img
                else:
                    right_stmp = o_img
                natively_consumed_indices.add(idx)
            elif o_img in ("stamp_check", "stamp_true"):
                if "right" in o_pos or not left_stmp:
                    right_stmp = o_img
                else:
                    left_stmp = o_img
                natively_consumed_indices.add(idx)
            elif o_img not in ("tag", "count") and not o_img.startswith("bars:"):
                res_path = resolve_sticker_path(o_img)
                if res_path:
                    if "left" in o_pos:
                        left_stk = res_path
                        natively_consumed_indices.add(idx)
                    elif "right" in o_pos:
                        right_stk = res_path
                        natively_consumed_indices.add(idx)
                    elif not paired_stk:
                        paired_stk = res_path
                        natively_consumed_indices.add(idx)
                    elif not left_stk:
                        left_stk = res_path
                        natively_consumed_indices.add(idx)
                    elif not right_stk:
                        right_stk = res_path
                        natively_consumed_indices.add(idx)

        if not paired_stk and sc.get("space"):
            res_sp = resolve_sticker_path(sc["space"])
            if res_sp:
                paired_stk = res_sp

        # Background composition: 6-Archetype Visual Variety Engine
        if img_path in ("card_stat", "card_phrase") or img_path.startswith("card_"):
            fr = draw_card_stat(W, H, text, is_shorts=is_shorts, dt=dt_scene, sticker_im=paired_stk)
        elif img_path in ("split_compare", "split_contrast") or img_path.startswith("split_"):
            fr = draw_split_compare(W, H, text, is_shorts=is_shorts, dt=dt_scene,
                                   left_sticker=left_stk, right_sticker=right_stk,
                                   left_stamp=left_stmp, right_stamp=right_stmp)
        elif img_path in ("bar_timeline", "timeline") or img_path.startswith("timeline_"):
            fr = draw_data_timeline(W, H, text, is_shorts=is_shorts, dt=dt_scene, accent_sticker=paired_stk)
        elif img_path in ("stat_pie", "stat_ring") or img_path.startswith("stat_"):
            fr = draw_stat_pie(W, H, text, is_shorts=is_shorts, dt=dt_scene, accent_sticker=paired_stk)
        elif img_path == "card" or img_path not in img_cache:
            fr = card_bg(W, H).convert("RGBA")
        else:
            raw = img_cache[img_path]

            is_vertical_img = (raw.height >= raw.width * 1.15)
            is_landscape_img = (raw.width >= raw.height * 1.15)

            # Virtual Multi-Cam Cuts (Archetype 2: 1.32x crop, 1.38x zoom, pan_left, pan_right)
            is_zoom_tight = "zoom_in_tight" in trans_type
            is_crop_focus = "crop_focus" in trans_type
            is_pan_l = "pan_left" in trans_type
            is_pan_r = "pan_right" in trans_type

            if is_shorts:
                if is_vertical_img:
                    # Native 9:16 Vertical Art from Flow (e.g. 1536x2752):
                    if is_zoom_tight:
                        cw = int(raw.width / 1.38)
                        ch = int(raw.height / 1.38)
                        cx = (raw.width - cw) // 2
                        cy = (raw.height - ch) // 2
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    elif is_crop_focus:
                        cw = int(raw.width / 1.32)
                        ch = int(raw.height / 1.32)
                        cx = (raw.width - cw) // 2
                        cy = max(0, min(raw.height - ch, int((raw.height - ch) * 0.38)))
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    elif is_pan_l:
                        cw = int(raw.width * 0.78)
                        ch = int(raw.height * 0.78)
                        cx = 0
                        cy = (raw.height - ch) // 2
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    elif is_pan_r:
                        cw = int(raw.width * 0.78)
                        ch = int(raw.height * 0.78)
                        cx = raw.width - cw
                        cy = (raw.height - ch) // 2
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    elif args.kenburns:
                        scale = 1.0 + 0.04 * np.sin(si * 1.7) * u
                        dx = int(np.sin(si * 2.3) * 12 * u)
                        dy = int(np.cos(si * 1.9) * 8 * u)
                        cw = max(1, int(raw.width / scale))
                        ch = max(1, int(raw.height / scale))
                        cx = max(0, min(raw.width - cw, (raw.width - cw) // 2 + dx))
                        cy = max(0, min(raw.height - ch, (raw.height - ch) // 2 + dy))
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    else:
                        fr = raw.resize((W, H), Image.LANCZOS)
                elif raw.width == 1 and raw.height == 1:
                    fr = card_bg(W, H).convert("RGBA")
                else:
                    # Landscape 16:9 image displayed inside vertical 9:16 Shorts frame
                    # Shows the complete 16:9 image inside a framed stage card, zero crop!
                    cached_bg = bg_cache.get(img_path)
                    fr = cached_bg.copy() if cached_bg else card_bg(W, H).convert("RGBA")
                    stage_img = raw.resize((stage_w, stage_h), Image.LANCZOS)
                    stage_img.putalpha(stage_mask)
                    stage_card = stage_card_base.copy()
                    stage_card.alpha_composite(stage_img, (12, 12))
                    fr.alpha_composite(stage_card, ((W - stage_w - 24) // 2, 750))
            else:
                # 16:9 Widescreen Master Format
                if is_landscape_img or not is_vertical_img:
                    # Native 16:9 Landscape Art from Flow (e.g. 2752x1536):
                    if is_zoom_tight:
                        cw = int(raw.width / 1.38)
                        ch = int(raw.height / 1.38)
                        cx = (raw.width - cw) // 2
                        cy = (raw.height - ch) // 2
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    elif is_crop_focus:
                        cw = int(raw.width / 1.32)
                        ch = int(raw.height / 1.32)
                        cx = (raw.width - cw) // 2
                        cy = max(0, min(raw.height - ch, int((raw.height - ch) * 0.40)))
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    elif is_pan_l:
                        cw = int(raw.width * 0.72)
                        ch = int(raw.height * 0.72)
                        cx = 0
                        cy = (raw.height - ch) // 2
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    elif is_pan_r:
                        cw = int(raw.width * 0.72)
                        ch = int(raw.height * 0.72)
                        cx = raw.width - cw
                        cy = (raw.height - ch) // 2
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    elif args.kenburns:
                        scale = 1.0 + 0.04 * np.sin(si * 1.7) * u
                        dx = int(np.sin(si * 2.3) * 12 * u)
                        dy = int(np.cos(si * 1.9) * 8 * u)
                        cw = max(1, int(raw.width / scale))
                        ch = max(1, int(raw.height / scale))
                        cx = max(0, min(raw.width - cw, (raw.width - cw) // 2 + dx))
                        cy = max(0, min(raw.height - ch, (raw.height - ch) // 2 + dy))
                        fr = raw.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
                    else:
                        fr = raw.resize((W, H), Image.LANCZOS)
                else:
                    # Vertical 9:16 image displayed inside landscape 16:9 frame:
                    # Pillarboxed with blurred background, zero crop!
                    cached_bg = bg_cache.get(img_path)
                    fr = cached_bg.copy() if cached_bg else card_bg(W, H).convert("RGBA")
                    pillar_h = H - 80
                    pillar_w = int(pillar_h * (raw.width / raw.height))
                    pillar_img = raw.resize((pillar_w, pillar_h), Image.LANCZOS)
                    fr.alpha_composite(pillar_img, ((W - pillar_w) // 2, 40))

        # Subtle paper texture and vignette
        if fr.mode != "RGBA":
            fr = fr.convert("RGBA")

        # Rule 32: Dynamic Camera Shake & Physical Weight
        shake_dx, shake_dy = 0, 0

        # Explicit shake or rumble in scene extra
        if "shake" in trans_type and dt_scene < 0.35:
            intensity = (1.0 - dt_scene / 0.35) * 12.0
            shake_dx += int(np.sin(dt_scene * 75.0) * intensity)
            shake_dy += int(np.cos(dt_scene * 90.0) * intensity)
        elif "rumble" in trans_type:
            shake_dx += int(np.sin(t * 30.0) * 2.8)
            shake_dy += int(np.cos(t * 35.0) * 2.8)

        # High-Impact Spoken Word hits
        for impact_t in impact_hit_times:
            dt_imp = t - impact_t
            if 0.0 <= dt_imp <= 0.22:
                intensity = (1.0 - dt_imp / 0.22) * 8.0
                shake_dx += int(np.sin(dt_imp * 75.0) * intensity)
                shake_dy += int(np.cos(dt_imp * 90.0) * intensity)
                break
        if shake_dx != 0 or shake_dy != 0:
            fr = fr.transform(fr.size, Image.AFFINE, (1, 0, shake_dx, 0, 1, shake_dy))

        # Zoom Punch Transition (1.06x snap to 1.00x)
        if "zoom_punch" in trans_type and dt_scene < 0.22:
            scale_zp = 1.0 + 0.06 * (1.0 - dt_scene / 0.22)
            cw = int(W / scale_zp)
            ch = int(H / scale_zp)
            fr = fr.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)

        # 4-7s Dynamic Pattern Interrupt: Slow Subtle Cinematic Push-in on longer holds (> 3.0s)
        # Prevents static visual numbness and resets viewer attention span without jarring movement
        elif dt_scene > 3.0:
            scale_pi = 1.0 + 0.045 * min(1.0, (dt_scene - 3.0) / 4.0)
            cw = int(W / scale_pi)
            ch = int(H / scale_pi)
            fr = fr.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)

        # Black & White / Grayscale / Historical Tragedy
        if "bw" in trans_type or "grayscale" in trans_type or "monochrome" in trans_type:
            gray = fr.convert("L").convert("RGBA")
            fr = Image.blend(fr, gray, 0.92)

        # Danger Crimson / Blood Vignette
        if "blood" in trans_type or "danger" in trans_type or "hazard" in trans_type:
            pulse_v = 0.65 + 0.35 * np.sin(dt_scene * 7.5)
            danger_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dd = ImageDraw.Draw(danger_layer)
            border_w = 60 if is_shorts else 80
            for i in range(border_w):
                alpha_v = int((border_w - i) / border_w * 170 * pulse_v)
                dd.rectangle((i, i, W - i, H - i), outline=(210, 25, 25, alpha_v), width=1)
            fr.alpha_composite(danger_layer)

        # Ice / Frost Cyan Vignette
        if "ice" in trans_type or "frost" in trans_type or "cold" in trans_type:
            frost_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fd = ImageDraw.Draw(frost_layer)
            border_w = 60 if is_shorts else 80
            for i in range(border_w):
                alpha_v = int((border_w - i) / border_w * 160)
                fd.rectangle((i, i, W - i, H - i), outline=(60, 210, 255, alpha_v), width=1)
            fr.alpha_composite(frost_layer)

        # Scene Transition VFX:
        # Smooth cinematic crossfades, warm reveal flashes, and punch zooms
        dt_scene = t - t0
        if dt_scene < 0.24 and si > 0:
            if "fade" in trans_type or "crossfade" in trans_type:
                prev_img_path = scenes[si - 1]["img"]
                if prev_img_path != "card" and prev_img_path in img_cache:
                    prev_raw = img_cache[prev_img_path]
                    prev_fr = prev_raw.resize((W, H), Image.LANCZOS) if prev_raw.size != (W, H) else prev_raw
                    blend_alpha = min(1.0, max(0.0, dt_scene / 0.20))
                    fr = Image.blend(prev_fr.convert("RGBA"), fr, blend_alpha)
            elif "flash" in trans_type:
                flash_p = max(0.0, 1.0 - dt_scene / 0.12)
                flash_layer = Image.new("RGBA", (W, H), (255, 252, 240, int(flash_p * 180)))
                fr.alpha_composite(flash_layer)

        # Label Deduplication & Clash Check:
        # Scene heading text label: Suppressed on standard scenes so stickers, art, and captions remain uncluttered.
        # Only displayed on dedicated full-screen title/chapter cards (img_path == "card") or if explicitly requested.
        active_tags = {o["text"].strip().upper() for o in sc["ov"] if o.get("text")}
        is_archetype_card = (img_path in ("card", "card_stat", "card_phrase", "split_compare", "split_contrast",
                                          "bar_timeline", "timeline", "stat_pie", "stat_ring") or
                             img_path.startswith(("card_", "split_", "timeline_", "stat_")))
        if text and (img_path == "card" or (args.scene_labels and not is_archetype_card)):
            scene_lbl = text.strip().upper()
            is_dup = False
            for atag in active_tags:
                if scene_lbl == atag or scene_lbl in atag or atag in scene_lbl:
                    is_dup = True
                    break
            # In Shorts, suppress scene tag during first 2.5s if opening title header is active!
            if is_shorts and t <= 2.5:
                is_dup = True
            if not is_dup:
                draw_label(fr, text, "big" if img_path == "card" else (pos or "auto"), W, H, is_shorts)

        # Dynamic Bars
        if extra.startswith("bars:"):
            draw_bars(fr, extra[5:], t - t0, W, H, is_shorts)

        # Overlays / Stickers (Intelligent positioning, boundary clamping, and anti-collision)
        active_overlays = []
        for o_idx, o in enumerate(sc["ov"]):
            if o_idx in natively_consumed_indices:
                continue
            dt = t - o["t"]
            if dt >= 0:
                # Rule 29 & Rule 70: Dynamic & Adaptive Sticker Lifetime
                # In Shorts: 1.8s - 2.2s fast punch
                # In Long-Form: Adaptive hold (3.5s - 5.5s) to eliminate empty screens during long explanations
                sync_policy = ACTIVE_RL_POLICY.get("rule_29_sticker_synchronization", {})
                rl_shorts_dur = sync_policy.get("shorts_sticker_ttl_sec", 1.8)
                rl_long_dur = sync_policy.get("long_sticker_ttl_sec", 3.5)
                scene_len = max(0.1, t1 - t0)
                default_dur = rl_shorts_dur if is_shorts else min(5.5, max(rl_long_dur, scene_len * 0.70))
                custom_dur = None
                for part in str(o.get("extra", "")).split("|"):
                    if part.startswith("dur:"):
                        try:
                            custom_dur = float(part[4:])
                        except Exception:
                            pass
                dur = custom_dur if custom_dur is not None else default_dur
                if "preempt_dur" in o:
                    dur = min(dur, o["preempt_dur"])
                if dt <= dur:
                    active_overlays.append((o_idx, o, dt, dur))

        # Enforce strict active sticker cap (Fix 4: Anti-Crowding)
        # Shorts (9:16) Max 1 active sticker; Long (16:9) Max 2 active stickers.
        max_active_stickers = 1 if is_shorts else 2
        if len(active_overlays) > max_active_stickers:
            active_overlays = active_overlays[-max_active_stickers:]

        occupied_boxes = []

        for o_idx, o, dt, dur in active_overlays:
            p = min(1.0, dt / 0.35)
            q = spring_p(p)
            alpha = min(1.0, dt / 0.18)

            # Clean exit animation during final 0.22s of sticker lifetime (smooth pre-emption)
            exit_window = min(0.22, max(0.05, dur * 0.45))
            time_left = dur - dt
            exit_p = 1.0
            if time_left < exit_window:
                exit_p = max(0.0, time_left / exit_window)
                q = q * (exit_p ** 1.6)
                alpha = min(alpha, exit_p)

            pos_str = str(o.get("pos", "")).strip().lower()
            default_fh = 0.22 if is_shorts else 0.28
            fx, fy, fh = 0.5, 0.38, default_fh

            if not pos_str or pos_str.startswith("auto"):
                # Intelligent quadrant docking based on scene's allocated free space
                shot_space = sc.get("space", "").lower()
                if "left" in shot_space:
                    fx, fy = (0.24, 0.38) if is_shorts else (0.22, 0.38)
                elif "right" in shot_space:
                    fx, fy = (0.68, 0.38) if is_shorts else (0.78, 0.38)
                elif "top" in shot_space:
                    fx, fy = 0.50, 0.34
                else:
                    fx = (0.68 if (o_idx % 2 == 0) else 0.24) if is_shorts else (0.78 if (o_idx % 2 == 0) else 0.22)
                    fy = 0.38
            elif "top-right" in pos_str or "tr" in pos_str:
                fx, fy = (0.68, 0.34) if is_shorts else (0.78, 0.28)
            elif "top-left" in pos_str or "tl" in pos_str:
                fx, fy = (0.24, 0.34) if is_shorts else (0.22, 0.28)
            elif "bottom-right" in pos_str or "br" in pos_str:
                fx, fy = (0.68, 0.44) if is_shorts else (0.78, 0.50)
            elif "bottom-left" in pos_str or "bl" in pos_str:
                fx, fy = (0.24, 0.44) if is_shorts else (0.22, 0.50)
            elif "right" in pos_str or pos_str == "r":
                fx, fy = (0.68, 0.38) if is_shorts else (0.78, 0.38)
            elif "left" in pos_str or pos_str == "l":
                fx, fy = (0.24, 0.38) if is_shorts else (0.22, 0.38)
            elif "top" in pos_str or pos_str == "t":
                fx, fy = 0.50, 0.34
            else:
                try:
                    parts = [float(x.strip()) for x in pos_str.split(",") if x.strip()]
                    if len(parts) >= 2:
                        fx, fy = parts[0], parts[1]
                        if len(parts) >= 3:
                            fh = parts[2]
                except Exception:
                    fx, fy, fh = 0.5, 0.38, default_fh

            # Anti-Occlusion Guard: Center character protection on scene images
            if img_path != "card":
                if 0.35 <= fx <= 0.65 and 0.32 <= fy <= 0.65:
                    fx, fy = (0.68, 0.36) if is_shorts else (0.78, 0.32)

            # Subtitle zone clearance
            if not is_shorts and fy > 0.52:
                fy = 0.50
            elif is_shorts and fy > 0.45:
                fy = 0.43

            hh = int(fh * (stage_h if (is_shorts and not is_vertical_img) else H))
            o_img = o["img"]

            item_im = None
            lbl_im = None
            if o_img == "count":
                num_str, _, cap = o["text"].partition("|")
                try:
                    target_num = float(num_str.replace(",", ""))
                except Exception:
                    target_num = 100.0
                v = target_num * (1.0 - (1.0 - min(1.0, dt / 0.85)) ** 3)
                disp_num = f"{int(round(v)):,}" if target_num >= 1000 else str(int(round(v)))
                item_im = tag_image(f"{disp_num}|{cap}" if cap else disp_num, max(38, hh // 4))
            elif o_img == "tag":
                item_im = tag_image(o["text"], max(36, hh // 4))
            elif o_img.startswith("bars:"):
                draw_bars(fr, o_img[5:], dt, W, H, is_shorts)
                continue
            elif o_img in ("stamp_x", "stamp_check", "stamp_false", "stamp_true", "stamp_myth"):
                item_im = draw_myth_stamp(o_img, dt, target_size=max(220, hh))
                if o.get("text"):
                    lbl_im = tag_image(o["text"], 34 if is_shorts else 40)
            elif os.path.exists(o_img):
                item_im = sticker(o_img, hh)
                if o.get("text"):
                    lbl_im = tag_image(o["text"], 34 if is_shorts else 40)
            else:
                # Bulletproof multi-directory and semantic registry resolution
                resolved_p = None
                name_base = os.path.basename(o_img)
                name_no_ext = os.path.splitext(name_base)[0]
                cands = [
                    o_img,
                    o_img + ".png" if not o_img.endswith(".png") else o_img,
                    os.path.join("elements", "cut", f"{name_no_ext}.png"),
                    os.path.join("elements", "cut", name_base),
                    os.path.join("..", "elements", "cut", f"{name_no_ext}.png"),
                    os.path.join("..", "elements", "cut", name_base),
                    os.path.join("..", "short", "elements", "cut", f"{name_no_ext}.png"),
                    os.path.join("..", "long", "elements", "cut", f"{name_no_ext}.png"),
                ]
                for cp in cands:
                    if os.path.exists(cp) and os.path.getsize(cp) > 500:
                        resolved_p = cp
                        break
                if not resolved_p:
                    try:
                        import asset_registry
                        p_root = asset_registry.resolve_project_root(os.getcwd())
                        reg_m = asset_registry.find_reusable_sticker(name_no_ext, p_root)
                        if reg_m and os.path.exists(reg_m["path"]):
                            resolved_p = reg_m["path"]
                    except Exception:
                        pass

                if resolved_p:
                    item_im = sticker(resolved_p, hh)
                    if o.get("text"):
                        lbl_im = tag_image(o["text"], 34 if is_shorts else 40)

            if item_im is None:
                continue

            # Phase 2 Spatial & Sticker Placement Intelligence
            sub_top_y = (1180 - 60) if is_shorts else (H - 150 - 50)
            target_cx, target_cy, auto_q = calculate_intelligent_sticker_anchor(
                fr, int(item_im.width * q), int(item_im.height * q), pos_str, is_shorts, W, H, occupied_boxes, sub_top_y
            )

            nw = max(1, int(item_im.width * q * auto_q))
            nh = max(1, int(item_im.height * q * auto_q))
            scaled_im = item_im.resize((nw, nh), Image.BILINEAR)

            cx = target_cx
            cy = target_cy

            # Strict Restraint Rule: If close to safe margins, restrain displacement
            spatial_policy = ACTIVE_RL_POLICY.get("rule_24_spatial_hierarchy", {})
            right_margin = spatial_policy.get("shorts_margin_right_px", 220) if is_shorts else 54
            min_x = nw // 2 + (48 if is_shorts else 54)
            max_x = W - nw // 2 - right_margin
            min_y = nh // 2 + (200 if is_shorts else 80)
            max_y = (sub_top_y - (140 if is_shorts else 80)) - nh // 2
            if max_y < min_y:
                max_y = min_y + 40

            near_boundary = (cx + nw // 2 > max_x - 30) or (cy + nh // 2 > max_y - 30)

            ov_extra = str(o.get("extra", "")).strip().lower()
            if "drop" in ov_extra or "slam" in ov_extra:
                cy -= int((80 if near_boundary else 160) * (1.0 - p)**2)
            elif "slide_left" in ov_extra:
                cx -= int((80 if near_boundary else 160) * (1.0 - p)**2)
            elif "slide_right" in ov_extra:
                cx += int((80 if near_boundary else 160) * (1.0 - p)**2)
            
            if p >= 1.0 and time_left >= 0.28:
                hover_amp = 2.0 if near_boundary else 4.0
                hover_dy = int(np.sin((dt - 0.38) * 2.0 + o_idx * 1.2) * hover_amp)
                cy += hover_dy
            elif time_left < 0.28:
                cy -= int((1.0 - exit_p) * 12)

            # Strict bounds clamp
            cx = max(min_x, min(cx, max_x))
            cy = max(min_y, min(cy, max_y))

            occupied_boxes.append((cx - nw // 2, cy - nh // 2, cx + nw // 2, cy + nh // 2))

            # Apply opacity fade (smooth entrance fade-in and exit fade-out)
            if alpha < 0.999:
                bands = list(scaled_im.split())
                bands[3] = bands[3].point(lambda a: int(a * max(0.0, min(1.0, alpha))))
                scaled_im = Image.merge("RGBA", bands)
                if lbl_im:
                    lbl_bands = list(lbl_im.split())
                    lbl_bands[3] = lbl_bands[3].point(lambda a: int(a * max(0.0, min(1.0, alpha))))
                    lbl_im = Image.merge("RGBA", lbl_bands)

            fr.alpha_composite(scaled_im, (cx - nw // 2, cy - nh // 2))

            if lbl_im:
                lbl_y = cy + nh // 2 + 6
                # If label would collide with subtitle zone, place it ABOVE the sticker instead!
                if lbl_y + lbl_im.height > (1040 if is_shorts else 860):
                    lbl_y = cy - nh // 2 - lbl_im.height - 6
                lbl_x = max(min_x - nw // 2, min(W - lbl_im.width - right_margin, cx - lbl_im.width // 2))
                fr.alpha_composite(lbl_im, (lbl_x, lbl_y))

        # Shorts Header & Progress Bar
        if is_shorts:
            d = ImageDraw.Draw(fr)
            prog_w = int(W * (t / total))
            d.rectangle((0, 0, prog_w, 8), fill=(236, 140, 50, 255))
            # Display title banner ONLY if explicitly requested via --header
            if args.header and t <= 2.5:
                header_txt = text_layer(title_text, 34, INK)
                hp_w, hp_h = header_txt.width + 36, header_txt.height + 12
                hp_x = (W - hp_w) // 2
                d.rounded_rectangle((hp_x, 190, hp_x + hp_w, 190 + hp_h), radius=16, fill=PAPER + (240,), outline=INK, width=3)
                fr.alpha_composite(header_txt, ((W - header_txt.width) // 2, 196))

        # Kinetic Subtitles
        if args.subtitles:
            render_subtitles(fr, words_list, t, W, H, is_shorts)

        # Professional Outro Slate for 16:9 Long-Form
        if not is_shorts and (img_path == "outro" or (t >= total - 12.0 and total >= 45.0)):
            dt_outro = max(0.0, t - (total - 12.0) if img_path != "outro" else (t - t0))
            draw_youtube_outro_slate(fr, W, H, dt_outro)

        # Shorts Ending Follow Callout
        if is_shorts and t >= total - 3.5:
            dt_s_end = t - (total - 3.5)
            draw_shorts_subscribe_callout(fr, W, H, dt_s_end)

        return fr

    # Single still frame mode (fast inspection without video encoding)
    if args.frame is not None:
        fr = compose_frame_at(args.frame)
        fr.convert("RGB").save(args.frame_out)
        print(f"✅ Still frame rendered at T={args.frame:.2f}s -> {args.frame_out}")
        return

    print(f"Rendering {out_file} [{W}x{H}] ({len(scenes)} scenes, {sum(len(s['ov']) for s in scenes)} overlays, {total:.1f}s)...")

    # Start ffmpeg with Rec.709 color matrix tags & faststart for instant streaming / YouTube & Instagram Reels compliance
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", args.audio,
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", "fast",
           "-crf", "18", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-colorspace", "bt709", "-movflags", "+faststart", "-threads", "4",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", out_file]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    # Render loop
    total_frames = int(total * FPS) + 1
    for fi in range(total_frames):
        t = fi / FPS
        fr = compose_frame_at(t)
        proc.stdin.write(fr.convert("RGB").tobytes())

    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        sys.exit(f"❌ ffmpeg rendering process failed with exit code {proc.returncode}")

    # Post-Mux Forensic Verification: Inspect container audio and video streams
    print(f"🔍 Running Post-Mux Verification on {out_file}...")
    try:
        import json
        probe_cmd = ["ffprobe", "-v", "error", "-show_streams", "-of", "json", out_file]
        p_res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p_res.returncode == 0:
            streams = json.loads(p_res.stdout).get("streams", [])
            has_v = any(s.get("codec_type") == "video" for s in streams)
            a_streams = [s for s in streams if s.get("codec_type") == "audio"]
            has_a = len(a_streams) > 0
            if not has_v:
                sys.exit(f"❌ Post-Mux Verification Failed: Output {out_file} has NO video stream!")
            if not has_a:
                sys.exit(f"❌ Post-Mux Verification Failed: Output {out_file} has NO audio stream!")
            
            # Check audio volume level to ensure audio is not silent
            vol_cmd = ["ffmpeg", "-i", out_file, "-af", "volumedetect", "-vn", "-sn", "-dn", "-f", "null", "-"]
            v_res = subprocess.run(vol_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            m_mean = re.search(r"mean_volume:\s+([-\d.]+)\s+dB", v_res.stderr)
            m_max = re.search(r"max_volume:\s+([-\d.]+)\s+dB", v_res.stderr)
            mean_vol = float(m_mean.group(1)) if m_mean else -99.0
            max_vol = float(m_max.group(1)) if m_max else -99.0
            if mean_vol < -50.0 or max_vol < -40.0:
                sys.exit(f"❌ Post-Mux Verification Failed: Muxed audio in {out_file} is inaudible/silent (mean={mean_vol:.1f} dB, max={max_vol:.1f} dB)")
            print(f"✅ Post-Mux Audio Verified: mean_vol={mean_vol:.1f} dB, max_vol={max_vol:.1f} dB (codec={a_streams[0].get('codec_name')})")
    except Exception as e:
        print(f"⚠️ Post-Mux check parsing notice: {e}")

    print(f"✅ Finished: {out_file} ({os.path.getsize(out_file)/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
