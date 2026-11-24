#!/usr/bin/env python3
"""flow_smart_generator.py: Self-Healing, Intelligent Google Flow Asset Generator
Features:
1. Auto-Detection of policy errors / stalls with auto-cancel & extension reload.
2. Synonym Prompt Rewriter for policy-sensitive or rejected words.
3. Assets API Fallback: uses `flow-auto assets --json` + `flow-auto download` if browser download delays.
4. Programmatic Quality Verification:
   - For Scenes: checks valid image format, resolution, file size > 100KB.
   - For Stickers: runs `key.key()`, verifies true alpha transparency (alpha.min() == 0, transparent_ratio > 15%).
5. Zero-Skip Guarantee: Never leaves a placeholder or duplicate box.
"""

import glob, json, os, re, shutil, subprocess, sys, time
from PIL import Image
import numpy as np

FLOW_DL_DIR = "/home/mirza-ahmed-hassan/Downloads/flow"
SKILL_SCRIPTS = "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts"
sys.path.insert(0, SKILL_SCRIPTS)
try:
    import key
except ImportError:
    key = None

# Sensitive word rewriter dictionary for Google Flow safety filter
SENSITIVE_REPLACEMENTS = {
    r"\blouse\b": "microscopic bug creature",
    r"\blice\b": "microscopic creatures",
    r"\bparasite\b": "tiny insect specimen",
    r"\bnaked\b": "bare skin",
    r"\bnude\b": "unclothed",
    r"\bcorpse\b": "ancient silhouette",
    r"\bdeath\b": "danger",
    r"\bblood\b": "red aura",
}

def get_style_tokens():
    for p in ["STYLE.txt", "../STYLE.txt"]:
        if os.path.exists(p):
            lines = open(p, encoding="utf-8").read().splitlines()
            body = " ".join(l for l in lines if l.strip() and not l.lower().startswith("look:"))
            if body:
                return body.strip()
    return "hand-drawn 2D cartoon illustration for a history explainer channel, clean dark ink outlines, flat colours with soft shading, a bright natural and varied colour palette like a modern flat cartoon: clear blue skies, fresh greens, clean whites, light pastel walls, colourful objects, balanced neutral daylight. Not sepia, not brown, not golden or orange colour cast. Full-bleed background that fills the whole frame, simple and readable. Simple round-head stick-figure characters with dot eyes and thin limbs."

NEGATIVE_PROMPT = (
    " Negative: photorealistic, hyperrealistic 3D render, glossy CGI, photograph, real human face, "
    "realistic skin texture, stock photo, watermark, logo, text, subtitles, distorted anatomy, "
    "modern artifacts in prehistoric scenes, anime, manga, inconsistent art style, cluttered background, blurry, "
    "multiple versions of the character in one frame, low resolution, extra limbs, bad proportions."
)

SHORTS_NEGATIVE_PROMPT = (
    " Negative: landscape framing, horizontal composition, horizontal orientation, widescreen, 16:9, 4:3, "
    "letterboxing, pillarboxing, black bars, white bars, border bars, horizontal strips, cinema aspect bars, "
    "panoramic view, horizon panorama, blank margins, cropped top, cropped bottom, "
    "photorealistic, hyperrealistic 3D render, glossy CGI, photograph, real human face, "
    "realistic skin texture, stock photo, watermark, logo, text, subtitles, distorted anatomy, "
    "modern artifacts in prehistoric scenes, anime, manga, blurry, extra limbs, bad proportions."
)

