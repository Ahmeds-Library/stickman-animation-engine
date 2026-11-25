#!/usr/bin/env python3
"""vfx_smart_designer.py: Intelligent Emotional VFX & Kinetic Animation Director
Enforces Pillar 1 (Sound, VFX, Music & Asset Intelligence) & Rule 56 (5-Pillar Visual Effects):
Automatically analyzes scene script, character actions, and voice keywords to populate
the `extra` and `space` columns of SCENES_HYBRID.tsv with context-aware VFX:
1. Camera Kinetics: zoom_punch (high-energy cut), shake (impact/fear), rumble (ambient dread).
2. Atmospheric Color Grades: danger/blood (peril), ice/frost (cold), bw/grayscale (historical gravity).
3. Transition Energy: flash (paradigm shift / title shock), crossfade (dreamy / time passage).
4. Sticker Physics: drop/slam (weapons, heavy stones, skulls), slide_left/right (comparisons), hover (ethereal/nocturnal).
5. Safe Spatial Layout: auto-allocates free screen space (left, right, top) away from focal characters.
"""

import os, sys, csv, re

DANGER_KEYWORDS = {
    "peril", "starvation", "predator", "deadly", "attack", "blood",
    "collapse", "crisis", "panic", "fatal", "ambush", "war",
    "battle", "invasion", "invaders", "siege", "earthquake", "burned",
    "destruction", "slaughter", "catastrophe", "famine", "plague"
}

COLD_KEYWORDS = {
    "ice", "cold", "freezing", "frost", "snow", "winter", "subzero",
    "glacier", "chill", "frozen", "arctic", "hypothermia"
}

TRAGEDY_HISTORICAL_KEYWORDS = {
    "extinct", "extinction", "dark age", "wiped out", "vanished forever", "lost forever"
}

HOOK_KEYWORDS = {
    "turns out", "actually", "shocking", "completely vanished", "wiped itself out"
}

IMPACT_KEYWORDS = {
    "earthquake", "shattered", "smash", "explosion", "explosion", "slam", "crushed"
}

HEAVY_STICKER_KEYWORDS = {
    "spear", "skull", "knife", "rock", "stone", "flint", "deadbolt",
    "anvil", "axe", "weapon", "bone", "hammer", "milestone", "groma",
    "pillar", "column", "shield", "armor", "sword", "paving", "block", "brick", "monument"
}

LATERAL_STICKER_KEYWORDS = {
    "switch", "clock", "clipboard", "price", "tag", "versus", "comparison",
    "option", "choice", "meter", "soldier", "runner", "courier", "horse",
    "chariot", "wagon", "traveler", "legionary", "legion"
}

HOVER_STICKER_KEYWORDS = {
    "owl", "moon", "star", "fire", "flame", "ember", "smoke", "spirit",
    "flute", "sound", "music", "ghost", "eagle", "spqr"
}

