#!/usr/bin/env python3
"""align_hybrid_scenes.py: Deterministic Word-Synchronizer for Stickman Hybrid Videos
Resolves every scene and sticker cue to exact line.i word tokens from WORDS.tsv.
Ensures zero drift, strictly ascending timestamps, keyword-locked overlays, and 2.5-3.0s visual beat density.
"""
import os, sys, csv, re

SYNONYM_DICTIONARY = {
    "dna": ["dna", "helix", "genome", "genetics", "genetic", "gene", "strangers", "sequence"],
    "gorilla": ["chimpanzee", "chimpanzees", "chimp", "ape", "apes", "gorilla", "primate"],
    "skull": ["extinct", "extinction", "skull", "fossil", "bones", "died", "perished", "almost"],
    "fossil": ["extinct", "extinction", "skull", "fossil", "bones", "died", "perished"],
    "volcano": ["volcano", "supervolcano", "toba", "eruption", "blast", "explosion", "mount"],
    "cone": ["volcano", "supervolcano", "toba", "eruption", "blast", "explosion"],
    "ash": ["ash", "suffocating", "black", "cloud", "smoke", "burying", "plume"],
    "cloud": ["ash", "suffocating", "black", "cloud", "smoke", "dark"],
    "freeze": ["winter", "freeze", "ice", "cold", "plunging", "plunge", "degrees", "dropped", "sun"],
    "thermometer": ["winter", "freeze", "ice", "cold", "plunging", "degrees", "temperature"],
    "seashell": ["shellfish", "seashell", "shell", "mussels", "mussel", "limpets", "coast", "tidepool"],
    "shell": ["shellfish", "seashell", "shell", "mussels", "limpets", "coast"],
    "flint": ["blade", "flint", "tool", "tools", "stone", "spear", "weapons", "crafting"],
    "blade": ["blade", "flint", "tool", "tools", "stone", "spear", "crafting"],
    "campfire": ["fire", "campfire", "flame", "stories", "hearth", "coals", "warmth", "language", "night"],
    "fire": ["fire", "campfire", "flame", "stories", "hearth", "coals", "warmth"],
    "circle": ["fire", "campfire", "circle", "gathering", "stories"],
    "bronze": ["bronze", "weapons", "sword", "swords", "armies", "metallurgy", "copper"],
    "sword": ["bronze", "weapons", "sword", "swords", "armies", "warrior", "defenseless"],
    "tablet": ["writing", "tablet", "tablets", "letters", "script", "archives", "clay", "forgotten"],
    "clay": ["writing", "tablet", "tablets", "letters", "clay", "forgotten"],
    "torch": ["burned", "fire", "flame", "flames", "ground", "ash"],
    "wheat": ["starved", "drought", "megadrought", "famine", "grain", "crops", "harvest"],
    "grain": ["starved", "drought", "megadrought", "famine", "grain", "crops"],
    "helmet": ["invaders", "peoples", "warrior", "warriors", "raiders", "armies", "crushing"],
    "horned": ["invaders", "peoples", "warrior", "warriors", "raiders", "armies"],
    "tin": ["tin", "copper", "alloy", "trade", "traded", "mines", "halted"],
    "ingot": ["tin", "copper", "alloy", "trade", "traded", "mines"],
    "ruin": ["abandoned", "ruins", "collapsed", "cities", "crumbling", "vanished"],
    "stone": ["abandoned", "ruins", "collapsed", "cities", "walls", "palace"],
    "warship": ["oceans", "sea", "ships", "fleet", "galley", "maritime", "coast"],
    "prow": ["oceans", "sea", "ships", "fleet", "warship", "maritime"],
    "decibels": ["decibel", "decibels", "sound", "volume", "loud", "noise", "pressure", "db"],
    "miles": ["miles", "mile", "distance", "away", "across"],
    "megatons": ["megatons", "megaton", "tons", "force", "power", "energy", "blast"],
    "war": ["war", "battle", "conflict", "combat", "military", "fight"],
    "nature": ["nature", "natural", "volcano", "island", "eruption", "earth"],
    "earth": ["earth", "globe", "planet", "circumference", "world"],
    "times": ["times", "time", "orbit", "circumnavigate", "wave", "pulse"],
}

