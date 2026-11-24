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
    "danger", "peril", "starvation", "predator", "sabertooth", "feline",
    "deadly", "attack", "blood", "kill", "monster", "collapse", "crisis",
    "fear", "panic", "fatal", "poison", "terror", "nightmare", "stalk",
    "ambush", "war", "battle", "enemy", "threat", "vulnerable", "siege",
    "rebellion", "strike", "hostile", "combat", "ruin", "assault"
}

COLD_KEYWORDS = {
    "ice", "cold", "freezing", "frost", "snow", "winter", "subzero",
    "glacier", "chill", "frozen", "arctic"
}

TRAGEDY_HISTORICAL_KEYWORDS = {
    "died", "extinct", "tragedy", "disaster", "ancestor", "fossil",
    "millennia", "ancient times", "dark age", "century", "buried"
}

HOOK_KEYWORDS = {
    "secret", "mystery", "conquer", "revolution", "unbelievable", "shock",
    "mastery", "invention", "hidden", "discovery", "empire", "truth"
}

IMPACT_KEYWORDS = {
    "excavate", "build", "construction", "hammer", "crack", "smash",
    "quarry", "stone", "impact", "blast", "pave", "layer"
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
            
            # Opening hook punch (Scene 1 & 2) or Revelation Shocks
            is_hook = (cut_scene_idx in (0, 1) or cue in ("@01", "@02", "0.0", "00.0", "01.0") or any(w in tokens for w in HOOK_KEYWORDS))
            if is_hook and "zoom_punch" not in vfx_tokens and "flash" not in vfx_tokens:
                vfx_tokens.append("zoom_punch")

            # Title card shocks
            if img == "card":
                if "cut" not in vfx_tokens and "flash" not in vfx_tokens and "zoom_punch" not in vfx_tokens:
                    vfx_tokens.append("zoom_punch")
            else:
                # Peril / Predator danger / Combat ambush
                if any(w in tokens for w in DANGER_KEYWORDS):
                    if "danger" not in vfx_tokens and "blood" not in vfx_tokens:
                        vfx_tokens.append("danger")
                    if "shake" not in vfx_tokens:
                        vfx_tokens.append("shake")
                # Heavy construction impact / physical rumble
                elif any(w in tokens for w in IMPACT_KEYWORDS):
                    if "shake" not in vfx_tokens:
                        vfx_tokens.append("shake")
                # Freezing cold
                elif any(w in tokens for w in COLD_KEYWORDS):
                    if "ice" not in vfx_tokens:
                        vfx_tokens.append("ice")
                # Historical tragedy / flashbacks
                elif any(w in tokens for w in TRAGEDY_HISTORICAL_KEYWORDS):
                    if "bw" not in vfx_tokens:
                        vfx_tokens.append("bw")

            # If dynamic active VFX is present, remove passive "fade"
            active_vfx = {"zoom_punch", "danger", "shake", "ice", "bw", "flash", "blood"}
            if any(tok in active_vfx for tok in vfx_tokens) and "fade" in vfx_tokens:
                vfx_tokens = [tok for tok in vfx_tokens if tok != "fade"]

            # Default smooth motion if empty
            if not vfx_tokens:
                vfx_tokens.append("fade")

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