def analyze_and_enrich_scenes(project_dir="."):
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")
    if not os.path.exists(scenes_path):
        print(f"❌ No SCENES file found in {project_dir}")
        return False

    shots_tsv = os.path.join(project_dir, "SHOTS.tsv")
    shot_prompts = {}
    if os.path.exists(shots_tsv):
        with open(shots_tsv, encoding="utf-8") as sf:
            for r in csv.DictReader(sf, delimiter="\t"):
                sid = r.get("id", "").strip()
                prompt = r.get("prompt", "").strip().lower()
                if sid:
                    shot_prompts[sid] = prompt
                    shot_prompts[f"shots/{sid}.png"] = prompt
                    shot_prompts[f"shots/{sid}.jpg"] = prompt

    lines_tsv = os.path.join(project_dir, "LINES.tsv")
    line_texts = {}
    if os.path.exists(lines_tsv):
        with open(lines_tsv, encoding="utf-8") as lf:
            for r in csv.DictReader(lf, delimiter="\t"):
                lid = r.get("id", "").strip()
                txt = r.get("text", "").strip().lower()
                if lid:
                    line_texts[lid] = txt
                    line_texts[f"@{lid}"] = txt

    rows = []
    with open(scenes_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for r in reader:
            if not r or not r[0].strip() or r[0].startswith("#") or r[0].lower() in ("cue", "cut_at", "cut", "time", "id"):
                continue
            rows.append(r)

    enriched_rows = []
    cut_scene_idx = 0
    prev_cam_move = None
    cam_cycle = ("push_in", "pan_left", "pull_back", "pan_right")
    CAM_MOVE_TOKENS = {"static", "push_in", "pull_back", "pan_left", "pan_right", "zoom_in_tight"}
    TRANSITION_TOKENS = {"crossfade", "cut", "flash", "fade", "cause_effect", "rapid_list"}
    for r in rows:
        # Columns: cue, img, text, pos, extra, space
        while len(r) < 6:
            r.append("")
        cue, img, text, pos, extra, space = r[0].strip(), r[1].strip(), r[2].strip(), r[3].strip(), r[4].strip(), r[5].strip()
        is_ov = cue.startswith("+")

        # Determine context text
        context_corpus = f"{text} {img}".lower()
        if img in shot_prompts:
            context_corpus += f" {shot_prompts[img]}"
        line_key = cue.lstrip("+").split(":")[0].split(".")[0]
        if line_key in line_texts:
            context_corpus += f" {line_texts[line_key]}"
        tokens = set(re.findall(r"\b[a-z0-9_]+\b", context_corpus))

        # Normalize column pollution (e.g. transitions in space or positions in extra)
        if space in ("fade", "crossfade", "cut", "flash"):
            extra = f"{extra},{space}".strip(",")
            space = "right"
        if "auto" in extra and not pos:
            extra = extra.replace("auto", "").strip(",")
            pos = "auto"

        if not is_ov:
            # SCENE CUT VFX INTELLIGENCE
            vfx_tokens = [tok.strip() for tok in extra.split(",") if tok.strip()] if extra else []
            
            # VFX Restraint: Only high-emotion hooks/twists get zoom_punch; calm narration uses smooth crossfade
            line_txt = line_texts.get(line_key, "")
            is_hook = (cut_scene_idx == 0 or cue in ("@01", "0.0", "00.0", "01.0") or any(p in line_txt for p in HOOK_KEYWORDS))
            if is_hook and "zoom_punch" not in vfx_tokens and "flash" not in vfx_tokens:
                vfx_tokens.append("zoom_punch")

            # Card / archetype scenes default cleanly to kinetic editorial transition
            is_arch = img.startswith(("card", "split", "bar_", "timeline", "stat_"))
            if is_arch:
                vfx_tokens = [t for t in vfx_tokens if t not in ("shake", "bw", "danger", "blood")]
                if not any(t in vfx_tokens for t in ("slide_wipe", "punch_settle", "whip_blur")):
                    vfx_tokens.append("slide_wipe" if "split" in img else "punch_settle")
            else:
                spoken_tokens = set(re.findall(r"\b[a-z0-9_]+\b", line_txt))
                if any(w in spoken_tokens for w in DANGER_KEYWORDS):
                    # High-tension crisis: kinetic whip blur or micro punch settle instead of ugly red overlay
                    if "whip_blur" not in vfx_tokens and "punch_settle" not in vfx_tokens:
                        vfx_tokens.append("whip_blur")
                    if any(w in spoken_tokens for w in ("earthquake", "explosion", "crushed", "battle", "collapse")):
                        if "shake" not in vfx_tokens:
                            vfx_tokens.append("shake")
                elif any(w in spoken_tokens for w in IMPACT_KEYWORDS):
                    if "punch_settle" not in vfx_tokens:
                        vfx_tokens.append("punch_settle")
                    if "shake" not in vfx_tokens:
                        vfx_tokens.append("shake")
                elif any(phrase in line_txt for phrase in TRAGEDY_HISTORICAL_KEYWORDS):
                    if "crossfade" not in vfx_tokens:
                        vfx_tokens.append("crossfade")

            # Clean editorial motion transitions (banned cheap color overlays)
            active_vfx = {"zoom_punch", "punch_settle", "whip_blur", "slide_wipe", "shake", "flash"}
            if any(tok in active_vfx for tok in vfx_tokens) and "fade" in vfx_tokens:
                vfx_tokens = [tok for tok in vfx_tokens if tok != "fade"]

            # Enforce max-2 simultaneous intensity VFX cues (excluding transitions & camera_move)
            kept_fx = []
            other_toks = []
            for tok in vfx_tokens:
                if tok in active_vfx:
                    if len(kept_fx) < 2 and tok not in kept_fx:
                        kept_fx.append(tok)
                elif tok not in CAM_MOVE_TOKENS and tok not in other_toks:
                    other_toks.append(tok)

            # Explicit non-repeating camera_move (static on cards/splits/diagrams, adjacent non-repeat on shots)
            explicit_cam = next((tok for tok in vfx_tokens if tok in CAM_MOVE_TOKENS), None)
            if is_arch or any(dk in context_corpus for dk in ("diagram", "chart", "map", "timeline", "equation")):
                cam_move = "static"
            elif explicit_cam and explicit_cam != prev_cam_move:
                cam_move = explicit_cam
            else:
                cand_moves = [m for m in cam_cycle if m != prev_cam_move]
                cam_move = cand_moves[cut_scene_idx % len(cand_moves)]
            prev_cam_move = cam_move

            vfx_tokens = other_toks + kept_fx
            if not any(tok in active_vfx or tok in TRANSITION_TOKENS for tok in vfx_tokens):
                vfx_tokens.append("crossfade")
            if cam_move not in vfx_tokens:
                vfx_tokens.append(cam_move)

            # Spatial allocation
            if not space or space == "auto":
                if "right" in context_corpus and "left" not in context_corpus:
                    space = "left"
                elif "left" in context_corpus and "right" not in context_corpus:
                    space = "right"
                else:
                    space = "right"

            extra = ",".join(vfx_tokens)
            cut_scene_idx += 1
        else:
            # OVERLAY / STICKER MOTION INTELLIGENCE
            ov_tokens = [tok.strip() for tok in extra.split(",") if tok.strip()] if extra else []
            # Filter out generic pop if we have a more specific physics directive
            if ov_tokens == ["pop"]:
                ov_tokens = []
            
            if any(w in tokens for w in HEAVY_STICKER_KEYWORDS):
                if not any(k in ov_tokens for k in ["drop", "slam", "rise"]):
                    ov_tokens.append("drop")
            elif any(w in tokens for w in LATERAL_STICKER_KEYWORDS):
                if not any(k in ov_tokens for k in ["slide_left", "slide_right", "pop"]):
                    ov_tokens.append("slide_left")
            elif any(w in tokens for w in HOVER_STICKER_KEYWORDS):
                if not any(k in ov_tokens for k in ["hover", "pop"]):
                    ov_tokens.append("hover")
            
            if not ov_tokens:
                ov_tokens.append("pop")

            extra = ",".join(ov_tokens)

        enriched_rows.append([cue, img, text, pos, extra, space])

    # Write back enriched SCENES_HYBRID.tsv
    target_out = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    with open(target_out, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f, delimiter="\t")
        writer.writerow(["cue", "img", "text", "pos", "extra", "space"])
        for r in enriched_rows:
            writer.writerow(r)

    print(f"✅ Enriched {len(enriched_rows)} scenes with intelligent VFX in {target_out}")
    return True

if __name__ == "__main__":
    p_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    analyze_and_enrich_scenes(p_dir)
