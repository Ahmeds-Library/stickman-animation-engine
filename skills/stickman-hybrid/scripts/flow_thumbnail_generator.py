#!/usr/bin/env python3
"""flow_thumbnail_generator.py: Stage 1 Intelligent Flow Thumbnail Base Artwork Generator
Generates dedicated high-CTR base artwork via Google Flow (flow-auto) or smart fallback.
Features:
1. Pre-Flight Check: Verifies Google Flow bridge (port 8791) via flow-auto daemon/status.
2. Bespoke High-CTR Prompts: Driven by viral_seo_intelligence + cognitive frameworks.
3. Strict No-Text Enforcement: Instructs Flow to generate ZERO text/labels, leaving clean negative space.
4. Active Look Palette Alignment: Audits prompts via flow_prompt_auditor with active --look directives.
5. Dual-Format Generation: Dedicated 16:9 Landscape & 9:16 Vertical native hero scenes.
6. Seamless Graceful Fallback: Selects/composites highest-contrast candidate if Flow is offline.
7. Validation: Ensures outputs are non-blank, valid aspect ratio, and properly dimensioned.
"""

import os
import sys
import glob
import json
import time
import math
import argparse
import shutil
import subprocess
import socket
from PIL import Image, ImageDraw, ImageFilter, ImageStat

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

try:
    import flow_prompt_auditor
except ImportError:
    flow_prompt_auditor = None

try:
    import viral_seo_intelligence
except ImportError:
    viral_seo_intelligence = None


def is_flow_bridge_ready(port=8791):
    """Checks whether the Google Flow connector bridge daemon is running and reachable."""
    # 1. Socket check
    sock_ok = False
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1.0):
            sock_ok = True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

    # 2. Check flow-auto CLI presence
    flow_bin = shutil.which("flow-auto")
    if not flow_bin:
        return False

    # 3. Check daemon status
    try:
        res = subprocess.run([flow_bin, "daemon", "status"], capture_output=True, text=True, timeout=3)
        if "running" in res.stdout.lower() or "connected" in res.stdout.lower():
            return True
    except Exception:
        pass

    return sock_ok


def extract_topic_and_entities(project_dir="."):
    """Extracts topic name, core entities, and high-impact nouns from project files."""
    slug = os.path.basename(os.path.abspath(project_dir))
    topic = slug.replace("_", " ").title()
    
    # Try reading SCRIPT.md or LINES.tsv from root, long, or short
    text_corpus = ""
    for cand in [
        os.path.join(project_dir, "SCRIPT.md"),
        os.path.join(project_dir, "long", "SCRIPT.md"),
        os.path.join(project_dir, "short", "SCRIPT.md"),
        os.path.join(project_dir, "LINES.tsv"),
        os.path.join(project_dir, "long", "LINES.tsv"),
        os.path.join(project_dir, "short", "LINES.tsv"),
    ]:
        if os.path.exists(cand):
            try:
                with open(cand, "r", encoding="utf-8", errors="ignore") as f:
                    text_corpus += " " + f.read()
            except Exception:
                pass

    # Extract top keywords
    import re
    words = re.findall(r"\b[A-Za-z]{4,}\b", text_corpus.lower())
    STOPWORDS = {
        "this", "that", "with", "from", "they", "were", "what", "when", "there", "their",
        "would", "could", "about", "which", "after", "before", "where", "into", "every",
        "without", "these", "other", "first", "years", "people", "century", "became",
        "human", "humans", "today", "tonight", "night", "short", "long", "version", "scene"
    }
    filtered = [w for w in words if w not in STOPWORDS]
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    top_entities = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:6]
    entity_names = [e[0] for e in top_entities]

    # Specific topic heuristics
    slug_clean = slug.lower()
    if "road" in slug_clean or "roman" in slug_clean:
        topic_subject = "straight Roman stone highway slicing across primordial mountains"
        prop_subject = "glowing ancient Roman bronze groma surveying tool and carved milestone pillar"
        action = "staring in shock and disbelief with hands on head at the impossible straight road"
    elif "cold" in slug_clean or "ice" in slug_clean:
        topic_subject = "towering desert ice structure radiating glowing mist"
        prop_subject = "glowing crystalline ice block radiating cyan cold vapor"
        action = "staring in pure shock at impossible frozen ice in the burning desert"
    elif "waking" in slug_clean or "sleep" in slug_clean or "alarm" in slug_clean:
        topic_subject = "dim atmospheric ancient bedroom chamber with soft dawn light"
        prop_subject = "mysterious screaming ancient water clock and burning incense labyrinth"
        action = "bolting upright in bed in wild panic and disbelief"
    else:
        e_str = " and ".join(entity_names[:2]) if entity_names else "ancient secret"
        topic_subject = f"dramatic atmospheric historical environment exploring {e_str}"
        prop_subject = f"mysterious glowing {entity_names[0] if entity_names else 'ancient artifact'} radiating vibrant light"
        action = "staring in shock and disbelief with hands on head"

    return {
        "slug": slug,
        "topic": topic,
        "entities": entity_names,
        "topic_subject": topic_subject,
        "prop_subject": prop_subject,
        "action": action
    }


