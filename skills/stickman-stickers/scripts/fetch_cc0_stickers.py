#!/usr/bin/env python3
"""fetch_cc0_stickers.py: Fetches genuine 100% CC0 / Public Domain 2D props (Wikimedia CC0 API when online) and builds normalized 2D CC0 editorial & category stickers."""

import os
import re
import sys
import json
import math
import urllib.request
import urllib.parse
import argparse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

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

    # 7. Expanded Documentary Cartoon Props (2D flat fill + crisp dark ink outline, look: bright)
    def _magnifying(_, d):
        d.line((580, 580, 845, 845), fill=(168, 108, 62, 255), width=76)
        d.line((580, 580, 845, 845), fill=INK, width=22)
        d.ellipse((165, 165, 655, 655), fill=(215, 240, 252, 255), outline=INK, width=30)
        d.arc((225, 225, 595, 595), start=205, end=275, fill=(255, 255, 255, 230), width=22)

    def _brain(_, d):
        d.ellipse((185, 235, 560, 745), fill=(242, 168, 178, 255), outline=INK, width=26)
        d.ellipse((464, 235, 839, 745), fill=(236, 152, 166, 255), outline=INK, width=26)
        d.line((512, 250, 512, 740), fill=INK, width=20)
        for yy in (360, 490, 610):
            d.arc((245, yy - 45, 455, yy + 45), start=10, end=175, fill=INK, width=16)
            d.arc((569, yy - 45, 779, yy + 45), start=5, end=170, fill=INK, width=16)

    def _factory(_, d):
        d.rectangle((160, 470, 864, 835), fill=(186, 114, 88, 255), outline=INK, width=26)
        d.polygon([(160, 470), (380, 325), (380, 470), (595, 325), (595, 470), (864, 470)],
                  fill=(152, 92, 72, 255), outline=INK, width=24)
        d.rectangle((690, 175, 795, 470), fill=(122, 128, 138, 255), outline=INK, width=24)
        for xx in (245, 415, 585):
            d.rectangle((xx, 575, xx + 95, 690), fill=(248, 224, 132, 255), outline=INK, width=16)

    def _ship(_, d):
        d.polygon([(160, 585), (864, 585), (750, 805), (274, 805)], fill=(154, 96, 56, 255), outline=INK, width=26)
        d.line((512, 200, 512, 585), fill=INK, width=26)
        d.polygon([(525, 220), (815, 455), (525, 515)], fill=(250, 246, 232, 255), outline=INK, width=22)
        d.polygon([(498, 260), (245, 490), (498, 520)], fill=(240, 232, 212, 255), outline=INK, width=22)

    def _hourglass(_, d):
        d.rectangle((260, 155, 764, 225), fill=(176, 122, 68, 255), outline=INK, width=24)
        d.rectangle((260, 799, 764, 869), fill=(176, 122, 68, 255), outline=INK, width=24)
        d.polygon([(305, 225), (719, 225), (535, 512), (489, 512)], fill=(224, 242, 248, 255), outline=INK, width=24)
        d.polygon([(489, 512), (535, 512), (719, 799), (305, 799)], fill=(224, 242, 248, 255), outline=INK, width=24)
        d.polygon([(355, 790), (669, 790), (545, 650), (479, 650)], fill=(238, 198, 92, 255))

    def _skull(_, d):
        d.ellipse((220, 175, 804, 675), fill=(244, 238, 222, 255), outline=INK, width=26)
        d.rounded_rectangle((345, 595, 679, 825), radius=36, fill=(244, 238, 222, 255), outline=INK, width=24)
        d.ellipse((320, 365, 455, 505), fill=INK)
        d.ellipse((569, 365, 704, 505), fill=INK)
        d.polygon([(512, 510), (472, 595), (552, 595)], fill=INK)
        for xx in (425, 512, 599):
            d.line((xx, 715, xx, 820), fill=INK, width=18)

    def _balance_scale(_, d):
        d.line((512, 215, 512, 815), fill=INK, width=28)
        d.rectangle((330, 785, 694, 845), fill=(168, 122, 68, 255), outline=INK, width=22)
        d.line((210, 315, 814, 315), fill=INK, width=26)
        d.arc((135, 520, 365, 675), start=0, end=180, fill=(234, 178, 64, 255), width=36)
        d.arc((659, 520, 889, 675), start=0, end=180, fill=(234, 178, 64, 255), width=36)
        d.line((210, 315, 145, 590), fill=INK, width=14)
        d.line((210, 315, 355, 590), fill=INK, width=14)
        d.line((814, 315, 669, 590), fill=INK, width=14)
        d.line((814, 315, 879, 590), fill=INK, width=14)

    def _map_pin(_, d):
        d.polygon([(512, 865), (275, 495), (749, 495)], fill=(214, 58, 48, 255), outline=INK, width=24)
        d.ellipse((245, 155, 779, 655), fill=(214, 58, 48, 255), outline=INK, width=26)
        d.ellipse((395, 295, 629, 529), fill=(252, 248, 238, 255), outline=INK, width=22)

    def _megaphone(_, d):
        d.polygon([(225, 445), (745, 215), (745, 765), (225, 565)], fill=(234, 172, 54, 255), outline=INK, width=26)
        d.rounded_rectangle((145, 425, 265, 585), radius=25, fill=(214, 58, 48, 255), outline=INK, width=24)
        d.rounded_rectangle((285, 565, 385, 815), radius=24, fill=(92, 98, 112, 255), outline=INK, width=22)

    def _microscope(_, d):
        d.rectangle((250, 770, 774, 845), fill=(112, 122, 138, 255), outline=INK, width=24)
        d.arc((415, 295, 775, 765), start=270, end=90, fill=INK, width=42)
        d.polygon([(355, 195), (495, 165), (565, 505), (425, 535)], fill=(224, 232, 240, 255), outline=INK, width=24)
        d.rectangle((295, 615, 565, 665), fill=(72, 82, 96, 255), outline=INK, width=20)

    def _rocket(_, d):
        d.polygon([(512, 130), (675, 410), (655, 725), (369, 725), (349, 410)], fill=(242, 240, 234, 255), outline=INK, width=26)
        d.polygon([(512, 130), (615, 310), (409, 310)], fill=(214, 58, 48, 255), outline=INK, width=22)
        d.polygon([(369, 580), (210, 770), (369, 725)], fill=(214, 58, 48, 255), outline=INK, width=22)
        d.polygon([(655, 580), (814, 770), (655, 725)], fill=(214, 58, 48, 255), outline=INK, width=22)
        d.ellipse((442, 405, 582, 545), fill=(116, 194, 236, 255), outline=INK, width=22)

    def _globe(_, d):
        d.ellipse((165, 165, 859, 859), fill=(94, 164, 218, 255), outline=INK, width=28)
        d.polygon([(265, 330), (450, 275), (495, 455), (350, 565), (255, 450)], fill=(96, 178, 108, 255), outline=INK, width=18)
        d.polygon([(565, 385), (755, 345), (780, 555), (615, 685), (545, 535)], fill=(96, 178, 108, 255), outline=INK, width=18)

    def _dna(_, d):
        for i in range(6):
            yy = 200 + i * 115
            x1 = 340 + int(160 * math.sin(i * 0.9))
            x2 = 684 - int(160 * math.sin(i * 0.9))
            d.line((x1, yy, x2, yy), fill=(234, 178, 64, 255), width=24)
            d.ellipse((x1 - 36, yy - 36, x1 + 36, yy + 36), fill=(62, 148, 212, 255), outline=INK, width=16)
            d.ellipse((x2 - 36, yy - 36, x2 + 36, yy + 36), fill=(214, 68, 56, 255), outline=INK, width=16)

    def _pyramid(_, d):
        d.polygon([(512, 190), (854, 790), (170, 790)], fill=(228, 186, 108, 255), outline=INK, width=28)
        d.polygon([(512, 190), (854, 790), (595, 790)], fill=(196, 152, 78, 255), outline=INK, width=22)

    def _column(_, d):
        d.rectangle((260, 175, 764, 255), fill=(236, 228, 210, 255), outline=INK, width=24)
        d.rectangle((325, 255, 699, 755), fill=(244, 238, 224, 255), outline=INK, width=24)
        d.rectangle((260, 755, 764, 835), fill=(236, 228, 210, 255), outline=INK, width=24)
        for xx in (415, 512, 609):
            d.line((xx, 285, xx, 725), fill=INK, width=16)

    def _bank(_, d):
        d.polygon([(150, 395), (512, 165), (874, 395)], fill=(216, 208, 192, 255), outline=INK, width=26)
        d.rectangle((200, 395, 824, 775), fill=(244, 238, 224, 255), outline=INK, width=24)
        for xx in (290, 440, 584, 734):
            d.rectangle((xx - 30, 425, xx + 30, 745), fill=(224, 216, 200, 255), outline=INK, width=18)
        d.rectangle((150, 775, 874, 845), fill=(186, 178, 164, 255), outline=INK, width=24)

    def _chest(_, d):
        d.rounded_rectangle((175, 435, 849, 815), radius=28, fill=(164, 102, 54, 255), outline=INK, width=26)
        d.chord((175, 235, 849, 635), start=180, end=0, fill=(186, 122, 68, 255), outline=INK, width=26)
        d.rectangle((452, 405, 572, 545), fill=(242, 192, 54, 255), outline=INK, width=22)

    def _thermometer(_, d):
        d.rounded_rectangle((432, 145, 592, 675), radius=80, fill=(242, 246, 250, 255), outline=INK, width=26)
        d.ellipse((362, 585, 662, 885), fill=(214, 58, 48, 255), outline=INK, width=26)
        d.rectangle((476, 335, 548, 665), fill=(214, 58, 48, 255))

    def _key(_, d):
        d.ellipse((165, 315, 495, 645), fill=(242, 188, 52, 255), outline=INK, width=26)
        d.ellipse((265, 415, 395, 545), fill=(0, 0, 0, 0), outline=INK, width=20)
        d.rectangle((485, 445, 855, 525), fill=(242, 188, 52, 255), outline=INK, width=24)
        d.rectangle((695, 525, 765, 645), fill=(242, 188, 52, 255), outline=INK, width=22)
        d.rectangle((785, 525, 855, 615), fill=(242, 188, 52, 255), outline=INK, width=22)

    def _lock(_, d):
        d.arc((305, 155, 719, 575), start=180, end=0, fill=(140, 148, 162, 255), width=64)
        d.rounded_rectangle((225, 415, 799, 855), radius=48, fill=(234, 178, 58, 255), outline=INK, width=28)
        d.ellipse((465, 545, 559, 639), fill=INK)
        d.polygon([(492, 615), (532, 615), (546, 735), (478, 735)], fill=INK)

    def _gear(_, d):
        pts = []
        for i in range(16):
            ang = i * math.pi / 8
            r = 385 if i % 2 == 0 else 285
            pts.append((512 + int(r * math.cos(ang)), 512 + int(r * math.sin(ang))))
        d.polygon(pts, fill=(154, 164, 178, 255), outline=INK, width=26)
        d.ellipse((385, 385, 639, 639), fill=(248, 244, 234, 255), outline=INK, width=24)

    def _battery(_, d):
        d.rectangle((425, 145, 599, 215), fill=(154, 164, 178, 255), outline=INK, width=22)
        d.rounded_rectangle((295, 215, 729, 865), radius=36, fill=(242, 246, 250, 255), outline=INK, width=26)
        d.rounded_rectangle((335, 365, 689, 825), radius=20, fill=(68, 186, 108, 255))

    def _newspaper(_, d):
        d.rounded_rectangle((175, 195, 849, 829), radius=28, fill=(246, 242, 230, 255), outline=INK, width=26)
        d.rectangle((245, 265, 779, 385), fill=(52, 62, 78, 255))
        d.rectangle((245, 435, 495, 645), fill=(168, 196, 222, 255), outline=INK, width=16)
        for yy in (455, 525, 595, 685, 755):
            x_st = 535 if yy < 650 else 245
            d.line((x_st, yy, 779, yy), fill=INK, width=20)

    def _house(_, d):
        d.polygon([(145, 475), (512, 185), (879, 475)], fill=(208, 78, 64, 255), outline=INK, width=26)
        d.rectangle((235, 475, 789, 835), fill=(246, 238, 218, 255), outline=INK, width=26)
        d.rectangle((445, 595, 579, 835), fill=(164, 108, 64, 255), outline=INK, width=20)

    def _coffee(_, d):
        d.arc((645, 415, 855, 675), start=270, end=90, fill=INK, width=38)
        d.rounded_rectangle((215, 345, 715, 825), radius=48, fill=(248, 244, 234, 255), outline=INK, width=26)
        d.ellipse((245, 315, 685, 395), fill=(138, 86, 52, 255), outline=INK, width=20)

    def _soda_can(_, d):
        # Metallic silver base & tapered aluminum rim
        d.rounded_rectangle((295, 225, 729, 865), radius=64, fill=(214, 48, 42, 255), outline=INK, width=26)
        # Cream & white retro diagonal stripe band
        d.polygon([(315, 515), (709, 415), (709, 555), (315, 655)], fill=(252, 246, 232, 255))
        d.line((315, 515, 709, 415), fill=INK, width=16)
        d.line((315, 655, 709, 555), fill=INK, width=16)
        # Top & bottom metallic rims
        d.rounded_rectangle((295, 215, 729, 305), radius=34, fill=(216, 222, 232, 255), outline=INK, width=24)
        d.rounded_rectangle((315, 795, 709, 865), radius=28, fill=(192, 198, 210, 255), outline=INK, width=22)
        # Pull-tab & fizz bubbles
        d.rounded_rectangle((465, 165, 575, 235), radius=18, fill=(230, 234, 240, 255), outline=INK, width=18)
        d.line((385, 355, 385, 745), fill=(255, 155, 145, 255), width=22)
        for bx, by, br in ((235, 245, 26), (785, 215, 30), (805, 335, 20)):
            d.ellipse((bx - br, by - br, bx + br, by + br), fill=(246, 250, 255, 255), outline=INK, width=14)

    def _question_badge(_, d):
        d.ellipse((155, 155, 869, 869), fill=(246, 202, 64, 255), outline=INK, width=28)
        d.arc((365, 285, 659, 535), start=190, end=45, fill=INK, width=54)
        d.line((512, 485, 512, 625), fill=INK, width=54)
        d.ellipse((475, 685, 549, 759), fill=INK)

    def _exclaim_badge(_, d):
        d.ellipse((155, 155, 869, 869), fill=(218, 64, 52, 255), outline=INK, width=28)
        d.line((512, 275, 512, 605), fill=(252, 248, 240, 255), width=64)
        d.ellipse((472, 675, 552, 755), fill=(252, 248, 240, 255))

    def _leaf(_, d):
        d.polygon([(512, 165), (765, 385), (715, 685), (512, 825), (309, 685), (259, 385)],
                  fill=(82, 178, 98, 255), outline=INK, width=26)
        d.line((512, 245, 512, 865), fill=INK, width=24)

    def _tree(_, d):
        d.rectangle((455, 565, 569, 845), fill=(154, 98, 56, 255), outline=INK, width=24)
        d.ellipse((225, 195, 799, 635), fill=(86, 172, 92, 255), outline=INK, width=26)

    def _mountain(_, d):
        d.polygon([(145, 795), (465, 225), (785, 795)], fill=(152, 164, 178, 255), outline=INK, width=26)
        d.polygon([(465, 225), (590, 445), (495, 425), (435, 465), (355, 425)], fill=(250, 252, 255, 255), outline=INK, width=18)

    def _sun(_, d):
        d.ellipse((295, 295, 729, 729), fill=(252, 204, 54, 255), outline=INK, width=26)
        for i in range(8):
            ang = i * math.pi / 4
            d.line((512 + int(275 * math.cos(ang)), 512 + int(275 * math.sin(ang)),
                    512 + int(395 * math.cos(ang)), 512 + int(395 * math.sin(ang))), fill=INK, width=26)

    def _moon(_, d):
        d.ellipse((205, 175, 819, 789), fill=(242, 214, 108, 255), outline=INK, width=26)
        d.ellipse((355, 225, 865, 735), fill=(0, 0, 0, 0))

    created.extend([
        _draw_2x(_magnifying, "editorial_accents", "cc0_magnifying_glass", "magnifying glass search inspect clue detect"),
        _draw_2x(_brain, "science_space", "cc0_human_brain", "brain mind psychology smart thinking memory"),
        _draw_2x(_factory, "money_economy", "cc0_factory_industry", "factory industry manufacturing production smoke"),
        _draw_2x(_ship, "history_ancient", "cc0_sailing_ship", "ship galleon vessel maritime voyage trade"),
        _draw_2x(_hourglass, "history_ancient", "cc0_hourglass_time", "hourglass time sand countdown era ancient"),
        _draw_2x(_skull, "nature_animals", "cc0_fossil_skull", "skull fossil bone skeleton death ancient"),
        _draw_2x(_balance_scale, "money_economy", "cc0_balance_scale", "scale balance justice law economy compare"),
        _draw_2x(_map_pin, "editorial_accents", "cc0_map_pin", "map pin location destination marker place"),
        _draw_2x(_megaphone, "modern_daily", "cc0_megaphone_shout", "megaphone announce broadcast shout speaker"),
        _draw_2x(_microscope, "science_space", "cc0_microscope_lab", "microscope lab science research biology"),
        _draw_2x(_rocket, "science_space", "cc0_space_rocket", "rocket space launch mars moon tech"),
        _draw_2x(_globe, "science_space", "cc0_earth_globe", "earth globe world planet continent geography"),
        _draw_2x(_dna, "science_space", "cc0_dna_helix", "dna helix genetics genome biology life"),
        _draw_2x(_pyramid, "history_ancient", "cc0_egypt_pyramid", "pyramid egypt ancient monument pharaoh"),
        _draw_2x(_column, "history_ancient", "cc0_roman_column", "column pillar roman greek ruin temple"),
        _draw_2x(_bank, "money_economy", "cc0_bank_building", "bank treasury finance money institution"),
        _draw_2x(_chest, "money_economy", "cc0_treasure_chest", "treasure chest wealth gold loot vault"),
        _draw_2x(_thermometer, "science_space", "cc0_thermometer_temp", "thermometer temperature heat cold climate"),
        _draw_2x(_key, "modern_daily", "cc0_brass_key", "key unlock secret solution access"),
        _draw_2x(_lock, "modern_daily", "cc0_padlock_lock", "lock security private protected closed"),
        _draw_2x(_gear, "money_economy", "cc0_gear_cog", "gear cog mechanism engine system industry"),
        _draw_2x(_battery, "modern_daily", "cc0_battery_power", "battery power energy charge tech"),
        _draw_2x(_newspaper, "modern_daily", "cc0_newspaper_press", "newspaper press media report headline"),
        _draw_2x(_house, "modern_daily", "cc0_house_home", "house home building shelter village"),
        _draw_2x(_coffee, "modern_daily", "cc0_coffee_mug", "coffee mug morning drink routine"),
        _draw_2x(_soda_can, "modern_daily", "cc0_soda_can", "soda cola pop fizzy drink can soft drink sugar beverage modern"),
        _draw_2x(_question_badge, "editorial_accents", "cc0_question_mark", "question mark mystery why unknown doubt"),
        _draw_2x(_exclaim_badge, "editorial_accents", "cc0_exclamation_mark", "exclamation alert shock surprise attention"),
        _draw_2x(_leaf, "nature_animals", "cc0_green_leaf", "leaf nature plant ecology environment"),
        _draw_2x(_tree, "nature_animals", "cc0_oak_tree", "tree forest wood nature environment"),
        _draw_2x(_mountain, "nature_animals", "cc0_mountain_peak", "mountain peak terrain geography nature"),
        _draw_2x(_sun, "science_space", "cc0_solar_sun", "sun solar daylight energy warmth star"),
        _draw_2x(_moon, "science_space", "cc0_crescent_moon", "moon night lunar sleep sky"),
    ])

    return created


