#!/usr/bin/env python3
"""pipeline_dual.py: Dual-Pipeline Decoupled Production Engine (Rule 22)
Orchestrates:
1. Short (9:16 Vertical, 40-60s, Viral Hook, Native 9:16 Flow Art, Channel CTA Handoff)
2. Long (16:9 Widescreen, User Duration e.g. 5m, Deep Narrative, Native 16:9 Flow Art)
3. Shared Character Continuity (img/ref_<name>.jpg)
4. Full Reinforcement Learning Quality Audit (evaluate_rl.py)
"""

import os
import sys
import time
import subprocess
import csv
import json

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

# Autonomous Zero-Setup Bootstrapper
try:
    import auto_bootstrap
    auto_bootstrap.ensure_environment()
except Exception:
    pass

VOX_SCRIPTS = os.path.abspath(os.path.join(SKILL_SCRIPTS, "../../../vox-doc-sound/scripts"))
SMART_GEN = os.path.join(SKILL_SCRIPTS, "flow_smart_generator.py")
RENDER_PRO = os.path.join(SKILL_SCRIPTS, "render_pro.py")
EVALUATE_RL = os.path.join(SKILL_SCRIPTS, "evaluate_rl.py")
SFX_SMART_DESIGNER = os.path.join(SKILL_SCRIPTS, "sfx_smart_designer.py")
KOKORO_VO = os.path.join(VOX_SCRIPTS, "kokoro_vo.py")
VO_JOIN = os.path.join(VOX_SCRIPTS, "vo_join.py")
ALIGN_VO = os.path.join(VOX_SCRIPTS, "align.py")
MIX_VO = os.path.join(VOX_SCRIPTS, "mix.py")


def setup_dual_structure(project_root):
    """Sets up decoupled sub-pipeline directories."""
    print(f"\n📂 Initializing Decoupled Dual-Pipeline Structure in {project_root}...")
    for sub in ["short", "long"]:
        d = os.path.join(project_root, sub)
        os.makedirs(os.path.join(d, "shots"), exist_ok=True)
        os.makedirs(os.path.join(d, "elements/raw"), exist_ok=True)
        os.makedirs(os.path.join(d, "elements/cut"), exist_ok=True)
        os.makedirs(os.path.join(d, "takes"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "img"), exist_ok=True)
    print("✅ Structure ready: short/ (9:16, 40-60s) and long/ (16:9, deep documentary)")


def synthesize_voice_pipeline(sub_dir, lang="a", voice="am_michael", speed=1.0):
    """Executes Kokoro voiceover synthesis, join, and faster-whisper alignment."""
    print(f"\n🎙️ Synthesizing Voiceover for {sub_dir} (Voice: {voice}, Speed: {speed:.2f}x)...")
    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        # 1. Kokoro takes
        subprocess.run([sys.executable, KOKORO_VO, "LINES.tsv", "--lang", lang, "--voice", voice, "--speed", str(speed), "--out", "takes"], check=True)
        # 2. Join takes
        subprocess.run([sys.executable, VO_JOIN, "takes", "LINES.tsv", "--out", "VO"], check=True)
        # 3. Align words
        subprocess.run([sys.executable, ALIGN_VO, "--vo", "VO.wav", "--lines", "VO.tsv", "--out", "WORDS.tsv", "--lang", "en", "--model", "tiny"], check=True)
        print(f"✅ Voiceover complete & aligned for {sub_dir}")
    finally:
        os.chdir(cwd)


def generate_sound_mix(sub_dir):
    """Executes smart sound design generation and broadcast sound mix at -14.0 LUFS."""
    print(f"\n🔊 Generating Broadcast Sound Design & Mix for {sub_dir}...")
    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        cues_path = "cues_pro.tsv"
        need_gen = True
        if os.path.exists(cues_path):
            with open(cues_path, encoding="utf-8") as cf:
                lines = [l for l in cf if l.strip() and not l.startswith("#")]
                if len(lines) >= 12:
                    need_gen = False
        if need_gen and os.path.exists(SFX_SMART_DESIGNER):
            print(f"🎵 Designing high-density smart sound cues for {sub_dir}...")
            sfx_cmd = [sys.executable, SFX_SMART_DESIGNER, "."]
            if "short" in sub_dir.lower():
                sfx_cmd.append("--short")
            subprocess.run(sfx_cmd)

        subprocess.run([
            sys.executable, MIX_VO, "cues_pro.tsv",
            "--vo", "VO.wav", "--lines", "VO.tsv", "--words", "WORDS.tsv",
            "--out", "mix_pro.wav"
        ], check=True)
        print(f"✅ Broadcast mix ready for {sub_dir}: mix_pro.wav (-14.0 LUFS compliant)")
    finally:
        os.chdir(cwd)


