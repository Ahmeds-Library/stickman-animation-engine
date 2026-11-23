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
import argparse, csv, os, shutil, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# Autonomous Zero-Setup Bootstrapper
try:
    import auto_bootstrap
    auto_bootstrap.ensure_environment()
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
FONTS = os.path.join(SKILL_ROOT, "fonts")
if not os.path.exists(FONTS):
    FONTS = "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/fonts"
FONT_PATH = os.path.join(FONTS, "PatrickHand-Regular.ttf")
FONT_CX_PATH = os.path.join(FONTS, "Kalam-Bold.ttf")

LOOKS = {
    "warm": ((252, 244, 222), (58, 34, 18), (236, 190, 105), (196, 132, 58)),
    "bright": ((255, 253, 246), (28, 32, 44), (252, 249, 238), (196, 222, 240)),
}
PAPER, INK, CARD_IN, CARD_OUT = LOOKS["warm"]
CARD_INK = INK

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
    """Damped harmonic spring: bouncy overshoot (0 -> 1.08 -> 1.00)."""
    p = max(0.0, min(1.0, p))
    return 1.0 - np.exp(-7.0 * p) * np.cos(9.0 * p)


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

    # Eye-level position: 1180 in Shorts (safe above Instagram/Shorts bottom 672px UI and within 300-1248 safe zone)
    pos_x = (w - bw) // 2
    pos_y = 1180 if is_shorts else (h - 150)

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
    ap.add_argument("--look", default="warm")
    ap.add_argument("--kenburns", action="store_true", default=False, help="Enable subtle Ken Burns drift (default: disabled to preserve 100% uncropped full image)")
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

    # Pre-cache scene images
    img_cache = {}
    bg_cache = {}
    for s in scenes:
        p = s["img"]
        if p != "card" and os.path.exists(p) and p not in img_cache:
            im = Image.open(p).convert("RGBA")
            img_cache[p] = im
            if is_shorts:
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
        dur = max(0.1, t1 - t0)
        u = min(1.0, dt / dur)

        img_path = sc["img"]
        text = sc["text"]
        pos = sc["pos"]
        extra = sc["extra"]

        # Background composition
        if img_path == "card" or img_path not in img_cache:
            fr = card_bg(W, H).convert("RGBA")
        else:
            raw = img_cache[img_path]

            is_vertical_img = (raw.height >= raw.width * 1.15)
            is_landscape_img = (raw.width >= raw.height * 1.15)

            if is_shorts:
                if is_vertical_img:
                    # Native 9:16 Vertical Art from Flow (e.g. 1536x2752):
                    # Zero cropping! Flow provides high-quality 9:16 compositions; use the full image directly.
                    if args.kenburns:
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
                    # Zero cropping! Use the complete full image directly.
                    if args.kenburns:
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
        trans_type = str(sc.get("extra", "")).strip().lower()

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
        if text and (img_path == "card" or args.scene_labels):
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
            dt = t - o["t"]
            if dt >= 0:
                # Rule 29: Dynamic Sticker Lifetime & Clean Exit
                # Standard duration: 1.8s in Shorts, 2.2s in Long, or custom dur:X.X
                default_dur = 1.8 if is_shorts else 2.2
                custom_dur = None
                for part in str(o.get("extra", "")).split("|"):
                    if part.startswith("dur:"):
                        try:
                            custom_dur = float(part[4:])
                        except Exception:
                            pass
                dur = custom_dur if custom_dur is not None else default_dur
                if dt <= dur:
                    active_overlays.append((o_idx, o, dt, dur))

        occupied_boxes = []

        for o_idx, o, dt, dur in active_overlays:
            p = min(1.0, dt / 0.35)
            q = spring_p(p)
            alpha = min(1.0, dt / 0.18)

            # Clean exit animation during final 0.28s of sticker lifetime
            time_left = dur - dt
            exit_p = 1.0
            if time_left < 0.28:
                exit_p = max(0.0, time_left / 0.28)
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
            elif os.path.exists(o_img):
                item_im = sticker(o_img, hh)
                if o.get("text"):
                    lbl_im = tag_image(o["text"], 34 if is_shorts else 40)

            if item_im is None:
                continue

            nw = max(1, int(item_im.width * q))
            nh = max(1, int(item_im.height * q))
            scaled_im = item_im.resize((nw, nh), Image.BILINEAR)

            cx = int(fx * W)
            cy = int(fy * H)

            # Dynamic sticker motion VFX (drop, slide, organic hover breathing)
            ov_extra = str(o.get("extra", "")).strip().lower()
            if "drop" in ov_extra or "slam" in ov_extra:
                cy -= int(220 * (1.0 - p)**2)
            elif "slide_left" in ov_extra:
                cx -= int(220 * (1.0 - p)**2)
            elif "slide_right" in ov_extra:
                cx += int(220 * (1.0 - p)**2)
            
            if p >= 1.0 and time_left >= 0.28:
                hover_dy = int(np.sin((dt - 0.38) * 2.2 + o_idx * 1.5) * 5)
                cy += hover_dy
            elif time_left < 0.28:
                cy -= int((1.0 - exit_p) * 16)

            # Screen bounds clamping (guarantee 100% visibility, never clipped)
            # In Shorts (9:16): Right 220px is UI action buttons (Like, Comment, Share) on IG/Shorts
            right_margin = 220 if is_shorts else 54
            min_x = nw // 2 + (48 if is_shorts else 54)
            max_x = W - nw // 2 - right_margin
            cx = max(min_x, min(cx, max_x))

            min_y = nh // 2 + (200 if is_shorts else 80)
            max_y = (980 if is_shorts else 820) - nh // 2
            cy = max(min_y, min(cy, max_y))

            # Multi-Overlay Collision Avoidance
            for bx0, by0, bx1, by1 in occupied_boxes:
                if not (cx + nw // 2 < bx0 - 20 or cx - nw // 2 > bx1 + 20 or
                        cy + nh // 2 < by0 - 20 or cy - nh // 2 > by1 + 20):
                    if by1 + nh + 30 <= max_y:
                        cy = by1 + nh // 2 + 30
                    else:
                        cx = min(max_x, bx1 + nw // 2 + 30)

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
           "-r", str(FPS), "-i", "-", "-i", args.audio, "-c:v", "libx264", "-preset", "fast",
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
    print(f"✅ Finished: {out_file} ({os.path.getsize(out_file)/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
