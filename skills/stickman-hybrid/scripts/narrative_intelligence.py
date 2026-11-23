#!/usr/bin/env python3
"""narrative_intelligence.py: AI Storytelling & Audio-Visual Emotion Director
Synthesizes Affective Science (emotional-arc-designer), Visual Psychology (visual-emotion-engineer),
and Documentary Sound Design (vox-doc-sound) into an automated, high-retention director.
Features:
1. 6-Act YouTube Retention Tension Curve:
   - Act 1: The Paradox Hook (Cold Anomaly)
   - Act 2: The Historical Complication (Ancient Struggle)
   - Act 3: The Ingenious Breakthrough (Mechanical Wonder)
   - Act 4: The Crisis / Catastrophic Flaw (High Stakes Peril)
   - Act 5: The Twist / Revelation (The Peak Aha! Moment)
   - Act 6: Philosophical Payoff & Return (Awe & Modern Reflection)
2. The Vox Drop-Out & Silence Director:
   - Detects the exact narrative turning point and marks the 0.8s-1.2s "Held Breath" silence (--dip).
3. Sub-Bass Impact Placement:
   - Directs 60Hz resonant sub-thuds on statistical shocks and paradigm shifts.
4. Visual Valence & VFX Harmonization:
   - Directs camera shake, rumble, monochrome flashbacks, and hazard vignettes based on emotional arousal.
"""

import os, sys, re, csv, json, argparse

# The 6 Documentary Narrative Acts
ACT_DEFINITIONS = [
    {
        "act": "ACT 1: THE PARADOX HOOK",
        "time_pct": (0.0, 0.15),
        "target_emotion": "Intense Curiosity & Disbelief",
        "arousal": 8.5,
        "tension": 8.0,
        "vfx_recommendation": ["flash", "zoom_punch"],
        "audio_mood": "High-tension ambient drone + vinyl rewind / sub-drop",
        "cue_triggers": ["you", "this morning", "every day", "without realizing", "imagine", "what if"]
    },
    {
        "act": "ACT 2: THE HISTORICAL COMPLICATION",
        "time_pct": (0.15, 0.35),
        "target_emotion": "Empathy & World-Building Wonder",
        "arousal": 5.5,
        "tension": 5.0,
        "vfx_recommendation": ["bw", "grayscale", "fade"],
        "audio_mood": "Curious melodic acoustic textures, warm mid-range",
        "cue_triggers": ["years ago", "ancient", "century", "ancestors", "struggled", "before"]
    },
    {
        "act": "ACT 3: THE INGENIOUS BREAKTHROUGH",
        "time_pct": (0.35, 0.60),
        "target_emotion": "Intellectual Fascination & Clarity",
        "arousal": 7.5,
        "tension": 6.5,
        "vfx_recommendation": ["hover", "pop", "slide_left"],
        "audio_mood": "Rhythmic driving pulse, tactile UI clicks, clock ticks",
        "cue_triggers": ["discovered", "figured out", "built", "invented", "designed", "engineered", "solution"]
    },
    {
        "act": "ACT 4: THE CRISIS / CATASTROPHIC PERIL",
        "time_pct": (0.60, 0.78),
        "target_emotion": "Visceral Dread & Urgent Stakes",
        "arousal": 9.2,
        "tension": 9.5,
        "vfx_recommendation": ["shake", "rumble", "blood", "ice"],
        "audio_mood": "Ominous low-pass filtering, sub-bass rumble, heartbeat pulse",
        "cue_triggers": ["danger", "disaster", "fatal", "starvation", "blackout", "collapse", "destroyed", "failed"]
    },
    {
        "act": "ACT 5: THE TWIST / REVELATION",
        "time_pct": (0.78, 0.90),
        "target_emotion": "Peak Cognitive Shift (The Aha! Moment)",
        "arousal": 10.0,
        "tension": 9.8,
        "vfx_recommendation": ["flash", "zoom_punch", "crossfade"],
        "audio_mood": "THE HELD BREATH DROP-OUT (sudden silence) -> Sub-Bass Reveal Hit",
        "cue_triggers": ["strange part", "terrifying truth", "real reason", "secret", "until one day", "actually"]
    },
    {
        "act": "ACT 6: PHILOSOPHICAL PAYOFF & RETURN",
        "time_pct": (0.90, 1.00),
        "target_emotion": "Awe, Perspective & Modern Integration",
        "arousal": 6.0,
        "tension": 3.0,
        "vfx_recommendation": ["outro", "fade"],
        "audio_mood": "Uplifting melodic swell, warm resolution, YouTube End Slate",
        "cue_triggers": ["today", "next time", "remember", "modern", "never forget", "still"]
    }
]