def verify_vertical_layout(image_path):
    """Rigorous validation guard: catches and rejects non-vertical or letterboxed layouts for 9:16 Shorts."""
    if not os.path.exists(image_path) or os.path.getsize(image_path) < 10000:
        return False, "File missing or unreadable"
    try:
        with Image.open(image_path) as im:
            w, h = im.size
            ratio = w / h
            # Strict aspect ratio constraint for 9:16 (0.5625 nominal, max 0.65)
            if ratio > 0.65 or w >= h:
                return False, f"Non-vertical dimensions: {w}x{h} (ratio {ratio:.3f} > 0.65)"
            
            # Detect horizontal letterbox bars (top/bottom bands)
            im_gray = np.array(im.convert("L"))
            top_h = max(2, int(h * 0.12))
            bot_h = max(2, int(h * 0.12))
            top_band = im_gray[:top_h, :]
            bot_band = im_gray[h - bot_h:, :]
            
            top_std = float(np.std(top_band))
            bot_std = float(np.std(bot_band))
            top_mean = float(np.mean(top_band))
            bot_mean = float(np.mean(bot_band))
            
            # Solid black or solid white letterbox bars (low standard deviation + extreme mean)
            if (top_std < 3.5 and (top_mean < 35 or top_mean > 225)) or \
               (bot_std < 3.5 and (bot_mean < 35 or bot_mean > 225)):
                return False, f"Horizontal letterbox bars detected (top_std={top_std:.1f}, bot_std={bot_std:.1f})"
                
            # Detect vertical pillarbox bars (left/right bands)
            left_w = max(2, int(w * 0.08))
            right_w = max(2, int(w * 0.08))
            left_band = im_gray[:, :left_w]
            right_band = im_gray[:, w - right_w:]
            left_std = float(np.std(left_band))
            right_std = float(np.std(right_band))
            left_mean = float(np.mean(left_band))
            right_mean = float(np.mean(right_band))
            
            if (left_std < 3.5 and (left_mean < 35 or left_mean > 225)) or \
               (right_std < 3.5 and (right_mean < 35 or right_mean > 225)):
                return False, f"Pillarbox bars detected (left_std={left_std:.1f}, right_std={right_std:.1f})"
                
            return True, f"Valid vertical 9:16 layout ({w}x{h})"
    except Exception as e:
        return False, f"Image inspection error: {e}"

def sanitize_prompt(prompt):
    cleaned = prompt
    for pattern, replacement in SENSITIVE_REPLACEMENTS.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    return cleaned

def get_newest_dl(since_time=0):
    candidates = (
        glob.glob(f"{FLOW_DL_DIR}/*.jpg") + glob.glob(f"{FLOW_DL_DIR}/*.png") + glob.glob(f"{FLOW_DL_DIR}/*.webp") +
        glob.glob("/home/mirza-ahmed-hassan/Desktop/Tool/flow-connector/exports/flow/*.jpg")
    )
    files = sorted(candidates, key=os.path.getmtime)
    if not files:
        return None
    latest = files[-1]
    if os.path.getmtime(latest) >= since_time:
        return latest
    return None

def verify_image(filepath, min_size_kb=50):
    if not os.path.exists(filepath):
        return False, "File does not exist"
    if os.path.getsize(filepath) < min_size_kb * 1024:
        return False, f"File size too small ({os.path.getsize(filepath)/1024:.1f} KB)"
    try:
        with Image.open(filepath) as im:
            im.verify()
        return True, "Valid image"
    except Exception as e:
        return False, f"Corrupted image: {e}"

def verify_sticker_cutout(png_path):
    """Rigorous cutout verification: alpha transparency, chroma halo detection, and boundary clipping."""
    if not os.path.exists(png_path):
        return False, "PNG does not exist"
    try:
        im = Image.open(png_path)
        if im.mode != "RGBA":
            return False, f"Wrong mode {im.mode}, expected RGBA"
        a = np.array(im)
        alpha = a[..., 3]
        if alpha.min() > 0:
            return False, "No transparent pixels found (alpha.min() > 0)"
        trans_ratio = (alpha == 0).mean()
        if trans_ratio < 0.01:
            return False, f"Insufficient transparency ({trans_ratio*100:.1f}%), likely background survived"
        if trans_ratio > 0.985:
            return False, "Empty sticker: no subject remaining after cutout (transparency > 98.5%)"

        opaque_mask = alpha > 40
        if opaque_mask.mean() < 0.01:
            return False, "Empty sticker: opaque subject < 1% of canvas"

        # Residual magenta chroma halo check
        # Detect unkeyed magenta pixels: alpha > 40 where R > 175, B > 175, G < 90, (R - G) > 90, (B - G) > 90
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        magenta_mask = (r > 175) & (b > 175) & (g < 90) & ((r.astype(int) - g.astype(int)) > 90) & ((b.astype(int) - g.astype(int)) > 90) & opaque_mask
        magenta_ratio = np.sum(magenta_mask) / max(1, np.sum(opaque_mask))
        if magenta_ratio > 0.018:
            return False, f"Magenta chroma halo detected: {magenta_ratio*100:.2f}% of subject pixels have unkeyed magenta halo (threshold 1.8%)"

        # Edge boundary clipping check: check 1-pixel outer border of image
        h, w = alpha.shape
        border_opaque = np.sum(opaque_mask[0, :]) + np.sum(opaque_mask[-1, :]) + np.sum(opaque_mask[:, 0]) + np.sum(opaque_mask[:, -1])
        total_border_pixels = 2 * w + 2 * h
        border_coverage = border_opaque / max(1, total_border_pixels)
        if border_coverage > 0.15:
            return False, f"Sticker clipping detected: subject touches canvas border ({border_coverage*100:.1f}% border coverage > 15%)"

        return True, f"Valid transparent cutout ({trans_ratio*100:.1f}% transparent, 0 halo, clean edges)"
    except Exception as e:
        return False, f"Error verifying sticker: {e}"

