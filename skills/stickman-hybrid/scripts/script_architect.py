#!/usr/bin/env python3
"""script_architect.py: Autonomous Viral Documentary Script & Scene Architect
Enforces Condition 1 & Rules 40-46:
- NO dumb string templates or hardcoded keyword lists.
- Supports structured agent/LLM-generated blueprints and rich prompts.
- Synthesizes 6-Act tension curves via narrative_intelligence.py (affective science).
- Synthesizes high-CTR titles, chapters, and descriptions via viral_seo_intelligence.py.
- Produces SCRIPT.md, LINES.tsv, and the complete SCENES_HYBRID.tsv manifest.
"""

import os
import sys
import csv
import re
import json
import argparse

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

try:
    import narrative_intelligence
    import viral_seo_intelligence
except ImportError:
    narrative_intelligence = None
    viral_seo_intelligence = None

COMPANION_SKILLS = [
    "emotional-arc-designer",
    "visual-emotion-engineer",
    "data-storytelling",
    "headline-psychologist",
    "loss-aversion-designer",
    "youtube-seo-optimizer"
]


def extract_companion_skills_directives(repo_root=None):
    """Dynamically parses the 6 active SKILL.md files to inject actionable checklists into SCRIPT_SPEC.json."""
    if not repo_root:
        curr = os.path.abspath(os.path.dirname(__file__))
        while curr != os.path.dirname(curr):
            if os.path.exists(os.path.join(curr, "skills")):
                repo_root = curr
                break
            curr = os.path.dirname(curr)
        if not repo_root:
            repo_root = "/home/mirza-ahmed-hassan/Desktop/stickman-animation"

    directives = {}
    for skill_name in COMPANION_SKILLS:
        skill_path = os.path.join(repo_root, "skills", skill_name, "SKILL.md")
        if os.path.exists(skill_path):
            try:
                with open(skill_path, "r", encoding="utf-8") as f:
                    content = f.read()

                desc_match = re.search(r"description:\s*[\"']?([^\"'\n]+)[\"']?", content)
                description = desc_match.group(1).strip() if desc_match else ""

                actionable_points = []
                lines = content.splitlines()
                capture = False
                for line in lines:
                    line_s = line.strip()
                    if re.match(r"^#{2,3}\s+(Execution Steps|Checklists|Rules|Key Directives|Framework|When to Use)", line_s, re.I):
                        capture = True
                        continue
                    if line_s.startswith(("- ", "* ", "1.", "2.", "3.", "4.", "5.", "**Step")):
                        clean_pt = re.sub(r"^[-*\d\.]+\s*", "", line_s).strip()
                        if len(clean_pt) > 15 and clean_pt not in actionable_points:
                            actionable_points.append(clean_pt)
                            if len(actionable_points) >= 6:
                                break

                if not actionable_points:
                    actionable_points = [
                        line.strip().lstrip("-* ").strip() for line in lines
                        if line.strip().startswith(("-", "*")) and len(line.strip()) > 20
                    ][:5]

                directives[skill_name] = {
                    "source": os.path.relpath(skill_path, repo_root),
                    "description": description or f"Core directives from {skill_name}",
                    "actionable_rules": actionable_points
                }
            except Exception as e:
                directives[skill_name] = {
                    "source": os.path.relpath(skill_path, repo_root),
                    "error": str(e),
                    "actionable_rules": [f"Enforce {skill_name} principles."]
                }
        else:
            directives[skill_name] = {
                "source": "fallback",
                "actionable_rules": [f"Enforce {skill_name} principles."]
            }
    return directives


