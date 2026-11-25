#!/usr/bin/env python3
"""pipeline_dual.py: Dual-Pipeline Decoupled Production Engine (Rule 22)
Orchestrates:
1. Script Architecture & Retention Curve (script_architect.py)
2. Decoupled Formats: Short (9:16 Vertical) + Long (16:9 Widescreen)
3. Voiceover Synthesis & Whisper Forced Alignment (kokoro_vo.py / Parler)
4. Word-Level Scene & Sticker Synchronization (align_hybrid_scenes.py)
5. Emotion & Visual Effects Directing (vfx_smart_designer.py)
6. Centralized Mutual Sticker Registry & Deduplication (asset_registry.py)
7. Google Flow Visual Asset Generation (flow_smart_generator.py)
8. High-Density CC0 Sound Design & 3-Stem Mastering (sfx_smart_designer.py & mix.py)
9. Mandatory Pre-Render Quality Gate (validate_pipeline.py)
10. Broadcast Multi-layer Video Rendering (render_pro.py)
11. Full Reinforcement Learning Quality Audit & Experience Replay (evaluate_rl.py)
"""

import os
import sys
import time
import subprocess
import csv
import json
import shutil
import argparse

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

# Autonomous Zero-Setup Bootstrapper
try:
    import auto_bootstrap
    auto_bootstrap.ensure_environment()
except Exception:
    pass

VOX_SCRIPTS = os.path.abspath(os.path.join(SKILL_SCRIPTS, "../../vox-doc-sound/scripts"))
SCRIPT_ARCHITECT = os.path.join(SKILL_SCRIPTS, "script_architect.py")
SMART_GEN = os.path.join(SKILL_SCRIPTS, "flow_smart_generator.py")
RENDER_PRO = os.path.join(SKILL_SCRIPTS, "render_pro.py")
EVALUATE_RL = os.path.join(SKILL_SCRIPTS, "evaluate_rl.py")
SFX_SMART_DESIGNER = os.path.join(SKILL_SCRIPTS, "sfx_smart_designer.py")
VFX_SMART_DESIGNER = os.path.join(SKILL_SCRIPTS, "vfx_smart_designer.py")
ALIGN_HYBRID_SCENES = os.path.join(SKILL_SCRIPTS, "align_hybrid_scenes.py")
DIRECTOR_SUPERVISOR = os.path.join(SKILL_SCRIPTS, "director_supervisor.py")
ASSET_REGISTRY = os.path.join(SKILL_SCRIPTS, "asset_registry.py")
VALIDATE_PIPELINE = os.path.join(SKILL_SCRIPTS, "validate_pipeline.py")

FLOW_BRIDGE_CHECKER = os.path.join(SKILL_SCRIPTS, "flow_bridge_checker.py")
FLOW_PROMPT_AUDITOR = os.path.join(SKILL_SCRIPTS, "flow_prompt_auditor.py")
THUMBNAIL_GENERATOR = os.path.join(SKILL_SCRIPTS, "thumbnail_generator.py")
FLOW_THUMBNAIL_GENERATOR = os.path.join(SKILL_SCRIPTS, "flow_thumbnail_generator.py")
SOCIAL_PACKAGER = os.path.join(SKILL_SCRIPTS, "social_packager.py")
LOW_RESOURCE_ENGINE = os.path.join(SKILL_SCRIPTS, "low_resource_engine.py")
LOW_RESOURCE_WHISPER = os.path.join(SKILL_SCRIPTS, "low_resource_whisper.py")

KOKORO_VO = os.path.join(VOX_SCRIPTS, "kokoro_vo.py")
VO_JOIN = os.path.join(VOX_SCRIPTS, "vo_join.py")
ALIGN_VO = os.path.join(VOX_SCRIPTS, "align.py")
MIX_VO = os.path.join(VOX_SCRIPTS, "mix.py")
PARLER_JOB_MAKER = os.path.abspath(os.path.join(VOX_SCRIPTS, "../kaggle/make_parler_job.py"))
KAGGLE_RUNNER = os.path.abspath(os.path.join(VOX_SCRIPTS, "kaggle_runner.py"))