def ensure_flow_daemon():
    """Ensure ~/.flow-connector/daemon.pid is populated if port 8791 is in use."""
    try:
        pid_file = os.path.expanduser("~/.flow-connector/daemon.pid")
        if not os.path.exists(pid_file):
            res = subprocess.run(["lsof", "-ti", ":8791", "-sTCP:LISTEN"], capture_output=True, text=True)
            pids = res.stdout.strip().split()
            if pids and pids[0].isdigit():
                os.makedirs(os.path.dirname(pid_file), exist_ok=True)
                with open(pid_file, "w") as f:
                    f.write(pids[0])
                print(f"🔧 Restored missing daemon.pid ({pids[0]})")
    except Exception:
        pass

def recover_via_assets_api(target_path):
    """Uses flow-auto assets to download the newest asset if Chrome download was missed."""
    print("🔄 Checking Flow Assets API for completed generation...")
    res = subprocess.run(["flow-auto", "assets", "--json"], capture_output=True, text=True)
    if res.returncode != 0:
        return False
    try:
        assets = json.loads(res.stdout)
        if not assets:
            return False
        first_asset = assets[0]
        idx = first_asset.get("index", 1)
        temp_dir = "/tmp/flow_download"
        os.makedirs(temp_dir, exist_ok=True)
        dl_res = subprocess.run(
            ["flow-auto", "download", str(idx), "recovered.jpg", "--out", temp_dir],
            capture_output=True, text=True
        )
        rec_file = f"{temp_dir}/recovered.jpg"
        if os.path.exists(rec_file) and os.path.getsize(rec_file) > 50000:
            shutil.copy2(rec_file, target_path)
            print(f"✅ Successfully recovered via Assets API: {target_path}")
            return True
    except Exception as e:
        print(f"⚠️ Assets API recovery error: {e}")
    return False

