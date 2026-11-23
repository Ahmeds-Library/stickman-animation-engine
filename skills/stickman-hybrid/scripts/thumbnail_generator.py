#!/usr/bin/env python3
"""thumbnail_generator.py: High-CTR Viral YouTube Thumbnail Generator
Generates broadcast-quality, high-clickthrough-rate thumbnails for YouTube 16:9 and Shorts 9:16:
1. 3-Element Rule: High-Emotion Character + Visual Mystery Anomaly + Ultra-Bold Curiosity Text.
2. Dynamic Color Contrasts: Warm Amber (#FFE600) / Neon Cyan (#00F0FF) / Crimson Danger (#FF3B30).
3. Heavy 12px Outlines & Deep Drop Shadows for instant readability on mobile feeds.
4. Dynamic -4° Velocity Tilt on Text.
5. Dual Format Export: 1280x720 (YouTube Landscape) and 1080x1920 (Shorts Cover).
"""

import os, sys, math, argparse, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(SKILL_ROOT, "fonts")
if not os.path.exists(FONTS_DIR):
    FONTS_DIR = "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/fonts"

LUCKIEST_FONT = os.path.join(FONTS_DIR, "LuckiestGuy-Regular.ttf")
MONTSERRAT_FONT = os.path.join(FONTS_DIR, "Montserrat-Black.ttf")
KALAM_FONT = os.path.join(FONTS_DIR, "Kalam-Bold.ttf")