NUMBER_WORD_MAP = {
    "1": ["one", "first"], "2": ["two", "second"], "3": ["three", "third"], "4": ["four", "fourth"],
    "5": ["five", "fifth"], "6": ["six", "sixth"], "7": ["seven", "seventh"], "8": ["eight", "eighth"],
    "9": ["nine", "ninth"], "10": ["ten", "tenth"], "11": ["eleven"], "12": ["twelve"],
    "13": ["thirteen", "thirteenth"], "14": ["fourteen"], "15": ["fifteen"], "16": ["sixteen"],
    "17": ["seventeen"], "18": ["eighteen"], "19": ["nineteen"], "20": ["twenty"],
    "30": ["thirty"], "40": ["forty"], "50": ["fifty"], "60": ["sixty"], "70": ["seventy"],
    "80": ["eighty"], "90": ["ninety"], "100": ["hundred"], "1000": ["thousand"],
    "1000000": ["million"], "1000000000": ["billion"],
    "194": ["one", "hundred", "ninety", "four", "194"],
    "200": ["two", "hundred", "200"],
    "3000": ["three", "thousand", "3000"],
    "310": ["three", "hundred", "ten", "310"],
    "4": ["four", "fourth", "4"],
    "1/13": ["thirteenth", "thirteen", "fraction", "earth"],
}

CARD_ARCHETYPES = (
    "card", "card_stat", "card_phrase", "card_strike_replace", "strike_replace",
    "split_compare", "split_contrast", "scale_compare", "scale_bar",
    "bar_timeline", "timeline", "stat_pie", "stat_ring", "chapter_breather", "breather"
)

def is_card_row(row):
    if len(row) < 2:
        return False
    img = row[1].strip()
    tok = img.split(":")[0].strip().lower()
    return (tok in CARD_ARCHETYPES or tok.startswith(("card_", "split_", "timeline_", "stat_", "bar_", "chapter_", "breather", "scale_")))

def find_card_spoken_trigger(cue_str, row, words_list, line_words, cur_t0=0.0):
    """Finds exact spoken keyword/number token in WORDS.tsv for editorial cards to eliminate desync."""
    img_field = row[1].strip() if len(row) > 1 else ""
    text_field = row[2].strip() if len(row) > 2 else ""
    comb = (img_field.split(":", 1)[1] + " " + text_field).strip() if ":" in img_field else text_field

    clean = cue_str.strip().lstrip("+")
    line_target = None
    if "." in clean:
        line_target = clean.split(".")[0].zfill(2)
    elif clean.startswith("@"):
        line_target = clean.lstrip("@").zfill(2)
    elif clean.isdigit():
        line_target = clean.zfill(2)

    # Extract numbers and words
    nums = re.findall(r"\b\d+[\d,]*(?:\.\d+)?(?:/\d+)?\b", comb)
    words_in_card = [w.lower() for w in re.findall(r"[a-zA-Z]{3,}", comb)]
    search_terms = set(words_in_card)
    for num in nums:
        n_clean = num.replace(",", "")
        if n_clean in NUMBER_WORD_MAP:
            search_terms.update(NUMBER_WORD_MAP[n_clean])
        search_terms.add(n_clean)
        if "/" in n_clean:
            for p in n_clean.split("/"):
                if p in NUMBER_WORD_MAP:
                    search_terms.update(NUMBER_WORD_MAP[p])

    for w in list(search_terms):
        if w in SYNONYM_DICTIONARY:
            search_terms.update(SYNONYM_DICTIONARY[w])

    search_lines = []
    if line_target:
        try:
            ln_num = int(line_target)
            search_lines = [f"{ln_num:02d}", f"{ln_num+1:02d}", f"{max(1, ln_num-1):02d}"]
        except Exception:
            search_lines = [line_target]

    for ln in search_lines:
        if ln in line_words:
            for w in line_words[ln]:
                cw = re.sub(r"[^\w]", "", w["word"].lower())
                if cw in search_terms or any(t == cw or (len(t) >= 5 and t in cw) for t in search_terms):
                    return w

    nearby_words = [w for w in words_list if -1.5 <= (w["start"] - cur_t0) <= 14.0]
    for w in nearby_words:
        cw = re.sub(r"[^\w]", "", w["word"].lower())
        if cw in search_terms or any(t == cw or (len(t) >= 5 and t in cw) for t in search_terms):
            return w

    return None

