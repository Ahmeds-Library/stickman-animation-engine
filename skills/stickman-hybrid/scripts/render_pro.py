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
import argparse, csv, json, os, shutil, subprocess, sys, math, re
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

# Curated 4-Font Editorial Typography Roles
FONT_PATHS = {
    "hero": os.path.join(FONTS, "PermanentMarker-Regular.ttf"),
    "stamp": os.path.join(FONTS, "Bangers-Regular.ttf"),
    "annotation": os.path.join(FONTS, "Caveat-Bold.ttf"),
    "title": os.path.join(FONTS, "SedgwickAve-Regular.ttf"),
    "caption": os.path.join(FONTS, "PatrickHand-Regular.ttf"),
    "kalam": os.path.join(FONTS, "Kalam-Bold.ttf"),
    "montserrat": os.path.join(FONTS, "Montserrat-Black.ttf"),
    "luckiest": os.path.join(FONTS, "LuckiestGuy-Regular.ttf"),
    "modern": os.path.join(FONTS, "Montserrat-Black.ttf"),
    "display": os.path.join(FONTS, "LuckiestGuy-Regular.ttf"),
    "sketch": os.path.join(FONTS, "Kalam-Bold.ttf"),
    "default": os.path.join(FONTS, "PatrickHand-Regular.ttf"),
}
FONT_PATH = FONT_PATHS["caption"]
FONT_CX_PATH = FONT_PATHS["kalam"]

_loaded_fonts = {}

def resolve_font(role="default", size=40):
    key = (role, size)
    if key in _loaded_fonts:
        return _loaded_fonts[key]
    p = FONT_PATHS.get(role, FONT_PATHS["default"])
    if not os.path.exists(p):
        p = FONT_PATHS.get("default", FONT_PATH)
    if not os.path.exists(p):
        import glob
        ttfs = glob.glob(os.path.join(FONTS, "*.ttf"))
        p = ttfs[0] if ttfs else None
    if p and os.path.exists(p):
        try:
            f = ImageFont.truetype(p, size)
            _loaded_fonts[key] = f
            return f
        except Exception:
            pass
    f = ImageFont.load_default()
    _loaded_fonts[key] = f
    return f

# All 9 Visual Looks End-to-End
LOOKS = {
    "warm": {
        "paper": (252, 244, 222),
        "ink": (43, 30, 22),
        "card_in": (254, 250, 242),
        "card_out": (212, 163, 115),
        "accent": (218, 92, 42),
        "sub_accent": (255, 174, 51),
        "pie_colors": [(218, 92, 42), (255, 174, 51), (180, 140, 90), (120, 80, 50)]
    },
    "bright": {
        "paper": (255, 253, 246),
        "ink": (28, 32, 44),
        "card_in": (255, 252, 244),
        "card_out": (244, 238, 224),
        "accent": (230, 75, 45),
        "sub_accent": (70, 140, 230),
        "pie_colors": [(230, 75, 45), (70, 140, 230), (245, 180, 50), (60, 180, 120)]
    },
    "night": {
        "paper": (18, 20, 32),
        "ink": (250, 242, 220),
        "card_in": (28, 34, 50),
        "card_out": (64, 128, 140),
        "accent": (255, 180, 50),
        "sub_accent": (90, 200, 220),
        "pie_colors": [(255, 180, 50), (90, 200, 220), (220, 90, 120), (130, 110, 210)]
    },
    "ink": {
        "paper": (250, 248, 242),
        "ink": (24, 24, 24),
        "card_in": (255, 255, 255),
        "card_out": (24, 24, 24),
        "accent": (230, 57, 70),
        "sub_accent": (244, 162, 97),
        "pie_colors": [(230, 57, 70), (244, 162, 97), (69, 123, 157), (42, 157, 143)]
    },
    "oversimplified": {
        "paper": (242, 230, 206),
        "ink": (17, 17, 17),
        "card_in": (255, 255, 255),
        "card_out": (17, 17, 17),
        "accent": (209, 44, 44),
        "sub_accent": (43, 84, 154),
        "pie_colors": [(209, 44, 44), (43, 84, 154), (229, 184, 44), (70, 160, 90)]
    },
    "cgp_grey": {
        "paper": (245, 246, 248),
        "ink": (26, 29, 32),
        "card_in": (255, 255, 255),
        "card_out": (61, 68, 82),
        "accent": (247, 181, 0),
        "sub_accent": (0, 163, 137),
        "pie_colors": [(247, 181, 0), (0, 163, 137), (224, 32, 32), (0, 122, 255)]
    },
    "casually_explained": {
        "paper": (250, 250, 250),
        "ink": (0, 0, 0),
        "card_in": (255, 255, 255),
        "card_out": (210, 215, 220),
        "accent": (96, 125, 139),
        "sub_accent": (229, 115, 115),
        "pie_colors": [(96, 125, 139), (229, 115, 115), (129, 199, 132), (255, 183, 77)]
    },
    "minute_physics": {
        "paper": (250, 248, 242),
        "ink": (24, 24, 24),
        "card_in": (244, 239, 230),
        "card_out": (24, 24, 24),
        "accent": (255, 215, 0),
        "sub_accent": (0, 180, 216),
        "pie_colors": [(255, 215, 0), (0, 180, 216), (230, 57, 70), (255, 183, 3)]
    },
    "painted": {
        "paper": (246, 243, 236),
        "ink": (34, 36, 40),
        "card_in": (236, 234, 228),
        "card_out": (150, 158, 160),
        "accent": (196, 92, 54),
        "sub_accent": (90, 120, 130),
        "pie_colors": [(196, 92, 54), (90, 120, 130), (210, 160, 80), (120, 140, 100)]
    }
}

ACTIVE_LOOK_NAME = "bright"
_default_cfg = LOOKS["bright"]
PAPER = _default_cfg["paper"]
INK = _default_cfg["ink"]
CARD_IN = _default_cfg["card_in"]
CARD_OUT = _default_cfg["card_out"]
ACCENT = _default_cfg["accent"]
SUB_ACCENT = _default_cfg["sub_accent"]
PIE_COLORS = _default_cfg["pie_colors"]
CARD_INK = INK

def set_look(name):
    global PAPER, INK, CARD_IN, CARD_OUT, CARD_INK, ACCENT, SUB_ACCENT, PIE_COLORS, ACTIVE_LOOK_NAME, _card_cache
    if name not in LOOKS:
        name = "bright"
    ACTIVE_LOOK_NAME = name
    cfg = LOOKS[name]
    PAPER = cfg["paper"]
    INK = cfg["ink"]
    CARD_IN = cfg["card_in"]
    CARD_OUT = cfg["card_out"]
    ACCENT = cfg["accent"]
    SUB_ACCENT = cfg["sub_accent"]
    PIE_COLORS = cfg["pie_colors"]
    CARD_INK = PAPER if name == "night" else INK
    _card_cache.clear()

FPS = 30
_text_cache = {}
_card_cache = {}
_sticker_cache = {}