def setup_dual_structure(project_root):
    """Sets up decoupled sub-pipeline directories with centralized asset registry."""
    try:
        from anti_pollution import validate_external_output_dir
        project_root = validate_external_output_dir(project_root)
    except ImportError:
        pass
    print(f"\n📂 Initializing Decoupled Dual-Pipeline Structure in {project_root}...")
    for sub in ["short", "long"]:
        d = os.path.join(project_root, sub)
        os.makedirs(os.path.join(d, "shots"), exist_ok=True)
        os.makedirs(os.path.join(d, "elements/raw"), exist_ok=True)
        os.makedirs(os.path.join(d, "elements/cut"), exist_ok=True)
        os.makedirs(os.path.join(d, "takes"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "elements/cut"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "img"), exist_ok=True)
    
    if os.path.exists(ASSET_REGISTRY):
        subprocess.run([sys.executable, ASSET_REGISTRY, project_root])
    print("✅ Structure ready: short/ (9:16) and long/ (16:9) with shared asset registry")


def ensure_scripts_generated(project_root, topic, format_type="both", lang="en", style="bright", blueprint=None):
    """Generates SCRIPT.md, LINES.tsv, and SCENES_HYBRID.tsv if not present."""
    short_lines = os.path.join(project_root, "short", "LINES.tsv")
    long_lines = os.path.join(project_root, "long", "LINES.tsv")

    needs_gen = False
    if format_type in ("short", "both") and not os.path.exists(short_lines):
        needs_gen = True
    if format_type in ("long", "both") and not os.path.exists(long_lines):
        needs_gen = True

    if needs_gen:
        print(f"\n📝 Synthesizing Narrative Architecture for '{topic}'...")
        cmd = [
            sys.executable, SCRIPT_ARCHITECT,
            "--topic", topic,
            "--format", format_type,
            "--lang", lang,
            "--style", style,
            "--out-dir", project_root
        ]
        if blueprint and os.path.exists(blueprint):
            cmd.extend(["--blueprint", blueprint])
        subprocess.run(cmd, check=True)


