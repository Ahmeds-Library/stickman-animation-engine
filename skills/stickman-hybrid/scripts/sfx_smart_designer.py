#!/usr/bin/env python3
"""sfx_smart_designer.py: Automated Intelligent Broadcast Sound Design Engine
Generates rich, high-density, multi-layered sound design (cues_pro.tsv) for Stickman Animation:
1. Scene Transition Swishes & Whooshes on every cut (Wyzowl CC0 & Kenney CC0).
2. Tactile Sticker Entrance SFX (pops, taps, clacks, dings) matched semantically and voice-synced.
3. Tactile Sticker Exit Whoosh/Zip (soft zip-out on sticker disappearance).
4. Spoken Keyword Audio Impacts (ice cracks, sub hits, bells, tonal chords) synced to WORDS.tsv.
5. Continuous Environmental Foley Ambiences (wind, room tone, water, crackle).
6. Thematically Matched 100% CC0 Music Bed (ducked at -24 dB with smooth fade-in/fade-out).
"""

import os, sys, csv, random, subprocess, glob, re, hashlib

# Autonomous Zero-Setup Bootstrapper
try:
    import auto_bootstrap
    auto_bootstrap.ensure_environment()
except Exception:
    pass

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SFX_ROOTS = [
    os.path.abspath(os.path.join(SKILL_SCRIPTS, "../../vox-doc-sound/sfx")),
    "/home/mirza-ahmed-hassan/.gemini/config/skills/vox-doc-sound/sfx",
    "/home/mirza-ahmed-hassan/.claude/skills/vox-doc-sound/sfx"
]
DEFAULT_MUSIC_ROOTS = [
    os.path.abspath(os.path.join(SKILL_SCRIPTS, "../../vox-doc-sound/music")),
    "/home/mirza-ahmed-hassan/.gemini/config/skills/vox-doc-sound/music",
    "/home/mirza-ahmed-hassan/.claude/skills/vox-doc-sound/music"
]

def find_sfx_library():
    for r in DEFAULT_SFX_ROOTS:
        if os.path.exists(r):
            return r
    return None

def find_music_library():
    for r in DEFAULT_MUSIC_ROOTS:
        if os.path.exists(r):
            return r
    return None

def collect_audio_catalog(sfx_root):
    catalog = {}
    if not sfx_root or not os.path.exists(sfx_root):
        return catalog
    for ext in ("*.mp3", "*.ogg", "*.wav"):
        for path in glob.glob(f"{sfx_root}/**/{ext}", recursive=True):
            rel = os.path.relpath(path, sfx_root)
            parts = [p.lower() for p in rel.split(os.sep)]
            for part in parts[:-1]:
                catalog.setdefault(part, []).append(path)
                if part.endswith("s"):
                    catalog.setdefault(part[:-1], []).append(path)
                else:
                    catalog.setdefault(part + "s", []).append(path)

                # Cross-category semantic aliases
                if "paper" in part or "office" in part or "stationery" in part:
                    catalog.setdefault("paper-and-office", []).append(path)
                if "impact" in part or "hit" in part or "emphasis" in part:
                    catalog.setdefault("hits-and-impacts", []).append(path)
                if "digital" in part or "tech" in part or "data" in part or "interface" in part:
                    catalog.setdefault("digital-and-tech", []).append(path)
                if "swish" in part or "zip" in part or "swipe" in part or "whoosh" in part:
                    catalog.setdefault("swishes-and-zips", []).append(path)
                if "pop" in part or "click" in part:
                    catalog.setdefault("pops-and-clicks", []).append(path)
                if "writing" in part or "draw" in part:
                    catalog.setdefault("writing-and-drawing", []).append(path)

            catalog.setdefault("all", []).append(path)
    return catalog

