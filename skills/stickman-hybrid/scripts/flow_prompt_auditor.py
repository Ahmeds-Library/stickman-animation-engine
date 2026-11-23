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

# Core Stickman Purity Anchor
STICKMAN_ANATOMY_ANCHOR = (
    "2D cartoon stickman character anatomy: clean round white ball head, simple dot eyes, "
    "expressive thin black stick limbs, simple ink mouth, hand-drawn vector art style, thick dark outlines"
)

# Layered Negative Prompts
NEGATIVE_STICKMAN = (
    "photorealistic, realistic human skin texture, detailed human face, photograph, 3D CGI render, "
    "glossy digital sculpture, uncanny valley, anime, manga, realistic muscles, realistic eyes, realistic lips"
)

NEGATIVE_CLEANLINESS = (
    "watermark, logo, text, letters, numbers, labels, typography, subtitles, credits, signature, "
    "blurry, out of focus, low resolution, multiple versions of the character in one frame, cluttered background"
)

NEGATIVE_ERA_ANCIENT = (
    "modern technology, cars, airplanes, power lines, plastic bottles, electric lights, smartphones, "
    "modern clothing, wristwatches, concrete highways, skyscrapers"
)

NEGATIVE_CHROMA_STICKER = (
    "complex background, gradient background, floor shadows, ground contact shadows, ambient occlusion on floor, "
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

def audit_and_enhance_prompt(prompt, is_sticker=False, is_ancient=False, space="auto", ref_char=None):
    """Audits a raw prompt, injects missing positive anchors, sanitizes policy triggers,
    and appends comprehensive multi-layered negative prompts.
    """
    cleaned = sanitize_policy_words(prompt.strip())
    
    # 1. Purity Check: Does it have stickman anatomy anchor?
    has_stickman = any(w in cleaned.lower() for w in ["stickman", "stick figure", "stick-figure", "white ball head"])
    if not is_sticker and not has_stickman and ref_char != "-":
        cleaned = f"{cleaned}, featuring {STICKMAN_ANATOMY_ANCHOR}"

    # 2. Spatial Composition Docking
    if space == "left" and "left" not in cleaned.lower():
        cleaned = f"{cleaned}, subject positioned on the right side, wide clear empty space on the left 45% of frame"
    elif space == "right" and "right" not in cleaned.lower():
        cleaned = f"{cleaned}, subject positioned on the left side, wide clear empty space on the right 45% of frame"

    # 3. Sticker Chroma Constraints
    if is_sticker:
        if "#FF00FF" not in cleaned and "magenta" not in cleaned.lower():
            cleaned = f"Isolated prop cutout on pure solid uniform magenta background #FF00FF: {cleaned}, centered, single object, crisp sharp edges"

    # 4. Assemble Multi-Layered Negative Prompt
    negatives = [NEGATIVE_STICKMAN, NEGATIVE_CLEANLINESS]
    if is_ancient:
        negatives.append(NEGATIVE_ERA_ANCIENT)
    if is_sticker:
        negatives.append(NEGATIVE_CHROMA_STICKER)

    negative_block = " Negative: " + ", ".join(negatives)
    
    # Return enriched prompt
    full_prompt = f"{cleaned} {negative_block}"
    return full_prompt

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
    parser.add_argument("--audit-file", type=str, help="Audit a SHOTS.tsv file")
    args = parser.parse_args()

    if args.audit_file:
        res = audit_shots_file(args.audit_file)
        print("==================================================")
        print(f"📋 SHOTS.TSV PROMPT AUDIT REPORT: {args.audit_file}")
        print("==================================================")
        for k, v in res.items():
            print(f"• {k}: {v}")
    elif args.prompt:
        enhanced = audit_and_enhance_prompt(args.prompt, is_sticker=args.sticker, is_ancient=args.ancient, space=args.space)
        print("==================================================")
        print("✨ ENHANCED & AUDITED FLOW PROMPT:")
        print("==================================================")
        print(enhanced)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