def synthesize_voice_pipeline(sub_dir, lang="en", voice="am_michael", speed=1.0):
    """Executes voiceover synthesis with clean language routing (Condition 4)."""
    print(f"\n🎙️ Synthesizing Voiceover for {sub_dir} (Language: {lang}, Voice: {voice}, Speed: {speed:.2f}x)...")
    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        lines_tsv = "LINES.tsv"
        if not os.path.exists(lines_tsv):
            raise FileNotFoundError(f"Missing {lines_tsv} in {sub_dir}")

        if lang == "en":
            # 1. Kokoro English takes
            subprocess.run([sys.executable, KOKORO_VO, lines_tsv, "--lang", "a", "--voice", voice, "--speed", str(speed), "--out", "takes"], check=True)
            # 2. Join takes
            subprocess.run([sys.executable, VO_JOIN, "takes", lines_tsv, "--out", "VO"], check=True)
            # 3. Align words (with low_resource_whisper fallback)
            try:
                subprocess.run([sys.executable, ALIGN_VO, "--vo", "VO.wav", "--lines", "VO.tsv", "--out", "WORDS.tsv", "--lang", "en", "--model", "tiny"], check=True)
            except Exception as align_err:
                print(f"⚠️ Primary alignment notice ({align_err}). Trying low_resource_whisper fallback...")
                if os.path.exists(LOW_RESOURCE_WHISPER):
                    subprocess.run([sys.executable, LOW_RESOURCE_WHISPER, "VO.wav", "--out-tsv", "WORDS.tsv"], check=True)
            print(f"✅ English voiceover complete & aligned for {sub_dir}")
        elif lang in ("ur", "roman_urdu"):
            # Check if VO.wav already placed by user / external TTS
            if os.path.exists("VO.wav") and os.path.getsize("VO.wav") > 10000:
                print(f"⏩ Existing Urdu VO.wav detected in {sub_dir}, performing alignment...")
                subprocess.run([sys.executable, ALIGN_VO, "--vo", "VO.wav", "--lines", lines_tsv, "--out", "WORDS.tsv", "--lang", "ur", "--model", "base"], check=True)
            else:
                print(f"🤖 Automating Urdu Parler Voiceover via Kaggle API runner for {sub_dir}...")
                if os.path.exists(KAGGLE_RUNNER):
                    res = subprocess.run([sys.executable, KAGGLE_RUNNER, lines_tsv, "--dir", "."], check=False)
                    if res.returncode == 0 and os.path.exists("VO.wav") and os.path.getsize("VO.wav") > 10000:
                        print(f"✅ Automated Kaggle Urdu VO complete & aligned for {sub_dir}")
                    else:
                        print(f"\n⏸️ [URDU VOICE ACTION REQUIRED]:")
                        print(f"   Kaggle credentials not configured in repo root .env or job failed.")
                        print(f"   Set KAGGLE_USERNAME and KAGGLE_KEY in /home/mirza-ahmed-hassan/Desktop/stickman-animation/.env")
                        print(f"   then resume with: python3 studio.py create --resume voice")
                        return False
                else:
                    if os.path.exists(PARLER_JOB_MAKER):
                        subprocess.run([sys.executable, PARLER_JOB_MAKER, lines_tsv, "--out", "takes"], check=True)
                    print(f"\n⏸️ [URDU VOICE ACTION REQUIRED]:")
                    print(f"   Takes script generated in {sub_dir}/takes. Place VO.wav in {sub_dir}/,")
                    print(f"   then resume with: python3 studio.py create --resume assets")
                    return False

        # 4. Intelligent Scene Synchronization & VFX Enrichment (Pillars 1 & 2)
        if os.path.exists("SCENES_HYBRID.tsv") or os.path.exists("SCENES.tsv"):
            if os.path.exists(VFX_SMART_DESIGNER):
                subprocess.run([sys.executable, VFX_SMART_DESIGNER, "."])
            if os.path.exists(ALIGN_HYBRID_SCENES):
                subprocess.run([sys.executable, ALIGN_HYBRID_SCENES, "."])
                print(f"⏱️ Time-locked scenes and overlays to spoken words in {sub_dir}")
            if os.path.exists(DIRECTOR_SUPERVISOR):
                subprocess.run([sys.executable, DIRECTOR_SUPERVISOR, "."])
        return True
    finally:
        os.chdir(cwd)


def generate_sound_mix(sub_dir):
    """Executes smart sound design with sha256/mtime cache validation (Condition 3)."""
    print(f"\n🔊 Generating Broadcast Sound Design & Mix for {sub_dir}...")
    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        
        if os.path.exists(ALIGN_HYBRID_SCENES) and os.path.exists("SCENES_HYBRID.tsv"):
            subprocess.run([sys.executable, ALIGN_HYBRID_SCENES, "."])
        if os.path.exists(DIRECTOR_SUPERVISOR) and os.path.exists("SCENES_HYBRID.tsv"):
            subprocess.run([sys.executable, DIRECTOR_SUPERVISOR, "."])
            
        cues_path = "cues_pro.tsv"
        # Validate cache freshness (Condition 3)
        need_gen = True
        try:
            import sfx_smart_designer
            if sfx_smart_designer.is_cues_cache_fresh(".", cues_path):
                need_gen = False
                print(f"⏩ Sound cues cache is fresh for {sub_dir} (sha256 verified)")
        except Exception:
            pass

        is_short = "short" in sub_dir.lower()
        if need_gen and os.path.exists(SFX_SMART_DESIGNER):
            print(f"🎵 Designing high-density smart sound cues for {sub_dir}...")
            sfx_cmd = [sys.executable, SFX_SMART_DESIGNER, "."]
            if is_short:
                sfx_cmd.append("--short")
            else:
                sfx_cmd.extend(["--outro-sec", "8.0"])
            subprocess.run(sfx_cmd, check=True)

        mix_cmd = [
            sys.executable, MIX_VO, "cues_pro.tsv",
            "--vo", "VO.wav", "--lines", "VO.tsv", "--words", "WORDS.tsv",
            "--out", "mix_pro.wav"
        ]
        if not is_short:
            mix_cmd.extend(["--outro-sec", "8.0"])
        # Auto-wire Vox Drop-Out silence dip from NARRATIVE_AUDIT.json if twist_line_id exists in VO.tsv
        na_path = "NARRATIVE_AUDIT.json"
        if os.path.exists(na_path) and os.path.exists("VO.tsv"):
            try:
                na_data = json.load(open(na_path, encoding="utf-8"))
                twist_id = str(na_data.get("twist_line_id") or "").strip()
                if twist_id:
                    vo_ids = {r.get("id", "").strip() for r in csv.DictReader(open("VO.tsv", encoding="utf-8"), delimiter="\t")}
                    if twist_id in vo_ids:
                        mix_cmd.extend(["--dip", f"@{twist_id}"])
                        print(f"🕳️ Pre-Twist Vox Drop-Out Dip armed at @{twist_id}")
            except Exception:
                pass
        subprocess.run(mix_cmd, check=True)
        print(f"✅ Broadcast mix ready for {sub_dir}: mix_pro.wav (-14.0 LUFS compliant)")
    finally:
        os.chdir(cwd)


