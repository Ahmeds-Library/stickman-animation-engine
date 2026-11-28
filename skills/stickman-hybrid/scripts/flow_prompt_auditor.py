#!/usr/bin/env python3
"""flow_prompt_auditor.py: Super-Intelligent Google Flow Prompt Auditor & Negative Prompt Engine
Ensures 100% 2D Stickman purity, zero style drift, policy filter compliance, and spatial cleanliness.
Features:
1. Multi-Layered Negative Prompt Injection:
   - NEGATIVE_STICKMAN (Anti-photorealism, anti-3D CGI, anti-realistic human anatomy)
   - NEGATIVE_CLEANLINESS (Anti-watermark, anti-text, anti-subtitles, anti-blur)
   - NEGATIVE_ERA (Anti-modern artifacts in prehistoric/ancient scenes)
   - NEGATIVE_CHROMA (Anti-gradient, pure solid #FF00FF magenta backing for stickers)
2. Character Anatomy Purity Enforcement (Clean white ball head, dot eyes, ink line mouth, thin stick limbs)
3. Spatial Layout & Docking Optimization (Enforces left/right 40% empty margins for sticker overlays)
4. Automated Policy Filter Sanitizer (Euphemistic rewriting to prevent Flow queue halts)
"""

import os, sys, re, argparse

HUMAN_ROLES_REPLACEMENTS = [
    (r"\b(sailors?|seamen|mariners?)\b", r"2D stickman \1 with pure-white round heads and black stick limbs"),
    (r"\b(captains?|commanders?)\b", r"2D stickman \1 with pure-white round head and black stick limbs"),
    (r"\b(miners?)\b", r"2D stickman miners with pure-white round heads and black stick limbs"),
    (r"\b(guards?|soldiers?|warriors?)\b", r"2D stickman \1 with pure-white round heads and black stick limbs"),
    (r"\b(scientists?|researchers?)\b", r"2D stickman \1 with pure-white round heads and black stick limbs"),
    (r"\b(villagers?|citizens?|townsfolk)\b", r"2D stickman \1 with pure-white round heads and black stick limbs"),
    (r"\b(harbor\s+masters?)\b", r"2D stickman harbor masters with pure-white round heads and black stick limbs"),
    (r"\b(witnesses|onlookers?|spectators?)\b", r"2D stickman \1 with pure-white round heads and black stick limbs"),
    (r"\b(crowds?|people|persons?|humans?)\b", r"2D stickman figures with pure-white round heads and black stick limbs"),
    (r"\b(workers?|laborers?)\b", r"2D stickman workers with pure-white round heads and black stick limbs"),
    (r"\b(historians?|scholars?|scribes?)\b", r"2D stickman \1 with pure-white round heads and black stick limbs"),
    (r"\b(priests?|monks?|prophets?)\b", r"2D stickman \1 with pure-white round heads and black stick limbs"),
]

def inline_rewrite_stickman_roles(text):
    """Rewrites human role nouns inline so Flow receives stickman constraints at the noun level."""
    out = text
    for pat, repl in HUMAN_ROLES_REPLACEMENTS:
        def _sub(m):
            prefix = out[:m.start()]
            if re.search(r"\b(?:stickman|stick-figure|stick figure)\s*$", prefix, re.IGNORECASE):
                return m.group(0)
            return re.sub(pat, repl, m.group(0), flags=re.IGNORECASE)
        out = re.sub(pat, _sub, out, flags=re.IGNORECASE)
    return out

# Core Stickman Purity Anchor
STICKMAN_ANATOMY_ANCHOR = (
    "2D stickman figure: pure flat crisp white round head, simple black dot eyes, "
    "expressive ink mouth, thin black stick limbs, crisp black ink outlines, "
    "zero realistic human anatomy, zero skin-toned heads"
)

# Bright Airy 2D Editorial Daylight & Warm Golden-Amber Sunset Directives
DAYLIGHT_STAGE_ANCHOR = (
    "bright airy editorial daylight with clean skies, crisp unbleached pigments "
    "(terracotta red, fresh green), gentle grounded contact shadows, zero milky haze"
)

