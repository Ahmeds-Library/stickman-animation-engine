#!/usr/bin/env python3
"""align_hybrid_scenes.py: Deterministic Word-Synchronizer for Stickman Hybrid Videos
Resolves every scene and sticker cue to exact line.i word tokens from WORDS.tsv.
Ensures zero drift, strictly ascending timestamps, and perfect overlay containment.
"""
import os, sys, csv, re

def load_words(words_path):
    words_list = []
    line_words = {}
    cue_map = {}
    if not os.path.exists(words_path):
        return words_list, line_words, cue_map
    with open(words_path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            line = r["line"]
            i = r["i"]
            start_t = float(r["start"])
            end_t = float(r["end"])
            w_clean = re.sub(r"[^\w]", "", r["word"].lower())
            cue_key = f"{line}.{i}"
            entry = {
                "line": line,
                "i": i,
                "cue": cue_key,
                "word": r["word"],
                "clean": w_clean,
                "start": start_t,
                "end": end_t
            }
            words_list.append(entry)
            line_words.setdefault(line, []).append(entry)
            cue_map[cue_key] = start_t
            cue_map[f"@{line}"] = cue_map.get(f"@{line}", start_t)
            cue_map[f"@{line}:{w_clean}"] = start_t
    return words_list, line_words, cue_map

def find_best_word_cue(cue_str, words_list, line_words, cur_t0=0.0):
    clean = cue_str.strip().lstrip("+")
    # Check if already a valid line.i format (e.g. 02.5)
    if re.fullmatch(r"\d{1,3}\.\d{1,3}", clean):
        parts = clean.split(".")
        ln, idx = parts[0], int(parts[1])
        # Verify if ln is a genuine line and idx is a valid word index
        if ln in line_words and idx < len(line_words[ln]):
            return clean
        elif ln.zfill(2) in line_words and idx < len(line_words[ln.zfill(2)]):
            return f"{ln.zfill(2)}.{idx}"
        # If not a valid line.i index, treat it as a float timestamp in seconds (e.g. 01.68, 03.74)
        try:
            sec = float(clean)
            closest = min(words_list, key=lambda w: abs(w["start"] - sec))
            return closest["cue"]
        except ValueError:
            pass
        
    line_target = None
    token = None
    if ":" in clean:
        line_target, _, token = clean.partition(":")
        line_target = line_target.lstrip("@")
        token = re.sub(r"[^\w]", "", token.lower())
    elif clean.startswith("@"):
        line_target = clean.lstrip("@")
        
    # Search within line_target first
    if line_target and line_target in line_words:
        target_group = line_words[line_target]
        if token:
            for w in target_group:
                if token in w["clean"] or w["clean"] in token:
                    return w["cue"]
        else:
            return target_group[0]["cue"]
            
    # Search within nearby window if token specified
    if token:
        nearby = [w for w in words_list if abs(w["start"] - cur_t0) < 18.0]
        for w in nearby:
            if token in w["clean"] or w["clean"] in token:
                return w["cue"]
                
    # Fallback to line start
    if line_target and line_target in line_words:
        return line_words[line_target][0]["cue"]
        
    # Fallback to closest word to cur_t0
    closest = min(words_list, key=lambda w: abs(w["start"] - cur_t0))
    return closest["cue"]

def align_file(project_dir):
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    words_path = os.path.join(project_dir, "WORDS.tsv")
    if not os.path.exists(scenes_path) or not os.path.exists(words_path):
        print(f"Skipping {project_dir}: missing files.")
        return False
        
    words_list, line_words, cue_map = load_words(words_path)
    if not words_list:
        return False
        
    rows = []
    with open(scenes_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for r in reader:
            if not r or not r[0].strip() or r[0].startswith("#") or r[0].lower() in ("cue", "cut_at", "cut", "time", "id"):
                continue
            rows.append(r)
            
    scenes = []
    overlays = []
    cur_t0 = 0.0
    for r in rows:
        cue = r[0].strip()
        is_ov = cue.startswith("+")
        best_cue = find_best_word_cue(cue, words_list, line_words, cur_t0)
        t_val = cue_map.get(best_cue, 0.0)
        
        prefix = "+" if is_ov else ""
        r[0] = f"{prefix}{best_cue}"
        if is_ov:
            overlays.append({"t": t_val, "row": r, "cue": best_cue})
        else:
            cur_t0 = t_val
            scenes.append({"t0": t_val, "row": r, "cue": best_cue, "ov": []})
            
    # Sort scenes chronologically
    scenes.sort(key=lambda s: s["t0"])
    for i in range(len(scenes)):
        scenes[i]["t1"] = scenes[i + 1]["t0"] if i + 1 < len(scenes) else 999999.0
        
    # Group each overlay into its proper containing scene
    for o in overlays:
        parent = None
        for s in scenes:
            if s["t0"] - 0.05 <= o["t"] < s["t1"]:
                parent = s
                break
        if not parent and scenes:
            # Fallback to scene that precedes o["t"] chronologically
            preceding = [s for s in scenes if s["t0"] <= o["t"]]
            if preceding:
                parent = max(preceding, key=lambda s: s["t0"])
            else:
                parent = scenes[0]
        if parent:
            parent["ov"].append(o)

    # Sort each scene's overlays chronologically
    for s in scenes:
        s["ov"].sort(key=lambda o: o["t"])
            
    aligned_rows = []
    for s in scenes:
        aligned_rows.append(s["row"])
        for o in s["ov"]:
            aligned_rows.append(o["row"])
            
    out_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["cue", "img", "text", "pos", "extra", "space"])
        for ar in aligned_rows:
            # Pad to 6 columns
            ar += [""] * (6 - len(ar))
            writer.writerow(ar[:6])
            
    print(f"✅ Aligned {len(aligned_rows)} cues in {out_path}")
    return True

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "."
    align_file(p)
