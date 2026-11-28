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
            "subtitles_center_y_shorts": 1590,
            "subtitles_center_y_long": 930,
            "min_cutout_subtitle_buffer_px": 140,
            "multi_sticker_min_padding_px": 32,
            "multi_sticker_scale_3plus": 0.82
        },
        "rule_25_heading_suppression": {
            "suppress_scene_headings": True,
            "allow_headings_on_cards_only": True
        },
        "rule_26_image_frequency": {
            "opening_hook_target_pace_sec": 2.4,
            "opening_hook_max_hold_sec": 3.5,
            "shorts_min_hold_sec": 1.8,
            "shorts_target_cut_duration_sec": 3.2,
            "shorts_max_hold_sec": 4.2,
            "shorts_min_shots_per_minute": 18,
            "long_min_hold_sec": 2.2,
            "long_target_cut_duration_sec": 4.5,
            "long_max_hold_sec": 6.5,
            "long_min_shots_per_minute": 12,
            "rapid_list_micro_beat_sec": 1.1,
            "forbid_chaotic_flicker_under_sec": 1.5
        },
        "rule_27_audio_sound_design": {
            "broadcast_integrated_lufs": -14.0,
            "lufs_tolerance": 1.0,
            "true_peak_max_dbfs": -1.0,
            "min_sfx_cues_per_minute": 14,
            "enforce_four_audio_layers": True,
            "music_bed_gain_long_db": -13.0,
            "music_bed_gain_shorts_db": -12.5,
            "ambient_foley_gain_db": -24.0,
            "vocal_pocket_eq_enabled": True,
            "vocal_warmth_eq_enabled": True,
            "sidechain_ducking_ratio": 3.0,
            "sidechain_ducking_threshold": 0.14,
            "sidechain_ducking_release_ms": 550
        },
        "rule_28_dynamic_vfx": {
            "camera_shake_on_catastrophe": True,
            "tension_rumble_enabled": True,
            "flashback_grayscale_enabled": False,
            "crimson_hazard_vignette_enabled": False,
            "cyan_frost_vignette_enabled": False,
            "punch_zoom_enabled": True,
            "editorial_slide_wipe_enabled": True,
            "whip_blur_enabled": True,
            "punch_settle_enabled": True
        },
        "rule_29_sticker_synchronization": {
            "strict_word_onset": True,
            "shorts_sticker_ttl_sec": 2.5,
            "long_sticker_ttl_sec": 3.0,
            "smooth_exit_ease_sec": 0.25,
            "exit_fade_enabled": True
        },
        "rule_33_youtube_outro": {
            "long_end_screen_safe_zones": True,
            "shorts_follow_callout_pill": True,
            "separate_standalone_outro": True,
            "outro_duration_sec": 8.0
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
        },
        "rule_46_director_choreography": {
            "require_director_plan": True,
            "word_sync_anticipation_sec": 0.06,
            "forbid_redundant_stickers": True,
            "enable_motion_archetypes": True,
            "animated_draw_on_arrows": True,
            "idle_breathing_enabled": True
        },
        "rule_47_v7_documentary_primitives": {
            "primitives": [
                "strike_replace",
                "circle_focus",
                "checklist_build",
                "chapter_breather",
                "pip_inset",
                "inset_shelf",
                "micro_accent",
                "scale_compare"
            ],
            "checklist_dim_opacity": 0.52,
            "salience_head_mask_enabled": True,
            "opening_proof_beats_before_breather": True,
            "full_circle_callback_plus_standalone_outro": True,
            "enforce_cc0_mit_catalog_clearance": True
        },
        "rule_48_v41_photometric_lighting": {
            "brightness_100_daylight_range": [60.0, 82.0],
            "brightness_100_sunset_range": [44.0, 68.0],
            "brightness_100_flat_max": 86.0,
            "brightness_100_gloomy_min": 45.0,
            "shadow_area_pct_target_range": [5.0, 28.0],
            "shadow_area_pct_heavy_max": 38.0,
            "saturation_pct_target_range": [20.0, 58.0],
            "clipped_white_pct_max": 14.0,
            "contrast_std_min": 30.0,
            "enforce_borderless_full_bleed": True,
            "enforce_clean_flat_white_head": True
        },
        "rule_49_v8_high_density_and_sync": {
            "shorts_unique_shots_target": [26, 36],
            "long_unique_shots_target": [58, 80],
            "forbid_duplicate_shot_transitions": True,
            "shorts_stickers_target": [16, 24],
            "long_stickers_target": [32, 48],
            "strict_voice_sync_max_drift_sec": 0.35,
            "disable_era_anchor_pill": True,
            "forbid_calendar_year_count_roll": True,
            "enforce_stickman_only_humans": True,
            "full_frame_ocr_leak_gate": True,
            "lock_outro_after_vo": True,
            "long_outro_music_only_sec": 8.0,
            "neutral_transformation_mode": True
        }
    },
    "user_feedback_log": [
        {
            "timestamp": "2026-11-28T11:28:00",
            "feedback": "Permanent Core Engine Fixes + High-Density Visuals, Richer Animations, Max Stickers/Cards, Music & VFX Upgrade. Fix stuck pill, same frame animating twice, out-of-sync/inverted cards & stickers, Long Outro overwriting VO, non-stickman humans, low unique shots.",
            "action": "Enforced multi-frame visual progression (26-36 Shorts, 58-80 Long), renderer safety coalescing, zero era pill, voice-sync <=0.35s, neutral strike_replace, 4-digit year roll freeze, outro lock strictly after story_dur, full-frame OCR gate, and 8 new hard-fail F-codes."
        },
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

def record_evaluation_run(slug, format_type, rl_score, metrics, deductions, warnings, f_codes=None):
    """Logs an automated RL-QC audit run, structured F-codes, and updates bounded policy weights."""
    memory = load_rl_memory()
    codes = sorted(list(set(f_codes or [])))
    # Also extract any F_* tags embedded in deductions/warnings for backward compatibility
    known_f_codes = (
        "F_STUTTER", "F_METRONOME", "F_READ_TOO_FAST", "F_NO_SILENCE_DROP",
        "F_FLASH_FRAME", "F_WHOOSH_FATIGUE",
        "F_FLAT_LIGHTING", "F_GLOOMY_DARK_STYLE", "F_MILKY_HAZE", "F_BURNT_HIGHLIGHTS", "F_COMIC_BORDER",
    )
    for txt in list(deductions or []) + list(warnings or []):
        for fc in known_f_codes:
            if fc in str(txt) and fc not in codes:
                codes.append(fc)

    run_entry = {
        "timestamp": datetime.now().isoformat(),
        "slug": slug,
        "format": format_type,
        "rl_score": rl_score,
        "f_codes": codes,
        "metrics": metrics,
        "deductions": deductions,
        "warnings": warnings
    }
    memory.setdefault("evaluation_history", []).append(run_entry)
    memory["evaluation_history"] = memory["evaluation_history"][-60:]

    # Track 4-of-6 Novelty Variety across archetypes/camera patterns
    combo = (metrics or {}).get("layout_signature")
    if combo:
        hist_sigs = [e.get("metrics", {}).get("layout_signature") for e in memory["evaluation_history"][-6:] if e.get("metrics", {}).get("layout_signature")]
        if hist_sigs:
            unique_ratio = len(set(hist_sigs)) / len(hist_sigs)
            run_entry["novelty_4_of_6_pass"] = (len(set(hist_sigs)) >= min(4, len(hist_sigs)))
            run_entry["novelty_unique_ratio"] = round(unique_ratio, 2)

    # Structured F-code bounded self-correction
    if "F_READ_TOO_FAST" in codes and "rule_26_image_frequency" in memory["rules"]:
        cur_min = memory["rules"]["rule_26_image_frequency"].get("shorts_min_hold_sec", 1.8)
        memory["rules"]["rule_26_image_frequency"]["shorts_min_hold_sec"] = min(2.4, round(cur_min + 0.1, 2))
        print(f"🎯 [RL F_READ_TOO_FAST] Raised shorts_min_hold_sec -> {memory['rules']['rule_26_image_frequency']['shorts_min_hold_sec']}s")
    if "F_NO_SILENCE_DROP" in codes and "rule_40_narrative_tension_curve" in memory["rules"]:
        memory["rules"]["rule_40_narrative_tension_curve"]["vox_dropout_silence_enabled"] = True
        memory["rules"]["rule_40_narrative_tension_curve"]["vox_dropout_min_sec"] = 0.45
    if "F_WHOOSH_FATIGUE" in codes and "rule_27_audio_sound_design" in memory["rules"]:
        memory["rules"]["rule_27_audio_sound_design"]["silent_cut_target_pct"] = 0.45
    if "F_METRONOME" in codes and "rule_42_visual_metaphor_entropy" in memory["rules"]:
        memory["rules"]["rule_42_visual_metaphor_entropy"]["enforce_pacing_variance"] = True
    if any(fc in codes for fc in ("F_FLAT_LIGHTING", "F_GLOOMY_DARK_STYLE", "F_MILKY_HAZE", "F_BURNT_HIGHLIGHTS", "F_COMIC_BORDER")):
        r48 = memory.setdefault("rules", {}).setdefault("rule_48_v41_photometric_lighting", {})
        r48["enforce_borderless_full_bleed"] = True
        r48["enforce_clean_flat_white_head"] = True
        if "F_GLOOMY_DARK_STYLE" in codes:
            r48["shadow_area_pct_heavy_max"] = min(38.0, float(r48.get("shadow_area_pct_heavy_max", 38.0)))
            print("🎯 [RL F_GLOOMY_DARK_STYLE] Restored bright open airy 2D daylight & <=38% gentle shadows")
        if "F_MILKY_HAZE" in codes:
            r48["contrast_std_min"] = max(30.0, float(r48.get("contrast_std_min", 30.0)))
            print("🎯 [RL F_MILKY_HAZE] Reinforced zero milky haze / crisp unbleached pigments")
        if "F_BURNT_HIGHLIGHTS" in codes:
            r48["clipped_white_pct_max"] = min(14.0, float(r48.get("clipped_white_pct_max", 14.0)))
            print("🎯 [RL F_BURNT_HIGHLIGHTS] Reinforced unbleached surface highlight protection")
        if "F_COMIC_BORDER" in codes:
            print("🎯 [RL F_COMIC_BORDER] Enforced borderless edge-to-edge full-bleed canvas")
    
    # Adaptive Self-Correction:
    # If pacing received deductions, tighten cut duration in policy
    if any("pacing" in d.lower() or "hold" in d.lower() for d in deductions):
        if "short" in format_type.lower():
            curr = memory["rules"]["rule_26_image_frequency"].get("shorts_target_cut_duration_sec", 2.6)
            new_val = max(2.0, round(curr - 0.2, 2))
            memory["rules"]["rule_26_image_frequency"]["shorts_target_cut_duration_sec"] = new_val
            print(f"🎯 [RL Self-Correction] Tightened Shorts target cut duration: {curr}s -> {new_val}s")
        else:
            curr = memory["rules"]["rule_26_image_frequency"].get("long_target_cut_duration_sec", 4.8)
            new_val = max(4.0, round(curr - 0.3, 2))
            memory["rules"]["rule_26_image_frequency"]["long_target_cut_duration_sec"] = new_val
            print(f"🎯 [RL Self-Correction] Tightened Long target cut duration: {curr}s -> {new_val}s")
            
    # If loudness deviated, strictly reinforce target
    if any("lufs" in d.lower() for d in deductions):
        memory["rules"]["rule_27_audio_sound_design"]["broadcast_integrated_lufs"] = -14.0
        print("🎯 [RL Self-Correction] Reset broadcast integrated loudness target to strict -14.0 LUFS")

    # If crowding / clutter deduction: enforce >= 32px multi-slot padding & spawn-time scale damping (no strict 1-sticker cap)
    if any("crowd" in d.lower() or "clutter" in d.lower() or "overlap" in d.lower() for d in deductions):
        if "rule_24_spatial_hierarchy" in memory["rules"]:
            memory["rules"]["rule_24_spatial_hierarchy"]["multi_sticker_min_padding_px"] = 36
            memory["rules"]["rule_24_spatial_hierarchy"]["multi_sticker_scale_3plus"] = 0.78
            print("🎯 [RL Self-Correction] Tightened multi-slot sticker padding (>=36px) & 0.78x 3+ scale damping (multi-sticker allowed)")

    # If sticker rendering failure: enforce runtime compositing verification gate
    if any("sticker" in d.lower() for d in deductions):
        if "rule_20_style_consistency" in memory["rules"]:
            memory["rules"]["rule_20_style_consistency"]["enforce_render_verification"] = True
            print("🎯 [RL Self-Correction] Enabled mandatory runtime sticker render verification gate")

    # If music intro or bed deduction: calibrate 0.3s fast onset and -11.5 to -12.0 dB bed target
    if any("music" in d.lower() or "intro" in d.lower() for d in deductions):
        if "rule_27_audio_sound_design" in memory["rules"]:
            memory["rules"]["rule_27_audio_sound_design"]["music_bed_fade_in_sec"] = 0.3
            memory["rules"]["rule_27_audio_sound_design"]["music_bed_gain_shorts_db"] = -11.5
            memory["rules"]["rule_27_audio_sound_design"]["music_bed_gain_long_db"] = -12.0
            print("🎯 [RL Self-Correction] Calibrated music bed: 0.3s fade-in, -11.5dB/-12.0dB nominal gain")

    # If SFX buried or inaudible: enforce dynamic boost targets
    if any("sfx" in d.lower() for d in deductions):
        if "rule_27_audio_sound_design" in memory["rules"]:
            memory["rules"]["rule_27_audio_sound_design"]["sfx_impact_boost_db"] = 3.0
            memory["rules"]["rule_27_audio_sound_design"]["sfx_pop_boost_db"] = 2.5
            print("🎯 [RL Self-Correction] Boosted SFX targets (+3dB impacts, +2.5dB tactile pops)")

    # If VFX / static hold deduction: boost kinetic amplitudes
    if any("vfx" in d.lower() or "motion" in d.lower() or "shake" in d.lower() for d in deductions):
        if "rule_28_dynamic_vfx" in memory["rules"]:
            memory["rules"]["rule_28_dynamic_vfx"]["camera_shake_amplitude_px"] = 32.0
            memory["rules"]["rule_28_dynamic_vfx"]["punch_zoom_scale"] = 1.12
            print("🎯 [RL Self-Correction] Boosted VFX kinetics: 32px shake amplitude, 1.12x punch zoom snap")

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