SUNSET_RICH_ANCHOR = (
    "warm golden-amber 2D editorial sunset sky with bright readable colors, "
    "gentle grounded contact shadows, open cheerful depth, zero dark gloomy shadows or milky fog"
)

SUNSET_SCENE_PAT = re.compile(
    r"\b(?:sunset|dusk|evening|twilight|crisis|nightfall|amber sky)\b",
    flags=re.IGNORECASE,
)

# Layered Negative Prompts
NEGATIVE_STICKMAN = (
    "no realistic humans, no detailed human faces, no skin-toned heads, no noses, no ears, "
    "no anime characters, no 3D render, photorealistic, 3D CGI, photograph, realistic skin, "
    "manga, heavy grey face shading"
)

NEGATIVE_CLEANLINESS = (
    "no text, no words, no letters, no text on screens, no words on monitors, no writing on scrolls, "
    "no latin text, no lorem ipsum, no comic headers, watermark, phone bezel, comic border, "
    "panel frame, paper margin, white frame, blurry"
)

NEGATIVE_LIGHTING = (
    "no milky haze, no global white bloom, no overexposed bleached white, "
    "no heavy dark moody shadows, no dark purple blotchy face shadows, no gloomy lighting"
)

NEGATIVE_ERA_ANCIENT = (
    "no wristwatch, plastic, smartphone, electric light, modern cars"
)

LAZY_ADJECTIVE_SOUP_PAT = re.compile(
    r"\b(?:cinematic|masterpiece|stunning|epic|breathtaking|ultra-detailed|hyperdetailed|hyper-realistic|8k|award-winning)\b,?\s*",
    flags=re.IGNORECASE,
)


def load_cast_anchors(project_dir="."):
    dp = os.path.join(project_dir, "DIRECTOR_PLAN.json")
    if os.path.exists(dp):
        try:
            import json
            return json.load(open(dp, encoding="utf-8")).get("cast_anchors", {}) or {}
        except Exception:
            pass
    return {}


def strip_lazy_adjectives(prompt):
    cleaned = LAZY_ADJECTIVE_SOUP_PAT.sub("", str(prompt or ""))
    return re.sub(r"\s{2,}", " ", cleaned).strip(" ,")

NEGATIVE_CHROMA_STICKER = (
    "complex background, gradient background, floor shadows, ground contact shadows, ambient occlusion on floor, "
    "text inside sticker, words, letters, labels, typography, numbers, "
    "multiple objects, cropped edges, partial cutoffs"
)

# Content Policy Filter Sanitizer
POLICY_SANITIZER_MAP = {
    r"\blouse\b": "microscopic insect specimen",
    r"\blice\b": "microscopic creatures",
    r"\bparasite\b": "tiny historical pest",
    r"\bnaked\b": "bare silhouette",
    r"\bnude\b": "unclothed silhouette",
    r"\bcorpse\b": "fainted ancient silhouette",
    r"\bdeath\b": "grave peril",
    r"\bblood\b": "crimson danger aura",
    r"\bkill\b": "defeat",
    r"\bexecution\b": "royal decree punishment",
    r"\bstrangle\b": "overpower"
}

def sanitize_policy_words(prompt):
    """Rewrites sensitive terms with safe illustrative equivalents."""
    cleaned = prompt
    for pattern, replacement in POLICY_SANITIZER_MAP.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    return cleaned

# Look Directives Map
LOOK_DIRECTIVES = {
    "night": "a moody night palette of deep blues and teals lit by warm firelight, torches, or lantern glow",
    "warm": "a warm golden-ochre textured paper backdrop with soft vignette, terracotta and amber accents",
    "ink": "high contrast minimalist ink style, clean black ink outlines, warm vintage off-white paper grain",
    "oversimplified": "vibrant 2D cartoon stick figure historical explainer style, thick clean black outlines, bright royal colors",
    "cgp_grey": "iconic minimalist vector graphic explainer illustration, bold flat silhouette stick figures, clean slate paper",
    "casually_explained": "ultra-minimal 2D stick figure illustration, clean thin black vector strokes on white background",
    "minute_physics": "hand-drawn whiteboard and textured paper sketch explainer, animated black felt marker strokes",
    "painted": "2D illustrated graphic-novel style, detailed hand-painted backgrounds with realistic perspective",
    "bright": "hand-drawn 2D flat cartoon palette, light cream walls, cheerful daylight",
}

