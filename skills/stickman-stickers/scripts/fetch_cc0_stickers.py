#!/usr/bin/env python3
"""fetch_cc0_stickers.py: Fetches genuine 100% CC0 / Public Domain 2D props (Wikimedia CC0 API when online) and builds normalized 2D CC0 editorial & category stickers."""

import os
import sys
import json
import math
import urllib.request
import urllib.parse
import argparse
from io import BytesIO
from PIL import Image, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
import index_stickers

CC0_ROOT = index_stickers.CC0_LIB_DIR
ALLOWED_LICENSES = {"cc0", "cc0 1.0", "public domain", "pd", "cc-zero"}


def _normalize_to_512_rgba(im):
    """Crops transparent margins tightly and centers on a clean 512x512 RGBA canvas with safe breathing margin."""
    im = im.convert("RGBA")
    bbox = im.getbbox()
    if not bbox:
        return None
    crop = im.crop(bbox)
    cw, ch = crop.size
    if cw < 16 or ch < 16:
        return None
    target = 420
    scale = min(target / cw, target / ch)
    nw, nh = max(16, int(round(cw * scale))), max(16, int(round(ch * scale)))
    resized = crop.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((512 - nw) // 2, (512 - nh) // 2))
    return canvas


def try_fetch_wikimedia_cc0(query, category, filename_slug, max_results=3):
    """Fetches a PNG thumbnail strictly if LicenseShortName verifies CC0 / Public Domain."""
    try:
        api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query",
            "generator": "search",
            "gsrsearch": f"{query} filetype:bitmap|drawing",
            "gsrnamespace": "6",
            "gsrlimit": str(max_results),
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": "512",
            "format": "json",
        })
        req = urllib.request.Request(api, headers={"User-Agent": "StickmanStickers/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = (data.get("query") or {}).get("pages") or {}
        for _, pg in pages.items():
            infos = pg.get("imageinfo") or []
            if not infos:
                continue
            ii = infos[0]
            lic = ((ii.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value", "").strip().lower()
            if not any(tok in lic for tok in ALLOWED_LICENSES):
                continue
            thumb = ii.get("thumburl") or ii.get("url")
            if not thumb:
                continue
            img_req = urllib.request.Request(thumb, headers={"User-Agent": "StickmanStickers/1.0"})
            with urllib.request.urlopen(img_req, timeout=8) as ir:
                im = Image.open(BytesIO(ir.read()))
                norm = _normalize_to_512_rgba(im)
                if norm:
                    out_dir = os.path.join(CC0_ROOT, category)
                    os.makedirs(out_dir, exist_ok=True)
                    out_p = os.path.join(out_dir, f"{filename_slug}.png")
                    norm.save(out_p)
                    ok, _, _ = index_stickers.inspect_png_alpha(out_p)
                    if ok:
                        return out_p
                    os.remove(out_p)
    except Exception:
        pass
    return None


def _draw_2x(draw_fn, category, slug, tags):
    """Draws a crisp 2D cartoon prop at 1024x1024 and downsamples to 512x512 LANCZOS RGBA."""
    im2 = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(im2)
    draw_fn(im2, d2)
    out_dir = os.path.join(CC0_ROOT, category)
    os.makedirs(out_dir, exist_ok=True)
    out_p = os.path.join(out_dir, f"{slug}.png")
    im2.resize((512, 512), Image.LANCZOS).save(out_p)
    meta_p = os.path.join(out_dir, f"{slug}.meta.json")
    with open(meta_p, "w", encoding="utf-8") as mf:
        json.dump({"tags": tags, "category": category, "source": "cc0_library", "license": "CC0-1.0"}, mf, indent=2)
    return out_p


INK = (24, 26, 34, 255)


def build_cc0_cartoon_library():
    """Creates normalized 100% CC0-1.0 2D cartoon props & editorial accents across all 6 categories."""
    created = []

    # 1. editorial_accents
    def _red_x(_, d):
        d.ellipse((140, 140, 884, 884), fill=(252, 232, 230, 255), outline=(212, 48, 38, 255), width=36)
        d.line((320, 320, 704, 704), fill=(212, 48, 38, 255), width=68)
        d.line((704, 320, 320, 704), fill=(212, 48, 38, 255), width=68)

    def _green_chk(_, d):
        d.ellipse((140, 140, 884, 884), fill=(228, 248, 235, 255), outline=(32, 160, 82, 255), width=36)
        d.line((290, 520, 440, 680), fill=(32, 160, 82, 255), width=68)
        d.line((440, 680, 740, 350), fill=(32, 160, 82, 255), width=68)

    def _arrow_red(_, d):
        d.line((150, 700, 770, 310), fill=(214, 52, 40, 255), width=48)
        d.polygon([(850, 260), (670, 275), (755, 420)], fill=(214, 52, 40, 255))

    def _star_burst(_, d):
        pts = []
        for i in range(16):
            ang = i * math.pi / 8
            r = 390 if i % 2 == 0 else 210
            pts.append((512 + int(r * math.cos(ang)), 512 + int(r * math.sin(ang))))
        d.polygon(pts, fill=(252, 198, 60, 255), outline=INK, width=22)

    def _warning_tri(_, d):
        d.polygon([(512, 150), (880, 820), (144, 820)], fill=(250, 192, 48, 255), outline=INK, width=28)
        d.line((512, 360, 512, 595), fill=INK, width=44)
        d.ellipse((482, 665, 542, 725), fill=INK)

    def _speech_bubble(_, d):
        d.rounded_rectangle((130, 190, 894, 690), radius=90, fill=(252, 249, 240, 255), outline=INK, width=26)
        d.polygon([(310, 685), (430, 685), (240, 850)], fill=(252, 249, 240, 255), outline=INK, width=22)
        d.ellipse((320, 415, 375, 470), fill=INK)
        d.ellipse((485, 415, 540, 470), fill=INK)
        d.ellipse((650, 415, 705, 470), fill=INK)

    created.extend([
        _draw_2x(_red_x, "editorial_accents", "cc0_red_cross_x", "cross x myth false wrong reject stamp"),
        _draw_2x(_green_chk, "editorial_accents", "cc0_green_check", "check checkmark verified fact true"),
        _draw_2x(_arrow_red, "editorial_accents", "cc0_red_arrow", "arrow pointer direction highlight red"),
        _draw_2x(_star_burst, "editorial_accents", "cc0_star_burst", "star burst impact spark accent highlight"),
        _draw_2x(_warning_tri, "editorial_accents", "cc0_warning_triangle", "warning alert danger hazard caution"),
        _draw_2x(_speech_bubble, "editorial_accents", "cc0_speech_bubble", "speech bubble quote talk dialogue"),
    ])

    # 2. history_ancient
    def _scroll(_, d):
        d.rounded_rectangle((220, 190, 804, 834), radius=45, fill=(238, 214, 168, 255), outline=INK, width=24)
        d.rounded_rectangle((170, 170, 854, 275), radius=48, fill=(220, 188, 132, 255), outline=INK, width=24)
        d.rounded_rectangle((170, 749, 854, 854), radius=48, fill=(220, 188, 132, 255), outline=INK, width=24)
        for yy in (370, 460, 550, 640):
            d.line((320, yy, 704, yy), fill=(110, 82, 52, 255), width=20)

    def _shield(_, d):
        d.polygon([(200, 200), (824, 200), (790, 570), (512, 870), (234, 570)], fill=(198, 62, 52, 255), outline=INK, width=28)
        d.polygon([(275, 275), (749, 275), (722, 540), (512, 775), (302, 540)], fill=(234, 178, 64, 255), outline=INK, width=18)
        d.ellipse((430, 405, 594, 569), fill=(242, 232, 208, 255), outline=INK, width=18)

    def _crown(_, d):
        d.polygon([(170, 740), (170, 320), (350, 520), (512, 230), (674, 520), (854, 320), (854, 740)],
                  fill=(242, 188, 48, 255), outline=INK, width=26)
        d.rectangle((170, 660, 854, 760), fill=(214, 152, 34, 255), outline=INK, width=24)
        d.ellipse((475, 480, 549, 554), fill=(208, 52, 46, 255), outline=INK, width=14)

    created.extend([
        _draw_2x(_scroll, "history_ancient", "cc0_ancient_scroll", "scroll parchment manuscript archive history record"),
        _draw_2x(_shield, "history_ancient", "cc0_warrior_shield", "shield armor roman warrior defense battle"),
        _draw_2x(_crown, "history_ancient", "cc0_royal_crown", "crown king empire ruler kingdom gold"),
    ])

    # 3. science_space
    def _atom(_, d):
        for ang in (0, 60, -60):
            # rotated ellipse approximation via polygon
            pts = []
            rad = math.radians(ang)
            for i in range(48):
                th = 2 * math.pi * i / 48
                ex = 350 * math.cos(th)
                ey = 140 * math.sin(th)
                rx = 512 + ex * math.cos(rad) - ey * math.sin(rad)
                ry = 512 + ex * math.sin(rad) + ey * math.cos(rad)
                pts.append((rx, ry))
            d.line(pts + [pts[0]], fill=(58, 138, 212, 255), width=22)
        d.ellipse((442, 442, 582, 582), fill=(224, 68, 56, 255), outline=INK, width=20)

    def _planet(_, d):
        d.ellipse((240, 240, 784, 784), fill=(224, 166, 98, 255), outline=INK, width=26)
        d.arc((110, 380, 914, 650), start=155, end=25, fill=(96, 162, 206, 255), width=42)

    def _flask(_, d):
        d.polygon([(430, 170), (594, 170), (594, 370), (800, 810), (224, 810), (430, 370)],
                  fill=(228, 245, 252, 255), outline=INK, width=26)
        d.polygon([(285, 680), (739, 680), (788, 795), (236, 795)], fill=(68, 192, 134, 255))
        d.line((400, 170, 624, 170), fill=INK, width=30)

    created.extend([
        _draw_2x(_atom, "science_space", "cc0_atom_orbit", "atom science physics particle energy molecule"),
        _draw_2x(_planet, "science_space", "cc0_planet_saturn", "planet space cosmos universe astronomy world"),
        _draw_2x(_flask, "science_space", "cc0_science_flask", "flask beaker chemistry lab experiment science"),
    ])

    # 4. nature_animals
    def _flame(_, d):
        d.polygon([(512, 135), (710, 390), (785, 610), (675, 835), (349, 835), (239, 610), (320, 370)],
                  fill=(238, 108, 42, 255), outline=INK, width=26)
        d.polygon([(512, 340), (630, 560), (595, 780), (429, 780), (394, 560)], fill=(252, 204, 58, 255))

    def _bolt(_, d):
        d.polygon([(560, 130), (260, 540), (475, 540), (385, 890), (760, 445), (535, 445)],
                  fill=(250, 204, 48, 255), outline=INK, width=26)

    def _drop(_, d):
        d.polygon([(512, 145), (760, 515), (745, 730), (620, 855), (404, 855), (279, 730), (264, 515)],
                  fill=(62, 158, 224, 255), outline=INK, width=26)
        d.line((390, 540, 365, 690), fill=(215, 242, 255, 255), width=26)

    created.extend([
        _draw_2x(_flame, "nature_animals", "cc0_flame_fire", "fire flame heat burn energy spark"),
        _draw_2x(_bolt, "nature_animals", "cc0_lightning_bolt", "lightning storm bolt thunder electric shock"),
        _draw_2x(_drop, "nature_animals", "cc0_water_droplet", "water drop ocean rain sea river"),
    ])

    # 5. money_economy
    def _coin(_, d):
        d.ellipse((175, 175, 849, 849), fill=(242, 188, 46, 255), outline=INK, width=28)
        d.ellipse((245, 245, 779, 779), fill=(252, 212, 76, 255), outline=(176, 128, 24, 255), width=16)
        d.line((512, 330, 512, 694), fill=INK, width=32)

    def _chart(_, d):
        d.rounded_rectangle((155, 195, 869, 829), radius=36, fill=(250, 248, 242, 255), outline=INK, width=26)
        d.rectangle((265, 550, 375, 750), fill=(86, 152, 212, 255), outline=INK, width=16)
        d.rectangle((455, 420, 565, 750), fill=(86, 152, 212, 255), outline=INK, width=16)
        d.rectangle((645, 290, 755, 750), fill=(224, 78, 56, 255), outline=INK, width=16)

    def _clock(_, d):
        d.ellipse((165, 165, 859, 859), fill=(250, 248, 242, 255), outline=INK, width=28)
        d.line((512, 512, 512, 285), fill=INK, width=32)
        d.line((512, 512, 695, 560), fill=(214, 52, 40, 255), width=26)
        d.ellipse((482, 482, 542, 542), fill=INK)

    created.extend([
        _draw_2x(_coin, "money_economy", "cc0_gold_coin", "coin gold money currency wealth trade economy"),
        _draw_2x(_chart, "money_economy", "cc0_bar_chart", "chart graph data economy trade growth stat"),
        _draw_2x(_clock, "money_economy", "cc0_clock_time", "clock time hourglass watch schedule era"),
    ])

    # 6. modern_daily
    def _bulb(_, d):
        d.ellipse((275, 145, 749, 619), fill=(252, 216, 68, 255), outline=INK, width=26)
        d.rounded_rectangle((390, 585, 634, 770), radius=24, fill=(182, 190, 202, 255), outline=INK, width=24)
        d.rounded_rectangle((435, 765, 589, 845), radius=24, fill=(130, 138, 150, 255), outline=INK, width=20)

    def _book(_, d):
        d.polygon([(140, 260), (505, 310), (505, 800), (140, 740)], fill=(250, 247, 238, 255), outline=INK, width=24)
        d.polygon([(884, 260), (519, 310), (519, 800), (884, 740)], fill=(242, 238, 224, 255), outline=INK, width=24)
        for yy in (410, 505, 600):
            d.line((210, yy, 430, yy + 22), fill=(110, 120, 132, 255), width=16)
            d.line((594, yy + 22, 814, yy), fill=(110, 120, 132, 255), width=16)

    def _compass(_, d):
        d.ellipse((170, 170, 854, 854), fill=(238, 224, 186, 255), outline=INK, width=26)
        d.polygon([(512, 240), (595, 512), (429, 512)], fill=(214, 52, 40, 255), outline=INK, width=14)
        d.polygon([(512, 784), (595, 512), (429, 512)], fill=(78, 118, 168, 255), outline=INK, width=14)

    created.extend([
        _draw_2x(_bulb, "modern_daily", "cc0_lightbulb_idea", "lightbulb idea think discover bright invent"),
        _draw_2x(_book, "modern_daily", "cc0_open_book", "book reading journal archive knowledge story"),
        _draw_2x(_compass, "modern_daily", "cc0_compass_nav", "compass navigation map travel north direction"),
    ])

    return created


def main():
    parser = argparse.ArgumentParser(description="Fetch / build 100% CC0 / Public Domain 2D stickers and update CATALOG.tsv")
    parser.add_argument("--online", action="store_true", help="Also query Wikimedia Commons strictly for CC0 / Public Domain props")
    parser.add_argument("--query", default=None, help="Optional Wikimedia CC0 search query")
    parser.add_argument("--category", default="history_ancient", choices=list(index_stickers.CATEGORIES))
    args = parser.parse_args()

    created = build_cc0_cartoon_library()
    if args.online or args.query:
        q = args.query or "sword icon"
        res = try_fetch_wikimedia_cc0(q, args.category, f"cc0_wiki_{q.replace(' ', '_')}")
        if res:
            created.append(res)
            print(f"Downloaded verified CC0 Wikimedia sticker -> {res}")
        else:
            print(f"Online CC0 fetch skipped or unavailable (offline/strict CC0 filter); built {len(created)} local CC0-1.0 PNGs.")

    rows = index_stickers.rebuild_catalog()
    print(f"CC0 library ready ({len(created)} CC0-1.0 PNGs ensured). Total catalog rows: {len(rows)}.")


if __name__ == "__main__":
    main()