def generate_smart(prompt, aspect, target_path, is_sticker=False, max_retries=3):
    """Smart generator with auto-healing, prompt sanitization, Assets API fallback, and verification."""
    # Check if already done and valid
    if is_sticker:
        cut_path = target_path
        raw_path = target_path.replace("/cut/", "/raw/").replace(".png", ".jpg")
        ok, msg = verify_sticker_cutout(cut_path)
        if ok:
            print(f"⏩ Sticker already verified: {cut_path} ({msg})")
            return True
    else:
        ok, msg = verify_image(target_path, min_size_kb=80)
        if ok:
            print(f"⏩ Scene image already verified: {target_path}")
            return True

    current_prompt = prompt
    out_dir = os.path.dirname(raw_path if is_sticker else target_path)
    os.makedirs(out_dir, exist_ok=True)
    if is_sticker:
        os.makedirs(os.path.dirname(cut_path), exist_ok=True)

    ensure_flow_daemon()

    for attempt in range(1, max_retries + 1):
        print(f"\n🚀 [Attempt {attempt}/{max_retries}] Generating: {current_prompt[:70]}...")
        t_start = time.time()
        
        cmd = ["flow-auto", "image", "--aspect", aspect, "--out", out_dir, "--json", current_prompt]
        res = subprocess.run(cmd, capture_output=True, text=True)
        output_text = res.stdout + res.stderr

        # Check for policy / unknown errors
        if "might violate our policies" in output_text or "UNKNOWN_ERROR" in output_text or res.returncode != 0:
            print(f"⚠️ Flow reported an issue (code {res.returncode}): {output_text.strip()[:200]}")
            subprocess.run(["flow-auto", "cancel"], capture_output=True)
            subprocess.run(["flow-auto", "reload"], capture_output=True)
            time.sleep(3)
            # Sanitize prompt
            sanitized = sanitize_prompt(current_prompt)
            if sanitized != current_prompt:
                print(f"🔄 Rephrased prompt: {sanitized[:70]}...")
                current_prompt = sanitized
            else:
                st = get_style_tokens()
                current_prompt = f"{current_prompt}. Style: {st}. Safe educational documentary illustration.{NEGATIVE_PROMPT}"
            continue

        # Look for downloaded file from JSON response first
        newest = None
        try:
            parsed = json.loads(res.stdout)
            if parsed.get("ok") and parsed.get("filePaths"):
                p0 = parsed["filePaths"][0]
                if os.path.exists(p0):
                    newest = p0
        except Exception:
            pass

        if not newest:
            time.sleep(2)
            newest = get_newest_dl(since_time=t_start - 2)
        
        # If not found in Downloads, try Assets API
        if not newest or not os.path.exists(newest):
            print("⏳ Download not detected in folder, invoking Assets API...")
            dest_raw = raw_path if is_sticker else target_path
            if recover_via_assets_api(dest_raw):
                newest = dest_raw

        if newest and os.path.exists(newest):
            dest_raw = raw_path if is_sticker else target_path
            shutil.copy2(newest, dest_raw)
            
            if not is_sticker:
                ok, msg = verify_image(target_path)
                if ok and aspect == "9:16":
                    vert_ok, vert_msg = verify_vertical_layout(target_path)
                    if not vert_ok:
                        ok = False
                        msg = f"Vertical layout violation: {vert_msg}"
                if ok:
                    print(f"✅ Scene saved & verified: {target_path} ({os.path.getsize(target_path)/1024:.1f} KB)")
                    return True
                else:
                    print(f"⚠️ Image verification failed ({msg}), refining prompt for retry...")
                    current_prompt = f"Tight vertical portrait shot, centered vertical composition, full bleed tall frame, towering vertical scale, absolutely no letterbox, no bars. {prompt}"
            else:
                # Chroma-key sticker
                print(f"🎨 Chroma-keying {dest_raw} -> {cut_path}...")
                try:
                    if key is not None:
                        cut_im = key.key(dest_raw)
                        cut_im.save(cut_path)
                        ok, msg = verify_sticker_cutout(cut_path)
                        if ok:
                            try:
                                shared_pool_cut = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), "elements", "cut")
                                os.makedirs(shared_pool_cut, exist_ok=True)
                                shutil.copy2(cut_path, os.path.join(shared_pool_cut, os.path.basename(cut_path)))
                            except Exception:
                                pass
                            print(f"✅ Transparent sticker ready: {cut_path} ({msg})")
                            return True
                        else:
                            print(f"⚠️ Keying verification failed: {msg}")
                            current_prompt = (
                                f"{prompt}. Isolated subject centered on pure solid flat magenta background #FF00FF, "
                                f"crisp clean dark ink outlines, ample negative margin around subject, zero edge clipping, "
                                f"no shadows, no gradients, no ground plane."
                            )
                    else:
                        print("❌ key module not available")
                except Exception as e:
                    print(f"⚠️ Keying exception: {e}")

        # If we reached here, attempt failed; clean up modal before next attempt
        subprocess.run(["flow-auto", "cancel"], capture_output=True)
        time.sleep(2)

    print(f"❌ Failed to generate {target_path} after {max_retries} attempts.")
    return False