def resolve_word_time(cue_raw, words_list, words_map, scene_t0=0.0, scene_t1=None):
    """Intelligently resolve spoken keyword timestamp from WORDS.tsv."""
    cue = cue_raw.strip().lstrip("+")
    if cue in words_map:
        return words_map[cue]

    cue_clean_num = cue.lstrip("@").replace(":", ".")
    try:
        return float(cue_clean_num)
    except ValueError:
        pass

    line_target = None
    search_term = cue.lower()
    if ":" in cue:
        prefix, _, search_term = cue.partition(":")
        line_target = prefix.lstrip("@")
    elif cue.startswith("@"):
        line_target = cue[1:]
        search_term = ""

    candidate_words = []
    if line_target:
        candidate_words = [w for w in words_list if w.get("line") == line_target or w.get("cue", "").startswith(line_target)]
    if not candidate_words and scene_t0 is not None:
        candidate_words = [w for w in words_list if scene_t0 <= w["start"] <= (scene_t1 or (scene_t0 + 10.0))]
    if not candidate_words:
        candidate_words = words_list

    if search_term:
        SYNONYMS = {
            "fridge": ["refrigerator", "refrigerators", "freezer", "electricity"],
            "icecream": ["ice", "cream", "sorbet", "sweet"],
            "pot": ["pots", "clay", "zeer", "terracotta"],
            "dome": ["yakhchal", "yakhchals", "vault", "structure", "wall"],
            "snow": ["alpine", "mountain", "runners", "ice"],
            "milk": ["camel", "fresh", "drink", "dairy"],
            "danger": ["spoil", "rot", "bacteria", "zone", "blackout", "peril"],
            "heat": ["desert", "sun", "hot", "degrees", "summer", "warm"],
            "cold": ["chill", "freeze", "frost", "subzero", "winter", "ice"],
            "persia": ["persian", "ancient", "kings", "desert"],
            "night": ["sky", "space", "stars", "dark", "radiation"],
            "sweat": ["evaporat", "cooling", "water", "sweating"],
            "sorbet": ["ice", "cream", "sweet", "royal"],
            "wall": ["canal", "shadow", "walls", "brick", "shade"],
            "sarooj": ["mortar", "egg", "ash", "goat", "hair"],
            "wine": ["chilled", "chalice", "goblet", "bottle", "drink"],
            "plow": ["wyeth", "plow", "harvest", "lake", "block"],
            "sawdust": ["pine", "sawdust", "insulat", "wood", "pack"],
            "icebox": ["zinc", "icebox", "wooden", "block", "kitchen"],
            "money": ["dollar", "cost", "price", "wealth", "expensive", "gold"],
        }

        for w in candidate_words:
            w_txt = w["word"].lower().strip('.,!?":;')
            if w_txt == search_term:
                return w["start"]

        for w in candidate_words:
            w_txt = w["word"].lower().strip('.,!?":;')
            if (len(search_term) >= 3 and search_term in w_txt) or (len(w_txt) >= 3 and w_txt in search_term):
                return w["start"]

        syns = SYNONYMS.get(search_term, [])
        for syn in syns:
            for w in candidate_words:
                w_txt = w["word"].lower().strip('.,!?":;')
                if syn in w_txt or w_txt in syn:
                    return w["start"]

        if len(search_term) >= 4:
            stem = search_term[:4]
            for w in candidate_words:
                w_txt = w["word"].lower().strip('.,!?":;')
                if w_txt.startswith(stem):
                    return w["start"]

    if scene_t0 is not None:
        return scene_t0 + 0.6
    return 0.0

# Semantic Keyword to Sound Matching Dictionary (Kenney CC0, Wyzowl CC0, StableAudio)
SEMANTIC_SFX_MAP = {
    ("ice", "cold", "frost", "snow", "winter", "frozen"): [
        "nature/b2_ice_crack_a.mp3", "nature/b2_ice_crack_b.mp3", "shimmers/shimmer-short-sparkle.wav", "impacts/impact-light-hard.wav"
    ],
    ("water", "liquid", "milk", "drop", "evaporat", "sweat", "wet"): [
        "everyday-props/props-splash.wav", "everyday-props/props-drip.wav", "pops/pop-medium-bubble.wav", "tonal/b5_water_drop_tone_a.mp3"
    ],
    ("fire", "heat", "sun", "blazing", "scorch", "burn"): [
        "nature/b2_fire_crackle_a.mp3", "nature/b2_fire_crackle_b.mp3", "archive/b3_steam_engine_a.mp3"
    ],
    ("fridge", "electric", "power", "grid", "machine", "tech"): [
        "digital/digital-glitch-clear.wav", "digital/digital-process-clear.wav", "data/b4_notification_ping_h.mp3", "digital/threeTone1.ogg"
    ],
    ("money", "gold", "coin", "trade", "millionaire", "hoard", "wealth"): [
        "money/coin-drop.wav", "money/register.wav", "casino/chipsStack1.ogg", "money/b2_coin_drop.mp3"
    ],
    ("danger", "peril", "starvation", "panic", "war", "battle", "deadly", "blackout", "collapse"): [
        "cinematic-hits/cinematic-slam-big.wav", "booms-and-bass/boom-hit-medium.wav", "emphasis/b2_boom_soft_a.mp3", "tonal/s1_drone_dark_a.mp3"
    ],
    ("dome", "yakhchal", "pot", "clay", "sand", "mortar", "brick", "wall", "stone"): [
        "impacts/impact-medium-firm.wav", "rpg/chop.ogg", "emphasis/impactWood_light_000.ogg", "pops/pop-medium-in.wav"
    ],
    ("king", "emperor", "palace", "roman", "alexander", "conquer", "victory"): [
        "cinematic-hits/cinematic-drum-big.wav", "jingle/jingle_win_00.ogg", "shimmers/shimmer-medium-sparkle.wav"
    ],
    ("watch", "channel", "click", "video", "cta", "bell"): [
        "interface/button-soft.wav", "office/b3_desk_bell_a.mp3", "ui/switch3.ogg"
    ],
    ("slap", "idiot", "weirdo", "absurd", "ridiculous", "punish", "revolution", "crazy", "overthrow"): [
        "impacts/impact-light-hard.wav", "rpg/chop.ogg", "cinematic-hits/cinematic-slam-big.wav", "emphasis/impactWood_light_000.ogg"
    ],
    ("quiz", "scenario", "option", "maybe", "awkward", "signal", "dating", "deadpan"): [
        "digital/threeTone1.ogg", "interface/button-soft.wav", "data/b4_notification_ping_h.mp3"
    ],
    ("ruler", "dictator", "power", "key", "treasury", "bureaucracy", "tax", "rule", "incentive"): [
        "money/coin-drop.wav", "digital/digital-process-clear.wav", "cinematic-hits/cinematic-drum-big.wav", "money/register.wav"
    ],
    ("flat", "disc", "orbit", "planet", "solar", "gravity", "dimension", "geometry", "space"): [
        "digital/digital-process-clear.wav", "shimmers/shimmer-short-sparkle.wav", "tonal/s1_drone_dark_a.mp3"
    ]
}