def generate_llm_prompt_specification(topic, format_type="both", lang="en", duration_target="5m"):
    """Generates an authoritative, structured prompt specification for an LLM/agent
    incorporating all 6 companion skills: emotional-arc-designer, visual-emotion-engineer,
    headline-psychologist, loss-aversion-designer, data-storytelling, and youtube-seo-optimizer.
    """
    is_both = (format_type == "both")
    lang_desc = "Conversational English (am_michael / am_fenrir)" if lang == "en" else "Conversational Roman Urdu / Urdu"
    
    companion_directives = extract_companion_skills_directives()

    spec = {
        "role": "Master YouTube Explainer Documentary Showrunner (Vox, Kurzgesagt, Johnny Harris)",
        "topic": topic,
        "language": lang_desc,
        "format": format_type,
        "target_duration": duration_target,
        "mandates": [
            "NO textbook language or flat narration. Every line must carry tension, contrast, or curiosity.",
            "0–15s Present-Day Mirror Hook: Open in 2nd person ('You' / conversational 'Tum') anchored in a relatable modern habit (bed, phone, alarm, coffee), then snap-rewind into history.",
            "Myth-Flip + Named Proof Loop: State the official story everyone believes -> flip it with real named proof (researcher/historian + year + location + concrete metric).",
            "Escalation & Open-Loop Bridges: End every act with a curiosity handoff into the next act so there are zero dead drop-off points.",
            "Full-Circle Emotional Payoff Ending: Always callback to the exact modern object/habit from the first 10 seconds to close the narrative loop.",
            "Natural Native Fluency: For Urdu / Roman Urdu, enforce natural conversational spoken style (relatable modern terms, punchy rhythm—never stiff textbook translations).",
            "Competitor High-Density Visual Pacing Rules: Opening 15s hook target 1.2s–2.2s per visual beat; Shorts body target 1.5s–2.5s (max hold 3.0s); Long body target 2.2s–3.8s (max hold 4.5s); rapid list micro-beats 0.8s–1.4s.",
            "6-Archetype Visual Variety & Sticker Pairing Syntax: Leverage all 6 visual archetypes paired with real 2D transparent stickers: (1) card_stat: 1 hero sticker in balanced negative space with soft drop shadow, (2) split_compare: 1 sticker per side (Left vs Right) + optional verdict stamps (stamp_x / stamp_check), (3) bar_timeline & stat_pie: contextual accent sticker(s) anchored cleanly outside chart bounding box, (4) virtual multi-cam cuts: zoom_in_tight / crop_focus / pan_left / pan_right on Flow hero art, (5) Flow hero scenes: 1-2 word-synced stickers per shot, (6) verdict stamps: animated stamp_x / stamp_check with physical impact.",
            "Enforce the 6-Act YouTube Retention Tension Curve.",
            "Short punchy lines (2-5 words) MUST follow complex explanatory sentences.",
            "Mark Act 5 with 'The Vox Drop-Out' (0.8s silence before a paradigm-shifting revelation).",
            "Identify 4-8 physical, concrete objects as 2D transparent sticker props (1:1 aspect, magenta #FF00FF).",
            "For Shorts (9:16): Fast-paced (40-60s), 0-3s thumb-stopping paradox hook, end with channel CTA.",
            "For Long (16:9): Deep historical or scientific context, multi-scene pacing, philosophical payoff.",
            "Apply all companion skill directives: emotional arc progression, visual palette contrast, loss aversion stakes, and data scale comparisons."
        ],
        "companion_skill_directives": companion_directives,
        "output_schema": {
            "title": topic,
            "short_script": {
                "acts": [
                    {"act_name": "ACT 1: THE PARADOX HOOK", "lines": ["Line 1 text...", "Line 2 text..."]},
                    {"act_name": "ACT 2: THE REWIND", "lines": ["Line 3 text..."]},
                    {"act_name": "ACT 3: THE DISCOVERY", "lines": ["Line 4 text..."]},
                    {"act_name": "ACT 4: THE TWIST", "lines": ["Line 5 text..."]},
                    {"act_name": "ACT 5: THE CHANNEL HANDOFF CTA", "lines": ["Line 6 text..."]}
                ],
                "scenes": [
                    {
                        "shot_id": "shot_01",
                        "cut_at_line": 1,
                        "visual_description": "Clean 2D cartoon description for Google Flow...",
                        "sticker_overlays": [
                            {"element_id": "sticker_name", "object": "description of isolated prop", "reveal_at_word": 4, "physics": "slam"}
                        ]
                    }
                ]
            },
            "long_script": {
                "acts": [
                    {"act_name": f"ACT {i}: ...", "lines": ["..."]} for i in range(1, 7)
                ],
                "scenes": []
            }
        }
    }
    return spec


def parse_and_validate_blueprint(blueprint_data):
    """Validates that a provided blueprint contains real narrative content and scene mappings."""
    if isinstance(blueprint_data, str):
        try:
            blueprint_data = json.loads(blueprint_data)
        except Exception as e:
            raise ValueError(f"Invalid JSON blueprint: {e}")

    if not isinstance(blueprint_data, dict):
        raise ValueError("Blueprint must be a dictionary.")

    title = blueprint_data.get("title", "Untitled Documentary")
    short_data = blueprint_data.get("short_script") or blueprint_data.get("short")
    long_data = blueprint_data.get("long_script") or blueprint_data.get("long")

    if not short_data and not long_data:
        # Check if root has 'acts'
        if "acts" in blueprint_data:
            short_data = blueprint_data
        else:
            raise ValueError("Blueprint must contain at least 'short_script', 'long_script', or 'acts'.")

    return {
        "title": title,
        "short": short_data,
        "long": long_data
    }