def generate_flow_assets(sub_dir, aspect="9:16", look="bright"):
    """Generates native aspect scene shots and transparent props via Flow with deduplication."""
    print(f"\n🎨 Generating Visual Assets for {sub_dir} (Native Aspect: {aspect}, Look: {look})...")
    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        p_root = os.path.dirname(os.path.abspath(sub_dir))
        if os.path.exists(ASSET_REGISTRY):
            subprocess.run([sys.executable, ASSET_REGISTRY, p_root])
            
        # Pre-Flow Prompt & Bridge Guard
        if os.path.exists(FLOW_BRIDGE_CHECKER):
            subprocess.run([sys.executable, FLOW_BRIDGE_CHECKER], check=False)
        if os.path.exists("SHOTS.tsv") and os.path.exists(FLOW_PROMPT_AUDITOR):
            print(f"🛡️ Pre-Flow Prompt Guard: Auditing SHOTS.tsv with '{look}' style directives...")
            subprocess.run([sys.executable, FLOW_PROMPT_AUDITOR, "SHOTS.tsv", "--look", look])

        # Generate shots in target aspect
        subprocess.run([sys.executable, SMART_GEN, "shots", f"--aspect={aspect}"])
        # Generate transparent elements (auto-reuses existing mutual stickers)
        subprocess.run([sys.executable, SMART_GEN, "elements"])
        print(f"✅ Visual assets ready for {sub_dir}")
    finally:
        os.chdir(cwd)


def create_upload_package(project_root, slug, topic, look="bright", no_flow_thumb=False):
    """Generates complete YouTube & Shorts upload package in UPLOAD_PACK/ directory using 2-stage thumbnail pipeline."""
    pack_dir = os.path.join(project_root, "UPLOAD_PACK")
    os.makedirs(pack_dir, exist_ok=True)
    os.makedirs(os.path.join(project_root, "img"), exist_ok=True)
    print(f"\n📦 Building Production Upload Pack in {pack_dir} (Look: {look})...")

    # 1. Social Packaging (METADATA.json & POSTING_GUIDE.md)
    if os.path.exists(SOCIAL_PACKAGER):
        try:
            cmd = [sys.executable, SOCIAL_PACKAGER, project_root, "--look", look, "--skip-thumbs"]
            subprocess.run(cmd, check=False)
            for doc in ["METADATA.json", "POSTING_GUIDE.md"]:
                src = os.path.join(project_root, doc)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(pack_dir, doc))
        except Exception as e:
            print(f"⚠️ Social packaging notice: {e}")

    # 2. 2-Stage Intelligent Thumbnail Pipeline (Google Flow Base -> Smart Supersampled Polish)
    t16_out = os.path.join(pack_dir, "thumbnail_16x9.png")
    t9_out = os.path.join(pack_dir, "thumbnail_9x16.png")
    
    if os.path.exists(THUMBNAIL_GENERATOR):
        try:
            cmd = [
                sys.executable, THUMBNAIL_GENERATOR, project_root,
                "--look", look,
                "--out-16x9", t16_out,
                "--out-9x16", t9_out
            ]
            if no_flow_thumb:
                cmd.append("--no-flow-thumb")
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"⚠️ Thumbnail generation notice: {e}")
    
    # Also sync to root img/ for quick review
    if os.path.exists(t16_out):
        shutil.copy2(t16_out, os.path.join(project_root, "img", "thumbnail_16x9.png"))
    if os.path.exists(t9_out):
        shutil.copy2(t9_out, os.path.join(project_root, "img", "thumbnail_9x16.png"))

    print(f"✅ Upload Pack ready in {pack_dir}:")
    print(f"   • Thumbnails: 16:9 Landscape & 9:16 Shorts Cover")
    print(f"   • Raw Flow Base: thumbnail_16x9_flow_raw.png & thumbnail_9x16_flow_raw.png")
    print(f"   • Strategy: METADATA.json (SEO tags, chapters, high-CTR titles)")
    print(f"   • Checklists: POSTING_GUIDE.md (Publishing workflow & pinned comments)")