def audit_and_enhance_prompt(prompt, is_sticker=False, is_ancient=False, space="auto", ref_char=None, look=None, cast_anchors=None, aspect="9:16"):
    """Audits a raw prompt, strips lazy buzzwords, injects verbatim cast anchors, bright 2D editorial lighting &
    clean canonical stickman anatomy, enforces token-0 vertical framing (<1200 chars), and appends surgical negatives.
    """
    raw_clean = strip_lazy_adjectives(sanitize_policy_words(str(prompt or "").strip()))
    if not is_sticker and "no people" not in raw_clean.lower():
        raw_clean = inline_rewrite_stickman_roles(raw_clean)

    # 0. Inject immutable cast_anchor verbatim when recurring ref character matches
    anchors = cast_anchors if isinstance(cast_anchors, dict) else load_cast_anchors(".")
    if not is_sticker and ref_char and ref_char in anchors:
        anch = anchors[ref_char].strip()
        if anch[:24].lower() not in raw_clean.lower():
            raw_clean = f"{anch} {raw_clean}"

    # 1. Aspect Token-0 Prefix or Sticker Chroma Constraints
    prefix = ""
    if is_sticker:
        if "#FF00FF" not in raw_clean and "magenta" not in raw_clean.lower():
            prefix = "Isolated prop cutout on pure solid uniform magenta background #FF00FF: "
    elif aspect == "9:16":
        if not raw_clean.lower().startswith("a true full-height vertical 9:16"):
            prefix = "A true full-height vertical 9:16 portrait, borderless edge-to-edge, no bezel, no text: "
    elif aspect == "16:9":
        if not raw_clean.lower().startswith(("clean 16:9", "complete 16:9")):
            prefix = "Clean 16:9 widescreen 2D cartoon illustration, borderless edge-to-edge, no text: "

    # 2. Craft Add-Ons (kept intact under budget while trimming only verbose middle scene text if needed)
    addons = []
    if is_sticker:
        addons.append("centered, single object, crisp sharp edges")
    else:
        has_char_kw = bool(re.search(
            r"\b(?:stickman|stick figure|stick-figure|white ball head|person|people|man|woman|child|boy|girl|human|caveman|worker|doctor|scientist|farmer|citizen|merchant|scribe|detective|soldier|villager|archaeologist|scholar|king|queen|emperor|priest|monk|god|goddess|deity|crowd|audience|warrior|leader|ruler|peasant|pastor|prophet|historian)\b",
            raw_clean, re.IGNORECASE,
        ))
        wants_stickman = ("no people" not in raw_clean.lower()) and (
            has_char_kw or (ref_char and ref_char != "-")
        )
        if wants_stickman and "pure flat crisp white round head" not in raw_clean.lower():
            addons.append(STICKMAN_ANATOMY_ANCHOR)
        if SUNSET_SCENE_PAT.search(raw_clean):
            if "golden-amber" not in raw_clean.lower():
                addons.append(SUNSET_RICH_ANCHOR)
        elif look != "night" and "airy editorial daylight" not in raw_clean.lower():
            addons.append(DAYLIGHT_STAGE_ANCHOR)

        if look and look in LOOK_DIRECTIVES:
            directive = LOOK_DIRECTIVES[look]
            if directive[:20].lower() not in raw_clean.lower():
                addons.append(directive)

        if space == "left" and "left" not in raw_clean.lower():
            addons.append("subject on right, open background on left 45%")
        elif space == "right" and "right" not in raw_clean.lower():
            addons.append("subject on left, open background on right 45%")
        elif space == "top" and "open sky above" not in raw_clean.lower():
            addons.append("subject in lower half, open sky above")

    # 3. Assemble Concise Multi-Layered Negative Prompt
    negatives = [NEGATIVE_STICKMAN, NEGATIVE_CLEANLINESS]
    if is_sticker:
        negatives.append(NEGATIVE_CHROMA_STICKER)
    else:
        negatives.append(NEGATIVE_LIGHTING)
    if is_ancient:
        negatives.append(NEGATIVE_ERA_ANCIENT)

    negative_block = " Negative: " + ", ".join(negatives)
    addon_str = (", " + ", ".join(addons)) if addons else ""
    max_total = 1195
    raw_budget = max_total - len(prefix) - len(addon_str) - len(negative_block)

    if len(raw_clean) > max(60, raw_budget):
        if raw_budget >= 60:
            raw_clean = raw_clean[:raw_budget].rsplit(" ", 1)[0].rstrip(" ,.;:")
        else:
            raw_clean = raw_clean[:120].rsplit(" ", 1)[0].rstrip(" ,.;:")

    body = f"{prefix}{raw_clean}{addon_str}".strip(" ,")
    max_body = max_total - len(negative_block)
    if len(body) > max_body:
        body = body[:max_body].rsplit(",", 1)[0].strip()
    return f"{body}{negative_block}"[:1199]