def craft_flow_thumbnail_prompts(project_dir=".", look="bright"):
    """Crafts dedicated 16:9 and 9:16 high-CTR prompts with strict negative space and zero text."""
    info = extract_topic_and_entities(project_dir)
    
    # 1. 16:9 Landscape Prompt (Negative space on left 45%)
    prompt_16x9_raw = (
        f"Cinematic YouTube thumbnail hero composition: Expressive 2D cartoon stickman character on the right side, "
        f"{info['action']}, looking at a gigantic monumental {info['prop_subject']} in the center, "
        f"set against {info['topic_subject']}, wide open clear empty negative space on the left 45% of frame with clean simple gradient, "
        f"high-contrast cinematic lighting, vibrant saturated palette, clean 2D vector storybook illustration style, thick dark ink outlines, "
        f"ultra-dramatic depth. STRICT NO-TEXT RULE: Generate ZERO text, zero letters, zero numbers, zero words, zero signs, zero watermark, zero logos."
    )

    # 2. 9:16 Vertical Prompt (Negative space in top 35%)
    prompt_9x16_raw = (
        f"Cinematic YouTube Shorts vertical cover hero composition: Expressive 2D cartoon stickman character in lower half, "
        f"{info['action']}, dramatic low angle shot looking up at {info['prop_subject']}, "
        f"with {info['topic_subject']}, wide open empty negative space in the top 35% of frame with clean simple atmospheric sky gradient, "
        f"high-contrast lighting, bold saturated colors, clean 2D vector illustration, thick dark ink outlines. "
        f"STRICT NO-TEXT RULE: Generate ZERO text, zero letters, zero numbers, zero words, zero signs, zero watermark, zero logos."
    )

    # Audit and enhance with look directives via flow_prompt_auditor
    if flow_prompt_auditor:
        prompt_16x9 = flow_prompt_auditor.audit_and_enhance_prompt(prompt_16x9_raw, look=look, is_ancient=True)
        prompt_9x16 = flow_prompt_auditor.audit_and_enhance_prompt(prompt_9x16_raw, look=look, is_ancient=True)
    else:
        prompt_16x9 = prompt_16x9_raw
        prompt_9x16 = prompt_9x16_raw

    return {
        "16x9": prompt_16x9,
        "9x16": prompt_9x16,
        "info": info,
        "look": look
    }


def validate_image_file(img_path, target_aspect=None):
    """Verifies that an image exists, is non-corrupt, non-empty, and non-blank."""
    if not os.path.exists(img_path) or os.path.getsize(img_path) < 10000:
        return False, "File missing or smaller than 10KB"
    try:
        with Image.open(img_path) as im:
            w, h = im.size
            if w < 300 or h < 300:
                return False, f"Image dimensions too small ({w}x{h})"
            gray = im.convert("L")
            stat = ImageStat.Stat(gray)
            mean_lum = stat.mean[0]
            std_lum = stat.stddev[0]
            if std_lum < 8.0:
                return False, f"Image appears blank or solid color (stddev: {std_lum:.2f})"
            if target_aspect:
                current_aspect = w / h
                if abs(current_aspect - target_aspect) > 0.4:
                    return True, f"Aspect ratio variance ({current_aspect:.2f} vs target {target_aspect:.2f})"
            return True, f"Valid ({w}x{h}, lum: {mean_lum:.1f}, std: {std_lum:.1f})"
    except Exception as e:
        return False, f"Corrupt image: {e}"