def generate_flow_assets(sub_dir, aspect="9:16"):
    """Generates native aspect scene shots and transparent props via Flow."""
    print(f"\n🎨 Generating Visual Assets for {sub_dir} (Native Aspect: {aspect})...")
    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        # Generate shots in target aspect
        subprocess.run([sys.executable, SMART_GEN, "shots", f"--aspect={aspect}"])
        # Generate transparent elements
        subprocess.run([sys.executable, SMART_GEN, "elements"])
        print(f"✅ Visual assets ready for {sub_dir}")
    finally:
        os.chdir(cwd)


def verify_aspect_purity(sub_dir, fmt):
    """Enforces Rule 22: Guarantees 100% native aspect Flow art without cross-pipeline contamination."""
    from PIL import Image
    shots_dir = os.path.join(sub_dir, "shots")
    if not os.path.exists(shots_dir):
        return True
    files = [f for f in os.listdir(shots_dir) if f.endswith((".png", ".jpg"))]
    for f in files:
        try:
            im = Image.open(os.path.join(shots_dir, f))
            if fmt == "9:16" and im.width > im.height * 1.15:
                raise RuntimeError(f"Rule 22 Violation in {sub_dir}: Shot {f} is landscape ({im.size}) in a 9:16 Shorts pipeline! Shorts must have dedicated 9:16 Flow art.")
            elif fmt == "16:9" and im.height > im.width * 1.15:
                raise RuntimeError(f"Rule 22 Violation in {sub_dir}: Shot {f} is vertical ({im.size}) in a 16:9 Widescreen pipeline! Long video must have dedicated 16:9 Flow art.")
        except Exception as e:
            if "Rule 22" in str(e):
                raise
    return True


def render_pipeline_video(sub_dir, fmt="9:16", out_name=None):
    """Renders final MP4 video using render_pro.py."""
    print(f"\n🎬 Rendering Final MP4 Video for {sub_dir} (Format: {fmt})...")
    verify_aspect_purity(sub_dir, fmt)
    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        cmd = [
            sys.executable, RENDER_PRO,
            "--format", fmt,
            "--audio", "mix_pro.wav",
            "--scenes", "SCENES_HYBRID.tsv",
            "--words", "WORDS.tsv"
        ]
        if out_name:
            cmd += ["--out", out_name]
        subprocess.run(cmd, check=True)
        print(f"✅ Render complete: {out_name or 'video.mp4'}")
    finally:
        os.chdir(cwd)


def main():
    root = os.getcwd()
    slug = os.path.basename(root)
    print("==================================================")
    print(f"🚀 DUAL-PIPELINE MASTER RUNNER: {slug.upper()}")
    print("==================================================")
    
    action = "all"
    if len(sys.argv) > 1:
        if sys.argv[1] in ("audit", "--audit", "qc"):
            action = "audit"
        elif sys.argv[1] in ("setup", "--setup"):
            action = "setup"
        elif sys.argv[1] in ("voice", "--voice"):
            action = "voice"
        elif sys.argv[1] in ("assets", "--assets"):
            action = "assets"
        elif sys.argv[1] in ("render", "--render"):
            action = "render"
            
    if action == "audit":
        subprocess.run([sys.executable, EVALUATE_RL])
        return

    # 1. Setup
    setup_dual_structure(root)
    if action == "setup":
        return
    
    # 2. Short Pipeline (40-60s, 9:16)
    short_dir = os.path.join(root, "short")
    if os.path.exists(os.path.join(short_dir, "LINES.tsv")):
        if action in ("all", "voice"):
            synthesize_voice_pipeline(short_dir, voice="am_michael", speed=1.05)
            if os.path.exists(os.path.join(short_dir, "cues_pro.tsv")):
                generate_sound_mix(short_dir)
        if action in ("all", "assets"):
            generate_flow_assets(short_dir, aspect="9:16")
        if action in ("all", "render"):
            render_pipeline_video(short_dir, fmt="9:16", out_name=f"{slug}_short_9x16.mp4")

    # 3. Long Pipeline (5+ min, 16:9)
    long_dir = os.path.join(root, "long")
    if os.path.exists(os.path.join(long_dir, "LINES.tsv")):
        if action in ("all", "voice"):
            synthesize_voice_pipeline(long_dir, voice="am_michael", speed=1.0)
            if os.path.exists(os.path.join(long_dir, "cues_pro.tsv")):
                generate_sound_mix(long_dir)
        if action in ("all", "assets"):
            generate_flow_assets(long_dir, aspect="16:9")
        if action in ("all", "render"):
            render_pipeline_video(long_dir, fmt="16:9", out_name=f"{slug}_long_16x9.mp4")

    # 4. Comprehensive RL-QC Quality Audit
    print("\n==================================================")
    print("🎯 RUNNING FULL REINFORCEMENT LEARNING AUDIT")
    print("==================================================")
    subprocess.run([sys.executable, EVALUATE_RL])


if __name__ == "__main__":
    main()