def render_pipeline_video(sub_dir, fmt="9:16", out_name=None, dry_run=False):
    """Enforces Pre-Render Quality Gate and renders MP4 video."""
    print(f"\n🎬 Rendering Final MP4 Video for {sub_dir} (Format: {fmt})...")
    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        
        # Enforce Mandatory Pre-Render Gate (Condition 2)
        if os.path.exists(VALIDATE_PIPELINE):
            import validate_pipeline
            passed = validate_pipeline.run_pre_render_gate(".", format_type=fmt)
            if not passed:
                raise RuntimeError(f"🚨 Pre-Render Quality Gate REJECTED {sub_dir}! Aborting render to prevent invalid output.")

        if dry_run:
            print(f"🔍 [DRY-RUN]: Pre-Render Gate passed for {sub_dir}. Video rendering skipped as requested.")
            return

        cmd = [
            sys.executable, RENDER_PRO,
            "--format", fmt,
            "--audio", "mix_pro.wav",
            "--scenes", "SCENES_HYBRID.tsv",
            "--words", "WORDS.tsv"
        ]
        if fmt == "16:9":
            cmd += ["--outro-sec", "8.0"]
        if out_name:
            cmd += ["--out", out_name]
        subprocess.run(cmd, check=True)
        print(f"✅ Render complete: {out_name or 'video.mp4'}")
    finally:
        os.chdir(cwd)