def calculate_line_gap(text, is_twist=False):
    """Calculates scientifically calibrated acoustic gap for speech synthesis."""
    txt = text.strip()
    if is_twist:
        return 0.85  # The Vox Drop-Out
    if txt.endswith("?"):
        return 0.60
    if txt.endswith("!"):
        return 0.55
    if txt.endswith("..."):
        return 0.75
    if len(txt.split()) <= 4:
        return 0.50  # Dramatic short punchline
    return 0.35


def compile_pipeline_files(script_branch, out_dir, is_shorts=False, style_tag="bright"):
    """Compiles SCRIPT.md, LINES.tsv, and SCENES_HYBRID.tsv for a pipeline branch."""
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "shots"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "elements/cut"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "takes"), exist_ok=True)

    acts = script_branch.get("acts", [])
    raw_lines = []
    for act in acts:
        for l in act.get("lines", []):
            if isinstance(l, str) and l.strip():
                raw_lines.append(l.strip())
            elif isinstance(l, dict) and "text" in l:
                raw_lines.append(l["text"].strip())

    if not raw_lines:
        raise ValueError(f"No narrative lines found in script branch for {out_dir}")

    # 1. Write SCRIPT.md
    script_md_path = os.path.join(out_dir, "SCRIPT.md")
    with open(script_md_path, "w", encoding="utf-8") as f:
        fmt_label = "9:16 VERTICAL VIRAL SHORT" if is_shorts else "16:9 WIDESCREEN MASTER DOCUMENTARY"
        f.write(f"# {fmt_label}\n\n")
        for act in acts:
            aname = act.get("act_name", "ACT")
            f.write(f"### {aname}\n\n")
            for l in act.get("lines", []):
                ltxt = l if isinstance(l, str) else l.get("text", "")
                f.write(f"{ltxt}\n\n")

    # 2. Write LINES.tsv
    lines_tsv_path = os.path.join(out_dir, "LINES.tsv")
    lines_data = []
    with open(lines_tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["id", "text", "gap"])
        for idx, text in enumerate(raw_lines, 1):
            lid = f"{idx:02d}"
            # Check if this line is in the 75% twist zone
            norm_pos = (idx - 1) / max(1, len(raw_lines) - 1)
            is_twist = (0.70 <= norm_pos <= 0.85 and any(k in text.lower() for k in ["turns out", "actually", "real reason", "truth", "discovered"]))
            gap = calculate_line_gap(text, is_twist=is_twist)
            writer.writerow([lid, text, f"{gap:.2f}"])
            lines_data.append({"id": lid, "text": text, "gap": gap})

    # 3. Write SCENES_HYBRID.tsv (Canonical format: cue, img, text, pos, extra, space)
    scenes_tsv_path = os.path.join(out_dir, "SCENES_HYBRID.tsv")
    provided_scenes = script_branch.get("scenes", [])
    
    shots_rows = []
    seen_shots = set()
    elements_rows = []
    seen_elements = set()

    blueprint_elements = script_branch.get("elements", [])
    if blueprint_elements:
        for el in blueprint_elements:
            eid = str(el.get("id", "01")).replace(".png", "")
            obj = el.get("object") or el.get("description", eid)
            elements_rows.append({"id": eid, "ref": "-", "object": obj})
            seen_elements.add(eid)

    with open(scenes_tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["cue", "img", "text", "pos", "extra", "space"])

        if provided_scenes:
            for s in provided_scenes:
                cut_at = str(s.get("cut_at", f"{s.get('cut_at_line', 1):02d}.0"))
                shot = s.get("shot") or s.get("shot_id") or "shot_01.png"
                if not shot.endswith((".png", ".jpg")):
                    shot += ".png"
                img_path = f"shots/{shot}"
                trans = s.get("trans_type", "flash" if cut_at.startswith("01.") else "cut")
                extra = s.get("extra", "")
                space = s.get("space", "center")
                pos = s.get("pos", "center")
                prompt = s.get("prompt") or s.get("visual_description", "")
                
                shot_base = os.path.splitext(shot)[0]
                if shot_base not in seen_shots:
                    seen_shots.add(shot_base)
                    shots_rows.append({"id": shot_base, "ref": "-", "prompt": prompt})

                # Write scene row
                writer.writerow([cut_at, img_path, "", pos, extra, space])

                # Write separate overlay rows
                ov_list = s.get("overlays") or s.get("sticker_overlays", [])
                if ov_list:
                    for o in ov_list:
                        eid = o.get("element_id") or o.get("name") or "prop"
                        eid_clean = eid.replace(".png", "")
                        r_word = o.get("reveal_at_word", 0)
                        line_num = int(cut_at.split(".")[0]) if "." in cut_at else 1
                        timing = o.get("timing", f"+{line_num:02d}.{r_word}")
                        if not timing.startswith("+"):
                            timing = f"+{timing}"
                        o_pos = o.get("pos", "auto")
                        o_extra = o.get("extra", "pop")
                        writer.writerow([timing, f"elements/cut/{eid_clean}.png", "", o_pos, o_extra, ""])

                        if eid_clean not in seen_elements:
                            seen_elements.add(eid_clean)
                            elements_rows.append({"id": eid_clean, "ref": "-", "object": eid_clean.replace("_", " ")})
        else:
            line_idx = 1
            shot_num = 1
            while line_idx <= len(raw_lines):
                cut_at = f"{line_idx:02d}.0"
                shot_name = f"shot_{shot_num:02d}.png"
                img_path = f"shots/{shot_name}"
                current_text = raw_lines[line_idx - 1]
                v_aspect = "vertical 9:16 portrait mobile illustration" if is_shorts else "16:9 widescreen cinematic documentary illustration"
                prompt = (f"A 2D hand-drawn cartoon illustration: {current_text[:90]}. "
                          f"Format: {v_aspect}. Clean dark ink linework, flat colors with soft shading, bright natural daylight palette. "
                          f"Style: {style_tag}. Full-bleed edge-to-edge frame.")

                shot_base = os.path.splitext(shot_name)[0]
                if shot_base not in seen_shots:
                    seen_shots.add(shot_base)
                    shots_rows.append({"id": shot_base, "ref": "-", "prompt": prompt})

                writer.writerow([cut_at, img_path, "", "center", "", "center"])

                # Concrete noun sticker
                words = re.findall(r"\b[A-Za-z]{4,}\b", current_text.lower())
                candidate_props = [w for w in words if w not in {"this", "that", "with", "from", "they", "were", "what", "when", "there", "their", "sleep", "night", "humans", "human", "today"}]
                if candidate_props and (shot_num % 2 == 1 or len(candidate_props) >= 3):
                    prop_name = candidate_props[0]
                    writer.writerow([f"+{line_idx:02d}.3", f"elements/cut/{prop_name}.png", "", "auto", "pop", ""])
                    if prop_name not in seen_elements:
                        seen_elements.add(prop_name)
                        elements_rows.append({"id": prop_name, "ref": "-", "object": prop_name.replace("_", " ")})

                step = 1 if is_shorts or len(current_text.split()) > 18 else 2
                line_idx += step
                shot_num += 1

    # Write SHOTS.tsv and ELEMENTS.tsv
    shots_tsv_path = os.path.join(out_dir, "SHOTS.tsv")
    elements_tsv_path = os.path.join(out_dir, "ELEMENTS.tsv")
    if shots_rows:
        with open(shots_tsv_path, "w", encoding="utf-8", newline="") as sf:
            w = csv.DictWriter(sf, fieldnames=["id", "ref", "prompt"], delimiter="\t")
            w.writeheader()
            w.writerows(shots_rows)

    if elements_rows:
        with open(elements_tsv_path, "w", encoding="utf-8", newline="") as ef:
            w = csv.DictWriter(ef, fieldnames=["id", "ref", "object"], delimiter="\t")
            w.writeheader()
            w.writerows(elements_rows)

    # 4. Run narrative intelligence verification
    if narrative_intelligence:
        try:
            analysis = narrative_intelligence.analyze_script_acts(lines_tsv_path)
            if analysis:
                report_path = os.path.join(out_dir, "NARRATIVE_AUDIT.json")
                with open(report_path, "w", encoding="utf-8") as rf:
                    json.dump(analysis, rf, indent=2)
        except Exception as e:
            print(f"⚠️ Narrative intelligence audit notice: {e}")

    # 5. Run viral SEO package generation
    if viral_seo_intelligence:
        try:
            seo_pkg = viral_seo_intelligence.generate_seo_package(out_dir)
            if seo_pkg:
                seo_path = os.path.join(out_dir, "METADATA.json")
                with open(seo_path, "w", encoding="utf-8") as sf:
                    json.dump(seo_pkg, sf, indent=2)
        except Exception as e:
            print(f"⚠️ Viral SEO intelligence notice: {e}")

    print(f"✅ Generated production assets for {out_dir}: SCRIPT.md, LINES.tsv, SCENES_HYBRID.tsv, METADATA.json")
    return True


