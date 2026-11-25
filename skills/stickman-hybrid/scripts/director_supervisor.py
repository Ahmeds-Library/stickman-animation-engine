#!/usr/bin/env python3
"""director_supervisor.py: Permanent Director Supervision & Motion Choreography Engine
Runs after align_hybrid_scenes.py (inside pipeline_dual.py, validate_pipeline.py, evaluate_rl.py)
and writes DIRECTOR_PLAN.json with:
1. Logical Relevance Audit (zero random clipart, auto-reject redundant stickers on matching shots)
2. Exact Spoken Word Time-Sync Lock (WORDS.tsv @ -0.06s anticipation + progressive list unbinding)
3. Shot-Scale & Continuity Supervision (WIDE / MEDIUM / TIGHT / EDITORIAL_CARD / SPLIT / DATA)
4. 6 Context-Aware Motion Archetypes + Group Choreography Patterns + Physics-Matched SFX intents
"""

import os
import re
import sys
import csv
import json
import argparse

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

STOP_TOKENS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "of", "to", "for", "with", "by", "from",
    "into", "across", "stickman", "stickmen", "figure", "cartoon", "2d", "style", "hand", "drawn",
    "clean", "ink", "outlines", "outline", "flat", "color", "colors", "warm", "paper", "bright",
    "background", "isolated", "single", "one", "scene", "shot", "png", "cut", "elements", "cc0",
}

SEMANTIC_ROOTS = {
    "fire": {"fire", "flame", "burn", "burning", "torch", "blaze", "ember", "ash", "smoke", "inferno"},
    "ruin": {"ruin", "ruins", "crumble", "collapse", "destroyed", "column", "palace", "temple", "rubble"},
    "grain": {"grain", "wheat", "crop", "crops", "harvest", "famine", "drought", "food", "starvation"},
    "ship": {"ship", "ships", "warship", "prow", "galley", "fleet", "raider", "raiders", "sea", "maritime", "trade", "harbor", "port", "boat"},
    "metal": {"tin", "copper", "bronze", "ingot", "metal", "alloy", "weapon", "weapons", "sword", "spear", "blade", "armor"},
    "document": {"tablet", "clay", "cuneiform", "scroll", "letter", "letters", "archive", "record", "records", "book", "map"},
    "money": {"coin", "gold", "trade", "economy", "wealth", "price", "cost", "merchant", "market"},
    "science": {"dna", "atom", "planet", "thermometer", "cold", "freeze", "ice", "volcano", "brain", "lightbulb"},
    "time": {"clock", "alarm", "year", "years", "century", "bc", "timeline", "ancient"},
    "warrior": {"warrior", "soldier", "helmet", "shield", "sword", "army", "invader", "invasion", "battle"},
}

DROP_WEIGHT_KWS = {"ingot", "tin", "ruin", "stone", "basalt", "skull", "fossil", "helmet", "anchor", "hammer", "milestone", "trench"}
PEEL_REVEAL_KWS = {"tablet", "scroll", "book", "notebook", "clipboard", "map", "paper", "journal", "tag", "badge", "channel"}
SWING_STRIKE_KWS = {"sword", "blade", "spear", "flint", "warship", "prow", "ship", "shield", "bolt", "lightning", "torch", "flame", "fire"}
BLOOM_FOCUS_KWS = {"dna", "atom", "planet", "clock", "alarm", "bulb", "lightbulb", "coin", "gold", "grain", "wheat", "thermometer", "count"}

CAUSAL_LINE_KWS = ("because", "so", "therefore", "caused", "triggered", "led to", "halted", "turned into", "killed", "starved", "without", "broke")

LAZY_ADJECTIVE_SOUP = (
    "cinematic", "masterpiece", "stunning", "epic", "breathtaking",
    "ultra-detailed", "hyperdetailed", "hyper-realistic", "photorealistic", "8k", "award-winning"
)

CAMERA_MOVE_CYCLE = ("push_in", "pan_left", "pull_back", "pan_right")


def _estimate_word_timings_from_lines(lines_rows):
    """Estimates word & line timings (~2.5 words/sec + gap) for Pre-Spend Gate 0 & legacy projects without WORDS.tsv."""
    words_est = []
    cur_t = 0.0
    for r in lines_rows:
        lid = (r.get("id") or r.get("line") or "").strip()
        txt = (r.get("text") or "").strip()
        try:
            gap = max(0.15, float(r.get("gap") or 0.30))
        except Exception:
            gap = 0.30
        toks = txt.split()
        if not lid or not toks:
            continue
        is_non_ascii = any(ord(ch) > 127 for ch in txt)
        wps = 2.0 if is_non_ascii else 2.5
        dur = max(0.9, len(toks) / wps)
        step = dur / len(toks)
        for i_w, w in enumerate(toks):
            st = round(cur_t + i_w * step, 3)
            en = round(st + step, 3)
            words_est.append({"line": lid, "i": str(i_w), "start": str(st), "end": str(en), "word": w})
        cur_t += dur + gap
    return words_est