TWIST_PATTERNS = [
    r"strange part",
    r"terrifying truth",
    r"here is the secret",
    r"real reason",
    r"nobody realized",
    r"but then in",
    r"actually",
    r"until one day",
    r"that was when",
    r"the catch"
]

def analyze_script_acts(lines_path="LINES.tsv"):
    """Maps every narration line to its psychological act, arousal level, and visual/audio direction."""
    if not os.path.exists(lines_path):
        return None

    rows = []
    with open(lines_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for r in reader:
            if r and r[0].strip() and not r[0].startswith("#"):
                rows.append({"id": r[0].strip(), "text": r[1].strip() if len(r) > 1 else ""})

    total_lines = len(rows)
    if total_lines == 0:
        return None

    analyzed_lines = []
    twist_line_id = None
    twist_line_idx = None

    for idx, r in enumerate(rows):
        pct = idx / total_lines
        matched_act = ACT_DEFINITIONS[-1]
        for act in ACT_DEFINITIONS:
            if act["time_pct"][0] <= pct < act["time_pct"][1]:
                matched_act = act
                break

        # Check for explicit twist trigger
        is_twist_phrase = any(re.search(p, r["text"], re.IGNORECASE) for p in TWIST_PATTERNS)
        if is_twist_phrase and not twist_line_id:
            twist_line_id = r["id"]
            twist_line_idx = idx

        analyzed_lines.append({
            "line_id": r["id"],
            "line_num": idx + 1,
            "text": r["text"],
            "act": matched_act["act"],
            "target_emotion": matched_act["target_emotion"],
            "arousal_score": matched_act["arousal"],
            "tension_score": matched_act["tension"],
            "recommended_vfx": matched_act["vfx_recommendation"],
            "is_twist": is_twist_phrase
        })

    # If no explicit twist phrase found, default twist to 82% mark
    if not twist_line_id:
        def_twist_idx = int(total_lines * 0.82)
        twist_line_id = rows[def_twist_idx]["id"]
        twist_line_idx = def_twist_idx
        analyzed_lines[def_twist_idx]["is_twist"] = True

    return {
        "total_lines": total_lines,
        "twist_line_id": twist_line_id,
        "twist_line_idx": twist_line_idx,
        "lines": analyzed_lines
    }

def print_director_report(analysis):
    if not analysis:
        print("Error: Could not analyze LINES.tsv")
        return

    print("==================================================")
    print("🎬 AI NARRATIVE & EMOTIONAL ARC DIRECTOR REPORT   ")
    print("==================================================")
    print(f"Total Lines: {analysis['total_lines']}")
    print(f"Pivotal Twist Line (The Held Breath Drop-Out): Line #{analysis['twist_line_idx']+1} (ID: @{analysis['twist_line_id']})")
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
        print(f"   • [@{l['line_id']}] {l['text'][:65]}...{marker}")

    print("\n==================================================")
    print("🎯 Actionable Audio/Visual Directives:")
    print(f"1. Silence Drop-out: Run mix.py with `--dip @{analysis['twist_line_id']}` (music drops out for 1.0s before reveal).")
    print(f"2. Sub-Bass Impact: Trigger `sub_thud` on line @{analysis['twist_line_id']}.")
    print("3. Visual Flash: Trigger `extra: flash, zoom_punch` on the twist line in SCENES_HYBRID.tsv.")
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