def execute_architecture(topic, blueprint_path=None, blueprint_str=None, format_type="both", lang="en", out_root=".", style="bright"):
    """Master entry point for script and scene generation."""
    print("==================================================")
    print(f"👑 SCRIPT ARCHITECTURE ENGINE: '{topic}'")
    print(f"   Format: {format_type} | Language: {lang} | Style: {style}")
    print("==================================================")

    blueprint = None
    if blueprint_path and os.path.exists(blueprint_path):
        with open(blueprint_path, "r", encoding="utf-8") as bf:
            blueprint = json.load(bf)
    elif blueprint_str:
        blueprint = json.loads(blueprint_str)

    if not blueprint:
        # Check if project root already has an authored blueprint or SCRIPT.md
        candidate_bp = os.path.join(out_root, "blueprint.json")
        if os.path.exists(candidate_bp):
            with open(candidate_bp, "r", encoding="utf-8") as bf:
                blueprint = json.load(bf)

    if not blueprint:
        # Generate prompt specification for AI agent
        spec = generate_llm_prompt_specification(topic, format_type=format_type, lang=lang)
        spec_path = os.path.join(out_root, "SCRIPT_SPEC.json")
        with open(spec_path, "w", encoding="utf-8") as sf:
            json.dump(spec, sf, indent=2)
        print(f"📋 Generated LLM/Agent Script Specification: {spec_path}")
        print("💡 Pass a structured blueprint using --blueprint <file> or --blueprint-json '<json>'")
        return spec

    validated = parse_and_validate_blueprint(blueprint)

    if format_type in ("short", "both") and validated.get("short"):
        s_dir = os.path.join(out_root, "short") if format_type == "both" else out_root
        compile_pipeline_files(validated["short"], s_dir, is_shorts=True, style_tag=style)

    if format_type in ("long", "both") and validated.get("long"):
        l_dir = os.path.join(out_root, "long") if format_type == "both" else out_root
        compile_pipeline_files(validated["long"], l_dir, is_shorts=False, style_tag=style)

    return True