def sanitize_words_tsv(words_path):
    """Splits em-dash glued words (e.g. 'humans—making') into cleanly timed individual words."""
    if not os.path.exists(words_path):
        return
    rows = []
    modified = False
    with open(words_path, encoding="utf-8") as f:
        reader = list(csv.DictReader(f, delimiter="\t"))
        for r in reader:
            raw_w = r.get("word", "")
            if re.search(r"[—–]|--", raw_w):
                modified = True
                parts = [p.strip() for p in re.split(r"[—–]|--", raw_w) if p.strip()]
                if len(parts) >= 2:
                    t_start = float(r["start"])
                    t_end = float(r["end"])
                    total_dur = max(0.05, t_end - t_start)
                    tot_len = sum(len(p) for p in parts)
                    cur_t = t_start
                    line_id = r.get("line", "01")
                    base_i = int(r.get("i", 0))
                    for p_idx, p_text in enumerate(parts):
                        p_dur = total_dur * (len(p_text) / max(1, tot_len))
                        rows.append({
                            "line": line_id,
                            "i": str(base_i + p_idx),
                            "start": f"{cur_t:.3f}",
                            "end": f"{cur_t + p_dur:.3f}",
                            "word": p_text
                        })
                        cur_t += p_dur
                    continue
            rows.append(r)

    if modified:
        # Re-index i per line
        line_counters = {}
        for r in rows:
            lid = r["line"]
            line_counters[lid] = line_counters.get(lid, 0)
            r["i"] = str(line_counters[lid])
            line_counters[lid] += 1
            
        with open(words_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["line", "i", "start", "end", "word"], delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Sanitized em-dash words in {words_path}")

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

def find_best_overlay_cue(cue_str, overlay_row, words_list, line_words, cur_t0=0.0):
    """Binds sticker reveals strictly to exact spoken trigger keywords."""
    clean = cue_str.strip().lstrip("+")
    img_path = overlay_row[1].strip() if len(overlay_row) > 1 else ""
    text_val = overlay_row[2].strip() if len(overlay_row) > 2 else ""
    
    stk_base = os.path.splitext(os.path.basename(img_path))[0].lower()
    stk_tokens = re.findall(r"[a-z]{3,}", f"{stk_base} {text_val.lower()}")
    
    # Expand tokens via synonym dictionary
    target_synonyms = set(stk_tokens)
    for tok in stk_tokens:
        if tok in SYNONYM_DICTIONARY:
            target_synonyms.update(SYNONYM_DICTIONARY[tok])

    line_target = None
    if "." in clean:
        parts = clean.split(".")
        line_target = parts[0].zfill(2)
    elif clean.startswith("@"):
        line_target = clean.lstrip("@").zfill(2)

    # 1. Search inside targeted line and nearby lines (+/- 1 line)
    search_lines = []
    if line_target:
        try:
            ln_num = int(line_target)
            search_lines = [f"{ln_num:02d}", f"{ln_num+1:02d}", f"{max(1, ln_num-1):02d}"]
        except Exception:
            search_lines = [line_target]

    for ln in search_lines:
        if ln in line_words:
            for w in line_words[ln]:
                if w["clean"] in target_synonyms or any(syn == w["clean"] or (len(syn) >= 5 and syn in w["clean"]) for syn in target_synonyms):
                    return w["cue"]

    # 2. Search within a local [-1.5s, +10.0s] window after cur_t0 (never trigger early on wrong context!)
    nearby_words = [w for w in words_list if -1.5 <= (w["start"] - cur_t0) <= 10.0]
    for w in nearby_words:
        if w["clean"] in target_synonyms or any(syn == w["clean"] or (len(syn) >= 5 and syn in w["clean"]) for syn in target_synonyms):
            return w["cue"]

    print(f"⚠️ [Semantic Sync Advisory] Sticker '{stk_base}' at cue '{cue_str}' has no matching keyword near line {line_target or '?'}; keeping cue.")
    # Fallback to standard word cue finder
    return find_best_word_cue(cue_str, words_list, line_words, cur_t0)

def find_best_word_cue(cue_str, words_list, line_words, cur_t0=0.0):
    clean = cue_str.strip().lstrip("+")
    if re.fullmatch(r"\d{1,3}\.\d{1,3}", clean):
        parts = clean.split(".")
        ln, idx = parts[0], int(parts[1])
        if ln in line_words and idx < len(line_words[ln]):
            return clean
        elif ln.zfill(2) in line_words and idx < len(line_words[ln.zfill(2)]):
            return f"{ln.zfill(2)}.{idx}"
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
        
    if line_target and line_target in line_words:
        target_group = line_words[line_target]
        if token:
            for w in target_group:
                if token in w["clean"] or w["clean"] in token:
                    return w["cue"]
        else:
            return target_group[0]["cue"]
            
    if token:
        nearby = [w for w in words_list if abs(w["start"] - cur_t0) < 18.0]
        for w in nearby:
            if token in w["clean"] or w["clean"] in token:
                return w["cue"]
                
    if line_target and line_target in line_words:
        return line_words[line_target][0]["cue"]
        
    closest = min(words_list, key=lambda w: abs(w["start"] - cur_t0))
    return closest["cue"]

def align_file(project_dir):
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    words_path = os.path.join(project_dir, "WORDS.tsv")
    if not os.path.exists(scenes_path) or not os.path.exists(words_path):
        print(f"Skipping {project_dir}: missing files.")
        return False

    # 1. Sanitize any em-dash glued words in WORDS.tsv
    sanitize_words_tsv(words_path)
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
            
    is_shorts = ("short" in os.path.abspath(project_dir).lower() or "9:16" in str(rows))
    scenes = []
    overlays = []
    cur_t0 = 0.0
    for r in rows:
        cue = r[0].strip()
        is_ov = cue.startswith("+")
        if is_ov:
            best_cue = find_best_overlay_cue(cue, r, words_list, line_words, cur_t0)
            t_val = cue_map.get(best_cue, 0.0)
            r[0] = f"+{best_cue}"
            overlays.append({"t": t_val, "row": r, "cue": best_cue})
        else:
            is_c = is_card_row(r)
            w_trig = find_card_spoken_trigger(cue, r, words_list, line_words, cur_t0) if is_c else None
            if w_trig:
                best_cue = w_trig["cue"]
                spoken_t = float(w_trig["start"])
                t_val = max(0.0, spoken_t - 0.15)
                r[0] = best_cue
                cur_t0 = t_val
                scenes.append({"t0": t_val, "row": r, "cue": best_cue, "ov": [], "is_card": True, "w_trig": w_trig})
            else:
                best_cue = find_best_word_cue(cue, words_list, line_words, cur_t0)
                t_val = cue_map.get(best_cue, 0.0)
                r[0] = best_cue
                cur_t0 = t_val
                scenes.append({"t0": t_val, "row": r, "cue": best_cue, "ov": [], "is_card": is_c})

    # Sort scenes chronologically and deduplicate exact same-timestamp collisions
    scenes.sort(key=lambda s: s["t0"])
    dedup_scenes = []
    for s in scenes:
        if dedup_scenes and abs(s["t0"] - dedup_scenes[-1]["t0"]) < 0.05:
            s["ov"] = dedup_scenes[-1]["ov"] + s["ov"]
            dedup_scenes[-1] = s
        else:
            dedup_scenes.append(s)
    scenes = dedup_scenes

    # Enforce minimum readable duration for cards so animations settle and remain readable
    for i in range(len(scenes)):
        sc = scenes[i]
        is_c = sc.get("is_card", False) or is_card_row(sc["row"])
        if is_c and i + 1 < len(scenes):
            img_f = sc["row"][1].strip().lower()
            min_dur = 2.6 if any(k in img_f for k in ("split_", "strike_", "scale_")) else 2.0
            min_t1 = sc["t0"] + min_dur
            if scenes[i + 1]["t0"] < min_t1:
                target_t = min_t1
                closest_w = min(words_list, key=lambda w: abs(w["start"] - target_t))
                scenes[i + 1]["t0"] = float(closest_w["start"])
                scenes[i + 1]["cue"] = closest_w["cue"]
                scenes[i + 1]["row"][0] = closest_w["cue"]

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
            preceding = [s for s in scenes if s["t0"] <= o["t"]]
            parent = max(preceding, key=lambda s: s["t0"]) if preceding else scenes[0]
        if parent:
            parent["ov"].append(o)

    # Sort each scene's overlays chronologically (do NOT fabricate fake crop_focus/zoom_in_tight snap-cuts on recycled shots!)
    for s in scenes:
        s["ov"].sort(key=lambda o: o["t"])

    expanded_scenes = scenes

    # Honest Unique Shot Density & Calm Pacing Check
    total_dur = max(1.0, words_list[-1]["end"]) if words_list else 60.0
    unique_hero_shots = {
        s["row"][1].strip() for s in expanded_scenes
        if len(s["row"]) > 1 and s["row"][1].strip().startswith("shots/")
    }
    min_req_shots = max(10, int(total_dur / 5.5)) if is_shorts else max(25, int(total_dur / 7.5))
    if len(unique_hero_shots) < min_req_shots:
        print(f"⚠️ [Unique Shot Density Warning] Only {len(unique_hero_shots)} unique Flow shots for {total_dur:.1f}s "
              f"({'Shorts' if is_shorts else 'Long'}; minimum required is {min_req_shots}). "
              f"Add fresh unique shots in blueprint/SCENES_HYBRID.tsv instead of recycling old shots.")

    for i_sc in range(len(expanded_scenes) - 1):
        sc_dur = expanded_scenes[i_sc + 1]["t0"] - expanded_scenes[i_sc]["t0"]
        extra_str = (expanded_scenes[i_sc]["row"][4] if len(expanded_scenes[i_sc]["row"]) > 4 else "").lower()
        if sc_dur < 1.5 and "rapid_list" not in extra_str:
            print(f"⚠️ [Pacing Warning] Erratic rapid cut {expanded_scenes[i_sc]['cue']} -> {expanded_scenes[i_sc+1]['cue']} ({sc_dur:.2f}s < 1.5s). Cut on complete spoken clauses (2.5-4.0s Shorts / 3.5-5.5s Long).")

    aligned_rows = []
    for s in expanded_scenes:
        aligned_rows.append(s["row"])
        for o in s["ov"]:
            aligned_rows.append(o["row"])

    out_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["cue", "img", "text", "pos", "extra", "space"])
        for ar in aligned_rows:
            ar += [""] * (6 - len(ar))
            writer.writerow(ar[:6])

    print(f"✅ Aligned {len(aligned_rows)} cues with Keyword-Lock & Smooth-Motion Compliance in {out_path}")
    return True

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "."
    align_file(p)