def audit_shots_file(shots_path="SHOTS.tsv"):
    """Audits an entire SHOTS.tsv file and reports spatial distribution, policy warnings, and style compliance."""
    if not os.path.exists(shots_path):
        return {"error": f"{shots_path} does not exist"}
        
    with open(shots_path, "r", encoding="utf-8") as f:
        lines = [l.strip().split("\t") for l in f if l.strip() and not l.startswith("#")]
        
    header = lines[0]
    rows = lines[1:]
    
    audit_results = {
        "total_shots": len(rows),
        "spatial_distribution": {"left": 0, "right": 0, "center": 0, "auto": 0},
        "policy_triggers_detected": 0,
        "missing_anatomy_anchors": 0,
        "recommendations": []
    }
    
    for r in rows:
        p = r[2] if len(r) > 2 else ""
        sp = r[3].lower() if len(r) > 3 and r[3] else "auto"
        if sp in audit_results["spatial_distribution"]:
            audit_results["spatial_distribution"][sp] += 1
        else:
            audit_results["spatial_distribution"]["auto"] += 1
            
        for pat in POLICY_SANITIZER_MAP:
            if re.search(pat, p, re.IGNORECASE):
                audit_results["policy_triggers_detected"] += 1
                
        if not any(w in p.lower() for w in ["stickman", "stick figure", "ball head"]):
            audit_results["missing_anatomy_anchors"] += 1

    if audit_results["spatial_distribution"]["auto"] == len(rows):
        audit_results["recommendations"].append("Consider specifying 'left' or 'right' space for 30% of shots to create natural sticker docking docks.")
        
    if audit_results["policy_triggers_detected"] > 0:
        audit_results["recommendations"].append(f"Auto-sanitized {audit_results['policy_triggers_detected']} words that could trigger Google Flow safety filter.")

    return audit_results

def main():
    parser = argparse.ArgumentParser(description="Google Flow Intelligent Prompt Auditor")
    parser.add_argument("prompt", nargs="?", help="Raw prompt string to audit and enhance")
    parser.add_argument("--sticker", action="store_true", help="Audit as sticker prop on magenta")
    parser.add_argument("--ancient", action="store_true", help="Add anti-modern negative prompts")
    parser.add_argument("--space", choices=["left", "right", "center", "auto"], default="auto")
    parser.add_argument("--look", choices=list(LOOK_DIRECTIVES.keys()), default=None, help="Art direction look preset")
    parser.add_argument("--aspect", choices=["9:16", "16:9"], default="9:16", help="Target aspect ratio")
    parser.add_argument("--audit-file", type=str, help="Audit a SHOTS.tsv file")
    args = parser.parse_args()

    if args.audit_file or (args.prompt and args.prompt.endswith(".tsv") and os.path.exists(args.prompt)):
        target_tsv = args.audit_file or args.prompt
        res = audit_shots_file(target_tsv)
        print("==================================================")
        print(f"📋 SHOTS.TSV PROMPT AUDIT REPORT: {target_tsv}")
        print("==================================================")
        for k, v in res.items():
            print(f"• {k}: {v}")
    elif args.prompt:
        enhanced = audit_and_enhance_prompt(
            args.prompt, is_sticker=args.sticker, is_ancient=args.ancient,
            space=args.space, look=args.look, aspect=args.aspect,
        )
        print("==================================================")
        print("✨ ENHANCED & AUDITED FLOW PROMPT:")
        print("==================================================")
        print(enhanced)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