def _classify_shot_size_angle(img_tok, shot_prompt, extra_tok):
    base = os.path.splitext(os.path.basename(str(img_tok or "")))[0].split(":")[0].lower()
    if base.startswith(("card", "card_")):
        return "CARD", "flat", {"fg": "none", "mg": "hero_typography", "bg": "textured_paper"}
    if base.startswith(("split", "split_")):
        return "SPLIT", "flat", {"fg": "verdict_badges", "mg": "dual_stickers", "bg": "dual_tint_canvas"}
    if base.startswith(("bar_", "stat_", "timeline")):
        return "DATA", "flat", {"fg": "accent_sticker", "mg": "data_bars", "bg": "textured_paper"}
    txt = f"{shot_prompt} {extra_tok}".lower()
    if any(k in txt for k in ("extreme close", "ecu", "macro", "pupil", "eye detail")):
        size = "ECU"
    elif any(k in txt for k in ("close-up", "closeup", "tight", "display case", "clay seal", "excited face", "window", "detail", "hands", "tablet")):
        size = "CU"
    elif any(k in txt for k in ("leaning", "staring", "watches", "holding", "pointing", "curious face", "amazed faces", "scrapes")):
        size = "MCU"
    elif any(k in txt for k in ("line-up", "panoramic", "aerial", "continent", "map of", "pacific ocean", "starry sky", "horizon")):
        size = "EWS"
    elif any(k in txt for k in ("wide", "river bank", "wide river", "wide calm sea", "deck of a big", "bridge over", "coastline", "harbor", "cityscape", "palace", "courtyard", "billowing", "sunset", "open")):
        size = "WS"
    else:
        size = "MS"

    if any(k in txt for k in ("overhead", "top-down", "looking down", "bird", "map of", "from above")):
        angle = "overhead"
    elif any(k in txt for k in ("looking up", "towering", "looming", "low-angle", "giant", "at the stars")):
        angle = "low-angle"
    elif any(k in txt for k in ("high-angle", "from the hills", "overlooking", "coastline of another", "below")):
        angle = "high-angle"
    elif any(k in txt for k in ("across", "distant", "side", "profile", "behind", "two cavemen", "paddling", "several cut")):
        angle = "three-quarter"
    else:
        angle = "eye-level"

    fg_mg_bg = {
        "fg": "ground_shore_or_prop" if size in ("WS", "EWS") else "primary_subject",
        "mg": "stickman_action",
        "bg": "sky_and_environment",
    }
    return size, angle, fg_mg_bg


def _build_cast_anchors(shots_rows):
    """Creates immutable 20-35 word verbatim cast descriptions per recurring ref character in SHOTS.tsv."""
    anchors = {}
    first_prompt = {}
    counts = {}
    for sh in shots_rows:
        ref = (sh.get("ref") or "").strip()
        if not ref or ref in ("-", "sheet", "none"):
            continue
        counts[ref] = counts.get(ref, 0) + 1
        if ref not in first_prompt:
            first_prompt[ref] = (sh.get("prompt") or "").strip()
    for ref, cnt in counts.items():
        if cnt < 1:
            continue
        p0 = first_prompt.get(ref, "")
        ref_clean = ref.replace("_", " ")
        anchor = (
            f"Recurring 2D stickman character '{ref_clean}': clean round white ball head, simple dot eyes, "
            f"expressive ink mouth, thin black stick limbs, thick dark outlines, flat cartoon colors consistent across all scenes."
        )
        if "caveman" in ref.lower() or "ancient" in p0.lower():
            anchor = (
                f"Recurring 2D caveman stickman '{ref_clean}': round white ball head, simple dot eyes, messy dark tuft, "
                f"tattered tan fur tunic, thin black stick limbs, thick clean ink outlines across every shot."
            )
        words_a = anchor.split()
        anchors[ref] = " ".join(words_a[:35])
    return anchors