def harmonize_cc0_icon_to_editorial(im, fill_rgb=(72, 132, 192)):
    """Converts a CC0 monochrome silhouette icon into a crisp dark-ink-outlined flat-filled 2D editorial sticker (512x512 RGBA)."""
    norm = _normalize_to_512_rgba(im)
    if norm is None:
        return None
    arr = np.array(norm)
    a = arr[:, :, 3]
    # Build dilated ink border mask (6px crisp dark ink outline)
    alpha_img = Image.fromarray(a, mode="L")
    dilated = alpha_img.filter(ImageFilter.MaxFilter(13))
    out_arr = np.zeros((512, 512, 4), dtype=np.uint8)
    d_mask = np.array(dilated) > 40
    out_arr[d_mask] = [24, 26, 34, 255]
    # Fill core shape with editorial flat color
    core_mask = a > 90
    out_arr[core_mask] = [fill_rgb[0], fill_rgb[1], fill_rgb[2], 255]
    # Preserve soft alpha edge
    out_img = Image.fromarray(out_arr, mode="RGBA")
    return out_img


KENNEY_CC0_CURATED = [
    # (github_subpath, category, slug, tags, fill_rgb)
    ("icons/Board%20Game%20Icons/Double%20(128px)/arrow_clockwise.png", "editorial_accents", "cc0_kenney_arrow_clockwise", "arrow clockwise cycle repeat loop", (214, 68, 56)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/arrow_counterclockwise.png", "editorial_accents", "cc0_kenney_arrow_rewind", "arrow rewind reverse back history", (72, 132, 192)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/arrow_right_curve.png", "editorial_accents", "cc0_kenney_arrow_curve", "arrow curve pointer next step", (214, 68, 56)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/arrow_rotate.png", "editorial_accents", "cc0_kenney_arrow_rotate", "arrow rotate turn change cycle", (234, 172, 54)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/award.png", "editorial_accents", "cc0_kenney_award_medal", "award medal prize winner best", (234, 178, 54)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/book_closed.png", "modern_daily", "cc0_kenney_book_closed", "book journal archive history manual", (176, 118, 72)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/book_open.png", "modern_daily", "cc0_kenney_book_open", "book open study knowledge read", (212, 168, 108)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/bow.png", "history_ancient", "cc0_kenney_hunting_bow", "bow hunting weapon ancient archery", (164, 108, 62)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/campfire.png", "nature_animals", "cc0_kenney_campfire", "campfire fire heat camp ancient", (234, 112, 46)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/chess_king.png", "history_ancient", "cc0_kenney_chess_king", "king leader ruler strategy empire", (234, 178, 54)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/chess_knight.png", "history_ancient", "cc0_kenney_chess_knight", "knight horse cavalry war strategy", (132, 142, 158)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/chess_rook.png", "history_ancient", "cc0_kenney_castle_rook", "castle tower fortress defense", (164, 156, 142)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/crown_a.png", "history_ancient", "cc0_kenney_crown_royal", "crown royal king monarch empire", (242, 188, 48)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/crown_b.png", "history_ancient", "cc0_kenney_crown_imperial", "crown emperor kingdom authority", (234, 168, 42)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/dollar.png", "money_economy", "cc0_kenney_dollar_sign", "dollar money currency price economy", (68, 168, 96)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/exploding.png", "editorial_accents", "cc0_kenney_explosion_burst", "explosion burst shock impact boom", (234, 108, 46)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/fire.png", "nature_animals", "cc0_kenney_fire_flame", "fire flame burn heat energy", (234, 96, 42)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/flag_square.png", "history_ancient", "cc0_kenney_flag_banner", "flag banner territory claim nation", (214, 62, 52)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/flag_triangle.png", "editorial_accents", "cc0_kenney_flag_marker", "flag milestone marker checkpoint", (234, 168, 48)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/flask_full.png", "science_space", "cc0_kenney_flask_potion", "flask chemistry science liquid lab", (72, 168, 198)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/hand.png", "modern_daily", "cc0_kenney_hand_palm", "hand stop touch human grab", (236, 192, 154)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/hourglass.png", "history_ancient", "cc0_kenney_hourglass", "hourglass time era ancient countdown", (224, 178, 86)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/lock_closed.png", "modern_daily", "cc0_kenney_lock_closed", "lock closed secret security vault", (152, 162, 178)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/lock_open.png", "modern_daily", "cc0_kenney_lock_open", "lock open unlock discovery free", (82, 168, 108)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/notepad.png", "modern_daily", "cc0_kenney_notepad", "notepad notes list document record", (242, 232, 202)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/notepad_write.png", "modern_daily", "cc0_kenney_notepad_write", "notepad write study log record", (238, 224, 182)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/pouch.png", "money_economy", "cc0_kenney_gold_pouch", "pouch bag money gold coins", (196, 148, 78)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/puzzle.png", "science_space", "cc0_kenney_puzzle_piece", "puzzle clue piece mystery solve", (88, 152, 208)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/resource_apple.png", "nature_animals", "cc0_kenney_apple_fruit", "apple fruit food diet harvest", (214, 64, 54)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/resource_iron.png", "history_ancient", "cc0_kenney_iron_ingot", "iron ore metal ingot bronze", (142, 152, 166)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/resource_lumber.png", "nature_animals", "cc0_kenney_lumber_wood", "lumber wood logs timber forest", (164, 106, 62)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/resource_wheat.png", "nature_animals", "cc0_kenney_wheat_grain", "wheat grain crop agriculture harvest", (234, 188, 64)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/shield.png", "history_ancient", "cc0_kenney_shield_defense", "shield defense armor protect war", (84, 138, 192)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/skull.png", "nature_animals", "cc0_kenney_skull_bone", "skull death fossil danger ancient", (236, 228, 210)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/structure_church.png", "history_ancient", "cc0_kenney_temple_church", "temple church building religion monument", (204, 188, 162)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/structure_farm.png", "money_economy", "cc0_kenney_farm_barn", "farm agriculture barn crop economy", (196, 86, 68)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/structure_house.png", "modern_daily", "cc0_kenney_house_village", "house home village shelter city", (214, 168, 114)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/structure_tower.png", "history_ancient", "cc0_kenney_tower_fort", "tower castle watchtower defense", (164, 156, 148)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/structure_wall.png", "history_ancient", "cc0_kenney_city_wall", "wall barrier border defense fort", (176, 166, 152)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/sword.png", "history_ancient", "cc0_kenney_sword_blade", "sword blade weapon battle war", (158, 172, 188)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/timer_50.png", "money_economy", "cc0_kenney_timer_half", "timer clock speed duration half", (72, 148, 204)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/tokens_stack.png", "money_economy", "cc0_kenney_coin_stack", "coins stack wealth money reserve", (234, 184, 54)),
    ("icons/Game%20Icons/Black/2x/checkmark.png", "editorial_accents", "cc0_kenney_checkmark", "check checkmark correct verified yes", (46, 166, 92)),
    ("icons/Game%20Icons/Black/2x/cross.png", "editorial_accents", "cc0_kenney_cross_x", "cross x wrong myth false no", (214, 58, 48)),
    ("icons/Game%20Icons/Black/2x/exclamation.png", "editorial_accents", "cc0_kenney_exclamation", "exclamation alert shock surprise", (214, 64, 52)),
    ("icons/Game%20Icons/Black/2x/gear.png", "money_economy", "cc0_kenney_gear", "gear cog machine industry system", (134, 146, 162)),
    ("icons/Game%20Icons/Black/2x/home.png", "modern_daily", "cc0_kenney_home", "home house shelter family", (212, 152, 92)),
    ("icons/Game%20Icons/Black/2x/information.png", "editorial_accents", "cc0_kenney_info", "info information fact guide note", (68, 138, 204)),
    ("icons/Game%20Icons/Black/2x/medal1.png", "editorial_accents", "cc0_kenney_medal_gold", "medal winner first champion award", (242, 188, 48)),
    ("icons/Game%20Icons/Black/2x/phone.png", "modern_daily", "cc0_kenney_phone", "phone mobile smartphone tech", (84, 132, 184)),
    ("icons/Game%20Icons/Black/2x/question.png", "editorial_accents", "cc0_kenney_question", "question why mystery unknown", (234, 178, 52)),
    ("icons/Game%20Icons/Black/2x/rewind.png", "editorial_accents", "cc0_kenney_rewind", "rewind back past history", (72, 132, 192)),
    ("icons/Game%20Icons/Black/2x/shoppingCart.png", "money_economy", "cc0_kenney_cart", "shopping cart market buy consumer", (84, 152, 198)),
    ("icons/Game%20Icons/Black/2x/star.png", "editorial_accents", "cc0_kenney_star", "star favorite highlight top", (248, 198, 48)),
    ("icons/Game%20Icons/Black/2x/target.png", "editorial_accents", "cc0_kenney_target", "target bullseye focus goal aim", (214, 58, 48)),
    ("icons/Game%20Icons/Black/2x/trophy.png", "editorial_accents", "cc0_kenney_trophy", "trophy victory winner champion", (242, 188, 48)),
    ("icons/Game%20Icons/Black/2x/warning.png", "editorial_accents", "cc0_kenney_warning", "warning danger caution alert", (242, 184, 44)),
    ("icons/Game%20Icons/Black/2x/wrench.png", "modern_daily", "cc0_kenney_wrench", "wrench tool repair craft build", (134, 148, 164)),
    ("icons/Game%20Icons/Black/2x/zoom.png", "editorial_accents", "cc0_kenney_zoom_search", "zoom search magnifying inspect", (78, 142, 198)),
    ("icons/Game%20Icons/Black/2x/locked.png", "modern_daily", "cc0_kenney_locked_icon", "locked security closed private", (142, 152, 168)),
    ("icons/Game%20Icons/Black/2x/unlocked.png", "modern_daily", "cc0_kenney_unlocked_icon", "unlocked open access freedom", (82, 168, 108)),
    ("icons/Game%20Icons/Black/2x/power.png", "science_space", "cc0_kenney_power_energy", "power energy electricity switch", (234, 172, 54)),
    ("icons/Game%20Icons/Black/2x/trashcan.png", "modern_daily", "cc0_kenney_trash_waste", "trash waste discard remove myth", (152, 160, 172)),
    ("icons/Game%20Icons/Black/2x/leaderboardsComplex.png", "money_economy", "cc0_kenney_podium_rank", "ranking podium stats top leaderboard", (68, 138, 204)),
    ("icons/Game%20Icons/Black/2x/barsVertical.png", "money_economy", "cc0_kenney_bars_chart", "bars chart statistics data growth", (68, 148, 204)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/dice_3D_detailed.png", "money_economy", "cc0_kenney_dice_chance", "dice chance probability risk gamble", (236, 228, 210)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/spinner.png", "editorial_accents", "cc0_kenney_spinner_cycle", "spinner cycle wheel random", (234, 148, 54)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/tag_shield.png", "history_ancient", "cc0_kenney_shield_badge", "shield badge armor emblem protect", (84, 138, 192)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/timer_100.png", "money_economy", "cc0_kenney_timer_full", "timer full complete clock deadline", (214, 68, 56)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/suit_hearts_broken.png", "editorial_accents", "cc0_kenney_broken_heart", "broken heart loss tragedy decline", (214, 58, 48)),
    ("icons/Board%20Game%20Icons/Double%20(128px)/direction_n.png", "editorial_accents", "cc0_kenney_compass_north", "north compass direction map arrow", (68, 138, 204)),
]


def fetch_kenney_cc0_icons():
    """Downloads curated Kenney CC0-1.0 icons and harmonizes them into flat-fill + crisp dark-ink-outline 2D stickers."""
    fetched = []
    base_raw = "https://raw.githubusercontent.com/shorepine/kenney/master/"
    for subpath, cat, slug, tags, fill_rgb in KENNEY_CC0_CURATED:
        out_dir = os.path.join(CC0_ROOT, cat)
        os.makedirs(out_dir, exist_ok=True)
        out_p = os.path.join(out_dir, f"{slug}.png")
        meta_p = os.path.join(out_dir, f"{slug}.meta.json")
        if os.path.exists(out_p) and os.path.getsize(out_p) > 500 and os.path.exists(meta_p):
            fetched.append(out_p)
            continue
        try:
            url = base_raw + subpath
            req = urllib.request.Request(url, headers={"User-Agent": "StickmanStickers/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                im = Image.open(BytesIO(resp.read()))
            harm = harmonize_cc0_icon_to_editorial(im, fill_rgb=fill_rgb)
            if harm:
                harm.save(out_p)
                ok, _, _ = index_stickers.inspect_png_alpha(out_p)
                if ok:
                    with open(meta_p, "w", encoding="utf-8") as mf:
                        json.dump({"tags": tags, "category": cat, "source": "cc0_library", "license": "CC0-1.0", "origin": "Kenney CC0"}, mf, indent=2)
                    fetched.append(out_p)
                else:
                    os.remove(out_p)
        except Exception:
            continue
    return fetched


def _parse_svg_color(val, default_ink=(24, 26, 34, 255)):
    """Maps SVG stroke/fill color strings to RGBA tuples harmonized to editorial ink."""
    if not val or val.strip().lower() in ("none", "transparent"):
        return None
    v = val.strip().lower()
    if v in ("currentcolor", "black", "#000", "#000000", "#2a2a2a", "#111", "#18181b", "#222", "#333"):
        return default_ink
    if v.startswith("#"):
        hx = v[1:]
        if len(hx) == 3:
            hx = "".join(c * 2 for c in hx)
        if len(hx) == 6:
            return (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), 255)
    return default_ink


def _svg_path_to_polylines(d_str):
    """Converts SVG path `d` commands (M,L,H,V,C,S,Q,T,Z) into list of sampled polylines."""
    tokens = re.findall(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", d_str or "")
    polylines = []
    cur = []
    cx, cy = 0.0, 0.0
    sx, sy = 0.0, 0.0
    prev_ctrl = None
    prev_cmd = ""
    idx = 0
    cmd = ""

    def _next_f():
        nonlocal idx
        v = float(tokens[idx])
        idx += 1
        return v

    def _has_num():
        return idx < len(tokens) and not tokens[idx].isalpha()

    while idx < len(tokens):
        tok = tokens[idx]
        if tok.isalpha():
            cmd = tok
            idx += 1
        elif cmd == "M":
            cmd = "L"
        elif cmd == "m":
            cmd = "l"

        if cmd in ("M", "m"):
            if cur:
                polylines.append((cur, False))
            nx, ny = _next_f(), _next_f()
            if cmd == "m":
                nx += cx
                ny += cy
            cx, cy = nx, ny
            sx, sy = cx, cy
            cur = [(cx, cy)]
            prev_ctrl = None
            cmd = "L" if cmd == "M" else "l"
        elif cmd in ("L", "l"):
            while _has_num():
                nx, ny = _next_f(), _next_f()
                if cmd == "l":
                    nx += cx
                    ny += cy
                cx, cy = nx, ny
                cur.append((cx, cy))
            prev_ctrl = None
        elif cmd in ("H", "h"):
            while _has_num():
                nx = _next_f()
                if cmd == "h":
                    nx += cx
                cx = nx
                cur.append((cx, cy))
            prev_ctrl = None
        elif cmd in ("V", "v"):
            while _has_num():
                ny = _next_f()
                if cmd == "v":
                    ny += cy
                cy = ny
                cur.append((cx, cy))
            prev_ctrl = None
        elif cmd in ("C", "c"):
            while _has_num():
                x1, y1, x2, y2, x3, y3 = (_next_f() for _ in range(6))
                if cmd == "c":
                    x1 += cx; y1 += cy; x2 += cx; y2 += cy; x3 += cx; y3 += cy
                for k in range(1, 17):
                    t = k / 16.0
                    mt = 1.0 - t
                    px = mt**3 * cx + 3 * mt**2 * t * x1 + 3 * mt * t**2 * x2 + t**3 * x3
                    py = mt**3 * cy + 3 * mt**2 * t * y1 + 3 * mt * t**2 * y2 + t**3 * y3
                    cur.append((px, py))
                prev_ctrl = (x2, y2)
                cx, cy = x3, y3
        elif cmd in ("S", "s"):
            while _has_num():
                x2, y2, x3, y3 = (_next_f() for _ in range(4))
                if cmd == "s":
                    x2 += cx; y2 += cy; x3 += cx; y3 += cy
                if prev_cmd in ("C", "c", "S", "s") and prev_ctrl:
                    x1, y1 = 2 * cx - prev_ctrl[0], 2 * cy - prev_ctrl[1]
                else:
                    x1, y1 = cx, cy
                for k in range(1, 17):
                    t = k / 16.0
                    mt = 1.0 - t
                    px = mt**3 * cx + 3 * mt**2 * t * x1 + 3 * mt * t**2 * x2 + t**3 * x3
                    py = mt**3 * cy + 3 * mt**2 * t * y1 + 3 * mt * t**2 * y2 + t**3 * y3
                    cur.append((px, py))
                prev_ctrl = (x2, y2)
                cx, cy = x3, y3
        elif cmd in ("Q", "q"):
            while _has_num():
                x1, y1, x2, y2 = (_next_f() for _ in range(4))
                if cmd == "q":
                    x1 += cx; y1 += cy; x2 += cx; y2 += cy
                for k in range(1, 13):
                    t = k / 12.0
                    mt = 1.0 - t
                    px = mt**2 * cx + 2 * mt * t * x1 + t**2 * x2
                    py = mt**2 * cy + 2 * mt * t * y1 + t**2 * y2
                    cur.append((px, py))
                prev_ctrl = (x1, y1)
                cx, cy = x2, y2
        elif cmd in ("T", "t"):
            while _has_num():
                x2, y2 = _next_f(), _next_f()
                if cmd == "t":
                    x2 += cx; y2 += cy
                if prev_cmd in ("Q", "q", "T", "t") and prev_ctrl:
                    x1, y1 = 2 * cx - prev_ctrl[0], 2 * cy - prev_ctrl[1]
                else:
                    x1, y1 = cx, cy
                for k in range(1, 13):
                    t = k / 12.0
                    mt = 1.0 - t
                    px = mt**2 * cx + 2 * mt * t * x1 + t**2 * x2
                    py = mt**2 * cy + 2 * mt * t * y1 + t**2 * y2
                    cur.append((px, py))
                prev_ctrl = (x1, y1)
                cx, cy = x2, y2
        elif cmd in ("A", "a"):
            while _has_num():
                _rx, _ry, _rot, _laf, _sf, x2, y2 = (_next_f() for _ in range(7))
                if cmd == "a":
                    x2 += cx; y2 += cy
                cur.append((x2, y2))
                cx, cy = x2, y2
            prev_ctrl = None
        elif cmd in ("Z", "z"):
            if cur:
                cur.append((sx, sy))
                polylines.append((cur, True))
                cur = []
            cx, cy = sx, sy
            prev_ctrl = None
        else:
            if _has_num():
                idx += 1
        prev_cmd = cmd
    if cur:
        polylines.append((cur, False))
    return polylines


def _rasterize_svg_to_512_rgba(svg_text, force_ink_accent=None):
    """Rasterizes simple 2D editorial SVGs at 1024x1024 and normalizes cleanly to 512x512 RGBA."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(svg_text)
    except Exception:
        return None

    vb = root.attrib.get("viewBox", "0 0 48 48").replace(",", " ").split()
    try:
        vx0, vy0, vw, vh = [float(x) for x in vb[:4]]
    except Exception:
        vx0, vy0, vw, vh = 0.0, 0.0, 48.0, 48.0

    S = 1024
    pad = 84
    scale = min((S - 2 * pad) / max(1.0, vw), (S - 2 * pad) / max(1.0, vh))
    ox = (S - vw * scale) * 0.5 - vx0 * scale
    oy = (S - vh * scale) * 0.5 - vy0 * scale

    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def_stroke = _parse_svg_color(root.attrib.get("stroke"), INK)
    def_fill = _parse_svg_color(root.attrib.get("fill"), INK) if root.attrib.get("fill") else None
    try:
        def_sw = float(root.attrib.get("stroke-width", "3.2"))
    except Exception:
        def_sw = 3.2

    def _tx(x, y):
        return (x * scale + ox, y * scale + oy)

    def _draw_node(node, p_stroke, p_fill, p_sw):
        tag = node.tag.split("}")[-1].lower()
        st = _parse_svg_color(node.attrib["stroke"], INK) if "stroke" in node.attrib else p_stroke
        fl = _parse_svg_color(node.attrib["fill"], INK) if "fill" in node.attrib else p_fill
        if force_ink_accent and fl is not None and fl == INK:
            fl = force_ink_accent
        try:
            sw = float(node.attrib.get("stroke-width", p_sw))
        except Exception:
            sw = p_sw
        lw = max(14, int(round(sw * scale * 1.15)))

        if tag in ("svg", "g"):
            for ch in node:
                _draw_node(ch, st, fl, sw)
        elif tag == "path":
            for pts, closed in _svg_path_to_polylines(node.attrib.get("d", "")):
                tpts = [_tx(px, py) for px, py in pts]
                if len(tpts) >= 3 and fl is not None and (closed or len(tpts) >= 4):
                    d.polygon(tpts, fill=fl)
                if len(tpts) >= 2 and st is not None:
                    d.line(tpts, fill=st, width=lw, joint="curve")
                    r_cap = max(2, lw // 2 - 1)
                    for end_pt in (tpts[0], tpts[-1]):
                        d.ellipse((end_pt[0] - r_cap, end_pt[1] - r_cap, end_pt[0] + r_cap, end_pt[1] + r_cap), fill=st)
        elif tag == "rect":
            x = float(node.attrib.get("x", 0)); y = float(node.attrib.get("y", 0))
            rw = float(node.attrib.get("width", 0)); rh = float(node.attrib.get("height", 0))
            rx = float(node.attrib.get("rx", 0)) * scale
            p0 = _tx(x, y); p1 = _tx(x + rw, y + rh)
            d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=int(rx), fill=fl, outline=st, width=lw if st else 0)
        elif tag == "circle":
            cx = float(node.attrib.get("cx", 0)); cy = float(node.attrib.get("cy", 0)); r = float(node.attrib.get("r", 0))
            p0 = _tx(cx - r, cy - r); p1 = _tx(cx + r, cy + r)
            d.ellipse((p0[0], p0[1], p1[0], p1[1]), fill=fl, outline=st, width=lw if st else 0)
        elif tag == "ellipse":
            cx = float(node.attrib.get("cx", 0)); cy = float(node.attrib.get("cy", 0))
            rx = float(node.attrib.get("rx", 0)); ry = float(node.attrib.get("ry", 0))
            p0 = _tx(cx - rx, cy - ry); p1 = _tx(cx + rx, cy + ry)
            d.ellipse((p0[0], p0[1], p1[0], p1[1]), fill=fl, outline=st, width=lw if st else 0)
        elif tag == "line":
            p0 = _tx(float(node.attrib.get("x1", 0)), float(node.attrib.get("y1", 0)))
            p1 = _tx(float(node.attrib.get("x2", 0)), float(node.attrib.get("y2", 0)))
            if st is not None:
                d.line([p0, p1], fill=st, width=lw)
        elif tag in ("polygon", "polyline"):
            nums = [float(v) for v in re.findall(r"[-+]?(?:\d*\.\d+|\d+)", node.attrib.get("points", ""))]
            tpts = [_tx(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
            if tag == "polygon" and len(tpts) >= 3:
                d.polygon(tpts, fill=fl, outline=st)
                if st:
                    d.line(tpts + [tpts[0]], fill=st, width=lw, joint="curve")
            elif len(tpts) >= 2 and st:
                d.line(tpts, fill=st, width=lw, joint="curve")

    _draw_node(root, def_stroke, def_fill, def_sw)
    return _normalize_to_512_rgba(im)


MIT_DOODLE_CURATED = [
    ("arrow-right.svg", "editorial_accents", "cc0_doodle_arrow_right", "arrow hand drawn doodle pointer right", (214, 58, 48, 255)),
    ("arrow-left.svg", "editorial_accents", "cc0_doodle_arrow_left", "arrow hand drawn doodle pointer left", (214, 58, 48, 255)),
    ("arrow-up.svg", "editorial_accents", "cc0_doodle_arrow_up", "arrow hand drawn doodle pointer up growth", (38, 152, 86, 255)),
    ("arrow-down.svg", "editorial_accents", "cc0_doodle_arrow_down", "arrow hand drawn doodle pointer down drop", (214, 58, 48, 255)),
    ("arrow-up-right.svg", "editorial_accents", "cc0_doodle_arrow_diag", "arrow hand drawn doodle diagonal trend", (234, 152, 42, 255)),
    ("ban.svg", "editorial_accents", "cc0_doodle_ban_stop", "ban stop reject forbidden myth cross", (214, 58, 48, 255)),
    ("check.svg", "editorial_accents", "cc0_doodle_check_mark", "check hand drawn doodle tick verified", (38, 152, 86, 255)),
    ("sparkles.svg", "editorial_accents", "cc0_doodle_sparkles", "sparkles burst highlight magic accent", (242, 184, 48, 255)),
    ("flame.svg", "nature_animals", "cc0_doodle_flame", "flame fire heat burn energy", (234, 108, 42, 255)),
    ("compass.svg", "modern_daily", "cc0_doodle_compass", "compass navigation map direction", (68, 138, 204, 255)),
    ("lightbulb.svg", "modern_daily", "cc0_doodle_lightbulb", "lightbulb idea epiphany invent", (242, 192, 48, 255)),
    ("lock.svg", "modern_daily", "cc0_doodle_lock", "lock security secret vault", (134, 146, 162, 255)),
    ("archive.svg", "history_ancient", "cc0_doodle_archive", "archive box history files record", (176, 128, 78, 255)),
    ("clock.svg", "money_economy", "cc0_doodle_clock", "clock time era schedule", (68, 138, 204, 255)),
    ("eye.svg", "science_space", "cc0_doodle_eye", "eye vision observe inspect focus", (68, 138, 204, 255)),
    ("zap.svg", "nature_animals", "cc0_doodle_zap", "zap lightning bolt shock energy", (242, 188, 48, 255)),
]

MIT_NAIVE_CURATED = [
    ("abacus.svg", "money_economy", "mit_naive_abacus", "abacus math calculate economy ancient"),
    ("alarm-clock.svg", "modern_daily", "mit_naive_alarm_clock", "alarm clock morning wake routine"),
    ("alert-triangle.svg", "editorial_accents", "mit_naive_alert_triangle", "alert warning danger caution"),
    ("anchor.svg", "history_ancient", "mit_naive_anchor", "anchor ship sea ocean maritime"),
    ("archive.svg", "history_ancient", "mit_naive_archive", "archive history files evidence"),
    ("award.svg", "editorial_accents", "mit_naive_award", "award medal prize winner"),
    ("balance-scale.svg", "money_economy", "mit_naive_balance_scale", "scale justice balance law compare"),
    ("bank.svg", "money_economy", "mit_naive_bank", "bank treasury wealth finance"),
    ("battery-charging.svg", "modern_daily", "mit_naive_battery", "battery power energy charge"),
    ("bell.svg", "modern_daily", "mit_naive_bell", "bell alert ring notification"),
    ("binoculars.svg", "editorial_accents", "mit_naive_binoculars", "binoculars search inspect discover"),
    ("book-open.svg", "modern_daily", "mit_naive_book_open", "book open story knowledge history"),
    ("brain.svg", "science_space", "mit_naive_brain", "brain mind neuroscience think"),
    ("briefcase.svg", "money_economy", "mit_naive_briefcase", "briefcase work business economy"),
    ("cactus.svg", "nature_animals", "mit_naive_cactus", "cactus desert dry climate"),
    ("calendar.svg", "money_economy", "mit_naive_calendar", "calendar date timeline year"),
    ("camera.svg", "modern_daily", "mit_naive_camera", "camera photo evidence archive"),
    ("campfire.svg", "nature_animals", "mit_naive_campfire", "campfire fire night ancient warmth"),
    ("castle.svg", "history_ancient", "mit_naive_castle", "castle fortress medieval empire"),
    ("chart-bar.svg", "money_economy", "mit_naive_chart_bar", "chart bar graph data metric"),
    ("compass.svg", "modern_daily", "mit_naive_compass", "compass navigation map travel"),
    ("cpu.svg", "science_space", "mit_naive_cpu", "cpu chip computer tech"),
    ("crown.svg", "history_ancient", "mit_naive_crown", "crown king emperor ruler"),
    ("dna.svg", "science_space", "mit_naive_dna", "dna genetics evolution biology"),
    ("earth.svg", "science_space", "mit_naive_earth", "earth planet world globe"),
    ("factory.svg", "money_economy", "mit_naive_factory", "factory industry pollution economy"),
    ("feather.svg", "history_ancient", "mit_naive_feather", "feather quill write history"),
    ("fire.svg", "nature_animals", "mit_naive_fire", "fire flame heat burn"),
    ("flag.svg", "editorial_accents", "mit_naive_flag", "flag milestone nation territory"),
    ("flask.svg", "science_space", "mit_naive_flask", "flask lab chemistry science"),
    ("fossil.svg", "history_ancient", "mit_naive_fossil", "fossil ancient relic archaeology"),
    ("gem.svg", "money_economy", "mit_naive_gem", "gem diamond wealth treasure"),
    ("hourglass.svg", "history_ancient", "mit_naive_hourglass", "hourglass time era history"),
    ("house.svg", "modern_daily", "mit_naive_house", "house home village shelter"),
    ("key.svg", "modern_daily", "mit_naive_key", "key unlock secret access"),
    ("leaf.svg", "nature_animals", "mit_naive_leaf", "leaf plant nature ecology"),
    ("lightbulb.svg", "modern_daily", "mit_naive_lightbulb", "lightbulb idea discovery"),
    ("lock.svg", "modern_daily", "mit_naive_lock", "lock security protected"),
    ("map-pin.svg", "editorial_accents", "mit_naive_map_pin", "map pin location place"),
    ("microscope.svg", "science_space", "mit_naive_microscope", "microscope science lab research"),
    ("mountain.svg", "nature_animals", "mit_naive_mountain", "mountain peak terrain"),
    ("newspaper.svg", "modern_daily", "mit_naive_newspaper", "newspaper media headline report"),
    ("planet.svg", "science_space", "mit_naive_planet", "planet space cosmos astronomy"),
    ("pyramid.svg", "history_ancient", "mit_naive_pyramid", "pyramid egypt ancient"),
    ("rocket.svg", "science_space", "mit_naive_rocket", "rocket launch space tech"),
    ("scroll.svg", "history_ancient", "mit_naive_scroll", "scroll parchment archive history"),
    ("shield.svg", "history_ancient", "mit_naive_shield", "shield armor defense war"),
    ("skull.svg", "nature_animals", "mit_naive_skull", "skull bone danger extinct"),
    ("smartphone.svg", "modern_daily", "mit_naive_smartphone", "smartphone phone mobile"),
    ("sun.svg", "science_space", "mit_naive_sun", "sun solar heat energy"),
    ("sword.svg", "history_ancient", "mit_naive_sword", "sword weapon battle history"),
    ("telescope.svg", "science_space", "mit_naive_telescope", "telescope astronomy space look"),
    ("thermometer.svg", "science_space", "mit_naive_thermometer", "thermometer heat cold temperature"),
    ("tree.svg", "nature_animals", "mit_naive_tree", "tree forest wood nature"),
    ("trophy.svg", "editorial_accents", "mit_naive_trophy", "trophy victory award"),
    ("volcano.svg", "nature_animals", "mit_naive_volcano", "volcano eruption catastrophe"),
    ("wheat.svg", "nature_animals", "mit_naive_wheat", "wheat grain crop harvest"),
    ("wrench.svg", "modern_daily", "mit_naive_wrench", "wrench tool repair build"),
]

KENNEY_CARTOGRAPHY_CURATED = [
    ("2d/Cartography%20Pack/Retina/arrowCorner.png", "editorial_accents", "cc0_carto_arrow_corner", "arrow corner map direction route"),
    ("2d/Cartography%20Pack/Retina/arrowHead.png", "editorial_accents", "cc0_carto_arrow_head", "arrow head pointer map"),
    ("2d/Cartography%20Pack/Retina/arrowSplit.png", "editorial_accents", "cc0_carto_arrow_split", "arrow split choice diverge path"),
    ("2d/Cartography%20Pack/Retina/arrowStraight.png", "editorial_accents", "cc0_carto_arrow_straight", "arrow straight pointer"),
    ("2d/Cartography%20Pack/Retina/banner.png", "editorial_accents", "cc0_carto_banner", "banner ribbon callout header"),
    ("2d/Cartography%20Pack/Retina/bridge.png", "history_ancient", "cc0_carto_bridge", "bridge crossing river connection"),
    ("2d/Cartography%20Pack/Retina/campfire.png", "nature_animals", "cc0_carto_campfire", "campfire fire camp ancient"),
    ("2d/Cartography%20Pack/Retina/castle.png", "history_ancient", "cc0_carto_castle", "castle fort kingdom empire"),
    ("2d/Cartography%20Pack/Retina/chest.png", "money_economy", "cc0_carto_chest", "chest treasure loot gold"),
    ("2d/Cartography%20Pack/Retina/compass.png", "modern_daily", "cc0_carto_compass", "compass navigation north map"),
    ("2d/Cartography%20Pack/Retina/flag.png", "editorial_accents", "cc0_carto_flag", "flag marker milestone territory"),
    ("2d/Cartography%20Pack/Retina/lighthouse.png", "history_ancient", "cc0_carto_lighthouse", "lighthouse coast beacon signal"),
    ("2d/Cartography%20Pack/Retina/mine.png", "money_economy", "cc0_carto_mine", "mine ore tin copper resource"),
    ("2d/Cartography%20Pack/Retina/pyramid.png", "history_ancient", "cc0_carto_pyramid", "pyramid egypt ancient monument"),
    ("2d/Cartography%20Pack/Retina/rocksMountain.png", "nature_animals", "cc0_carto_mountain", "mountain rocks terrain barrier"),
    ("2d/Cartography%20Pack/Retina/runis.png", "history_ancient", "cc0_carto_ruins", "ruins collapse ancient broken"),
    ("2d/Cartography%20Pack/Retina/ship.png", "history_ancient", "cc0_carto_ship", "ship sailing vessel trade sea"),
    ("2d/Cartography%20Pack/Retina/skull.png", "nature_animals", "cc0_carto_skull", "skull danger extinct death"),
    ("2d/Cartography%20Pack/Retina/towerWatch.png", "history_ancient", "cc0_carto_watchtower", "watchtower lookout guard defense"),
    ("2d/Cartography%20Pack/Retina/vulcano.png", "nature_animals", "cc0_carto_volcano", "volcano eruption disaster"),
]


def fetch_mit_svg_collections():
    """Downloads curated MIT-licensed hand-drawn SVGs (doodle-icons + naive-icons) and rasterizes them cleanly."""
    fetched = []
    # 1. doodle-icons (MIT)
    for fname, cat, slug, tags, ink_col in MIT_DOODLE_CURATED:
        out_dir = os.path.join(CC0_ROOT, cat)
        os.makedirs(out_dir, exist_ok=True)
        out_p = os.path.join(out_dir, f"{slug}.png")
        meta_p = os.path.join(out_dir, f"{slug}.meta.json")
        if os.path.exists(out_p) and os.path.getsize(out_p) > 500 and os.path.exists(meta_p):
            fetched.append(out_p)
            continue
        url = f"https://raw.githubusercontent.com/oreo-design/doodle-icons/main/icons/{fname}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "StickmanStickers/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                svg_txt = r.read().decode("utf-8", errors="ignore")
            im512 = _rasterize_svg_to_512_rgba(svg_txt, force_ink_accent=ink_col)
            if im512:
                im512.save(out_p)
                ok, _, _ = index_stickers.inspect_png_alpha(out_p)
                if ok:
                    with open(meta_p, "w", encoding="utf-8") as mf:
                        json.dump({"tags": tags, "category": cat, "source": "cc0_library", "license": "MIT", "origin": "oreo-design/doodle-icons (MIT)", "url": url}, mf, indent=2)
                    fetched.append(out_p)
                else:
                    os.remove(out_p)
        except Exception:
            continue

    # 2. naive-icons (MIT, flat editorial fill + #2A2A2A ink outline)
    for fname, cat, slug, tags in MIT_NAIVE_CURATED:
        out_dir = os.path.join(CC0_ROOT, cat)
        os.makedirs(out_dir, exist_ok=True)
        out_p = os.path.join(out_dir, f"{slug}.png")
        meta_p = os.path.join(out_dir, f"{slug}.meta.json")
        if os.path.exists(out_p) and os.path.getsize(out_p) > 500 and os.path.exists(meta_p):
            fetched.append(out_p)
            continue
        url = f"https://raw.githubusercontent.com/guokaigdg/naive-icons/main/svg/{fname}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "StickmanStickers/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                svg_txt = r.read().decode("utf-8", errors="ignore")
            im512 = _rasterize_svg_to_512_rgba(svg_txt)
            if im512:
                im512.save(out_p)
                ok, _, _ = index_stickers.inspect_png_alpha(out_p)
                if ok:
                    with open(meta_p, "w", encoding="utf-8") as mf:
                        json.dump({"tags": tags, "category": cat, "source": "cc0_library", "license": "MIT", "origin": "guokaigdg/naive-icons (MIT)", "url": url}, mf, indent=2)
                    fetched.append(out_p)
                else:
                    os.remove(out_p)
        except Exception:
            continue
    return fetched


def fetch_kenney_cartography_sprites():
    """Downloads curated Kenney CC0-1.0 Cartography 2D sprites and normalizes to 512x512 RGBA."""
    fetched = []
    base_raw = "https://raw.githubusercontent.com/shorepine/kenney/master/"
    for subpath, cat, slug, tags in KENNEY_CARTOGRAPHY_CURATED:
        out_dir = os.path.join(CC0_ROOT, cat)
        os.makedirs(out_dir, exist_ok=True)
        out_p = os.path.join(out_dir, f"{slug}.png")
        meta_p = os.path.join(out_dir, f"{slug}.meta.json")
        if os.path.exists(out_p) and os.path.getsize(out_p) > 500 and os.path.exists(meta_p):
            fetched.append(out_p)
            continue
        url = base_raw + subpath
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "StickmanStickers/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                im = Image.open(BytesIO(r.read()))
            norm = _normalize_to_512_rgba(im)
            if norm:
                norm.save(out_p)
                ok, _, _ = index_stickers.inspect_png_alpha(out_p)
                if ok:
                    with open(meta_p, "w", encoding="utf-8") as mf:
                        json.dump({"tags": tags, "category": cat, "source": "cc0_library", "license": "CC0-1.0", "origin": "Kenney Cartography CC0", "url": url}, mf, indent=2)
                    fetched.append(out_p)
                else:
                    os.remove(out_p)
        except Exception:
            continue
    return fetched


def main():
    parser = argparse.ArgumentParser(description="Fetch / build 100% CC0 / MIT-open 2D stickers and update CATALOG.tsv")
    parser.add_argument("--online", action="store_true", help="Download curated Kenney CC0, MIT Doodle/Naive SVGs & Wikimedia CC0 props")
    parser.add_argument("--query", default=None, help="Optional Wikimedia CC0 search query")
    parser.add_argument("--category", default="history_ancient", choices=list(index_stickers.CATEGORIES))
    args = parser.parse_args()

    created = build_cc0_cartoon_library()
    if args.online:
        k_icons = fetch_kenney_cc0_icons()
        k_carto = fetch_kenney_cartography_sprites()
        m_svgs = fetch_mit_svg_collections()
        created.extend(k_icons + k_carto + m_svgs)
        print(f"Kenney CC0 icons: {len(k_icons)} | Kenney Cartography CC0: {len(k_carto)} | MIT Hand-Drawn SVGs: {len(m_svgs)}")
    if args.query:
        res = try_fetch_wikimedia_cc0(args.query, args.category, f"cc0_wiki_{args.query.replace(' ', '_')}")
        if res:
            created.append(res)
            print(f"Downloaded verified CC0 Wikimedia sticker -> {res}")

    rows = index_stickers.rebuild_catalog()
    print(f"CC0/MIT library ready ({len(created)} assets ensured). Total catalog rows: {len(rows)}.")


if __name__ == "__main__":
    main()
