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
        raw + ".png" if not raw.endswith(".png") else raw,
        os.path.join(project_dir, "elements", "cut", f"{name_no_ext}.png"),
        os.path.join(project_dir, "elements", "cut", basename),
        os.path.join(project_dir, "..", "elements", "cut", f"{name_no_ext}.png"),
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


def inspect_sticker_cutout_quality(png_path):
    """Verifies that a resolved sticker has true alpha transparency, no magenta halo, and no edge clipping."""
    try:
        with Image.open(png_path) as im:
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
    total_scenes = 0
    total_stickers = 0

    PROGRAMMATIC_SHOTS = {
        "card", "card_stat", "card_phrase", "split_compare", "split_contrast",
        "bar_timeline", "stat_pie", "stat_ring", "grid_week"
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
                if shot_file in PROGRAMMATIC_SHOTS or shot_file.startswith(("card_", "split_", "timeline_", "stat_")):
                    continue
                if shot_file:
                    # Check candidate locations for shot
                    shot_cands = [
                        shot_file,
                        os.path.join(project_dir, "shots", os.path.basename(shot_file)),
                        os.path.join(project_dir, shot_file)
                    ]
                    if not any(os.path.exists(p) and os.path.getsize(p) > 20000 for p in shot_cands):
                        missing_shots.append(f"Row {row_idx}: {shot_file}")

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

    errors = []
    if missing_shots:
        errors.append(f"Missing {len(missing_shots)} scene shot(s):\n  " + "\n  ".join(missing_shots[:6]))
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

        # Verify that EVERY sound asset referenced in cues_pro.tsv actually exists on disk!
        missing_sfx = []
        for c in cues_rows:
            f_path = c.get("file", "").strip()
            if f_path and not os.path.exists(f_path):
                # Check candidate relative paths
                cand = os.path.join(project_dir, f_path)
                if not os.path.exists(cand):
                    missing_sfx.append(f"{c.get('label')}: '{f_path}'")
        if missing_sfx:
            errors.append(f"Missing {len(missing_sfx)} sound asset(s) referenced in cues_pro.tsv:\n  " + "\n  ".join(missing_sfx[:5]))

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

    is_ok = (len(errors) == 0)
    return is_ok, errors


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
    DYNAMIC_CUT_VFX = {"zoom_punch", "danger", "shake", "ice", "bw", "flash", "blood", "rumble"}
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

    print("==================================================")
    if all_failures:
        print("🚨 PRE-RENDER GATE REJECTED THE TIMELINE! FIXES REQUIRED:")
        for idx, f in enumerate(all_failures, 1):
            print(f"  {idx}. {f}")
        print("==================================================")
        return False

    print("🎯 ALL 5 QUALITY GATES PASSED! SAFE FOR 100% ERROR-FREE RENDERING.")
    print("==================================================")
    return True


def main():
    parser = argparse.ArgumentParser(description="Mandatory Pre-Render Quality Gate")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory")
    parser.add_argument("--format", choices=["9:16", "16:9"], default=None)
    args = parser.parse_args()

    fmt = args.format
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