def _extract_thesis_terms_facts(lines_rows, scene_rows, project_dir):
    meta_p = os.path.join(project_dir, "METADATA.json")
    thesis = ""
    if os.path.exists(meta_p):
        try:
            md = json.load(open(meta_p, encoding="utf-8"))
            thesis = (md.get("hook") or md.get("title") or md.get("description") or "").split(".")[0].strip()
        except Exception:
            pass
    if not thesis and lines_rows:
        first_txt = (lines_rows[0].get("text") or "").strip()
        twist_cand = next(((r.get("text") or "").strip() for r in lines_rows if any(k in (r.get("text") or "").lower() for k in ("actually", "turns out", "real reason", "but", "truth"))), "")
        thesis = f"{first_txt} {twist_cand}".strip()[:180]

    vo_corpus = " ".join((r.get("text") or "") for r in lines_rows)
    vo_toks = _tok(vo_corpus)
    vis_corpus = " ".join(f"{r.get('img','')} {r.get('text','')}" for r in scene_rows)
    vis_toks = _tok(vis_corpus)
    shared = sorted(list((vo_toks & vis_toks) or vo_toks))[:12]

    facts = []
    for r in scene_rows:
        c = (r.get("cue") or "").strip()
        im = (r.get("img") or "").strip()
        tx = (r.get("text") or "").strip()
        if tx and (im.startswith(("card", "split", "bar_", "stat_", "timeline")) or re.search(r"\d", tx)):
            facts.append({"cue": c, "claim": tx, "provenance": "script_card"})
    for ln in lines_rows:
        tx = (ln.get("text") or "").strip()
        if re.search(r"\b\d{2,4}\b|\bpercent\b|\bmillion\b", tx.lower()) and len(facts) < 12:
            facts.append({"cue": f"@{ln.get('id','')}", "claim": tx[:110], "provenance": "script_narration"})
    return thesis, shared, facts[:12]


def _tok(txt):
    raw = [w.strip("_") for w in re.split(r"[^a-z0-9]+", str(txt or "").lower()) if len(w.strip("_")) >= 2]
    out = set()
    for w in raw:
        if w in STOP_TOKENS:
            continue
        out.add(w)
        if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
            out.add(w[:-1])
    return out


def _expand(toks):
    exp = set(toks)
    for t in list(toks):
        for root, syms in SEMANTIC_ROOTS.items():
            if t == root or t in syms:
                exp.add(root)
                exp.update(syms)
    return exp


def _load_tsv_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _resolve_cue_time(cue_raw, words_list, words_map, default_t=0.0):
    c = str(cue_raw or "").strip().lstrip("+")
    if c in words_map:
        return words_map[c]
    try:
        return float(c.lstrip("@").replace(":", "."))
    except ValueError:
        pass
    if ":" in c:
        ln, _, kw = c.partition(":")
        ln = ln.lstrip("@").strip()
        kw_l = kw.strip().lower()
        cands = [w for w in words_list if w.get("line") == ln]
        for w in cands:
            wt = w.get("word", "").lower().strip('.,!?":;')
            if wt == kw_l or (len(kw_l) >= 3 and (kw_l in wt or wt in kw_l)):
                return max(0.0, float(w["start"]))
        if cands:
            return max(0.0, float(cands[0]["start"]))
    elif c.startswith("@"):
        ln = c[1:].strip()
        for w in words_list:
            wl = (w.get("line") or "").strip()
            if wl == ln or wl.zfill(2) == ln.zfill(2):
                return max(0.0, float(w["start"]))
    return max(0.0, float(default_t))


def _classify_shot_scale(img_tok, shot_prompt, extra_tok):
    base = os.path.splitext(os.path.basename(str(img_tok or "")))[0].split(":")[0].lower()
    if base.startswith(("card", "card_")):
        return "EDITORIAL_CARD"
    if base.startswith(("split", "split_")):
        return "SPLIT_COMPARE"
    if base.startswith(("bar_", "stat_", "timeline")):
        return "DATA_GRAPHIC"
    txt = f"{shot_prompt} {extra_tok}".lower()
    if any(k in txt for k in ("close-up", "closeup", "tight", "macro", "detail", "face", "hands", "eyes", "zoom_in")):
        return "TIGHT"
    if any(k in txt for k in ("wide", "panoramic", "aerial", "harbor", "cityscape", "establishing", "landscape", "panorama")):
        return "WIDE"
    return "MEDIUM"


def _pick_motion_archetype(sticker_img, slot_side="right", pos_hint=""):
    s = os.path.splitext(os.path.basename(str(sticker_img or "")))[0].lower()
    toks = _tok(s)
    if s in ("stamp_x", "stamp_check", "stamp_false", "stamp_true", "stamp_myth", "count", "tag"):
        return "bloom_focus", "pop_bubble"
    if toks & DROP_WEIGHT_KWS:
        return "drop_weight", "heavy_thud"
    if toks & PEEL_REVEAL_KWS:
        return "peel_reveal", "paper_slide"
    if toks & SWING_STRIKE_KWS:
        return "swing_strike", "whoosh_strike"
    if toks & BLOOM_FOCUS_KWS:
        return "bloom_focus", "pop_bubble"
    hint = str(pos_hint or "").lower()
    if "left" in hint or slot_side == "left":
        return "slide_arc_left", "micro_whoosh"
    return "slide_arc_right", "micro_whoosh"


