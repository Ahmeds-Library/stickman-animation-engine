#!/usr/bin/env python3
"""rl_memory.py: Continuous Reinforcement Learning & Self-Correcting Experience Replay Hub
Maintains persistent RL history, user feedback policies, and adaptive generation parameters.
Every time a video is rendered or audited:
1. Records quantitative metrics (cut pacing, hold duration, loudness LUFS, SFX density, subtitle margins).
2. Integrates qualitative user feedback into persistent policy rules.
3. Dynamically exports optimal generation constraints to render_pro.py, pictures.py, and flow generators.
"""

import os, sys, json, time, argparse
from datetime import datetime

GLOBAL_CONFIG_DIR = os.path.expanduser("~/.gemini/config/skills/stickman-hybrid")
GLOBAL_RL_FILE = os.path.join(GLOBAL_CONFIG_DIR, "rl_feedback_memory.json")
LOCAL_RL_FILE = os.path.join(os.getcwd(), ".planning", "rl_history.json")

# Default Ground-Truth Policy Vector (calibrated from viral reference data & user feedback)
DEFAULT_POLICY = {
    "version": "2.0.0",
    "updated_at": "2026-11-22T21:45:00",
    "rules": {
        "rule_20_style_consistency": {
            "enforce_pure_2d": True,
            "forbid_photorealism_and_3d": True,
            "universal_negative_prompt_enabled": True
        },
        "rule_24_spatial_hierarchy": {
            "shorts_margin_right_px": 220,
            "shorts_bottom_clearance_px": 660,
            "subtitles_center_y_shorts": 1180,
            "subtitles_center_y_long": 930,
            "min_cutout_subtitle_buffer_px": 140
        },
        "rule_25_heading_suppression": {
            "suppress_scene_headings": True,
            "allow_headings_on_cards_only": True
        },
        "rule_26_image_frequency": {
            "shorts_target_cut_duration_sec": 2.6,
            "shorts_max_hold_sec": 3.4,
            "shorts_min_shots_per_minute": 24,
            "long_target_cut_duration_sec": 4.8,
            "long_max_hold_sec": 6.8,
            "long_min_shots_per_minute": 14
        },
        "rule_27_audio_sound_design": {
            "broadcast_integrated_lufs": -14.0,
            "lufs_tolerance": 1.0,
            "true_peak_max_dbfs": -1.0,
            "min_sfx_cues_per_minute": 16,
            "enforce_four_audio_layers": True,
            "music_bed_gain_long_db": -17.0,
            "music_bed_gain_shorts_db": -16.0,
            "ambient_foley_gain_db": -23.0,
            "vocal_pocket_eq_enabled": True,
            "vocal_warmth_eq_enabled": True,
            "sidechain_ducking_ratio": 2.8,
            "sidechain_ducking_threshold": 0.08,
            "sidechain_ducking_release_ms": 550
        },
        "rule_28_dynamic_vfx": {
            "camera_shake_on_catastrophe": True,
            "tension_rumble_enabled": True,
            "flashback_grayscale_enabled": True,
            "crimson_hazard_vignette_enabled": True,
            "cyan_frost_vignette_enabled": True,
            "punch_zoom_enabled": True
        },
        "rule_29_sticker_synchronization": {
            "strict_word_onset": True,
            "shorts_sticker_ttl_sec": 1.8,
            "long_sticker_ttl_sec": 2.2,
            "smooth_exit_ease_sec": 0.28,
            "exit_fade_enabled": True
        },
        "rule_33_youtube_outro": {
            "long_end_screen_safe_zones": True,
            "shorts_follow_callout_pill": True,
            "outro_duration_sec": 12.0
        },
        "rule_35_thumbnail_3_elements": {
            "enforce_expressive_stickman": True,
            "enforce_glowing_hero_prop": True,
            "enforce_tilted_curiosity_text": True,
            "text_tilt_deg": -3.5,
            "text_stroke_px": 14,
            "flow_generation_enabled": True
        },
        "rule_40_narrative_tension_curve": {
            "enforce_6_acts": True,
            "vox_dropout_silence_enabled": True,
            "sub_bass_impacts_enabled": True
        },
        "rule_41_pattern_interrupts": {
            "max_static_hold_sec": 3.0,
            "cinematic_push_in_scale": 1.045,
            "push_in_duration_sec": 4.0
        },
        "rule_42_visual_metaphor_entropy": {
            "target_entropy_pace_sec": 3.8,
            "prevent_repetitive_layouts": True
        },
        "rule_43_auditory_highlighters": {
            "highlight_dates_and_stats": True,
            "highlighter_gain_db": -22.0,
            "kurzgesagt_pencil_transients": True
        },
        "rule_44_curiosity_architecture": {
            "macro_hook_act1_required": True,
            "micro_bridges_target_gap_sec": 60.0,
            "loewenstein_information_gap": True,
            "zeigarnik_effect_enabled": True
        },
        "rule_45_thumbnail_mobile_readability": {
            "mobile_check_140px": True,
            "contrast_luminance_threshold": 25.0,
            "max_words_hook": 3
        }
    },
    "user_feedback_log": [
        {
            "timestamp": "2026-11-22T20:45:00",
            "feedback": "Ziada image use kia kro, fast pacing sustains dopamine",
            "action": "Calibrated shorts_target_cut_duration_sec to 2.6s and long to 4.8s"
        },
        {
            "timestamp": "2026-11-22T20:55:00",
            "feedback": "Heading text screen pr na aaye, sticker k sath clutter banta hai",
            "action": "Enforced suppress_scene_headings=True on all standard scenes"
        },
        {
            "timestamp": "2026-11-22T21:10:00",
            "feedback": "Sticker word aane par aae aur kuch time baad chala jae (sync & exit)",
            "action": "Configured word-onset synchronization with 1.8s/2.2s TTL and smooth 0.28s exit ease"
        },
        {
            "timestamp": "2026-11-22T21:30:00",
            "feedback": "Shaking, black & white, blood/danger, YouTube outro closing aur viral thumbnails add kro",
            "action": "Implemented Broadcast VFX Suite, YouTube End Screen Slates, and High-CTR Thumbnail Generator"
        },
        {
            "timestamp": "2026-11-22T21:46:00",
            "feedback": "RL se continuous update kro, Flow se thumbnail banao aur missing elements auto-add kro",
            "action": "Established RL Experience Replay Hub, Flow Thumbnail Generator, and Flow Extension architecture recommendations"
        },
        {
            "timestamp": "2026-11-22T22:26:00",
            "feedback": "Background music is way too low, voice feels like textbook reading instead of storytelling",
            "action": "Upgraded to Storytelling Golden Ratio (-17dB bed, vocal pocket notch EQ -3.2dB at 1.8kHz, gentle 2.8:1 ducking with 550ms release, vocal warmth broadcast EQ)"
        },
        {
            "timestamp": "2026-11-22T23:15:00",
            "feedback": "Deep intelligence add kro, internet deep research kro, related skills explore & download kro",
            "action": "Integrated Loewenstein Information Gap, Zeigarnik curiosity bridges, Kurzgesagt Auditory Highlighter Pens, 3-Element Mobile Test, and vendored 7 companion skills"
        }
    ],
    "evaluation_history": []
}

