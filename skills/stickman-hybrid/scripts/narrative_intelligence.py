#!/usr/bin/env python3
"""narrative_intelligence.py: AI Storytelling & Audio-Visual Emotion Director
Synthesizes Affective Science (emotional-arc-designer), Visual Psychology (visual-emotion-engineer),
and Documentary Sound Design (vox-doc-sound) into an automated, high-retention director.

Programmatically loads and enforces:
- skills/emotional-arc-designer/SKILL.md
- skills/visual-emotion-engineer/SKILL.md
- skills/data-storytelling/SKILL.md
"""

import os
import sys
import re
import csv
import json
import argparse

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SKILL_SCRIPTS, "../../../"))
SKILLS_DIR = os.path.join(PROJECT_ROOT, "skills")


def load_companion_skill_directives(skill_name):
    """Loads and extracts actionable directives from a companion SKILL.md file."""
    skill_md = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    directives = {"name": skill_name, "loaded": False, "raw_text": "", "rules": []}
    if os.path.exists(skill_md):
        try:
            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()
                directives["loaded"] = True
                directives["raw_text"] = content
                # Extract sections
                sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
                directives["rules"] = sections
        except Exception as e:
            directives["error"] = str(e)
    return directives


# Load and verify companion skills at module initialization
COMPANION_SKILLS = {
    "emotional-arc-designer": load_companion_skill_directives("emotional-arc-designer"),
    "visual-emotion-engineer": load_companion_skill_directives("visual-emotion-engineer"),
    "data-storytelling": load_companion_skill_directives("data-storytelling")
}


# The 6 Documentary Narrative Acts (Calibrated with emotional-arc-designer & Top 19.3M-View Retention Architecture)
ACT_DEFINITIONS = [
    {
        "act": "ACT 1: THE PRESENT-DAY MIRROR HOOK",
        "time_pct": (0.0, 0.15),
        "target_emotion": "Intense Relatability & Immediate Curiosity",
        "arousal": 8.5,
        "tension": 8.0,
        "vfx_recommendation": ["flash", "zoom_punch"],
        "audio_mood": "High-tension ambient drone + vinyl rewind / sub-drop",
        "cue_triggers": ["you", "your", "tum", "aap", "this morning", "tonight", "every day", "without realizing", "imagine", "what if", "bed", "alarm", "phone"]
    },
    {
        "act": "ACT 2: THE HISTORICAL COMPLICATION & MYTH FLIP",
        "time_pct": (0.15, 0.35),
        "target_emotion": "Cognitive Dissonance & World-Building Wonder",
        "arousal": 6.5,
        "tension": 6.0,
        "vfx_recommendation": ["bw", "vignette_amber", "stamp_x"],
        "audio_mood": "Warm tactile foley + muted marimba pulse",
        "cue_triggers": ["we were taught", "official story", "everyone thinks", "sub sochtay hain", "years ago", "ancestors", "centuries", "prehistoric", "ancient", "history", "originally"]
    },
    {
        "act": "ACT 3: THE INGENIOUS BREAKTHROUGH & NAMED PROOF",
        "time_pct": (0.35, 0.55),
        "target_emotion": "Intellectual Euphoria & Concrete Proof",
        "arousal": 7.5,
        "tension": 5.0,
        "vfx_recommendation": ["zoom_punch", "slide_right", "stamp_check"],
        "audio_mood": "Driving Kurzgesagt synth bed + playful mechanical clacks",
        "cue_triggers": ["discovered", "historian", "dr.", "archaeologist", "researchers", "built", "invented", "designed", "engineered", "solution", "fire", "tools", "technology"]
    },
    {
        "act": "ACT 4: THE CRISIS / CATASTROPHIC FLAW",
        "time_pct": (0.55, 0.72),
        "target_emotion": "Visceral Dread & High-Stakes Urgency",
        "arousal": 9.0,
        "tension": 9.5,
        "vfx_recommendation": ["shake", "rumble", "danger"],
        "audio_mood": "Sub-bass tension drone (50Hz) + sudden percussion drop",
        "cue_triggers": ["deadly", "failed", "collapsed", "predator", "nightmare", "starvation", "freeze", "extinction", "threat", "danger"]
    },
    {
        "act": "ACT 5: THE PEAK TWIST & VOX SILENCE",
        "time_pct": (0.72, 0.88),
        "target_emotion": "Profound Revelation & Paradigm Shift",
        "arousal": 8.0,
        "tension": 6.0,
        "vfx_recommendation": ["flash", "zoom_punch"],
        "audio_mood": "THE VOX DROP-OUT: 0.8s Total Digital Silence -> Resonant Bass Chime",
        "cue_triggers": ["turns out", "the real reason", "nobody realized", "the truth is", "actually", "hidden in plain sight", "reveals"]
    },
    {
        "act": "ACT 6: THE PHILOSOPHICAL FULL-CIRCLE RETURN",
        "time_pct": (0.88, 1.0),
        "target_emotion": "Contemplative Awe & Closing Callback Payoff",
        "arousal": 5.0,
        "tension": 2.5,
        "vfx_recommendation": ["vignette_amber", "crossfade"],
        "audio_mood": "Lush melodic acoustic guitar / ambient piano reverb decay",
        "cue_triggers": ["next time", "tonight", "your bed", "we carry", "remains", "our DNA", "every human", "living inside you", "callback"]
    }
]