def _find_best_word_in_window(words_list, t0, t1, sticker_img, sticker_desc, used_times):
    """Finds exact spoken trigger word timestamp in WORDS.tsv inside [t0 - 0.15, t1]."""
    slug = os.path.splitext(os.path.basename(str(sticker_img or "")))[0]
    stk_toks = _expand(_tok(f"{slug} {sticker_desc}"))
    if not stk_toks or not words_list:
        return None, None

    win_words = [w for w in words_list if (t0 - 0.15) <= float(w.get("start", 0.0)) <= max(t0 + 0.5, t1)]
    if not win_words:
        return None, None

    best_w = None
    best_score = 0
    for w in win_words:
        wt_raw = w.get("word", "").lower().strip('.,!?":;')
        if not wt_raw:
            continue
        w_toks = _expand(_tok(wt_raw))
        overlap = len(stk_toks & w_toks)
        direct = len(_tok(f"{slug} {sticker_desc}") & _tok(wt_raw))
        score = direct * 3 + overlap
        if score > best_score:
            best_score = score
            best_w = w

    if best_w and best_score > 0:
        t_hit = max(0.0, float(best_w["start"]))
        # Ensure distinct items in same list don't pile onto exact identical timestamp
        while any(abs(t_hit - ut) < 0.08 for ut in used_times):
            t_hit += 0.12
        return round(t_hit, 3), best_w.get("word", "")
    return None, None


def _infer_shot_function(idx, total_scenes, spoken_text, img_tok):
    norm = idx / max(1, total_scenes - 1)
    txt = spoken_text.lower()
    if idx == 0 or norm <= 0.12:
        return "hook"
    if norm >= 0.88 or any(k in txt for k in ("subscribe", "watch the full", "link below", "comment")):
        return "cta"
    if 0.65 <= norm <= 0.88 and any(k in txt for k in ("turns out", "actually", "truth", "real reason", "surprise", "discovered")):
        return "twist"
    if str(img_tok).startswith(("card", "split", "bar_", "stat_", "timeline")):
        return "evidence"
    if norm >= 0.80:
        return "payoff"
    if norm >= 0.45:
        return "escalation"
    return "setup"


