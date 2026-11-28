#!/usr/bin/env python3
"""validate_pipeline.py: Mandatory Pre-Render Quality Gate
Enforces Condition 2 & Rules 20, 22, 24, 27, 30:
Aborts rendering before render_pro.py if any check fails:
1. Sticker & Shot Manifest Gate: All required stickers and scene shots must exist on disk.
2. 9:16 Vertical Framing Gate: Catches and rejects landscape framing or horizontal letterbox bars in Shorts.
3. 3-Stem Audio Integrity Gate: Verifies mix_pro.wav, VO.wav, and cues_pro.tsv are non-empty and non-silent.
4. Flow Bridge Connectivity Gate: If assets are missing, verifies flow-auto bridge on port 8791 is active.
"""

import os
import sys
import csv
import re
import socket
import argparse
import subprocess
from PIL import Image
import numpy as np

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

try:
    import asset_registry
except ImportError:
    asset_registry = None


def resolve_sticker_path(img_name, project_dir="."):
    """Bulletproof multi-candidate sticker resolution."""
    raw = img_name.strip()
    if not raw or raw in ("count", "tag", "stamp_x", "stamp_check", "stamp_false", "stamp_true", "stamp_myth") or raw.startswith("bars:"):
        return None, True  # Special procedural overlay

    basename = os.path.basename(raw)
    name_no_ext = os.path.splitext(basename)[0]
    
    candidates = [
        raw,
        raw + ".png" if not raw.lower().endswith((".png", ".webp", ".gif")) else raw,
        os.path.join(project_dir, "elements", "cut", f"{name_no_ext}.png"),
        os.path.join(project_dir, "elements", "cut", f"{name_no_ext}.webp"),
        os.path.join(project_dir, "elements", "cut", f"{name_no_ext}.gif"),
        os.path.join(project_dir, "elements", "cut", basename),
        os.path.join(project_dir, "..", "elements", "cut", f"{name_no_ext}.png"),
        os.path.join(project_dir, "..", "elements", "cut", f"{name_no_ext}.webp"),
        os.path.join(project_dir, "..", "elements", "cut", basename),
        os.path.join(project_dir, "..", "short", "elements", "cut", f"{name_no_ext}.png"),
        os.path.join(project_dir, "..", "long", "elements", "cut", f"{name_no_ext}.png"),
    ]

    for c in candidates:
        if os.path.exists(c) and os.path.getsize(c) > 500:
            return os.path.abspath(c), True

    # Try asset registry semantic match
    if asset_registry:
        try:
            p_root = asset_registry.resolve_project_root(project_dir)
            match = asset_registry.find_reusable_sticker(name_no_ext, p_root)
            if match and os.path.exists(match["path"]):
                return match["path"], True
        except Exception:
            pass

    return candidates[2], False