def text_layer(text, size, colour, font_role="default"):
    key = (text, size, colour, font_role)
    if key not in _text_cache:
        f = resolve_font(font_role, size)
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
    key = (w, h, ACTIVE_LOOK_NAME)
    if key not in _card_cache:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.clip(np.hypot((x - w / 2) / (w * 0.56), (y - h / 2) / (h * 0.56)), 0, 1) ** 1.25
        r = r[..., None]
        # Warm bright center gently vignetting toward edges + organic paper fiber texture
        a = np.array(CARD_IN, np.float32) * (1 - r) + np.array(CARD_OUT, np.float32) * r
        rng = np.random.default_rng(42)
        fiber = rng.normal(0, 3.8, a.shape[:2]).astype(np.float32)
        # Subtle corner darkening vignette (~6%)
        edge_v = np.clip((np.hypot((x - w / 2) / (w * 0.72), (y - h / 2) / (h * 0.72)) - 0.55) * 0.16, 0, 0.12)[..., None]
        a = a * (1.0 - edge_v) + fiber[..., None]
        base_im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")

        # Subtle handcrafted blueprint dot-grid & faint editorial rule lines (~6% ink opacity)
        grid_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grid_layer)
        dot_col = INK + (18,)
        rule_col = INK + (12,)
        step = max(36, int(min(w, h) / 26))
        for ry in range(step, h, step * 4):
            gd.line((0, ry, w, ry), fill=rule_col, width=1)
        for gy in range(step // 2, h, step):
            for gx in range(step // 2, w, step):
                gd.ellipse((gx - 1, gy - 1, gx + 1, gy + 1), fill=dot_col)
        base_im.alpha_composite(grid_layer)
        _card_cache[key] = base_im
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
    key_k = (path, h)
    if key_k not in _sticker_cache:
        if len(_sticker_cache) > 40:
            _sticker_cache.clear()
        im = Image.open(path).convert("RGBA")
        # Crisp 1px boundary feather so resized edges blend cleanly without white cutout halos
        nw = max(1, round(im.width * h / im.height))
        im = im.resize((nw, h), Image.LANCZOS)
        pad = max(16, h // 20)
        shadow = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        a_ch = im.getchannel("A")
        shadow_pad = Image.new("L", shadow.size, 0)
        shadow_pad.paste(a_ch.point(lambda v: int(v * 0.36)), (pad + max(6, h // 45), pad + max(8, h // 32)))
        shadow.putalpha(shadow_pad.filter(ImageFilter.GaussianBlur(max(6, h // 36))))
        out = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
        out.alpha_composite(shadow, (0, 0))
        out.alpha_composite(im, (pad, pad))
        _sticker_cache[key_k] = out
    return _sticker_cache[key_k]


def spring_p(p):
    """Smooth damped ease-out curve (zero jitter or harsh overshoot wobble)."""
    p = max(0.0, min(1.0, p))
    return 1.0 - (1.0 - p) ** 3


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


_backdrop_halo_cache = {}


def _soft_backdrop_halo(w, h, base_rgb=(252, 248, 238), peak_alpha=68):
    """Generates a true analytical radial-falloff halo (alpha==0 strictly inside r<=0.84*half_dim, ZERO rectangular seam)."""
    bw = max(96, int(w * 1.95))
    bh = max(96, int(h * 1.95))
    key = (bw // 16, bh // 16, base_rgb, peak_alpha)
    if key not in _backdrop_halo_cache:
        if len(_backdrop_halo_cache) > 48:
            _backdrop_halo_cache.clear()
        rw, rh = max(96, (bw // 16) * 16), max(96, (bh // 16) * 16)
        yg, xg = np.ogrid[:rh, :rw]
        dx = (xg - (rw * 0.5)) / max(1.0, rw * 0.42)
        dy = (yg - (rh * 0.5)) / max(1.0, rh * 0.42)
        dist = np.sqrt(dx * dx + dy * dy)
        falloff = np.where(dist < 1.0, np.power(np.clip(1.0 - dist, 0.0, 1.0), 2.4), 0.0)
        arr = np.zeros((rh, rw, 4), dtype=np.uint8)
        arr[:, :, 0] = base_rgb[0]
        arr[:, :, 1] = base_rgb[1]
        arr[:, :, 2] = base_rgb[2]
        arr[:, :, 3] = np.clip(falloff * peak_alpha, 0, 255).astype(np.uint8)
        _backdrop_halo_cache[key] = Image.fromarray(arr, mode="RGBA")
    halo = _backdrop_halo_cache[key]
    if halo.size != (bw, bh):
        return halo.resize((bw, bh), Image.BILINEAR)
    return halo


def calculate_intelligent_sticker_anchor(
    bg_im, item_w, item_h, requested_pos, is_shorts, W, H, occupied_boxes, sub_top_y,
    slot_bias=0, cohort_size=1, cohort_rank=0
):
    """Director-Grade Intentional Formation Solver:
    Replaces grid scatter with cohesive editorial formations locked once in overlay_anchor_cache:
    - 1 Sticker: Sightline & Rule-of-Thirds focus on opposite cleanest third at eye/chest level.
    - 2 Stickers: Matched aligned horizontal duo shelf (shared Y baseline).
    - 3 Stickers: Clean triangle (9:16) or aligned horizontal trio row (16:9).
    - 4+ Stickers: Aligned 2x2 showcase grid (9:16) or 4-across editorial gallery row (16:9) with >=36px gap.
    """
    spatial = ACTIVE_RL_POLICY.get("rule_24_spatial_hierarchy", {})
    right_ui_margin = spatial.get("shorts_margin_right_px", 220) if is_shorts else 54
    sub_buf = spatial.get("min_cutout_subtitle_buffer_px", 140 if is_shorts else 80)
    pad_px = max(36, int(spatial.get("multi_sticker_min_padding_px", 36)))

    left_ui_margin = 48 if is_shorts else 54
    top_ui_margin = 105 if is_shorts else 65

    def _bounds_for_size(bw, bh):
        max_sy = sub_top_y - sub_buf - bh // 2
        min_sy = top_ui_margin + bh // 2
        min_sx = left_ui_margin + bw // 2
        max_sx = W - right_ui_margin - bw // 2
        if max_sy < min_sy:
            max_sy = min_sy + 40
        if max_sx < min_sx:
            max_sx = min_sx + 40
        return min_sx, max_sx, min_sy, max_sy

    min_safe_x, max_safe_x, min_safe_y, max_safe_y = _bounds_for_size(item_w, item_h)
    usable_mid_x = (left_ui_margin + (W - right_ui_margin)) // 2
    usable_span_x = (W - right_ui_margin) - left_ui_margin
    span_y = max(40, max_safe_y - min_safe_y)

    def _collides(bx0, by0, bx1, by1):
        for ox0, oy0, ox1, oy1 in occupied_boxes:
            if not (bx1 <= ox0 - pad_px or bx0 >= ox1 + pad_px or by1 <= oy0 - pad_px or by0 >= oy1 + pad_px):
                return True
        return False

    req = str(requested_pos or "").lower()

    # Respect explicit fractional coords if collision-free
    if "," in req:
        try:
            pts = [float(x.strip()) for x in req.split(",") if x.strip()]
            if len(pts) >= 2:
                req_cx = max(min_safe_x, min(int(W * pts[0]), max_safe_x))
                req_cy = max(min_safe_y, min(int(H * pts[1]), max_safe_y))
                bx0, by0 = req_cx - item_w // 2, req_cy - item_h // 2
                if not _collides(bx0, by0, bx0 + item_w, by0 + item_h):
                    return req_cx, req_cy, 1.0
        except Exception:
            pass

    # Build intentional formation targets by simultaneous cohort size
    candidates = []
    if cohort_size <= 1:
        # Sightline & Rule-of-Thirds: pick cleanest opposite peripheral third at eye/chest level
        eye_y = int(min_safe_y + span_y * (0.28 if is_shorts else 0.34))
        left_x = int(left_ui_margin + usable_span_x * (0.25 if is_shorts else 0.19))
        right_x = int(left_ui_margin + usable_span_x * (0.76 if is_shorts else 0.81))
        alt_y = int(min_safe_y + span_y * (0.14 if is_shorts else 0.22))
        l_score = compute_negative_space_score(bg_im, left_x - item_w // 2, eye_y - item_h // 2, left_x + item_w // 2, eye_y + item_h // 2)
        r_score = compute_negative_space_score(bg_im, right_x - item_w // 2, eye_y - item_h // 2, right_x + item_w // 2, eye_y + item_h // 2)
        if "left" in req:
            candidates = [("rule3_left", left_x, eye_y), ("rule3_left_hi", left_x, alt_y), ("rule3_right", right_x, eye_y)]
        elif "right" in req:
            candidates = [("rule3_right", right_x, eye_y), ("rule3_right_hi", right_x, alt_y), ("rule3_left", left_x, eye_y)]
        elif "top" in req or "high" in req:
            candidates = [("rule3_top", usable_mid_x, alt_y), ("rule3_right_hi", right_x, alt_y), ("rule3_left_hi", left_x, alt_y)]
        elif r_score <= l_score:
            candidates = [("rule3_right", right_x, eye_y), ("rule3_right_hi", right_x, alt_y), ("rule3_left", left_x, eye_y), ("rule3_left_hi", left_x, alt_y)]
        else:
            candidates = [("rule3_left", left_x, eye_y), ("rule3_left_hi", left_x, alt_y), ("rule3_right", right_x, eye_y), ("rule3_right_hi", right_x, alt_y)]
    elif cohort_size == 2:
        # Balanced Paired Shelf / Duo along matched horizontal horizon
        shared_y = int(min_safe_y + span_y * (0.22 if is_shorts else 0.28))
        lx = int(left_ui_margin + usable_span_x * (0.25 if is_shorts else 0.20))
        rx = int(left_ui_margin + usable_span_x * (0.75 if is_shorts else 0.80))
        pair = [("duo_left", lx, shared_y), ("duo_right", rx, shared_y)]
        idx_pref = cohort_rank % 2
        candidates = [pair[idx_pref], pair[1 - idx_pref], ("duo_low_l", lx, int(min_safe_y + span_y * 0.68)), ("duo_low_r", rx, int(min_safe_y + span_y * 0.68))]
    elif cohort_size == 3:
        if is_shorts:
            # 2-top + 1-lower-center inverted triangle inside clean upper stage
            top_y = int(min_safe_y + span_y * 0.10)
            bot_y = int(min_safe_y + span_y * 0.78)
            lx = int(left_ui_margin + usable_span_x * 0.25)
            rx = int(left_ui_margin + usable_span_x * 0.75)
            trio = [("tri_tl", lx, top_y), ("tri_tr", rx, top_y), ("tri_bc", usable_mid_x, bot_y)]
        else:
            # Clean aligned 3-across horizontal showcase row across upper stage
            row_y = int(H * 0.23)
            trio = [
                ("trio_1", int(W * 0.20), row_y),
                ("trio_2", int(W * 0.50), int(H * 0.18)),
                ("trio_3", int(W * 0.80), row_y),
            ]
        r_idx = cohort_rank % 3
        candidates = trio[r_idx:] + trio[:r_idx]
    else:
        if is_shorts:
            # Crisp aligned 2x2 showcase grid inside clean upper stage
            col_l = int(left_ui_margin + usable_span_x * 0.26)
            col_r = int(left_ui_margin + usable_span_x * 0.74)
            row_t = int(min_safe_y + span_y * 0.08)
            row_b = int(min_safe_y + span_y * 0.84)
            grid4 = [
                ("g4_tl", col_l, row_t),
                ("g4_tr", col_r, row_t),
                ("g4_bl", col_l, row_b),
                ("g4_br", col_r, row_b),
            ]
        else:
            # Crisp 4-across aligned gallery showcase row
            row_y = int(H * 0.24)
            grid4 = [
                ("row4_1", int(W * 0.15), row_y),
                ("row4_2", int(W * 0.38), int(H * 0.18)),
                ("row4_3", int(W * 0.62), int(H * 0.18)),
                ("row4_4", int(W * 0.85), row_y),
            ]
        r_idx = cohort_rank % len(grid4)
        candidates = grid4[r_idx:] + grid4[:r_idx]

    # Secondary safety net candidates ONLY if formation targets physically cannot fit without overlap
    safety_net = []
    for gy in (0.12, 0.42, 0.72, 0.92):
        for gx in (0.16, 0.50, 0.84):
            safety_net.append((f"safe_{gx:.2f}_{gy:.2f}", int(min_safe_x + max(40, max_safe_x - min_safe_x) * gx), int(min_safe_y + span_y * gy)))

    # First prioritize keeping the exact intentional formation by trying uniform scale steps on formation slots
    for scale_try in (1.0, 0.90, 0.80, 0.70, 0.58):
        bw = max(32, int(item_w * scale_try))
        bh = max(32, int(item_h * scale_try))
        msx, mxsx, msy, mxsy = _bounds_for_size(bw, bh)
        for _, raw_cx, raw_cy in candidates:
            cx = max(msx, min(raw_cx, mxsx))
            cy = max(msy, min(raw_cy, mxsy))
            bx0, by0, bx1, by1 = cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2
            if not _collides(bx0, by0, bx1, by1):
                return cx, cy, scale_try

    # Last-resort clean slot search across safety net
    for scale_try in (0.85, 0.72, 0.60, 0.50):
        bw = max(32, int(item_w * scale_try))
        bh = max(32, int(item_h * scale_try))
        msx, mxsx, msy, mxsy = _bounds_for_size(bw, bh)
        best_a = None
        best_s = float("inf")
        for _, raw_cx, raw_cy in safety_net:
            cx = max(msx, min(raw_cx, mxsx))
            cy = max(msy, min(raw_cy, mxsy))
            bx0, by0, bx1, by1 = cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2
            if _collides(bx0, by0, bx1, by1):
                continue
            sc = compute_negative_space_score(bg_im, bx0, by0, bx1, by1)
            if sc < best_s:
                best_s = sc
                best_a = (cx, cy)
        if best_a:
            return best_a[0], best_a[1], scale_try

    bw, bh = max(32, int(item_w * 0.58)), max(32, int(item_h * 0.58))
    msx, mxsx, msy, mxsy = _bounds_for_size(bw, bh)
    return max(msx, min(candidates[0][1], mxsx)), max(msy, min(candidates[0][2], mxsy)), 0.58


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
    lines = [text_layer(ln, size, CARD_INK if big else INK, font_role="hero" if (big or any(c.isdigit() for c in ln)) else "default") for ln in text.split("|")]
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


def fit_sticker_in_box(path_or_im, max_w, max_h):
    """Loads a sticker and scales it preserving aspect ratio so BOTH width <= max_w and height <= max_h."""
    if path_or_im is None or max_w <= 0 or max_h <= 0:
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

    scale = min(max_w / max(1, raw.width), max_h / max(1, raw.height))
    nw = max(1, int(raw.width * scale))
    nh = max(1, int(raw.height * scale))
    return raw.resize((nw, nh), Image.LANCZOS)


def load_and_scale_sticker(path_or_im, target_h):
    """Loads a sticker, scales it keeping aspect ratio to target_h."""
    return fit_sticker_in_box(path_or_im, max_w=target_h * 4, max_h=target_h)


def render_wrapped_text_block(text, font_role, start_size, min_size, max_w, max_h, color, max_lines=3, line_gap_ratio=0.18, return_line_boxes=False):
    """Auto-fits and wraps text cleanly to maximize legibility inside (max_w, max_h)."""
    words = [w for w in str(text).split() if w]
    if not words:
        empty = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        return (empty, []) if return_line_boxes else empty

    best_layers = None
    best_gap = 12
    for sz in range(int(start_size), int(min_size) - 1, -8):
        lines = []
        cur = []
        too_wide = False
        for wd in words:
            cand = " ".join(cur + [wd])
            if text_layer(cand, sz, color, font_role=font_role).width > max_w:
                if cur:
                    lines.append(" ".join(cur))
                    cur = [wd]
                    if text_layer(wd, sz, color, font_role=font_role).width > max_w:
                        too_wide = True
                        break
                else:
                    too_wide = True
                    break
            else:
                cur.append(wd)
        if too_wide:
            continue
        if cur:
            lines.append(" ".join(cur))
        if len(lines) > max_lines:
            continue

        layers = [text_layer(ln, sz, color, font_role=font_role) for ln in lines]
        gap = max(8, int(sz * line_gap_ratio))
        tot_h = sum(l.height for l in layers) + gap * max(0, len(layers) - 1)
        if tot_h <= max_h:
            best_layers = layers
            best_gap = gap
            break

    if best_layers is None:
        # Safe fallback at min_size
        sz = max(24, int(min_size))
        lines = []
        cur = []
        for wd in words:
            cand = " ".join(cur + [wd])
            if cur and text_layer(cand, sz, color, font_role=font_role).width > max_w:
                lines.append(" ".join(cur))
                cur = [wd]
            else:
                cur.append(wd)
        if cur:
            lines.append(" ".join(cur))
        best_layers = [text_layer(ln, sz, color, font_role=font_role) for ln in lines[:max_lines + 1]]
        best_gap = max(6, int(sz * line_gap_ratio))

    bw = max(l.width for l in best_layers)
    bh = sum(l.height for l in best_layers) + best_gap * max(0, len(best_layers) - 1)
    block = Image.new("RGBA", (bw, max(1, bh)), (0, 0, 0, 0))
    line_boxes = []
    yy = 0
    for l in best_layers:
        lx = (bw - l.width) // 2
        block.alpha_composite(l, (lx, yy))
        line_boxes.append((lx, yy, l.width, l.height))
        yy += l.height + best_gap
    return (block, line_boxes) if return_line_boxes else block


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


def _draw_elliptical_ground_shadow(overlay_im, cx, base_y, width):
    """Draws a soft natural ground shadow ellipse beneath a sticker on full-bleed canvas."""
    ew = max(40, int(width * 0.72))
    eh = max(16, int(ew * 0.14))
    sh = Image.new("RGBA", (ew + 40, eh + 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse((20, 20, 20 + ew, 20 + eh), fill=(25, 22, 18, 46))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    overlay_im.alpha_composite(sh, (int(cx - sh.width // 2), int(base_y - sh.height // 2)))


def _draw_highlighter_swipe(overlay_im, cx, cy, sw_w, sw_h, color, tilt=-1.6):
    """Draws a tapered, slightly angled hand-drawn marker highlighter brush stroke with organic rough edges."""
    pad = 44
    sw_im = Image.new("RGBA", (sw_w + 2 * pad, sw_h + 2 * pad), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sw_im)
    y0 = pad + int(sw_h * 0.10)
    y1 = pad + int(sw_h * 0.94)
    x0, x1 = pad, pad + sw_w
    # Multi-vertex rough hand-drawn polygon mimicking authentic chisel-tip highlighter sweep
    poly = [
        (x0 + 16, y0 + 7),
        (x0 + int(sw_w * 0.25), y0 + 2),
        (x0 + int(sw_w * 0.55), y0 + 5),
        (x0 + int(sw_w * 0.82), y0 + 1),
        (x1 - 4, y0 + 4),
        (x1, y1 - 9),
        (x0 + int(sw_w * 0.78), y1 - 3),
        (x0 + int(sw_w * 0.45), y1 - 6),
        (x0 + int(sw_w * 0.18), y1 - 2),
        (x0, y1 - 5),
    ]
    sd.polygon(poly, fill=color)
    # Second translucent inner overlap pass for real ink pooling
    sd.rounded_rectangle((x0 + 20, y0 + 10, x1 - 16, y1 - 6), radius=max(10, sw_h // 5), fill=color[:3] + (max(18, int(color[3] * 0.45)),))
    sw_im = sw_im.rotate(tilt, resample=Image.BILINEAR, expand=True)
    overlay_im.alpha_composite(sw_im, (int(cx - sw_im.width // 2), int(cy - sw_im.height // 2)))


def _draw_per_line_highlighters(overlay_im, block_x0, block_y0, line_boxes, color, pad_x=42):
    """Draws tight individual organic marker brush swipes behind each wrapped line (never across line gaps)."""
    tilts = (-1.8, 1.3, -1.4)
    for li, (lx, ly, lw, lh) in enumerate(line_boxes):
        cx = block_x0 + lx + lw // 2
        cy = block_y0 + ly + int(lh * 0.56)
        sw_w = lw + pad_x * 2
        sw_h = max(38, int(lh * 0.54))
        _draw_highlighter_swipe(overlay_im, cx, cy, sw_w, sw_h, color, tilt=tilts[li % len(tilts)])


def _draw_editorial_corner_ticks(d, x0, y0, x1, y1, color, arm=44, width=6):
    """Draws crisp minimalist editorial registration corner brackets around an impact stage."""
    # Top-Left
    d.line((x0, y0 + arm, x0, y0, x0 + arm, y0), fill=color, width=width)
    # Top-Right
    d.line((x1 - arm, y0, x1, y0, x1, y0 + arm), fill=color, width=width)
    # Bottom-Left
    d.line((x0, y1 - arm, x0, y1, x0 + arm, y1), fill=color, width=width)
    # Bottom-Right
    d.line((x1 - arm, y1, x1, y1, x1, y1 - arm), fill=color, width=width)


def _resolve_timeline_row_sticker(seg_text, used_paths=None):
    """Resolves a unique contextual sticker from project elements/cut or global skills/stickman-stickers/ for a timeline step."""
    used = used_paths if used_paths is not None else set()
    txt_l = str(seg_text or "").lower()

    # 1. Check local / sibling elements/cut first with semantic matching
    cand_dirs = [
        os.path.join("elements", "cut"),
        os.path.join("..", "elements", "cut"),
        os.path.join("..", "short", "elements", "cut"),
        os.path.join("..", "long", "elements", "cut"),
    ]
    pool = {}
    for cd in cand_dirs:
        if os.path.isdir(cd):
            for fn in sorted(os.listdir(cd)):
                if fn.endswith(".png"):
                    fp = os.path.abspath(os.path.join(cd, fn))
                    if os.path.getsize(fp) > 500 and fp not in used:
                        pool[os.path.splitext(fn)[0].lower()] = fp

    keyword_map = [
        (("trade", "ship", "route", "export", "import", "sea", "maritime"), ("warship_prow", "cc0_gold_coin", "tin_ingot")),
        (("crop", "wheat", "grain", "famine", "drought", "food", "harvest"), ("wheat_grain", "cc0_flame_fire")),
        (("tin", "copper", "bronze", "sword", "weapon", "metal", "ingot"), ("tin_ingot", "bronze_sword")),
        (("collapse", "burn", "fire", "ash", "torch", "destroy", "fall"), ("burning_torch", "stone_ruin", "cc0_flame_fire")),
        (("record", "tablet", "write", "letter", "scroll", "archive"), ("clay_tablet", "cc0_ancient_scroll")),
        (("war", "invad", "army", "raider", "soldier", "helmet"), ("horned_helmet", "bronze_sword", "cc0_warrior_shield")),
    ]
    for kws, prefs in keyword_map:
        if any(k in txt_l for k in kws):
            for pk in prefs:
                if pk in pool:
                    used.add(pool[pk])
                    return pool[pk]

    # 2. Query Tier 1 flow_vault & Tier 2 cc0_library via stickman-stickers index
    try:
        import asset_registry
        idx_mod = asset_registry._get_sticker_library_indexer()
        if idx_mod:
            hits = idx_mod.search_stickers(seg_text, min_score=0.35, require_alpha_ok=True)
            for h in hits:
                hp = os.path.abspath(h["path"])
                if hp not in used and os.path.exists(hp):
                    used.add(hp)
                    return hp
    except Exception:
        pass

    for b, fp in pool.items():
        if any(tok in txt_l for tok in b.split("_")):
            used.add(fp)
            return fp
    if pool:
        first_fp = next(iter(pool.values()))
        used.add(first_fp)
        return first_fp
    return None


def _draw_radial_ticks(d, x, y, scale=1.0, color=(230, 75, 45, 220)):
    """Draws 3 crisp editorial radial accent ticks near headline corner."""
    s = scale
    d.line((x - int(22 * s), y - int(8 * s), x - int(48 * s), y - int(28 * s)), fill=color, width=max(4, int(9 * s)))
    d.line((x - int(10 * s), y - int(22 * s), x - int(20 * s), y - int(58 * s)), fill=color, width=max(4, int(9 * s)))
    d.line((x + int(8 * s), y - int(26 * s), x + int(16 * s), y - int(56 * s)), fill=color, width=max(4, int(9 * s)))


def _draw_curved_ink_arrow(d, x0, y0, x1, y1, color, width=10, ctrl_pt=None, draw_progress=1.0):
    """Draws an animated hand-drawn tapered Bezier ink arrow (0%->100% trim-path + crisp barbs)."""
    dp = max(0.0, min(1.0, float(draw_progress)))
    if dp <= 0.02:
        return
    if ctrl_pt is not None:
        mx, my = ctrl_pt
    else:
        mx = (x0 + x1) / 2.0 + (110 if x1 >= x0 else -110)
        my = (y0 + y1) / 2.0
    steps = 36
    pts = []
    for k in range(steps + 1):
        t = k / steps
        px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t ** 2 * x1
        py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t ** 2 * y1
        pts.append((px, py))

    curve_p = min(1.0, dp / 0.88)
    f_idx = curve_p * steps
    n_whole = int(f_idx)
    vis_pts = pts[:n_whole + 1]
    if n_whole < steps and (f_idx - n_whole) > 0.01:
        frac = f_idx - n_whole
        nx = pts[n_whole][0] * (1.0 - frac) + pts[n_whole + 1][0] * frac
        ny = pts[n_whole][1] * (1.0 - frac) + pts[n_whole + 1][1] * frac
        vis_pts.append((nx, ny))

    for k in range(len(vis_pts) - 1):
        u = (k + 0.5) / steps
        seg_w = max(3, int(round(width * (0.86 + 0.30 * math.sin(math.pi * u)))))
        d.line([vis_pts[k], vis_pts[k + 1]], fill=color, width=seg_w)
        r_cap = max(1, seg_w // 2 - 1)
        if r_cap >= 2:
            vx, vy = vis_pts[k + 1]
            d.ellipse((vx - r_cap, vy - r_cap, vx + r_cap, vy + r_cap), fill=color)

    # Hand-drawn arrowhead barbs pop smoothly at final 0.85 -> 1.00 trim phase
    if dp >= 0.85:
        ah_p = min(1.0, (dp - 0.85) / 0.15)
        dx, dy = pts[-1][0] - pts[-5][0], pts[-1][1] - pts[-5][1]
        ang = math.atan2(dy, dx)
        ah_len = width * 3.4 * ah_p
        p1 = (x1 - ah_len * math.cos(ang - 0.50), y1 - ah_len * math.sin(ang - 0.50))
        p2 = (x1 - ah_len * math.cos(ang + 0.50), y1 - ah_len * math.sin(ang + 0.50))
        d.line([p1, (x1, y1), p2], fill=color, width=max(3, int(width * 0.96)))


def _auto_resolve_second_split_sticker(existing_stk, other_text):
    """Picks a contrasting second transparent sticker from elements/cut/ when split_compare only supplied one."""
    exist_base = os.path.splitext(os.path.basename(str(existing_stk or "")))[0].lower()
    cand_dirs = [
        os.path.join("elements", "cut"),
        os.path.join("..", "elements", "cut"),
        os.path.join("..", "short", "elements", "cut"),
        os.path.join("..", "long", "elements", "cut"),
    ]
    pool = {}
    for cd in cand_dirs:
        if os.path.isdir(cd):
            for fn in sorted(os.listdir(cd)):
                if fn.endswith(".png"):
                    b = os.path.splitext(fn)[0].lower()
                    if b != exist_base and b not in pool:
                        fp = os.path.join(cd, fn)
                        if os.path.getsize(fp) > 500:
                            pool[b] = fp
    if not pool:
        return None

    txt_l = str(other_text or "").lower()
    priority_map = {
        "stone_ruin": ("breakdown", "collapse", "ruin", "city", "cities", "abandoned", "system", "wreck"),
        "tin_ingot": ("tin", "copper", "trade", "chain", "bronze", "alloy", "economy", "system"),
        "clay_tablet": ("tablet", "writing", "archive", "record", "myth", "story", "letters"),
        "bronze_sword": ("weapon", "sword", "army", "armies", "defenseless", "warrior"),
        "wheat_grain": ("drought", "famine", "grain", "starv", "crop", "food"),
        "horned_helmet": ("invader", "raider", "barbarian", "war", "soldier", "army"),
        "warship_prow": ("ship", "fleet", "sea", "maritime", "coast", "ocean"),
        "burning_torch": ("fire", "burn", "ash", "torch"),
    }
    for stk_key, kws in priority_map.items():
        if stk_key in pool and any(k in txt_l for k in kws):
            return pool[stk_key]
    for b, fp in pool.items():
        if any(tok in txt_l for tok in b.split("_")):
            return fp
    # Deterministic fallback contrast sticker
    for pref in ("stone_ruin", "tin_ingot", "clay_tablet", "bronze_sword"):
        if pref in pool:
            return pool[pref]
    return next(iter(pool.values()), None)


def _text_with_offset_shadow(block_im, dx=8, dy=10, shadow_col=(18, 16, 14, 65)):
    """Adds subtle crisp offset ink drop shadow to rendered text block."""
    out = Image.new("RGBA", (block_im.width + abs(dx) + 8, block_im.height + abs(dy) + 8), (0, 0, 0, 0))
    ox = max(0, -dx)
    oy = max(0, -dy)
    a = block_im.getchannel("A")
    sh = Image.new("RGBA", block_im.size, shadow_col[:3] + (0,))
    sh.putalpha(a.point(lambda v: int(v * (shadow_col[3] / 255.0))))
    out.alpha_composite(sh, (ox + dx, oy + dy))
    out.alpha_composite(block_im, (ox, oy))
    return out


def draw_card_stat(w, h, text, is_shorts=False, dt=0.0, sticker_im=None):
    """Archetype 3: Full-Bleed Viral Documentary Impact Frame (Per-Line Organic Brush Swipes, Clean Arrow Clearance, Corner Registration)."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    parts = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else [text.strip()]
    stat_txt = parts[0] if parts else "100%"
    sub_txt = " ".join(parts[1].split()[:6]) if len(parts) > 1 and parts[1].strip() else ""

    p = min(1.0, dt / 0.30)
    ease_s = 0.96 + 0.04 * spring_p(p)
    has_sticker = (sticker_im is not None)

    if is_shorts:
        # Full active visual stage on 9:16 Shorts: Y 10% - 72% (strict >=9% horizontal margin left/right!)
        max_w = int(W2 * 0.78)
        _draw_editorial_corner_ticks(d2, int(W2 * 0.085), int(H2 * 0.11), int(W2 * 0.915), int(H2 * 0.69), INK + (58,), arm=48, width=6)
        if has_sticker:
            # 1. Generous sticker cleanly inside Y: 11% - 36% with seamless radial backplate lift (leaves safe room above bottom caption pill)
            stk_img = fit_sticker_in_box(sticker_im, max_w=int(W2 * 0.54), max_h=int(H2 * 0.24))
            stk_cy = int(H2 * 0.235)
            stk_w = stk_img.width if stk_img else 420
            stk_h = stk_img.height if stk_img else 320
            stk_x0 = W2 // 2 - stk_w // 2
            stk_y0 = stk_cy - stk_h // 2
            if stk_img:
                bp = _soft_backdrop_halo(stk_img.width, stk_img.height, base_rgb=SUB_ACCENT, peak_alpha=46)
                overlay2.alpha_composite(bp, (W2 // 2 - bp.width // 2, stk_cy - bp.height // 2))
                _draw_elliptical_ground_shadow(overlay2, W2 // 2, stk_cy + stk_img.height // 2 + 18, stk_img.width)
                stk_sh = add_sticker_drop_shadow(stk_img, offset=(10, 14), shadow_color=(0, 0, 0, 42), blur_radius=12)
                overlay2.alpha_composite(stk_sh, (W2 // 2 - stk_sh.width // 2, stk_cy - stk_sh.height // 2))

            # 2. Giant Hero Stat with PER-LINE organic brush highlighters cleanly inside <=80% width
            stat_raw, line_boxes = render_wrapped_text_block(
                stat_txt, "hero", start_size=int(345 * ease_s), min_size=190,
                max_w=max_w, max_h=int(H2 * 0.17), color=INK, max_lines=2, return_line_boxes=True
            )
            stat_block = _text_with_offset_shadow(stat_raw, dx=8, dy=10)
            sub_block = render_wrapped_text_block(
                sub_txt.upper(), "annotation", start_size=118, min_size=82,
                max_w=max_w, max_h=int(H2 * 0.08), color=ACCENT, max_lines=2
            ) if sub_txt else None

            tot_h = stat_block.height + (36 + sub_block.height if sub_block else 0)
            txt_top = int(H2 * 0.485) - tot_h // 2
            bx_stat = W2 // 2 - stat_block.width // 2
            _draw_per_line_highlighters(overlay2, bx_stat, txt_top, line_boxes, SUB_ACCENT + (132,), pad_x=34)
            overlay2.alpha_composite(stat_block, (bx_stat, txt_top))
            cur_y = txt_top + stat_block.height
            if sub_block:
                rule_w = min(int(max_w * 0.80), stat_raw.width + 32)
                d2.line((W2 // 2 - rule_w // 2, cur_y + 10, W2 // 2 + rule_w // 2, cur_y + 6), fill=ACCENT + (240,), width=11)
                overlay2.alpha_composite(sub_block, (W2 // 2 - sub_block.width // 2, cur_y + 30))

            # 3. Aim curved arrow cleanly inward at the lower-left flank of the sticker (stopping 44px @ 2x = 22px @ 1x outside outline)
            flank_x, flank_y = stk_x0 + int(stk_w * 0.08), stk_y0 + int(stk_h * 0.74)
            if stk_img is not None:
                try:
                    a_np = np.array(stk_img.split()[3])
                    y_lo, y_hi = int(stk_h * 0.55), int(stk_h * 0.90)
                    band_rows, band_cols = np.where(a_np[y_lo:y_hi, :] > 120)
                    if len(band_cols) > 0:
                        min_i = int(np.argmin(band_cols))
                        flank_x = stk_x0 + int(band_cols[min_i])
                        flank_y = stk_y0 + y_lo + int(band_rows[min_i])
                except Exception:
                    pass

            first_lx, first_ly, _, first_lh = line_boxes[0]
            first_left_x = bx_stat + first_lx - 34
            arr_x0 = max(int(W2 * 0.14), first_left_x - 52)
            arr_y0 = txt_top + first_ly + int(first_lh * 0.42)
            arr_x1 = max(int(W2 * 0.11), flank_x - 46)
            arr_y1 = flank_y + 16
            ctrl_x = max(int(W2 * 0.095), min(arr_x0, arr_x1) - 160)
            ctrl_y = int((arr_y0 + arr_y1) * 0.56)
            arrow_prog = min(1.0, max(0.0, (dt - 0.28) / 0.32))
            _draw_curved_ink_arrow(d2, arr_x0, arr_y0, arr_x1, arr_y1, ACCENT + (235,), width=11, ctrl_pt=(ctrl_x, ctrl_y), draw_progress=arrow_prog)

        else:
            # Preview 1 (No Sticker): Gently offset 5.2% watermark + Per-Line Swipes strictly inside ~80% width
            num_m = re.search(r"([0-9]+)", stat_txt)
            wm_str = num_m.group(1) if num_m else stat_txt.split()[0]
            wm_im = text_layer(wm_str, 720, INK, font_role="hero")
            if wm_im.width > int(W2 * 0.88):
                wm_im = text_layer(wm_str, int(720 * (W2 * 0.84) / max(1, wm_im.width)), INK, font_role="hero")
            wm_b = list(wm_im.split())
            wm_b[3] = wm_b[3].point(lambda v: int(v * 0.052))
            wm_im = Image.merge("RGBA", wm_b)
            overlay2.alpha_composite(wm_im, (W2 // 2 - wm_im.width // 2 + 28, int(H2 * 0.39) - wm_im.height // 2 - 20))

            stat_raw, line_boxes = render_wrapped_text_block(
                stat_txt, "hero", start_size=int(480 * ease_s), min_size=220,
                max_w=int(W2 * 0.80), max_h=int(H2 * 0.24), color=INK, max_lines=2, return_line_boxes=True
            )
            stat_block = _text_with_offset_shadow(stat_raw, dx=10, dy=12)
            sub_block = render_wrapped_text_block(
                sub_txt.upper(), "annotation", start_size=126, min_size=88,
                max_w=int(W2 * 0.80), max_h=int(H2 * 0.12), color=ACCENT, max_lines=2
            ) if sub_txt else None

            tot_h = stat_block.height + (56 + sub_block.height if sub_block else 0)
            txt_top = int(H2 * 0.425) - tot_h // 2
            bx_stat = W2 // 2 - stat_block.width // 2

            _draw_per_line_highlighters(overlay2, bx_stat, txt_top, line_boxes, SUB_ACCENT + (138,), pad_x=40)
            _draw_radial_ticks(d2, bx_stat - 14, txt_top + 14, scale=1.55, color=ACCENT + (228,))
            overlay2.alpha_composite(stat_block, (bx_stat, txt_top))

            cur_y = txt_top + stat_block.height
            if sub_block:
                rule_w = min(int(W2 * 0.74), stat_raw.width)
                d2.rounded_rectangle((W2 // 2 - rule_w // 2, cur_y + 18, W2 // 2 + rule_w // 2, cur_y + 30), radius=6, fill=ACCENT + (240,))
                overlay2.alpha_composite(sub_block, (W2 // 2 - sub_block.width // 2, cur_y + 52))

    else:
        # Long (16:9): Clean authoritative widescreen editorial composition with registration corners & per-line highlighters
        _draw_editorial_corner_ticks(d2, 120, 120, W2 - 120, H2 - 140, INK + (52,), arm=52, width=6)
        if has_sticker:
            left_cx = int(W2 * 0.34)
            left_max_w = int(W2 * 0.46)
            stat_raw, line_boxes = render_wrapped_text_block(
                stat_txt, "hero", start_size=int(360 * ease_s), min_size=180,
                max_w=left_max_w, max_h=int(H2 * 0.38), color=INK, max_lines=2, return_line_boxes=True
            )
            stat_block = _text_with_offset_shadow(stat_raw, dx=9, dy=11)
            sub_block = render_wrapped_text_block(
                sub_txt.upper(), "annotation", start_size=122, min_size=80,
                max_w=int(left_max_w * 0.94), max_h=int(H2 * 0.16), color=ACCENT, max_lines=2
            ) if sub_txt else None

            tot_h = stat_block.height + (44 + sub_block.height if sub_block else 0)
            cur_y = int(H2 * 0.44) - tot_h // 2
            bx_stat = left_cx - stat_block.width // 2
            _draw_per_line_highlighters(overlay2, bx_stat, cur_y, line_boxes, SUB_ACCENT + (135,), pad_x=40)
            overlay2.alpha_composite(stat_block, (bx_stat, cur_y))
            cur_y += stat_block.height
            if sub_block:
                rule_w = min(int(left_max_w * 0.72), stat_raw.width)
                d2.line((left_cx - rule_w // 2, cur_y + 14, left_cx + rule_w // 2, cur_y + 10), fill=ACCENT + (240,), width=11)
                overlay2.alpha_composite(sub_block, (left_cx - sub_block.width // 2, cur_y + 42))

            right_cx = int(W2 * 0.74)
            stk_img = fit_sticker_in_box(sticker_im, max_w=int(W2 * 0.35), max_h=int(H2 * 0.52))
            if stk_img:
                stk_cy = int(H2 * 0.44)
                bp = _soft_backdrop_halo(stk_img.width, stk_img.height, base_rgb=SUB_ACCENT, peak_alpha=42)
                overlay2.alpha_composite(bp, (right_cx - bp.width // 2, stk_cy - bp.height // 2))
                _draw_elliptical_ground_shadow(overlay2, right_cx, stk_cy + stk_img.height // 2 + 16, stk_img.width)
                stk_sh = add_sticker_drop_shadow(stk_img, offset=(10, 14), shadow_color=(0, 0, 0, 42), blur_radius=12)
                overlay2.alpha_composite(stk_sh, (right_cx - stk_sh.width // 2, stk_cy - stk_sh.height // 2))
                arrow_prog = min(1.0, max(0.0, (dt - 0.28) / 0.32))
                # Graceful arched draw-on arrow from first headline line shoulder directly toward sticker upper-left alpha flank
                hdr_top = int(H2 * 0.44) - tot_h // 2
                l0_x, l0_y, l0_w, l0_h = line_boxes[0]
                ax0 = min(int(W2 * 0.48), bx_stat + l0_x + l0_w + 68)
                ay0 = max(int(H2 * 0.18), hdr_top + l0_y + int(l0_h * 0.32))

                stk_x0 = right_cx - stk_img.width // 2
                stk_y0 = stk_cy - stk_img.height // 2
                ax1 = stk_x0 - 52
                ay1 = stk_y0 + int(stk_img.height * 0.28)
                try:
                    a16 = np.array(stk_img.split()[3])
                    y_hi = max(1, int(stk_img.height * 0.48))
                    r16, c16 = np.where(a16[:y_hi, :] > 120)
                    if len(c16) > 0:
                        k16 = int(np.argmin(c16))
                        ax1 = stk_x0 + int(c16[k16]) - 54
                        ay1 = stk_y0 + int(r16[k16])
                except Exception:
                    pass
                # Ensure arrow stays cleanly above the 2nd line / bottom of headline block
                ax0 = min(ax0, ax1 - 180)
                ay1 = min(ay1, hdr_top + l0_y + l0_h + 120)
                ctrl_x = (ax0 + ax1) * 0.50
                ctrl_y = max(int(H2 * 0.11), min(ay0, ay1) - 145)
                _draw_curved_ink_arrow(d2, ax0, ay0, ax1, ay1, ACCENT + (235,), width=11,
                                       ctrl_pt=(ctrl_x, ctrl_y), draw_progress=arrow_prog)
        else:
            max_w = int(W2 * 0.80)
            stat_raw, line_boxes = render_wrapped_text_block(
                stat_txt, "hero", start_size=int(460 * ease_s), min_size=220,
                max_w=max_w, max_h=int(H2 * 0.40), color=INK, max_lines=2, return_line_boxes=True
            )
            stat_block = _text_with_offset_shadow(stat_raw, dx=10, dy=12)
            sub_block = render_wrapped_text_block(
                sub_txt.upper(), "annotation", start_size=132, min_size=84,
                max_w=int(max_w * 0.88), max_h=int(H2 * 0.16), color=ACCENT, max_lines=2
            ) if sub_txt else None
            tot_h = stat_block.height + (48 + sub_block.height if sub_block else 0)
            cur_y = int(H2 * 0.44) - tot_h // 2
            bx_stat = W2 // 2 - stat_block.width // 2
            _draw_per_line_highlighters(overlay2, bx_stat, cur_y, line_boxes, SUB_ACCENT + (135,), pad_x=48)
            _draw_radial_ticks(d2, bx_stat - 16, cur_y + 16, scale=1.5, color=ACCENT + (225,))
            overlay2.alpha_composite(stat_block, (bx_stat, cur_y))
            cur_y += stat_block.height
            if sub_block:
                rule_w = min(int(max_w * 0.64), stat_raw.width)
                d2.rounded_rectangle((W2 // 2 - rule_w // 2, cur_y + 14, W2 // 2 + rule_w // 2, cur_y + 26), radius=6, fill=ACCENT + (240,))
                overlay2.alpha_composite(sub_block, (W2 // 2 - sub_block.width // 2, cur_y + 46))

    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    return fr


def draw_split_compare(w, h, text, is_shorts=False, dt=0.0, left_sticker=None, right_sticker=None, left_stamp=None, right_stamp=None, duration=3.5):
    """Archetype 4: Aspect-Aware Progressive Split Contrast (Smooth Feathered Transition, Tight Integrated Badges, Scaled-Up 16:9 Headers & Backplate Depth)."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    def _split_badge_body(raw_side, fallback_badge):
        if ":" in raw_side:
            b, _, rest = raw_side.partition(":")
            return b.strip().upper(), rest.strip().upper()
        return fallback_badge, raw_side.strip().upper()

    parts = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else ["MYTH", "REALITY"]
    raw_left = parts[0] if len(parts) > 0 else "MYTH"
    raw_right = parts[1] if len(parts) > 1 else "REALITY"
    badge_l, body_l = _split_badge_body(raw_left, "MYTH")
    badge_r, body_r = _split_badge_body(raw_right, "REALITY")

    # Auto-resolve 2nd balanced sticker if only 1 was provided so BOTH sides have equal weight!
    if left_sticker and not right_sticker:
        right_sticker = _auto_resolve_second_split_sticker(left_sticker, raw_right)
    elif right_sticker and not left_sticker:
        left_sticker = _auto_resolve_second_split_sticker(right_sticker, raw_left)

    eff_left_stamp = left_stamp or "stamp_x"
    eff_right_stamp = right_stamp or "stamp_check"

    left_alpha = min(1.0, max(0.0, dt / 0.25)) if dt < 0.25 else 1.0
    reveal_t = max(0.7, min(1.4, duration * 0.38))
    right_alpha = min(1.0, max(0.0, (dt - reveal_t) / 0.30)) if dt >= reveal_t else 0.10

    if is_shorts:
        # 9:16 Vertical Shorts: Exact 50/50 full-bleed top/bottom split (Y = 50% divider, zero bottom beige cutoff strip)
        div_y = H2 // 2
        top_box = (0, int(H2 * 0.08), W2, int(H2 * 0.43))
        bot_box = (0, int(H2 * 0.52), W2, int(H2 * 0.77))

        top_tint = Image.new("RGBA", (W2, div_y), (255, 228, 210, 148))
        bot_tint = Image.new("RGBA", (W2, H2 - div_y), (212, 236, 250, 155))
        overlay2.alpha_composite(top_tint, (0, 0))
        overlay2.alpha_composite(bot_tint, (0, div_y))

        # Full-width horizontal dashed ink divider across exact Y = 50%
        curr_x = int(W2 * 0.05)
        end_x = int(W2 * 0.95)
        while curr_x < end_x:
            d2.line((curr_x, div_y, min(end_x, curr_x + 42), div_y), fill=INK + (230,), width=10)
            curr_x += 70

        panels = [
            (top_box, badge_l, body_l, (208, 48, 38), left_sticker, eff_left_stamp, left_alpha),
            (bot_box, badge_r, body_r, (28, 152, 82), right_sticker, eff_right_stamp, right_alpha),
        ]

        for (bx0, by0, bx1, by1), badge_txt, body_txt, accent_col, stk_src, stmp_tok, side_alpha in panels:
            p_layer = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
            pd = ImageDraw.Draw(p_layer)
            p_h = by1 - by0
            p_cy = (by0 + by1) // 2

            txt_x0 = int(W2 * 0.07)
            txt_w = int(W2 * 0.47)
            txt_cx = txt_x0 + txt_w // 2

            hdr_im = render_wrapped_text_block(
                badge_txt, "hero", start_size=148, min_size=96,
                max_w=int(txt_w * 0.78), max_h=int(p_h * 0.34), color=accent_col, max_lines=1
            )
            body_im = render_wrapped_text_block(
                body_txt, "annotation", start_size=96, min_size=68,
                max_w=txt_w, max_h=int(p_h * 0.42), color=INK, max_lines=3
            ) if body_txt and body_txt != badge_txt else None

            tot_h = hdr_im.height + (34 + body_im.height if body_im else 0)
            cur_y = p_cy - tot_h // 2

            # Tight Badge Integration directly beside header!
            st_badge = draw_myth_stamp(stmp_tok, dt, target_size=132, compact=True) if stmp_tok else None
            gap_b = 24 if st_badge else 0
            cluster_w = hdr_im.width + gap_b + (st_badge.width if st_badge else 0)
            hdr_x = txt_cx - cluster_w // 2
            _draw_highlighter_swipe(p_layer, hdr_x + hdr_im.width // 2, cur_y + hdr_im.height // 2 + 6,
                                    min(txt_w, hdr_im.width + 72), int(hdr_im.height * 0.60), accent_col + (48,))
            p_layer.alpha_composite(hdr_im, (hdr_x, cur_y))
            if st_badge:
                p_layer.alpha_composite(st_badge, (hdr_x + hdr_im.width + gap_b, cur_y + (hdr_im.height - st_badge.height) // 2))
            cur_y += hdr_im.height + 12
            uw = min(int(txt_w * 0.85), cluster_w + 24)
            pd.line((txt_cx - uw // 2, cur_y, txt_cx + uw // 2, cur_y - 2), fill=accent_col + (240,), width=10)
            if body_im:
                p_layer.alpha_composite(body_im, (txt_cx - body_im.width // 2, cur_y + 20))

            # Right 40% of row: Crisp Balanced Sticker + Soft Radial Backplate
            vis_x0 = int(W2 * 0.56)
            vis_w = int(W2 * 0.38)
            vis_cx = vis_x0 + vis_w // 2

            if stk_src:
                s_im = fit_sticker_in_box(stk_src, max_w=int(vis_w * 0.90), max_h=int(p_h * 0.84))
                if s_im:
                    bp = _soft_backdrop_halo(s_im.width, s_im.height, base_rgb=(255, 252, 246), peak_alpha=72)
                    p_layer.alpha_composite(bp, (vis_cx - bp.width // 2, p_cy - bp.height // 2))
                    s_sh = add_sticker_drop_shadow(s_im, offset=(10, 14), shadow_color=(0, 0, 0, 44), blur_radius=10)
                    sx = max(vis_x0, min(W2 - 40 - s_sh.width, vis_cx - s_sh.width // 2))
                    sy = max(by0 + 16, min(by1 - 16 - s_sh.height, p_cy - s_sh.height // 2))
                    _draw_elliptical_ground_shadow(p_layer, vis_cx, sy + s_sh.height - 20, s_im.width)
                    p_layer.alpha_composite(s_sh, (sx, sy))

            if side_alpha < 0.999:
                sb = list(p_layer.split())
                sb[3] = sb[3].point(lambda v: int(v * side_alpha))
                p_layer = Image.merge("RGBA", sb)
            overlay2.alpha_composite(p_layer)
    else:
        # 16:9 Widescreen Long: Full-height Left vs Right Vertical Split with ~35% Larger Authoritative Headers & Backplates
        div_x = W2 // 2
        left_tint = Image.new("RGBA", (div_x, H2), (255, 228, 210, 148))
        right_tint = Image.new("RGBA", (W2 - div_x, H2), (212, 236, 250, 155))
        overlay2.alpha_composite(left_tint, (0, 0))
        overlay2.alpha_composite(right_tint, (div_x, 0))

        top_div_y = int(H2 * 0.05)
        bot_div_y = int(H2 * 0.95)
        curr_y = top_div_y
        while curr_y < bot_div_y:
            d2.line((div_x, curr_y, div_x, min(bot_div_y, curr_y + 42)), fill=INK + (230,), width=10)
            curr_y += 70

        margin = 76
        gutter = 48
        sides = [
            ((margin, top_div_y, div_x - gutter, bot_div_y - 110), badge_l, body_l, (208, 48, 38), left_sticker, eff_left_stamp, left_alpha),
            ((div_x + gutter, top_div_y, W2 - margin, bot_div_y - 110), badge_r, body_r, (28, 152, 82), right_sticker, eff_right_stamp, right_alpha),
        ]

        for (bx0, by0, bx1, by1), badge_txt, body_txt, accent_col, stk_src, stmp_tok, side_alpha in sides:
            side_layer = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
            sd = ImageDraw.Draw(side_layer)
            lane_w = bx1 - bx0
            lane_cx = (bx0 + bx1) // 2
            avail_w = lane_w - 60

            # Scaled up ~35% on 16:9 (192px -> 128px @ 2x) with compact X/check badge integrated tightly beside header
            hdr_im = render_wrapped_text_block(
                badge_txt, "hero", start_size=192, min_size=128,
                max_w=int(avail_w * 0.78), max_h=240, color=accent_col, max_lines=1
            )
            st_badge = draw_myth_stamp(stmp_tok, dt, target_size=160, compact=True) if stmp_tok else None
            gap_b = 30 if st_badge else 0
            cluster_w = hdr_im.width + gap_b + (st_badge.width if st_badge else 0)
            hdr_x = lane_cx - cluster_w // 2

            cur_y = by0 + 36
            _draw_highlighter_swipe(side_layer, hdr_x + hdr_im.width // 2, cur_y + hdr_im.height // 2 + 8,
                                    min(avail_w, hdr_im.width + 96), int(hdr_im.height * 0.60), accent_col + (48,))
            side_layer.alpha_composite(hdr_im, (hdr_x, cur_y))
            if st_badge:
                side_layer.alpha_composite(st_badge, (hdr_x + hdr_im.width + gap_b, cur_y + (hdr_im.height - st_badge.height) // 2))

            cur_y += hdr_im.height + 16
            uw = min(int(avail_w * 0.80), cluster_w + 30)
            sd.line((lane_cx - uw // 2, cur_y, lane_cx + uw // 2, cur_y - 2), fill=accent_col + (240,), width=11)
            cur_y += 28

            if body_txt and body_txt != badge_txt:
                body_im = render_wrapped_text_block(
                    body_txt, "annotation", start_size=108, min_size=72,
                    max_w=int(avail_w * 0.94), max_h=int((by1 - cur_y) * 0.28), color=INK, max_lines=2
                )
                side_layer.alpha_composite(body_im, (lane_cx - body_im.width // 2, cur_y))
                cur_y += body_im.height + 24

            vis_h = max(160, (by1 - 24) - cur_y)
            vis_cy = cur_y + vis_h // 2

            if stk_src:
                s_im = fit_sticker_in_box(stk_src, max_w=int(avail_w * 0.84), max_h=int(vis_h * 0.86))
                if s_im:
                    bp = _soft_backdrop_halo(s_im.width, s_im.height, base_rgb=(255, 252, 246), peak_alpha=78)
                    side_layer.alpha_composite(bp, (lane_cx - bp.width // 2, vis_cy - bp.height // 2))
                    s_sh = add_sticker_drop_shadow(s_im, offset=(10, 14), shadow_color=(0, 0, 0, 44), blur_radius=10)
                    sx = max(bx0 + 16, min(bx1 - s_sh.width - 16, lane_cx - s_sh.width // 2))
                    sy = max(cur_y, min(by1 - s_sh.height - 16, vis_cy - s_sh.height // 2))
                    _draw_elliptical_ground_shadow(side_layer, lane_cx, sy + s_sh.height - 22, s_im.width)
                    side_layer.alpha_composite(s_sh, (sx, sy))

            if side_alpha < 0.999:
                sb = list(side_layer.split())
                sb[3] = sb[3].point(lambda v: int(v * side_alpha))
                side_layer = Image.merge("RGBA", sb)
            overlay2.alpha_composite(side_layer)

    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    return fr


def draw_data_timeline(w, h, text, is_shorts=False, dt=0.0, accent_sticker=None, duration=4.0):
    """Archetype 6: Mobile-Readable Editorial Timeline Infographic (Per-Row Contextual Stickers from Stickman-Stickers Vault, Bold Typography, Accent Left Stripes)."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    title_str = "THE COLLAPSE TIMELINE"
    raw_body = text
    if ";" in text:
        title_str, _, raw_body = text.partition(";")
        title_str = title_str.strip().upper()
    parts = [p.strip() for p in raw_body.split("|") if p.strip()] if "|" in raw_body else ["1200 BC: MEGADROUGHT", "1190 BC: INVASION", "1177 BC: TOTAL COLLAPSE"]
    n_blocks = max(1, min(5, len(parts)))
    parts = parts[:n_blocks]

    prog = min(1.0, dt / max(1.2, duration * 0.72))
    visible_float = prog * n_blocks
    accent_cycle = [(58, 134, 212), (218, 140, 42), (96, 152, 86), ACCENT]

    climax_idx = n_blocks - 1
    used_stks = set()
    if accent_sticker and os.path.exists(str(accent_sticker)):
        used_stks.add(os.path.abspath(str(accent_sticker)))

    # Pre-resolve unique contextual sticker for EVERY timeline step so zero rows look empty!
    row_stickers = [None] * n_blocks
    if accent_sticker:
        row_stickers[climax_idx] = accent_sticker
    for i, seg in enumerate(parts):
        if row_stickers[i] is None:
            row_stickers[i] = _resolve_timeline_row_sticker(seg, used_stks)

    if is_shorts:
        hdr_im = render_wrapped_text_block(title_str, "hero", 142, 96, int(W2 * 0.86), 195, INK, max_lines=1)
        hdr_y = int(H2 * 0.08)
        _draw_highlighter_swipe(overlay2, W2 // 2, hdr_y + hdr_im.height // 2 + 6,
                                min(int(W2 * 0.90), hdr_im.width + 94), int(hdr_im.height * 0.60), SUB_ACCENT + (138,))
        overlay2.alpha_composite(hdr_im, (W2 // 2 - hdr_im.width // 2, hdr_y))
        d2.line((int(W2 * 0.14), hdr_y + hdr_im.height + 16, int(W2 * 0.86), hdr_y + hdr_im.height + 14), fill=ACCENT + (235,), width=10)

        spine_x = int(W2 * 0.13)
        strip_x0 = int(W2 * 0.225)
        strip_x1 = int(W2 * 0.93)
        y_start = int(H2 * 0.225)
        y_end = int(H2 * 0.66)
        step_dy = (y_end - y_start) // max(1, n_blocks - 1) if n_blocks > 1 else 0
        row_h = min(335, int(step_dy * 0.80)) if n_blocks > 1 else 335

        if n_blocks > 1 and prog > 0.05:
            line_prog = min(1.0, prog * 1.05)
            d2.line((spine_x, y_start, spine_x, int(y_start + (y_end - y_start) * line_prog)), fill=INK + (220,), width=12)
            for ci in range(n_blocks - 1):
                if visible_float > ci + 0.5:
                    cy_ch = y_start + ci * step_dy + step_dy // 2
                    d2.line((spine_x - 18, cy_ch - 14, spine_x, cy_ch + 8, spine_x + 18, cy_ch - 14), fill=INK + (210,), width=9)

        for i, seg in enumerate(parts):
            node_alpha = min(1.0, max(0.0, visible_float - i * 0.82))
            if node_alpha <= 0.05:
                continue
            ny = y_start + i * step_dy
            is_climax = (i == climax_idx)
            col = ACCENT if is_climax else accent_cycle[i % len(accent_cycle)]

            node_layer = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
            nd = ImageDraw.Draw(node_layer)

            r = 80
            nd.ellipse((spine_x - r + 7, ny - r + 9, spine_x + r + 7, ny + r + 9), fill=(0, 0, 0, 48))
            nd.ellipse((spine_x - r, ny - r, spine_x + r, ny + r), fill=col + (255,), outline=INK, width=8)
            num_im = text_layer(f"{i+1:02d}", 78, (255, 255, 255) if (is_climax or sum(col) < 420) else INK, font_role="hero")
            node_layer.alpha_composite(num_im, (spine_x - num_im.width // 2, ny - num_im.height // 2 - 4))

            ry0, ry1 = ny - row_h // 2, ny + row_h // 2
            strip_fill = (255, 224, 214, 240) if is_climax else (255, 251, 244, 228)
            strip_out = ACCENT + (245,) if is_climax else INK + (175,)
            strip_w = 8 if is_climax else 5
            nd.rounded_rectangle((strip_x0 + 10, ry0 + 12, strip_x1 + 10, ry1 + 12), radius=34, fill=(0, 0, 0, 42))
            nd.rounded_rectangle((strip_x0, ry0, strip_x1, ry1), radius=34, fill=strip_fill, outline=strip_out, width=strip_w)
            # Crisp thick left color accent stripe inside every row card
            nd.rounded_rectangle((strip_x0 + 14, ry0 + 22, strip_x0 + 32, ry1 - 22), radius=9, fill=col + (240,))

            seg_parts = [sp.strip() for sp in seg.split(":", 1) if sp.strip()]
            h_str = seg_parts[0].upper() if len(seg_parts) > 1 else f"STAGE {i+1}"
            b_str = seg_parts[1] if len(seg_parts) > 1 else seg_parts[0]

            row_stk = row_stickers[i]
            has_row_stk = (row_stk is not None)
            tx0 = strip_x0 + 56
            stk_slot_w = int(row_h * 0.92) + 48
            max_tw = (strip_x1 - tx0 - (stk_slot_w if has_row_stk else 44))

            h_im = render_wrapped_text_block(h_str, "hero", 128, 92, max_tw, int(row_h * 0.44), ACCENT if is_climax else INK, max_lines=1)
            b_im = render_wrapped_text_block(b_str, "annotation", 96, 76, max_tw, int(row_h * 0.44), INK, max_lines=2)
            tot_row_h = h_im.height + 10 + b_im.height
            ty0 = ny - tot_row_h // 2
            node_layer.alpha_composite(h_im, (tx0, ty0))
            node_layer.alpha_composite(b_im, (tx0, ty0 + h_im.height + 10))

            if has_row_stk:
                s_im = fit_sticker_in_box(row_stk, max_w=int(row_h * 0.90), max_h=int(row_h * 0.80))
                if s_im:
                    s_sh = add_sticker_drop_shadow(s_im, offset=(6, 8), shadow_color=(0, 0, 0, 40), blur_radius=7)
                    stk_cx = strip_x1 - stk_slot_w // 2 - 6
                    node_layer.alpha_composite(s_sh, (stk_cx - s_sh.width // 2, ny - s_sh.height // 2))

            if node_alpha < 0.999:
                nb = list(node_layer.split())
                nb[3] = nb[3].point(lambda v: int(v * node_alpha))
                node_layer = Image.merge("RGBA", nb)
            overlay2.alpha_composite(node_layer)
    else:
        hdr_im = render_wrapped_text_block(title_str, "hero", 136, 94, int(W2 * 0.78), 185, INK, max_lines=1)
        hdr_y = int(H2 * 0.09)
        _draw_highlighter_swipe(overlay2, W2 // 2, hdr_y + hdr_im.height // 2 + 6,
                                min(int(W2 * 0.82), hdr_im.width + 90), int(hdr_im.height * 0.58), SUB_ACCENT + (135,))
        overlay2.alpha_composite(hdr_im, (W2 // 2 - hdr_im.width // 2, hdr_y))

        margin_x = 320
        x_start, x_end = margin_x, W2 - margin_x
        spine_y = int(H2 * 0.52)
        step_dx = (x_end - x_start) // max(1, n_blocks - 1) if n_blocks > 1 else 0

        if n_blocks > 1 and prog > 0.05:
            line_prog = min(1.0, prog * 1.05)
            d2.line((x_start, spine_y, int(x_start + (x_end - x_start) * line_prog), spine_y), fill=INK + (210,), width=11)

        for i, seg in enumerate(parts):
            node_alpha = min(1.0, max(0.0, visible_float - i * 0.85))
            if node_alpha <= 0.05:
                continue
            nx = x_start + i * step_dx
            is_climax = (i == climax_idx)
            col = ACCENT if is_climax else accent_cycle[i % len(accent_cycle)]
            node_layer = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
            nd = ImageDraw.Draw(node_layer)

            r = 76
            nd.ellipse((nx - r + 6, spine_y - r + 8, nx + r + 6, spine_y + r + 8), fill=(0, 0, 0, 42))
            nd.ellipse((nx - r, spine_y - r, nx + r, spine_y + r), fill=col + (255,), outline=INK, width=8)
            num_im = text_layer(f"{i+1:02d}", 74, (255, 255, 255) if (is_climax or sum(col) < 420) else INK, font_role="hero")
            node_layer.alpha_composite(num_im, (nx - num_im.width // 2, spine_y - num_im.height // 2 - 4))

            seg_parts = [sp.strip() for sp in seg.split(":", 1) if sp.strip()]
            h_str = seg_parts[0].upper() if len(seg_parts) > 1 else f"PHASE {i+1}"
            b_str = seg_parts[1] if len(seg_parts) > 1 else seg_parts[0]

            col_w = max(280, step_dx - 40)
            h_im = render_wrapped_text_block(h_str, "hero", 96, 66, col_w, 130, col if is_climax else INK, max_lines=2)
            b_im = render_wrapped_text_block(b_str, "annotation", 78, 56, col_w, 180, INK, max_lines=3)
            node_layer.alpha_composite(h_im, (nx - h_im.width // 2, spine_y - r - 30 - h_im.height))
            node_layer.alpha_composite(b_im, (nx - b_im.width // 2, spine_y + r + 28))

            row_stk = row_stickers[i]
            if row_stk:
                s_im = fit_sticker_in_box(row_stk, max_w=240, max_h=240)
                if s_im:
                    s_sh = add_sticker_drop_shadow(s_im, offset=(8, 10), shadow_color=(0, 0, 0, 38), blur_radius=8)
                    node_layer.alpha_composite(s_sh, (nx - s_sh.width // 2, spine_y + r + 42 + b_im.height))

            if node_alpha < 0.999:
                nb = list(node_layer.split())
                nb[3] = nb[3].point(lambda v: int(v * node_alpha))
                node_layer = Image.merge("RGBA", nb)
            overlay2.alpha_composite(node_layer)

    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    return fr


def draw_stat_pie(w, h, text, is_shorts=False, dt=0.0, accent_sticker=None):
    """Archetype 6: Full-Bleed Animated Donut Stat Ring with Marker Highlight & Seamless Sticker."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    parts = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else [text.strip(), "STATISTIC"]
    stat_val = parts[0]
    stat_desc = " ".join(parts[1].split()[:6]) if len(parts) > 1 and parts[1].strip() else ""
    num_m = re.search(r"(\d+(?:\.\d+)?)", stat_val)
    pct = min(100.0, max(0.0, float(num_m.group(1)) if num_m else 75.0))
    has_sticker = (accent_sticker is not None)

    if not is_shorts:
        cx = int(W2 * 0.34) if has_sticker else W2 // 2
        cy = int(H2 * 0.42)
        if has_sticker:
            stk_img = fit_sticker_in_box(accent_sticker, max_w=int(W2 * 0.32), max_h=int(H2 * 0.46))
            if stk_img:
                rcx = int(W2 * 0.74)
                _draw_elliptical_ground_shadow(overlay2, rcx, cy + stk_img.height // 2 + 12, stk_img.width)
                stk_sh = add_sticker_drop_shadow(stk_img, offset=(10, 14), shadow_color=(0, 0, 0, 38), blur_radius=10)
                overlay2.alpha_composite(stk_sh, (rcx - stk_sh.width // 2, cy - stk_sh.height // 2))
    else:
        cx = W2 // 2
        cy = int(H2 * (0.42 if has_sticker else 0.34))
        if has_sticker:
            stk_img = fit_sticker_in_box(accent_sticker, max_w=int(W2 * 0.44), max_h=int(H2 * 0.18))
            if stk_img:
                scy = int(H2 * 0.16)
                _draw_elliptical_ground_shadow(overlay2, cx, scy + stk_img.height // 2 + 8, stk_img.width)
                stk_sh = add_sticker_drop_shadow(stk_img, offset=(8, 12), shadow_color=(0, 0, 0, 38), blur_radius=8)
                overlay2.alpha_composite(stk_sh, (cx - stk_sh.width // 2, scy - stk_sh.height // 2))

    radius = 270 if is_shorts else 320
    ring_thick = 52
    track_col = CARD_OUT + (220,) if sum(CARD_OUT) < 600 else (218, 212, 202, 255)
    d2.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=track_col, width=ring_thick)

    prog = spring_p(min(1.0, dt / 0.95))
    angle = int(360.0 * (pct / 100.0) * prog)
    if angle > 0:
        d2.arc((cx - radius, cy - radius, cx + radius, cy + radius), start=-90, end=-90 + angle, fill=ACCENT + (255,), width=ring_thick)

    num_txt = text_layer(stat_val, 140 if is_shorts else 160, INK, font_role="hero")
    overlay2.alpha_composite(num_txt, (cx - num_txt.width // 2, cy - num_txt.height // 2))

    if stat_desc:
        desc_block = render_wrapped_text_block(stat_desc.upper(), "annotation", 92 if is_shorts else 104, 56, int(W2 * 0.76), 160, INK, max_lines=2)
        dy0 = cy + radius + 56
        _draw_highlighter_swipe(overlay2, cx, dy0 + desc_block.height // 2 + 6, desc_block.width + 68, int(desc_block.height * 0.65), SUB_ACCENT + (110,))
        overlay2.alpha_composite(desc_block, (cx - desc_block.width // 2, dy0))

    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    return fr


def draw_myth_stamp(token, dt, target_size=280, compact=False):
    """Archetype 5: Hand-Drawn Editorial Brush Verdict Accent (clean crimson X or emerald check — zero clunky rubber seal)."""
    target_size = max(120, min(560, target_size))
    sz2 = target_size * 2
    im2 = Image.new("RGBA", (sz2, sz2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(im2)

    tok_lower = str(token).lower()
    is_x = ("x" in tok_lower or "false" in tok_lower or "myth" in tok_lower)
    col = (212, 48, 38, 248) if is_x else (32, 160, 82, 248)
    soft_halo = (212, 48, 38, 44) if is_x else (32, 160, 82, 44)

    if compact:
        # Clean circular corner badge seal (no text overflow at corners of split halves)
        cx, cy = sz2 // 2, sz2 // 2
        r = int(sz2 * 0.41)
        d2.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(252, 249, 242, 232))
        d2.ellipse((cx - r, cy - r, cx + r, cy + r), fill=soft_halo)
        d2.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=max(10, int(sz2 * 0.045)))
        stroke_w = max(22, int(sz2 * 0.085))
        if is_x:
            off = r * 0.48
            d2.line((cx - off, cy - off, cx + off, cy + off), fill=col, width=stroke_w)
            d2.line((cx + off, cy - off, cx - off, cy + off), fill=col, width=stroke_w)
        else:
            d2.line((cx - r * 0.48, cy + 4, cx - r * 0.10, cy + r * 0.40), fill=col, width=stroke_w)
            d2.line((cx - r * 0.10, cy + r * 0.40, cx + r * 0.54, cy - r * 0.36), fill=col, width=stroke_w)
        return im2.resize((target_size, target_size), Image.LANCZOS)

    cx, cy = sz2 // 2, sz2 // 2 - int(sz2 * 0.06)
    r = int(sz2 * 0.34)
    # Subtle soft marker halo behind hand-drawn mark
    d2.ellipse((cx - r, cy - r, cx + r, cy + r), fill=soft_halo)

    stroke_w = max(24, int(sz2 * 0.065))
    if is_x:
        off = r * 0.62
        d2.line((cx - off, cy - off, cx + off, cy + off), fill=col, width=stroke_w)
        d2.line((cx + off, cy - off, cx - off, cy + off), fill=col, width=stroke_w)
    else:
        d2.line((cx - r * 0.65, cy + 6, cx - r * 0.14, cy + r * 0.56), fill=col, width=stroke_w)
        d2.line((cx - r * 0.14, cy + r * 0.56, cx + r * 0.72, cy - r * 0.52), fill=col, width=stroke_w)

    stamp_word = "MYTH" if is_x else "FACT"
    if "false" in tok_lower: stamp_word = "FALSE"
    elif "true" in tok_lower: stamp_word = "TRUE"
    elif "verified" in tok_lower: stamp_word = "VERIFIED"
    elif "debunked" in tok_lower: stamp_word = "DEBUNKED"

    lbl_st = text_layer(stamp_word, int(sz2 * 0.17), col[:3], font_role="hero")
    ly = int(cy + r + 24)
    im2.alpha_composite(lbl_st, (cx - lbl_st.width // 2, ly))
    d2.line((cx - lbl_st.width // 2, ly + lbl_st.height + 6, cx + lbl_st.width // 2, ly + lbl_st.height + 4), fill=col, width=10)

    im = im2.resize((target_size, target_size), Image.LANCZOS)
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

    # Split em-dash or double-hyphen joined words (e.g. HUMANS—MAKING)
    if "—" in txt or "--" in txt:
        sep = "—" if "—" in txt else "--"
        sub_tokens = [st.strip() for st in txt.split(sep) if st.strip()]
        if len(sub_tokens) >= 2:
            dur_total = max(0.01, cur_item["end"] - cur_item["start"])
            frac = min(0.999, max(0.0, dt / dur_total))
            token_idx = int(frac * len(sub_tokens))
            txt = sub_tokens[token_idx]

    pop_scale = 1.0 + 0.16 * max(0.0, 1.0 - dt / 0.08)

    base_font_size = 110 if is_shorts else 88
    font_size = int(base_font_size * pop_scale)
    clean_w_upper = txt.strip('.,!?:;"')
    is_shock_w = clean_w_upper in {"DANGER", "FREEZING", "IMPOSSIBLE", "BLACKOUT", "ATTACK", "FATAL", "SECRET", "TRUTH", "COLLAPSE"}
    font = resolve_font("stamp" if is_shock_w else "caption", font_size)

    b = font.getbbox(txt)
    tw = max(1, b[2] - b[0])
    th = max(1, b[3] - b[1])

    pad_x, pad_y = 36, 18
    bw = tw + pad_x * 2
    bh = th + pad_y * 2

    sub_im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(sub_im)

    # Sleek consistent caption box styling (Rule 58: Hormozi / Vox high-retention pill)
    # Default is premium golden-amber border; red for shock danger; cyan for frost/ice
    if clean_w_upper in {"DANGER", "DEADLY", "EXTINCTION", "PERIL", "ATTACK", "BLAST"}:
        text_fill = (255, 75, 75, 255)
        border_col = (255, 75, 75, 240)
    elif clean_w_upper in {"ICE", "COLD", "FREEZING", "FROST", "WINTER"}:
        text_fill = (75, 225, 255, 255)
        border_col = (75, 225, 255, 240)
    else:
        text_fill = (255, 225, 60, 255)
        border_col = (255, 215, 30, 240)

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
    ap.add_argument("--caption-font", default=None, help="Override kinetic caption font role or TTF path (caption, modern, montserrat, kalam, hero, etc.)")
    ap.add_argument("--subtitles", action="store_true", default=True)
    ap.add_argument("--clip-seconds", type=float, default=None, help="Clip to first N seconds (e.g. short clip from long video)")
    ap.add_argument("--title", default=None, help="Header text for Shorts format")
    ap.add_argument("--scene-labels", action="store_true", default=False, help="Render floating scene label banners (default: False for clean modern sticker-focused visuals)")
    ap.add_argument("--header", action="store_true", default=False, help="Render top title banner in Shorts (default: False to avoid screen clutter)")
    ap.add_argument("--frame", type=float, default=None, help="Render a single still frame at timestamp T seconds and exit")
    ap.add_argument("--frame-out", default="frame.png", help="Output path for single still frame")
    args = ap.parse_args()

    try:
        from anti_pollution import validate_external_output_dir
        validate_external_output_dir(os.getcwd())
        if args.out:
            out_parent = os.path.dirname(os.path.abspath(args.out)) or os.getcwd()
            validate_external_output_dir(out_parent)
    except ImportError:
        pass

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

    if args.caption_font:
        cf = args.caption_font.lower()
        if cf in FONT_PATHS and os.path.exists(FONT_PATHS[cf]):
            FONT_PATH = FONT_PATHS[cf]
        elif os.path.exists(args.caption_font):
            FONT_PATH = args.caption_font

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
                line_id = r.get("line", "").strip()
                if line_id:
                    w_clean = r["word"].lower().strip('.,!?":;')
                    for lk in {line_id, line_id.zfill(2), line_id.lstrip("0") or "0"}:
                        if f"@{lk}" not in words_map:
                            words_map[f"@{lk}"] = start_t
                            words_map[lk] = start_t
                        words_map[f"@{lk}:{w_clean}"] = start_t
                        words_map[f"{lk}:{w_clean}"] = start_t
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
    # Deduplicate same-timestamp scene rows (keep last explicit beat, preserve any overlays)
    dedup_scenes = []
    for sc in scenes:
        if dedup_scenes and abs(sc["t0"] - dedup_scenes[-1]["t0"]) < 0.05:
            prev_ovs = dedup_scenes[-1].get("ov", [])
            sc["ov"] = prev_ovs + sc.get("ov", [])
            dedup_scenes[-1] = sc
        else:
            dedup_scenes.append(sc)
    scenes = dedup_scenes
    
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

    # Keep all scene-attached overlays natural across parent scene duration (multi-sticker diagrams supported!)
    all_overlays.sort(key=lambda o: o["t"])

    # Apply DIRECTOR_PLAN.json choreography, exact spoken word-sync (-0.06s), & logical filter if present
    director_plan_path = os.path.join(os.path.dirname(os.path.abspath(args.scenes)) or ".", "DIRECTOR_PLAN.json")
    if os.path.exists(director_plan_path):
        try:
            d_plan = json.load(open(director_plan_path, encoding="utf-8"))
            d_scenes = d_plan.get("scenes", [])
            for d_sc in d_scenes:
                d_t0 = float(d_sc.get("t0", -1.0))
                match_sc = min(scenes, key=lambda s: abs(s["t0"] - d_t0)) if scenes else None
                if match_sc and abs(match_sc["t0"] - d_t0) < 0.25:
                    match_sc["_group_pattern"] = d_sc.get("group_pattern", "solo_focus")
                    match_sc["_camera_move"] = d_sc.get("camera_move", "")
                    filtered_ovs = []
                    for o_i, ov in enumerate(match_sc["ov"]):
                        d_ov = None
                        for cand_do in d_sc.get("overlays", []):
                            if cand_do.get("idx") == o_i or os.path.basename(cand_do.get("img", "")) == os.path.basename(ov["img"]):
                                d_ov = cand_do
                                break
                        if d_ov:
                            if d_ov.get("status") == "REJECTED_REDUNDANT":
                                print(f"🎬 [Director Supervisor] Skipped redundant sticker '{ov['img']}' in scene {match_sc['cue']}: {d_ov.get('reason','')}")
                                continue
                            ov["t"] = float(d_ov.get("sync_t", ov["t"]))
                            ov["_motion_archetype"] = d_ov.get("motion_archetype", "")
                            ov["_rest_tilt_deg"] = float(d_ov.get("rest_tilt_deg", 0.0))
                            ov["_arrow_to_next"] = bool(d_ov.get("arrow_to_next", False))
                            ov["_director_synced"] = True
                        filtered_ovs.append(ov)
                    match_sc["ov"] = filtered_ovs
        except Exception as dp_err:
            print(f"⚠️ DIRECTOR_PLAN.json notice: {dp_err}")

    for sc in scenes:
        sc["ov"].sort(key=lambda o: o["t"])
        # Stagger only non-director-synced overlays that share exact timestamp
        cluster_idx = 0
        prev_raw_t = None
        for o in sc["ov"]:
            raw_t = o["t"]
            if not o.get("_director_synced") and prev_raw_t is not None and abs(raw_t - prev_raw_t) < 0.08:
                cluster_idx += 1
                stagger = min(0.45, cluster_idx * 0.12)
                if raw_t + stagger < sc["t1"] - 0.8:
                    o["t"] = raw_t + stagger
            else:
                cluster_idx = 0
                prev_raw_t = raw_t

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

    # Runtime Compositing Counter & Telemetry
    rendered_stickers_counter = [0]
    rendered_unique_stickers = set()
    rendered_stickers_telemetry = []
    overlay_anchor_cache = {}

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

        # Background composition: 6-Archetype Visual Variety Engine
        token = os.path.basename(img_path)
        token_base = os.path.splitext(token)[0]
        token_key = token_base.split(":")[0].strip()

        is_stat_card = (token in ("card", "card_stat", "card_phrase") or token_base in ("card", "card_stat", "card_phrase") or token_key in ("card", "card_stat", "card_phrase") or token.startswith("card_"))
        is_split_card = (token in ("split_compare", "split_contrast") or token_base in ("split_compare", "split_contrast") or token_key in ("split_compare", "split_contrast") or token.startswith("split_"))
        is_timeline_card = (token in ("bar_timeline", "timeline") or token_base in ("bar_timeline", "timeline") or token_key in ("bar_timeline", "timeline") or token.startswith(("timeline_", "bar_")))
        is_pie_card = (token in ("stat_pie", "stat_ring") or token_base in ("stat_pie", "stat_ring") or token_key in ("stat_pie", "stat_ring") or token.startswith("stat_"))
        is_native_archetype = (is_stat_card or is_split_card or is_timeline_card or is_pie_card)

        # Collect stickers ONLY if current scene is an archetype card that actually embeds them natively
        paired_stk = None
        left_stk = None
        right_stk = None
        left_stmp = None
        right_stmp = None
        natively_consumed_indices = set()

        if is_native_archetype:
            for idx, o in enumerate(sc.get("ov", [])):
                o_img = o.get("img", "").strip()
                o_pos = str(o.get("pos", "")).lower()
                if o_img in ("stamp_x", "stamp_false", "stamp_myth"):
                    if "left" in o_pos or not left_stmp:
                        left_stmp = o_img
                    else:
                        right_stmp = o_img
                    natively_consumed_indices.add(idx)
                    rendered_stickers_counter[0] += 1
                    rendered_unique_stickers.add(o_img)
                elif o_img in ("stamp_check", "stamp_true"):
                    if "right" in o_pos or not right_stmp:
                        right_stmp = o_img
                    else:
                        left_stmp = o_img
                    natively_consumed_indices.add(idx)
                    rendered_stickers_counter[0] += 1
                    rendered_unique_stickers.add(o_img)
                elif o_img not in ("tag", "count") and not o_img.startswith("bars:"):
                    res_path = resolve_sticker_path(o_img)
                    if res_path:
                        if is_split_card:
                            if "left" in o_pos and not left_stk:
                                left_stk = res_path
                                natively_consumed_indices.add(idx)
                                rendered_stickers_counter[0] += 1
                                rendered_unique_stickers.add(o_img)
                            elif "right" in o_pos and not right_stk:
                                right_stk = res_path
                                natively_consumed_indices.add(idx)
                                rendered_stickers_counter[0] += 1
                                rendered_unique_stickers.add(o_img)
                            elif not left_stk:
                                left_stk = res_path
                                natively_consumed_indices.add(idx)
                                rendered_stickers_counter[0] += 1
                                rendered_unique_stickers.add(o_img)
                            elif not right_stk:
                                right_stk = res_path
                                natively_consumed_indices.add(idx)
                                rendered_stickers_counter[0] += 1
                                rendered_unique_stickers.add(o_img)
                        elif not paired_stk:
                            paired_stk = res_path
                            natively_consumed_indices.add(idx)
                            rendered_stickers_counter[0] += 1
                            rendered_unique_stickers.add(o_img)

            if not paired_stk and sc.get("space"):
                res_sp = resolve_sticker_path(sc["space"])
                if res_sp:
                    paired_stk = res_sp
        token_base = os.path.splitext(token)[0]
        token_key = token_base.split(":")[0].strip()
        if token in ("card", "card_stat", "card_phrase") or token_base in ("card", "card_stat", "card_phrase") or token_key in ("card", "card_stat", "card_phrase") or token.startswith("card_") or token_base.startswith("card_") or token_key.startswith("card_"):
            fr = draw_card_stat(W, H, text, is_shorts=is_shorts, dt=dt_scene, sticker_im=paired_stk)
        elif token in ("split_compare", "split_contrast") or token_base in ("split_compare", "split_contrast") or token_key in ("split_compare", "split_contrast") or token.startswith("split_") or token_base.startswith("split_") or token_key.startswith("split_"):
            fr = draw_split_compare(W, H, text, is_shorts=is_shorts, dt=dt_scene,
                                   left_sticker=left_stk, right_sticker=right_stk,
                                   left_stamp=left_stmp, right_stamp=right_stmp, duration=dur)
        elif token in ("bar_timeline", "timeline") or token_base in ("bar_timeline", "timeline") or token_key in ("bar_timeline", "timeline") or token.startswith(("timeline_", "bar_")) or token_base.startswith(("timeline_", "bar_")) or token_key.startswith(("timeline_", "bar_")):
            fr = draw_data_timeline(W, H, text, is_shorts=is_shorts, dt=dt_scene, accent_sticker=paired_stk, duration=dur)
        elif token in ("stat_pie", "stat_ring") or token_base in ("stat_pie", "stat_ring") or token_key in ("stat_pie", "stat_ring") or token.startswith("stat_") or token_base.startswith("stat_") or token_key.startswith("stat_"):
            fr = draw_stat_pie(W, H, text, is_shorts=is_shorts, dt=dt_scene, accent_sticker=paired_stk)
        elif img_path not in img_cache:
            fr = draw_card_stat(W, H, text, is_shorts=is_shorts, dt=dt_scene, sticker_im=paired_stk)
        else:
            raw = img_cache[img_path]

            is_vertical_img = (raw.height >= raw.width * 1.15)
            is_landscape_img = (raw.width >= raw.height * 1.15)

            # Explicit director-driven eased camera motion (zero stacked zoom crops or parity bounce)
            def _smooth_shot_motion(src_im, out_w, out_h, t_flags, u_prog, cam_move=""):
                ease = 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, u_prog)))
                mv = (cam_move or "").strip().lower()
                if not mv:
                    for tok_m in ("pan_left", "pan_right", "zoom_in_tight", "crop_focus", "pull_back", "push_in", "static"):
                        if tok_m in t_flags:
                            mv = "zoom_in_tight" if tok_m == "crop_focus" else tok_m
                            break
                if mv == "static":
                    return src_im.resize((out_w, out_h), Image.LANCZOS)
                if mv == "pan_left":
                    scale = 1.12
                    dx_frac = 0.45 - 0.90 * ease
                    dy_frac = 0.0
                elif mv == "pan_right":
                    scale = 1.12
                    dx_frac = -0.45 + 0.90 * ease
                    dy_frac = 0.0
                elif mv == "zoom_in_tight":
                    scale = 1.02 + 0.12 * ease
                    dx_frac = 0.0
                    dy_frac = -0.05 * ease
                elif mv == "pull_back":
                    scale = 1.045 - 0.045 * ease
                    dx_frac = 0.02 * (0.5 - ease)
                    dy_frac = -0.015 * ease
                elif mv == "push_in":
                    scale = 1.00 + 0.045 * ease
                    dx_frac = 0.02 * (ease - 0.5)
                    dy_frac = -0.02 * ease
                else:
                    return src_im.resize((out_w, out_h), Image.LANCZOS)

                cw = max(1, int(src_im.width / scale))
                ch = max(1, int(src_im.height / scale))
                avail_x = max(0, src_im.width - cw)
                avail_y = max(0, src_im.height - ch)
                cx = max(0, min(avail_x, int(avail_x * (0.5 + dx_frac))))
                cy = max(0, min(avail_y, int(avail_y * (0.5 + dy_frac))))
                return src_im.crop((cx, cy, cx + cw, cy + ch)).resize((out_w, out_h), Image.LANCZOS)

            cam_move_str = sc.get("_camera_move", "")
            if is_shorts:
                if is_vertical_img:
                    fr = _smooth_shot_motion(raw, W, H, trans_type, u, cam_move_str)
                elif raw.width == 1 and raw.height == 1:
                    fr = card_bg(W, H).convert("RGBA")
                else:
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
                    fr = _smooth_shot_motion(raw, W, H, trans_type, u, cam_move_str)
                else:
                    cached_bg = bg_cache.get(img_path)
                    fr = cached_bg.copy() if cached_bg else card_bg(W, H).convert("RGBA")
                    pillar_h = H - 80
                    pillar_w = int(pillar_h * (raw.width / raw.height))
                    pillar_img = raw.resize((pillar_w, pillar_h), Image.LANCZOS)
                    fr.alpha_composite(pillar_img, ((W - pillar_w) // 2, 40))

        # Subtle paper texture and vignette
        if fr.mode != "RGBA":
            fr = fr.convert("RGBA")

        # Capture clean un-shaken frame for stable sticker spatial anchoring
        clean_base_fr = fr.copy()

        # Rule 32: Dynamic Camera Shake & Physical Weight (High-Impact Broadcast Calibration)
        shake_dx, shake_dy = 0, 0

        # Explicit shake or rumble in scene extra
        if "shake" in trans_type and dt_scene < 0.40:
            intensity = ((1.0 - dt_scene / 0.40) ** 1.8) * (26.0 if is_shorts else 32.0)
            shake_dx += int(np.sin(dt_scene * 65.0) * intensity)
            shake_dy += int(np.cos(dt_scene * 75.0) * intensity)
        elif "rumble" in trans_type:
            shake_dx += int(np.sin(t * 30.0) * 4.5)
            shake_dy += int(np.cos(t * 35.0) * 4.5)

        # High-Impact Spoken Word hits
        for impact_t in impact_hit_times:
            dt_imp = t - impact_t
            if 0.0 <= dt_imp <= 0.28:
                intensity = ((1.0 - dt_imp / 0.28) ** 1.8) * 18.0
                shake_dx += int(np.sin(dt_imp * 65.0) * intensity)
                shake_dy += int(np.cos(dt_imp * 75.0) * intensity)
                break
        if shake_dx != 0 or shake_dy != 0:
            fr = fr.transform(fr.size, Image.AFFINE, (1, 0, shake_dx, 0, 1, shake_dy))

        # Zoom Punch Transition (Cinematic 1.12x/1.10x Snap to 1.00x)
        if "zoom_punch" in trans_type and dt_scene < 0.28:
            scale_zp = 1.0 + (0.12 if is_shorts else 0.10) * ((1.0 - dt_scene / 0.28) ** 2)
            cw = int(W / scale_zp)
            ch = int(H / scale_zp)
            fr = fr.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)

        # Black & White / Grayscale / Historical Tragedy
        if "bw" in trans_type or "grayscale" in trans_type or "monochrome" in trans_type:
            gray = fr.convert("L").convert("RGBA")
            fr = Image.blend(fr, gray, 0.92)

        # Danger Crimson / Blood Vignette (Rich atmospheric edge gradient)
        if "blood" in trans_type or "danger" in trans_type or "hazard" in trans_type:
            pulse_v = 0.70 + 0.30 * np.sin(dt_scene * 6.0)
            danger_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dd = ImageDraw.Draw(danger_layer)
            border_w = 160 if is_shorts else 200
            for i in range(0, border_w, 2):
                p_edge = 1.0 - (i / border_w)
                alpha_v = int((p_edge ** 1.5) * 190 * pulse_v)
                dd.rectangle((i, i, W - i, H - i), outline=(225, 20, 20, alpha_v), width=2)
            fr.alpha_composite(danger_layer)

        # Ice / Frost Cyan Vignette (Vibrant freezing atmospheric edge)
        if "ice" in trans_type or "frost" in trans_type or "cold" in trans_type:
            frost_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fd = ImageDraw.Draw(frost_layer)
            border_w = 160 if is_shorts else 200
            for i in range(0, border_w, 2):
                p_edge = 1.0 - (i / border_w)
                alpha_v = int((p_edge ** 1.5) * 185)
                fd.rectangle((i, i, W - i, H - i), outline=(40, 205, 255, alpha_v), width=2)
            fr.alpha_composite(frost_layer)

        # Scene Transition VFX:
        # Clean 0.22s smooth crossfades between calm narrative scenes (crisp cuts for explicit dramatic impacts)
        dt_scene = t - t0
        is_hard_impact = ("zoom_punch" in trans_type or "shake" in trans_type or "danger" in trans_type or "flash" in trans_type)
        if dt_scene < 0.22 and si > 0:
            if "flash" in trans_type:
                flash_p = max(0.0, 1.0 - dt_scene / 0.12)
                flash_layer = Image.new("RGBA", (W, H), (255, 252, 240, int(flash_p * 180)))
                fr.alpha_composite(flash_layer)
            elif "fade" in trans_type or "crossfade" in trans_type or not is_hard_impact:
                prev_img_path = scenes[si - 1]["img"]
                if prev_img_path in img_cache:
                    prev_raw = img_cache[prev_img_path]
                    prev_fr = prev_raw.resize((W, H), Image.LANCZOS) if prev_raw.size != (W, H) else prev_raw
                    blend_alpha = min(1.0, max(0.0, dt_scene / 0.22))
                    fr = Image.blend(prev_fr.convert("RGBA"), fr, blend_alpha)

        # Label Deduplication & Clash Check:
        # Scene heading text label: Suppressed on standard scenes so stickers, art, and captions remain uncluttered.
        # Only displayed on dedicated full-screen title/chapter cards (img_path == "card") or if explicitly requested.
        active_tags = {o["text"].strip().upper() for o in sc["ov"] if o.get("text")}
        token = os.path.basename(img_path)
        token_base = os.path.splitext(token)[0]
        token_key = token_base.split(":")[0].strip()
        is_archetype_card = (token in ("card", "card_stat", "card_phrase", "split_compare", "split_contrast",
                                       "bar_timeline", "timeline", "stat_pie", "stat_ring") or
                             token_base in ("card", "card_stat", "card_phrase", "split_compare", "split_contrast",
                                            "bar_timeline", "timeline", "stat_pie", "stat_ring") or
                             token_key in ("card", "card_stat", "card_phrase", "split_compare", "split_contrast",
                                           "bar_timeline", "timeline", "stat_pie", "stat_ring") or
                             token.startswith(("card_", "split_", "timeline_", "stat_", "bar_")) or
                             token_base.startswith(("card_", "split_", "timeline_", "stat_", "bar_")) or
                             token_key.startswith(("card_", "split_", "timeline_", "stat_", "bar_")))
        if text and (args.scene_labels and not is_archetype_card):
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
                draw_label(fr, text, pos or "auto", W, H, is_shorts)

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
                # Rule 29 & Rule 70: Smart Scene-Locked Duration
                # Hold sticker cleanly until next beat or scene transition (min 2.5s-4.0s hold, no dead screens)
                scene_remaining = max(0.2, t1 - o["t"])
                default_dur = min(scene_remaining, max(2.5, min(4.2, scene_remaining))) if is_shorts else min(scene_remaining, max(3.5, min(6.5, scene_remaining)))
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

        # Multi-Sticker Collision-Free Composition (unlimited simultaneous logical stickers per scene!)
        # Pre-compute spawn-time cohort scaling from scene schedule so stickers NEVER resize or jump mid-display.
        scheduled_spans = []
        for idx_s, os_ov in enumerate(sc["ov"]):
            if idx_s in natively_consumed_indices:
                continue
            rem = max(0.2, t1 - os_ov["t"])
            d_s = min(rem, max(2.5, min(4.2, rem))) if is_shorts else min(rem, max(3.5, min(6.5, rem)))
            for pt in str(os_ov.get("extra", "")).split("|"):
                if pt.startswith("dur:"):
                    try:
                        d_s = float(pt[4:])
                    except Exception:
                        pass
            scheduled_spans.append((idx_s, os_ov["t"], os_ov["t"] + d_s))

        occupied_boxes = []
        scene_drawn_stickers = {}

        for o_idx, o, dt, dur in active_overlays:
            # Peak instantaneous simultaneous count overlapping this overlay's lifetime + cohort rank
            my_t0 = o["t"]
            my_t1 = my_t0 + dur
            probe_pts = [my_t0] + [ot0 for _, ot0, _ in scheduled_spans if my_t0 <= ot0 < my_t1]
            peak_cohort = 1
            for tp in probe_pts:
                ov_cnt = sum(1 for _, a0, a1 in scheduled_spans if a0 <= tp + 0.02 < a1)
                peak_cohort = max(peak_cohort, ov_cnt)
            cohort_members = [idx_s for idx_s, a0, a1 in scheduled_spans if max(my_t0, a0) < min(my_t1, a1) - 0.02]
            cohort_rank = cohort_members.index(o_idx) if o_idx in cohort_members else 0
            cohort_scale = 1.0 if peak_cohort <= 2 else (0.80 if peak_cohort == 3 else 0.72)

            p_ent = min(1.0, dt / 0.36)
            ease_c = 1.0 - (1.0 - p_ent) ** 3
            p = p_ent
            q = spring_p(p_ent)
            alpha = min(1.0, dt / 0.18)

            # Clean 0.22s ease-out exit + subtle retract
            exit_window = min(0.22, max(0.05, dur * 0.45))
            time_left = dur - dt
            exit_p = 1.0
            exit_e = 0.0
            if time_left < exit_window:
                exit_p = max(0.0, time_left / exit_window)
                exit_e = 1.0 - exit_p
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

            # Multi-Slot Collision-Free Anchor Solver (Locked Anchor Cache: zero jitter/teleporting)
            sub_top_y = (1180 - 60) if is_shorts else (H - 150 - 50)
            ov_cache_key = f"{si}_{o_idx}_{o.get('t', 0.0)}"
            if ov_cache_key not in overlay_anchor_cache:
                base_ref = clean_base_fr if 'clean_base_fr' in locals() and clean_base_fr is not None else fr
                usable_w = W - (268 if is_shorts else 108)
                usable_h = max(240, sub_top_y - (250 if is_shorts else 145))
                max_prop_w = int(usable_w * (0.48 if peak_cohort == 1 else (0.39 if peak_cohort == 2 else 0.34)))
                max_prop_h = int(usable_h * (0.50 if peak_cohort == 1 else (0.42 if peak_cohort == 2 else 0.36)))
                norm_scale = min(cohort_scale, max_prop_w / max(1, item_im.width), max_prop_h / max(1, item_im.height))
                scaled_probe_w = max(32, int(item_im.width * norm_scale))
                scaled_probe_h = max(32, int(item_im.height * norm_scale))
                anchor_cx, anchor_cy, slot_q = calculate_intelligent_sticker_anchor(
                    base_ref, scaled_probe_w, scaled_probe_h, pos_str, is_shorts, W, H,
                    occupied_boxes, sub_top_y, slot_bias=o_idx,
                    cohort_size=peak_cohort, cohort_rank=cohort_rank
                )
                overlay_anchor_cache[ov_cache_key] = (anchor_cx, anchor_cy, norm_scale * slot_q)

            target_cx, target_cy, auto_q = overlay_anchor_cache[ov_cache_key]

            # Resolve Context-Aware Motion Archetype from DIRECTOR_PLAN or fallback
            m_arch = o.get("_motion_archetype", "").strip().lower()
            ov_extra = str(o.get("extra", "")).strip().lower()
            if not m_arch:
                if "drop" in ov_extra or "slam" in ov_extra:
                    m_arch = "drop_weight"
                elif "peel" in ov_extra:
                    m_arch = "peel_reveal"
                elif "bloom" in ov_extra:
                    m_arch = "bloom_focus"
                elif "swing" in ov_extra or "strike" in ov_extra:
                    m_arch = "swing_strike"
                elif "slide_left" in ov_extra:
                    m_arch = "slide_arc_left"
                elif "slide_right" in ov_extra:
                    m_arch = "slide_arc_right"
                else:
                    try:
                        import director_supervisor
                        m_arch, _ = director_supervisor._pick_motion_archetype(o_img, "left" if target_cx < W * 0.5 else "right", pos_str)
                    except Exception:
                        m_arch = "slide_arc_left" if target_cx < W * 0.5 else "slide_arc_right"

            # Compute Physics-Based Entry, Squash/Bloom, Alive Breathing & Directional Exit
            scale_x_mult, scale_y_mult = 1.0, 1.0
            dx_anim, dy_anim, entry_ang = 0, 0, 0.0
            shadow_scale = 1.0
            halo_boost = 0

            if m_arch == "drop_weight":
                p_g = min(1.0, dt / 0.28)
                ease_g = 1.0 - (1.0 - p_g) ** 2.4
                dy_anim = -int(78 * (1.0 - ease_g))
                scale_x_mult = scale_y_mult = 0.92 + 0.08 * ease_g
                shadow_scale = 0.65 + 0.35 * ease_g
                if 0.25 <= dt <= 0.43:
                    sq = math.sin(((dt - 0.25) / 0.18) * math.pi)
                    scale_y_mult *= (1.0 - 0.07 * sq)
                    scale_x_mult *= (1.0 + 0.05 * sq)
            elif m_arch == "peel_reveal":
                scale_x_mult = scale_y_mult = 0.86 + 0.14 * ease_c
                entry_ang = -13.0 * (1.0 - ease_c)
            elif m_arch == "bloom_focus":
                p_b = min(1.0, dt / 0.38)
                sc_b = 0.36 + 0.64 * (1.0 - (1.0 - p_b) ** 3) + 0.045 * math.sin(p_b * math.pi) * (1.0 - p_b)
                scale_x_mult = scale_y_mult = sc_b
                if dt < 0.34:
                    halo_boost = int(32 * math.sin((dt / 0.34) * math.pi))
            elif m_arch == "swing_strike":
                p_s = min(1.0, dt / 0.30)
                ease_s = 1.0 - (1.0 - p_s) ** 3
                dx_anim = (-1 if target_cx < W * 0.5 else 1) * int(66 * (1.0 - ease_s))
                dy_anim = -int(44 * (1.0 - ease_s))
                entry_ang = (-16.0 if target_cx < W * 0.5 else 16.0) * (1.0 - ease_s)
                scale_x_mult = scale_y_mult = 0.82 + 0.18 * ease_s
            else:
                # slide_arc_left / slide_arc_right
                is_left_arc = ("left" in m_arch)
                dx_anim = (-92 if is_left_arc else 92) * (1.0 - ease_c)
                dy_anim = -26.0 * math.sin(p_ent * math.pi) * (1.0 - p_ent)
                entry_ang = (-8.5 if is_left_arc else 8.5) * (1.0 - ease_c)
                scale_x_mult = scale_y_mult = 0.88 + 0.12 * ease_c

            # Ultra-gentle continuous alive idle breathing (zero jitter)
            idle_dy, idle_ang = 0.0, 0.0
            if dt > 0.36 and exit_e <= 0.01:
                ramp_idle = min(1.0, (dt - 0.36) / 0.25)
                idle_dy = 3.2 * ramp_idle * math.sin(2.0 * math.pi * 0.45 * (dt - 0.36) + o_idx * 1.1)
                idle_ang = 0.45 * ramp_idle * math.sin(2.0 * math.pi * 0.35 * (dt - 0.36) + o_idx * 0.7)

            # Smooth ease-out exit scale + directional retract
            if exit_e > 0.0:
                scale_x_mult *= (1.0 - 0.08 * exit_e)
                scale_y_mult *= (1.0 - 0.08 * exit_e)
                dy_anim += int(16 * (exit_e ** 2))

            nw = max(1, int(item_im.width * auto_q * scale_x_mult))
            nh = max(1, int(item_im.height * auto_q * scale_y_mult))
            scaled_im = item_im.resize((nw, nh), Image.BILINEAR)

            slot_tilts = (-2.2, 1.9, -1.6, 2.3, -1.8)
            base_tilt = o.get("_rest_tilt_deg", slot_tilts[o_idx % len(slot_tilts)]) if img_path != "card" else 0.0
            total_tilt = base_tilt + entry_ang + idle_ang
            if abs(total_tilt) > 0.08 and nw > 24 and nh > 24:
                scaled_im = scaled_im.rotate(total_tilt, resample=Image.BICUBIC, expand=True)
                nw, nh = scaled_im.size

            cx = int(round(target_cx + dx_anim))
            cy = int(round(target_cy + dy_anim + idle_dy))

            # Strict safe-margin clamp
            spatial_policy = ACTIVE_RL_POLICY.get("rule_24_spatial_hierarchy", {})
            right_margin = spatial_policy.get("shorts_margin_right_px", 220) if is_shorts else 54
            min_x = nw // 2 + (48 if is_shorts else 54)
            max_x = W - nw // 2 - right_margin
            min_y = nh // 2 + (105 if is_shorts else 65)
            max_y = (sub_top_y - (140 if is_shorts else 80)) - nh // 2
            if max_y < min_y:
                max_y = min_y + 40
            cx = max(min_x, min(cx, max_x))
            cy = max(min_y, min(cy, max_y))

            rest_w = max(1, int(item_im.width * auto_q))
            rest_h = max(1, int(item_im.height * auto_q))
            occupied_boxes.append((target_cx - rest_w // 2, target_cy - rest_h // 2, target_cx + rest_w // 2, target_cy + rest_h // 2))

            # Apply opacity fade (smooth entrance fade-in and exit fade-out)
            if alpha < 0.999:
                bands = list(scaled_im.split())
                bands[3] = bands[3].point(lambda a: int(a * max(0.0, min(1.0, alpha))))
                scaled_im = Image.merge("RGBA", bands)
                if lbl_im:
                    lbl_bands = list(lbl_im.split())
                    lbl_bands[3] = lbl_bands[3].point(lambda a: int(a * max(0.0, min(1.0, alpha))))
                    lbl_im = Image.merge("RGBA", lbl_bands)

            # Soft feathered backdrop separation scrim on busy illustrated background shots
            if img_path != "card":
                halo_base = PAPER if sum(PAPER) > 380 else (28, 34, 48)
                halo_im = _soft_backdrop_halo(nw, nh, base_rgb=halo_base, peak_alpha=min(110, int((66 + halo_boost) * max(0.0, min(1.0, alpha)))))
                fr.alpha_composite(halo_im, (cx - halo_im.width // 2, cy - halo_im.height // 2))

            # Grounded shadow scales subtly for drop_weight landings
            sh_w = max(8, int(nw * shadow_scale))
            sh_h = max(8, int(nh * shadow_scale))
            shadow_src = scaled_im.resize((sh_w, sh_h), Image.BILINEAR) if (sh_w != nw or sh_h != nh) else scaled_im
            shadow_mask = shadow_src.split()[3].point(lambda a: int(a * 0.35))
            shadow_im = Image.new("RGBA", (sh_w, sh_h), (0, 0, 0, 0))
            shadow_im.putalpha(shadow_mask)
            fr.alpha_composite(shadow_im, (cx - sh_w // 2 + 5, cy - sh_h // 2 + 7))

            fr.alpha_composite(scaled_im, (cx - nw // 2, cy - nh // 2))
            scene_drawn_stickers[o_idx] = (cx, cy, scaled_im, o["t"], exit_e)

            # Runtime Compositing Telemetry
            rendered_stickers_counter[0] += 1
            rendered_unique_stickers.add(o_img)
            rendered_stickers_telemetry.append({
                "t": round(t, 2),
                "sticker": o_img,
                "bbox": [cx - nw // 2, cy - nh // 2, cx + nw // 2, cy + nh // 2],
                "anchor": [target_cx, target_cy]
            })

            if lbl_im:
                lbl_y = cy + nh // 2 + 6
                # If label would collide with subtitle zone, place it ABOVE the sticker instead!
                if lbl_y + lbl_im.height > (1040 if is_shorts else 860):
                    lbl_y = cy - nh // 2 - lbl_im.height - 6
                lbl_x = max(min_x - nw // 2, min(W - lbl_im.width - right_margin, cx - lbl_im.width // 2))
                fr.alpha_composite(lbl_im, (lbl_x, lbl_y))

        # Animated Cause -> Effect Editorial Connecting Arrow (Sticker A -> Sticker B)
        if sc.get("_group_pattern") == "cause_effect" and 0 in scene_drawn_stickers and len(sc.get("ov", [])) >= 2:
            cxA, cyA, imA, tA, exitA = scene_drawn_stickers[0]
            ovB = sc["ov"][1]
            tB = ovB["t"]
            if 1 in scene_drawn_stickers:
                cxB, cyB, imB, _, exitB = scene_drawn_stickers[1]
                wB, hB = imB.size
            else:
                b_key = f"{si}_1_{ovB.get('t', 0.0)}"
                if b_key in overlay_anchor_cache:
                    cxB, cyB, _ = overlay_anchor_cache[b_key]
                else:
                    usable_span_x = (W - (220 if is_shorts else 54)) - (48 if is_shorts else 54)
                    cxB = int((48 if is_shorts else 54) + usable_span_x * (0.75 if is_shorts else 0.80))
                    cyB = cyA
                imB, wB, hB, exitB = None, 220, 220, 0.0

            arrow_dur = 0.36
            arrow_start = max(tA + 0.18, tB - arrow_dur) if tB > tA + 0.30 else (tA + 0.18)
            arrow_prog = min(1.0, max(0.0, (t - arrow_start) / arrow_dur))
            arrow_alpha = min(1.0 - exitA, 1.0 - exitB)
            if arrow_prog > 0.02 and arrow_alpha > 0.05:
                # Exact outer upper-shoulder contour clearance so arc stays ABOVE props & >= 24px clear of label pills
                dx_ab = cxB - cxA
                wA, hA = imA.size
                sx_flank = cxA + (wA // 2) if dx_ab >= 0 else cxA - (wA // 2)
                sy_flank = cyA - int(hA * 0.18)
                try:
                    aA = np.array(imA.split()[3])
                    rowsA, colsA = np.where(aA[:max(1, int(hA * 0.62)), :] > 120)
                    if len(colsA) > 0:
                        idxA = int(np.argmax(colsA) if dx_ab >= 0 else np.argmin(colsA))
                        sx_flank = cxA - wA // 2 + int(colsA[idxA])
                        sy_flank = cyA - hA // 2 + int(rowsA[idxA])
                except Exception:
                    pass

                ex_flank = cxB - (wB // 2) if dx_ab >= 0 else cxB + (wB // 2)
                ey_flank = cyB - int(hB * 0.18)
                if imB is not None:
                    try:
                        aB = np.array(imB.split()[3])
                        rowsB, colsB = np.where(aB[:max(1, int(hB * 0.68)), :] > 120)
                        if len(colsB) > 0:
                            idxB = int(np.argmin(colsB) if dx_ab >= 0 else np.argmax(colsB))
                            ex_flank = cxB - wB // 2 + int(colsB[idxB])
                            ey_flank = cyB - hB // 2 + int(rowsB[idxB])
                    except Exception:
                        pass

                dir_sign = 1 if dx_ab >= 0 else -1
                ax0 = sx_flank + dir_sign * 26
                ay0 = min(sy_flank - 14, cyA - int(hA * 0.18))
                ax1 = ex_flank - dir_sign * 26
                ay1 = min(ey_flank - 14, cyB - int(hB * 0.16))
                # Strict clearance above both props and any label pill below Sticker A or B
                min_top_y = min(cyA - hA // 2, cyB - hB // 2)
                ctrl_x = (ax0 + ax1) * 0.5
                ctrl_y = max(36, min(ay0, ay1, min_top_y + 10) - max(96, int(abs(ax1 - ax0) * 0.34)))
                arr_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ad = ImageDraw.Draw(arr_layer)
                _draw_curved_ink_arrow(ad, ax0, ay0, ax1, ay1, ACCENT + (int(238 * arrow_alpha),), width=7 if is_shorts else 8, ctrl_pt=(ctrl_x, ctrl_y), draw_progress=arrow_prog)
                fr.alpha_composite(arr_layer)

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
        print(f"✅ Still frame rendered at T={args.frame:.2f}s -> {args.frame_out} (active stickers: {list(rendered_unique_stickers)})")
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

    # Runtime Compositing Verification & Telemetry Export (Rule 20 / Rule 24 / Gate 1)
    scheduled_stickers = [ov["img"] for sc in scenes for ov in sc.get("ov", [])
                          if ov.get("img") not in ("tag", "count") and not ov.get("img", "").startswith("bars:")]
    unique_scheduled = set(scheduled_stickers)

    telemetry_path = os.path.join(os.path.dirname(out_file) or ".", "sticker_telemetry.json")
    telemetry_data = {
        "scheduled_stickers_count": len(scheduled_stickers),
        "unique_scheduled_stickers": sorted(list(unique_scheduled)),
        "rendered_sticker_frame_hits": rendered_stickers_counter[0],
        "unique_rendered_stickers": sorted(list(rendered_unique_stickers)),
        "missing_stickers": sorted(list(unique_scheduled - rendered_unique_stickers))
    }
    try:
        with open(telemetry_path, "w", encoding="utf-8") as tf:
            json.dump(telemetry_data, tf, indent=2)
    except Exception as e:
        print(f"⚠️ Telemetry write notice: {e}")

    if unique_scheduled:
        if rendered_stickers_counter[0] == 0:
            sys.exit(f"❌ [Render Fatal Error] 0 stickers were rendered on screen despite {len(unique_scheduled)} scheduled stickers in {args.scenes}!")
        missing = unique_scheduled - rendered_unique_stickers
        if missing:
            sys.exit(f"❌ [Render Fatal Error] Scheduled sticker(s) failed to render on screen: {missing}")
        print(f"✅ Runtime Compositing Verified: All {len(unique_scheduled)} scheduled stickers rendered across {rendered_stickers_counter[0]} frame hits (telemetry logged to {telemetry_path})")

    # Post-Mux Forensic Verification: Inspect container audio and video streams
    print(f"🔍 Running Post-Mux Verification on {out_file}...")
    try:
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