def get_best_font(size):
    for fpath in [LUCKIEST_FONT, MONTSERRAT_FONT, KALAM_FONT]:
        if os.path.exists(fpath):
            try:
                return ImageFont.truetype(fpath, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_tilted_text(canvas, text, cx, cy, font, fill_color, stroke_color, stroke_w=12, angle=-4.0):
    """Renders bold text with heavy outline and drop shadow at a dynamic velocity angle."""
    # Measure text bounding box
    dummy_im = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy_im)
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = bbox[2] - bbox[0] + stroke_w * 4 + 40
    th = bbox[3] - bbox[1] + stroke_w * 4 + 40

    txt_im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt_im)
    
    # Draw drop shadow (+8px, +8px)
    td.text((tw // 2 + 8, th // 2 + 8), text, font=font, fill=(10, 14, 24, 220),
            anchor="mm", stroke_width=stroke_w + 4, stroke_fill=(10, 14, 24, 220))
    # Draw heavy outline & main fill
    td.text((tw // 2, th // 2), text, font=font, fill=fill_color,
            anchor="mm", stroke_width=stroke_w, stroke_fill=stroke_color)

    # Rotate
    rotated = txt_im.rotate(angle, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(rotated, (cx - rotated.width // 2, cy - rotated.height // 2))

def create_thumbnail(project_dir=".", text=None, tag="SECRET REVEALED", out_16x9="thumbnail_16x9.png", out_9x16="thumbnail_9x16.png"):
    slug = os.path.basename(os.path.abspath(project_dir))
    
    # Find background shot
    candidates = []
    for d in [project_dir, os.path.join(project_dir, "long"), os.path.join(project_dir, "short")]:
        shots_dir = os.path.join(d, "shots")
        if os.path.exists(shots_dir):
            candidates.extend(sorted(glob.glob(os.path.join(shots_dir, "*.png"))))
            candidates.extend(sorted(glob.glob(os.path.join(shots_dir, "*.jpg"))))
    
    bg_path = candidates[0] if candidates else None

    # Find transparent sticker prop
    prop_candidates = []
    for d in [project_dir, os.path.join(project_dir, "long"), os.path.join(project_dir, "short")]:
        cut_dir = os.path.join(d, "elements", "cut")
        if os.path.exists(cut_dir):
            prop_candidates.extend(sorted(glob.glob(os.path.join(cut_dir, "*.png"))))
    
    prop_path = prop_candidates[0] if prop_candidates else None

    # Determine Title Text
    if not text:
        slug_clean = slug.replace("_", " ").lower()
        if "cold" in slug_clean or "ice" in slug_clean:
            text = "IMPOSSIBLE ICE?"
            tag = "400 BC SECRET"
        elif "waking" in slug_clean or "alarm" in slug_clean:
            text = "NEVER SLEEP IN?"
            tag = "ANCIENT TRICK"
        elif "clothes" in slug_clean:
            text = "WHY WE WEAR THIS"
            tag = "100,000 YEARS AGO"
        else:
            text = slug.replace("_", " ").upper()
            tag = "HOW IT WORKED"

    # --- 1. RENDER 16:9 LANDSCAPE THUMBNAIL (1280x720) ---
    W16, H16 = 1280, 720
    im16 = Image.new("RGBA", (W16, H16), (20, 24, 32, 255))

    if bg_path and os.path.exists(bg_path):
        raw_bg = Image.open(bg_path).convert("RGBA")
        # Cover resize
        scale = max(W16 / raw_bg.width, H16 / raw_bg.height)
        scaled_w, scaled_h = int(raw_bg.width * scale), int(raw_bg.height * scale)
        bg_fitted = raw_bg.resize((scaled_w, scaled_h), Image.LANCZOS)
        crop_x = (scaled_w - W16) // 2
        crop_y = (scaled_h - H16) // 2
        bg_cropped = bg_fitted.crop((crop_x, crop_y, crop_x + W16, crop_y + H16))
        im16.alpha_composite(bg_cropped)

    # Cinematic Dramatic Vignette (Dark edges to maximize CTR text pop)
    vignette = Image.new("RGBA", (W16, H16), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(120):
        alpha = int((120 - i) / 120 * 190)
        vd.rectangle((i, i, W16 - i, H16 - i), outline=(12, 16, 24, alpha), width=1)
    im16.alpha_composite(vignette)

    # Overlay Hero Prop (Enlarged on right side with outer glow)
    if prop_path and os.path.exists(prop_path):
        hero_prop = Image.open(prop_path).convert("RGBA")
        target_h = int(H16 * 0.62)
        prop_scale = target_h / hero_prop.height
        target_w = int(hero_prop.width * prop_scale)
        hero_prop = hero_prop.resize((target_w, target_h), Image.LANCZOS)

        # Glow layer
        glow = hero_prop.copy()
        r, g, b, a = glow.split()
        glow_col = Image.new("RGBA", glow.size, (255, 230, 80, 255))
        glow_col.putalpha(a)
        glow_blurred = glow_col.filter(ImageFilter.GaussianBlur(18))

        px = int(W16 * 0.72 - target_w // 2)
        py = int(H16 * 0.52 - target_h // 2)
        im16.alpha_composite(glow_blurred, (px, py))
        im16.alpha_composite(hero_prop, (px, py))

    # Top Pill Stamp (e.g. [ 400 BC SECRET ])
    if tag:
        tag_font = get_best_font(36)
        d_im = ImageDraw.Draw(im16)
        tb = d_im.textbbox((0, 0), tag.upper(), font=tag_font)
        pw, ph = tb[2] - tb[0] + 44, tb[3] - tb[1] + 20
        px, py = 80, 70
        d_im.rounded_rectangle((px, py, px + pw, py + ph), radius=14, fill=(255, 59, 48, 245), outline=(255, 255, 255, 255), width=3)
        d_im.text((px + pw // 2, py + ph // 2 - 2), tag.upper(), font=tag_font, fill=(255, 255, 255, 255), anchor="mm")

    # Main Viral Curiosity Text (Large, Golden-Yellow #FFE600 with black border)
    title_font_16 = get_best_font(104)
    # Support two lines if text contains | or is long
    lines = text.split("|") if "|" in text else [text]
    if len(lines) == 1 and len(text) > 14:
        words = text.split()
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    text_y = 220 if len(lines) == 1 else 190
    for l_idx, line in enumerate(lines):
        draw_tilted_text(
            im16, line.upper(),
            cx=420, cy=text_y + l_idx * 115,
            font=title_font_16,
            fill_color=(255, 230, 0, 255),  # High-CTR Golden Yellow
            stroke_color=(16, 20, 30, 255), # Deep Charcoal Ink Outline
            stroke_w=14, angle=-3.5
        )

    im16.convert("RGB").save(out_16x9, quality=95)
    print(f"✅ Generated 16:9 YouTube Thumbnail: {out_16x9} (1280x720)")

    # --- 2. RENDER 9:16 VERTICAL SHORTS COVER (1080x1920) ---
    W9, H9 = 1080, 1920
    im9 = Image.new("RGBA", (W9, H9), (20, 24, 32, 255))

    if bg_path and os.path.exists(bg_path):
        raw_bg = Image.open(bg_path).convert("RGBA")
        scale = max(W9 / raw_bg.width, H9 / raw_bg.height)
        scaled_w, scaled_h = int(raw_bg.width * scale), int(raw_bg.height * scale)
        bg_fitted = raw_bg.resize((scaled_w, scaled_h), Image.LANCZOS)
        crop_x = (scaled_w - W9) // 2
        crop_y = (scaled_h - H9) // 2
        im9.alpha_composite(bg_fitted.crop((crop_x, crop_y, crop_x + W9, crop_y + H9)))

    # Shorts Vignette
    vignette9 = Image.new("RGBA", (W9, H9), (0, 0, 0, 0))
    vd9 = ImageDraw.Draw(vignette9)
    for i in range(160):
        alpha = int((160 - i) / 160 * 210)
        vd9.rectangle((i, i, W9 - i, H9 - i), outline=(12, 16, 24, alpha), width=1)
    im9.alpha_composite(vignette9)

    # Prop centered in middle
    if prop_path and os.path.exists(prop_path):
        hero_prop = Image.open(prop_path).convert("RGBA")
        target_h = int(H9 * 0.38)
        prop_scale = target_h / hero_prop.height
        target_w = int(hero_prop.width * prop_scale)
        hero_prop = hero_prop.resize((target_w, target_h), Image.LANCZOS)
        
        glow = hero_prop.copy()
        r, g, b, a = glow.split()
        glow_col = Image.new("RGBA", glow.size, (255, 230, 80, 255))
        glow_col.putalpha(a)
        glow_blurred = glow_col.filter(ImageFilter.GaussianBlur(24))

        px = (W9 - target_w) // 2
        py = int(H9 * 0.44 - target_h // 2)
        im9.alpha_composite(glow_blurred, (px, py))
        im9.alpha_composite(hero_prop, (px, py))

    # Top Tag Pill in Shorts
    if tag:
        tag_font9 = get_best_font(44)
        d_im9 = ImageDraw.Draw(im9)
        tb = d_im9.textbbox((0, 0), tag.upper(), font=tag_font9)
        pw, ph = tb[2] - tb[0] + 56, tb[3] - tb[1] + 24
        px, py = (W9 - pw) // 2, 280
        d_im9.rounded_rectangle((px, py, px + pw, py + ph), radius=18, fill=(255, 59, 48, 245), outline=(255, 255, 255, 255), width=4)
        d_im9.text((px + pw // 2, py + ph // 2 - 2), tag.upper(), font=tag_font9, fill=(255, 255, 255, 255), anchor="mm")

    # Main Text in Shorts
    title_font_9 = get_best_font(116)
    text_y = 440
    for l_idx, line in enumerate(lines):
        draw_tilted_text(
            im9, line.upper(),
            cx=W9 // 2, cy=text_y + l_idx * 135,
            font=title_font_9,
            fill_color=(255, 230, 0, 255),
            stroke_color=(16, 20, 30, 255),
            stroke_w=16, angle=-3.0
        )

    im9.convert("RGB").save(out_9x16, quality=95)
    print(f"✅ Generated 9:16 Shorts Cover: {out_9x16} (1080x1920)")
    return True

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dir", nargs="?", default=".")
    p.add_argument("--text", default=None, help="Bold thumbnail text (2-4 words)")
    p.add_argument("--tag", default=None, help="Top badge tag (e.g. 400 BC SECRET)")
    p.add_argument("--out-16x9", default="thumbnail_16x9.png")
    p.add_argument("--out-9x16", default="thumbnail_9x16.png")
    args = p.parse_args()
    create_thumbnail(args.dir, text=args.text, tag=args.tag, out_16x9=args.out_16x9, out_9x16=args.out_9x16)