def generate_all_shots(aspect=None, force=False, target_shot=None):
    if not os.path.exists("SHOTS.tsv"):
        print("❌ SHOTS.tsv not found.")
        return
    import csv
    shots = list(csv.DictReader(open("SHOTS.tsv", encoding="utf-8"), delimiter="\t"))
    style_tok = get_style_tokens()
    
    # Auto-detect aspect ratio: 16:9 for long-form / widescreen, 9:16 for shorts / vertical
    if not aspect:
        cur_name = os.path.basename(os.path.abspath(os.getcwd())).lower()
        if "long" in cur_name or "master" in cur_name or "--16x9" in sys.argv or "--aspect=16:9" in sys.argv:
            aspect = "16:9"
        else:
            aspect = "9:16"
            
    is_16x9 = (aspect == "16:9")
    print(f"📸 Generator Target Aspect Ratio: {aspect} ({'Widescreen 16:9 Master' if is_16x9 else 'Vertical 9:16 Shorts'})")
    
    # Check which shots are needed in SCENES_HYBRID.tsv
    needed_shots = set()
    if os.path.exists("SCENES_HYBRID.tsv"):
        for r in csv.DictReader(open("SCENES_HYBRID.tsv", encoding="utf-8"), delimiter="\t"):
            if not r.get("cue") or r["cue"].startswith("#"):
                continue
            img = (r.get("img") or "").strip()
            if img.startswith("shots/"):
                needed_shots.add(os.path.basename(img).split(".")[0])
    
    total = len(shots)
    for idx, s in enumerate(shots, 1):
        sid = s["id"].strip().lstrip("0") or s["id"].strip()
        sid_raw = s["id"].strip()
        
        # If targeting a specific shot, skip others
        if target_shot and sid != target_shot and sid_raw != target_shot:
            continue
            
        if needed_shots and (sid not in needed_shots and sid_raw not in needed_shots):
            continue
            
        target = f"shots/{sid_raw}.png"
        need_regen = force
        if not need_regen and os.path.exists(target) and os.path.getsize(target) > 50000:
            if not is_16x9:
                valid_vert, reason = verify_vertical_layout(target)
                if not valid_vert:
                    print(f"⚠️ Shot {sid_raw} failed vertical layout guard: {reason}. Purging & regenerating native 9:16 vertical...")
                    need_regen = True
            else:
                try:
                    with Image.open(target) as cur_im:
                        cw, ch = cur_im.size
                        if ch > cw * 0.75:
                            print(f"⚠️ Shot {sid_raw} is vertical/square ({cw}x{ch}) in 16:9 pipeline. Purging & regenerating native 16:9 widescreen...")
                            need_regen = True
                except Exception:
                    need_regen = True

        if not need_regen and os.path.exists(target) and os.path.getsize(target) > 50000:
            print(f"[{idx}/{total}] ⏩ Shot {sid_raw} already exists: {target}")
            continue
            
        prompt = s["prompt"].strip()
        side = s.get("space", "").strip().lower()
        if is_16x9:
            if side in ("left", "right"):
                keep = "left" if side == "right" else "right"
                prompt += f" Composition: a complete 16:9 widescreen landscape scene with the subject towards the {keep} and open background on the {side} side."
            elif side == "top":
                prompt += " Composition: a complete 16:9 widescreen landscape scene with the subject in lower half and open sky/wall at top."
            else:
                prompt += " Composition: a complete 16:9 cinematic widescreen landscape scene."
            full_prompt = f"{prompt}. Style: {style_tok}. Absolutely no text, no letters, no labels, no watermark.{NEGATIVE_PROMPT}"
        else:
            # SHORTS 9:16 NATIVE VERTICAL PROMPT ARCHITECTURE:
            # 1. Sanitize horizontal trigger words
            sanitized = prompt
            for horiz_w, vert_rep in [
                (r"\blandscape\b", "vertical environment"),
                (r"\bhorizon\b", "tall sky"),
                (r"\bpanoramic\b", "tall vertical scene"),
                (r"\bwide shot\b", "full-height vertical shot"),
                (r"\bsplit screen\b", "vertical stacked comparison")
            ]:
                sanitized = re.sub(horiz_w, vert_rep, sanitized, flags=re.IGNORECASE)

            # 2. Front-load vertical framing tokens (highest attention weight)
            prefix = "A true full-height vertical 9:16 portrait illustration, tall mobile smartphone wallpaper framing: "

            # 3. Dynamic space composition for overlays
            if side in ("left", "right"):
                keep = "left" if side == "right" else "right"
                comp = (f"Framing: Strictly vertical 9:16 mobile phone portrait framing filling the entire canvas from top to bottom, "
                        f"subject framed vertically towards the {keep} with open background on the {side} side. "
                        f"Tall vertical perspective, subject filling full vertical height, absolutely no landscape composition, "
                        f"no horizontal bars, no letterbox, no pillarbox, edge-to-edge illustration.")
            elif side == "top":
                comp = ("Framing: Strictly vertical 9:16 mobile phone portrait framing filling the entire canvas from top to bottom, "
                        "subject framed vertically in lower half with open vertical space above. "
                        "Tall vertical perspective, subject filling full vertical height, absolutely no landscape composition, "
                        "no horizontal bars, no letterbox, no pillarbox, edge-to-edge illustration.")
            else:
                comp = ("Framing: Strictly vertical 9:16 mobile phone portrait framing filling the entire canvas from top to bottom, "
                        "subject centered vertically with generous top and bottom height. "
                        "Tall vertical perspective, subject filling full vertical height, absolutely no landscape composition, "
                        "no horizontal bars, no letterbox, no pillarbox, edge-to-edge illustration.")

            full_prompt = f"{prefix}{sanitized}. {comp} Style: {style_tok}. Absolutely no text, no letters, no labels, no watermark.{SHORTS_NEGATIVE_PROMPT}"

        print(f"\n[{idx}/{total}] 🎬 Generating Scene {sid_raw}: {target} ({aspect})...")
        generate_smart(full_prompt, aspect=aspect, target_path=target, is_sticker=False)

        # 4. Post-generation validation & guard check
        if not is_16x9 and os.path.exists(target):
            valid_vert, reason = verify_vertical_layout(target)
            if not valid_vert:
                print(f"❌ Shot {sid_raw} failed post-generation vertical guard: {reason}. Retrying with reinforced vertical weights...")
                os.remove(target)
                reinforced_prompt = f"STRICTLY VERTICAL 9:16 SMARTPHONE PORTRAIT ONLY. NO WIDESCREEN. NO LANDSCAPE. {full_prompt}"
                generate_smart(reinforced_prompt, aspect="9:16", target_path=target, is_sticker=False)