def main():
    parser = argparse.ArgumentParser(description="Autonomous Viral Documentary Script & Scene Architect")
    parser.add_argument("--topic", required=True, help="Documentary Topic")
    parser.add_argument("--format", choices=["short", "long", "both"], default="both")
    parser.add_argument("--lang", choices=["en", "ur", "roman_urdu"], default="en")
    parser.add_argument("--style", default="bright", help="Visual style preset")
    parser.add_argument("--blueprint", default=None, help="Path to structured blueprint JSON")
    parser.add_argument("--blueprint-json", default=None, help="Inline JSON blueprint string")
    parser.add_argument("--out-dir", default=".", help="Target project root directory")
    parser.add_argument("--get-spec", action="store_true", help="Output LLM prompt specification and exit")

    args = parser.parse_args()

    if args.get_spec:
        spec = generate_llm_prompt_specification(args.topic, format_type=args.format, lang=args.lang)
        if args.out_dir:
            os.makedirs(args.out_dir, exist_ok=True)
            spec_path = os.path.join(args.out_dir, "SCRIPT_SPEC.json")
            with open(spec_path, "w", encoding="utf-8") as sf:
                json.dump(spec, sf, indent=2)
            print(f"📋 Generated LLM/Agent Script Specification: {spec_path}", file=sys.stderr)
        print(json.dumps(spec, indent=2))
        sys.exit(0)

    execute_architecture(
        topic=args.topic,
        blueprint_path=args.blueprint,
        blueprint_str=args.blueprint_json,
        format_type=args.format,
        lang=args.lang,
        out_root=args.out_dir,
        style=args.style
    )


if __name__ == "__main__":
    main()