def supervise_project(project_dir=".", pre_spend=False):
    """Runs Unified Director Supervision (Gate 0 + Choreography) & writes DIRECTOR_PLAN.json."""
    scenes_path = os.path.join(project_dir, "SCENES_HYBRID.tsv")
    if not os.path.exists(scenes_path):
        scenes_path = os.path.join(project_dir, "SCENES.tsv")
    if not os.path.exists(scenes_path):
        return None

    words_rows = _load_tsv_rows(os.path.join(project_dir, "WORDS.tsv"))
    lines_rows = _load_tsv_rows(os.path.join(project_dir, "LINES.tsv"))
    shots_rows = _load_tsv_rows(os.path.join(project_dir, "SHOTS.tsv"))
    elements_rows = _load_tsv_rows(os.path.join(project_dir, "ELEMENTS.tsv"))

    used_estimated_timing = False
    if not words_rows and lines_rows:
        words_rows = _estimate_word_timings_from_lines(lines_rows)
        used_estimated_timing = True

    words_map = {}
    max_word_t = 0.0
    for w in words_rows:
        try:
            st = max(0.0, float(w.get("start", 0.0)))
            en = max(st, float(w.get("end", st)))
            max_word_t = max(max_word_t, en)
            ln = (w.get("line") or "").strip()
            wi = str(w.get("i", "")).strip()
            if ln and wi != "":
                for lk in {ln, ln.zfill(2), ln.lstrip("0") or "0"}:
                    words_map[f"{lk}.{wi}"] = st
            elif w.get("cue"):
                words_map[w["cue"]] = st
            if ln:
                for lk in {ln, ln.zfill(2), ln.lstrip("0") or "0"}:
                    if f"@{lk}" not in words_map:
                        words_map[f"@{lk}"] = st
                        words_map[lk] = st
        except Exception:
            pass

    shots_prompt_map = {}
    for sh in shots_rows:
        sid = (sh.get("id") or sh.get("shot") or "").strip()
        pr = (sh.get("prompt") or sh.get("desc") or "").strip()
        if sid:
            num_core = sid.lstrip("s").lstrip("0") or "0"
            variants = {
                sid,
                os.path.splitext(os.path.basename(sid))[0],
                f"s{sid}",
                f"s{num_core.zfill(2)}",
                f"shot_{sid}",
                f"shot_{num_core.zfill(2)}",
                num_core,
                num_core.zfill(2),
            }
            for vk in variants:
                shots_prompt_map[vk] = pr

    el_desc_map = {}
    for el in elements_rows:
        eid = (el.get("id") or "").strip()
        obj = (el.get("object") or "").strip()
        if eid:
            el_desc_map[eid] = obj

    lines_text_by_id = {}
    for ln in lines_rows:
        lid = (ln.get("id") or ln.get("line") or "").strip()
        txt = (ln.get("text") or "").strip()
        if lid:
            lines_text_by_id[lid] = txt

    scene_rows = _load_tsv_rows(scenes_path)

    # Parse scenes & attached overlays
    scenes = []
    cur_sc = None
    for idx, r in enumerate(scene_rows):
        cue = (r.get("cue") or "").strip()
        if not cue or cue.startswith("#"):
            continue
        if cue.startswith("+"):
            t_raw = _resolve_cue_time(cue, words_rows, words_map, cur_sc["t0"] if cur_sc else 0.0)
            if cur_sc is not None:
                cur_sc["overlays"].append({
                    "row_idx": idx + 2,
                    "cue": cue,
                    "raw_t": t_raw,
                    "img": (r.get("img") or "").strip(),
                    "text": (r.get("text") or "").strip(),
                    "pos": (r.get("pos") or "").strip(),
                    "extra": (r.get("extra") or "").strip(),
                })
        else:
            t_raw = _resolve_cue_time(cue, words_rows, words_map, 0.0)
            cur_sc = {
                "scene_idx": len(scenes),
                "cue": cue,
                "t0": t_raw,
                "t1": t_raw + 3.5,
                "img": (r.get("img") or "").strip(),
                "text": (r.get("text") or "").strip(),
                "extra": (r.get("extra") or "").strip(),
                "overlays": [],
            }
            scenes.append(cur_sc)

    for i in range(len(scenes)):
        if i + 1 < len(scenes):
            scenes[i]["t1"] = max(scenes[i]["t0"] + 0.5, scenes[i + 1]["t0"])
        else:
            scenes[i]["t1"] = max(scenes[i]["t0"] + 3.5, max_word_t or (scenes[i]["t0"] + 3.5))

    approved_count = 0
    rejected_count = 0
    flagged_count = 0
    continuity_warnings = []
    audit_flags = []
    scale_sequence = []
    director_scenes = []
    prev_cam_move = None

    thesis, key_terms, facts_list = _extract_thesis_terms_facts(lines_rows, scene_rows, project_dir)
    cast_anchors = _build_cast_anchors(shots_rows)

    for sc in scenes:
        t0, t1 = sc["t0"], sc["t1"]
        hold_sec = round(max(0.1, t1 - t0), 3)
        shot_base = os.path.splitext(os.path.basename(sc["img"]))[0].split(":")[0]
        shot_prompt = shots_prompt_map.get(shot_base, shots_prompt_map.get(sc["img"], ""))
        is_editorial_card = shot_base.startswith(("card", "split", "bar_", "stat_", "timeline"))

        # Collect spoken words & matching line text in [t0-0.5, t1+0.5]
        spoken_words = [w for w in words_rows if (t0 - 0.5) <= float(w.get("start", 0.0)) <= (t1 + 0.5)]
        line_ids = {w.get("line") for w in spoken_words if w.get("line")}
        spoken_text = " ".join([lines_text_by_id.get(lid, "") for lid in sorted(line_ids)] + [w.get("word", "") for w in spoken_words])

        scale = _classify_shot_scale(sc["img"], shot_prompt, sc["extra"])
        shot_size, shot_angle, fg_mg_bg = _classify_shot_size_angle(sc["img"], shot_prompt, sc["extra"])
        shot_func = _infer_shot_function(sc["scene_idx"], len(scenes), spoken_text, sc["img"])
        scale_sequence.append({"cue": sc["cue"], "t0": round(t0, 2), "scale": scale, "size": shot_size, "angle": shot_angle, "hold": hold_sec, "is_card": is_editorial_card})

        # Unmotivated intense VFX warning on calm narration
        ext_l = sc["extra"].lower()
        if any(k in ext_l for k in ("shake", "danger", "blood", "bw")):
            crisis_hits = any(k in spoken_text.lower() for k in (
                "collapse", "dead", "die", "starv", "burn", "ash", "war", "attack", "invad",
                "freeze", "ice", "myth", "false", "wrong", "trap", "crisis", "destroyed", "fatal"
            ))
            if spoken_text.strip() and not crisis_hits:
                continuity_warnings.append(f"Unmotivated intense VFX '{sc['extra']}' on calm scene {sc['cue']}")

        # Assign adjacent non-repeating camera_move (always static on cards/splits/diagrams)
        explicit_cam = next((c for c in ("static", "push_in", "pull_back", "pan_left", "pan_right", "zoom_in_tight") if c in ext_l), None)
        if is_editorial_card or shot_size == "DATA" or "diagram" in shot_prompt.lower() or "chart" in shot_prompt.lower():
            cam_move = "static"
        elif explicit_cam and explicit_cam != prev_cam_move:
            cam_move = explicit_cam
        elif sc["scene_idx"] % 3 == 1 and prev_cam_move != "static":
            cam_move = "static"
        else:
            cands = [m for m in CAMERA_MOVE_CYCLE if m != prev_cam_move]
            cam_move = cands[sc["scene_idx"] % len(cands)]
        prev_cam_move = cam_move

        # Reads-Formula Hold Floor check on text-bearing programmatic cards/splits/timelines
        card_words = len([w for w in re.split(r"\s+", sc["text"].replace("|", " ").strip()) if w])
        reads_min_sec = round(max(1.8, 1.0 + 0.3 * card_words), 2) if (is_editorial_card and card_words > 0) else 0.0
        slack = 0.65 if used_estimated_timing else 0.08
        if is_editorial_card and card_words > 0 and hold_sec + slack < reads_min_sec:
            msg = f"F_READ_TOO_FAST: {sc['cue']} ({shot_base}, {card_words}w) held {hold_sec:.2f}s < reads floor {reads_min_sec:.2f}s"
            continuity_warnings.append(msg)
            audit_flags.append({"code": "F_READ_TOO_FAST", "cue": sc["cue"], "penalty": 8, "msg": msg})

        n_ov = len(sc["overlays"])
        # Determine Group Choreography Pattern
        if n_ov <= 1:
            group_pattern = "solo_focus"
        elif n_ov == 2:
            has_causal_cue = ("cause_effect" in ext_l or any("cause_effect" in o["extra"].lower() for o in sc["overlays"]))
            has_causal_text = any(ck in spoken_text.lower() for ck in CAUSAL_LINE_KWS)
            group_pattern = "cause_effect" if (has_causal_cue or (not is_editorial_card and has_causal_text and len(sc["overlays"]) == 2)) else "duo_converge"
        elif n_ov == 3:
            group_pattern = "trio_cascade"
        else:
            group_pattern = "quad_showcase"

        used_word_times = []
        directed_ovs = []
        shot_primary_toks = _tok(shot_prompt)
        spoken_exp = _expand(_tok(f"{spoken_text} {sc['text']}"))

        for k_idx, ov in enumerate(sc["overlays"]):
            stk_base = os.path.splitext(os.path.basename(ov["img"]))[0]
            stk_desc = el_desc_map.get(stk_base, ov.get("text", "") or stk_base.replace("_", " "))
            stk_raw_toks = _tok(f"{stk_base} {stk_desc}")
            stk_exp_toks = _expand(stk_raw_toks)

            # 1. Logical Relevance Audit
            status = "APPROVED"
            reason = "Aligned with spoken concept and distinct from background shot"
            is_special = stk_base in ("stamp_x", "stamp_check", "stamp_false", "stamp_true", "stamp_myth", "count", "tag") or ov["img"].startswith("bars:")

            if not is_special and not is_editorial_card and shot_primary_toks:
                # Auto-reject redundant sticker if background shot's focal prompt already centers the identical prop
                direct_dup = len(stk_raw_toks & shot_primary_toks)
                if direct_dup >= 2 or (len(stk_raw_toks) == 1 and direct_dup == 1):
                    status = "REJECTED_REDUNDANT"
                    reason = f"Redundant with scene shot '{sc['img']}': shot already illustrates {sorted(stk_raw_toks & shot_primary_toks)}"

            if status == "APPROVED" and not is_special and spoken_exp:
                rel_hits = len(stk_exp_toks & spoken_exp)
                if rel_hits == 0 and not is_editorial_card:
                    status = "FLAGGED_OFFTOPIC"
                    reason = f"No keyword/semantic overlap with spoken clause '{spoken_text[:70].strip()}'"

            if status == "APPROVED":
                approved_count += 1
            elif status == "REJECTED_REDUNDANT":
                rejected_count += 1
            else:
                flagged_count += 1

            # 2. Exact Spoken Word Time-Sync Lock (-0.06s visual anticipation)
            hit_t, hit_word = _find_best_word_in_window(words_rows, t0, t1, ov["img"], stk_desc, used_word_times)
            if hit_t is not None:
                used_word_times.append(hit_t)
                sync_t = max(t0, round(hit_t - 0.06, 3))
            else:
                base_t = ov["raw_t"] if (t0 - 0.05 <= ov["raw_t"] < t1) else t0
                while any(abs(base_t - ut) < 0.10 for ut in used_word_times):
                    base_t = min(t1 - 0.6, base_t + 0.12)
                used_word_times.append(base_t)
                sync_t = max(0.0, round(base_t - 0.06 if base_t > t0 + 0.10 else base_t, 3))

            # 3. Motion Archetype, Resting Angle & Group Choreography Role
            slot_side = "left" if (k_idx % 2 == 0) else "right"
            motion_arch, sfx_kind = _pick_motion_archetype(ov["img"], slot_side=slot_side, pos_hint=ov["pos"])
            if group_pattern == "duo_converge":
                rest_tilt = -3.4 if k_idx == 0 else 3.4
                if motion_arch in ("slide_arc_left", "slide_arc_right", "bloom_focus"):
                    motion_arch = "slide_arc_left" if k_idx == 0 else "slide_arc_right"
            elif group_pattern == "cause_effect":
                rest_tilt = -2.2 if k_idx == 0 else 2.2
            elif group_pattern == "trio_cascade":
                rest_tilt = (-3.0, 0.0, 3.0)[k_idx % 3]
            elif group_pattern == "quad_showcase":
                rest_tilt = (-2.6, 2.6, -2.2, 2.2)[k_idx % 4]
            else:
                rest_tilt = (-2.0, 1.8)[k_idx % 2]

            directed_ovs.append({
                "idx": k_idx,
                "row_idx": ov["row_idx"],
                "cue": ov["cue"],
                "img": ov["img"],
                "status": status,
                "reason": reason,
                "trigger_word": hit_word,
                "sync_t": sync_t,
                "motion_archetype": motion_arch,
                "sfx_kind": sfx_kind,
                "rest_tilt_deg": rest_tilt,
                "arrow_to_next": (group_pattern == "cause_effect" and k_idx == 0),
                "idle_breath": True,
                "exit_ease_sec": 0.22,
            })

        director_scenes.append({
            "scene_idx": sc["scene_idx"],
            "cue": sc["cue"],
            "img": sc["img"],
            "t0": round(t0, 3),
            "t1": round(t1, 3),
            "hold_sec": hold_sec,
            "reads_min_sec": reads_min_sec,
            "shot_scale": scale,
            "shot_size": shot_size,
            "shot_function": shot_func,
            "angle": shot_angle,
            "fg_mg_bg": fg_mg_bg,
            "camera_move": cam_move,
            "group_pattern": group_pattern,
            "spoken_preview": spoken_text[:120].strip(),
            "overlays": directed_ovs,
        })

    # Continuity checks across hero shots:
    # 1. 2-Rung Shot-Size / 30deg Angle Alternation Rule (flag directly adjacent hero shots sharing IDENTICAL size AND angle)
    for i in range(1, len(scale_sequence)):
        prev_s, cur_s = scale_sequence[i - 1], scale_sequence[i]
        if not prev_s["is_card"] and not cur_s["is_card"]:
            if prev_s["size"] == cur_s["size"] and prev_s["angle"] == cur_s["angle"]:
                msg = f"Shot-size/angle repeat: {prev_s['cue']} -> {cur_s['cue']} both ({cur_s['size']}, {cur_s['angle']}); vary size by 2 rungs or shift >=30deg angle"
                continuity_warnings.append(msg)
                audit_flags.append({"code": "SHOT_REPEAT", "cue": cur_s["cue"], "penalty": 5, "msg": msg})

    # 2. Anti-Metronome Right-Skewed Pacing Variance: flag 3+ consecutive hero cuts within 0.25s of identical duration
    hero_seq = [s for s in scale_sequence if not s["is_card"]]
    for i in range(2, len(hero_seq)):
        d_win = [hero_seq[i - 2]["hold"], hero_seq[i - 1]["hold"], hero_seq[i]["hold"]]
        if max(d_win) - min(d_win) <= 0.25 and max(d_win) >= 1.5:
            msg = f"F_METRONOME: 3 consecutive identical holds ({d_win[0]:.2f}s..{d_win[2]:.2f}s) ending at {hero_seq[i]['cue']}"
            continuity_warnings.append(msg)
            audit_flags.append({"code": "F_METRONOME", "cue": hero_seq[i]["cue"], "penalty": 10, "msg": msg})
            break

    # 3. Lazy Adjective Soup Hygiene Audit on SHOTS.tsv prompts
    soup_hits = []
    for sh in shots_rows:
        pr_l = (sh.get("prompt") or "").lower()
        bad_words = [bw for bw in LAZY_ADJECTIVE_SOUP if re.search(rf"\b{re.escape(bw)}\b", pr_l)]
        if bad_words:
            sid = (sh.get("id") or "?").strip()
            msg = f"Lazy adjective soup in shot '{sid}': {', '.join(bad_words)}"
            continuity_warnings.append(msg)
            audit_flags.append({"code": "ADJECTIVE_SOUP", "cue": sid, "penalty": 6, "msg": msg})
            soup_hits.append(sid)

    if rejected_count > 0:
        audit_flags.append({"code": "REDUNDANT_STICKER", "cue": "-", "penalty": min(24, rejected_count * 6),
                            "msg": f"{rejected_count} REJECTED_REDUNDANT sticker(s)"})

    total_penalty = (
        min(24, sum(f["penalty"] for f in audit_flags if f["code"] == "F_READ_TOO_FAST"))
        + min(28, sum(f["penalty"] for f in audit_flags if f["code"] == "SHOT_REPEAT"))
        + min(15, sum(f["penalty"] for f in audit_flags if f["code"] == "F_METRONOME"))
        + min(24, sum(f["penalty"] for f in audit_flags if f["code"] == "ADJECTIVE_SOUP"))
        + sum(f["penalty"] for f in audit_flags if f["code"] == "REDUNDANT_STICKER")
    )
    audit_score = max(0, 100 - total_penalty)

    plan = {
        "version": "1.1.0",
        "project_dir": os.path.abspath(project_dir),
        "pre_spend_mode": bool(pre_spend or used_estimated_timing),
        "audit_score": audit_score,
        "thesis": thesis,
        "terms": key_terms,
        "cast_anchors": cast_anchors,
        "facts": facts_list,
        "summary": {
            "total_scenes": len(director_scenes),
            "approved_stickers": approved_count,
            "rejected_redundant_stickers": rejected_count,
            "flagged_offtopic_stickers": flagged_count,
            "continuity_warnings": len(continuity_warnings),
            "audit_score": audit_score,
            "scale_variety": sorted(list({s["scale"] for s in scale_sequence})),
            "shot_size_variety": sorted(list({s["size"] for s in scale_sequence})),
        },
        "audit_breakdown": audit_flags,
        "continuity_warnings": continuity_warnings,
        "scenes": director_scenes,
    }

    out_path = os.path.join(project_dir, "DIRECTOR_PLAN.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    return plan


def main():
    parser = argparse.ArgumentParser(description="Unified Director Supervisor: Gate 0, Continuity, Word-Sync & Motion Choreography")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory")
    parser.add_argument("--pre-spend", action="store_true", help="Run Pre-Spend Gate 0 audit (estimates timings if WORDS.tsv pending)")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if rejected redundant stickers remain or audit_score < 70")
    parser.add_argument("--warn-only", action="store_true", help="Never fail exit code; emit warnings cleanly")
    args = parser.parse_args()

    plan = supervise_project(args.project_dir, pre_spend=args.pre_spend)
    if not plan:
        print(f"⚠️ No scene manifest found in {args.project_dir}")
        sys.exit(0 if args.warn_only else 1)

    sm = plan["summary"]
    print(f"🎬 DIRECTOR_PLAN.json generated for {args.project_dir} (score={plan['audit_score']}/100{' [pre-spend]' if plan['pre_spend_mode'] else ''}):")
    print(f"   • Scenes: {sm['total_scenes']} | Scale Variety: {sm['scale_variety']} | Sizes: {sm['shot_size_variety']}")
    print(f"   • Stickers: {sm['approved_stickers']} APPROVED | {sm['rejected_redundant_stickers']} REJECTED_REDUNDANT | {sm['flagged_offtopic_stickers']} FLAGGED_OFFTOPIC")
    print(f"   • Continuity Warnings: {sm['continuity_warnings']}")
    if plan["continuity_warnings"]:
        for cw in plan["continuity_warnings"][:5]:
            print(f"     ⚠️ {cw}")
    if args.strict and not args.warn_only and (sm["rejected_redundant_stickers"] > 0 or plan["audit_score"] < 70):
        sys.exit(2)


if __name__ == "__main__":
    main()