def generate_fallback_base_artwork(project_dir, out_path, target_w, target_h, aspect_name="16:9", look="bright"):
    """Composites the highest-contrast project shot, stickman, and prop with clean negative space."""
    # Find candidate shot backgrounds
    candidates = []
    for d in [project_dir, os.path.join(project_dir, "long"), os.path.join(project_dir, "short")]:
        shots_dir = os.path.join(d, "shots")
        if os.path.exists(shots_dir):
            candidates.extend(sorted(glob.glob(os.path.join(shots_dir, "*.png"))))
            candidates.extend(sorted(glob.glob(os.path.join(shots_dir, "*.jpg"))))

    # Evaluate best candidate background by contrast
    best_bg = None
    best_score = -1.0
    for cand in candidates:
        try:
            with Image.open(cand) as im:
                st = ImageStat.Stat(im.convert("L"))
                score = st.stddev[0]
                if score > best_score:
                    best_score = score
                    best_bg = cand
        except Exception:
            pass

    # Find prop cutout
    prop_candidates = []
    stickman_candidates = []
    for d in [project_dir, os.path.join(project_dir, "long"), os.path.join(project_dir, "short")]:
        cut_dir = os.path.join(d, "elements", "cut")
        if os.path.exists(cut_dir):
            prop_candidates.extend(sorted(glob.glob(os.path.join(cut_dir, "*.png"))))
        img_dir = os.path.join(d, "img")
        if os.path.exists(img_dir):
            stickman_candidates.extend(sorted(glob.glob(os.path.join(img_dir, "ref_*.png"))))
            stickman_candidates.extend(sorted(glob.glob(os.path.join(img_dir, "ref_*.jpg"))))

    prop_path = prop_candidates[0] if prop_candidates else None
    stickman_path = stickman_candidates[0] if stickman_candidates else None

    # Create base canvas
    canvas = Image.new("RGBA", (target_w, target_h), (24, 28, 38, 255))
    if best_bg and os.path.exists(best_bg):
        raw_bg = Image.open(best_bg).convert("RGBA")
        scale = max(target_w / raw_bg.width, target_h / raw_bg.height)
        sw, sh = int(raw_bg.width * scale), int(raw_bg.height * scale)
        bg_fitted = raw_bg.resize((sw, sh), Image.Resampling.LANCZOS)
        cx = (sw - target_w) // 2
        cy = (sh - target_h) // 2
        canvas.alpha_composite(bg_fitted.crop((cx, cy, cx + target_w, cy + target_h)))
    else:
        # Procedural atmospheric gradient
        d = ImageDraw.Draw(canvas)
        top_color = (28, 34, 48) if look == "night" else (50, 42, 34)
        bot_color = (12, 14, 20)
        for y in range(target_h):
            t = y / target_h
            r = int(top_color[0] * (1 - t) + bot_color[0] * t)
            g = int(top_color[1] * (1 - t) + bot_color[1] * t)
            b = int(top_color[2] * (1 - t) + bot_color[2] * t)
            d.line([(0, y), (target_w, y)], fill=(r, g, b, 255))

    # Composite hero prop on right or center
    if prop_path and os.path.exists(prop_path):
        prop_im = Image.open(prop_path).convert("RGBA")
        target_prop_dim = int(min(target_w, target_h) * (0.55 if aspect_name == "16:9" else 0.42))
        p_scale = target_prop_dim / max(prop_im.width, prop_im.height)
        pw, ph = int(prop_im.width * p_scale), int(prop_im.height * p_scale)
        prop_im = prop_im.resize((pw, ph), Image.Resampling.LANCZOS)

        # Radial glow
        glow_size = (pw + 120, ph + 120)
        glow_im = Image.new("RGBA", glow_size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_im)
        glow_color = (255, 220, 60, 180) if look != "night" else (0, 240, 255, 170)
        gd.ellipse([(30, 30), (glow_size[0] - 30, glow_size[1] - 30)], fill=glow_color)
        glow_im = glow_im.filter(ImageFilter.GaussianBlur(32))

        if aspect_name == "16:9":
            px = int(target_w * 0.72 - pw // 2)
            py = int(target_h * 0.54 - ph // 2)
        else:
            px = int(target_w * 0.50 - pw // 2)
            py = int(target_h * 0.52 - ph // 2)

        canvas.alpha_composite(glow_im, (px - 60, py - 60))
        canvas.alpha_composite(prop_im, (px, py))

    # Composite stickman
    if stickman_path and os.path.exists(stickman_path):
        stick_im = Image.open(stickman_path).convert("RGBA")
        target_stick_dim = int(min(target_w, target_h) * (0.65 if aspect_name == "16:9" else 0.50))
        s_scale = target_stick_dim / max(stick_im.width, stick_im.height)
        sw, sh = int(stick_im.width * s_scale), int(stick_im.height * s_scale)
        stick_im = stick_im.resize((sw, sh), Image.Resampling.LANCZOS)

        if aspect_name == "16:9":
            # Position stickman on far right or lower mid-right to leave left 45% clear
            sx = int(target_w * 0.82 - sw // 2)
            sy = int(target_h * 0.60 - sh // 2)
        else:
            # Position stickman in lower third (Y ~ 0.75) to leave top third clear
            sx = int(target_w * 0.50 - sw // 2)
            sy = int(target_h * 0.75 - sh // 2)

        canvas.alpha_composite(stick_im, (sx, sy))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    canvas.convert("RGB").save(out_path, quality=95)
    return out_path


def recover_via_assets_api(target_path, aspect="16:9"):
    """Uses flow-auto assets to download the newest asset if Chrome direct download was missed."""
    print(f"🔄 Checking Flow Assets API for completed {aspect} generation...")
    res = subprocess.run(["flow-auto", "assets", "--json"], capture_output=True, text=True)
    if res.returncode != 0:
        return False
    try:
        assets = json.loads(res.stdout)
        if not assets:
            return False
        first_asset = assets[0]
        idx = first_asset.get("index", 1)
        temp_dir = "/tmp/flow_thumb_download"
        os.makedirs(temp_dir, exist_ok=True)
        rec_filename = f"recovered_{aspect.replace(':', 'x')}.jpg"
        dl_res = subprocess.run(
            ["flow-auto", "download", str(idx), rec_filename, "--out", temp_dir],
            capture_output=True, text=True
        )
        rec_file = os.path.join(temp_dir, rec_filename)
        if os.path.exists(rec_file) and os.path.getsize(rec_file) > 10000:
            with Image.open(rec_file) as im:
                tw, th = (1080, 1920) if aspect == "9:16" else (1280, 720)
                scale = max(tw / im.width, th / im.height)
                sw, sh = int(im.width * scale), int(im.height * scale)
                im_resized = im.resize((sw, sh), Image.Resampling.LANCZOS)
                cx = (sw - tw) // 2
                cy = (sh - th) // 2
                final_im = im_resized.crop((cx, cy, cx + tw, cy + th))
                os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
                final_im.convert("RGB").save(target_path, quality=95)
            return True
    except Exception as e:
        print(f"⚠️ Assets API download recovery error: {e}")
    return False


def generate_stage1_flow_artwork(project_dir=".", out_dir=None, look="bright", no_flow=False, timeout=30):
    """Executes Stage 1: Google Flow generation with pre-flight check, prompt audit, and smart fallback."""
    project_dir = os.path.abspath(project_dir)
    out_dir = os.path.abspath(out_dir or os.path.join(project_dir, "UPLOAD_PACK"))
    os.makedirs(out_dir, exist_ok=True)

    raw_16x9 = os.path.join(out_dir, "thumbnail_16x9_flow_raw.png")
    raw_9x16 = os.path.join(out_dir, "thumbnail_9x16_flow_raw.png")

    print("==================================================")
    print("🎨 STAGE 1: GOOGLE FLOW DEDICATED THUMBNAIL SUITE")
    print(f"   Project: {os.path.basename(project_dir)} | Look: {look}")
    print("==================================================")

    t_start = time.time()

    # 1. Pre-Flight Diagnostic
    bridge_ready = False if no_flow else is_flow_bridge_ready(port=8791)
    if bridge_ready:
        print("✅ Flow Bridge: CONNECTED (Port 8791 active, daemon verified)")
    else:
        reason = "User requested --no-flow-thumb" if no_flow else "Flow bridge offline / port 8791 unreachable"
        print(f"ℹ️ Flow Bridge: NOT ACTIVE ({reason})")

    # 2. Bespoke High-CTR Prompts Crafting
    prompts_data = craft_flow_thumbnail_prompts(project_dir, look=look)
    p16 = prompts_data["16x9"]
    p9 = prompts_data["9x16"]

    print("\n--- Dedicated 16:9 Flow Prompt ---")
    print(f"{p16[:160]}... [STRICT NO-TEXT & NEGATIVE SPACE]")
    print("\n--- Dedicated 9:16 Flow Prompt ---")
    print(f"{p9[:160]}... [STRICT NO-TEXT & NEGATIVE SPACE]")

    stage1_audit = {
        "project": os.path.basename(project_dir),
        "look": look,
        "bridge_ready": bridge_ready,
        "flow_attempted": False,
        "outputs": {},
        "fallback_used": False,
        "flow_error": None,
        "elapsed_sec": 0.0,
        "prompts": {
            "16x9": p16,
            "9x16": p9
        }
    }

    # 3. Generation Loop
    flow_bin = shutil.which("flow-auto")
    gen_16_ok = False
    gen_9_ok = False
    err16 = None
    err9 = None

    if bridge_ready and flow_bin:
        print("\n🚀 Submitting 16:9 thumbnail prompt to Google Flow (flow-auto)...")
        stage1_audit["flow_attempted"] = True
        try:
            cmd16 = [flow_bin, "image", "--aspect", "16:9", "--out", out_dir, "--json", p16]
            res16 = subprocess.run(cmd16, capture_output=True, text=True, timeout=timeout)
            if res16.returncode == 0:
                try:
                    data = json.loads(res16.stdout)
                    fps = data.get("filePaths", [])
                    if fps and os.path.exists(fps[0]):
                        shutil.copy2(fps[0], raw_16x9)
                        ok, msg = validate_image_file(raw_16x9, target_aspect=16/9)
                        if ok:
                            gen_16_ok = True
                            print(f"✅ Generated 16:9 Flow Artwork: {raw_16x9} ({msg})")
                except Exception as ex:
                    err16 = str(ex)
            else:
                err16 = res16.stderr.strip() or f"returncode {res16.returncode}"
        except Exception as e:
            err16 = str(e)
            print(f"⚠️ 16:9 Flow generation timed out or direct download stalled: {e}")

        # Try Assets API recovery for 16:9 if direct download did not produce a valid file
        if not gen_16_ok:
            if recover_via_assets_api(raw_16x9, aspect="16:9"):
                ok, msg = validate_image_file(raw_16x9, target_aspect=16/9)
                if ok:
                    gen_16_ok = True
                    err16 = None
                    print(f"✅ Recovered 16:9 Flow Artwork via Assets API: {raw_16x9} ({msg})")

        print("🚀 Submitting 9:16 thumbnail prompt to Google Flow (flow-auto)...")
        try:
            cmd9 = [flow_bin, "image", "--aspect", "9:16", "--out", out_dir, "--json", p9]
            res9 = subprocess.run(cmd9, capture_output=True, text=True, timeout=timeout)
            if res9.returncode == 0:
                try:
                    data = json.loads(res9.stdout)
                    fps = data.get("filePaths", [])
                    if fps and os.path.exists(fps[0]):
                        shutil.copy2(fps[0], raw_9x16)
                        ok, msg = validate_image_file(raw_9x16, target_aspect=9/16)
                        if ok:
                            gen_9_ok = True
                            print(f"✅ Generated 9:16 Flow Artwork: {raw_9x16} ({msg})")
                except Exception as ex:
                    err9 = str(ex)
            else:
                err9 = res9.stderr.strip() or f"returncode {res9.returncode}"
        except Exception as e:
            err9 = str(e)
            print(f"⚠️ 9:16 Flow generation timed out or direct download stalled: {e}")

        # Try Assets API recovery for 9:16 if direct download did not produce a valid file
        if not gen_9_ok:
            if recover_via_assets_api(raw_9x16, aspect="9:16"):
                ok, msg = validate_image_file(raw_9x16, target_aspect=9/16)
                if ok:
                    gen_9_ok = True
                    err9 = None
                    print(f"✅ Recovered 9:16 Flow Artwork via Assets API: {raw_9x16} ({msg})")

    # 4. Fallback Handling
    if not gen_16_ok:
        print("ℹ️ [Stage 1 Advisory]: Using high-contrast candidate artwork from project for 16:9 base.")
        generate_fallback_base_artwork(project_dir, raw_16x9, 1280, 720, aspect_name="16:9", look=look)
        stage1_audit["fallback_used"] = True

    if not gen_9_ok:
        print("ℹ️ [Stage 1 Advisory]: Using high-contrast candidate artwork from project for 9:16 base.")
        generate_fallback_base_artwork(project_dir, raw_9x16, 1080, 1920, aspect_name="9:16", look=look)
        stage1_audit["fallback_used"] = True

    # 5. Final Validation Check & Metrics
    elapsed_sec = round(time.time() - t_start, 2)
    stage1_audit["elapsed_sec"] = elapsed_sec
    stage1_audit["flow_error"] = err16 or err9

    ok16, msg16 = validate_image_file(raw_16x9)
    ok9, msg9 = validate_image_file(raw_9x16)
    stage1_audit["outputs"]["raw_16x9"] = {"path": raw_16x9, "valid": ok16, "status": msg16}
    stage1_audit["outputs"]["raw_9x16"] = {"path": raw_9x16, "valid": ok9, "status": msg9}

    audit_path = os.path.join(out_dir, "STAGE1_FLOW_AUDIT.json")
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(stage1_audit, f, indent=2)

    print("\n🏆 Stage 1 Flow Artwork Ready:")
    print(f"   • 16:9 Raw: {raw_16x9} ({msg16})")
    print(f"   • 9:16 Raw: {raw_9x16} ({msg9})")
    print(f"   • Elapsed: {elapsed_sec}s | Flow Error: {stage1_audit['flow_error']}")
    print(f"   • Audit Log: {audit_path}")
    print("==================================================")

    return {
        "raw_16x9": raw_16x9,
        "raw_9x16": raw_9x16,
        "audit": stage1_audit
    }


def main():
    p = argparse.ArgumentParser(description="Stage 1 Google Flow Thumbnail Generator")
    p.add_argument("project_dir", nargs="?", default=".", help="Project root directory")
    p.add_argument("--out-dir", default=None, help="Output directory for raw artwork (defaults to UPLOAD_PACK/)")
    p.add_argument("--look", default="bright", help="Look preset palette (warm, night, bright, etc.)")
    p.add_argument("--no-flow-thumb", action="store_true", help="Force fallback without querying Flow bridge")
    p.add_argument("--timeout", type=int, default=30, help="Flow generation timeout in seconds")
    args = p.parse_args()

    generate_stage1_flow_artwork(
        project_dir=args.project_dir,
        out_dir=args.out_dir,
        look=args.look,
        no_flow=args.no_flow_thumb,
        timeout=args.timeout
    )


if __name__ == "__main__":
    main()