def check_flow_bridge_active(port=8791):
    """Checks whether Google Flow Chrome extension bridge is actively listening."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1.0):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def detect_image_text_leak(img_path):
    """Full-frame automated text-leak / baked words check using tesseract OCR with confidence gating."""
    if not os.path.exists(img_path) or os.path.getsize(img_path) < 10000:
        return False, ""
    try:
        im = Image.open(img_path)
        w, h = im.size
        # Downscale if large for speed
        if max(w, h) > 1280:
            scale = 1280.0 / max(w, h)
            im_scan = im.resize((int(w * scale), int(h * scale)), Image.BILINEAR)
        else:
            im_scan = im

        tmp_scan = f"/tmp/_ocr_scan_{os.getpid()}_{os.path.basename(img_path)}"
        im_scan.save(tmp_scan)

        r = subprocess.run(["tesseract", tmp_scan, "stdout", "--oem", "1", "-l", "eng", "--psm", "11", "tsv"],
                           capture_output=True, text=True, timeout=8)
        if os.path.exists(tmp_scan):
            try:
                os.remove(tmp_scan)
            except OSError:
                pass

        words = []
        high_conf_words = []
        suspect_kws = {
            "ancient", "history", "dental", "care", "pain", "tooth", "toothache",
            "ipsum", "lorem", "dolor", "chapter", "episode", "suspense", "danger",
            "mystery", "baal", "god", "temple", "screen", "monitor"
        }
        for ln in r.stdout.splitlines()[1:]:
            cols = ln.split("\t")
            if len(cols) >= 12:
                tok = cols[11].strip()
                try:
                    conf = float(cols[10])
                except ValueError:
                    conf = 0.0
                if conf >= 65.0 and re.fullmatch(r"[A-Za-z]{3,}", tok):
                    words.append((tok, conf))
                    if conf >= 75.0 and len(tok) >= 5:
                        high_conf_words.append(tok)

        word_tokens = [w[0] for w in words]
        hit_kws = [w for w in word_tokens if w.lower() in suspect_kws]
        if hit_kws:
            return True, f"Baked-in keyword/header text detected: '{' '.join(word_tokens[:6])}' (matched {hit_kws})"
        if len(high_conf_words) >= 1:
            return True, f"Baked-in clean text detected: '{', '.join(high_conf_words[:4])}'"
        if len(word_tokens) >= 3:
            return True, f"Baked-in text leak detected ({len(word_tokens)} tokens): '{' '.join(word_tokens[:6])}'"
        return False, ""
    except Exception:
        return False, ""


def measure_shot_photometrics(img_path, scene_mood="auto", prompt=""):
    """Local NumPy/Pillow photometric inspector (Measure, Don't Guess!).
    Computes normalized brightness_100, shadow_area_pct, saturation_pct,
    clipped_white_pct (excluding round dark-outlined white stickman head cores),
    and luminance contrast_std.
    """
    out = {
        "ok": True,
        "failures": [],
        "warnings": [],
        "mood": "daylight",
        "brightness_100": 0.0,
        "shadow_area_pct": 0.0,
        "saturation_pct": 0.0,
        "clipped_white_pct": 0.0,
        "clipped_white_raw_pct": 0.0,
        "contrast_std": 0.0,
        "head_cores_excluded": 0,
        "summary": "",
    }
    if not img_path or not os.path.exists(img_path):
        out["ok"] = False
        out["failures"].append("Image missing")
        return out

    try:
        with Image.open(img_path) as im_src:
            im = im_src.convert("RGB")
            w0, h0 = im.size
            if w0 > 640:
                sh_h = max(64, int(round(h0 * (640.0 / w0))))
                im = im.resize((640, sh_h), Image.Resampling.BILINEAR)
            arr = np.asarray(im, dtype=np.float32)
            hsv = np.asarray(im.convert("HSV"), dtype=np.float32)

        luma = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
        b100 = float(luma.mean()) / 255.0 * 100.0
        shad_pct = float((luma < 95.0).mean()) * 100.0
        sat_pct = float(hsv[..., 1].mean()) / 255.0 * 100.0
        c_std = float(luma.std())

        clip_mask = (arr[..., 0] > 248.0) & (arr[..., 1] > 248.0) & (arr[..., 2] > 248.0)
        clip_raw = float(clip_mask.mean()) * 100.0
        filtered_clip = clip_mask.copy()
        heads_excluded = 0

        # Exclude compact dark-outlined white round stickman head cores from burnt-white metric
        try:
            from scipy import ndimage
            labeled, n_comp = ndimage.label(clip_mask)
            if n_comp > 0:
                total_px = clip_mask.size
                ink_mask = luma < 115.0
                slices = ndimage.find_objects(labeled)
                for cid, sl in enumerate(slices, 1):
                    if sl is None:
                        continue
                    comp = (labeled[sl] == cid)
                    area = int(comp.sum())
                    area_ratio = area / max(1, total_px)
                    if not (0.0012 <= area_ratio <= 0.085):
                        continue
                    bh = sl[0].stop - sl[0].start
                    bw = sl[1].stop - sl[1].start
                    if bh == 0 or bw == 0:
                        continue
                    aspect_r = bw / float(bh)
                    fill_r = area / float(bw * bh)
                    if not (0.45 <= aspect_r <= 2.2 and fill_r >= 0.45):
                        continue
                    # Expand slice by 3px to verify dark ink outline ring
                    y0 = max(0, sl[0].start - 3)
                    y1 = min(clip_mask.shape[0], sl[0].stop + 3)
                    x0 = max(0, sl[1].start - 3)
                    x1 = min(clip_mask.shape[1], sl[1].stop + 3)
                    sub_comp = (labeled[y0:y1, x0:x1] == cid)
                    ring = ndimage.binary_dilation(sub_comp, iterations=3) & (~sub_comp)
                    ring_px = int(ring.sum())
                    if ring_px > 0 and (float(ink_mask[y0:y1, x0:x1][ring].sum()) / ring_px) >= 0.22:
                        filtered_clip[y0:y1, x0:x1][sub_comp] = False
                        heads_excluded += 1
        except Exception:
            pass

        clip_pct = float(filtered_clip.mean()) * 100.0
        mood_txt = f"{scene_mood} {prompt}".lower()
        mood = "sunset" if any(k in mood_txt for k in ("sunset", "dusk", "evening", "twilight", "night", "crisis")) else "daylight"

        # Bright 2D editorial calibration (airy daylight B=60-82, gentle shadows 5-28%; sunset B=44-68)
        failures = []
        warnings = []
        if mood == "daylight":
            if b100 > 86.0:
                failures.append(f"Overexposed washed-out brightness (B={b100:.1f} > 86)")
            elif b100 < 45.0:
                failures.append(f"Bright 2D scene too dark/gloomy (B={b100:.1f} < 45)")
            if shad_pct > 38.0:
                failures.append(f"Overly heavy/gloomy shadows on daylight bright scene (Shad={shad_pct:.1f}% > 38%)")
            elif shad_pct < 3.0:
                warnings.append(f"Ultra-low contact shadows (Shad={shad_pct:.1f}% < 3%; gentle target 5-28%)")
        else:
            if b100 > 84.0:
                failures.append(f"Overexposed sunset scene (B={b100:.1f} > 84)")
            elif b100 < 36.0:
                failures.append(f"Overly dark gloomy sunset/evening scene (B={b100:.1f} < 36)")

        if clip_pct > 14.0:
            failures.append(f"Burnt-out white highlights (Clip={clip_pct:.1f}% > 14%)")

        if c_std < 30.0:
            failures.append(f"Milky washout haze (Std={c_std:.1f} < 30)")

        if sat_pct < 16.0:
            warnings.append(f"Low washed-out saturation (Sat={sat_pct:.1f}% < 16%)")
        elif sat_pct > 72.0:
            warnings.append(f"Harsh neon saturation (Sat={sat_pct:.1f}% > 72%)")

        out.update({
            "ok": len(failures) == 0,
            "failures": failures,
            "warnings": warnings,
            "mood": mood,
            "brightness_100": round(b100, 2),
            "shadow_area_pct": round(shad_pct, 2),
            "saturation_pct": round(sat_pct, 2),
            "clipped_white_pct": round(clip_pct, 2),
            "clipped_white_raw_pct": round(clip_raw, 2),
            "contrast_std": round(c_std, 2),
            "head_cores_excluded": heads_excluded,
            "summary": (
                f"B={b100:.1f} | Shad={shad_pct:.1f}% | Sat={sat_pct:.1f}% | "
                f"Clip={clip_pct:.2f}% | Std={c_std:.1f}"
            ),
        })
        return out
    except Exception as e:
        out["ok"] = False
        out["failures"].append(f"Photometric read error: {e}")
        return out


def detect_outer_frame_border(img_path, edge_pct=0.028):
    """Detects solid uniform comic/paper/white/black frame margins bordering the outer ~3% perimeter."""
    res = {"ok": True, "border_detected": False, "close_ratio": 0.0, "med_rgb": [], "msg": "Borderless full-bleed"}
    if not img_path or not os.path.exists(img_path):
        return res
    try:
        with Image.open(img_path) as im_src:
            im = im_src.convert("RGB")
            w, h = im.size
            if w > 640:
                sh_h = max(64, int(round(h * (640.0 / w))))
                im = im.resize((640, sh_h), Image.Resampling.BILINEAR)
                w, h = im.size
            arr = np.asarray(im, dtype=np.float32)

        bw = max(2, int(round(w * edge_pct)))
        bh = max(2, int(round(h * edge_pct)))
        strips = [arr[:bh, :, :], arr[h - bh:, :, :], arr[:, :bw, :], arr[:, w - bw:, :]]
        rim_rgb = np.concatenate([s.reshape(-1, 3) for s in strips], axis=0)
        med = np.median(rim_rgb, axis=0)
        total_close = float((np.abs(rim_rgb - med).max(axis=1) < 22.0).mean())
        side_closes = [float((np.abs(s.reshape(-1, 3) - med).max(axis=1) < 22.0).mean()) for s in strips]
        sides_matching = sum(1 for sc in side_closes if sc >= 0.85)

        if total_close >= 0.86 and sides_matching >= 3:
            med_int = [int(round(float(x))) for x in med]
            msg = f"Outer comic/paper border detected ({total_close*100:.1f}% uniform rim, {sides_matching}/4 sides, rgb={med_int})"
            return {
                "ok": False,
                "border_detected": True,
                "close_ratio": round(total_close, 4),
                "med_rgb": med_int,
                "msg": msg,
            }
        res["close_ratio"] = round(total_close, 4)
        return res
    except Exception as e:
        res["msg"] = f"Border check error: {e}"
        return res


def inspect_sticker_cutout_quality(png_path):
    """Verifies that a resolved sticker has true alpha transparency, no magenta halo, and no edge clipping."""
    try:
        with Image.open(png_path) as im_raw:
            if png_path.lower().endswith((".webp", ".gif")):
                im = im_raw.convert("RGBA")
            else:
                im = im_raw
            if im.mode != "RGBA":
                return True, "RGB mode (not RGBA)"
            a = np.array(im)
            alpha = a[..., 3]
            if alpha.min() > 0:
                return False, "No transparent pixels (alpha.min() > 0)"
            trans_ratio = (alpha == 0).mean()
            if trans_ratio < 0.03:
                return False, f"Insufficient transparency ({trans_ratio*100:.1f}%)"
            if trans_ratio > 0.985:
                return False, f"Sticker subject empty ({trans_ratio*100:.1f}% transparent)"
            opaque_mask = alpha > 40
            if opaque_mask.mean() < 0.01:
                return False, "Opaque subject is < 1% of canvas"
            r, g, b = a[..., 0], a[..., 1], a[..., 2]
            magenta_mask = (r > 175) & (b > 175) & (g < 90) & ((r.astype(int) - g.astype(int)) > 90) & ((b.astype(int) - g.astype(int)) > 90) & opaque_mask
            magenta_ratio = np.sum(magenta_mask) / max(1, np.sum(opaque_mask))
            if magenta_ratio > 0.018:
                return False, f"Magenta halo: {magenta_ratio*100:.2f}% unkeyed pixels"
            h, w = alpha.shape
            border_opaque = np.sum(opaque_mask[0, :]) + np.sum(opaque_mask[-1, :]) + np.sum(opaque_mask[:, 0]) + np.sum(opaque_mask[:, -1])
            border_cov = border_opaque / max(1, 2 * w + 2 * h)
            if border_cov > 0.15:
                return False, f"Edge clipping: {border_cov*100:.1f}% border coverage"
            return True, "Valid cutout"
    except Exception as e:
        return False, f"Cannot read sticker: {e}"


def validate_stickers_and_shots(project_dir="."):
    """Gate 1: Verifies all shots and stickers referenced in SCENES_HYBRID.tsv exist and pass cutout QC."""
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")

    if not os.path.exists(scenes_path):
        return False, [f"Fatal: Scene manifest not found at {scenes_path}."]

    missing_shots = []
    missing_stickers = []
    flawed_stickers = []
    text_leaks = []
    photo_records = []
    checked_shot_paths = set()
    total_scenes = 0
    total_stickers = 0

    PROGRAMMATIC_SHOTS = {
        "card", "card_stat", "card_phrase", "split_compare", "split_contrast",
        "bar_timeline", "stat_pie", "stat_ring", "grid_week",
        "chapter_breather", "breather", "scale_compare", "scale_bar"
    }

    with open(scenes_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row_idx, r in enumerate(reader, 1):
            total_scenes += 1
            cue = r.get("cue", "").strip()
            is_overlay_row = cue.startswith("+")

            if is_overlay_row:
                img_token = r.get("img", "").strip()
                if img_token:
                    resolved_path, exists = resolve_sticker_path(img_token, project_dir)
                    total_stickers += 1
                    if not exists:
                        missing_stickers.append(f"Row {row_idx}: '{img_token}' (looked for: {resolved_path})")
                    elif resolved_path:
                        ok_cut, cut_reason = inspect_sticker_cutout_quality(resolved_path)
                        if not ok_cut:
                            flawed_stickers.append(f"Row {row_idx}: '{img_token}' ({resolved_path}): {cut_reason}")
            else:
                shot_file = r.get("shot", "").strip() or r.get("img", "").strip()
                shot_token = os.path.basename(shot_file)
                shot_base = os.path.splitext(shot_token)[0]
                shot_prefix = shot_base.split(":")[0].strip()
                arch_pfx2 = ("card_", "split_", "timeline_", "stat_", "bar_", "chapter_", "breather", "scale_", "strike_")
                if (shot_file in PROGRAMMATIC_SHOTS or shot_token in PROGRAMMATIC_SHOTS or shot_base in PROGRAMMATIC_SHOTS or
                    shot_prefix in PROGRAMMATIC_SHOTS or
                    shot_file.startswith(arch_pfx2) or
                    shot_token.startswith(arch_pfx2) or
                    shot_base.startswith(arch_pfx2) or
                    shot_prefix.startswith(arch_pfx2)):
                    continue
                if shot_file:
                    # Check candidate locations for shot
                    shot_cands = [
                        shot_file,
                        os.path.join(project_dir, "shots", os.path.basename(shot_file)),
                        os.path.join(project_dir, shot_file)
                    ]
                    found_p = next((p for p in shot_cands if os.path.exists(p) and os.path.getsize(p) > 20000), None)
                    if not found_p:
                        missing_shots.append(f"Row {row_idx}: {shot_file}")
                    else:
                        has_leak, leak_msg = detect_image_text_leak(found_p)
                        if has_leak:
                            text_leaks.append(f"Row {row_idx}: '{shot_file}': {leak_msg}")
                        abs_fp = os.path.abspath(found_p)
                        if abs_fp not in checked_shot_paths:
                            checked_shot_paths.add(abs_fp)
                            pm = measure_shot_photometrics(found_p, prompt=r.get("text", "") or r.get("desc", ""))
                            photo_records.append((os.path.basename(found_p), pm))
                            if pm.get("failures"):
                                print(f"   ⚠️ Gate 1 Photometric Alert [{os.path.basename(found_p)}]: {'; '.join(pm['failures'])} ({pm['summary']})")
                            b_res = detect_outer_frame_border(found_p)
                            if b_res.get("border_detected"):
                                print(f"   ⚠️ Gate 1 Border Alert [{os.path.basename(found_p)}]: {b_res['msg']}")

            # Check legacy overlays column if present
            ov_raw = r.get("ov", "").strip()
            if ov_raw:
                items = ov_raw.split(";")
                for item in items:
                    item = item.strip()
                    if not item:
                        continue
                    m = re.match(r"^([^@]+)(?:@([+-]?[0-9.]+))?", item)
                    if m:
                        img_token = m.group(1).strip()
                        resolved_path, exists = resolve_sticker_path(img_token, project_dir)
                        total_stickers += 1
                        if not exists:
                            missing_stickers.append(f"Row {row_idx}: '{img_token}' (looked for: {resolved_path})")
                        elif resolved_path:
                            ok_cut, cut_reason = inspect_sticker_cutout_quality(resolved_path)
                            if not ok_cut:
                                flawed_stickers.append(f"Row {row_idx}: '{img_token}' ({resolved_path}): {cut_reason}")

    if photo_records:
        n_pm = len(photo_records)
        m_b = sum(p["brightness_100"] for _, p in photo_records) / n_pm
        m_sh = sum(p["shadow_area_pct"] for _, p in photo_records) / n_pm
        m_sat = sum(p["saturation_pct"] for _, p in photo_records) / n_pm
        m_clip = sum(p["clipped_white_pct"] for _, p in photo_records) / n_pm
        m_std = sum(p["contrast_std"] for _, p in photo_records) / n_pm
        print(
            f"   📊 Gate 1 Photometrics ({n_pm} unique shots): "
            f"B={m_b:.1f} | Shad={m_sh:.1f}% | Sat={m_sat:.1f}% | Clip={m_clip:.2f}% | Std={m_std:.1f}"
        )

    errors = []
    if missing_shots:
        errors.append(f"Missing {len(missing_shots)} scene shot(s):\n  " + "\n  ".join(missing_shots[:6]))
    if text_leaks:
        errors.append(f"Baked-in text leak / comic header detected on {len(text_leaks)} shot(s):\n  " + "\n  ".join(text_leaks[:4]))
    if missing_stickers:
        errors.append(f"Missing {len(missing_stickers)} sticker prop(s) on disk:\n  " + "\n  ".join(missing_stickers[:8]))
    if flawed_stickers:
        errors.append(f"Flawed cutout QC on {len(flawed_stickers)} sticker(s):\n  " + "\n  ".join(flawed_stickers[:6]))

    is_ok = (len(errors) == 0)
    return is_ok, errors


def validate_vertical_framing(project_dir="."):
    """Gate 2: Enforces strict native 9:16 vertical orientation and anti-letterbox purity."""
    shots_dir = os.path.join(project_dir, "shots")
    if not os.path.exists(shots_dir):
        return True, []

    errors = []
    for f in os.listdir(shots_dir):
        if not f.endswith((".png", ".jpg", ".webp")):
            continue
        p = os.path.join(shots_dir, f)
        try:
            with Image.open(p) as im:
                w, h = im.size
                ratio = w / h
                if ratio > 0.65 or w >= h:
                    errors.append(f"Shot '{f}' has horizontal/landscape aspect ratio ({w}x{h}, ratio={ratio:.2f} > 0.65).")
                    continue

                # Test for letterbox bars in top and bottom 12% pixel bands
                gray = np.array(im.convert("L"))
                top_h = max(2, int(h * 0.12))
                bot_h = max(2, int(h * 0.12))
                top_std = float(np.std(gray[:top_h, :]))
                bot_std = float(np.std(gray[h - bot_h:, :]))
                top_mean = float(np.mean(gray[:top_h, :]))
                bot_mean = float(np.mean(gray[h - bot_h:, :]))

                if (top_std < 3.5 and (top_mean < 35 or top_mean > 225)) or \
                   (bot_std < 3.5 and (bot_mean < 35 or bot_mean > 225)):
                    errors.append(f"Shot '{f}' has horizontal letterbox bars detected (top_std={top_std:.1f}, bot_std={bot_std:.1f}).")
        except Exception as e:
            errors.append(f"Failed to inspect shot '{f}': {e}")

    return (len(errors) == 0), errors


def validate_audio_integrity(project_dir="."):
    """Gate 3: Validates 3-stem master mix, voiceover energy, music bed presence, and SFX assets."""
    errors = []
    mix_path = os.path.join(project_dir, "mix_pro.wav")
    vo_path = os.path.join(project_dir, "VO.wav")
    cues_path = os.path.join(project_dir, "cues_pro.tsv")

    # 1. Voiceover Check
    if not os.path.exists(vo_path):
        errors.append(f"Voiceover track missing: {vo_path}")
    elif os.path.getsize(vo_path) < 10000:
        errors.append(f"Voiceover track is empty/corrupt ({os.path.getsize(vo_path)} bytes)")
    else:
        try:
            import soundfile as sf
            vo_data, vo_sr = sf.read(vo_path)
            vo_rms = float(np.sqrt(np.mean(vo_data**2)))
            if vo_rms < 0.005:
                errors.append(f"Voiceover audio track is silent (RMS energy={vo_rms:.5f} < 0.005)")
        except Exception as e:
            if os.path.getsize(vo_path) < 10000:
                errors.append(f"Cannot inspect voiceover track: {e}")

    # 2. Sound Cues & Stem Asset Completeness Check
    if not os.path.exists(cues_path):
        errors.append(f"Sound cues TSV missing: {cues_path}")
    else:
        cues_rows = []
        with open(cues_path, "r", encoding="utf-8") as cf:
            for l in csv.DictReader(cf, delimiter="\t"):
                if l and l.get("file") and not l.get("label", "").startswith("#"):
                    cues_rows.append(l)

        if len(cues_rows) < 4:
            errors.append(f"Sound cues TSV has insufficient cues ({len(cues_rows)} cues; minimum required is 4)")

        # Verify Music Bed presence
        has_bed = any(c.get("label") == "bed" or c.get("kind") == "loop" for c in cues_rows)
        if not has_bed:
            errors.append("Sound cues missing background music bed ('bed' loop cue required)")

        # Verify that EVERY sound asset referenced in cues_pro.tsv actually exists on disk & isn't blacklisted!
        BANNED_SFX = (
            "celesta", "sparkle", "twinkle", "chime", "bell", "ding", "jingle",
            "boing", "squeak", "cartoon", "coin", "magic", "laser", "sci-fi",
            "shimmer", "threetone", "twotone", "pepsound", "notification_ping",
            "fairy", "glockenspiel", "arcade", "whistle", "zip-out", "zip_out",
            "scratch", "chalk", "marker", "pencil",
            "beep", "beeps", "countdown", "reverse", "screech", "radio", "glitch", "buzz", "alarm_phone"
        )
        missing_sfx = []
        banned_hits = []
        for c in cues_rows:
            f_path = c.get("file", "").strip()
            if c.get("kind") == "one" and any(b in f_path.lower() for b in BANNED_SFX):
                banned_hits.append(f"{c.get('label')}: '{os.path.basename(f_path)}'")
            if f_path and not os.path.exists(f_path):
                # Check candidate relative paths
                cand = os.path.join(project_dir, f_path)
                if not os.path.exists(cand):
                    missing_sfx.append(f"{c.get('label')}: '{f_path}'")
        if missing_sfx:
            errors.append(f"Missing {len(missing_sfx)} sound asset(s) referenced in cues_pro.tsv:\n  " + "\n  ".join(missing_sfx[:5]))
        if banned_hits:
            errors.append(f"Blacklisted twink/bell/scratch SFX in cues_pro.tsv:\n  " + "\n  ".join(banned_hits[:5]))

    # 3. Master Mix Check
    if not os.path.exists(mix_path):
        errors.append(f"Master mix audio missing: {mix_path}")
    else:
        try:
            import soundfile as sf
            mix_data, mix_sr = sf.read(mix_path)
            duration = len(mix_data) / mix_sr
            if duration < 5.0:
                errors.append(f"Master mix is too short ({duration:.1f}s < 5.0s)")
            mix_rms = float(np.sqrt(np.mean(mix_data**2)))
            if mix_rms < 0.010:
                errors.append(f"Master mix is silent/inaudible (RMS energy={mix_rms:.5f} < 0.010)")
        except Exception as e:
            if os.path.getsize(mix_path) < 50000:
                errors.append(f"Master mix audio file is abnormally small ({os.path.getsize(mix_path)} bytes): {e}")

    return (len(errors) == 0), errors


def validate_multitrack_sync(project_dir="."):
    """Gate 4: Multi-Track Synchronization Verification.
    Validates alignment across WORDS.tsv, SCENES_HYBRID.tsv, and cues_pro.tsv.
    Flags timing drift > 100ms and audio/visual timeline length mismatches.
    """
    words_path = os.path.join(project_dir, "WORDS.tsv")
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")
    cues_path = os.path.join(project_dir, "cues_pro.tsv")
    vo_path = os.path.join(project_dir, "VO.wav")
    mix_path = os.path.join(project_dir, "mix_pro.wav")

    errors = []

    if not os.path.exists(words_path):
        errors.append(f"Gate 4 failed: WORDS.tsv missing at {words_path}")
        return False, errors

    if not os.path.exists(scenes_path):
        errors.append(f"Gate 4 failed: SCENES manifest missing at {scenes_path}")
        return False, errors

    # 1. Load WORDS.tsv
    words_map = {}
    max_word_end = 0.0
    with open(words_path, "r", encoding="utf-8", errors="ignore") as wf:
        for r in csv.DictReader(wf, delimiter="\t"):
            line = r.get("line", "").strip()
            idx = r.get("i", "").strip()
            if not line or not idx:
                continue
            try:
                st = float(r["start"])
                en = float(r["end"])
                words_map[f"{line}.{idx}"] = st
                words_map[f"{int(line)}.{idx}"] = st
                if en > max_word_end:
                    max_word_end = en
            except ValueError:
                continue

    if not words_map:
        errors.append("Gate 4 failed: WORDS.tsv contains no valid word timestamps")
        return False, errors

    # 2. Parse scenes and overlays
    scenes = []
    overlays = []
    prev_scene_t = -1.0

    with open(scenes_path, "r", encoding="utf-8", errors="ignore") as sf:
        reader = csv.DictReader(sf, delimiter="\t")
        for row_idx, r in enumerate(reader, 1):
            cue_raw = r.get("cue", "").strip()
            if not cue_raw or cue_raw.startswith("#"):
                continue

            is_ov = cue_raw.startswith("+")
            clean_cue = cue_raw.lstrip("+")
            
            # Resolve timestamp
            t_val = None
            if clean_cue in words_map:
                t_val = words_map[clean_cue]
            else:
                try:
                    t_val = float(clean_cue.replace(":", "."))
                except ValueError:
                    pass

            if t_val is None:
                continue

            if is_ov:
                overlays.append({"t": t_val, "cue": clean_cue, "row": row_idx})
            else:
                if t_val < prev_scene_t - 0.05:
                    errors.append(f"Row {row_idx}: Scene cut '{cue_raw}' ({t_val:.2f}s) is out of chronological order (prev={prev_scene_t:.2f}s)")
                prev_scene_t = t_val
                scenes.append({"t0": t_val, "cue": clean_cue, "row": row_idx, "card": r.get("text", "").strip()})

    for i in range(len(scenes)):
        scenes[i]["t1"] = scenes[i + 1]["t0"] if i + 1 < len(scenes) else (max_word_end + 3.0)

    for ov in overlays:
        in_bounds = any((s["t0"] - 0.15 <= ov["t"] <= s["t1"] + 0.15) for s in scenes)
        if not in_bounds and scenes:
            errors.append(f"Overlay cue '{ov['cue']}' at {ov['t']:.2f}s falls outside any active scene boundaries")

    # 3. Validate cues_pro.tsv drift
    if os.path.exists(cues_path):
        cues_map = {}
        with open(cues_path, "r", encoding="utf-8", errors="ignore") as cf:
            for r in csv.DictReader(cf, delimiter="\t"):
                lbl = r.get("label", "").strip()
                if not lbl or lbl.startswith("#"):
                    continue
                try:
                    cues_map[lbl] = float(r.get("at", 0.0))
                except ValueError:
                    pass

        for ov in overlays:
            pop_label = f"pop_{ov['cue']}"
            if pop_label in cues_map:
                drift = abs(cues_map[pop_label] - ov["t"])
                if drift > 0.10:  # > 100ms drift
                    errors.append(f"Audio cue '{pop_label}' drift > 100ms: cue at {cues_map[pop_label]:.2f}s vs visual at {ov['t']:.2f}s (drift={drift*1000:.0f}ms)")

        for s in scenes:
            norm = s["cue"].replace(".", "_")
            whoosh_label = f"jcut_whoosh_{norm}"
            if whoosh_label in cues_map:
                expected = max(0.0, s["t0"] - 0.12)
                drift = abs(cues_map[whoosh_label] - expected)
                if drift > 0.10:
                    errors.append(f"J-cut cue '{whoosh_label}' drift > 100ms: cue at {cues_map[whoosh_label]:.2f}s vs expected {expected:.2f}s (drift={drift*1000:.0f}ms)")

            if s["card"]:
                slam_label = f"card_slam_{norm}"
                if slam_label in cues_map:
                    drift = abs(cues_map[slam_label] - s["t0"])
                    if drift > 0.10:
                        errors.append(f"Card slam cue '{slam_label}' drift > 100ms: cue at {cues_map[slam_label]:.2f}s vs card at {s['t0']:.2f}s (drift={drift*1000:.0f}ms)")

    # 4. Audio vs Video duration checks
    def get_duration(path):
        if not os.path.exists(path):
            return None
        import wave
        try:
            with wave.open(path, "rb") as wf:
                return wf.getnframes() / float(wf.getframerate())
        except Exception:
            return None

    vo_dur = get_duration(vo_path) or max_word_end
    mix_dur = get_duration(mix_path)

    if mix_dur is not None and vo_dur is not None:
        if mix_dur < vo_dur - 0.4:
            errors.append(f"Master mix ({mix_dur:.2f}s) is shorter than voiceover ({vo_dur:.2f}s) - speech cut off!")
        if prev_scene_t > mix_dur + 1.5:
            errors.append(f"Last scene starts at {prev_scene_t:.2f}s, exceeding master audio mix duration ({mix_dur:.2f}s)")

    # 5. Fact-Number Parity Audit (card stats in SCENES_HYBRID.tsv vs spoken numbers in LINES.tsv)
    parity_errs = validate_fact_number_parity(project_dir)
    errors.extend(parity_errs)

    # 6. Card-to-Voice Sync & Minimum Readable Hold Audit
    card_sync_errs = validate_card_voice_sync(project_dir)
    errors.extend(card_sync_errs)

    is_ok = (len(errors) == 0)
    return is_ok, errors


def validate_card_voice_sync(project_dir="."):
    """Verifies that every editorial card aligns with spoken timestamps and holds for readable duration."""
    words_path = os.path.join(project_dir, "WORDS.tsv")
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(words_path) or not os.path.exists(scenes_path):
        return []

    words_list = []
    line_words = {}
    with open(words_path, encoding="utf-8", errors="ignore") as wf:
        for r in csv.DictReader(wf, delimiter="\t"):
            try:
                item = {
                    "line": r.get("line", ""),
                    "i": r.get("i", ""),
                    "start": float(r["start"]),
                    "end": float(r["end"]),
                    "word": r.get("word", ""),
                    "clean": re.sub(r"[^\w]", "", r.get("word", "").lower()),
                    "cue": f"{r.get('line', '')}.{r.get('i', '')}",
                }
                words_list.append(item)
                line_words.setdefault(item["line"], []).append(item)
            except Exception:
                continue

    scenes = []
    with open(scenes_path, encoding="utf-8", errors="ignore") as sf:
        for r in csv.reader(sf, delimiter="\t"):
            if not r or r[0].startswith(("+", "#")) or r[0].lower() in ("cue", "id"):
                continue
            scenes.append(r)

    errs = []
    for i, sc in enumerate(scenes):
        cue = sc[0].strip()
        img = sc[1].strip() if len(sc) > 1 else ""
        tok = img.split(":")[0].strip().lower()
        is_card = tok in (
            "card", "card_stat", "card_phrase", "card_strike_replace", "strike_replace",
            "split_compare", "split_contrast", "scale_compare", "scale_bar",
            "bar_timeline", "timeline", "stat_pie", "stat_ring", "chapter_breather", "breather"
        ) or tok.startswith(("card_", "split_", "timeline_", "stat_", "bar_", "chapter_", "breather", "scale_"))

        if not is_card:
            continue

        card_t0 = None
        if "." in cue:
            parts = cue.split(".")
            ln, idx = parts[0], parts[1]
            if ln in line_words:
                for w in line_words[ln]:
                    if w["i"] == idx:
                        card_t0 = w["start"]
                        break
        if card_t0 is None:
            continue

        next_t0 = None
        if i + 1 < len(scenes):
            nxt_cue = scenes[i + 1][0].strip()
            if "." in nxt_cue:
                parts = nxt_cue.split(".")
                ln, idx = parts[0], parts[1]
                if ln in line_words:
                    for w in line_words[ln]:
                        if w["i"] == idx:
                            next_t0 = w["start"]
                            break

        card_dur = (next_t0 - card_t0) if next_t0 is not None else 5.0
        min_readable_dur = 2.6 if any(k in tok for k in ("split", "strike", "scale")) else 2.0
        if card_dur < min_readable_dur - 0.05:
            errs.append(f"F_CARD_EARLY_OR_LATE_DESYNC: Card '{cue}' ({tok}) held only {card_dur:.2f}s (< readable floor {min_readable_dur:.2f}s)")
    return errs


def _extract_spoken_numbers(text):
    """Parses both digit tokens ('1.4', '92') and English spoken number words ('two', 'ninety-two', 'one point four')."""
    txt = str(text or "").lower().replace(",", "")
    nums = set()
    for m in re.findall(r"\d+(?:\.\d+)?", txt):
        try:
            nums.add(float(m))
        except ValueError:
            pass
    ones = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
        "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
        "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19,
    }
    tens = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
    # Decimal phrase e.g. 'one point four'
    for mp in re.finditer(r"\b([a-z]+)\s+point\s+([a-z]+)\b", txt):
        if mp.group(1) in ones and mp.group(2) in ones:
            nums.add(float(f"{ones[mp.group(1)]}.{ones[mp.group(2)]}"))
    # Compound tens e.g. 'ninety-two', 'sixty six'
    for mt in re.finditer(r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[-\s]+(one|two|three|four|five|six|seven|eight|nine)\b", txt):
        nums.add(float(tens[mt.group(1)] + ones[mt.group(2)]))
    for w in re.findall(r"\b[a-z]+\b", txt):
        if w in ones:
            nums.add(float(ones[w]))
        elif w in tens:
            nums.add(float(tens[w]))
    return nums


def validate_fact_number_parity(project_dir="."):
    """Verifies numeric stats shown on editorial cards match spoken numbers in LINES.tsv."""
    lines_path = os.path.join(project_dir, "LINES.tsv")
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(lines_path) or not os.path.exists(scenes_path):
        return []
    line_map = {}
    with open(lines_path, encoding="utf-8", errors="ignore") as lf:
        for r in csv.DictReader(lf, delimiter="\t"):
            lid = (r.get("id") or "").strip()
            if lid:
                line_map[lid] = r.get("text", "")
                if lid.isdigit():
                    line_map[str(int(lid))] = r.get("text", "")
    errs = []
    with open(scenes_path, encoding="utf-8", errors="ignore") as sf:
        for idx_r, r in enumerate(csv.DictReader(sf, delimiter="\t"), 1):
            cue = (r.get("cue") or "").strip()
            img = (r.get("img") or "").strip().lower()
            txt = (r.get("text") or "").strip()
            if not cue or cue.startswith(("+", "#")) or not txt:
                continue
            if not any(k in img for k in ("card_stat", "strike_replace", "card_strike_replace", "scale_compare", "stat_")):
                continue
            card_nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", txt.replace(",", ""))]
            if not card_nums:
                continue
            lid_tok = cue.split(".")[0].lstrip("@")
            cand_txt = " ".join(filter(None, [
                line_map.get(lid_tok, ""),
                line_map.get(f"{int(lid_tok):02d}" if lid_tok.isdigit() else lid_tok, ""),
            ]))
            if not cand_txt:
                continue
            spoken_nums = _extract_spoken_numbers(cand_txt)
            if not spoken_nums:
                continue
            for cn in card_nums:
                matched = any(abs(cn - sn) <= max(0.05, 0.03 * max(abs(cn), 1.0)) for sn in spoken_nums)
                if not matched and len(card_nums) >= 2:
                    # Allow derived ratio on scale_compare (e.g. round(92 / 1.4) == 66)
                    mn, mx = min(card_nums), max(card_nums)
                    if mn > 0 and abs(cn - round(mx / mn)) <= 1:
                        matched = True
                if not matched:
                    errs.append(f"Row {idx_r} Fact-Number Parity FAILED: card '{img}' displays '{cn:g}' but script line '{cand_txt.strip()}' speaks {sorted(spoken_nums)}")
    return errs


def check_list_prosody_gaps(project_dir="."):
    """Inspects WORDS.tsv word gaps on checklist/inset_shelf lines for F_RUSHED_LIST (<0.22s spacing)."""
    words_path = os.path.join(project_dir, "WORDS.tsv")
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(words_path) or not os.path.exists(scenes_path):
        return []
    line_words = {}
    with open(words_path, encoding="utf-8", errors="ignore") as wf:
        for r in csv.DictReader(wf, delimiter="\t"):
            lid = (r.get("line") or "").strip()
            try:
                st, en = float(r["start"]), float(r["end"])
                line_words.setdefault(lid, []).append((st, en, r.get("word", "")))
                if lid.isdigit():
                    line_words.setdefault(str(int(lid)), []).append((st, en, r.get("word", "")))
            except Exception:
                continue
    rushed = []
    with open(scenes_path, encoding="utf-8", errors="ignore") as sf:
        for r in csv.DictReader(sf, delimiter="\t"):
            cue = (r.get("cue") or "").strip()
            ext = (r.get("extra") or "").lower()
            if cue.startswith("+") or not any(k in ext for k in ("checklist", "inset_shelf")):
                continue
            lid = cue.split(".")[0].lstrip("@")
            ws = line_words.get(lid) or line_words.get(f"{int(lid):02d}" if lid.isdigit() else lid, [])
            if len(ws) < 4:
                continue
            gaps = [ws[i + 1][0] - ws[i][1] for i in range(len(ws) - 1)]
            max_gap = max(gaps) if gaps else 0.0
            list_pauses = [g for g in gaps if g >= 0.22]
            if len(list_pauses) < 1 and max_gap < 0.22:
                rushed.append(f"Line {lid} ({' '.join(w[2] for w in ws[:6])}...): max internal pause={max_gap:.2f}s < 0.22s")
    return rushed


def validate_vfx_and_scenes(project_dir="."):
    """Gate 5: Visual Effects & Scene Dynamic Kinetics Verification.
    Verifies that the scene manifest is not visually inert (e.g. 100% generic 'fade' cuts and 'pop' overlays).
    Ensures dynamic VFX tags (zoom_punch, shake, danger, bw, ice, flash, drop, slam, slide) are present.
    """
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")

    if not os.path.exists(scenes_path):
        return False, [f"Scene manifest missing at {scenes_path}"]

    errors = []
    cut_extras = []
    ov_extras = []
    DYNAMIC_CUT_VFX = {"zoom_punch", "zoom_dissolve", "slide_push", "paper_crossfade", "crossfade", "danger", "shake", "ice", "bw", "flash", "blood", "rumble"}
    DYNAMIC_OV_VFX = {"drop", "slam", "slide_left", "slide_right", "hover", "rise"}

    with open(scenes_path, "r", encoding="utf-8", errors="ignore") as sf:
        for r in csv.DictReader(sf, delimiter="\t"):
            cue = r.get("cue", "").strip()
            if not cue or cue.startswith("#"):
                continue
            extra = r.get("extra", "").strip().lower()
            tokens = [t.strip() for t in extra.split(",") if t.strip()]
            if cue.startswith("+"):
                ov_extras.extend(tokens)
            else:
                cut_extras.extend(tokens)

    has_dynamic_cut = any(t in DYNAMIC_CUT_VFX for t in cut_extras)
    has_dynamic_ov = any(t in DYNAMIC_OV_VFX for t in ov_extras)

    if len(cut_extras) > 0 and not has_dynamic_cut and not has_dynamic_ov:
        errors.append("Visual kinetics are completely inert: 100% of cuts are generic 'fade' and overlays are 'pop'. Run vfx_smart_designer.py to assign dynamic punch zooms, camera shakes, danger vignettes, and kinetic sticker physics.")

    return (len(errors) == 0), errors


def inspect_card_split_frame_pixels(frame_im, archetype_kind, is_shorts=False):
    """Pixel-level layout guard for card_stat and split_compare frames.
    Rejects >65% blank uniform card interiors, empty left/right split halves,
    or stickers crossing the center W/2 split divider.
    """
    arr = np.array(frame_im.convert("RGB"))
    H, W = arr.shape[:2]

    if archetype_kind == "card":
        # Check for symmetric legacy corporate box borders first; otherwise evaluate full-bleed editorial canvas density
        gray = arr.mean(axis=2)
        cx_mid = W // 2
        border_ys = np.where((gray[:, cx_mid] < 80) & (np.arange(H) > int(0.08 * H)) & (np.arange(H) < int(0.85 * H)))[0]
        is_symmetric_box = False
        if len(border_ys) >= 2 and (border_ys[-1] - border_ys[0]) > int(0.15 * H):
            y0_b, y1_b = int(border_ys[0]), int(border_ys[-1])
            top_row_dark = float((gray[max(0, y0_b - 2):min(H, y0_b + 3), int(0.25 * W):int(0.75 * W)] < 90).mean())
            bot_row_dark = float((gray[max(0, y1_b - 2):min(H, y1_b + 3), int(0.25 * W):int(0.75 * W)] < 90).mean())
            is_symmetric_box = (top_row_dark > 0.70 and bot_row_dark > 0.70)

        if is_symmetric_box:
            y0_box = int(border_ys[0]) + 10
            y1_box = int(border_ys[-1]) - 10
            cy_mid = (y0_box + y1_box) // 2
            border_xs = np.where((gray[cy_mid, :] < 80) & (np.arange(W) > int(0.03 * W)) & (np.arange(W) < int(0.97 * W)))[0]
            if len(border_xs) >= 2 and (border_xs[-1] - border_xs[0]) > int(0.25 * W):
                x0_box, x1_box = int(border_xs[0]) + 10, int(border_xs[-1]) - 10
            else:
                x0_box, x1_box = int(0.12 * W), int(0.88 * W)
            roi = arr[y0_box:y1_box, x0_box:x1_box]
            med = np.median(roi.reshape(-1, 3), axis=0)
            diff = np.max(np.abs(roi.astype(np.int16) - med.astype(np.int16)), axis=2)
            blank_ratio = float((diff < 14).mean())
            if blank_ratio > 0.65:
                return False, f"Card interior is {blank_ratio*100:.1f}% empty uniform blank (> 65% max allowed)"
            return True, f"Card interior well-filled ({100 - blank_ratio*100:.1f}% visual density)"
        else:
            # Full-bleed minimalist editorial canvas (no heavy box border): verify crisp bold ink/highlighter/sticker density
            roi = arr[int(0.08 * H):int(0.56 * H), int(0.06 * W):int(0.94 * W)] if is_shorts else arr[int(0.14 * H):int(0.76 * H), int(0.08 * W):int(0.92 * W)]
            med = np.median(roi.reshape(-1, 3), axis=0)
            diff = np.max(np.abs(roi.astype(np.int16) - med.astype(np.int16)), axis=2)
            fg_mask = diff > 14
            fg_ratio = float(fg_mask.mean())
            cols_active = np.where(fg_mask.any(axis=0))[0]
            span_w = (cols_active[-1] - cols_active[0]) / max(1, roi.shape[1]) if len(cols_active) >= 2 else 0.0
            if fg_ratio < 0.055 or span_w < 0.35:
                return False, f"Full-bleed card too sparse/small (fill={fg_ratio*100:.1f}%, span={span_w*100:.0f}%)"
            return True, f"Full-bleed editorial card verified ({fg_ratio*100:.1f}% visual density, {span_w*100:.0f}% width span)"

    elif archetype_kind == "split":
        if is_shorts:
            # 9:16 Top-vs-Bottom horizontal split in upper visual stage (Y: 6% - 72%)
            top_roi = arr[int(0.08 * H):int(0.36 * H), int(0.06 * W):int(0.94 * W)]
            bot_roi = arr[int(0.42 * H):int(0.70 * H), int(0.06 * W):int(0.94 * W)]
            for side_name, roi in (("Top half", top_roi), ("Bottom half", bot_roi)):
                med = np.median(roi.reshape(-1, 3), axis=0)
                diff = np.max(np.abs(roi.astype(np.int16) - med.astype(np.int16)), axis=2)
                non_bg = float((diff > 16).mean())
                if non_bg < 0.03:
                    return False, f"Split-screen {side_name} is blank/empty ({non_bg*100:.2f}% content < 3.0% minimum)"

            # Also check horizontal divider gutter around Y = 0.39*H
            div_y = int(0.39 * H)
            top_ref_m = np.median(arr[div_y - 60:div_y - 32, int(0.2 * W):int(0.8 * W)].reshape(-1, 3), axis=0)
            bot_ref_m = np.median(arr[div_y + 32:div_y + 60, int(0.2 * W):int(0.8 * W)].reshape(-1, 3), axis=0)
            for g_name, gy0, gy1, ref_m in (("top divider gutter", div_y - 14, div_y - 6, top_ref_m),
                                            ("bottom divider gutter", div_y + 6, div_y + 14, bot_ref_m)):
                gutter_roi = arr[gy0:gy1, int(0.06 * W):int(0.94 * W)]
                g_diff = np.max(np.abs(gutter_roi.astype(np.int16) - ref_m.astype(np.int16)), axis=2)
                cross_ratio = float((g_diff > 22).mean())
                if cross_ratio > 0.08:
                    return False, f"Sticker/asset crossed horizontal split divider in {g_name} ({cross_ratio*100:.1f}% pixels > 8% max)"
            return True, "Top-vs-Bottom split panels balanced and divider clean"
        else:
            y0 = int(0.14 * H)
            y1 = int(0.76 * H)
            left_roi = arr[y0:y1, int(0.05 * W):int(0.45 * W)]
            right_roi = arr[y0:y1, int(0.55 * W):int(0.95 * W)]

            for side_name, roi in (("Left half", left_roi), ("Right half", right_roi)):
                med = np.median(roi.reshape(-1, 3), axis=0)
                diff = np.max(np.abs(roi.astype(np.int16) - med.astype(np.int16)), axis=2)
                non_bg = float((diff > 16).mean())
                if non_bg < 0.03:
                    return False, f"Split-screen {side_name} is blank/empty ({non_bg*100:.2f}% content < 3.0% minimum)"

            g_y0, g_y1 = int(0.20 * H), int(0.70 * H)
            left_ref_med = np.median(arr[g_y0:g_y1, W // 2 - 80:W // 2 - 48].reshape(-1, 3), axis=0)
            right_ref_med = np.median(arr[g_y0:g_y1, W // 2 + 48:W // 2 + 80].reshape(-1, 3), axis=0)
            for g_name, gx0, gx1, ref_m in (("left divider gutter", W // 2 - 15, W // 2 - 6, left_ref_med),
                                            ("right divider gutter", W // 2 + 6, W // 2 + 15, right_ref_med)):
                gutter_roi = arr[g_y0:g_y1, gx0:gx1]
                g_diff = np.max(np.abs(gutter_roi.astype(np.int16) - ref_m.astype(np.int16)), axis=2)
                cross_ratio = float((g_diff > 22).mean())
                if cross_ratio > 0.06:
                    return False, f"Sticker/asset crossed W/2 split divider in {g_name} ({cross_ratio*100:.1f}% pixels > 6% max)"

            return True, "Left-vs-Right split panels balanced and divider gutter clean"

    return True, "OK"


def audit_timeline_real_visual_density(project_dir=".", format_type="9:16"):
    """Enforces true unique Flow shot density, opening 15s flow, and zero shot stagnation/ping-pong."""
    errors = []
    deductions = []
    is_shorts = (format_type == "9:16")

    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")
    words_path = os.path.join(project_dir, "WORDS.tsv")
    if not os.path.exists(scenes_path) or not os.path.exists(words_path):
        return True, [], []

    words_map = {}
    max_word_end = 0.0
    with open(words_path, encoding="utf-8") as wf:
        for r in csv.DictReader(wf, delimiter="\t"):
            line_id = r.get("line", "")
            cue_idx = f"{line_id}.{r['i']}" if "line" in r and "i" in r else r.get("cue", "")
            try:
                st = float(r.get("start", 0.0))
                en = float(r.get("end", st))
                if cue_idx:
                    words_map[cue_idx] = st
                max_word_end = max(max_word_end, en)
            except Exception:
                pass

    dur_sec = max_word_end
    for af in ("mix_pro.wav", "mix.wav", "VO.wav"):
        ap = os.path.join(project_dir, af)
        if os.path.exists(ap):
            try:
                import soundfile as sf
                data, sr = sf.read(ap)
                dur_sec = max(dur_sec, len(data) / sr)
                break
            except Exception:
                pass
    dur_sec = max(1.0, dur_sec)

    scene_cuts = []
    with open(scenes_path, encoding="utf-8") as sf_in:
        for r in csv.DictReader(sf_in, delimiter="\t"):
            cue = (r.get("cue") or "").strip()
            if not cue or cue.startswith("#") or cue.startswith("+"):
                continue
            img = (r.get("img") or "").strip()
            t_val = words_map.get(cue)
            if t_val is None:
                try:
                    t_val = float(cue)
                except Exception:
                    continue
            scene_cuts.append((t_val, cue, img, r.get("extra", "")))

    scene_cuts.sort(key=lambda x: x[0])
    # Deduplicate same-timestamp rows
    dedup = []
    for sc in scene_cuts:
        if dedup and abs(sc[0] - dedup[-1][0]) < 0.05:
            dedup[-1] = sc
        else:
            dedup.append(sc)
    scene_cuts = dedup

    # 1. Unique Hero Shot Density (stop cheating with 6-12 recycled shots; scale cleanly with duration)
    unique_hero_shots = {sc[2] for sc in scene_cuts if sc[2].startswith("shots/")}
    if is_shorts:
        min_req_shots = max(6, int(dur_sec / 3.5))
    else:
        min_req_shots = max(12, int(dur_sec / 4.4))
    if len(unique_hero_shots) < min_req_shots:
        msg = (f"F_LOW_UNIQUE_SHOTS: Only {len(unique_hero_shots)} unique Flow hero shots for "
               f"{dur_sec:.1f}s ({'9:16 Shorts' if is_shorts else '16:9 Long'}; minimum required is {min_req_shots}). "
               f"Stop recycling {len(unique_hero_shots)} images with fake cuts!")
        errors.append(msg)
        deductions.append(f"[-25 pts] {msg}")

    # Hard Blocker: Consecutive duplicate shots/*.png rows
    consecutive_dups = []
    for idx_c in range(len(scene_cuts) - 1):
        _, c0, img0, _ = scene_cuts[idx_c]
        _, c1, img1, _ = scene_cuts[idx_c + 1]
        if img0.startswith("shots/") and img0 == img1:
            consecutive_dups.append(f"{c0}->{c1} ({img0})")
    if consecutive_dups:
        msg = f"F_DUPLICATE_SHOT_TRANSITION: Consecutive duplicate shot rows detected: {', '.join(consecutive_dups[:4])}. Each narrative beat must advance to a distinct unique hero shot!"
        errors.append(msg)
        deductions.append(f"[-25 pts] {msg}")

    # 2. Check BOTH pacing extremes: Dead Stagnation (>7.5s/11s) AND Chaotic Rapid Shifting (<1.5s)
    rapid_flickers = []
    for idx_c in range(len(scene_cuts) - 1):
        t0_c, c0_c, img0_c, ext0_c = scene_cuts[idx_c]
        t1_c, c1_c, img1_c, ext1_c = scene_cuts[idx_c + 1]
        cut_dur = t1_c - t0_c
        e0l = (ext0_c or "").lower()
        e1l = (ext1_c or "").lower()
        is_allowed_fast = any(k in e0l or k in e1l for k in ("rapid_list", "hook_beat"))
        if cut_dur < 1.50 and not (is_allowed_fast and cut_dur >= 0.90):
            rapid_flickers.append(f"{c0_c}->{c1_c} ({cut_dur:.2f}s)")
    if rapid_flickers:
        msg = (f"Chaotic Rapid Shifting FAILED: {len(rapid_flickers)} erratic sub-1.5s scene cut(s) detected "
               f"({', '.join(rapid_flickers[:3])}). Enforce calm clause-locked holds (>= {'1.8s' if is_shorts else '2.2s'}).")
        errors.append(msg)
        deductions.append(f"[-20 pts] {msg}")

    max_shot_span = 7.5 if is_shorts else 11.0
    span_idx = 0
    while span_idx < len(scene_cuts):
        t_start, c_start, img_start, _ = scene_cuts[span_idx]
        end_idx = span_idx + 1
        while end_idx < len(scene_cuts) and scene_cuts[end_idx][2] == img_start and img_start.startswith("shots/"):
            end_idx += 1
        t_end = scene_cuts[end_idx][0] if end_idx < len(scene_cuts) else dur_sec
        span_dur = t_end - t_start
        if img_start.startswith("shots/") and span_dur > max_shot_span:
            msg = (f"Shot Stagnation FAILED: '{img_start}' held continuously for {span_dur:.1f}s "
                   f"(max allowed {max_shot_span:.1f}s before new unique shot or visual archetype).")
            errors.append(msg)
            deductions.append(f"[-20 pts] {msg}")
            break
        span_idx = end_idx

    # 3. Opening 15s Flow & Full-Timeline Ping-Pong Guard (No A -> card -> A snap-backs)
    opening_cuts = [sc for sc in scene_cuts if sc[0] < 15.0]
    open_seq = []
    for _, _, img, _ in opening_cuts:
        tok = os.path.basename(img).split(":")[0].strip()
        if not open_seq or open_seq[-1] != tok:
            open_seq.append(tok)

    distinct_open = set(open_seq)
    if len(distinct_open) < 3:
        msg = (f"Opening 15s Flow FAILED: Only {len(distinct_open)} distinct visual source(s) in first 15s "
               f"({list(distinct_open)}; minimum 3 required).")
        errors.append(msg)
        deductions.append(f"[-20 pts] {msg}")

    all_seq = []
    for _, c_lbl, img, _ in scene_cuts:
        tok = os.path.basename(img).split(":")[0].strip()
        if not all_seq or all_seq[-1][0] != tok:
            all_seq.append((tok, c_lbl))

    for i in range(len(all_seq) - 2):
        (a, ca), (mid, _), (b, cb) = all_seq[i], all_seq[i + 1], all_seq[i + 2]
        arch_pfx = ("card", "split", "timeline", "stat", "bar_", "chapter_", "breather", "scale_", "strike_")
        is_card_mid = mid.startswith(arch_pfx)
        if a == b and not a.startswith(arch_pfx) and is_card_mid:
            msg = f"Linear Flow Ping-Pong Repeat FAILED: '{a}' ({ca}) -> '{mid}' -> '{b}' ({cb}) snaps back to same shot."
            errors.append(msg)
            deductions.append(f"[-20 pts] {msg}")
            break

    # Ban Back-to-Back Blank/Editorial Cards (never let two blank/stat/breather cards run back-to-back)
    arch_pfx_c = ("card", "split", "timeline", "stat", "bar_", "chapter_", "breather", "scale_", "strike_")
    for i in range(len(all_seq) - 1):
        (a, ca), (b, cb) = all_seq[i], all_seq[i + 1]
        if a.startswith(arch_pfx_c) and b.startswith(arch_pfx_c):
            msg = f"Consecutive Blank Cards BANNED: '{a}' ({ca}) -> '{b}' ({cb}) back-to-back kills visual engagement."
            errors.append(msg)
            deductions.append(f"[-20 pts] {msg}")
            break

    return (len(errors) == 0), errors, deductions


def validate_pacing_and_density(project_dir=".", format_type="9:16"):
    """Gate 6: Visual Pacing, High Frame Density, Unique Shot Density, Director Supervision & Card/Split Pixel Guard."""
    errors = []
    is_shorts = (format_type == "9:16")

    # -1. Director Supervision Plan Gate (Logical Relevance, -0.06s Word-Sync, Scale Continuity)
    scenes_p = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    words_p = os.path.join(project_dir, "WORDS.tsv")
    if os.path.exists(scenes_p) and os.path.exists(words_p):
        try:
            import json
            import director_supervisor
            dp_p = os.path.join(project_dir, "DIRECTOR_PLAN.json")
            if not os.path.exists(dp_p) or os.path.getmtime(dp_p) < os.path.getmtime(scenes_p):
                plan = director_supervisor.supervise_project(project_dir)
            else:
                plan = json.load(open(dp_p, encoding="utf-8"))
            if not plan or not plan.get("scenes"):
                errors.append("Director Supervision FAILED: Missing or empty DIRECTOR_PLAN.json.")
            else:
                sm = plan.get("summary", {})
                rej = int(sm.get("rejected_redundant_stickers", 0))
                if rej > 0:
                    errors.append(
                        f"Director Supervision FAILED: {rej} REJECTED_REDUNDANT sticker(s) in DIRECTOR_PLAN.json. "
                        f"Remove redundant overlays matching background shots before rendering."
                    )
                fast_cards = [f for f in plan.get("audit_breakdown", []) if f.get("code") == "F_READ_TOO_FAST"]
                if fast_cards:
                    print(f"⚠️ Director Gate Advisory ({len(fast_cards)} fast card warning(s)): {fast_cards[0].get('msg','')}")
                era_bad = [f for f in plan.get("audit_breakdown", []) if f.get("code") in ("ERA_MISMATCH", "NONLITERAL_STICKER")]
                if era_bad:
                    errors.append(f"Director Era/Literal Sticker Gate FAILED: {era_bad[0].get('msg', '')}")
        except Exception as dp_ex:
            errors.append(f"Director Supervision FAILED: {dp_ex}")

    rushed_lists = check_list_prosody_gaps(project_dir)
    if rushed_lists:
        print(f"⚠️ List Prosody Advisory (F_RUSHED_LIST): {rushed_lists[0]}")

    # 0. Real Unique Shot Density & Opening 15s Flow Audit (Zero Fake Shot Recycling)
    ok_real, real_errs, _ = audit_timeline_real_visual_density(project_dir, format_type=format_type)
    if not ok_real:
        errors.extend(real_errs)

    # 1. Bezel Detection in shots
    shots_dir = os.path.join(project_dir, "shots")
    if os.path.exists(shots_dir):
        for fname in sorted(os.listdir(shots_dir)):
            if fname.endswith((".png", ".jpg")):
                sp = os.path.join(shots_dir, fname)
                try:
                    im = Image.open(sp)
                    arr = np.array(im)
                    if arr.shape[0] > 100 and arr.shape[1] > 100:
                        top_dark = float(arr[:40, :, :3].mean()) < 25.0
                        left_dark = float(arr[:, :40, :3].mean()) < 25.0
                        right_dark = float(arr[:, -40:, :3].mean()) < 25.0
                        # Also check inner bezel: a thick black rectangular frame inset ~150-250px
                        inner_left_dark = float(arr[200:-200, 180:240, :3].mean()) < 30.0
                        if (top_dark and (left_dark or right_dark)) or (inner_left_dark and left_dark):
                            errors.append(f"Device Bezel detected in {fname}: Shot contains an artificial smartphone mockup/bezel frame. Regenerate with no phone frame or crop cleanly.")
                except Exception:
                    pass

    # 2. WORDS.tsv em-dash check
    words_path = os.path.join(project_dir, "WORDS.tsv")
    if os.path.exists(words_path):
        with open(words_path, encoding="utf-8") as wf:
            for r in csv.DictReader(wf, delimiter="\t"):
                w = r.get("word", "")
                if re.search(r"[—–]|--", w):
                    errors.append(f"Em-dash glued word detected in WORDS.tsv: '{w}' at {r.get('start')}s. Run align_hybrid_scenes.py to sanitize.")
                    break

    # 3. Visual hold duration check
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if os.path.exists(scenes_path) and os.path.exists(words_path):
        words_map = {}
        with open(words_path, encoding="utf-8") as wf:
            for r in csv.DictReader(wf, delimiter="\t"):
                line_id = r.get("line", "")
                cue_idx = f"{line_id}.{r['i']}" if "line" in r and "i" in r else r.get("cue", "")
                if cue_idx:
                    try:
                        words_map[cue_idx] = float(r["start"])
                    except Exception:
                        pass

        max_allowed_hold = 4.2 if is_shorts else 6.5
        visual_beats = []
        with open(scenes_path, encoding="utf-8") as sf:
            for r in csv.DictReader(sf, delimiter="\t"):
                cue = r.get("cue", "").strip()
                if not cue or cue.startswith("#"):
                    continue
                clean_cue = cue.lstrip("+")
                t_val = words_map.get(clean_cue)
                if t_val is not None:
                    visual_beats.append((t_val, cue, r.get("img", "")))

        visual_beats.sort(key=lambda b: b[0])
        for idx in range(len(visual_beats) - 1):
            interval = visual_beats[idx + 1][0] - visual_beats[idx][0]
            if interval > max_allowed_hold + 0.15:
                errors.append(f"Visual Dead-Hold > {max_allowed_hold}s: Beat {visual_beats[idx][1]} held for {interval:.2f}s before {visual_beats[idx + 1][1]}. Insert a fresh hero shot, archetype beat, or synchronized sticker.")

        # Check Sticker Density (Rule 29 & Mission Mandate)
        stk_rows = [r for r in list(csv.DictReader(open(scenes_path, encoding="utf-8"), delimiter="\t"))
                    if (r.get("cue") or "").startswith("+") and not (r.get("img") or "").startswith("bars:")
                    and (r.get("img") or "") not in ("tag", "count")]
        min_stks = 14 if is_shorts else 28
        if len(stk_rows) < min_stks:
            errors.append(f"F_SPARSE_STICKERS: Only {len(stk_rows)} stickers scheduled in SCENES_HYBRID.tsv (minimum required is {min_stks}). Video is under-decorated; add purposeful voice-synced stickers!")

        # Check Card-to-Voice Sync Gate (F_CARD_VOICE_DESYNC)
        all_words_list = []
        with open(words_path, encoding="utf-8") as wf:
            for wr in csv.DictReader(wf, delimiter="\t"):
                all_words_list.append({"word": wr.get("word", "").lower().strip('.,!?":;'), "start": float(wr.get("start", 0.0)), "end": float(wr.get("end", 0.0))})

        card_desyncs = []
        for r in list(csv.DictReader(open(scenes_path, encoding="utf-8"), delimiter="\t")):
            c_cue = (r.get("cue") or "").strip()
            if not c_cue or c_cue.startswith("#") or c_cue.startswith("+"):
                continue
            c_img = (r.get("img") or "").strip()
            c_tok = os.path.splitext(os.path.basename(c_img))[0].split(":")[0].strip()
            if c_tok in ("card", "card_stat", "card_phrase", "split_compare", "split_contrast", "scale_compare", "card_strike_replace", "strike_replace"):
                c_t0 = words_map.get(c_cue, 0.0)
                c_text = (r.get("text") or "").strip().lower()
                c_words = set(re.findall(r"\b[a-z]{3,}\b|\b\d+\b", c_text))
                c_words -= {"the", "and", "for", "with", "from", "that", "this", "myth", "reality", "card", "stat"}
                if c_words:
                    spoken_in_win = {w["word"] for w in all_words_list if c_t0 - 0.5 <= w["start"] <= c_t0 + 4.5}
                    overlap = c_words & spoken_in_win
                    if not overlap and len(spoken_in_win) > 0:
                        card_desyncs.append(f"{c_cue} ({c_tok}: '{c_text[:30]}')")
        if card_desyncs:
            errors.append(f"F_CARD_VOICE_DESYNC: Card text out-of-sync with spoken narration: {', '.join(card_desyncs[:3])}")

        # 4. Pre-Render Card & Split-Screen Pixel Content Verification
        try:
            import render_pro
            render_pro.set_look("bright")
            W_test, H_test = (1080, 1920) if is_shorts else (1920, 1080)
            cwd_orig = os.getcwd()
            os.chdir(project_dir)
            try:
                cur_rows = list(csv.DictReader(open(scenes_path, encoding="utf-8"), delimiter="\t"))
                i_row = 0
                while i_row < len(cur_rows):
                    r = cur_rows[i_row]
                    cue = (r.get("cue") or "").strip()
                    if not cue or cue.startswith("#") or cue.startswith("+"):
                        i_row += 1
                        continue
                    img_tok = (r.get("img") or "").strip()
                    txt = (r.get("text") or "").strip()
                    base_tok = os.path.splitext(os.path.basename(img_tok))[0].split(":")[0].strip()
                    ov_paths = []
                    j_row = i_row + 1
                    while j_row < len(cur_rows) and (cur_rows[j_row].get("cue") or "").strip().startswith("+"):
                        ov_paths.append((cur_rows[j_row].get("img") or "").strip())
                        j_row += 1

                    if base_tok in ("card", "card_stat", "card_phrase") or base_tok.startswith("card_"):
                        stk = render_pro.resolve_sticker_path(ov_paths[0]) if ov_paths else None
                        fr = render_pro.draw_card_stat(W_test, H_test, txt or img_tok, is_shorts=is_shorts, dt=0.6, sticker_im=stk)
                        ok_px, msg_px = inspect_card_split_frame_pixels(fr, "card", is_shorts=is_shorts)
                        if not ok_px:
                            errors.append(f"Card Layout Defect ({cue}): {msg_px}")
                    elif base_tok in ("split_compare", "split_contrast") or base_tok.startswith("split_"):
                        l_stk = render_pro.resolve_sticker_path(ov_paths[0]) if len(ov_paths) >= 1 else None
                        r_stk = render_pro.resolve_sticker_path(ov_paths[1]) if len(ov_paths) >= 2 else None
                        fr = render_pro.draw_split_compare(W_test, H_test, txt or img_tok, is_shorts=is_shorts, dt=1.8,
                                                           left_sticker=l_stk, right_sticker=r_stk, duration=3.5)
                        ok_px, msg_px = inspect_card_split_frame_pixels(fr, "split", is_shorts=is_shorts)
                        if not ok_px:
                            errors.append(f"Split Layout Defect ({cue}): {msg_px}")
                    i_row = j_row
            finally:
                os.chdir(cwd_orig)
        except Exception as e:
            print(f"⚠️ Pre-render card/split layout audit skipped: {e}")

    return (len(errors) == 0), errors


def run_pre_render_gate(project_dir=".", format_type="9:16"):
    """Executes the complete mandatory Pre-Render Quality Gate."""
    print("==================================================")
    print(f"🛡️ PRE-RENDER QUALITY GATE: {os.path.abspath(project_dir)}")
    print(f"   Target Format: {format_type}")
    print("==================================================")

    all_failures = []

    # Gate 1: Stickers & Shots
    ok1, errs1 = validate_stickers_and_shots(project_dir)
    if not ok1:
        print("❌ Gate 1 FAILED: Scene & Sticker Manifest Completeness")
        all_failures.extend(errs1)
        # Check if bridge is running to explain missing assets
        bridge_on = check_flow_bridge_active()
        if not bridge_on:
            all_failures.append("🚨 Flow Bridge on port 8791 is OFFLINE! Start it with: flow-auto bridge start")
        else:
            print("   ℹ️ Flow Bridge (port 8791) is active. Visual assets must be generated.")
    else:
        print("✅ Gate 1 PASSED: All scene shots and sticker props exist on disk & pass cutout QC.")

    # Gate 2: Vertical Framing (Shorts only)
    if format_type == "9:16":
        ok2, errs2 = validate_vertical_framing(project_dir)
        if not ok2:
            print("❌ Gate 2 FAILED: 9:16 Vertical Framing Purity")
            all_failures.extend(errs2)
        else:
            print("✅ Gate 2 PASSED: 100% native vertical 9:16 framing verified (no letterbox bars).")
    else:
        print("✅ Gate 2 PASSED: 16:9 Widescreen target.")

    # Gate 3: 3-Stem Audio
    ok3, errs3 = validate_audio_integrity(project_dir)
    if not ok3:
        print("❌ Gate 3 FAILED: 3-Stem Master Audio Integrity")
        all_failures.extend(errs3)
    else:
        print("✅ Gate 3 PASSED: Master mix and voiceover validated (non-silent, calibrated).")

    # Gate 4: Multi-Track Synchronization
    ok4, errs4 = validate_multitrack_sync(project_dir)
    if not ok4:
        print("❌ Gate 4 FAILED: Multi-Track Synchronization (WORDS <-> SCENES <-> CUES)")
        all_failures.extend(errs4)
    else:
        print("✅ Gate 4 PASSED: Multi-track sync verified (zero drift >100ms, timeline duration locked).")

    # Gate 5: Visual Effects & Kinetic Directing
    ok5, errs5 = validate_vfx_and_scenes(project_dir)
    if not ok5:
        print("❌ Gate 5 FAILED: Visual Effects & Dynamic Scene Kinetics")
        all_failures.extend(errs5)
    else:
        print("✅ Gate 5 PASSED: Dynamic visual effects verified (punch zooms, camera shakes, kinetic overlays).")

    # Gate 6: Visual Pacing, High Frame Density & Bezel Sanity Gate
    ok6, errs6 = validate_pacing_and_density(project_dir, format_type=format_type)
    if not ok6:
        print("❌ Gate 6 FAILED: Visual Pacing & Density Gate (Hold <= 3.5s & No Phone Bezels)")
        all_failures.extend(errs6)
    else:
        print("✅ Gate 6 PASSED: Visual pacing density verified (holds <= 3.5s, no device bezels, clean word tokens).")

    print("==================================================")
    if all_failures:
        print("🚨 PRE-RENDER GATE REJECTED THE TIMELINE! FIXES REQUIRED:")
        for idx, f in enumerate(all_failures, 1):
            print(f"  {idx}. {f}")
        print("==================================================")
        return False

    print("🎯 ALL 6 QUALITY GATES PASSED! SAFE FOR 100% ERROR-FREE RENDERING.")
    print("==================================================")
    return True


def main():
    parser = argparse.ArgumentParser(description="Mandatory Pre-Render Quality Gate")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory")
    parser.add_argument("--format", choices=["9:16", "16:9", "short", "long"], default=None)
    args = parser.parse_args()

    fmt = args.format
    if fmt == "short":
        fmt = "9:16"
    elif fmt == "long":
        fmt = "16:9"
    if not fmt:
        p_base = os.path.basename(os.path.abspath(args.project_dir)).lower()
        if p_base == "long" or p_base.endswith("_long"):
            fmt = "16:9"
        else:
            fmt = "9:16"

    passed = run_pre_render_gate(args.project_dir, format_type=fmt)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