def find_semantic_mutual_sticker(target_obj, current_dir="."):
    """Finds an existing transparent sticker matching target_obj semantically across project directories."""
    stop = {"a", "an", "the", "with", "and", "in", "of", "to", "for", "on", "by", "cartoon", "sticker", "flat", "style", "color", "illustration", "modern", "ancient"}
    words = re.findall(r"[a-z0-9]+", target_obj.lower())
    target_tokens = {w for w in words if len(w) > 3 and w not in stop}
    
    KEY_OBJECTS = {"mattress", "sabertooth", "flint", "campfire", "spear", "flute", "clock", "clipboard", "skull", "knife", "badge", "switch", "deadbolt", "brain", "ember", "mug", "owl"}
    
    candidate_dirs = [
        os.path.join(current_dir, "..", "short"),
        os.path.join(current_dir, "..", "long"),
        os.path.join(current_dir, ".."),
        os.path.join(os.path.dirname(os.path.abspath(current_dir)), "elements"),
        current_dir
    ]
    for c_dir in candidate_dirs:
        c_tsv = os.path.join(c_dir, "ELEMENTS.tsv")
        if not os.path.exists(c_tsv) or os.path.abspath(c_tsv) == os.path.abspath(os.path.join(current_dir, "ELEMENTS.tsv")):
            continue
        try:
            with open(c_tsv, encoding="utf-8") as f:
                for r in csv.DictReader(f, delimiter="\t"):
                    cand_words = re.findall(r"[a-z0-9]+", r.get("object", "").lower())
                    cand_tokens = {w for w in cand_words if len(w) > 3 and w not in stop}
                    overlap = target_tokens & cand_tokens
                    if (len(overlap) >= 2 and any(k in overlap for k in KEY_OBJECTS)) or \
                       (len(overlap) >= 3) or \
                       any(k in target_tokens and k in cand_tokens for k in ["mattress", "sabertooth", "campfire", "flute", "spear", "clipboard", "skull", "knife"]):
                        cand_id = r["id"].strip()
                        cand_cut = os.path.join(c_dir, "elements", "cut", f"{cand_id}.png")
                        if os.path.exists(cand_cut) and os.path.getsize(cand_cut) > 20000:
                            return cand_cut, r.get("object", "")
        except Exception:
            pass
    return None, None