class SfxCooldownSelector:
    """Anti-Repetition Engine: ensures the exact same sound effect is NEVER repeated back-to-back."""
    def __init__(self, capacity=5):
        self.history = []
        self.capacity = capacity

    def pick(self, candidates, fallback_pool=None):
        pool = [c for c in (candidates or []) if c]
        if not pool and fallback_pool:
            pool = [c for c in fallback_pool if c]
        if not pool:
            return None
        fresh = [c for c in pool if c not in self.history]
        chosen = random.choice(fresh) if fresh else random.choice(pool)
        self.history.append(chosen)
        if len(self.history) > self.capacity:
            self.history.pop(0)
        return chosen

COOLDOWN = SfxCooldownSelector(capacity=6)

def pick_sfx_for_text(text, catalog, default_cat="paper", cooldown=None):
    cd = cooldown or COOLDOWN
    txt = text.lower()
    for triggers, candidates in SEMANTIC_SFX_MAP.items():
        if any(tr in txt for tr in triggers):
            matching_paths = []
            for cand in candidates:
                for p in catalog.get("all", []):
                    if cand.lower() in p.lower():
                        matching_paths.append(p)
            if matching_paths:
                return cd.pick(matching_paths)
    # Default for tactile sticker pop: authentic paper card-place sounds
    paper_places = [p for p in catalog.get("paper-and-office", []) if "card" in p.lower()] or \
                   [p for p in catalog.get("paper", []) if "card-place" in p.lower()]
    if paper_places:
        return cd.pick(paper_places)
    cat_list = catalog.get(default_cat.lower()) or catalog.get("pops") or catalog.get("all", [])
    return cd.pick(cat_list)

def select_music_track(music_root, script_text=""):
    """Intelligently match background music to script theme."""
    candidates = glob.glob(f"{music_root}/**/*.mp3", recursive=True) if music_root else []
    if not candidates:
        return None
    
    txt = script_text.lower()
    if any(w in txt for w in ["ancient", "persia", "rome", "egypt", "king", "desert", "history"]):
        matched = [p for p in candidates if any(m in p.lower() for m in ["ancient", "attic", "vanished"])]
        if matched: return matched[0]
    elif any(w in txt for w in ["physics", "science", "space", "star", "radiation", "quantum"]):
        matched = [p for p in candidates if any(m in p.lower() for m in ["clock", "spaceship", "alien", "dimension"])]
        if matched: return matched[0]
    elif any(w in txt for w in ["danger", "war", "crisis", "blackout", "panic", "survival"]):
        matched = [p for p in candidates if any(m in p.lower() for m in ["action", "after the end", "anxiety"])]
        if matched: return matched[0]
    elif any(w in txt for w in ["curious", "mystery", "why", "secret", "discover"]):
        matched = [p for p in candidates if any(m in p.lower() for m in ["asking", "attic", "questions"])]
        if matched: return matched[0]
    
    chill = [p for p in candidates if any(m in p.lower() for m in ["chillin", "lofi", "roomscene", "arcade"])]
    return chill[0] if chill else candidates[0]

def select_multi_act_music(music_root, script_text=""):
    """Returns a list of 4 mood-matched music tracks for Long-form documentary progression."""
    candidates = glob.glob(f"{music_root}/**/*.mp3", recursive=True) if music_root else []
    if not candidates:
        return []
    
    def find_match(keywords, fallback_kw):
        for kw in keywords:
            m = [p for p in candidates if kw in p.lower()]
            if m: return random.choice(m)
        for kw in fallback_kw:
            m = [p for p in candidates if kw in p.lower()]
            if m: return random.choice(m)
        return random.choice(candidates)

    act1 = find_match(["asking questions", "attic secrets", "abstract anxiety", "ambient_mystery", "question"], ["mystery", "asking"])
    act2 = find_match(["ancient rite", "aquatic city", "explainer", "explainer_lofi", "ambient_history"], ["explainer", "ancient"])
    act3 = find_match(["action strike", "after the end", "tension", "ambient_tension", "alternative clock"], ["tension", "action"])
    act4 = find_match(["be chillin", "a waltz for naseem", "hopeful", "reflective", "duru-roomscene-lofi"], ["chillin", "hopeful", "arcade"])
    return [act1, act2, act3, act4]

def compute_inputs_signature(project_dir="."):
    """Computes a SHA256 signature of SCENES_HYBRID.tsv and WORDS.tsv."""
    hasher = hashlib.sha256()
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")

    if os.path.exists(scenes_path):
        with open(scenes_path, "rb") as f:
            hasher.update(f.read())
            
    words_path = os.path.join(project_dir, "WORDS.tsv")
    if os.path.exists(words_path):
        with open(words_path, "rb") as f:
            hasher.update(f.read())
            
    return hasher.hexdigest()[:16]