def main():
    parser = argparse.ArgumentParser(description="Dual-Pipeline Decoupled Production Engine")
    parser.add_argument("--topic", default="Stickman Documentary", help="Documentary topic")
    parser.add_argument("--format", choices=["short", "long", "both"], default="both", help="Production format")
    parser.add_argument("--lang", choices=["en", "ur", "roman_urdu"], default="en", help="Narration language")
    parser.add_argument("--look", default="bright", help="Visual art style preset")
    parser.add_argument("--length", default="auto", help="Target duration")
    parser.add_argument("--captions", choices=["yes", "no"], default="yes", help="Enable kinetic subtitles")
    parser.add_argument("--resume", choices=["all", "script", "voice", "assets", "render", "audit"], default="all")
    parser.add_argument("--action", default=None, help="Legacy action alias")
    parser.add_argument("--blueprint", default=None, help="Path to rich agent blueprint JSON")
    parser.add_argument("--dry-run", action="store_true", help="Run end-to-end wiring check without video render")
    parser.add_argument("--no-flow-thumb", action="store_true", help="Skip Google Flow for thumbnails, use local base")
    parser.add_argument("--out-dir", "--project-dir", dest="out_dir", default=None, help="Target project root directory")

    args = parser.parse_args()
    resume = args.action or args.resume

    target_root = args.out_dir if args.out_dir else os.getcwd()
    try:
        from anti_pollution import validate_external_output_dir
        root = validate_external_output_dir(target_root)
    except ImportError:
        root = os.path.abspath(target_root)
    slug = os.path.basename(root)

    print("==================================================")
    print(f"🚀 DUAL-PIPELINE MASTER RUNNER: {slug.upper()}")
    print(f"   Topic: '{args.topic}' | Format: {args.format} | Language: {args.lang} | Look: {args.look}")
    print("==================================================")

    # 0. Hardware Profile Diagnostic
    try:
        import low_resource_engine
        specs = low_resource_engine.get_system_specs()
        accel = low_resource_engine.get_optimal_ffmpeg_flags()
        vram = specs.get("vram_gb", 0)
        flags_str = " ".join(accel.get("flags", []))
        accel_name = "Intel VA-API" if "vaapi" in flags_str else ("Nvidia NVENC" if "nvenc" in flags_str else "CPU Multi-threaded")
        print(f"⚡ Hardware Acceleration: {accel_name} ({specs.get('threads', 4)} threads, {specs.get('ram_gb', 8):.1f}GB RAM, {vram:.1f}GB VRAM)")
    except Exception as hw_err:
        print(f"⚡ Hardware Profile: CPU mode active ({hw_err})")

    if resume == "audit":
        subprocess.run([sys.executable, EVALUATE_RL])
        return

    # 1. Setup Directories
    setup_dual_structure(root)
    if resume == "setup":
        return

    # 2. Narrative Architecture & Script Synthesis
    if resume in ("all", "script"):
        ensure_scripts_generated(root, args.topic, format_type=args.format, lang=args.lang, style=args.look, blueprint=args.blueprint)
        # Pre-Spend Gate 0: Director Plan & Continuity Audit BEFORE spending TTS / Flow compute
        if os.path.exists(DIRECTOR_SUPERVISOR):
            for branch_name in (("short", "long") if args.format == "both" else (args.format,)):
                b_dir = os.path.join(root, branch_name)
                if os.path.exists(os.path.join(b_dir, "LINES.tsv")):
                    subprocess.run([sys.executable, DIRECTOR_SUPERVISOR, b_dir, "--pre-spend", "--warn-only"], check=False)

    # 3. Short Pipeline (9:16 Vertical)
    if args.format in ("short", "both"):
        short_dir = os.path.join(root, "short")
        if os.path.exists(os.path.join(short_dir, "LINES.tsv")):
            if resume in ("all", "voice"):
                vo_ok = synthesize_voice_pipeline(short_dir, lang=args.lang, voice="am_michael", speed=1.05)
                if not vo_ok:
                    return
                generate_sound_mix(short_dir)
            if resume in ("all", "assets"):
                generate_flow_assets(short_dir, aspect="9:16", look=args.look)
                # Fix 2: Re-scan and rebuild registry after Short assets to make them immediately available for Long
                if os.path.exists(ASSET_REGISTRY):
                    subprocess.run([sys.executable, ASSET_REGISTRY, root])
            if resume in ("all", "render"):
                render_pipeline_video(short_dir, fmt="9:16", out_name=f"{slug}_short_9x16.mp4", dry_run=args.dry_run)

    # 4. Long Pipeline (16:9 Widescreen)
    if args.format in ("long", "both"):
        long_dir = os.path.join(root, "long")
        if os.path.exists(os.path.join(long_dir, "LINES.tsv")):
            if resume in ("all", "voice"):
                vo_ok = synthesize_voice_pipeline(long_dir, lang=args.lang, voice="am_michael", speed=1.0)
                if not vo_ok:
                    return
                generate_sound_mix(long_dir)
            if resume in ("all", "assets"):
                generate_flow_assets(long_dir, aspect="16:9", look=args.look)
                # Fix 2: Re-scan and rebuild registry after Long assets for full bidirectional sync
                if os.path.exists(ASSET_REGISTRY):
                    subprocess.run([sys.executable, ASSET_REGISTRY, root])
            if resume in ("all", "render"):
                render_pipeline_video(long_dir, fmt="16:9", out_name=f"{slug}_long_16x9.mp4", dry_run=args.dry_run)

    # 5. Full Reinforcement Learning Evaluation & Experience Replay
    if not args.dry_run:
        print("\n==================================================")
        print("🎯 RUNNING FULL REINFORCEMENT LEARNING AUDIT")
        print("==================================================")
        subprocess.run([sys.executable, EVALUATE_RL])

    # 6. Production Upload Packaging (Thumbnails, Guide, Metadata)
    create_upload_package(root, slug, args.topic, look=args.look, no_flow_thumb=args.no_flow_thumb)


if __name__ == "__main__":
    main()