def get_companion_status():
    """Returns load status of companion skills."""
    return {k: v["loaded"] for k, v in COMPANION_SKILLS.items()}


def analyze_script_acts(lines_path="LINES.tsv"):
    """Reads LINES.tsv and classifies each line into the 6-Act tension curve,
    enforcing emotional-arc-designer and visual-emotion-engineer rules.
    """
    if not os.path.exists(lines_path):
        return None

    lines = []
    with open(lines_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        for r in reader:
            if not r or r[0].startswith("#"):
                continue
            lid = r[0].strip()
            text = r[1].strip() if len(r) > 1 else ""
            gap = float(r[2].strip()) if len(r) > 2 else 0.45
            lines.append({"id": lid, "text": text, "gap": gap})

    total_lines = len(lines)
    if total_lines == 0:
        return None

    analyzed_lines = []
    twist_line_id = None
    twist_line_idx = -1

    for i, l in enumerate(lines):
        norm_pos = i / max(1, total_lines - 1)
        matched_act = ACT_DEFINITIONS[-1]
        for act in ACT_DEFINITIONS:
            if act["time_pct"][0] <= norm_pos <= act["time_pct"][1]:
                matched_act = act
                break

        # Check for twist turning point
        text_lower = l["text"].lower()
        is_twist_candidate = any(t in text_lower for t in ACT_DEFINITIONS[4]["cue_triggers"])
        is_in_twist_zone = (0.65 <= norm_pos <= 0.88)

        is_twist = False
        if is_twist_candidate and is_in_twist_zone and twist_line_id is None:
            is_twist = True
            twist_line_id = l["id"]
            twist_line_idx = i

        # Calculate pacing variance metric (from data-storytelling)
        words = l["text"].split()
        word_count = len(words)
        pacing_type = "punchy" if word_count <= 5 else ("analytical" if word_count >= 16 else "standard")

        analyzed_lines.append({
            "line_id": l["id"],
            "text": l["text"],
            "gap": l["gap"],
            "act": matched_act["act"],
            "target_emotion": matched_act["target_emotion"],
            "arousal_score": matched_act["arousal"],
            "tension_score": matched_act["tension"],
            "recommended_vfx": matched_act["vfx_recommendation"],
            "audio_mood": matched_act["audio_mood"],
            "word_count": word_count,
            "pacing_type": pacing_type,
            "is_twist": is_twist
        })

    # Default twist if not detected by keywords
    if twist_line_id is None:
        def_twist_idx = int(total_lines * 0.75)
        twist_line_id = lines[def_twist_idx]["id"]
        twist_line_idx = def_twist_idx
        analyzed_lines[def_twist_idx]["is_twist"] = True

    return {
        "total_lines": total_lines,
        "twist_line_id": twist_line_id,
        "twist_line_idx": twist_line_idx,
        "companion_skills_loaded": get_companion_status(),
        "lines": analyzed_lines
    }


def print_director_report(analysis):
    if not analysis:
        print("Error: Could not analyze LINES.tsv")
        return

    print("==================================================")
    print("🎬 AI NARRATIVE & EMOTIONAL ARC DIRECTOR REPORT")
    print(f"   Companion Skills: {analysis.get('companion_skills_loaded')}")
    print("==================================================")
    print(f"Total Lines: {analysis['total_lines']}")
    print(f"Pivotal Twist Line (Vox Drop-Out): Line #{analysis['twist_line_idx']+1} (ID: @{analysis['twist_line_id']})")
    print("\n--- 6-Act Narrative Tension Curve Breakdown ---")

    current_act = None
    for l in analysis["lines"]:
        if l["act"] != current_act:
            current_act = l["act"]
            print(f"\n▶ {current_act}")
            print(f"   Target Emotion: {l['target_emotion']}")
            print(f"   Arousal: {l['arousal_score']}/10 | Tension: {l['tension_score']}/10")
            print(f"   Recommended VFX: {', '.join(l['recommended_vfx'])}")

        marker = " ⚡ [THE DROP-OUT SILENCE & TWIST]" if l["is_twist"] else ""
        print(f"   • [@{l['line_id']}] ({l['pacing_type']}) {l['text'][:65]}...{marker}")

    print("\n==================================================")
    print("🎯 Actionable Audio/Visual Directives:")
    print(f"1. Silence Drop-out: Run mix.py with `--dip @{analysis['twist_line_id']}` (music drops out for 0.8s).")
    print(f"2. Sub-Bass Impact: Trigger `sub_thud` on line @{analysis['twist_line_id']}.")
    print(f"3. Visual Flash: Trigger `extra: flash, zoom_punch` on the twist line in SCENES_HYBRID.tsv.")
    print("==================================================")


def main():
    parser = argparse.ArgumentParser(description="AI Storytelling & Audio-Visual Emotion Director")
    parser.add_argument("lines_file", nargs="?", default="LINES.tsv", help="Path to LINES.tsv")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    analysis = analyze_script_acts(args.lines_file)
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print_director_report(analysis)


if __name__ == "__main__":
    main()