def load_rl_memory():
    """Loads active RL memory from global or local config with fallback to default."""
    os.makedirs(GLOBAL_CONFIG_DIR, exist_ok=True)
    if os.path.exists(GLOBAL_RL_FILE):
        try:
            with open(GLOBAL_RL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception:
            pass
    return DEFAULT_POLICY

def save_rl_memory(data):
    """Saves updated RL memory to both global and local workspaces."""
    os.makedirs(GLOBAL_CONFIG_DIR, exist_ok=True)
    data["updated_at"] = datetime.now().isoformat()
    try:
        with open(GLOBAL_RL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[RL Memory Warning] Could not save global RL memory: {e}")
        
    claude_dir = os.path.expanduser("~/.claude/skills/stickman-hybrid")
    if os.path.exists(claude_dir):
        try:
            with open(os.path.join(claude_dir, "rl_feedback_memory.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    # Save to local project .planning if available
    local_planning = os.path.join(os.getcwd(), ".planning")
    if os.path.exists(local_planning):
        try:
            with open(os.path.join(local_planning, "rl_history.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

def record_evaluation_run(slug, format_type, rl_score, metrics, deductions, warnings):
    """Logs an automated RL-QC audit run and updates policy weights if needed."""
    memory = load_rl_memory()
    run_entry = {
        "timestamp": datetime.now().isoformat(),
        "slug": slug,
        "format": format_type,
        "rl_score": rl_score,
        "metrics": metrics,
        "deductions": deductions,
        "warnings": warnings
    }
    memory["evaluation_history"].append(run_entry)
    
    # Adaptive Self-Correction:
    # If pacing received deductions, tighten cut duration in policy
    if any("pacing" in d.lower() or "hold" in d.lower() for d in deductions):
        if "short" in format_type.lower():
            memory["rules"]["rule_26_image_frequency"]["shorts_target_cut_duration_sec"] = max(2.0, memory["rules"]["rule_26_image_frequency"]["shorts_target_cut_duration_sec"] - 0.2)
        else:
            memory["rules"]["rule_26_image_frequency"]["long_target_cut_duration_sec"] = max(4.0, memory["rules"]["rule_26_image_frequency"]["long_target_cut_duration_sec"] - 0.3)
            
    # If loudness deviated, strictly reinforce target
    if any("lufs" in d.lower() for d in deductions):
        memory["rules"]["rule_27_audio_sound_design"]["broadcast_integrated_lufs"] = -14.0

    save_rl_memory(memory)
    return memory

def log_user_feedback(feedback_text, action_taken="Registered in policy vector"):
    """Appends qualitative user feedback and updates learning memory."""
    memory = load_rl_memory()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "feedback": feedback_text,
        "action": action_taken
    }
    memory["user_feedback_log"].append(entry)
    save_rl_memory(memory)
    print(f"✅ User feedback logged to persistent RL memory: \"{feedback_text}\"")

def get_active_policy():
    """Retrieves current active policy vector for generator scripts."""
    memory = load_rl_memory()
    return memory.get("rules", DEFAULT_POLICY["rules"])

def print_status():
    memory = load_rl_memory()
    print("==================================================")
    print("🧠 RL CONTINUOUS LEARNING MEMORY STATUS")
    print("==================================================")
    print(f"Version: {memory.get('version', '2.0.0')} | Last Updated: {memory.get('updated_at')}")
    print(f"Total Logged User Feedback Items: {len(memory.get('user_feedback_log', []))}")
    print(f"Total Video Audits Recorded: {len(memory.get('evaluation_history', []))}")
    print("\n--- Active Policy Rules ---")
    rules = memory.get("rules", {})
    for r_name, r_vals in rules.items():
        print(f"• {r_name}:")
        for k, v in r_vals.items():
            print(f"   ↳ {k}: {v}")
    print("\n--- Recent User Feedback Log ---")
    for fb in memory.get("user_feedback_log", [])[-4:]:
        print(f"[{fb['timestamp'][:16]}] \"{fb['feedback']}\" -> {fb['action']}")
    print("==================================================")

def main():
    parser = argparse.ArgumentParser(description="RL Experience Replay Memory Hub")
    parser.add_argument("action", choices=["status", "log", "get"], default="status", nargs="?")
    parser.add_argument("--feedback", type=str, help="User feedback text to log")
    parser.add_argument("--action-taken", type=str, default="Policy adjusted", help="Action taken description")
    args = parser.parse_args()

    if args.action == "status":
        print_status()
    elif args.action == "log":
        if args.feedback:
            log_user_feedback(args.feedback, args.action_taken)
        else:
            print("Error: --feedback is required for 'log' action.")
    elif args.action == "get":
        print(json.dumps(get_active_policy(), indent=2))

if __name__ == "__main__":
    main()