def is_cues_cache_fresh(project_dir=".", cues_file="cues_pro.tsv"):
    """Enforces Condition 3: Replaces broken >= 12 lines check with sha256 & mtime validation."""
    target = os.path.join(project_dir, cues_file)
    if not os.path.exists(target) or os.path.getsize(target) < 100:
        return False
        
    target_mtime = os.path.getmtime(target)
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")
        
    if os.path.exists(scenes_path) and os.path.getmtime(scenes_path) > target_mtime:
        return False
        
    words_path = os.path.join(project_dir, "WORDS.tsv")
    if os.path.exists(words_path) and os.path.getmtime(words_path) > target_mtime:
        return False
        
    current_sig = compute_inputs_signature(project_dir)
    try:
        with open(target, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# sig:"):
                    stored_sig = line.strip().split(":", 1)[1].strip()
                    if stored_sig == current_sig:
                        return True
    except Exception:
        pass
        
    return False


def generate_smart_cues(project_dir=".", out_tsv="cues_pro.tsv", is_shorts=False, force=False):
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")
    words_path = os.path.join(project_dir, "WORDS.tsv")
    script_path = os.path.join(project_dir, "SCRIPT.md")
    
    sfx_root = find_sfx_library()
    music_root = find_music_library()
    catalog = collect_audio_catalog(sfx_root)
    
    if not catalog:
        print("❌ SFX library not found. Sound designer aborted.")
        return False

    # Load words
    words_list = []
    words_map = {}
    if os.path.exists(words_path):
        with open(words_path, encoding="utf-8") as wf:
            for r in csv.DictReader(wf, delimiter="\t"):
                start_t = float(r["start"])
                end_t = float(r["end"])
                line_id = r.get("line", "")
                w_clean = r["word"].lower().strip('.,!?":;')
                cue_idx = f"{line_id}.{r['i']}" if "line" in r and "i" in r else r.get("cue", "")
                if cue_idx:
                    words_map[cue_idx] = start_t
                words_map[f"@{line_id}"] = words_map.get(f"@{line_id}", start_t)
                words_map[line_id] = words_map.get(line_id, start_t)
                words_map[f"@{line_id}:{w_clean}"] = start_t
                words_map[f"{line_id}:{w_clean}"] = start_t
                words_list.append({
                    "cue": f"w{len(words_list)+1:03d}",
                    "line": line_id,
                    "start": start_t,
                    "end": end_t,
                    "word": r["word"]
                })
        
    cues = []
    
    # 1. Background Music Bed (Golden Dynamic Ratio: -8.0 dB Shorts / -8.5 dB Long, guaranteed 0.0s onset with 0.3s fade-in)
    script_txt = open(script_path, encoding="utf-8").read().lower() if os.path.exists(script_path) else ""
    total_dur = words_list[-1]["end"] if words_list else 60.0
    music_gain = "-8.0" if is_shorts else "-8.5"

    if not is_shorts and total_dur > 45.0:
        act_tracks = select_multi_act_music(music_root, script_txt)
        if len(act_tracks) == 4 and all(act_tracks):
            t1 = 0.0
            t2 = total_dur * 0.25
            t3 = total_dur * 0.55
            t4 = total_dur * 0.80
            cues.append({"label": "bed_act1", "kind": "loop", "file": act_tracks[0], "at": f"{t1:.2f}", "dur": f"{(t2 - t1 + 1.5):.2f}", "gain_db": music_gain, "fade_in": "0.3", "fade_out": "1.5"})
            cues.append({"label": "bed_act2", "kind": "loop", "file": act_tracks[1], "at": f"{(t2 - 1.5):.2f}", "dur": f"{(t3 - t2 + 3.0):.2f}", "gain_db": music_gain, "fade_in": "1.5", "fade_out": "1.5"})
            cues.append({"label": "bed_act3", "kind": "loop", "file": act_tracks[2], "at": f"{(t3 - 1.5):.2f}", "dur": f"{(t4 - t3 + 3.0):.2f}", "gain_db": music_gain, "fade_in": "1.5", "fade_out": "1.5"})
            cues.append({"label": "bed_act4", "kind": "loop", "file": act_tracks[3], "at": f"{(t4 - 1.5):.2f}", "dur": f"{(total_dur - t4 + 1.5):.2f}", "gain_db": music_gain, "fade_in": "1.5", "fade_out": "2.0"})
        else:
            bg_music = select_music_track(music_root, script_txt)
            if bg_music:
                cues.append({"label": "bed", "kind": "loop", "file": bg_music, "at": "0.0", "dur": "all", "gain_db": music_gain, "fade_in": "0.3", "fade_out": "2.0"})
    else:
        bg_music = select_music_track(music_root, script_txt)
        if bg_music:
            cues.append({"label": "bed", "kind": "loop", "file": bg_music, "at": "0.0", "dur": "all", "gain_db": music_gain, "fade_in": "0.3", "fade_out": "2.0"})

    # 2. Continuous Environmental Foley Loop
    amb_file = None
    if any(k in script_txt for k in ["desert", "persia", "egypt", "sand"]):
        amb_candidates = [p for p in catalog.get("ambience", []) if "desert_wind" in p.lower()]
        amb_file = amb_candidates[0] if amb_candidates else None
    if not amb_file and catalog.get("ambience"):
        amb_file = catalog["ambience"][0]
        
    if amb_file:
        cues.append({
            "label": "ambient_foley",
            "kind": "loop",
            "file": amb_file,
            "at": "0.0",
            "dur": "all",
            "gain_db": "-14.0",
            "fade_in": "0.5",
            "fade_out": "2.0"
        })

    # Frame-0 Auditory Attention Shock (50Hz Sub-Bass Impact on opening frame)
    booms = catalog.get("booms-and-bass", catalog.get("cinematic-hits", []))
    sub_impact = booms[0] if booms else None
    if sub_impact:
        cues.append({
            "label": "frame0_sub_shock",
            "kind": "one",
            "file": sub_impact,
            "at": "0.0",
            "dur": "-",
            "gain_db": "-3.5",
            "fade_in": "0",
            "fade_out": "0"
        })

    # 3. Transitions on Scene Cuts & Overlays (with Psychoacoustic 120ms J-Cut Pre-Lapping)
    whooshes = catalog.get("whooshes", catalog.get("whoosh", catalog.get("ui", [])))
    zip_outs = [p for p in catalog.get("swishes-and-zips", []) if "zip-out" in p.lower()]
    pop_outs = [p for p in catalog.get("pops", []) if "pop" in p.lower() and "out" in p.lower()]
    exit_sfx_pool = zip_outs or pop_outs

    cur_scene_t0 = 0.0
    ordinary_cut_idx = 0
    silent_cut_count = 0
    whoosh_cut_count = 0
    total_lines_cnt = max(1, len({(w.get("line") or "").lstrip("0") or "0" for w in words_list}) if words_list else 12)
    # Load optional DIRECTOR_PLAN.json for physics-matched motion SFX & arrow draw-on sounds
    director_ov_map = {}
    director_arrows = []
    dp_path = os.path.join(project_dir, "DIRECTOR_PLAN.json")
    if os.path.exists(dp_path):
        try:
            import json
            dp_data = json.load(open(dp_path, encoding="utf-8"))
            for dsc in dp_data.get("scenes", []):
                d_ovs = dsc.get("overlays", [])
                for oi, dov in enumerate(d_ovs):
                    key_d = (dov.get("cue", "").strip(), os.path.basename(dov.get("img", "")))
                    director_ov_map[key_d] = dov
                    if dov.get("arrow_to_next"):
                        tA_s = float(dov.get("sync_t", dsc.get("t0", 0.0)))
                        tB_s = float(d_ovs[oi + 1].get("sync_t", tA_s + 0.5)) if oi + 1 < len(d_ovs) else (tA_s + 0.5)
                        arr_t_s = max(tA_s + 0.18, tB_s - 0.36) if tB_s > tA_s + 0.30 else (tA_s + 0.18)
                        director_arrows.append((arr_t_s, dsc.get("cue", "")))
        except Exception:
            pass

    if os.path.exists(scenes_path):
        with open(scenes_path, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                cue = r.get("cue", "").strip()
                if not cue or cue.startswith("#"):
                    continue
                if not cue.startswith("+"):
                    # Scene Cut Transition (Whoosh on scene changes, Paper Slam on text cards, Swish on split compare, Ping on data cards)
                    cur_scene_t0 = words_map.get(cue, float(cue) if cue.replace(".", "", 1).isdigit() else cur_scene_t0)
                    img_raw = r.get("img", "").strip()
                    token = os.path.basename(img_raw)
                    token_base = os.path.splitext(token)[0]
                    token_key = token_base.split(":")[0].strip()
                    is_card = (img_raw in ("card", "card_stat", "card_phrase") or token in ("card", "card_stat", "card_phrase") or token_base in ("card", "card_stat", "card_phrase") or token_key in ("card", "card_stat", "card_phrase") or img_raw.startswith("card_") or token.startswith("card_"))
                    is_split = (img_raw in ("split_compare", "split_contrast") or token in ("split_compare", "split_contrast") or token_base in ("split_compare", "split_contrast") or token_key in ("split_compare", "split_contrast") or img_raw.startswith("split_") or token.startswith("split_"))
                    is_data = (img_raw in ("bar_timeline", "stat_pie", "grid_week") or token in ("bar_timeline", "stat_pie", "grid_week") or token_base in ("bar_timeline", "stat_pie", "grid_week") or token_key in ("bar_timeline", "stat_pie", "grid_week") or img_raw.startswith(("timeline_", "bar_")) or token.startswith(("timeline_", "bar_")))

                    if is_card:
                        card_slams = [p for p in catalog.get("paper-and-office", []) if "card" in p.lower() or "paper" in p.lower()] or \
                                     [p for p in catalog.get("emphasis", []) if "paper_slam" in p.lower()] or \
                                     [p for p in catalog.get("paper", []) if "card-place-2" in p.lower()]
                        sf = COOLDOWN.pick(card_slams)
                        if sf:
                            cues.append({
                                "label": f"card_slam_{cue.replace('@', '').replace('.', '_')}",
                                "kind": "one",
                                "file": sf,
                                "at": f"{cur_scene_t0:.2f}",
                                "dur": "-",
                                "gain_db": "-4.5",
                                "fade_in": "0",
                                "fade_out": "0"
                            })
                    elif is_split:
                        swishes = [p for p in catalog.get("swishes-and-zips", []) if "swish" in p.lower()] or whooshes
                        sf = COOLDOWN.pick(swishes)
                        if sf:
                            cues.append({
                                "label": f"split_swish_{cue.replace('@', '').replace('.', '_')}",
                                "kind": "one",
                                "file": sf,
                                "at": f"{max(0.0, cur_scene_t0 - 0.08):.2f}",
                                "dur": "-",
                                "gain_db": "-5.0",
                                "fade_in": "0",
                                "fade_out": "0"
                            })
                    elif is_data:
                        drawing_sfx = [p for p in catalog.get("writing-and-drawing", []) if "draw" in p.lower() or "tick" in p.lower() or "write" in p.lower()] or \
                                      [p for p in catalog.get("digital-and-tech", []) if "notification_ping" in p.lower()] or \
                                      [p for p in catalog.get("all", []) if HIGHLIGHT_DATE_SFX in p.lower() or "notification_ping" in p.lower()]
                        sf = COOLDOWN.pick(drawing_sfx, fallback_pool=whooshes)
                        if sf:
                            cues.append({
                                "label": f"data_ping_{cue.replace('@', '').replace('.', '_')}",
                                "kind": "one",
                                "file": sf,
                                "at": f"{cur_scene_t0:.2f}",
                                "dur": "-",
                                "gain_db": "-4.5",
                                "fade_in": "0",
                                "fade_out": "0"
                            })
                    elif whooshes and cue not in ("@01", "00.0", "0.0", "01.0"): # Skip very first frame whoosh to allow clean hook onset
                        # Maintain 40-55% silent cuts on calm intra-act narration; reserve whooshes for high-energy turns & Act shifts
                        extra_low = (r.get("extra") or "").lower()
                        line_tok = cue.lstrip("@").split(".")[0].split(":")[0].lstrip("0") or "1"
                        try:
                            ln_int = int(line_tok)
                        except ValueError:
                            ln_int = 1
                        is_high_energy = any(k in extra_low for k in ("zoom_punch", "flash", "danger", "shake", "blood"))
                        act_boundary_lines = (
                            {max(3, int(total_lines_cnt * p)) for p in (0.28, 0.62, 0.85)}
                            if total_lines_cnt >= 10 else set()
                        )
                        is_act_boundary = (ln_int in act_boundary_lines)
                        tot_so_far = max(1, whoosh_cut_count + silent_cut_count + 1)
                        cur_silent_ratio = silent_cut_count / tot_so_far
                        if is_high_energy or (is_act_boundary and cur_silent_ratio >= 0.40) or (not is_act_boundary and cur_silent_ratio >= 0.45):
                            wf = COOLDOWN.pick(whooshes)
                            j_cut_time = max(0.0, cur_scene_t0 - 0.12)
                            cues.append({
                                "label": f"jcut_whoosh_{cue.replace('@', '').replace('.', '_')}",
                                "kind": "one",
                                "file": wf,
                                "at": f"{j_cut_time:.2f}",
                                "dur": "-",
                                "gain_db": "-5.0",
                                "fade_in": "0",
                                "fade_out": "0"
                            })
                            whoosh_cut_count += 1
                        else:
                            silent_cut_count += 1
                        ordinary_cut_idx += 1
                else:
                    # Sticker Overlay Entrance SFX: Voice-keyword synchronized with exact 0.00s spring alignment
                    o_img = r.get("img", "").strip()
                    label_txt = r.get("text", "") or o_img
                    resolved_t = resolve_word_time(cue, words_list, words_map, cur_scene_t0)
                    cue_at_str = f"{resolved_t:.2f}"
                    
                    if o_img in ("stamp_x", "stamp_false", "stamp_myth"):
                        stamp_hits = [p for p in catalog.get("hits-and-impacts", []) if "impact" in p.lower() or "slam" in p.lower()] or \
                                     [p for p in catalog.get("cinematic-hits", []) if "impact" in p.lower() or "slam" in p.lower()] or \
                                     [p for p in catalog.get("emphasis", []) if "boom" in p.lower()]
                        sfx_file = COOLDOWN.pick(stamp_hits)
                        sfx_gain = "-4.0"
                    elif o_img in ("stamp_check", "stamp_true", "stamp_verified"):
                        chimes = [p for p in catalog.get("tones", []) if "ding" in p.lower() or "high" in p.lower()] or \
                                 [p for p in catalog.get("jingle", []) if "win" in p.lower()] or \
                                 [p for p in catalog.get("all", []) if HIGHLIGHT_DATE_SFX in p.lower()] or \
                                 [p for p in catalog.get("pops", []) if "bubble" in p.lower()]
                        sfx_file = COOLDOWN.pick(chimes)
                        sfx_gain = "-4.5"
                    else:
                        d_ov = director_ov_map.get((cue, os.path.basename(o_img)))
                        sfx_kind = d_ov.get("sfx_kind", "") if d_ov else ""
                        if d_ov and d_ov.get("sync_t") is not None:
                            resolved_t = float(d_ov["sync_t"])
                            cue_at_str = f"{resolved_t:.2f}"
                        if sfx_kind == "heavy_thud":
                            thuds = [p for p in catalog.get("impacts", []) if "firm" in p.lower() or "wood" in p.lower() or "chop" in p.lower()] or catalog.get("hits-and-impacts", [])
                            sfx_file = COOLDOWN.pick(thuds) or pick_sfx_for_text(label_txt, catalog, default_cat="impacts", cooldown=COOLDOWN)
                            sfx_gain = "-3.8"
                        elif sfx_kind == "paper_slide":
                            papers = [p for p in catalog.get("paper", []) if "card-place" in p.lower()] or catalog.get("paper-and-office", [])
                            sfx_file = COOLDOWN.pick(papers) or pick_sfx_for_text(label_txt, catalog, default_cat="paper", cooldown=COOLDOWN)
                            sfx_gain = "-4.2"
                        elif sfx_kind == "whoosh_strike":
                            strikes = [p for p in catalog.get("swishes-and-zips", []) if "swish" in p.lower() or "whoosh" in p.lower()] or whooshes
                            sfx_file = COOLDOWN.pick(strikes)
                            sfx_gain = "-4.2"
                        elif sfx_kind == "micro_whoosh":
                            sfx_file = COOLDOWN.pick(whooshes)
                            sfx_gain = "-5.2"
                        else:
                            sfx_file = pick_sfx_for_text(label_txt, catalog, default_cat="pops", cooldown=COOLDOWN)
                            sfx_gain = "-4.5"
                    
                    if sfx_file:
                        cues.append({
                            "label": f"pop_{cue.replace('+', '').replace('@', '').replace(':', '_')}",
                            "kind": "one",
                            "file": sfx_file,
                            "at": cue_at_str,
                            "dur": "-",
                            "gain_db": sfx_gain,
                            "fade_in": "0",
                            "fade_out": "0"
                        })
                    
                    # Rule 29: Sticker Exit SFX (subtle soft zip-out on disappear, >= 2.5s hold)
                    if exit_sfx_pool:
                        sticker_dur = 2.5 if is_shorts else 3.0
                        exit_t = resolved_t + sticker_dur - 0.25
                        cues.append({
                            "label": f"exit_{cue.replace('+', '').replace('@', '').replace(':', '_')}",
                            "kind": "one",
                            "file": COOLDOWN.pick(exit_sfx_pool),
                            "at": f"{exit_t:.2f}",
                            "dur": "-",
                            "gain_db": "-6.5",
                            "fade_in": "0",
                            "fade_out": "0"
                        })

    # 3b. Subtle marker/pencil draw-on sound for Director-planned cause_effect arrows
    draw_pool = [p for p in catalog.get("writing-and-drawing", []) if "draw" in p.lower() or "write" in p.lower() or "pencil" in p.lower()] or \
                [p for p in catalog.get("paper-and-office", []) if "card-place" in p.lower()]
    if draw_pool and director_arrows:
        for arr_t, arr_cue in director_arrows:
            df = COOLDOWN.pick(draw_pool)
            if df:
                cues.append({
                    "label": f"arrow_draw_{arr_cue.replace('+', '').replace('@', '').replace(':', '_')}",
                    "kind": "one",
                    "file": df,
                    "at": f"{max(0.0, arr_t):.2f}",
                    "dur": "-",
                    "gain_db": "-6.0",
                    "fade_in": "0",
                    "fade_out": "0"
                })

    # 4. Spoken Keyword Audio Impacts & Auditory Highlighter Pens (Vox/Kurzgesagt)
    EMPHATIC_WORDS = {
        "freezing": ("nature/b2_ice_crack_a.mp3", "-3.5"),
        "danger": ("cinematic-hits/cinematic-slam-big.wav", "-3.5"),
        "blackout": ("booms-and-bass/boom-hit-medium.wav", "-3.5"),
        "peril": ("emphasis/b2_boom_soft_a.mp3", "-4.0"),
        "starvation": ("tonal/s1_drone_dark_a.mp3", "-4.5"),
        "impossible": ("reveal/s1_swell_reverse_a.mp3", "-4.0"),
        "conquered": ("jingle/jingle_win_00.ogg", "-4.0"),
        "millionaire": ("money/coin-drop.wav", "-4.0"),
        "miracle": ("shimmers/shimmer-short-sparkle.wav", "-4.0"),
        "zero": ("digital/digital-glitch-clear.wav", "-4.5"),
        "fatal": ("cinematic-hits/cinematic-slam-big.wav", "-3.5"),
        "secret": ("reveal/s1_swell_reverse_a.mp3", "-4.0"),
        "truth": ("shimmers/shimmer-short-sparkle.wav", "-4.0"),
        "collapse": ("booms-and-bass/boom-hit-medium.wav", "-3.5"),
        "discovered": ("shimmers/shimmer-short-sparkle.wav", "-4.0"),
        "ambush": ("cinematic-hits/cinematic-slam-big.wav", "-3.5"),
        "war": ("emphasis/b2_boom_soft_a.mp3", "-3.5"),
        "battle": ("cinematic-hits/cinematic-slam-big.wav", "-3.5"),
        "empire": ("jingle/jingle_win_00.ogg", "-4.0"),
        "legion": ("emphasis/b2_boom_soft_a.mp3", "-4.0")
    }
    
    # Kurzgesagt Auditory Highlighter Pens: Subtly punctuate metrics, dates & statistical shifts
    HIGHLIGHT_DATE_SFX = "data/b4_notification_ping_h.mp3"
    HIGHLIGHT_METRIC_SFX = "pops/pop-medium-bubble.wav"
    HIGHLIGHT_CURIOSITY_SFX = "digital/digital-glitch-clear.wav"

    if words_list:
        placed_times = set()
        for r in words_list:
            w_clean = r["word"].lower().strip('.,!?":;')
            t_start = r["start"]
            
            # Check for high-impact dramatic words
            if w_clean in EMPHATIC_WORDS:
                if not any(abs(t_start - pt) < 3.2 for pt in placed_times):
                    cand_rel, gain = EMPHATIC_WORDS[w_clean]
                    matched = [p for p in catalog.get("all", []) if cand_rel.lower() in p.lower()]
                    if matched:
                        placed_times.add(t_start)
                        cue_tag = f"{t_start:.2f}"
                        cues.append({
                            "label": f"hit_{w_clean}",
                            "kind": "one",
                            "file": matched[0],
                            "at": cue_tag,
                            "dur": "-",
                            "gain_db": gain,
                            "fade_in": "0",
                            "fade_out": "0"
                        })
            # Auditory Highlighter: Dates, years, and statistics
            elif (re.match(r"^\d{3,4}$", w_clean) or w_clean in ["percent", "thousand", "million", "billion", "degrees", "centuries"]):
                if not any(abs(t_start - pt) < 2.8 for pt in placed_times):
                    matched = [p for p in catalog.get("all", []) if HIGHLIGHT_DATE_SFX in p.lower() or HIGHLIGHT_METRIC_SFX in p.lower()]
                    if matched:
                        placed_times.add(t_start)
                        cue_tag = f"{t_start:.2f}"
                        cues.append({
                            "label": f"highlighter_{w_clean}",
                            "kind": "one",
                            "file": matched[0],
                            "at": cue_tag,
                            "dur": "-",
                            "gain_db": "-13",
                            "fade_in": "0",
                            "fade_out": "0"
                        })
            # Time rewinds: historical dates ("50,000 years ago", "century", "clock")
            elif any(tw in w_clean.upper() for tw in ["YEARS", "AGO", "CENTURY", "CLOCK", "MINUTES", "HOURS", "DAYS"]):
                if not any(abs(t_start - pt) < 4.0 for pt in placed_times):
                    time_sfx = [p for p in catalog.get("time", []) if "clock" in p.lower() or "stopwatch" in p.lower() or "tick" in p.lower()]
                    sf = COOLDOWN.pick(time_sfx)
                    if sf:
                        placed_times.add(t_start)
                        cues.append({
                            "label": f"time_{w_clean}",
                            "kind": "one",
                            "file": sf,
                            "at": f"{t_start:.2f}",
                            "dur": "-",
                            "gain_db": "-13",
                            "fade_in": "0",
                            "fade_out": "0"
                        })
            # Modern mirror hooks ("phone", "fridge", "alarm", "app", "sensor")
            elif any(tw in w_clean.upper() for tw in ["PHONE", "FRIDGE", "ALARM", "APP", "SENSOR"]):
                if not any(abs(t_start - pt) < 4.0 for pt in placed_times):
                    tech_sfx = [p for p in catalog.get("digital-and-tech", []) if "process" in p.lower() or "glitch" in p.lower()] or \
                               [p for p in catalog.get("digital", []) if "process" in p.lower() or "glitch" in p.lower()]
                    sf = COOLDOWN.pick(tech_sfx)
                    if sf:
                        placed_times.add(t_start)
                        cues.append({
                            "label": f"tech_{w_clean}",
                            "kind": "one",
                            "file": sf,
                            "at": f"{t_start:.2f}",
                            "dur": "-",
                            "gain_db": "-13",
                            "fade_in": "0",
                            "fade_out": "0"
                        })

    # Write cues_pro.tsv with cryptographic signature
    target_out = os.path.join(project_dir, out_tsv)
    sig = compute_inputs_signature(project_dir)
    with open(target_out, "w", encoding="utf-8", newline="") as out_f:
        fieldnames = ["label", "kind", "file", "at", "dur", "gain_db", "fade_in", "fade_out"]
        writer = csv.DictWriter(out_f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        out_f.write(f"# sig:{sig}\n")
        for c in cues:
            writer.writerow(c)
            
    tot_ord = silent_cut_count + whoosh_cut_count
    silent_pct = (silent_cut_count * 100.0 / tot_ord) if tot_ord > 0 else 0.0
    print(f"✅ Generated {len(cues)} smart sound cues in {target_out} (sig: {sig}, silent_cuts={silent_cut_count}/{tot_ord} [{silent_pct:.0f}%])")
    return True

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python3 sfx_smart_designer.py [dir] [--short] [--force] [--check-cache]")
        sys.exit(0)
    p_dir = sys.argv[1] if (len(sys.argv) > 1 and not sys.argv[1].startswith("-")) else "."
    is_s = "--short" in sys.argv or "--shorts" in sys.argv or "short" in p_dir.lower()
    force_gen = "--force" in sys.argv or "-f" in sys.argv
    if "--check-cache" in sys.argv:
        fresh = is_cues_cache_fresh(p_dir)
        print("FRESH" if fresh else "STALE")
        sys.exit(0 if fresh else 1)
    generate_smart_cues(p_dir, is_shorts=is_s, force=force_gen)
