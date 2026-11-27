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
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageSequence

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


_BG_CATALOG_CACHE = None


def _resolve_cc0_background(variant="default"):
    """Loads matching CC0/editorial background from skills/stickman-hybrid/backgrounds/CATALOG.tsv."""
    global _BG_CATALOG_CACHE
    bg_dir = os.path.join(SKILL_ROOT, "backgrounds")
    if _BG_CATALOG_CACHE is None:
        _BG_CATALOG_CACHE = {}
        cat_p = os.path.join(bg_dir, "CATALOG.tsv")
        if os.path.exists(cat_p):
            try:
                with open(cat_p, encoding="utf-8") as f:
                    for row in csv.DictReader(f, delimiter="\t"):
                        var_name = str(row.get("variant", "")).strip().lower()
                        rel = str(row.get("path", "")).strip()
                        looks_s = str(row.get("looks", "all")).strip().lower()
                        usage_s = str(row.get("usage", "")).strip().lower()
                        if not rel:
                            continue
                        full_p = os.path.join(bg_dir, rel)
                        if var_name:
                            _BG_CATALOG_CACHE[var_name] = full_p
                        for tok in usage_s.split(","):
                            tok = tok.strip()
                            if tok:
                                _BG_CATALOG_CACHE[tok] = full_p
                        for lk in looks_s.split(","):
                            lk = lk.strip()
                            if lk and var_name:
                                _BG_CATALOG_CACHE[f"{var_name}:{lk}"] = full_p
            except Exception:
                pass
    var = (variant or "default").strip().lower()
    look = ACTIVE_LOOK_NAME.strip().lower()
    alias_map = {
        "default": ("parchment_warm_bright", "parchment_warm_bright.png"),
        "sketchbook": ("sketchbook_grain", "sketchbook_grain.png"),
        "breather": ("breather_cream_editorial", "breather_cream_editorial.png"),
        "split_warm": ("split_warm_paper", "split_warm_paper.png"),
        "split_cool": ("split_cool_paper", "split_cool_paper.png"),
        "blueprint": ("dotgrid_blueprint", "dotgrid_blueprint.png"),
        "kraft": ("kraft_archive_paper", "kraft_archive_paper.png"),
        "scale": ("dotgrid_blueprint", "dotgrid_blueprint.png"),
        "outro_dark": ("dark_charcoal_matte", "dark_charcoal_matte.png"),
    }
    var_key, fallback_fn = alias_map.get(var, ("parchment_warm_bright", "parchment_warm_bright.png"))
    for k in (f"{var_key}:{look}", var_key, var):
        p = _BG_CATALOG_CACHE.get(k)
        if p and os.path.exists(p):
            return p
    cand = os.path.join(bg_dir, fallback_fn)
    return cand if os.path.exists(cand) else None


def _apply_cc0_vfx_layer(im, kind="paper_grain", opacity=0.08):
    """Applies subtle lightweight CC0 editorial VFX overlay from vfx_assets/ without muddying contrast."""
    vfx_map = {
        "paper_grain": os.path.join(SKILL_ROOT, "vfx_assets", "vfx_paper_grain_overlay.png"),
        "vignette": os.path.join(SKILL_ROOT, "vfx_assets", "vfx_soft_editorial_vignette.png"),
    }
    vp = vfx_map.get(kind)
    if not vp or not os.path.exists(vp) or opacity <= 0.0:
        return im
    try:
        ov = Image.open(vp).convert("RGBA").resize(im.size, Image.BILINEAR)
        if opacity < 0.99:
            arr = np.array(ov, dtype=np.float32)
            arr[:, :, 3] = np.clip(arr[:, :, 3] * opacity, 0, 255)
            ov = Image.fromarray(arr.astype(np.uint8), mode="RGBA")
        out = im.convert("RGBA")
        out.alpha_composite(ov)
        return out
    except Exception:
        return im


def card_bg(w, h, variant="default"):
    key = (w, h, ACTIVE_LOOK_NAME, variant)
    if key not in _card_cache:
        var = (variant or "default").strip().lower()
        bg_p = _resolve_cc0_background(var)
        if var == "outro_dark" and bg_p:
            try:
                base_im = Image.open(bg_p).convert("RGBA").resize((w, h), Image.LANCZOS)
                _card_cache[key] = _apply_cc0_vfx_layer(base_im, "vignette", opacity=0.35)
                return _card_cache[key].copy()
            except Exception:
                pass

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

        # Composite curated CC0 paper/grain background harmonized with active --look palette
        is_light_look = sum(CARD_IN) > 420
        if bg_p and is_light_look:
            try:
                tex = Image.open(bg_p).convert("RGBA").resize((w, h), Image.BILINEAR)
                blend_amt = 0.42 if var in ("breather", "blueprint", "kraft", "scale", "split_warm", "split_cool") else 0.28
                base_im = Image.blend(base_im, tex, blend_amt)
            except Exception:
                pass
        else:
            tex_p = bg_p or os.path.abspath(os.path.join(SKILL_ROOT, "textures", "parchment_vintage.png"))
            if os.path.exists(tex_p):
                try:
                    tex = Image.open(tex_p).convert("RGBA").resize((w, h), Image.BILINEAR)
                    base_im = Image.blend(base_im, tex, 0.10)
                except Exception:
                    pass

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
        base_im = _apply_cc0_vfx_layer(base_im, "vignette", opacity=0.28 if var in ("breather", "scale") else 0.18)
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


_sticker_anim_cache = {}


def _load_sticker_frames(path):
    """Loads single static frame or full animated WebP/GIF frame sequence with durations."""
    ap = os.path.abspath(path)
    if ap in _sticker_anim_cache:
        return _sticker_anim_cache[ap]
    if len(_sticker_anim_cache) > 48:
        _sticker_anim_cache.clear()
    with Image.open(ap) as im:
        is_anim = bool(getattr(im, "is_animated", False) and getattr(im, "n_frames", 1) > 1)
        if is_anim:
            frames, durs = [], []
            for f_raw in ImageSequence.Iterator(im):
                frames.append(f_raw.convert("RGBA").copy())
                dur_ms = f_raw.info.get("duration", im.info.get("duration", 60)) or 60
                durs.append(max(0.02, float(dur_ms) / 1000.0))
            tot = max(0.05, sum(durs))
            entry = (frames, durs, tot)
        else:
            entry = ([im.convert("RGBA").copy()], [1.0], 1.0)
    _sticker_anim_cache[ap] = entry
    return entry


def _get_sticker_frame_at(path, t_sec=0.0):
    frames, durs, tot = _load_sticker_frames(path)
    if len(frames) == 1:
        return frames[0], 0
    tt = max(0.0, float(t_sec)) % tot
    acc = 0.0
    for idx, (fr_im, d_s) in enumerate(zip(frames, durs)):
        acc += d_s
        if tt <= acc:
            return fr_im, idx
    return frames[-1], len(frames) - 1


def _apply_animated_vfx_layer(im, kind="paper_grain_cycle", t_abs=0.0, opacity=0.22):
    """Composites looping animated CC0/MIT VFX WebP overlay harmonized with active look."""
    p = os.path.join(SKILL_ROOT, "vfx_assets", f"vfx_{kind}.webp")
    if not os.path.exists(p):
        p = os.path.join(SKILL_ROOT, "vfx_assets", kind)
    if not os.path.exists(p):
        return im
    try:
        v_fr, _ = _get_sticker_frame_at(p, t_sec=t_abs)
        if v_fr.size != im.size:
            v_fr = v_fr.resize(im.size, Image.BILINEAR)
        if opacity < 0.999:
            v_fr = _apply_alpha_to_image(v_fr, opacity)
        out = im.convert("RGBA")
        out.alpha_composite(v_fr)
        return out
    except Exception:
        return im


