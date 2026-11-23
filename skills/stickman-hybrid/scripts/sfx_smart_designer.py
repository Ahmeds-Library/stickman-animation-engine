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

import os, sys, csv, random, subprocess, glob, re

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
            parts = rel.split(os.sep)
            cat = parts[1] if len(parts) > 1 else parts[0]
            catalog.setdefault(cat.lower(), []).append(path)
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
    ]
}

def pick_sfx_for_text(text, catalog, default_cat="pops"):
    txt = text.lower()
    for triggers, candidates in SEMANTIC_SFX_MAP.items():
        if any(tr in txt for tr in triggers):
            for cand in candidates:
                for p in catalog.get("all", []):
                    if cand.lower() in p.lower():
                        return p
    cat_list = catalog.get(default_cat.lower(), catalog.get("all", []))
    return random.choice(cat_list) if cat_list else None

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

def generate_smart_cues(project_dir=".", out_tsv="cues_pro.tsv", is_shorts=False):
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
                words_map[f"@{line_id}"] = words_map.get(f"@{line_id}", start_t)
                words_map[f"@{line_id}:{w_clean}"] = start_t
                words_list.append({
                    "cue": f"w{len(words_list)+1:03d}",
                    "line": line_id,
                    "start": start_t,
                    "end": end_t,
                    "word": r["word"]
                })
        
    cues = []
    
    # 1. Background Music Bed (Storytelling Golden Ratio: -17 dB Long / -16 dB Shorts with Vocal Pocket EQ)
    script_txt = open(script_path, encoding="utf-8").read().lower() if os.path.exists(script_path) else ""
    bg_music = select_music_track(music_root, script_txt)
    music_gain = "-16" if is_shorts else "-17"
    if bg_music:
        cues.append({
            "label": "bed",
            "kind": "loop",
            "file": bg_music,
            "at": "0.0",
            "dur": "all",
            "gain_db": music_gain,
            "fade_in": "1.2",
            "fade_out": "2.0"
        })

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
            "gain_db": "-23",
            "fade_in": "1.5",
            "fade_out": "2.0"
        })

    # 3. Transitions on Scene Cuts & Overlays
    whooshes = catalog.get("whooshes", catalog.get("whoosh", catalog.get("ui", [])))
    zip_outs = [p for p in catalog.get("swishes-and-zips", []) if "zip-out" in p.lower()]
    pop_outs = [p for p in catalog.get("pops", []) if "pop" in p.lower() and "out" in p.lower()]
    exit_sfx_pool = zip_outs or pop_outs

    cur_scene_t0 = 0.0
    if os.path.exists(scenes_path):
        with open(scenes_path, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                cue = r.get("cue", "").strip()
                if not cue or cue.startswith("#"):
                    continue
                if not cue.startswith("+"):
                    # Scene Cut Transition Whoosh
                    cur_scene_t0 = words_map.get(cue, float(cue) if cue.replace(".", "", 1).isdigit() else cur_scene_t0)
                    if whooshes and cue != "@01": # Skip very first frame whoosh to allow clean hook onset
                        wf = random.choice(whooshes)
                        cues.append({
                            "label": f"cut_{cue.replace('@', '')}",
                            "kind": "one",
                            "file": wf,
                            "at": cue,
                            "dur": "-",
                            "gain_db": "-21",
                            "fade_in": "0",
                            "fade_out": "0"
                        })
                else:
                    # Sticker Overlay Entrance SFX: Voice-keyword synchronized
                    label_txt = r.get("text", "") or r.get("img", "")
                    sfx_file = pick_sfx_for_text(label_txt, catalog, default_cat="pops")
                    resolved_t = resolve_word_time(cue, words_list, words_map, cur_scene_t0)
                    cue_at_str = f"{resolved_t:.2f}"
                    
                    if sfx_file:
                        cues.append({
                            "label": f"pop_{cue.replace('+', '').replace('@', '').replace(':', '_')}",
                            "kind": "one",
                            "file": sfx_file,
                            "at": cue_at_str,
                            "dur": "-",
                            "gain_db": "-16",
                            "fade_in": "0",
                            "fade_out": "0"
                        })
                    
                    # Rule 29: Sticker Exit SFX (subtle soft zip-out on disappear)
                    if exit_sfx_pool:
                        sticker_dur = 1.8 if is_shorts else 2.2
                        exit_t = resolved_t + sticker_dur - 0.28
                        cues.append({
                            "label": f"exit_{cue.replace('+', '').replace('@', '').replace(':', '_')}",
                            "kind": "one",
                            "file": random.choice(exit_sfx_pool),
                            "at": f"{exit_t:.2f}",
                            "dur": "-",
                            "gain_db": "-26",
                            "fade_in": "0",
                            "fade_out": "0"
                        })

    # 4. Spoken Keyword Audio Impacts & Auditory Highlighter Pens (Vox/Kurzgesagt)
    EMPHATIC_WORDS = {
        "freezing": ("nature/b2_ice_crack_a.mp3", "-18"),
        "danger": ("cinematic-hits/cinematic-slam-big.wav", "-17"),
        "blackout": ("booms-and-bass/boom-hit-medium.wav", "-17"),
        "peril": ("emphasis/b2_boom_soft_a.mp3", "-18"),
        "starvation": ("tonal/s1_drone_dark_a.mp3", "-19"),
        "impossible": ("reveal/s1_swell_reverse_a.mp3", "-18"),
        "conquered": ("jingle/jingle_win_00.ogg", "-17"),
        "millionaire": ("money/coin-drop.wav", "-16"),
        "miracle": ("shimmers/shimmer-short-sparkle.wav", "-17"),
        "zero": ("digital/digital-glitch-clear.wav", "-18"),
        "fatal": ("cinematic-hits/cinematic-slam-big.wav", "-17"),
        "secret": ("reveal/s1_swell_reverse_a.mp3", "-19"),
        "truth": ("shimmers/shimmer-short-sparkle.wav", "-19"),
        "collapse": ("booms-and-bass/boom-hit-medium.wav", "-17"),
        "discovered": ("shimmers/shimmer-short-sparkle.wav", "-18")
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
                        line_id = r.get("line", "")
                        cue_tag = f"@{line_id}:{w_clean}" if line_id else f"{t_start:.2f}"
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
                        line_id = r.get("line", "")
                        cue_tag = f"@{line_id}:{w_clean}" if line_id else f"{t_start:.2f}"
                        cues.append({
                            "label": f"highlighter_{w_clean}",
                            "kind": "one",
                            "file": matched[0],
                            "at": cue_tag,
                            "dur": "-",
                            "gain_db": "-22",
                            "fade_in": "0",
                            "fade_out": "0"
                        })

    # Write cues_pro.tsv
    target_out = os.path.join(project_dir, out_tsv)
    with open(target_out, "w", encoding="utf-8", newline="") as out_f:
        fieldnames = ["label", "kind", "file", "at", "dur", "gain_db", "fade_in", "fade_out"]
        writer = csv.DictWriter(out_f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for c in cues:
            writer.writerow(c)
            
    print(f"✅ Generated {len(cues)} smart sound cues in {target_out}")
    return True

if __name__ == "__main__":
    p_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    is_s = "--short" in sys.argv or "--shorts" in sys.argv or "short" in p_dir.lower()
    generate_smart_cues(p_dir, is_shorts=is_s)