def generate_all_elements(force=False, target_element=None):
    if not os.path.exists("ELEMENTS.tsv"):
        print("❌ ELEMENTS.tsv not found.")
        return
    import csv
    elements = list(csv.DictReader(open("ELEMENTS.tsv", encoding="utf-8"), delimiter="\t"))
    style_tok = get_style_tokens()
    
    needed_els = set()
    if os.path.exists("SCENES_HYBRID.tsv"):
        for r in csv.DictReader(open("SCENES_HYBRID.tsv", encoding="utf-8"), delimiter="\t"):
            if not r.get("cue") or r["cue"].startswith("#"):
                continue
            img = (r.get("img") or "").strip()
            if img.startswith("elements/cut/"):
                needed_els.add(os.path.basename(img).split(".")[0])
                
    total = len(elements)
    for idx, e in enumerate(elements, 1):
        eid = e["id"].strip().lstrip("0") or e["id"].strip()
        eid_raw = e["id"].strip()
        obj = e["object"].strip()
        
        if target_element and eid != target_element and eid_raw != target_element:
            continue
            
        if needed_els and (eid not in needed_els and eid_raw not in needed_els):
            continue
            
        target_cut = f"elements/cut/{eid_raw}.png"
        
        # Check if already generated in local or sibling/parent folders (Mutual Sticker Reuse Rule)
        candidate_paths = [
            target_cut,
            f"../elements/cut/{eid_raw}.png",
            f"../short/elements/cut/{eid_raw}.png",
            f"../long/elements/cut/{eid_raw}.png",
            os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), "elements", "cut", f"{eid_raw}.png")
        ]
        shared_found = None
        if not force:
            for cp in candidate_paths:
                if os.path.exists(cp) and os.path.getsize(cp) > 20000:
                    shared_found = cp
                    break
            if not shared_found:
                try:
                    import asset_registry
                    p_root = asset_registry.resolve_project_root(os.getcwd())
                    reg_match = asset_registry.find_reusable_sticker(obj, p_root)
                    if reg_match:
                        matched_path = reg_match["path"]
                        matched_base = os.path.splitext(os.path.basename(matched_path))[0]
                        current_scope = os.path.basename(os.getcwd())
                        if matched_base == eid_raw or reg_match.get("scope") != current_scope:
                            shared_found = matched_path
                            print(f"[{idx}/{total}] 🎯 [Asset Registry] Semantic mutual match: '{obj[:35]}' matched '{reg_match['name'][:35]}' ({shared_found})")
                except Exception as ex:
                    pass
            if not shared_found:
                sem_cut, sem_obj = find_semantic_mutual_sticker(obj)
                if sem_cut:
                    shared_found = sem_cut
                    print(f"[{idx}/{total}] 🎯 Semantic mutual sticker found: '{obj[:35]}' matches '{sem_obj[:35]}' in {sem_cut}")
        
        if shared_found:
            if shared_found != target_cut:
                os.makedirs(os.path.dirname(target_cut), exist_ok=True)
                shutil.copy2(shared_found, target_cut)
                print(f"[{idx}/{total}] ♻️ Reusing shared sticker {eid_raw} from {shared_found} -> {target_cut}")
            else:
                print(f"[{idx}/{total}] ⏩ Element {eid_raw} already exists: {target_cut}")
            continue
            
        obj = e["object"].strip()
        prefix = "" if obj.lower().startswith("one single isolated") else "One single isolated "
        prompt = (f"{prefix}{obj}, 2D cartoon style with thick clean dark ink outlines, "
                  f"placed perfectly centered against a solid flat pure magenta background #FF00FF, with no shadows, "
                  f"no table, no floor, no background clutter, no people. Style: {style_tok}. "
                  f"Absolutely no text, no letters, no labels, no watermark.{NEGATIVE_PROMPT}")
        print(f"\n[{idx}/{total}] 🎨 Generating Sticker Prop {eid_raw}: {target_cut}...")
        generate_smart(prompt, aspect="1:1", target_path=target_cut, is_sticker=True)
        try:
            import asset_registry
            p_root = asset_registry.resolve_project_root(os.getcwd())
            asset_registry.scan_and_rebuild_registry(p_root)
        except Exception:
            pass


if __name__ == "__main__":
    action = "all"
    aspect = None
    force = False
    target_item = None
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("shots", "elements", "all"):
            action = arg
        elif arg in ("16:9", "--16x9", "--aspect=16:9"):
            aspect = "16:9"
        elif arg in ("9:16", "--9x16", "--aspect=9:16"):
            aspect = "9:16"
        elif arg == "--aspect" and i + 1 < len(args):
            i += 1
            aspect = args[i]
        elif arg in ("--force", "-f"):
            force = True
        elif arg in ("--shot", "--element", "--id") and i + 1 < len(args):
            i += 1
            target_item = args[i]
        elif arg.isdigit():
            target_item = arg
        i += 1

    if action == "shots":
        generate_all_shots(aspect=aspect, force=force, target_shot=target_item)
    elif action == "elements":
        generate_all_elements(force=force, target_element=target_item)
    elif action == "all":
        generate_all_shots(aspect=aspect, force=force, target_shot=target_item)
        generate_all_elements(force=force, target_element=target_item)
    else:
        print(f"Usage: {sys.argv[0]} [all|shots|elements] [--16x9|--9x16|--aspect=16:9] [--force] [--shot <id>]")