def sticker(path, h, t_sec=0.0):
    raw_im, frame_idx = _get_sticker_frame_at(path, t_sec=t_sec)
    key_k = (os.path.abspath(path), h, frame_idx)
    if key_k not in _sticker_cache:
        if len(_sticker_cache) > 96:
            _sticker_cache.clear()
        nw = max(1, round(raw_im.width * h / max(1, raw_im.height)))
        im = raw_im.resize((nw, h), Image.LANCZOS)
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

    # Unified subject / white stickman head salience mask (protects focal character & head across all cohort sizes)
    def _subject_salience_penalty(bx0, by0, bx1, by1):
        try:
            x0, y0 = max(0, int(bx0)), max(0, int(by0))
            x1, y1 = min(bg_im.width, int(bx1)), min(bg_im.height, int(by1))
            if x1 <= x0 + 8 or y1 <= y0 + 8:
                return 0.0
            crop_rgb = np.array(bg_im.crop((x0, y0, x1, y1)).convert("RGB"), dtype=np.uint8)
            white_head = ((crop_rgb[:, :, 0] > 232) & (crop_rgb[:, :, 1] > 228) & (crop_rgb[:, :, 2] > 218)).mean()
            dark_ink = ((crop_rgb[:, :, 0] < 65) & (crop_rgb[:, :, 1] < 65) & (crop_rgb[:, :, 2] < 65)).mean()
            cx_p, cy_p = (x0 + x1) * 0.5, (y0 + y1) * 0.5
            in_center = (0.20 * W <= cx_p <= 0.80 * W) and (0.18 * H <= cy_p <= 0.78 * H)
            if in_center and white_head > 0.035 and dark_ink > 0.015:
                return 95.0
            if dark_ink > 0.032:
                return 38.0
        except Exception:
            pass
        return 0.0

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
        l_score += _subject_salience_penalty(left_x - item_w // 2, eye_y - item_h // 2, left_x + item_w // 2, eye_y + item_h // 2)
        r_score += _subject_salience_penalty(right_x - item_w // 2, eye_y - item_h // 2, right_x + item_w // 2, eye_y + item_h // 2)
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
    # Enforce strict subject/head-avoidance: score negative space cleanliness and penalize central focal character zone
    for scale_try in (1.0, 0.90, 0.80, 0.70, 0.58):
        bw = max(32, int(item_w * scale_try))
        bh = max(32, int(item_h * scale_try))
        msx, mxsx, msy, mxsy = _bounds_for_size(bw, bh)
        best_cand = None
        best_cand_score = float("inf")
        for _, raw_cx, raw_cy in candidates:
            cx = max(msx, min(raw_cx, mxsx))
            cy = max(msy, min(raw_cy, mxsy))
            bx0, by0, bx1, by1 = cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2
            if not _collides(bx0, by0, bx1, by1):
                sc = compute_negative_space_score(bg_im, bx0, by0, bx1, by1)
                sc += _subject_salience_penalty(bx0, by0, bx1, by1)
                # Penalize placing sticker on top of centered stickman / focal character head/food
                if 0.36 < (cx / W) < 0.64 and 0.28 < (cy / H) < 0.66:
                    sc += 160.0
                if sc < best_cand_score:
                    best_cand_score = sc
                    best_cand = (cx, cy)
        if best_cand and best_cand_score < 260.0:
            return best_cand[0], best_cand[1], scale_try

    # Last-resort clean slot search across safety net (still respects head/subject salience!)
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
            sc = compute_negative_space_score(bg_im, bx0, by0, bx1, by1) + _subject_salience_penalty(bx0, by0, bx1, by1)
            if 0.36 < (cx / W) < 0.64 and 0.28 < (cy / H) < 0.66:
                sc += 120.0
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


def resolve_sticker_path(o_img, single_object_only=False):
    """Bulletproof multi-directory and semantic registry resolution (.png/.webp/.gif)."""
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
        s + ".png" if not s.lower().endswith((".png", ".webp", ".gif")) else s,
        s + ".webp" if not s.lower().endswith((".png", ".webp", ".gif")) else s,
        os.path.join("elements", "cut", f"{name_no_ext}.png"),
        os.path.join("elements", "cut", f"{name_no_ext}.webp"),
        os.path.join("elements", "cut", name_base),
        os.path.join("..", "elements", "cut", f"{name_no_ext}.png"),
        os.path.join("..", "elements", "cut", f"{name_no_ext}.webp"),
        os.path.join("..", "elements", "cut", name_base),
        os.path.join("..", "short", "elements", "cut", f"{name_no_ext}.png"),
        os.path.join("..", "long", "elements", "cut", f"{name_no_ext}.png"),
    ]
    for cp in cands:
        if os.path.exists(cp) and os.path.getsize(cp) > 500:
            if not (single_object_only and os.path.splitext(os.path.basename(cp))[0].lower() in {"skull_fossil", "scientific_field_researcher", "tribal_storytelling_pie", "campfire_circle"}):
                return cp
    try:
        import asset_registry
        p_root = asset_registry.resolve_project_root(os.getcwd())
        reg_m = asset_registry.find_reusable_sticker(name_no_ext, p_root, single_object_only=single_object_only)
        if reg_m and os.path.exists(reg_m["path"]) and os.path.getsize(reg_m["path"]) > 500:
            return reg_m["path"]
    except Exception:
        pass
    return None


def fit_sticker_in_box(path_or_im, max_w, max_h, t_sec=0.0):
    """Loads a static or animated sticker and scales it preserving aspect ratio inside (max_w, max_h)."""
    if path_or_im is None or max_w <= 0 or max_h <= 0:
        return None
    if isinstance(path_or_im, Image.Image):
        raw = path_or_im.convert("RGBA") if path_or_im.mode != "RGBA" else path_or_im
    else:
        resolved = resolve_sticker_path(str(path_or_im))
        if not resolved or not os.path.exists(resolved):
            return None
        try:
            raw, _ = _get_sticker_frame_at(resolved, t_sec=t_sec)
        except Exception:
            return None

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


def _apply_alpha_to_image(im, alpha):
    """Multiplies the alpha channel of an image by alpha factor."""
    if alpha >= 0.999 or im is None:
        return im
    out = im.copy()
    bands = list(out.split())
    if len(bands) == 4:
        bands[3] = bands[3].point(lambda a: int(a * max(0.0, min(1.0, alpha))))
        return Image.merge("RGBA", bands)
    return out


def _interpolate_stat_numbers(target_text, ease_val):
    """Interpolates numbers in target_text smoothly from 0 up to final values over ease curve."""
    if ease_val >= 0.999:
        return target_text
    def _repl(m):
        raw = m.group(0).replace(",", "")
        try:
            val = float(raw)
            cur = int(round(val * ease_val))
            if "," in m.group(0):
                return f"{cur:,}"
            return str(cur)
        except Exception:
            return m.group(0)
    return re.sub(r'\b\d+(?:,\d+)?\b', _repl, target_text)


def _draw_highlighter_swipe(overlay_im, cx, cy, sw_w, sw_h, color, tilt=-1.6, progress=1.0):
    """Draws a tapered, slightly angled hand-drawn marker highlighter brush stroke with organic rough edges.
    Supports live progressive sweep 0% -> 100% left-to-right.
    """
    p = max(0.0, min(1.0, float(progress)))
    if p <= 0.02:
        return
    cur_w = max(12, int(sw_w * p))
    cur_cx = (cx - sw_w // 2) + cur_w // 2

    pad = 44
    sw_im = Image.new("RGBA", (cur_w + 2 * pad, sw_h + 2 * pad), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sw_im)
    y0 = pad + int(sw_h * 0.10)
    y1 = pad + int(sw_h * 0.94)
    x0, x1 = pad, pad + cur_w
    poly = [
        (x0 + min(16, cur_w // 4), y0 + 7),
        (x0 + int(cur_w * 0.25), y0 + 2),
        (x0 + int(cur_w * 0.55), y0 + 5),
        (x0 + int(cur_w * 0.82), y0 + 1),
        (x1 - 4, y0 + 4),
        (x1, y1 - 9),
        (x0 + int(cur_w * 0.78), y1 - 3),
        (x0 + int(cur_w * 0.45), y1 - 6),
        (x0 + int(cur_w * 0.18), y1 - 2),
        (x0, y1 - 5),
    ]
    sd.polygon(poly, fill=color)
    sd.rounded_rectangle((x0 + min(20, cur_w // 4), y0 + 10, max(x0 + 20, x1 - 16), y1 - 6),
                         radius=max(8, sw_h // 5), fill=color[:3] + (max(18, int(color[3] * 0.45)),))
    sw_im = sw_im.rotate(tilt, resample=Image.BILINEAR, expand=True)
    overlay_im.alpha_composite(sw_im, (int(cur_cx - sw_im.width // 2), int(cy - sw_im.height // 2)))


def _draw_per_line_highlighters(overlay_im, block_x0, block_y0, line_boxes, color, pad_x=42, progress=1.0):
    """Draws tight individual organic marker brush swipes behind each wrapped line (never across line gaps)."""
    p = max(0.0, min(1.0, float(progress)))
    if p <= 0.02:
        return
    tilts = (-1.8, 1.3, -1.4)
    for li, (lx, ly, lw, lh) in enumerate(line_boxes):
        cx = block_x0 + lx + lw // 2
        cy = block_y0 + ly + int(lh * 0.56)
        sw_w = lw + pad_x * 2
        sw_h = max(38, int(lh * 0.54))
        if len(line_boxes) > 1:
            line_p = max(0.0, min(1.0, (p - li * 0.20) / 0.80))
        else:
            line_p = p
        if line_p > 0.02:
            _draw_highlighter_swipe(overlay_im, cx, cy, sw_w, sw_h, color, tilt=tilts[li % len(tilts)], progress=line_p)


def _draw_editorial_corner_ticks(d, x0, y0, x1, y1, color, arm=44, width=6, progress=1.0):
    """Draws crisp minimalist editorial registration corner brackets around an impact stage."""
    p = max(0.0, min(1.0, float(progress)))
    if p <= 0.05:
        return
    eff_arm = int(arm * (1.0 - (1.0 - p) ** 2))
    if eff_arm <= 4:
        return
    # Top-Left
    d.line((x0, y0 + eff_arm, x0, y0, x0 + eff_arm, y0), fill=color, width=width)
    # Top-Right
    d.line((x1 - eff_arm, y0, x1, y0, x1, y0 + eff_arm), fill=color, width=width)
    # Bottom-Left
    d.line((x0, y1 - eff_arm, x0, y1, x0 + eff_arm, y1), fill=color, width=width)
    # Bottom-Right
    d.line((x1 - eff_arm, y1, x1, y1, x1, y1 - eff_arm), fill=color, width=width)


def draw_kinetic_editorial_badge(fr, W, H, text, dt, duration=3.0, is_shorts=False):
    """Draws a kinetic hand-styled editorial fact badge (e.g. '14,000 YEARS AGO') in clean upper space with live ink underline."""
    p_ent = min(1.0, max(0.0, dt / 0.28))
    ease_ent = 1.0 - (1.0 - p_ent) ** 3
    alpha = min(1.0, ease_ent * 1.35)

    rem = duration - dt
    if rem < 0.25:
        alpha *= max(0.0, rem / 0.25)
    if alpha <= 0.02:
        return

    dy_ent = int(22 * (1.0 - ease_ent))
    badge_im = text_layer(text, 36 if is_shorts else 38, (252, 248, 240), font_role="hero")
    if not badge_im:
        return

    pad_x = 28
    pad_y = 12
    bw = badge_im.width + pad_x * 2
    bh = badge_im.height + pad_y * 2

    layer = Image.new("RGBA", (bw + 20, bh + 24), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # Subtle drop shadow
    ld.rounded_rectangle((10 + 3, 10 + 4, 10 + bw + 3, 10 + bh + 4), radius=16, fill=(0, 0, 0, int(60 * alpha)))
    # Warm dark charcoal plate
    ld.rounded_rectangle((10, 10, 10 + bw, 10 + bh), radius=16, fill=(24, 28, 38, int(238 * alpha)),
                         outline=(235, 140, 40, int(220 * alpha)), width=3)
    layer.alpha_composite(badge_im, (10 + pad_x, 10 + pad_y))

    # Live brush ink underline sweeping 0% -> 100% underneath text
    und_prog = min(1.0, max(0.0, (dt - 0.14) / 0.26))
    ease_und = 1.0 - (1.0 - und_prog) ** 2.2
    _draw_live_ink_underline(ld, 10 + pad_x, 10 + bh - 6, 10 + bw - pad_x, 10 + bh - 6,
                             progress=ease_und, color=(245, 160, 50, int(240 * alpha)), width=5)

    cx = W // 2
    cy = int(H * (0.13 if is_shorts else 0.15)) + dy_ent
    fr.alpha_composite(layer, (cx - layer.width // 2, cy - layer.height // 2))


def _extract_editorial_fact_badges(words_list):
    """Detects spoken historical dates, metrics, and milestones from WORDS.tsv for live kinetic badge display."""
    badges = []
    if not words_list:
        return badges
    words = [w.get("word", "").lower().strip('.,!?":;') for w in words_list]
    starts = [float(w.get("start", 0.0)) for w in words_list]
    n = len(words)
    i = 0
    while i < n:
        w = words[i]
        if w in ("fourteen", "14") and i + 1 < n and words[i + 1] in ("thousand", "000"):
            t_s = starts[i]
            badges.append((t_s, t_s + 3.2, "14,000 YEARS AGO"))
            i += 2
            continue
        elif w in ("six", "6") and i + 1 < n and words[i + 1] in ("thousand", "000"):
            t_s = starts[i]
            badges.append((t_s, t_s + 3.2, "6,500 YEARS AGO"))
            i += 2
            continue
        elif w in ("1498", "fourteen-ninety-eight") or (w in ("fourteen", "14") and i + 1 < n and words[i + 1] in ("ninety", "98", "ninety-eight")):
            t_s = starts[i]
            badges.append((t_s, t_s + 3.2, "YEAR 1498"))
            i += 2
            continue
        elif w in ("two", "2") and i + 1 < n and words[i + 1] in ("percent", "%"):
            t_s = starts[i]
            badges.append((t_s, t_s + 3.2, "2% CAVITY RATE"))
            i += 2
            continue
        elif w in ("twenty", "20") and i + 1 < n and words[i + 1] in ("percent", "%"):
            t_s = starts[i]
            badges.append((t_s, t_s + 3.2, "20% CAVITY SPIKE"))
            i += 2
            continue
        elif w in ("1177",) or (w in ("eleven", "11") and i + 1 < n and words[i + 1] in ("seventy-seven", "77")):
            t_s = starts[i]
            badges.append((t_s, t_s + 3.2, "1177 BC"))
            i += 2
            continue
        i += 1
    return badges


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


def _draw_live_ink_circle(d, cx, cy, rx, ry, progress=1.0, color=(220, 48, 38, 235), width=7):
    """Draws an animated organic hand-drawn ink callout circle sweeping 0% -> 100%."""
    dp = max(0.0, min(1.0, float(progress)))
    if dp <= 0.02:
        return
    n_pts = max(6, int(36 * dp))
    angles = np.linspace(-math.pi / 2, -math.pi / 2 + 2 * math.pi * dp, n_pts)
    pts = []
    for idx_a, theta in enumerate(angles):
        wobble = 1.0 + 0.032 * math.sin(idx_a * 1.9)
        px = cx + rx * wobble * math.cos(theta)
        py = cy + ry * wobble * math.sin(theta)
        pts.append((px, py))
    if len(pts) >= 2:
        for k in range(len(pts) - 1):
            d.line([pts[k], pts[k + 1]], fill=color, width=width)


def _draw_live_ink_underline(d, x0, y0, x1, y1, progress=1.0, color=(235, 140, 40, 235), width=8):
    """Draws an animated organic hand-drawn ink underline sweeping 0% -> 100%."""
    dp = max(0.0, min(1.0, float(progress)))
    if dp <= 0.02:
        return
    cur_x = x0 + (x1 - x0) * dp
    cur_y = y0 + (y1 - y0) * dp
    mid_x = (x0 + cur_x) * 0.5
    mid_y = y0 + 3.0 * math.sin(dp * math.pi)
    d.line([(x0, y0), (mid_x, mid_y), (cur_x, cur_y)], fill=color, width=width)


def detect_panel_polarity(badge_txt, body_txt=""):
    """Detects positive vs negative polarity from panel headers and labels for sentiment-aware badges."""
    combined = f"{badge_txt} {body_txt}".lower()
    if "[+]" in combined or "(+)" in combined or "✓" in combined:
        return "stamp_check", (28, 152, 82)
    if "[-]" in combined or "(-)" in combined or "✗" in combined or "x" in combined.split():
        return "stamp_x", (208, 48, 38)
    pos_kws = {"reality", "truth", "fact", "ancient", "sugar-free", "healthy", "natural", "clean", "solution", "correct", "real", "cure", "verified", "safe", "pure"}
    neg_kws = {"myth", "fake", "lie", "modern", "sugar", "acid", "decay", "cavity", "rot", "pain", "danger", "crisis", "wrong", "false", "ruin", "culprit", "attacks", "fatal"}
    pos_score = sum(1 for w in pos_kws if w in combined)
    neg_score = sum(1 for w in neg_kws if w in combined)
    if pos_score > neg_score:
        return "stamp_check", (28, 152, 82)
    elif neg_score > pos_score:
        return "stamp_x", (208, 48, 38)
    return None, None


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

    # Staged slow cubic-bezier entrance dynamics (~0.00 -> 1.50s choreography)
    p_ent = min(1.0, max(0.0, dt / 0.45))
    ease_ent = 1.0 - (1.0 - p_ent) ** 4
    dy_ent = int(56 * (1.0 - ease_ent))
    alpha_ent = min(1.0, ease_ent * 1.35)

    # Number roll settle over 0.15s -> 1.15s
    p_roll = min(1.0, max(0.0, (dt - 0.10) / 1.05))
    ease_roll = 1.0 - (1.0 - p_roll) ** 4
    disp_stat_txt = _interpolate_stat_numbers(stat_txt, ease_roll)

    # Live brush highlighter sweep over 0.40s -> 1.15s
    hl_prog = min(1.0, max(0.0, (dt - 0.40) / 0.75))
    ease_hl = 1.0 - (1.0 - hl_prog) ** 3

    # Live ink underline sweep over 0.85s -> 1.45s
    und_prog = min(1.0, max(0.0, (dt - 0.85) / 0.60))
    ease_und = 1.0 - (1.0 - und_prog) ** 3

    # Corner ticks pop over 0.25s -> 0.85s
    tick_prog = min(1.0, max(0.0, (dt - 0.25) / 0.60))

    # Sub-label upward slide & fade over 0.90s -> 1.50s
    sub_prog = min(1.0, max(0.0, (dt - 0.90) / 0.60))
    ease_sub = 1.0 - (1.0 - sub_prog) ** 4
    dy_sub = int(32 * (1.0 - ease_sub))
    alpha_sub = min(1.0, ease_sub * 1.35)

    has_sticker = (sticker_im is not None)

    if is_shorts:
        # Full active visual stage on 9:16 Shorts: Y 10% - 72% (strict >=9% horizontal margin left/right!)
        max_w = int(W2 * 0.78)
        _draw_editorial_corner_ticks(d2, int(W2 * 0.085), int(H2 * 0.11), int(W2 * 0.915), int(H2 * 0.69), INK + (58,), arm=48, width=6, progress=tick_prog)
        if has_sticker:
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

            stat_raw, line_boxes = render_wrapped_text_block(
                disp_stat_txt, "hero", start_size=345, min_size=190,
                max_w=max_w, max_h=int(H2 * 0.17), color=INK, max_lines=2, return_line_boxes=True
            )
            stat_block = _text_with_offset_shadow(stat_raw, dx=8, dy=10)
            stat_block = _apply_alpha_to_image(stat_block, alpha_ent)
            sub_block = render_wrapped_text_block(
                sub_txt.upper(), "annotation", start_size=118, min_size=82,
                max_w=max_w, max_h=int(H2 * 0.08), color=ACCENT, max_lines=2
            ) if sub_txt else None
            if sub_block:
                sub_block = _apply_alpha_to_image(sub_block, alpha_sub)

            tot_h = stat_block.height + (36 + sub_block.height if sub_block else 0)
            txt_top = int(H2 * 0.485) - tot_h // 2
            bx_stat = W2 // 2 - stat_block.width // 2
            _draw_per_line_highlighters(overlay2, bx_stat, txt_top + dy_ent, line_boxes, SUB_ACCENT + (132,), pad_x=34, progress=ease_hl)
            overlay2.alpha_composite(stat_block, (bx_stat, txt_top + dy_ent))
            cur_y = txt_top + stat_block.height + dy_ent
            if sub_block:
                rule_w = min(int(max_w * 0.80), stat_raw.width + 32)
                _draw_live_ink_underline(d2, W2 // 2 - rule_w // 2, cur_y + 10, W2 // 2 + rule_w // 2, cur_y + 6,
                                         progress=ease_und, color=ACCENT + (240,), width=11)
                overlay2.alpha_composite(sub_block, (W2 // 2 - sub_block.width // 2, cur_y + 30 + dy_sub))

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
                disp_stat_txt, "hero", start_size=480, min_size=220,
                max_w=int(W2 * 0.80), max_h=int(H2 * 0.24), color=INK, max_lines=2, return_line_boxes=True
            )
            stat_block = _text_with_offset_shadow(stat_raw, dx=10, dy=12)
            stat_block = _apply_alpha_to_image(stat_block, alpha_ent)
            sub_block = render_wrapped_text_block(
                sub_txt.upper(), "annotation", start_size=126, min_size=88,
                max_w=int(W2 * 0.80), max_h=int(H2 * 0.12), color=ACCENT, max_lines=2
            ) if sub_txt else None
            if sub_block:
                sub_block = _apply_alpha_to_image(sub_block, alpha_sub)

            tot_h = stat_block.height + (56 + sub_block.height if sub_block else 0)
            txt_top = int(H2 * 0.425) - tot_h // 2
            bx_stat = W2 // 2 - stat_block.width // 2

            _draw_per_line_highlighters(overlay2, bx_stat, txt_top + dy_ent, line_boxes, SUB_ACCENT + (138,), pad_x=40, progress=ease_hl)
            _draw_radial_ticks(d2, bx_stat - 14, txt_top + 14 + dy_ent, scale=1.55, color=ACCENT + (228,))
            overlay2.alpha_composite(stat_block, (bx_stat, txt_top + dy_ent))

            cur_y = txt_top + stat_block.height + dy_ent
            if sub_block:
                rule_w = min(int(W2 * 0.74), stat_raw.width)
                _draw_live_ink_underline(d2, W2 // 2 - rule_w // 2, cur_y + 18, W2 // 2 + rule_w // 2, cur_y + 24,
                                         progress=ease_und, color=ACCENT + (240,), width=10)
                overlay2.alpha_composite(sub_block, (W2 // 2 - sub_block.width // 2, cur_y + 46 + dy_sub))

    else:
        # Long (16:9): Clean authoritative widescreen editorial composition with registration corners & per-line highlighters
        _draw_editorial_corner_ticks(d2, 120, 120, W2 - 120, H2 - 140, INK + (52,), arm=52, width=6, progress=tick_prog)
        if has_sticker:
            left_cx = int(W2 * 0.34)
            left_max_w = int(W2 * 0.46)
            stat_raw, line_boxes = render_wrapped_text_block(
                disp_stat_txt, "hero", start_size=360, min_size=180,
                max_w=left_max_w, max_h=int(H2 * 0.38), color=INK, max_lines=2, return_line_boxes=True
            )
            stat_block = _text_with_offset_shadow(stat_raw, dx=9, dy=11)
            stat_block = _apply_alpha_to_image(stat_block, alpha_ent)
            sub_block = render_wrapped_text_block(
                sub_txt.upper(), "annotation", start_size=122, min_size=80,
                max_w=int(left_max_w * 0.94), max_h=int(H2 * 0.16), color=ACCENT, max_lines=2
            ) if sub_txt else None
            if sub_block:
                sub_block = _apply_alpha_to_image(sub_block, alpha_sub)

            tot_h = stat_block.height + (44 + sub_block.height if sub_block else 0)
            cur_y = int(H2 * 0.44) - tot_h // 2
            bx_stat = left_cx - stat_block.width // 2
            _draw_per_line_highlighters(overlay2, bx_stat, cur_y + dy_ent, line_boxes, SUB_ACCENT + (135,), pad_x=40, progress=ease_hl)
            overlay2.alpha_composite(stat_block, (bx_stat, cur_y + dy_ent))
            cur_y += stat_block.height + dy_ent
            if sub_block:
                rule_w = min(int(left_max_w * 0.72), stat_raw.width)
                _draw_live_ink_underline(d2, left_cx - rule_w // 2, cur_y + 14, left_cx + rule_w // 2, cur_y + 10,
                                         progress=ease_und, color=ACCENT + (240,), width=11)
                overlay2.alpha_composite(sub_block, (left_cx - sub_block.width // 2, cur_y + 40 + dy_sub))

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
                hdr_top = int(H2 * 0.44) - tot_h // 2
                l0_x, l0_y, l0_w, l0_h = line_boxes[0]
                min_clearance_ax0 = bx_stat + l0_x + l0_w + 64
                ax0 = max(min_clearance_ax0, min(int(W2 * 0.54), bx_stat + l0_x + l0_w + 80))
                ay0 = max(int(H2 * 0.18), hdr_top + l0_y + int(l0_h * 0.32))

                stk_x0 = right_cx - stk_img.width // 2
                stk_y0 = stk_cy - stk_img.height // 2
                ax1 = max(ax0 + 120, stk_x0 - 52)
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
                ax0 = min(ax0, ax1 - 180)
                ay1 = min(ay1, hdr_top + l0_y + l0_h + 120)
                ctrl_x = (ax0 + ax1) * 0.50
                ctrl_y = max(int(H2 * 0.11), min(ay0, ay1) - 145)
                _draw_curved_ink_arrow(d2, ax0, ay0, ax1, ay1, ACCENT + (235,), width=11,
                                       ctrl_pt=(ctrl_x, ctrl_y), draw_progress=arrow_prog)
        else:
            max_w = int(W2 * 0.80)
            stat_raw, line_boxes = render_wrapped_text_block(
                disp_stat_txt, "hero", start_size=460, min_size=220,
                max_w=max_w, max_h=int(H2 * 0.40), color=INK, max_lines=2, return_line_boxes=True
            )
            stat_block = _text_with_offset_shadow(stat_raw, dx=10, dy=12)
            stat_block = _apply_alpha_to_image(stat_block, alpha_ent)
            sub_block = render_wrapped_text_block(
                sub_txt.upper(), "annotation", start_size=132, min_size=84,
                max_w=int(max_w * 0.88), max_h=int(H2 * 0.16), color=ACCENT, max_lines=2
            ) if sub_txt else None
            if sub_block:
                sub_block = _apply_alpha_to_image(sub_block, alpha_sub)

            tot_h = stat_block.height + (48 + sub_block.height if sub_block else 0)
            cur_y = int(H2 * 0.44) - tot_h // 2
            bx_stat = W2 // 2 - stat_block.width // 2
            _draw_per_line_highlighters(overlay2, bx_stat, cur_y + dy_ent, line_boxes, SUB_ACCENT + (135,), pad_x=48, progress=ease_hl)
            _draw_radial_ticks(d2, bx_stat - 16, cur_y + 16 + dy_ent, scale=1.5, color=ACCENT + (225,))
            overlay2.alpha_composite(stat_block, (bx_stat, cur_y + dy_ent))
            cur_y += stat_block.height + dy_ent
            if sub_block:
                rule_w = min(int(max_w * 0.64), stat_raw.width)
                _draw_live_ink_underline(d2, W2 // 2 - rule_w // 2, cur_y + 14, W2 // 2 + rule_w // 2, cur_y + 20,
                                         progress=ease_und, color=ACCENT + (240,), width=10)
                overlay2.alpha_composite(sub_block, (W2 // 2 - sub_block.width // 2, cur_y + 44 + dy_sub))

    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    # Slow continuous documentary drift (1.00 -> 1.035 over scene hold)
    if dt > 0.0:
        drift_scale = 1.00 + 0.035 * min(1.0, dt / 4.8)
        dw = int(w * drift_scale)
        dh = int(h * drift_scale)
        fr = fr.resize((dw, dh), Image.BILINEAR).crop(((dw - w) // 2, (dh - h) // 2, (dw - w) // 2 + w, (dh - h) // 2 + h))
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

    # Sentiment-Aware Polarity Detection
    left_pol_stamp, left_pol_col = detect_panel_polarity(badge_l, body_l)
    right_pol_stamp, right_pol_col = detect_panel_polarity(badge_r, body_r)

    eff_left_stamp = left_stamp or left_pol_stamp or "stamp_x"
    eff_right_stamp = right_stamp or right_pol_stamp or "stamp_check"
    left_accent_col = left_pol_col or (208, 48, 38)
    right_accent_col = right_pol_col or (28, 152, 82)

    if eff_left_stamp == eff_right_stamp and not left_stamp and not right_stamp:
        eff_left_stamp, left_accent_col = "stamp_x", (208, 48, 38)
        eff_right_stamp, right_accent_col = "stamp_check", (28, 152, 82)

    left_p = min(1.0, max(0.0, dt / 0.55))
    left_alpha = 1.0 - (1.0 - left_p) ** 4 if dt < 0.55 else 1.0
    reveal_t = max(0.75, min(1.45, duration * 0.36))
    right_p = min(1.0, max(0.0, (dt - reveal_t) / 0.55))
    right_alpha = 1.0 - (1.0 - right_p) ** 4 if dt >= reveal_t else 0.08

    if is_shorts:
        # 9:16 Vertical Shorts: Exact 50/50 full-bleed top/bottom split (Y = 50% divider)
        # Content bounded strictly to Y: 12% - 46% (top) and Y: 54% - 72% (bottom) to prevent subtitle collisions!
        div_y = H2 // 2
        top_box = (0, int(H2 * 0.12), W2, int(H2 * 0.46))
        bot_box = (0, int(H2 * 0.54), W2, int(H2 * 0.72))

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
            (top_box, badge_l, body_l, left_accent_col, left_sticker, eff_left_stamp, left_alpha),
            (bot_box, badge_r, body_r, right_accent_col, right_sticker, eff_right_stamp, right_alpha),
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
            ((margin, top_div_y, div_x - gutter, bot_div_y - 110), badge_l, body_l, left_accent_col, left_sticker, eff_left_stamp, left_alpha),
            ((div_x + gutter, top_div_y, W2 - margin, bot_div_y - 110), badge_r, body_r, right_accent_col, right_sticker, eff_right_stamp, right_alpha),
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
    if dt > 0.0:
        drift_scale = 1.00 + 0.035 * min(1.0, dt / 4.8)
        dw = int(w * drift_scale)
        dh = int(h * drift_scale)
        fr = fr.resize((dw, dh), Image.BILINEAR).crop(((dw - w) // 2, (dh - h) // 2, (dw - w) // 2 + w, (dh - h) // 2 + h))
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

    raw_prog = min(1.0, max(0.0, dt / max(1.4, duration * 0.72)))
    prog = (4.0 * (raw_prog ** 3)) if raw_prog < 0.5 else (1.0 - ((-2.0 * raw_prog + 2.0) ** 3) / 2.0)
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
    fr = card_bg(w, h, variant="kraft").convert("RGBA")
    fr.alpha_composite(overlay)
    if dt > 0.0:
        drift_scale = 1.00 + 0.035 * min(1.0, dt / 4.8)
        dw = int(w * drift_scale)
        dh = int(h * drift_scale)
        fr = fr.resize((dw, dh), Image.BILINEAR).crop(((dw - w) // 2, (dh - h) // 2, (dw - w) // 2 + w, (dh - h) // 2 + h))
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

    p_ring = min(1.0, max(0.0, (dt - 0.15) / 1.20))
    prog = 1.0 - (1.0 - p_ring) ** 4
    angle = int(360.0 * (pct / 100.0) * prog)
    if angle > 0:
        d2.arc((cx - radius, cy - radius, cx + radius, cy + radius), start=-90, end=-90 + angle, fill=ACCENT + (255,), width=ring_thick)

    disp_ring_val = _interpolate_stat_numbers(stat_val, prog)
    num_txt = text_layer(disp_ring_val, 140 if is_shorts else 160, INK, font_role="hero")
    overlay2.alpha_composite(num_txt, (cx - num_txt.width // 2, cy - num_txt.height // 2))

    if stat_desc:
        desc_block = render_wrapped_text_block(stat_desc.upper(), "annotation", 92 if is_shorts else 104, 56, int(W2 * 0.76), 160, INK, max_lines=2)
        dy0 = cy + radius + 56
        _draw_highlighter_swipe(overlay2, cx, dy0 + desc_block.height // 2 + 6, desc_block.width + 68, int(desc_block.height * 0.65), SUB_ACCENT + (110,))
        overlay2.alpha_composite(desc_block, (cx - desc_block.width // 2, dy0))

    overlay = overlay2.resize((w, h), Image.LANCZOS)
    fr = card_bg(w, h).convert("RGBA")
    fr.alpha_composite(overlay)
    if dt > 0.0:
        drift_scale = 1.00 + 0.035 * min(1.0, dt / 4.8)
        dw = int(w * drift_scale)
        dh = int(h * drift_scale)
        fr = fr.resize((dw, dh), Image.BILINEAR).crop(((dw - w) // 2, (dh - h) // 2, (dw - w) // 2 + w, (dh - h) // 2 + h))
    return fr


def draw_circle_focus(fr, W, H, dt, cx_norm=0.5, cy_norm=0.45, rx_norm=0.18, ry_norm=0.14, color=None):
    """Primitive 1: Live Hand-Drawn Focus Circle (multi-pass organic marker loop 0%->100% over 0.38s)."""
    if dt < 0.0:
        return
    p = min(1.0, dt / 0.38)
    ease = 1.0 - (1.0 - p) ** 2.4
    cx, cy = int(W * cx_norm), int(H * cy_norm)
    rx, ry = max(36, int(W * rx_norm)), max(36, int(H * ry_norm))
    col = color or ((214, 52, 42, 238) if ACTIVE_LOOK_NAME == "bright" else ACCENT + (238,))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w_px = max(6, int(min(W, H) * 0.0075))
    # Pass 1: primary loop with subtle organic wobble + slight overlap tail
    n_pts = max(8, int(52 * ease))
    pts1 = []
    for i in range(n_pts + 1):
        ang = -0.35 * math.pi + (2.14 * math.pi) * (i / 52.0)
        wob = 1.0 + 0.038 * math.sin(i * 0.72) + 0.018 * math.cos(i * 1.45)
        px = int(cx + rx * wob * math.cos(ang))
        py = int(cy + ry * wob * math.sin(ang))
        pts1.append((px, py))
    if len(pts1) >= 2:
        d.line(pts1, fill=col, width=w_px, joint="curve")
    # Pass 2: subtle second marker pass for authentic hand-drawn weight
    if ease > 0.45:
        n2 = max(4, int(36 * min(1.0, (ease - 0.45) / 0.55)))
        pts2 = []
        for i in range(n2 + 1):
            ang = -0.25 * math.pi + (1.75 * math.pi) * (i / 36.0)
            wob = 1.03 + 0.025 * math.cos(i * 0.9)
            pts2.append((int(cx + rx * wob * math.cos(ang)), int(cy + ry * wob * math.sin(ang))))
        if len(pts2) >= 2:
            d.line(pts2, fill=(col[0], col[1], col[2], 145), width=max(3, w_px // 2), joint="curve")
    fr.alpha_composite(layer)


_spotlight_mask_cache = {}


def draw_spotlight_dim(fr, W, H, dt, duration=3.0, cx_norm=0.5, cy_norm=0.45, rx_norm=0.24, ry_norm=0.22):
    """Primitive 2: Dim + Circular Spotlight (smooth 0->58% dim over 0.28s, soft feathered bright focus, smooth lift)."""
    if dt < 0.0 or dt > duration:
        return
    in_p = min(1.0, dt / 0.28)
    out_p = min(1.0, max(0.0, (duration - dt) / 0.28))
    dim_alpha = 0.58 * (1.0 - (1.0 - in_p) ** 2.2) * (1.0 - (1.0 - out_p) ** 2.0)
    if dim_alpha <= 0.02:
        return
    key = (W, H, round(cx_norm, 3), round(cy_norm, 3), round(rx_norm, 3), round(ry_norm, 3))
    if key not in _spotlight_mask_cache:
        if len(_spotlight_mask_cache) > 16:
            _spotlight_mask_cache.clear()
        yg, xg = np.ogrid[:H, :W]
        dx = (xg - W * cx_norm) / max(24.0, W * rx_norm)
        dy = (yg - H * cy_norm) / max(24.0, H * ry_norm)
        dist = np.sqrt(dx * dx + dy * dy)
        # Inside r<=0.78 is 0% dim (crystal bright); 0.78..1.25 feathers smoothly to 100% dim
        mask_f = np.clip((dist - 0.78) / 0.47, 0.0, 1.0) ** 1.4
        _spotlight_mask_cache[key] = mask_f.astype(np.float32)
    mask_f = _spotlight_mask_cache[key]
    dim_arr = np.zeros((H, W, 4), dtype=np.uint8)
    dim_arr[:, :, 0] = 14
    dim_arr[:, :, 1] = 18
    dim_arr[:, :, 2] = 26
    dim_arr[:, :, 3] = np.clip(mask_f * (255.0 * dim_alpha), 0, 255).astype(np.uint8)
    fr.alpha_composite(Image.fromarray(dim_arr, mode="RGBA"))
    # Subtle animated amber/ink halo ring around spotlight
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    cx, cy = int(W * cx_norm), int(H * cy_norm)
    rx, ry = int(W * rx_norm * 0.96), int(H * ry_norm * 0.96)
    ring_a = int(175 * min(1.0, dim_alpha / 0.58))
    hd.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=SUB_ACCENT + (ring_a,), width=4)
    fr.alpha_composite(halo)


def _detect_head_top_and_salience(im, x0, y0, x1, y1):
    """Inspects an RGB/RGBA image crop for white stickman head + dark ink outline salience."""
    try:
        W_i, H_i = im.size
        cx0, cy0 = max(0, int(x0)), max(0, int(y0))
        cx1, cy1 = min(W_i, int(x1)), min(H_i, int(y1))
        if cx1 <= cx0 + 12 or cy1 <= cy0 + 12:
            return None, 0.0
        arr = np.array(im.crop((cx0, cy0, cx1, cy1)).convert("RGB"), dtype=np.uint8)
        white_mask = (arr[:, :, 0] > 232) & (arr[:, :, 1] > 228) & (arr[:, :, 2] > 218)
        ink_mask = (arr[:, :, 0] < 65) & (arr[:, :, 1] < 65) & (arr[:, :, 2] < 65)
        white_mean = float(white_mask.mean())
        ink_mean = float(ink_mask.mean())
        score = white_mean * 220.0 + ink_mean * 180.0
        # Estimate topmost foreground head/ink row inside crop
        row_fg = (white_mask | ink_mask).mean(axis=1)
        fg_rows = np.where(row_fg > 0.045)[0]
        top_y = int(cy0 + fg_rows[0]) if len(fg_rows) > 0 else None
        return top_y, score
    except Exception:
        return None, 0.0


def _draw_vector_badge_glyph(draw_obj, cx, cy, marker, radius=13, col=(255, 255, 255, 255), width=5):
    """Draws crisp resolution-independent vector ✓ / ✗ / → glyphs inside badge circles (zero missing-font boxes)."""
    r = max(6, int(radius))
    if marker == "✓":
        draw_obj.line([(cx - r, cy + int(r * 0.08)), (cx - int(r * 0.22), cy + int(r * 0.72)), (cx + r, cy - int(r * 0.65))],
                      fill=col, width=width, joint="curve")
    elif marker == "✗":
        d = int(r * 0.72)
        draw_obj.line([(cx - d, cy - d), (cx + d, cy + d)], fill=col, width=width)
        draw_obj.line([(cx + d, cy - d), (cx - d, cy + d)], fill=col, width=width)
    else:
        draw_obj.line([(cx - r, cy), (cx + r - 2, cy)], fill=col, width=width)
        draw_obj.line([(cx + int(r * 0.2), cy - int(r * 0.6)), (cx + r, cy), (cx + int(r * 0.2), cy + int(r * 0.6))],
                      fill=col, width=width, joint="curve")


def draw_strike_replace_card(w, h, text, is_shorts=False, dt=0.0, duration=3.0):
    """Full-Bleed Borderless Editorial Strike & Replace Card (commanding stat hierarchy + per-line highlighters)."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    if ";" in text:
        _, _, body = text.partition(";")
    else:
        body = text
    parts = [p.strip() for p in body.split("|") if p.strip()]
    old_text = parts[0] if len(parts) > 0 else "THE MYTH"
    new_text = parts[1] if len(parts) > 1 else "THE REALITY"

    # Slowly choreographed editorial timing (0.00-0.35s myth entry -> 0.38-0.78s slash + dim -> 0.72-1.25s stat roll -> 1.05-1.45s sub-label)
    p_ent = min(1.0, max(0.0, dt / 0.35))
    ease_ent = 1.0 - (1.0 - p_ent) ** 4
    p_slash = min(1.0, max(0.0, (dt - 0.38) / 0.40))
    ease_slash = 1.0 - (1.0 - p_slash) ** 3
    p_new = min(1.0, max(0.0, (dt - 0.72) / 0.53))
    ease_new = 1.0 - (1.0 - p_new) ** 4
    p_sub = min(1.0, max(0.0, (dt - 1.05) / 0.40))
    ease_sub = 1.0 - (1.0 - p_sub) ** 3
    myth_alpha = ease_ent * (1.0 - 0.45 * ease_slash)

    _draw_editorial_corner_ticks(d2, int(W2 * 0.06), int(H2 * 0.08), int(W2 * 0.94), int(H2 * (0.72 if is_shorts else 0.90)),
                                 INK + (78,), arm=64, width=7, progress=ease_ent)

    # 1. Giant Myth Headline (+40% larger scale, boldly anchored in upper visual band)
    old_im = render_wrapped_text_block(
        old_text.upper(), "hero", start_size=268 if is_shorts else 284, min_size=132,
        max_w=int(W2 * 0.88), max_h=int(H2 * 0.26), color=INK, max_lines=2
    )
    old_sh = _apply_alpha_to_image(_text_with_offset_shadow(old_im, dx=8, dy=10), myth_alpha)
    ox = W2 // 2 - old_sh.width // 2
    oy = int(H2 * (0.21 if is_shorts else 0.26)) - old_sh.height // 2 + int(22 * (1.0 - ease_ent))
    overlay2.alpha_composite(old_sh, (ox, oy))

    # Expressive organic tapered crimson marker slash (0% -> 100% eased across myth phrase)
    if ease_slash > 0.01:
        sx0, sy0 = max(int(W2 * 0.06), ox - 28), oy + int(old_sh.height * 0.68)
        sx1, sy1 = min(int(W2 * 0.94), ox + old_sh.width + 28), oy + int(old_sh.height * 0.30)
        steps_s = 16
        pts_s = [
            (sx0 + (sx1 - sx0) * ease_slash * (k / steps_s),
             sy0 + (sy1 - sy0) * ease_slash * (k / steps_s) - 10 * math.sin(math.pi * (k / steps_s)))
            for k in range(steps_s + 1)
        ]
        base_sw = 34 if is_shorts else 36
        for k in range(len(pts_s) - 1):
            u_s = (k + 0.5) / steps_s
            sw_k = max(14, int(base_sw * (0.78 + 0.32 * math.sin(math.pi * u_s))))
            d2.line([pts_s[k], pts_s[k + 1]], fill=(214, 46, 38, 246), width=sw_k)
            r_nib = sw_k // 2
            d2.ellipse((pts_s[k + 1][0] - r_nib, pts_s[k + 1][1] - r_nib,
                        pts_s[k + 1][0] + r_nib, pts_s[k + 1][1] + r_nib), fill=(214, 46, 38, 246))

    # 2. Commanding Hero Truth Reveal filling Y:18%-68% on 9:16 with per-line aligned highlighters
    if ease_new > 0.02:
        m_stat = re.match(r"^\s*([0-9]+(?:[.,][0-9]+)?[%×xX+]?)\s+(.+)$", new_text.strip())
        if m_stat:
            stat_s = _interpolate_stat_numbers(m_stat.group(1).upper(), ease_new)
            sub_s = m_stat.group(2).upper()
            stat_im = render_wrapped_text_block(
                stat_s, "hero", start_size=420 if is_shorts else 410, min_size=260,
                max_w=int(W2 * 0.88), max_h=int(H2 * 0.25), color=(18, 128, 62), max_lines=1
            )
            stat_sh = _apply_alpha_to_image(_text_with_offset_shadow(stat_im, dx=9, dy=11), ease_new)
            sy_stat = oy + old_sh.height + (190 if is_shorts else 64) + int(28 * (1.0 - ease_new))
            _draw_highlighter_swipe(overlay2, W2 // 2, sy_stat + stat_sh.height // 2 + 12,
                                    int(stat_sh.width * 1.08), int(stat_sh.height * 0.56),
                                    SUB_ACCENT + (135,), tilt=-1.6, progress=ease_new)
            overlay2.alpha_composite(stat_sh, (W2 // 2 - stat_sh.width // 2, sy_stat))

            if ease_sub > 0.02:
                sub_im, line_boxes = render_wrapped_text_block(
                    sub_s, "hero", start_size=148 if is_shorts else 142, min_size=92,
                    max_w=int(W2 * 0.88), max_h=int(H2 * 0.16), color=INK, max_lines=2, return_line_boxes=True
                )
                sub_sh = _apply_alpha_to_image(_text_with_offset_shadow(sub_im, dx=5, dy=7), ease_sub)
                sub_x = W2 // 2 - sub_sh.width // 2
                sub_y = sy_stat + stat_sh.height + (64 if is_shorts else 26)
                _draw_per_line_highlighters(overlay2, W2 // 2 - sub_im.width // 2, sub_y, line_boxes,
                                            color=(142, 224, 172, 132), pad_x=44, progress=ease_sub)
                overlay2.alpha_composite(sub_sh, (sub_x, sub_y))
                last_lb = line_boxes[-1]
                uw = min(int(W2 * 0.82), last_lb[2] + 54)
                uy = sub_y + last_lb[1] + last_lb[3] + 12
                _draw_live_ink_underline(d2, W2 // 2 - uw // 2, uy, W2 // 2 + uw // 2, uy - 4,
                                         progress=ease_sub, color=(18, 128, 62, 240), width=14)
        else:
            new_im, line_boxes = render_wrapped_text_block(
                new_text.upper(), "hero", start_size=236 if is_shorts else 256, min_size=118,
                max_w=int(W2 * 0.88), max_h=int(H2 * 0.30), color=(18, 128, 62), max_lines=2, return_line_boxes=True
            )
            new_sh = _apply_alpha_to_image(_text_with_offset_shadow(new_im, dx=7, dy=9), ease_new)
            nx = W2 // 2 - new_sh.width // 2
            ny = oy + old_sh.height + (150 if is_shorts else 64) + int(28 * (1.0 - ease_new))
            _draw_per_line_highlighters(overlay2, W2 // 2 - new_im.width // 2, ny, line_boxes,
                                        color=SUB_ACCENT + (125,), pad_x=44, progress=ease_new)
            overlay2.alpha_composite(new_sh, (nx, ny))
            last_lb = line_boxes[-1]
            rw = min(int(W2 * 0.82), last_lb[2] + 50)
            uy = ny + last_lb[1] + last_lb[3] + 12
            _draw_live_ink_underline(d2, W2 // 2 - rw // 2, uy, W2 // 2 + rw // 2, uy - 4,
                                     progress=ease_new, color=(18, 128, 62, 240), width=14)

    fr = card_bg(w, h, variant="default").convert("RGBA")
    fr.alpha_composite(overlay2.resize((w, h), Image.LANCZOS))
    p_drift = min(1.0, max(0.0, dt / max(0.5, duration)))
    drift_scale = 1.00 + 0.025 * (0.55 * (1.0 - (1.0 - p_drift) ** 3) + 0.45 * p_drift)
    dw, dh = int(w * drift_scale), int(h * drift_scale)
    return fr.resize((dw, dh), Image.BILINEAR).crop(((dw - w) // 2, (dh - h) // 2, (dw - w) // 2 + w, (dh - h) // 2 + h))


def draw_strike_replace(fr, W, H, dt, old_text, new_text="", cx_norm=0.5, cy_norm=0.42, is_shorts=False, mode="replace", placement="below", exit_alpha=1.0):
    """Primitive 3: Strike & Replace — uses clean upper sky when truly free, or auto-promotes to full-bleed card so faces are NEVER hidden."""
    if dt < 0.0 or exit_alpha <= 0.02:
        return
    p_ent = min(1.0, dt / 0.20)
    ease_ent = 1.0 - (1.0 - p_ent) ** 3
    p_slash = min(1.0, max(0.0, (dt - 0.14) / 0.25))
    ease_slash = 1.0 - (1.0 - p_slash) ** 2.4
    p_new = min(1.0, max(0.0, (dt - 0.32) / 0.26))
    ease_new = 1.0 - (1.0 - p_new) ** 3

    cx, cy = int(W * cx_norm), int(H * cy_norm)
    if mode == "strike_x":
        # Animated 2-stroke red X stamp strictly faded with its target sticker (zero orphan X)
        sz = 164 if is_shorts else 184
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        r = sz // 2
        a_x = int(242 * max(0.0, min(1.0, exit_alpha)))
        p1 = min(1.0, dt / 0.16)
        p2 = min(1.0, max(0.0, (dt - 0.14) / 0.16))
        if p1 > 0:
            d.line((cx - r, cy - r, int(cx - r + 2 * r * p1), int(cy - r + 2 * r * p1)), fill=(214, 46, 38, a_x), width=15)
        if p2 > 0:
            d.line((cx + r, cy - r, int(cx + r - 2 * r * p2), int(cy - r + 2 * r * p2)), fill=(214, 46, 38, a_x), width=15)
        fr.alpha_composite(layer)
        return

    # Inspect upper open sky bands ONLY (never cover center character heads!)
    sky_cands = [(0.50, 0.16), (0.26, 0.18), (0.74, 0.18)] if is_shorts else [(0.24, 0.20), (0.76, 0.20), (0.50, 0.17)]
    best_pt = None
    best_sc = float("inf")
    probe_w = int(W * (0.64 if is_shorts else 0.38))
    probe_h = int(H * (0.16 if is_shorts else 0.22))
    for px_n, py_n in sky_cands:
        px, py = int(W * px_n), int(H * py_n)
        _, sc_sal = _detect_head_top_and_salience(fr, px - probe_w // 2, py - probe_h // 2, px + probe_w // 2, py + probe_h // 2)
        if sc_sal < best_sc:
            best_sc = sc_sal
            best_pt = (px, py)

    # If no open upper zone exists free of head/artwork, auto-promote to crisp full-bleed card!
    if best_pt is None or best_sc > 34.0:
        card_fr = draw_strike_replace_card(W, H, f"{old_text}|{new_text}", is_shorts=is_shorts, dt=dt, duration=3.0)
        fr.paste(card_fr, (0, 0))
        return

    cx, cy = best_pt
    old_im = render_wrapped_text_block(
        old_text.upper(), "hero", start_size=62 if is_shorts else 68, min_size=40,
        max_w=int(W * (0.74 if is_shorts else 0.42)), max_h=110, color=INK, max_lines=1
    )
    pad_x, pad_y = 32, 16
    pw, ph = old_im.width + pad_x * 2, old_im.height + pad_y * 2
    box = Image.new("RGBA", (pw + 16, ph + 16), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle((10, 12, 10 + pw, 12 + ph), radius=18, fill=(0, 0, 0, int(52 * ease_ent)))
    bd.rounded_rectangle((6, 6, 6 + pw, 6 + ph), radius=18, fill=PAPER + (int(248 * ease_ent),), outline=INK + (int(235 * ease_ent),), width=4)
    box.alpha_composite(_apply_alpha_to_image(old_im, ease_ent), (6 + pad_x, 6 + pad_y))
    if ease_slash > 0.01:
        x0, y0 = 16, ph // 2 + 10
        x1, y1 = pw - 6, ph // 2 - 4
        bd.line((x0, y0, int(x0 + (x1 - x0) * ease_slash), int(y0 + (y1 - y0) * ease_slash)), fill=(214, 46, 38, 245), width=11)

    dy_old = int(14 * (1.0 - ease_ent))
    fr.alpha_composite(box, (cx - box.width // 2, cy - box.height // 2 + dy_old))

    if new_text and ease_new > 0.02:
        new_im = render_wrapped_text_block(
            new_text.upper(), "hero", start_size=60 if is_shorts else 66, min_size=40,
            max_w=int(W * (0.74 if is_shorts else 0.42)), max_h=110, color=(26, 138, 72), max_lines=1
        )
        npw, nph = new_im.width + pad_x * 2, new_im.height + pad_y * 2
        nbox = Image.new("RGBA", (npw + 16, nph + 16), (0, 0, 0, 0))
        nbd = ImageDraw.Draw(nbox)
        nbd.rounded_rectangle((10, 12, 10 + npw, 12 + nph), radius=18, fill=(0, 0, 0, int(52 * ease_new)))
        nbd.rounded_rectangle((6, 6, 6 + npw, 6 + nph), radius=18, fill=(238, 250, 242, int(250 * ease_new)), outline=(26, 138, 72, int(240 * ease_new)), width=4)
        nbox.alpha_composite(_apply_alpha_to_image(new_im, ease_new), (6 + pad_x, 6 + pad_y))
        _draw_live_ink_underline(nbd, 20, 6 + nph - 8, 6 + npw - 20, 6 + nph - 10, progress=ease_new, color=(26, 138, 72, 235), width=5)
        ny = cy + box.height // 2 + 12 + int(16 * (1.0 - ease_new))
        fr.alpha_composite(nbox, (cx - nbox.width // 2, ny))


_checklist_frost_cache = {}


def _get_checklist_frost_overlay(w, h, mode):
    """Creates cached smooth feathered translucent frosted parchment scrim (alpha peaks ~0.72 -> 0.0 seamlessly, ZERO hard lines)."""
    key = (w, h, mode)
    if key in _checklist_frost_cache:
        return _checklist_frost_cache[key]

    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[:, :, 0] = 248
    arr[:, :, 1] = 243
    arr[:, :, 2] = 232

    if mode == "short_mid":
        y_n = (np.arange(h, dtype=np.float32) / max(1, h - 1))[:, None]
        a = np.zeros_like(y_n)
        # Smooth cubic fade-in Y: 0.38 -> 0.49
        m_in = (y_n >= 0.38) & (y_n < 0.49)
        t_in = (y_n[m_in] - 0.38) / 0.11
        a[m_in] = 0.74 * (3.0 * t_in ** 2 - 2.0 * t_in ** 3)
        # Soft translucent core Y: 0.49 -> 0.74 (above 81% subtitle pill)
        a[(y_n >= 0.49) & (y_n <= 0.74)] = 0.74
        # Smooth cubic fade-out Y: 0.74 -> 0.805
        m_out = (y_n > 0.74) & (y_n <= 0.805)
        t_out = (y_n[m_out] - 0.74) / 0.065
        a[m_out] = 0.74 * (1.0 - (3.0 * t_out ** 2 - 2.0 * t_out ** 3))
        arr[:, :, 3] = np.broadcast_to((a * 255.0).clip(0, 255).astype(np.uint8), (h, w))
    else:
        x_n = (np.arange(w, dtype=np.float32) / max(1, w - 1))[None, :]
        if mode == "right":
            x_n = 1.0 - x_n
        a = np.zeros_like(x_n)
        a[x_n <= 0.34] = 0.72
        m_fall = (x_n > 0.34) & (x_n <= 0.54)
        t_f = (x_n[m_fall] - 0.34) / 0.20
        a[m_fall] = 0.72 * (1.0 - (3.0 * t_f ** 2 - 2.0 * t_f ** 3))
        arr[:, :, 3] = np.broadcast_to((a * 255.0).clip(0, 255).astype(np.uint8), (h, w))

    im = Image.fromarray(arr, mode="RGBA")
    _checklist_frost_cache[key] = im
    return im


def draw_checklist_build(fr, W, H, dt, items, item_times=None, t_abs=0.0, is_shorts=False, side="auto", layout_cache=None, cache_key=None, title="", raw_scene_im=None, cam_u=0.0):
    """Primitive 4: Seamless Translucent Frosted Checklist Over 100% Full-Bleed Artwork (ZERO opaque panels or hard divider lines)."""
    if not items or dt < 0.0:
        return
    items = items[:4]
    n = len(items)
    p_panel = min(1.0, max(0.0, dt / 0.24))
    ease_hdr = 1.0 - (1.0 - p_panel) ** 3
    hdr_txt = str(title or "").strip().upper() or "KEY FACTORS"

    def _halo_text_block(txt_str, font_role, start_sz, min_sz, max_w, max_h, max_lines=2):
        core = render_wrapped_text_block(txt_str, font_role, start_size=start_sz, min_size=min_sz, max_w=max_w, max_h=max_h, color=INK, max_lines=max_lines)
        # Subtle warm paper outer glow + crisp dark-ink soft shadow so letters pop seamlessly over illustrated details
        pad = 10
        canvas = Image.new("RGBA", (core.width + pad * 2, core.height + pad * 2), (0, 0, 0, 0))
        a_ch = core.split()[3]
        halo_rgb = Image.new("RGBA", core.size, (252, 248, 238, 0))
        halo_rgb.putalpha(a_ch.filter(ImageFilter.MaxFilter(5)))
        canvas.alpha_composite(_apply_alpha_to_image(halo_rgb, 0.78), (pad, pad))
        sh = _text_with_offset_shadow(core, dx=3, dy=5, shadow_col=(18, 16, 14, 48))
        canvas.alpha_composite(sh, (pad, pad))
        return canvas, core.width, core.height

    if is_shorts:
        # Seamless soft translucent gradient in Y: 38% -> 80% over 100% full-bleed illustration
        frost = _get_checklist_frost_overlay(W, H, "short_mid")
        fr.alpha_composite(frost)

        pad_x = 64
        hy = int(H * 0.455)
        hdr_halo, hdr_w, hdr_h = _halo_text_block(hdr_txt, "hero", 58, 42, W - pad_x * 2, 96, max_lines=1)
        fr.alpha_composite(_apply_alpha_to_image(hdr_halo, min(1.0, ease_hdr * 1.4)), (pad_x - 10, hy - 10))
        d_u = ImageDraw.Draw(fr)
        _draw_live_ink_underline(d_u, pad_x, hy + hdr_h + 10, min(W - pad_x, pad_x + hdr_w + 42),
                                 hy + hdr_h + 7, progress=max(0.4, ease_hdr), color=ACCENT + (235,), width=6)

        list_top = hy + hdr_h + 34
        list_bot = int(H * 0.765)  # strictly clear above Y >= 81% subtitles
        avail_h = max(300, list_bot - list_top)
        row_pitch = min(158, avail_h // max(1, n))
        row_h = max(90, row_pitch - 14)
        text_w = W - pad_x * 2 - 116
        text_size = 56 if n <= 3 else 48
        badge_r = 34 if n <= 3 else 30

        for idx, raw_it in enumerate(items):
            dt_it = (t_abs - float(item_times[idx])) if (item_times and idx < len(item_times)) else (dt - idx * 0.45)
            if dt_it < 0.0:
                continue
            p_it = min(1.0, dt_it / 0.24)
            ease_it = 1.0 - (1.0 - p_it) ** 3
            dy_it = int(18 * (1.0 - ease_it))

            txt_str = str(raw_it).strip()
            marker, m_col = "✓", (24, 152, 76)
            if txt_str.startswith(("✗", "X:", "x:")):
                marker, m_col = "✗", (214, 52, 42)
                txt_str = txt_str.lstrip("✗Xx:").strip()
            elif txt_str.startswith(("->", "→")):
                marker, m_col = "→", ACCENT
                txt_str = txt_str.lstrip("-→>").strip()
            elif txt_str.startswith("✓"):
                txt_str = txt_str.lstrip("✓").strip()

            ry = list_top + idx * row_pitch + dy_it
            row2 = Image.new("RGBA", ((W - pad_x * 2) * 2, row_h * 2), (0, 0, 0, 0))
            rd2 = ImageDraw.Draw(row2)
            bcx, bcy, br2 = badge_r * 2 + 6, row2.height // 2, badge_r * 2
            rd2.ellipse((bcx - br2 + 4, bcy - br2 + 6, bcx + br2 + 4, bcy + br2 + 6), fill=(0, 0, 0, int(48 * ease_it)))
            rd2.ellipse((bcx - br2, bcy - br2, bcx + br2, bcy + br2), fill=m_col + (int(250 * ease_it),), outline=INK + (int(242 * ease_it),), width=6)
            _draw_vector_badge_glyph(rd2, bcx, bcy, marker, radius=int(br2 * 0.50), col=(255, 255, 255, int(255 * ease_it)), width=12)

            lbl_im, _, _ = _halo_text_block(txt_str.upper(), "hero", text_size * 2, 78, text_w * 2, row2.height - 12, max_lines=2)
            row2.alpha_composite(_apply_alpha_to_image(lbl_im, ease_it), (bcx + br2 + 26, (row2.height - lbl_im.height) // 2))
            fr.alpha_composite(row2.resize((W - pad_x * 2, row_h), Image.LANCZOS), (pad_x, ry))
        return

    # 16:9 Widescreen: Lock cleaner side ONCE per scene & composite smooth feathered horizontal frost (0% -> 54% alpha->0.0)
    use_side = None
    if layout_cache is not None and cache_key and cache_key in layout_cache:
        use_side = layout_cache[cache_key]
    if not use_side:
        req_s = str(side).strip().lower()
        if req_s in ("left", "right"):
            use_side = req_s
        else:
            _, l_sc = _detect_head_top_and_salience(fr, 48, int(H * 0.14), int(W * 0.44), int(H * 0.84))
            _, r_sc = _detect_head_top_and_salience(fr, int(W * 0.56), int(H * 0.14), W - 48, int(H * 0.84))
            use_side = "left" if l_sc <= r_sc else "right"
        if layout_cache is not None and cache_key:
            layout_cache[cache_key] = use_side

    frost = _get_checklist_frost_overlay(W, H, use_side)
    fr.alpha_composite(frost)

    col_w = int(W * 0.41)
    pad_x = 64 if use_side == "left" else (W - col_w + 24)
    hy = 96
    hdr_halo, hdr_w, hdr_h = _halo_text_block(hdr_txt, "hero", 62, 42, col_w - 72, 110, max_lines=1)
    fr.alpha_composite(_apply_alpha_to_image(hdr_halo, min(1.0, ease_hdr * 1.4)), (pad_x - 10, hy - 10))
    d_u = ImageDraw.Draw(fr)
    _draw_live_ink_underline(d_u, pad_x, hy + hdr_h + 10, min(pad_x + col_w - 64, pad_x + hdr_w + 42),
                             hy + hdr_h + 6, progress=max(0.4, ease_hdr), color=ACCENT + (235,), width=6)

    list_top = hy + hdr_h + 66
    list_bot = H - 150
    avail_h = max(420, list_bot - list_top)
    row_pitch = min(194, avail_h // max(1, n))
    row_h = max(124, row_pitch - 18)
    panel_inner_w = col_w - 56
    text_w = panel_inner_w - 110

    for idx, raw_it in enumerate(items):
        dt_it = (t_abs - float(item_times[idx])) if (item_times and idx < len(item_times)) else (dt - idx * 0.45)
        if dt_it < 0.0:
            continue
        p_it = min(1.0, dt_it / 0.24)
        ease_it = 1.0 - (1.0 - p_it) ** 3
        dx_it = int((-22 if use_side == "left" else 22) * (1.0 - ease_it))

        txt_str = str(raw_it).strip()
        marker, m_col = "✓", (24, 152, 76)
        if txt_str.startswith(("✗", "X:", "x:")):
            marker, m_col = "✗", (214, 52, 42)
            txt_str = txt_str.lstrip("✗Xx:").strip()
        elif txt_str.startswith(("->", "→")):
            marker, m_col = "→", ACCENT
            txt_str = txt_str.lstrip("-→>").strip()
        elif txt_str.startswith("✓"):
            txt_str = txt_str.lstrip("✓").strip()

        ry = list_top + idx * row_pitch
        row2 = Image.new("RGBA", (panel_inner_w * 2, row_h * 2), (0, 0, 0, 0))
        rd2 = ImageDraw.Draw(row2)
        bcx, bcy, br2 = 72, row2.height // 2, 62
        rd2.ellipse((bcx - br2 + 4, bcy - br2 + 6, bcx + br2 + 4, bcy + br2 + 6), fill=(0, 0, 0, int(48 * ease_it)))
        rd2.ellipse((bcx - br2, bcy - br2, bcx + br2, bcy + br2), fill=m_col + (int(250 * ease_it),), outline=INK + (int(242 * ease_it),), width=6)
        _draw_vector_badge_glyph(rd2, bcx, bcy, marker, radius=31, col=(255, 255, 255, int(255 * ease_it)), width=12)

        lbl_im, _, _ = _halo_text_block(txt_str.upper(), "hero", 112, 76, text_w * 2, row2.height - 14, max_lines=2)
        row2.alpha_composite(_apply_alpha_to_image(lbl_im, ease_it), (bcx + br2 + 26, (row2.height - lbl_im.height) // 2))
        fr.alpha_composite(row2.resize((panel_inner_w, row_h), Image.LANCZOS), (pad_x + dx_it, ry))


def draw_era_anchor(fr, W, H, dt, label, is_shorts=False):
    """Primitive 5: Persistent Top-Left Era / Date Anchor (sleek editorial chronological pill)."""
    if not label or dt < 0.0:
        return
    p = min(1.0, dt / 0.28)
    ease = 1.0 - (1.0 - p) ** 3
    dx = int(-28 * (1.0 - ease))
    lbl_im = text_layer(str(label).strip().upper(), 28 if is_shorts else 26, (250, 248, 240), font_role="hero")
    pw = lbl_im.width + 58
    ph = lbl_im.height + 24
    px = (34 if is_shorts else 42) + dx
    py = 96 if is_shorts else 38
    pill = Image.new("RGBA", (pw + 12, ph + 12), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((6, 8, 6 + pw, 8 + ph), radius=14, fill=(0, 0, 0, int(65 * ease)))
    pd.rounded_rectangle((4, 4, 4 + pw, 4 + ph), radius=14, fill=(24, 28, 38, int(238 * ease)), outline=ACCENT + (int(220 * ease),), width=2)
    pd.ellipse((18, 4 + ph // 2 - 5, 28, 4 + ph // 2 + 5), fill=ACCENT + (int(245 * ease),))
    pill.alpha_composite(_apply_alpha_to_image(lbl_im, ease), (38, 4 + (ph - lbl_im.height) // 2))
    fr.alpha_composite(pill, (px, py))


def draw_inset_shelf(fr, W, H, dt, items, item_times=None, t_abs=0.0, is_shorts=False, resolve_fn=None, layout_cache=None, cache_key=None, scene_end_t=None):
    """Primitive 6A: Circular/Flanking Evidence Insets — >=72px above character head OR borderless flanking props on left/right."""
    if not items or dt < 0.0:
        return
    items = items[:3]
    n = len(items)

    spec_lay = None
    if layout_cache is not None and cache_key and cache_key in layout_cache:
        spec_lay = layout_cache[cache_key]

    if spec_lay is None:
        if is_shorts:
            head_top, _ = _detect_head_top_and_salience(fr, int(W * 0.22), int(H * 0.12), int(W * 0.78), int(H * 0.62))
            avail_above = (head_top - 72 - 108) if head_top is not None else 400
            if avail_above >= 225:
                diam = max(168, min(204, avail_above - 54))
                cy = max(108 + diam // 2, head_top - 72 - 54 - diam // 2)
                spec_lay = {"mode": "top_circles", "diam": diam, "gap": 30, "cy": cy}
            else:
                # Tight headroom: use high center crown slot ONLY if prop+tag stays >=24px above detected head_top
                top_cy = int(H * 0.095)
                top_d = 136
                can_top_arc = (head_top is None) or (top_cy + top_d // 2 + 52 <= head_top - 24)
                if can_top_arc:
                    slots = [
                        (int(W * 0.17), int(H * 0.21)),
                        (int(W * 0.50), top_cy),
                        (int(W * 0.83), int(H * 0.21)),
                    ]
                    spec_lay = {"mode": "flank_props", "diam": top_d, "slots": slots}
                else:
                    slots = [
                        (int(W * 0.16), int(H * 0.21)),
                        (int(W * 0.84), int(H * 0.21)),
                        (int(W * 0.16), int(H * 0.43)),
                    ]
                    spec_lay = {"mode": "flank_props", "diam": 156, "slots": slots}
        else:
            _, top_sc = _detect_head_top_and_salience(fr, int(W * 0.20), int(H * 0.04), int(W * 0.80), int(H * 0.34))
            _, bot_sc = _detect_head_top_and_salience(fr, int(W * 0.20), int(H * 0.56), int(W * 0.80), int(H * 0.86))
            cy = int(H * 0.185) if top_sc <= bot_sc else int(H * 0.70)
            spec_lay = {"mode": "top_circles", "diam": 234, "gap": 58, "cy": cy}
        if layout_cache is not None and cache_key:
            layout_cache[cache_key] = spec_lay

    mode = spec_lay["mode"]
    diam = spec_lay["diam"]

    eff_times = [float(x) for x in item_times] if item_times else None
    if eff_times and scene_end_t is not None:
        max_end = float(scene_end_t) - 0.55
        if eff_times[-1] > max_end:
            eff_times[-1] = max_end
            for j in range(len(eff_times) - 2, -1, -1):
                if eff_times[j] > eff_times[j + 1] - 0.24:
                    eff_times[j] = eff_times[j + 1] - 0.24

    for idx, spec in enumerate(items):
        if eff_times and idx < len(eff_times):
            dt_it = t_abs - eff_times[idx]
        else:
            dt_it = dt - idx * 0.45
        if dt_it < 0.0:
            continue
        p = min(1.0, dt_it / 0.26)
        ease = 1.0 - (1.0 - p) ** 3
        scale = 0.72 + 0.28 * ease
        dy = int(26 * (1.0 - ease))

        if isinstance(spec, dict):
            stk_tok = spec.get("img", "")
            lbl_txt = spec.get("label", "")
        else:
            stk_tok = str(spec)
            lbl_txt = os.path.splitext(os.path.basename(stk_tok))[0].replace("cc0_", "").replace("_", " ")

        stk_path = resolve_fn(stk_tok, single_object_only=True) if resolve_fn else (stk_tok if os.path.exists(stk_tok) else None)
        cur_d = max(48, int(diam * scale))

        if mode == "flank_props":
            slots = spec_lay["slots"]
            cx, cy = slots[idx % len(slots)]
            if stk_path and os.path.exists(stk_path):
                s_im = fit_sticker_in_box(stk_path, max_w=cur_d, max_h=cur_d, t_sec=dt_it)
                if s_im:
                    s_sh = add_sticker_drop_shadow(_apply_alpha_to_image(s_im, ease), offset=(6, 9), shadow_color=(0, 0, 0, 56), blur_radius=7)
                    fr.alpha_composite(s_sh, (cx - s_sh.width // 2, cy - s_sh.height // 2 + dy))
            if lbl_txt and ease > 0.35:
                tag = tag_image(lbl_txt.upper()[:18], 24)
                fr.alpha_composite(_apply_alpha_to_image(tag, ease), (cx - tag.width // 2, cy + cur_d // 2 + 8 + dy))
        else:
            gap = spec_lay["gap"]
            total_w = n * diam + (n - 1) * gap
            start_x = (W - total_w) // 2
            cx = start_x + idx * (diam + gap) + diam // 2
            cy = spec_lay["cy"]
            plate = Image.new("RGBA", (cur_d + 20, cur_d + 20), (0, 0, 0, 0))
            pd = ImageDraw.Draw(plate)
            pd.ellipse((12, 14, 12 + cur_d, 14 + cur_d), fill=(0, 0, 0, int(62 * ease)))
            pd.ellipse((8, 8, 8 + cur_d, 8 + cur_d), fill=PAPER + (int(250 * ease),), outline=INK + (int(240 * ease),), width=5)
            pd.ellipse((16, 16, cur_d, cur_d), outline=ACCENT + (int(145 * ease),), width=2)
            if stk_path and os.path.exists(stk_path):
                s_im = fit_sticker_in_box(stk_path, max_w=int(cur_d * 0.72), max_h=int(cur_d * 0.72), t_sec=dt_it)
                if s_im:
                    plate.alpha_composite(_apply_alpha_to_image(s_im, ease), (8 + (cur_d - s_im.width) // 2, 8 + (cur_d - s_im.height) // 2))
            fr.alpha_composite(plate, (cx - plate.width // 2, cy - plate.height // 2 + dy))
            if lbl_txt and ease > 0.35:
                tag = tag_image(lbl_txt.upper()[:22], 24 if is_shorts else 26)
                fr.alpha_composite(_apply_alpha_to_image(tag, ease), (cx - tag.width // 2, cy + cur_d // 2 + 12 + dy))


def draw_pip_inset(fr, W, H, dt, duration, src_img, label="EVIDENCE", is_shorts=False):
    """Primitive 4B: Clean Ink-Bordered Picture-in-Picture Frame (slide-in ease + soft shadow) for evidence & callbacks."""
    if src_img is None or dt < 0.0 or dt > duration:
        return
    p_in = min(1.0, dt / 0.30)
    p_out = min(1.0, max(0.0, (duration - dt) / 0.25))
    ease = (1.0 - (1.0 - p_in) ** 3) * (1.0 - (1.0 - p_out) ** 2)
    if ease <= 0.02:
        return
    pip_w = int(W * (0.34 if is_shorts else 0.26))
    pip_h = int(pip_w * (src_img.height / max(1, src_img.width)))
    pip_h = min(pip_h, int(H * 0.28))
    dx = int(42 * (1.0 - p_in) ** 3)
    px = W - pip_w - (40 if is_shorts else 52) + dx
    py = 165 if is_shorts else 52

    thumb = src_img.convert("RGBA").resize((pip_w, pip_h), Image.LANCZOS)
    frame = Image.new("RGBA", (pip_w + 28, pip_h + 28), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle((12, 14, 22 + pip_w, 24 + pip_h), radius=18, fill=(0, 0, 0, int(75 * ease)))
    fd.rounded_rectangle((6, 6, 18 + pip_w, 18 + pip_h), radius=18, fill=PAPER + (int(252 * ease),), outline=INK + (int(240 * ease),), width=4)
    frame.alpha_composite(_apply_alpha_to_image(thumb, ease), (12, 12))
    fr.alpha_composite(frame, (px - 12, py - 12))
    if label:
        tag = text_layer(label.upper(), 20, (250, 248, 240), font_role="hero")
        tw, th = tag.width + 24, tag.height + 12
        tb = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        tbd = ImageDraw.Draw(tb)
        tbd.rounded_rectangle((0, 0, tw, th), radius=10, fill=ACCENT + (int(240 * ease),))
        tb.alpha_composite(_apply_alpha_to_image(tag, ease), (12, 6))
        fr.alpha_composite(tb, (px + 12, py + pip_h - th // 2 + 4))


def draw_pip_flashback(fr, W, H, dt, duration, src_img, label="CALLBACK", is_shorts=False):
    return draw_pip_inset(fr, W, H, dt, duration, src_img, label=label, is_shorts=is_shorts)


def draw_chapter_breather(w, h, text, is_shorts=False, dt=0.0, duration=2.0):
    """Primitive 4A: Clean 1.8s-2.4s Textured-Background Chapter Breather Card to reset visual fatigue."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    p_ent = min(1.0, max(0.0, dt / 0.32))
    ease = 1.0 - (1.0 - p_ent) ** 3
    dy = int(38 * (1.0 - ease))
    rule_p = min(1.0, max(0.0, (dt - 0.14) / 0.35))
    ease_r = 1.0 - (1.0 - rule_p) ** 2.2

    parts = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else [text.strip()]
    title = parts[0] if parts else "CHAPTER"
    sub = parts[1] if len(parts) > 1 else ""

    max_w = int(W2 * (0.82 if is_shorts else 0.74))
    _draw_editorial_corner_ticks(d2, int(W2 * 0.08), int(H2 * 0.12), int(W2 * 0.92), int(H2 * (0.68 if is_shorts else 0.88)),
                                 INK + (64,), arm=52, width=6, progress=ease)
    t_im = render_wrapped_text_block(
        title.upper(), "hero", start_size=185 if is_shorts else 205, min_size=96,
        max_w=max_w, max_h=int(H2 * 0.24), color=INK, max_lines=2
    )
    t_im = _apply_alpha_to_image(_text_with_offset_shadow(t_im, dx=7, dy=9), min(1.0, ease * 1.3))
    cy = int(H2 * (0.40 if is_shorts else 0.47)) - t_im.height // 2 + dy
    overlay2.alpha_composite(t_im, (W2 // 2 - t_im.width // 2, cy))

    rw = min(int(max_w * 0.75), t_im.width + 60)
    ry = cy + t_im.height + 28
    _draw_live_ink_underline(d2, W2 // 2 - rw // 2, ry, W2 // 2 + rw // 2, ry - 4,
                             progress=ease_r, color=ACCENT + (240,), width=12)
    if sub:
        s_im = render_wrapped_text_block(
            sub.upper(), "annotation", start_size=76 if is_shorts else 82, min_size=48,
            max_w=max_w, max_h=150, color=ACCENT, max_lines=2
        )
        overlay2.alpha_composite(_apply_alpha_to_image(s_im, ease), (W2 // 2 - s_im.width // 2, ry + 34))

    fr = card_bg(w, h, variant="breather").convert("RGBA")
    fr.alpha_composite(overlay2.resize((w, h), Image.LANCZOS))
    drift_scale = 1.00 + 0.03 * min(1.0, dt / max(0.5, duration))
    dw, dh = int(w * drift_scale), int(h * drift_scale)
    return fr.resize((dw, dh), Image.BILINEAR).crop(((dw - w) // 2, (dh - h) // 2, (dw - w) // 2 + w, (dh - h) // 2 + h))


def draw_scale_compare(w, h, text, is_shorts=False, dt=0.0, duration=3.5):
    """Primitive 7B: Custom Vox/Good-Enough Editorial Scale Chart (thick bars, gridlines, giant stats, 66x arrow badge, ZERO screen shake)."""
    W2, H2 = 2 * w, 2 * h
    overlay2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)

    title = "SCALE COMPARISON"
    body = text
    if ";" in text:
        title, _, body = text.partition(";")
        title = title.strip().upper()
    parts = [p.strip() for p in body.split("|") if p.strip()]
    lbl_a = parts[0] if len(parts) > 0 else "BEFORE"
    val_a_str = parts[1] if len(parts) > 1 else "5%"
    lbl_b = parts[2] if len(parts) > 2 else "AFTER"
    val_b_str = parts[3] if len(parts) > 3 else "90%"

    def _num(s):
        m = re.search(r"[\d,.]+", s)
        try:
            return float(m.group(0).replace(",", "")) if m else 10.0
        except Exception:
            return 10.0

    na, nb = max(0.1, _num(val_a_str)), max(0.1, _num(val_b_str))
    m_max = max(na, nb)
    frac_a = max(0.06, na / m_max)
    frac_b = max(0.06, nb / m_max)

    # Staged slow cubic-bezier bar reveal (title 0->0.28s, Bar A 0.25->0.70s, Bar B 0.65->1.75s, arrow 1.55->2.05s, badge 1.90->2.30s)
    p_a = min(1.0, max(0.0, (dt - 0.25) / 0.45))
    ease_a = 1.0 - (1.0 - p_a) ** 4
    p_b = min(1.0, max(0.0, (dt - 0.65) / 1.10))
    ease_b = (4.0 * (p_b ** 3)) if p_b < 0.5 else (1.0 - ((-2.0 * p_b + 2.0) ** 3) / 2.0)

    hdr = render_wrapped_text_block(title, "hero", 212 if is_shorts else 224, 128, int(W2 * 0.88), 260, INK, max_lines=1)
    hdr_y = int(H2 * (0.085 if is_shorts else 0.09))
    overlay2.alpha_composite(_text_with_offset_shadow(hdr, dx=7, dy=9), (W2 // 2 - hdr.width // 2, hdr_y))
    _draw_live_ink_underline(d2, int(W2 * 0.12), hdr_y + hdr.height + 18, int(W2 * 0.88), hdr_y + hdr.height + 14,
                             progress=min(1.0, dt / 0.28), color=ACCENT + (242,), width=14)

    bx0 = int(W2 * 0.085)
    max_bar_w = int(W2 * 0.83)
    bar_h = 264 if is_shorts else 284
    y_a = int(H2 * (0.26 if is_shorts else 0.30))
    y_b = int(H2 * (0.50 if is_shorts else 0.58))

    # Subtle vertical editorial gridlines & baseline ticks (0%, 25%, 50%, 75%, 100%)
    grid_top = y_a - 24
    grid_bot = y_b + bar_h + 24
    for g_pct in (0, 25, 50, 75, 100):
        gx = bx0 + int(max_bar_w * (g_pct / 100.0))
        d2.line((gx, grid_top, gx, grid_bot), fill=INK + (44 if g_pct == 0 else 26,), width=4 if g_pct == 0 else 3)
        tick_lbl = _apply_alpha_to_image(text_layer(f"{g_pct}%", 42 if is_shorts else 44, INK, font_role="annotation"), 0.50)
        overlay2.alpha_composite(tick_lbl, (gx - tick_lbl.width // 2, grid_bot + 10))

    bar_meta = []
    for lbl_s, val_s, frac, ease, yy, col in (
        (lbl_a, val_a_str, frac_a, ease_a, y_a, (54, 126, 198)),
        (lbl_b, val_b_str, frac_b, ease_b, y_b, ACCENT),
    ):
        l_im = render_wrapped_text_block(lbl_s.upper(), "hero", 96 if is_shorts else 104, 64, max_bar_w, 130, INK, max_lines=1)
        overlay2.alpha_composite(l_im, (bx0 + 6, yy - l_im.height - 20))

        # Faint empty bar guide track + crisp drop shadow on fill
        d2.rounded_rectangle((bx0, yy, bx0 + max_bar_w, yy + bar_h), radius=34, fill=(232, 226, 212, 135), outline=INK + (110,), width=4)
        cur_w = max(68, int(max_bar_w * frac * ease)) if ease > 0.01 else 0
        if cur_w > 0:
            d2.rounded_rectangle((bx0 + 12, yy + 14, bx0 + cur_w + 12, yy + bar_h + 14), radius=34, fill=(0, 0, 0, 52))
            # Render textured editorial fill bar inside rounded clip
            bar_im = Image.new("RGBA", (cur_w, bar_h), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bar_im)
            bd.rounded_rectangle((0, 0, cur_w - 1, bar_h - 1), radius=34, fill=col + (248,))
            stripe_layer = Image.new("RGBA", (cur_w, bar_h), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stripe_layer)
            for sx in range(-bar_h, cur_w + bar_h, 46):
                sd.line((sx, bar_h, sx + bar_h, 0), fill=(255, 255, 255, 26), width=14)
            mask_im = Image.new("L", (cur_w, bar_h), 0)
            ImageDraw.Draw(mask_im).rounded_rectangle((0, 0, cur_w - 1, bar_h - 1), radius=34, fill=255)
            bar_im.alpha_composite(Image.composite(stripe_layer, Image.new("RGBA", (cur_w, bar_h), (0, 0, 0, 0)), mask_im))
            ImageDraw.Draw(bar_im).rounded_rectangle((0, 0, cur_w - 1, bar_h - 1), radius=34, outline=INK + (244,), width=8)
            overlay2.alpha_composite(bar_im, (bx0, yy))

        disp_v = _interpolate_stat_numbers(val_s.upper(), ease)
        inside_bar = cur_w > 480
        v_col = (255, 255, 255) if inside_bar else INK
        v_im = text_layer(disp_v, 154 if inside_bar else 148, v_col, font_role="hero")
        v_draw = _text_with_offset_shadow(v_im, dx=5, dy=6, shadow_col=(0, 0, 0, 95)) if inside_bar else _text_with_offset_shadow(v_im, dx=4, dy=5)
        vx = (bx0 + cur_w - v_draw.width - 36) if cur_w > (v_draw.width + 86) else (bx0 + cur_w + 34)
        overlay2.alpha_composite(v_draw, (vx, yy + (bar_h - v_draw.height) // 2))
        bar_meta.append((bx0 + cur_w, yy, vx + v_draw.width))

    # Giant "66× HIGHER" hand-drawn badge + slow curved ink arrow pointing from Bar A to Bar B
    ratio = round(max(na, nb) / max(0.1, min(na, nb)))
    if ratio >= 2 and dt >= 1.55:
        p_arr = min(1.0, max(0.0, (dt - 1.55) / 0.50))
        e_arr = 1.0 - (1.0 - p_arr) ** 4
        p_badge = min(1.0, max(0.0, (dt - 1.90) / 0.40))
        e_badge = 1.0 - (1.0 - p_badge) ** 4

        # Curved ink arrow sweeping from right of 1.4% bar directly into Bar B surge area
        ax0 = min(int(bx0 + max_bar_w * 0.42), bar_meta[0][2] + 36) if bar_meta else int(bx0 + max_bar_w * 0.34)
        ay0 = y_a + bar_h // 2 + 12
        ax1 = int(bx0 + max_bar_w * 0.76)
        ay1 = y_b - 28
        ctrl_x = int(bx0 + max_bar_w * 0.72)
        ctrl_y = y_a + int(bar_h * 0.45)
        _draw_curved_ink_arrow(d2, ax0, ay0, ax1, ay1, ACCENT + (int(242 * min(1.0, e_arr * 1.4)),),
                               width=16 if is_shorts else 18, ctrl_pt=(ctrl_x, ctrl_y), draw_progress=e_arr)

        if e_badge > 0.02:
            # Tilted bold "66× HIGHER" editorial callout badge in right upper open space beside Row A
            b_lbl = f"{ratio}× HIGHER"
            b_txt = text_layer(b_lbl, 94 if is_shorts else 104, (255, 255, 255), font_role="hero")
            bw_r, bh_r = b_txt.width + 82, b_txt.height + 44
            badge2 = Image.new("RGBA", (bw_r + 24, bh_r + 24), (0, 0, 0, 0))
            bd2 = ImageDraw.Draw(badge2)
            bd2.rounded_rectangle((14, 16, 14 + bw_r, 16 + bh_r), radius=30, fill=(0, 0, 0, int(72 * e_badge)))
            bd2.rounded_rectangle((6, 6, 6 + bw_r, 6 + bh_r), radius=30, fill=ACCENT + (int(250 * e_badge),), outline=INK + (int(245 * e_badge),), width=8)
            badge2.alpha_composite(_apply_alpha_to_image(b_txt, e_badge), (6 + 41, 6 + 22))
            sc_b = 0.84 + 0.16 * e_badge
            if sc_b < 0.999:
                badge2 = badge2.resize((max(1, int(badge2.width * sc_b)), max(1, int(badge2.height * sc_b))), Image.BILINEAR)
            badge2 = badge2.rotate(2.4, resample=Image.BILINEAR, expand=True)
            bcx_f = bx0 + int(max_bar_w * 0.72)
            bcy_f = y_a + int(bar_h * 0.22)
            overlay2.alpha_composite(badge2, (bcx_f - badge2.width // 2, bcy_f - badge2.height // 2))

    fr = card_bg(w, h, variant="blueprint").convert("RGBA")
    fr.alpha_composite(overlay2.resize((w, h), Image.LANCZOS))
    p_drift = min(1.0, max(0.0, dt / max(0.5, duration)))
    drift_scale = 1.00 + 0.025 * (0.55 * (1.0 - (1.0 - p_drift) ** 3) + 0.45 * p_drift)
    dw, dh = int(w * drift_scale), int(h * drift_scale)
    return fr.resize((dw, dh), Image.BILINEAR).crop(((dw - w) // 2, (dh - h) // 2, (dw - w) // 2 + w, (dh - h) // 2 + h))


def draw_micro_accent(fr, W, H, dt, kind="burst", cx_norm=0.5, cy_norm=0.35, is_shorts=False):
    """Lightweight comic editorial micro-accents (!, ?, curve_ticks, motion_ticks, burst, strike_x) synced to beats."""
    if dt < 0.0 or dt > 1.05:
        return
    p = min(1.0, dt / 0.22)
    ease = 1.0 - (1.0 - p) ** 3
    fade = min(1.0, max(0.0, (1.05 - dt) / 0.28))
    alpha = ease * fade
    if alpha <= 0.05:
        return
    cx, cy = int(W * cx_norm), int(H * cy_norm)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if kind in ("!", "?"):
        im = text_layer(kind, 96 if is_shorts else 108, ACCENT if kind == "!" else INK, font_role="hero")
        layer.alpha_composite(_apply_alpha_to_image(im, alpha), (cx - im.width // 2, cy - im.height // 2 - int(18 * ease)))
    elif kind in ("motion_ticks", "curve_ticks", "curved_ticks"):
        for ang_d in (-32, 0, 32):
            ang = math.radians(ang_d)
            r0, r1 = int(42 + 22 * ease), int(84 + 26 * ease)
            mid_ang = ang + 0.14
            r_mid = int((r0 + r1) * 0.5)
            d.line([
                (cx + int(r0 * math.cos(ang)), cy + int(r0 * math.sin(ang))),
                (cx + int(r_mid * math.cos(mid_ang)), cy + int(r_mid * math.sin(mid_ang))),
                (cx + int(r1 * math.cos(ang + 0.08)), cy + int(r1 * math.sin(ang + 0.08))),
            ], fill=INK + (int(220 * alpha),), width=6, joint="curve")
    elif kind == "strike_x":
        r = 68 if is_shorts else 76
        p1 = min(1.0, dt / 0.16)
        p2 = min(1.0, max(0.0, (dt - 0.12) / 0.16))
        if p1 > 0:
            d.line((cx - r, cy - r, int(cx - r + 2 * r * p1), int(cy - r + 2 * r * p1)), fill=(214, 46, 38, int(242 * fade)), width=14)
        if p2 > 0:
            d.line((cx + r, cy - r, int(cx + r - 2 * r * p2), int(cy - r + 2 * r * p2)), fill=(214, 46, 38, int(242 * fade)), width=14)
    else:
        for i in range(6):
            ang = i * (math.pi / 3.0) + 0.2
            r0, r1 = int(34 + 18 * ease), int(72 + 24 * ease)
            d.line((cx + int(r0 * math.cos(ang)), cy + int(r0 * math.sin(ang)),
                    cx + int(r1 * math.cos(ang)), cy + int(r1 * math.sin(ang))), fill=ACCENT + (int(225 * alpha),), width=6)
    fr.alpha_composite(layer)


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
    # Lower safe zone for 9:16 Shorts (Y: 81%–88%, 1590px in 1920p, safely clear of bottom graphics)
    sub_y_short = int(spatial_policy.get("subtitles_center_y_shorts", int(h * 0.83)))
    sub_y_short = max(int(h * 0.81), min(int(h * 0.88), sub_y_short))
    sub_y_long = int(spatial_policy.get("subtitles_center_y_long", h - 150))
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
    ap.add_argument("--outro-sec", type=float, default=None, help="Duration of standalone music-only outro (default: 8.0 for 16:9, 0.0 for 9:16)")
    args = ap.parse_args()
    if args.format == "9:16":
        args.outro_sec = 0.0  # Strict mandate: NEVER attach 16:9 end-screen cards to 9:16 Shorts!
    elif args.outro_sec is None:
        args.outro_sec = 8.0

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
    story_dur = max(0.1, total - args.outro_sec) if args.outro_sec > 0 else total

    for i in range(len(scenes)):
        scenes[i]["t1"] = scenes[i + 1]["t0"] if i + 1 < len(scenes) else story_dur

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
                    match_sc["_annotations"] = d_sc.get("annotations", [])
                    match_sc["_era_anchor"] = d_sc.get("era_anchor", "")
                    filtered_ovs = []
                    for o_i, ov in enumerate(match_sc["ov"]):
                        d_ov = None
                        for cand_do in d_sc.get("overlays", []):
                            if cand_do.get("idx") == o_i or os.path.basename(cand_do.get("img", "")) == os.path.basename(ov["img"]):
                                d_ov = cand_do
                                break
                        if d_ov:
                            d_stat = str(d_ov.get("status", ""))
                            if d_stat.startswith("REJECTED_"):
                                print(f"🎬 [Director Supervisor] Skipped sticker '{ov['img']}' ({d_stat}) in scene {match_sc['cue']}: {d_ov.get('reason','')}")
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

    def draw_youtube_outro_slate(fr, W, H, dt, standalone=False):
        """Renders broadcast YouTube End Screen Slate with textured dark charcoal CC0 matte & subscribe bubble."""
        if standalone:
            bg_outro = card_bg(W, H, variant="outro_dark").convert("RGBA")
            fr.paste(bg_outro, (0, 0))
            d = ImageDraw.Draw(fr)
            _draw_editorial_corner_ticks(d, 80, 80, W - 80, H - 80, (65, 80, 105, 180), arm=44, width=4)
        else:
            d = ImageDraw.Draw(fr)
            slate_dark = Image.new("RGBA", (W, H), (14, 18, 26, 235))
            fr.alpha_composite(slate_dark)

        # Header
        is_vert = (W < H)
        header_im = text_layer("THANKS FOR WATCHING", 54 if is_vert else 52, (255, 230, 80))
        fr.alpha_composite(header_im, ((W - header_im.width) // 2, 185 if is_vert else 85))

        sub_im = text_layer("WATCH NEXT & SUBSCRIBE", 30, (220, 230, 245))
        fr.alpha_composite(sub_im, ((W - sub_im.width) // 2, 260 if is_vert else 155))

        p_card = min(1.0, dt / 0.5)
        q_card = spring_p(p_card)
        card_alpha = int(min(1.0, dt / 0.3) * 255)

        if is_vert:
            box_w, box_h = 680, 320
            cx_card = (W - box_w) // 2
            top_y, bot_y = 385, 1025
            # Top Card: Watch Next
            d.rounded_rectangle((cx_card + 6, top_y + 6, cx_card + box_w + 6, top_y + box_h + 6), radius=24, fill=(0, 0, 0, 105))
            d.rounded_rectangle((cx_card, top_y, cx_card + box_w, top_y + box_h), radius=24, fill=(28, 34, 46, 242), outline=(255, 215, 30, card_alpha), width=4)
            lbl_left = text_layer("▶ WATCH NEXT", 38, (255, 215, 30))
            fr.alpha_composite(lbl_left, (cx_card + (box_w - lbl_left.width) // 2, top_y + (box_h - lbl_left.height) // 2))

            # Center Subscribe Circle cleanly between cards
            cx_sub, cy_sub = W // 2, 865
            r_sub = max(12, int(92 * q_card))
            d.ellipse((cx_sub - r_sub + 4, cy_sub - r_sub + 4, cx_sub + r_sub + 4, cy_sub + r_sub + 4), fill=(0, 0, 0, 85))
            d.ellipse((cx_sub - r_sub, cy_sub - r_sub, cx_sub + r_sub, cy_sub + r_sub), fill=(235, 45, 45, 245), outline=(255, 255, 255, 255), width=4)
            sub_txt = text_layer("SUB", 34, (255, 255, 255))
            fr.alpha_composite(sub_txt, (cx_sub - sub_txt.width // 2, cy_sub - sub_txt.height // 2))

            # Bottom Card: Best For You
            d.rounded_rectangle((cx_card + 6, bot_y + 6, cx_card + box_w + 6, bot_y + box_h + 6), radius=24, fill=(0, 0, 0, 105))
            d.rounded_rectangle((cx_card, bot_y, cx_card + box_w, bot_y + box_h), radius=24, fill=(28, 34, 46, 242), outline=(75, 225, 255, card_alpha), width=4)
            lbl_right = text_layer("★ BEST FOR YOU", 38, (75, 225, 255))
            fr.alpha_composite(lbl_right, (cx_card + (box_w - lbl_right.width) // 2, bot_y + (box_h - lbl_right.height) // 2))

            bot_im = text_layer("TAP THE CARDS TO CONTINUE THE STORY", 26, (180, 195, 215))
            fr.alpha_composite(bot_im, ((W - bot_im.width) // 2, 1450))
            return

        box_w, box_h = 610, 344
        box_y = 250
        left_x = 120
        right_x = W - box_w - 120

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
        """Draws floating sleek modern dark/amber editorial subscribe badge in lower safe area during Shorts closing."""
        p = min(1.0, dt / 0.35)
        ease = 1.0 - (1.0 - p) ** 3
        dy = int(24 * (1.0 - ease))
        alpha = min(1.0, ease * 1.3)
        pulse = 1.0 + 0.02 * math.sin(dt * 6.0)
        pill_w = int(580 * pulse)
        pill_h = 76
        pill_x = (W - pill_w) // 2
        pill_y = 1380 + dy
        badge_im = Image.new("RGBA", (pill_w + 16, pill_h + 16), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge_im)
        bd.rounded_rectangle((8 + 3, 8 + 5, 8 + pill_w + 3, 8 + pill_h + 5), radius=22, fill=(0, 0, 0, int(75 * alpha)))
        bd.rounded_rectangle((8, 8, 8 + pill_w, 8 + pill_h), radius=22, fill=(24, 28, 38, int(245 * alpha)),
                             outline=ACCENT + (int(235 * alpha),), width=3)
        fr.alpha_composite(badge_im, (pill_x - 8, pill_y - 8))
        txt = text_layer("SUBSCRIBE • FULL VIDEO ON CHANNEL", 30, (250, 248, 240))
        if txt:
            fr.alpha_composite(txt, ((W - txt.width) // 2, pill_y + (pill_h - txt.height) // 2))

    # Runtime Compositing Counter & Telemetry
    rendered_stickers_counter = [0]
    rendered_unique_stickers = set()
    rendered_stickers_telemetry = []
    overlay_anchor_cache = {}
    scene_layout_cache = {}
    scene_end_cache = {}
    fact_badges = _extract_editorial_fact_badges(words_list)

    def _smooth_shot_motion(src_im, out_w, out_h, t_flags, u_prog, cam_move=""):
        """Single unified, strictly monotonic ease-out camera curve (zero bounce or scale reversal)."""
        p = max(0.0, min(1.0, float(u_prog)))
        ease = 0.55 * (1.0 - (1.0 - p) ** 3) + 0.45 * p
        mv = (cam_move or "").strip().lower()
        if not mv:
            for tok_m in ("pan_left", "pan_right", "zoom_in_tight", "crop_focus", "pull_back", "push_in", "static"):
                if tok_m in t_flags:
                    mv = "zoom_in_tight" if tok_m == "crop_focus" else tok_m
                    break
        has_punch = ("zoom_punch" in t_flags)
        if mv == "static":
            scale = 1.00 + 0.025 * ease
            dx_frac = 0.010 * (ease - 0.5)
            dy_frac = 0.0
        elif mv == "pan_left":
            scale = 1.12
            dx_frac = 0.42 - 0.84 * ease
            dy_frac = 0.0
        elif mv == "pan_right":
            scale = 1.12
            dx_frac = -0.42 + 0.84 * ease
            dy_frac = 0.0
        elif mv == "zoom_in_tight":
            scale = 1.03 + 0.12 * ease
            dx_frac = 0.0
            dy_frac = -0.04 * ease
        elif mv == "pull_back":
            scale = 1.075 - 0.075 * ease
            dx_frac = 0.025 * (0.5 - ease)
            dy_frac = -0.015 * ease
        elif mv == "push_in":
            # Forward cubic punch-in cleanly folds into monotonic push without scale reversal
            scale = 1.00 + (0.085 if has_punch else 0.070) * ease
            dx_frac = 0.025 * (ease - 0.5)
            dy_frac = -0.020 * ease
        else:
            scale = 1.00 + (0.085 if has_punch else 0.070) * ease
            dx_frac = 0.025 * (ease - 0.5)
            dy_frac = -0.018 * ease

        cw = max(1, int(src_im.width / scale))
        ch = max(1, int(src_im.height / scale))
        avail_x = max(0, src_im.width - cw)
        avail_y = max(0, src_im.height - ch)
        cx = max(0, min(avail_x, int(avail_x * (0.5 + dx_frac))))
        cy = max(0, min(avail_y, int(avail_y * (0.5 + dy_frac))))
        return src_im.crop((cx, cy, cx + cw, cy + ch)).resize((out_w, out_h), Image.LANCZOS)

    def _render_base_scene_at(si_idx, t_eval, count_telemetry=True):
        sc_x = scenes[si_idx]
        t0_x = sc_x["t0"]
        t1_x = sc_x["t1"]
        dt_x = max(0.0, t_eval - t0_x)
        dur_x = max(0.1, t1_x - t0_x)
        u_x = min(1.0, dt_x / dur_x)
        img_x = sc_x["img"]
        txt_x = sc_x["text"]
        t_flags_x = f"{sc_x.get('extra', '')} {sc_x.get('pos', '')} {sc_x.get('space', '')}".strip().lower()

        tok = os.path.basename(img_x)
        tok_b = os.path.splitext(tok)[0]
        tok_k = tok_b.split(":")[0].strip()

        is_stat_c = (tok in ("card", "card_stat", "card_phrase") or tok_b in ("card", "card_stat", "card_phrase") or tok_k in ("card", "card_stat", "card_phrase") or tok.startswith("card_"))
        is_split_c = (tok in ("split_compare", "split_contrast") or tok_b in ("split_compare", "split_contrast") or tok_k in ("split_compare", "split_contrast") or tok.startswith("split_"))
        is_time_c = (tok in ("bar_timeline", "timeline") or tok_b in ("bar_timeline", "timeline") or tok_k in ("bar_timeline", "timeline") or tok.startswith(("timeline_", "bar_")))
        is_pie_c = (tok in ("stat_pie", "stat_ring") or tok_b in ("stat_pie", "stat_ring") or tok_k in ("stat_pie", "stat_ring") or tok.startswith("stat_"))
        is_breath_c = (tok in ("chapter_breather", "breather") or tok_b in ("chapter_breather", "breather") or tok_k in ("chapter_breather", "breather") or tok.startswith("chapter_"))
        is_scale_c = (tok in ("scale_compare", "scale_bar") or tok_b in ("scale_compare", "scale_bar") or tok_k in ("scale_compare", "scale_bar") or tok.startswith("scale_"))
        is_strike_c = (tok in ("card_strike_replace", "strike_replace") or tok_b in ("card_strike_replace", "strike_replace") or tok_k in ("card_strike_replace", "strike_replace") or tok.startswith("strike_"))
        is_nat_arch = (is_stat_c or is_split_c or is_time_c or is_pie_c or is_breath_c or is_scale_c or is_strike_c)

        paired_stk = left_stk = right_stk = left_stmp = right_stmp = None
        nat_consumed = set()
        if is_nat_arch:
            for idx, o in enumerate(sc_x.get("ov", [])):
                o_img = o.get("img", "").strip()
                o_pos = str(o.get("pos", "")).lower()
                if o_img in ("stamp_x", "stamp_false", "stamp_myth"):
                    if "left" in o_pos or not left_stmp:
                        left_stmp = o_img
                    else:
                        right_stmp = o_img
                    nat_consumed.add(idx)
                    if count_telemetry:
                        rendered_stickers_counter[0] += 1
                        rendered_unique_stickers.add(o_img)
                elif o_img in ("stamp_check", "stamp_true"):
                    if "right" in o_pos or not right_stmp:
                        right_stmp = o_img
                    else:
                        left_stmp = o_img
                    nat_consumed.add(idx)
                    if count_telemetry:
                        rendered_stickers_counter[0] += 1
                        rendered_unique_stickers.add(o_img)
                elif o_img not in ("tag", "count") and not o_img.startswith("bars:"):
                    res_path = resolve_sticker_path(o_img)
                    if res_path:
                        if is_split_c:
                            if "left" in o_pos and not left_stk:
                                left_stk = res_path
                            elif "right" in o_pos and not right_stk:
                                right_stk = res_path
                            elif not left_stk:
                                left_stk = res_path
                            elif not right_stk:
                                right_stk = res_path
                            else:
                                continue
                        elif not paired_stk:
                            paired_stk = res_path
                        else:
                            continue
                        nat_consumed.add(idx)
                        if count_telemetry:
                            rendered_stickers_counter[0] += 1
                            rendered_unique_stickers.add(o_img)
            if not paired_stk and sc_x.get("space"):
                res_sp = resolve_sticker_path(sc_x["space"])
                if res_sp:
                    paired_stk = res_sp

        # Draw 100% full-bleed base artwork FIRST, then overlay seamless frosted checklist if active in scene
        if is_strike_c:
            fr_out = draw_strike_replace_card(W, H, txt_x, is_shorts=is_shorts, dt=dt_x, duration=dur_x)
        elif tok in ("card", "card_stat", "card_phrase") or tok_b in ("card", "card_stat", "card_phrase") or tok_k in ("card", "card_stat", "card_phrase") or tok.startswith("card_") or tok_b.startswith("card_") or tok_k.startswith("card_"):
            fr_out = draw_card_stat(W, H, txt_x, is_shorts=is_shorts, dt=dt_x, sticker_im=paired_stk)
        elif tok in ("split_compare", "split_contrast") or tok_b in ("split_compare", "split_contrast") or tok_k in ("split_compare", "split_contrast") or tok.startswith("split_") or tok_b.startswith("split_") or tok_k.startswith("split_"):
            fr_out = draw_split_compare(W, H, txt_x, is_shorts=is_shorts, dt=dt_x, left_sticker=left_stk, right_sticker=right_stk, left_stamp=left_stmp, right_stamp=right_stmp, duration=dur_x)
        elif tok in ("bar_timeline", "timeline") or tok_b in ("bar_timeline", "timeline") or tok_k in ("bar_timeline", "timeline") or tok.startswith(("timeline_", "bar_")) or tok_b.startswith(("timeline_", "bar_")) or tok_k.startswith(("timeline_", "bar_")):
            fr_out = draw_data_timeline(W, H, txt_x, is_shorts=is_shorts, dt=dt_x, accent_sticker=paired_stk, duration=dur_x)
        elif tok in ("stat_pie", "stat_ring") or tok_b in ("stat_pie", "stat_ring") or tok_k in ("stat_pie", "stat_ring") or tok.startswith("stat_") or tok_b.startswith("stat_") or tok_k.startswith("stat_"):
            fr_out = draw_stat_pie(W, H, txt_x, is_shorts=is_shorts, dt=dt_x, accent_sticker=paired_stk)
        elif is_breath_c:
            fr_out = draw_chapter_breather(W, H, txt_x, is_shorts=is_shorts, dt=dt_x, duration=dur_x)
        elif is_scale_c:
            fr_out = draw_scale_compare(W, H, txt_x, is_shorts=is_shorts, dt=dt_x, duration=dur_x)
        elif img_x not in img_cache:
            fr_out = draw_card_stat(W, H, txt_x, is_shorts=is_shorts, dt=dt_x, sticker_im=paired_stk)
        else:
            raw = img_cache[img_x]
            is_vert = (raw.height >= raw.width * 1.15)
            is_land = (raw.width >= raw.height * 1.15)
            cam_m = sc_x.get("_camera_move", "")
            if is_shorts:
                if is_vert:
                    fr_out = _smooth_shot_motion(raw, W, H, t_flags_x, u_x, cam_m)
                elif raw.width == 1 and raw.height == 1:
                    fr_out = card_bg(W, H).convert("RGBA")
                else:
                    cached_bg = bg_cache.get(img_x)
                    fr_out = cached_bg.copy() if cached_bg else card_bg(W, H).convert("RGBA")
                    stage_img = raw.resize((stage_w, stage_h), Image.LANCZOS)
                    stage_img.putalpha(stage_mask)
                    stage_card = stage_card_base.copy()
                    stage_card.alpha_composite(stage_img, (12, 12))
                    fr_out.alpha_composite(stage_card, ((W - stage_w - 24) // 2, 750))
            else:
                if is_land or not is_vert:
                    fr_out = _smooth_shot_motion(raw, W, H, t_flags_x, u_x, cam_m)
                else:
                    cached_bg = bg_cache.get(img_x)
                    fr_out = cached_bg.copy() if cached_bg else card_bg(W, H).convert("RGBA")
                    pillar_h = H - 80
                    pillar_w = int(pillar_h * (raw.width / raw.height))
                    pillar_img = raw.resize((pillar_w, pillar_h), Image.LANCZOS)
                    fr_out.alpha_composite(pillar_img, ((W - pillar_w) // 2, 40))

        if fr_out.mode != "RGBA":
            fr_out = fr_out.convert("RGBA")
        chk_ann = next((a for a in sc_x.get("_annotations", []) if a.get("kind") == "checklist_build" and float(a.get("t0", t0_x)) <= t_eval <= float(a.get("t1", t1_x))), None)
        if chk_ann:
            draw_checklist_build(
                fr_out, W, H, max(0.0, t_eval - float(chk_ann.get("t0", t0_x))),
                items=chk_ann.get("items", []), item_times=chk_ann.get("item_times"),
                t_abs=t_eval, is_shorts=is_shorts, side=chk_ann.get("side", "auto"),
                layout_cache=scene_layout_cache, cache_key=f"chk_{si_idx}",
                title=chk_ann.get("title", "")
            )
            return fr_out, is_nat_arch, is_breath_c, is_strike_c, is_scale_c, nat_consumed, t_flags_x, True
        return fr_out, is_nat_arch, is_breath_c, is_strike_c, is_scale_c, nat_consumed, t_flags_x, False

    def compose_frame_at(t):
        if args.outro_sec > 0 and t >= story_dur:
            dt_outro = t - story_dur
            fr = Image.new("RGBA", (W, H), (16, 20, 28, 255))
            draw_youtube_outro_slate(fr, W, H, dt_outro, standalone=True)
            return fr

        si = 0
        while si + 1 < len(scenes) and t >= scenes[si + 1]["t0"]:
            si += 1
        sc = scenes[si]
        t0 = sc["t0"]
        t1 = sc["t1"]
        dt = max(0.0, t - t0)
        dt_scene = dt
        img_path = sc["img"]
        text = sc["text"]
        pos = sc["pos"]
        extra = sc["extra"]

        fr, is_native_archetype, is_breather_card, is_strike_card, is_scale_card, natively_consumed_indices, trans_type, checklist_base_rendered = _render_base_scene_at(si, t, count_telemetry=True)
        is_archetype_card = (is_native_archetype or img_path == "card")
        raw_cur = img_cache.get(img_path)
        is_vertical_img = (raw_cur.height >= raw_cur.width * 1.15) if raw_cur is not None else is_shorts
        is_landscape_img = (raw_cur.width >= raw_cur.height * 1.15) if raw_cur is not None else (not is_shorts)

        # Capture clean frame for stable sticker spatial anchoring
        clean_base_fr = fr.copy()

        # Dynamic Camera Shake (only on explicit earthquake/impact shake cues; NEVER backward zoom bounce!)
        shake_dx, shake_dy = 0, 0
        if "shake" in trans_type and dt_scene < 0.40:
            intensity = ((1.0 - dt_scene / 0.40) ** 1.8) * (24.0 if is_shorts else 28.0)
            shake_dx += int(np.sin(dt_scene * 65.0) * intensity)
            shake_dy += int(np.cos(dt_scene * 75.0) * intensity)
        elif "rumble" in trans_type:
            shake_dx += int(np.sin(t * 30.0) * 4.5)
            shake_dy += int(np.cos(t * 35.0) * 4.5)

        for impact_t in impact_hit_times:
            dt_imp = t - impact_t
            if 0.0 <= dt_imp <= 0.28:
                intensity = ((1.0 - dt_imp / 0.28) ** 1.8) * 16.0
                shake_dx += int(np.sin(dt_imp * 65.0) * intensity)
                shake_dy += int(np.cos(dt_imp * 75.0) * intensity)
                break
        if shake_dx != 0 or shake_dy != 0:
            fr = fr.transform(fr.size, Image.AFFINE, (1, 0, shake_dx, 0, 1, shake_dy))

        # Helper to retrieve outgoing scene's exact end frame for silky slide-push / cross-dissolve
        def _get_prev_end_frame():
            if si <= 0:
                return None
            if (si - 1) not in scene_end_cache:
                prev_t = max(scenes[si - 1]["t0"], scenes[si - 1]["t1"] - 0.02)
                pfr, *_ = _render_base_scene_at(si - 1, prev_t, count_telemetry=False)
                scene_end_cache[si - 1] = pfr
            return scene_end_cache[si - 1]

        prev_was_card = False
        if si > 0:
            pb = os.path.splitext(os.path.basename(scenes[si - 1]["img"]))[0].split(":")[0]
            prev_was_card = (scenes[si - 1]["img"] == "card" or pb.startswith(("card", "split", "bar_", "timeline", "stat_", "chapter_", "breather", "scale_", "strike_")))

        # Silky Cinema Transitions (~70% crisp beat cuts, ~30% smooth zoom_dissolve / slide_push / paper_crossfade)
        wants_slide = ("slide_push" in trans_type or "slide_wipe" in trans_type)
        wants_paper_cf = ("paper_crossfade" in trans_type or "fade" in trans_type or ((is_archetype_card != prev_was_card) and "cut" not in trans_type and not wants_slide))
        wants_zoom_dis = ("zoom_dissolve" in trans_type or ("crossfade" in trans_type and not wants_paper_cf and not wants_slide))

        if wants_slide and dt_scene < 0.34 and si > 0:
            prev_fr = _get_prev_end_frame()
            if prev_fr is not None:
                p_slide = min(1.0, max(0.0, dt_scene / 0.34))
                ease_s = (4.0 * (p_slide ** 3)) if p_slide < 0.5 else (1.0 - ((-2.0 * p_slide + 2.0) ** 3) / 2.0)
                in_x = int(round((1.0 - ease_s) * W))
                out_x = -int(round(ease_s * W * 0.45))
                out_fr = prev_fr
                if 0.15 < p_slide < 0.85:
                    blur_px = 3.5 * math.sin(math.pi * p_slide)
                    out_fr = prev_fr.resize((max(1, W // 2), max(1, H // 2)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur_px)).resize((W, H), Image.BILINEAR)
                comp_slide = Image.new("RGBA", (W, H), (244, 238, 224, 255))
                comp_slide.paste(out_fr, (out_x, 0))
                # Soft feathered 36px edge shadow instead of harsh black line
                sh_strip = Image.new("RGBA", (36, H), (0, 0, 0, 0))
                sd = ImageDraw.Draw(sh_strip)
                for sx in range(36):
                    a_sh = int(52 * ((sx / 35.0) ** 1.7))
                    sd.line((sx, 0, sx, H), fill=(18, 16, 14, a_sh), width=1)
                comp_slide.alpha_composite(sh_strip, (max(-36, in_x - 36), 0))
                comp_slide.paste(fr, (in_x, 0))
                fr = comp_slide
        elif wants_zoom_dis and dt_scene < 0.32 and si > 0:
            prev_fr = _get_prev_end_frame()
            if prev_fr is not None:
                p_zd = min(1.0, max(0.0, dt_scene / 0.32))
                ease_zd = (4.0 * (p_zd ** 3)) if p_zd < 0.5 else (1.0 - ((-2.0 * p_zd + 2.0) ** 3) / 2.0)
                # Outgoing gently pushes forward (1.00 -> 1.05); incoming glides smoothly in from (0.96 -> 1.00)
                s_out = 1.00 + 0.05 * ease_zd
                ow, oh = int(W * s_out), int(H * s_out)
                p_scaled = prev_fr.resize((ow, oh), Image.BILINEAR).crop(((ow - W) // 2, (oh - H) // 2, (ow - W) // 2 + W, (oh - H) // 2 + H))
                s_in = 0.96 + 0.04 * ease_zd
                iw, ih = int(W * s_in), int(H * s_in)
                if iw < W:
                    in_canvas = fr.copy()
                    in_inner = fr.resize((iw, ih), Image.BILINEAR)
                    in_canvas.paste(in_inner, ((W - iw) // 2, (H - ih) // 2))
                else:
                    in_canvas = fr
                fr = Image.blend(p_scaled, in_canvas, ease_zd)
        elif wants_paper_cf and dt_scene < 0.28 and si > 0:
            prev_fr = _get_prev_end_frame()
            if prev_fr is not None:
                p_cf = min(1.0, max(0.0, dt_scene / 0.28))
                ease_cf = (4.0 * (p_cf ** 3)) if p_cf < 0.5 else (1.0 - ((-2.0 * p_cf + 2.0) ** 3) / 2.0)
                fr = Image.blend(prev_fr, fr, ease_cf)
                warm_bridge = int(28 * math.sin(math.pi * ease_cf))
                if warm_bridge > 2:
                    fr.alpha_composite(Image.new("RGBA", (W, H), PAPER + (warm_bridge,)))
        elif "flash" in trans_type and dt_scene < 0.14 and si > 0:
            flash_p = max(0.0, 1.0 - dt_scene / 0.14)
            fr.alpha_composite(Image.new("RGBA", (W, H), (255, 252, 240, int(flash_p * 160))))

        # Subtle living 11fps paper grain boil + warm drifting sunlight dust motes on bright editorial shots
        if not checklist_base_rendered:
            fr = _apply_animated_vfx_layer(fr, "paper_grain_cycle", t_abs=t, opacity=0.14)
            if not is_archetype_card and img_path != "card":
                fr = _apply_animated_vfx_layer(fr, "dust_motes_drift", t_abs=t, opacity=0.20)

        # Label Deduplication & Clash Check:
        # Scene heading text label: Suppressed on standard scenes so stickers, art, and captions remain uncluttered.
        # Only displayed on dedicated full-screen title/chapter cards (img_path == "card") or if explicitly requested.
        active_tags = {o["text"].strip().upper() for o in sc["ov"] if o.get("text")}
        token = os.path.basename(img_path)
        token_base = os.path.splitext(token)[0]
        token_key = token_base.split(":")[0].strip()
        is_archetype_card = (token in ("card", "card_stat", "card_phrase", "split_compare", "split_contrast",
                                       "bar_timeline", "timeline", "stat_pie", "stat_ring", "scale_compare",
                                       "card_strike_replace", "strike_replace", "chapter_breather", "breather") or
                             token_base in ("card", "card_stat", "card_phrase", "split_compare", "split_contrast",
                                            "bar_timeline", "timeline", "stat_pie", "stat_ring", "scale_compare",
                                            "card_strike_replace", "strike_replace", "chapter_breather", "breather") or
                             token_key in ("card", "card_stat", "card_phrase", "split_compare", "split_contrast",
                                           "bar_timeline", "timeline", "stat_pie", "stat_ring", "scale_compare",
                                           "card_strike_replace", "strike_replace", "chapter_breather", "breather") or
                             token.startswith(("card_", "split_", "timeline_", "stat_", "bar_", "scale_", "strike_", "chapter_", "breather")) or
                             token_base.startswith(("card_", "split_", "timeline_", "stat_", "bar_", "scale_", "strike_", "chapter_", "breather")) or
                             token_key.startswith(("card_", "split_", "timeline_", "stat_", "bar_", "scale_", "strike_", "chapter_", "breather")))
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
        seen_stk_names = set()
        for o_idx, o in enumerate(sc["ov"]):
            if o_idx in natively_consumed_indices:
                continue
            stk_name = os.path.basename(o["img"].strip()).lower()
            if stk_name and stk_name not in ("tag", "count") and not stk_name.startswith("bars:"):
                if stk_name in seen_stk_names:
                    continue
                seen_stk_names.add(stk_name)
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
        seen_sched_stks = set()
        for idx_s, os_ov in enumerate(sc["ov"]):
            if idx_s in natively_consumed_indices:
                continue
            stk_name_s = os.path.basename(os_ov["img"].strip()).lower()
            if stk_name_s and stk_name_s not in ("tag", "count") and not stk_name_s.startswith("bars:"):
                if stk_name_s in seen_sched_stks:
                    continue
                seen_sched_stks.add(stk_name_s)
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

            p_ent = min(1.0, dt / 0.42)
            ease_c = 1.0 - (1.0 - p_ent) ** 4
            p = p_ent
            q = spring_p(p_ent)
            alpha = min(1.0, dt / 0.22)

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
                item_im = sticker(o_img, hh, t_sec=dt)
                if o.get("text"):
                    lbl_im = tag_image(o["text"], 34 if is_shorts else 40)
            else:
                resolved_p = resolve_sticker_path(o_img)
                if resolved_p:
                    item_im = sticker(resolved_p, hh, t_sec=dt)
                    if o.get("text"):
                        lbl_im = tag_image(o["text"], 34 if is_shorts else 40)

            if item_im is None:
                continue

            # Multi-Slot Collision-Free Anchor Solver (Locked Anchor Cache: zero jitter/teleporting)
            sub_top_y = (1180 - 60) if is_shorts else (H - 150 - 50)
            ov_cache_key = f"{si}_{o_idx}_{o.get('t', 0.0)}"
            base_ref = clean_base_fr if 'clean_base_fr' in locals() and clean_base_fr is not None else fr
            if ov_cache_key not in overlay_anchor_cache:
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

            # Ultra-gentle 0.55 Hz float + +-1.8 deg pendulum tilt + 11fps organic hand-drawn breath
            idle_dy, idle_ang = 0.0, 0.0
            boil_dx, boil_dy = 0.0, 0.0
            if dt > 0.42 and exit_e <= 0.01:
                ramp_idle = min(1.0, (dt - 0.42) / 0.30)
                idle_dy = 4.2 * ramp_idle * math.sin(2.0 * math.pi * 0.55 * (dt - 0.42) + o_idx * 1.1)
                idle_ang = 1.8 * ramp_idle * math.sin(2.0 * math.pi * 0.42 * (dt - 0.42) + o_idx * 0.7)
                boil_tick = int(t * 11.0)
                boil_dx = 0.8 * math.sin(boil_tick * 2.3 + o_idx)
                boil_dy = 0.8 * math.cos(boil_tick * 1.7 + o_idx)

            # Smooth ease-out exit scale + directional retract
            if exit_e > 0.0:
                scale_x_mult *= (1.0 - 0.08 * exit_e)
                scale_y_mult *= (1.0 - 0.08 * exit_e)
                dy_anim += int(16 * (exit_e ** 2))

            nw = max(1, int(item_im.width * auto_q * scale_x_mult))
            nh = max(1, int(item_im.height * auto_q * scale_y_mult))
            scaled_im = item_im.resize((nw, nh), Image.BILINEAR)

            # Subtle diagonal specular sheen sweep on metallic / glass / focal props (~0.55s after spawn)
            if 0.48 <= dt <= 1.25 and any(kw in o_img.lower() for kw in ("coin", "mug", "soda", "coffee", "sugar", "clock", "skull", "gold", "bronze", "thermometer", "bulb")):
                sheen_u = (dt - 0.48) / 0.77
                if 0.0 < sheen_u < 1.0:
                    sh_lay = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
                    sh_d = ImageDraw.Draw(sh_lay)
                    sx_c = int(-nw * 0.3 + (nw * 1.6) * sheen_u)
                    bw_s = max(16, nw // 7)
                    sh_d.polygon([(sx_c, 0), (sx_c + bw_s, 0), (sx_c - bw_s, nh), (sx_c - bw_s * 2, nh)], fill=(255, 255, 255, 62))
                    a_mask = scaled_im.getchannel("A")
                    sh_clipped = Image.composite(sh_lay, Image.new("RGBA", (nw, nh), (0, 0, 0, 0)), a_mask)
                    scaled_im.alpha_composite(sh_clipped)

            slot_tilts = (-2.2, 1.9, -1.6, 2.3, -1.8)
            base_tilt = o.get("_rest_tilt_deg", slot_tilts[o_idx % len(slot_tilts)]) if img_path != "card" else 0.0
            total_tilt = base_tilt + entry_ang + idle_ang
            if abs(total_tilt) > 0.08 and nw > 24 and nh > 24:
                scaled_im = scaled_im.rotate(total_tilt, resample=Image.BICUBIC, expand=True)
                nw, nh = scaled_im.size

            cx = int(round(target_cx + dx_anim + boil_dx))
            cy = int(round(target_cy + dy_anim + idle_dy + boil_dy))

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
                clutter = compute_negative_space_score(base_ref, cx - nw // 2, cy - nh // 2, cx + nw // 2, cy + nh // 2)
                if clutter >= 22.0:
                    callout_pad = 32 if is_shorts else 26
                    c_dim = max(nw, nh) + callout_pad * 2
                    callout_im = Image.new("RGBA", (c_dim + 16, c_dim + 16), (0, 0, 0, 0))
                    cd = ImageDraw.Draw(callout_im)
                    cd.ellipse((8 + 4, 8 + 6, 8 + c_dim + 4, 8 + c_dim + 6), fill=(0, 0, 0, int(52 * max(0.0, min(1.0, alpha)))))
                    cd.ellipse((8, 8, 8 + c_dim, 8 + c_dim), fill=PAPER + (int(248 * max(0.0, min(1.0, alpha))),),
                               outline=INK + (int(220 * max(0.0, min(1.0, alpha))),), width=3)
                    cd.ellipse((14, 14, 8 + c_dim - 6, 8 + c_dim - 6), outline=ACCENT + (int(120 * max(0.0, min(1.0, alpha))),), width=1)
                    fr.alpha_composite(callout_im, (cx - callout_im.width // 2, cy - callout_im.height // 2))
                else:
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

            # Rule: Crisp animated sparkle ticks / pop lines on sticker entrance
            if dt <= 0.22:
                spark_p = dt / 0.22
                spark_alpha = int(220 * (1.0 - spark_p))
                if spark_alpha > 10:
                    spark_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    sd = ImageDraw.Draw(spark_layer)
                    rad_dist = int(12 + 24 * spark_p)
                    tick_len = int(10 * (1.0 - spark_p * 0.5))
                    corners = [
                        (cx - nw // 2 - rad_dist, cy - nh // 2 - rad_dist, -1, -1),
                        (cx + nw // 2 + rad_dist, cy - nh // 2 - rad_dist, 1, -1),
                        (cx - nw // 2 - rad_dist, cy + nh // 2 + rad_dist, -1, 1),
                        (cx + nw // 2 + rad_dist, cy + nh // 2 + rad_dist, 1, 1),
                    ]
                    for x0, y0, dx, dy in corners:
                        sd.line([(x0, y0), (x0 + dx * tick_len, y0 + dy * tick_len)], fill=(245, 180, 50, spark_alpha), width=3)
                    fr.alpha_composite(spark_layer)

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

        # Procedural Live Ink Annotation & Visual Storytelling Primitives (synced to DIRECTOR_PLAN.json / WORDS.tsv)
        active_anns = sc.get("_annotations", [])
        # First pass: spotlight_dim so focus subjects & annotations pop above the dimmed surroundings
        for ann in active_anns:
            if ann.get("kind") == "spotlight_dim":
                a_t0 = float(ann.get("t0", t0))
                a_t1 = float(ann.get("t1", t1))
                if a_t0 <= t <= a_t1:
                    draw_spotlight_dim(
                        fr, W, H, t - a_t0, duration=max(0.4, a_t1 - a_t0),
                        cx_norm=float(ann.get("cx", 0.5)), cy_norm=float(ann.get("cy", 0.45)),
                        rx_norm=float(ann.get("rx", 0.24)), ry_norm=float(ann.get("ry", 0.22))
                    )
        # Second pass: circle_focus, strike_replace, checklist_build, inset_shelf, pip_flashback, micro_accent
        for ann in active_anns:
            akind = ann.get("kind", "")
            if akind == "spotlight_dim":
                continue
            a_t0 = float(ann.get("t0", t0))
            a_t1 = float(ann.get("t1", t1))
            if not (a_t0 <= t <= a_t1):
                continue
            dt_a = t - a_t0
            dur_a = max(0.3, a_t1 - a_t0)
            cx_a = float(ann.get("cx", 0.5))
            cy_a = float(ann.get("cy", 0.45))
            targ_resolved = None  # (sx, sy, sw, sh, exit_e)
            targ_idx = ann.get("target_ov_idx")
            if targ_idx is not None:
                try:
                    t_i = int(targ_idx)
                    if t_i in scene_drawn_stickers:
                        sx_a, sy_a, im_a, _, exit_a = scene_drawn_stickers[t_i]
                        cx_a, cy_a = sx_a / max(1, W), sy_a / max(1, H)
                        targ_resolved = (sx_a, sy_a, im_a.width, im_a.height, exit_a)
                except Exception:
                    pass
            elif ann.get("target_sticker") and scene_drawn_stickers:
                targ_slug = str(ann.get("target_sticker", "")).lower()
                for idx_s, ov_s in enumerate(sc.get("ov", [])):
                    if idx_s in scene_drawn_stickers and targ_slug in str(ov_s.get("img", "")).lower():
                        sx_a, sy_a, im_a, _, exit_a = scene_drawn_stickers[idx_s]
                        cx_a, cy_a = sx_a / max(1, W), sy_a / max(1, H)
                        targ_resolved = (sx_a, sy_a, im_a.width, im_a.height, exit_a)
                        break

            if akind == "circle_focus":
                # Disabled for stickers/floating props; ONLY allowed on verified geographic map targets
                if ann.get("verified_map_target"):
                    draw_circle_focus(
                        fr, W, H, dt_a,
                        cx_norm=cx_a, cy_norm=cy_a,
                        rx_norm=float(ann.get("rx", 0.14)), ry_norm=float(ann.get("ry", 0.11))
                    )
            elif akind == "strike_x":
                if targ_resolved is not None and targ_resolved[4] < 0.96:
                    draw_strike_replace(
                        fr, W, H, dt_a, old_text="", new_text="", cx_norm=cx_a, cy_norm=cy_a,
                        is_shorts=is_shorts, mode="strike_x", exit_alpha=(1.0 - targ_resolved[4])
                    )
            elif akind == "strike_replace":
                draw_strike_replace(
                    fr, W, H, dt_a,
                    old_text=ann.get("old_text", ""), new_text=ann.get("new_text", ""),
                    cx_norm=cx_a, cy_norm=cy_a,
                    is_shorts=is_shorts, mode="replace",
                    placement=ann.get("placement", "below")
                )
            elif akind == "checklist_build":
                if not checklist_base_rendered:
                    draw_checklist_build(
                        fr, W, H, dt_a,
                        items=ann.get("items", []), item_times=ann.get("item_times"),
                        t_abs=t, is_shorts=is_shorts, side=ann.get("side", "left"),
                        layout_cache=scene_layout_cache, cache_key=f"chk_{si}",
                        title=ann.get("title", ""), raw_scene_im=img_cache.get(img_path)
                    )
            elif akind == "inset_shelf":
                draw_inset_shelf(
                    fr, W, H, dt_a,
                    items=ann.get("items", []), item_times=ann.get("item_times"),
                    t_abs=t, is_shorts=is_shorts, resolve_fn=resolve_sticker_path,
                    layout_cache=scene_layout_cache, cache_key=f"shelf_{si}", scene_end_t=t1
                )
            elif akind in ("pip_inset", "pip_flashback"):
                pip_tok = str(ann.get("src_img", "")).strip()
                pip_im = img_cache.get(pip_tok)
                if pip_im is None and pip_tok:
                    for cp in (pip_tok, os.path.join("shots", pip_tok), os.path.join("shots", f"{pip_tok}.png"), os.path.join("..", pip_tok)):
                        if os.path.exists(cp):
                            try:
                                pip_im = Image.open(cp).convert("RGBA")
                                img_cache[pip_tok] = pip_im
                            except Exception:
                                pass
                            break
                if pip_im is None and scenes:
                    pip_im = img_cache.get(scenes[0]["img"])
                draw_pip_inset(fr, W, H, dt_a, dur_a, pip_im, label=ann.get("label", "CALLBACK" if akind == "pip_flashback" else "EVIDENCE"), is_shorts=is_shorts)
            elif akind == "micro_accent":
                # Never stamp !/? over illustrated character scenes; only allow on clean card/abstract backdrops
                if is_archetype_card or img_path == "card":
                    draw_micro_accent(
                        fr, W, H, dt_a, kind=ann.get("symbol", "burst"),
                        cx_norm=cx_a, cy_norm=cy_a,
                        is_shorts=is_shorts
                    )

        # Persistent Top-Left Era / Date Anchor
        era_lbl = sc.get("_era_anchor", "")
        if not era_lbl and "era_anchor:" in extra:
            era_lbl = extra.split("era_anchor:", 1)[1].split(",")[0].strip()
        if era_lbl and not is_breather_card:
            draw_era_anchor(fr, W, H, dt_scene, era_lbl, is_shorts=is_shorts)

        # Shorts Header & Progress Bar (14px with dark track & precise 0%->100% clamping)
        if is_shorts:
            d = ImageDraw.Draw(fr)
            prog_ratio = min(1.0, max(0.0, t / max(0.1, total)))
            prog_w = int(W * prog_ratio)
            d.rectangle((0, 0, W, 14), fill=(20, 24, 32, 160))
            d.rectangle((0, 0, prog_w, 14), fill=(240, 145, 45, 255))
            # Display title banner ONLY if explicitly requested via --header
            if args.header and t <= 2.5:
                header_txt = text_layer(title_text, 34, INK)
                hp_w, hp_h = header_txt.width + 36, header_txt.height + 12
                hp_x = (W - hp_w) // 2
                d.rounded_rectangle((hp_x, 190, hp_x + hp_w, 190 + hp_h), radius=16, fill=PAPER + (240,), outline=INK, width=3)
                fr.alpha_composite(header_txt, ((W - header_txt.width) // 2, 196))

        # On-Shot Kinetic Fact / Date Badges (e.g. 14,000 YEARS AGO synced to spoken words)
        if img_path != "card" and not is_archetype_card and fact_badges:
            for b_t0, b_t1, b_text in fact_badges:
                if b_t0 <= t <= b_t1:
                    draw_kinetic_editorial_badge(fr, W, H, b_text, t - b_t0, duration=(b_t1 - b_t0), is_shorts=is_shorts)
                    break

        # Kinetic Subtitles
        if args.subtitles:
            render_subtitles(fr, words_list, t, W, H, is_shorts)

        # Professional Outro Slate for 16:9 Long-Form (explicit outro scene only; standalone handled at start of compose_frame_at)
        if not is_shorts and img_path == "outro":
            dt_outro = t - t0
            draw_youtube_outro_slate(fr, W, H, dt_outro, standalone=True)

        # Shorts Ending Follow Callout: ONLY on final CTA scene (never mid-story & never over archetype/data cards!)
        is_clip_preview = bool(args.clip_seconds and args.clip_seconds < (audio_dur - 2.0))
        is_final_scene = (si == len(scenes) - 1)
        scene_words_txt = " ".join(w.get("word", "").lower() for w in words_list if t0 <= w.get("start", 0.0) <= t1)
        has_cta_cue = ("cta" in trans_type or any(k in scene_words_txt for k in ("subscribe", "full video", "channel", "watch the")))
        if is_shorts and not args.clip_seconds and not is_clip_preview and is_final_scene and not is_archetype_card and has_cta_cue:
            draw_shorts_subscribe_callout(fr, W, H, max(0.0, t - t0))

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
                          if ov.get("t", 0.0) <= total and ov.get("img") not in ("tag", "count") and not ov.get("img", "").startswith("bars:")]
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
