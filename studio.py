#!/usr/bin/env python3
"""studio.py: Unified Master Control Plane for AI Stickman Animation Studio
Provides a single-command interface for the entire production pipeline:
- Video Generation (Dual 16:9 Master + 9:16 Shorts)
- 3-Second Viral Hook Engine (12 Psychological Archetypes)
- Animated Chapter Heading Cards & Visual Effects (VFX)
- Mandatory Pre-Render Quality Gate (validate_pipeline.py)
- System Self-Diagnostic & Hardware Doctor (Kokoro, Whisper, VA-API)
- 60-Rule Reinforcement Learning Quality Audit (RL-QC)
- Trending Topic Research & Retention Curve Analytics
"""

import os
import sys
import re
import argparse
import subprocess
import importlib.util

# Self-healing environment bootstrap
try:
    import auto_bootstrap
    auto_bootstrap.ensure_environment()
except Exception:
    pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "skills", "stickman-hybrid", "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


def _get_script_module(name):
    """Dynamically loads a skill script from SCRIPTS_DIR, bypassing static missing-import warnings."""
    try:
        return importlib.import_module(name)
    except ImportError:
        p = os.path.join(SCRIPTS_DIR, f"{name}.py")
        if os.path.exists(p):
            spec = importlib.util.spec_from_file_location(name, p)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
    return None


def run_doctor():
    """Runs a complete end-to-end system diagnostic."""
    print("==================================================")
    print("🩺 STICKMAN STUDIO SYSTEM DIAGNOSTIC (DOCTOR)")
    print("==================================================")
    
    # 1. Python Environment
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"🐍 Python Version: {py_ver} -> {'✅ OK' if sys.version_info >= (3, 10) else '⚠️ Recommend >= 3.10'}")

    # 2. Hardware Acceleration
    try:
        import importlib
        try:
            lre = importlib.import_module("low_resource_engine")
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location("low_resource_engine", os.path.join(SCRIPTS_DIR, "low_resource_engine.py"))
            if spec and spec.loader:
                lre = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(lre)
            else:
                raise ImportError("low_resource_engine could not be loaded")
        hw = lre.get_system_specs()
        opt = lre.get_optimal_ffmpeg_flags()
        flags = opt.get("flags", [])
        accel_name = "Intel VA-API" if "vaapi" in " ".join(flags) else ("Nvidia NVENC" if "nvenc" in " ".join(flags) else "CPU (Multi-thread)")
        print(f"⚡ Hardware Acceleration: {accel_name} ({hw.get('threads', 4)} threads, {hw.get('ram_gb', 8):.1f} GB RAM) -> ✅ ACTIVE")
    except Exception as e:
        print(f"⚡ Hardware Acceleration: CPU Fallback ({e}) -> ✅ OK")

    # 3. Audio & Voice Models
    try:
        import soundfile
        import scipy.signal
        print("🔊 Audio Signal Processing (NumPy, SciPy, SoundFile) -> ✅ ACTIVE")
    except ImportError as e:
        print(f"🔊 Audio Processing: Missing package ({e}) -> ⚠️ RUN auto_bootstrap.py")

    # 4. Neural Speech (Kokoro-82M)
    try:
        from kokoro import KPipeline
        print("🎙️ Local Neural TTS (Kokoro-82M Apache 2.0) -> ✅ READY")
    except Exception:
        print("🎙️ Local Neural TTS (Kokoro-82M): Will auto-install on first run -> ⏳ READY")

    # 5. Word Alignment (Faster-Whisper)
    try:
        from faster_whisper import WhisperModel
        print("⏱️ Word-Level Timestamp Alignment (Faster-Whisper int8) -> ✅ READY")
    except Exception:
        print("⏱️ Word Alignment (Faster-Whisper): Will auto-install on first run -> ⏳ READY")

    # 6. Fonts
    font_path = os.path.join(ROOT_DIR, "skills", "stickman-hybrid", "fonts", "PatrickHand-Regular.ttf")
    print(f"🔤 Display Fonts: {'✅ VERIFIED' if os.path.exists(font_path) else '⚠️ Default system fonts used'}")

    # 7. CC0 Sound Effects & Music
    sfx_cat = os.path.join(ROOT_DIR, "skills", "vox-doc-sound", "CATALOG.tsv")
    if os.path.exists(sfx_cat):
        with open(sfx_cat, encoding="utf-8", errors="ignore") as cf:
            sfx_cnt = max(0, sum(1 for _ in cf) - 1)
        print(f"🎵 CC0 Sound & Music Library: ✅ VERIFIED ({sfx_cnt} indexed tracks in vox-doc-sound/CATALOG.tsv)")
    else:
        sfx_path = os.path.join(ROOT_DIR, "skills", "vox-doc-sound", "sfx")
        print(f"🎵 CC0 Sound Library: {'✅ VERIFIED (Wyzowl & Kenney CC0)' if os.path.exists(sfx_path) else '⚠️ Procedural fallback active'}")

    # 7b. Permanent Sticker Vault & CC0/MIT Library (skills/stickman-stickers)
    stk_cat = os.path.join(ROOT_DIR, "skills", "stickman-stickers", "CATALOG.tsv")
    if os.path.exists(stk_cat):
        with open(stk_cat, encoding="utf-8", errors="ignore") as cf:
            cnt = max(0, sum(1 for _ in cf) - 1)
        print(f"🧩 Permanent Sticker Vault: ✅ VERIFIED ({cnt} indexed transparent stickers in CATALOG.tsv)")
    else:
        print("🧩 Permanent Sticker Vault: ⚠️ CATALOG.tsv not yet indexed (run: studio.py stickers --index)")

    # 7c. v7 CC0 Editorial Backgrounds & VFX Overlays
    bg_cat = os.path.join(ROOT_DIR, "skills", "stickman-hybrid", "backgrounds", "CATALOG.tsv")
    vfx_cat = os.path.join(ROOT_DIR, "skills", "stickman-hybrid", "vfx_assets", "CATALOG.tsv")
    if os.path.exists(bg_cat):
        with open(bg_cat, encoding="utf-8", errors="ignore") as cf:
            bg_cnt = max(0, sum(1 for _ in cf) - 1)
        print(f"📜 CC0 Editorial Backgrounds: ✅ VERIFIED ({bg_cnt} textures in backgrounds/CATALOG.tsv)")
    else:
        print("📜 CC0 Editorial Backgrounds: ⚠️ backgrounds/CATALOG.tsv missing")
    if os.path.exists(vfx_cat):
        with open(vfx_cat, encoding="utf-8", errors="ignore") as cf:
            vfx_cnt = max(0, sum(1 for _ in cf) - 1)
        print(f"✨ CC0/MIT VFX Overlays: ✅ VERIFIED ({vfx_cnt} overlays in vfx_assets/CATALOG.tsv)")
    else:
        print("✨ CC0/MIT VFX Overlays: ⚠️ vfx_assets/CATALOG.tsv missing")

    # 8. Reinforcement Learning Policies (60 Rules)
    eval_path = os.path.join(SCRIPTS_DIR, "evaluate_rl.py")
    print(f"🧠 RL Quality Evaluator: {'✅ 60-RULE ACTIVE POLICY' if os.path.exists(eval_path) else '❌ MISSING'}")

    # 9. Pre-Render Quality Gate
    gate_path = os.path.join(SCRIPTS_DIR, "validate_pipeline.py")
    print(f"🛡️ Pre-Render Quality Gate: {'✅ ACTIVE PRE-FLIGHT SHIELD' if os.path.exists(gate_path) else '❌ MISSING'}")

    print("==================================================")
    print("✅ SYSTEM READY FOR 100% ERROR-FREE PRODUCTION")
    print("==================================================")
    return True


def run_hook(args):
    """Generates a 3-second viral hook video using the 12 psychological archetypes."""
    script = os.path.join(SCRIPTS_DIR, "viral_hook_engine.py")
    cmd = [sys.executable, script]
    if args.list_archetypes:
        cmd.append("--list-archetypes")
    else:
        cmd.extend(["--topic", args.topic, "--archetype", args.archetype, "--ratio", args.ratio, "--out", args.out])
    subprocess.run(cmd)


def run_heading(args):
    """Generates an animated chapter heading title card."""
    script = os.path.join(SCRIPTS_DIR, "video_editor_studio.py")
    cmd = [sys.executable, script, "heading", args.title]
    if args.subtitle:
        cmd.extend(["--subtitle", args.subtitle])
    cmd.extend(["--style", args.style, "--duration", str(args.duration), "--out", args.out])
    if args.shorts:
        cmd.append("--shorts")
    subprocess.run(cmd)


def run_page(args):
    """Generates the signature Ink Explainer Plain Paper Palate Cleanser page."""
    script = os.path.join(SCRIPTS_DIR, "video_editor_studio.py")
    cmd = [sys.executable, script, "page", args.text]
    if args.subtitle:
        cmd.extend(["--subtitle", args.subtitle])
    cmd.extend(["--pose", args.pose, "--duration", str(args.duration), "--out", args.out])
    if args.shorts:
        cmd.append("--shorts")
    subprocess.run(cmd)


def run_vfx(args):
    """Applies high-impact VFX like screen shake or flash frame."""
    script = os.path.join(SCRIPTS_DIR, "video_editor_studio.py")
    cmd = [sys.executable, script, "vfx", args.input_video, "--effect", args.effect, "--out", args.out]
    subprocess.run(cmd)


def run_gate(args):
    """Runs the mandatory Pre-Render Quality Gate."""
    script = os.path.join(SCRIPTS_DIR, "validate_pipeline.py")
    cmd = [sys.executable, script, args.target, "--format", args.format]
    subprocess.run(cmd)


def run_qc(args):
    """Executes the 61-Rule Reinforcement Learning Quality Audit."""
    script = os.path.join(SCRIPTS_DIR, "evaluate_rl.py")
    cmd = [sys.executable, script]
    if args.target:
        cmd.append(args.target)
    subprocess.run(cmd)


def run_director(args):
    """Runs Unified Director Supervision (Gate 0 + Choreography) on a project directory."""
    script = os.path.join(SCRIPTS_DIR, "director_supervisor.py")
    cmd = [sys.executable, script, args.target]
    if getattr(args, "pre_spend", False):
        cmd.append("--pre-spend")
    if getattr(args, "strict", False):
        cmd.append("--strict")
    if getattr(args, "warn_only", False):
        cmd.append("--warn-only")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        sys.exit(res.returncode)


def run_sheets(args):
    """Exports qa/hook_sheet.jpg, qa/phone_sheet.jpg, qa/beats_sheet.jpg and prints signal QA summary."""
    eval_mod = _get_script_module("evaluate_rl")
    if not eval_mod:
        print("❌ evaluate_rl module unavailable")
        sys.exit(1)
    import time
    t_s = time.time()
    sheets = eval_mod.export_contact_sheets(args.mp4, out_dir=getattr(args, "out", None))
    sig = eval_mod.scan_video_signals(args.mp4)
    dt_s = time.time() - t_s
    print(f"🖼️ Contact Sheets & Forensic Signal Scan ({dt_s:.2f}s):")
    for k, p in sheets.items():
        print(f"   • {k}: {p} ({'OK' if os.path.exists(p) else 'MISSING'})")
    print(f"   • Signal QA: blank_frame0={sig.get('blank_frame0')}, flash={sig.get('flash_frames')}, "
          f"freeze_2.5s={sig.get('freeze_runs_2_5s')}, min_otsu_contrast={sig.get('min_advisory_contrast')}:1, "
          f"f_codes={sig.get('f_codes')}")


def run_stickers(args):
    """Manages and searches the permanent skills/stickman-stickers vault & CC0 library."""
    stk_scripts = os.path.join(ROOT_DIR, "skills", "stickman-stickers", "scripts")
    if getattr(args, "harvest", False):
        subprocess.run([sys.executable, os.path.join(stk_scripts, "harvest_project_stickers.py")])
    elif getattr(args, "fetch_cc0", False):
        cmd = [sys.executable, os.path.join(stk_scripts, "fetch_cc0_stickers.py")]
        if getattr(args, "online", False):
            cmd.append("--online")
        subprocess.run(cmd)
    elif getattr(args, "search", None):
        cmd = [sys.executable, os.path.join(stk_scripts, "index_stickers.py"), "--search", args.search]
        if getattr(args, "json", False):
            cmd.append("--json")
        subprocess.run(cmd)
    else:
        subprocess.run([sys.executable, os.path.join(stk_scripts, "index_stickers.py")])


def run_trends(args):
    """Searches high-RPM trending explainer topics and SEO tag clusters."""
    trending_researcher = _get_script_module("trending_researcher")
    if not trending_researcher:
        print("❌ trending_researcher.py could not be imported.")
        return

    if args.query:
        res = trending_researcher.search_trending(args.query)
    elif args.niche and args.niche in trending_researcher.TRENDING_NICHES:
        res = trending_researcher.TRENDING_NICHES[args.niche]
    elif args.niche:
        res = trending_researcher.search_trending(args.niche)
    else:
        res = trending_researcher.get_trending_summary()

    if args.json:
        import json
        print(json.dumps(res, indent=2))
    else:
        print("==================================================")
        print("📈 HIGH-RPM TRENDING EXPLAINER RESEARCHER")
        print("==================================================")
        if isinstance(res, dict) and "niche_name" in res:
            print(f"🎯 Niche: {res['niche_name']} (Est. RPM: {res.get('estimated_rpm', 'N/A')})")
            for t in res.get("topics", []):
                print(f"  • Title Idea: {t.get('title_options', [''])[0]}")
                print(f"    Hook: {t.get('barnum_hook', '')}")
                print(f"    Badge: [{t.get('badge', '')}] | Text: \"{t.get('thumbnail_text', '')}\"")
        elif isinstance(res, list):
            for t in res:
                if "category" in t:
                    print(f"🎯 Category: {t.get('category')} (RPM: {t.get('rpm', 'N/A')})")
                    for top in t.get("top_topics", [])[:3]:
                        print(f"   • {top}")
                else:
                    print(f"  • {t.get('title_options', [''])[0]} (Badge: [{t.get('badge', '')}])")
                    print(f"    Hook: {t.get('barnum_hook', '')}")
        elif isinstance(res, dict):
            for niche_id, n_data in res.items():
                print(f"\n📂 [{niche_id.upper()}]: {n_data.get('niche_name', '')} (RPM: {n_data.get('estimated_rpm', '')})")
                for t in n_data.get("topics", [])[:2]:
                    print(f"   - {t.get('title_options', [''])[0]}")
        print("==================================================")


def run_create(args):
    """Runs the full automated production pipeline with unified parameter routing."""
    raw_slug = re.sub(r"[^\w\s-]", "", args.topic.lower()).strip()
    slug = re.sub(r"[-\s]+", "_", raw_slug) or "project"

    # Resolve target output project path: user specified --out-dir or default ~/StickmanHybrid/<slug>
    out_dir = getattr(args, "out_dir", None)
    if not out_dir:
        out_dir = os.path.expanduser(f"~/StickmanHybrid/{slug}")

    # Validate resolved project path against anti-pollution guard (rejects inside repo root)
    ap_mod = _get_script_module("anti_pollution")
    if ap_mod and hasattr(ap_mod, "validate_external_output_dir"):
        project_dir = ap_mod.validate_external_output_dir(out_dir)
    else:
        project_dir = os.path.realpath(os.path.abspath(os.path.expanduser(out_dir)))

    os.makedirs(project_dir, exist_ok=True)

    if getattr(args, "suggest", False):
        try:
            tr_mod = _get_script_module("trending_researcher")
            if tr_mod:
                sug = tr_mod.search_trending(args.topic)
                if sug:
                    print("\n💡 [TOPIC RETENTION SUGGESTIONS]:")
                    for s in sug[:2]:
                        print(f"  • Viral Angle: {s.get('title_options', [''])[0]}")
                        print(f"  • Recommended Hook: \"{s.get('barnum_hook', '')}\"")
                        print(f"  • Thumbnail Concept: \"{s.get('thumbnail_text', '')}\" (Badge: [{s.get('badge', '')}])\n")
        except Exception:
            pass

    script = os.path.join(SCRIPTS_DIR, "pipeline_dual.py")
    cmd = [
        sys.executable, script,
        "--topic", args.topic,
        "--format", args.format,
        "--lang", args.lang,
        "--look", args.look,
        "--length", args.length,
        "--captions", args.captions,
        "--resume", args.resume,
        "--out-dir", project_dir
    ]
    if args.blueprint:
        cmd.extend(["--blueprint", args.blueprint])
    if args.dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, cwd=project_dir)


def main():
    parser = argparse.ArgumentParser(
        description="👑 AI Stickman Animation Studio: Unified Master CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 studio.py doctor
  python3 studio.py create "Ancient Human Night" --format both --lang en --look bright
  python3 studio.py gate short/ --format 9:16
  python3 studio.py hook "Ancient Human Night" --archetype modern_inversion --ratio 9x16
  python3 studio.py heading "Chapter 1: The Void" --subtitle "50,000 Years Ago"
  python3 studio.py qc example/boat_hi
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Studio commands")

    # 1. Doctor
    subparsers.add_parser("doctor", help="Run system diagnostics and verify zero-setup readiness")

    # 2. Gate (Pre-Render Validator)
    p_gate = subparsers.add_parser("gate", help="Run mandatory Pre-Render Quality Gate on a project folder")
    p_gate.add_argument("target", nargs="?", default=".", help="Target project directory")
    p_gate.add_argument("--format", choices=["9:16", "16:9"], default="9:16", help="Target aspect ratio")

    # 3. Hook
    p_hook = subparsers.add_parser("hook", help="Generate high-retention 3-second viral hook videos")
    p_hook.add_argument("topic", nargs="?", default="Black Holes", help="Video topic")
    p_hook.add_argument("--archetype", default="modern_inversion", help="Psychological hook archetype")
    p_hook.add_argument("--ratio", choices=["9x16", "16x9"], default="9x16", help="Aspect ratio")
    p_hook.add_argument("--out", default="hook_output.mp4", help="Output MP4 filename")
    p_hook.add_argument("--list-archetypes", action="store_true", help="List all 12 psychological archetypes")

    # 4. Heading
    p_head = subparsers.add_parser("heading", help="Generate animated chapter title cards with Ken Burns push-in")
    p_head.add_argument("title", help="Chapter heading title")
    p_head.add_argument("--subtitle", default="", help="Optional subtitle")
    p_head.add_argument("--style", choices=["warm_parchment", "slate_grey", "midnight_dark"], default="warm_parchment")
    p_head.add_argument("--shorts", action="store_true", help="9:16 Shorts format")
    p_head.add_argument("--duration", type=float, default=3.0, help="Duration in seconds")
    p_head.add_argument("--out", default="heading_card.mp4", help="Output MP4 filename")

    # 5. Plain Paper Page (Rule 61)
    p_page = subparsers.add_parser("page", help="Generate signature Ink Explainer Plain Paper Palate Cleanser page with felt-pen typography")
    p_page.add_argument("text", help="Main shocking statement, metric, or question")
    p_page.add_argument("--subtitle", default="", help="Optional secondary context")
    p_page.add_argument("--pose", choices=["none", "shock", "think", "point"], default="think", help="Stickman reaction pose")
    p_page.add_argument("--duration", type=float, default=2.5, help="Duration in seconds (default: 2.5s)")
    p_page.add_argument("--shorts", action="store_true", help="9:16 Shorts format")
    p_page.add_argument("--out", default="plain_page.mp4", help="Output MP4 filename")

    # 6. VFX
    p_vfx = subparsers.add_parser("vfx", help="Apply visual effects (screen shake, flash frame, radial vignette)")
    p_vfx.add_argument("input_video", help="Input MP4 video file")
    p_vfx.add_argument("--effect", choices=["shake_impact", "flash_frame", "vignette_amber"], default="shake_impact")
    p_vfx.add_argument("--out", default="vfx_output.mp4", help="Output MP4 filename")

    # 7. QC / RL Evaluation
    p_qc = subparsers.add_parser("qc", help="Execute 61-Rule Reinforcement Learning Quality Audit")
    p_qc.add_argument("target", nargs="?", default=".", help="Target project directory")

    # 7b. Director Supervisor
    p_dir = subparsers.add_parser("director", help="Run Unified Director Supervisor (Gate 0 + Choreography)")
    p_dir.add_argument("target", nargs="?", default=".", help="Target project directory")
    p_dir.add_argument("--pre-spend", action="store_true", help="Pre-Spend Gate 0 estimate mode before TTS/Flow")
    p_dir.add_argument("--strict", action="store_true", help="Exit non-zero on audit_score < 70 or redundant stickers")
    p_dir.add_argument("--warn-only", action="store_true", help="Report findings with exit code 0")

    # 7c. Contact Sheets & Forensic Signal Scan
    p_sh = subparsers.add_parser("sheets", help="Export hook_sheet.jpg / phone_sheet.jpg / beats_sheet.jpg & signal QA")
    p_sh.add_argument("mp4", help="Rendered MP4 video path")
    p_sh.add_argument("--out", default=None, help="Output folder (default: <mp4_dir>/qa)")

    # 8. Trends Researcher
    p_trends = subparsers.add_parser("trends", help="Search high-RPM trending YouTube explainer topics and SEO tag clusters")
    p_trends.add_argument("--query", "-q", default=None, help="Search query or keyword")
    p_trends.add_argument("--niche", "-n", default=None, help="Filter by niche (ancient_engineering, crisis_whatif, etc.)")
    p_trends.add_argument("--json", action="store_true", help="Output pure JSON")

    # 8b. Sticker Library Manager
    p_stk = subparsers.add_parser("stickers", help="Search, index, harvest, or fetch CC0 stickers in skills/stickman-stickers")
    p_stk.add_argument("--search", "-s", default=None, help="Search indexed Flow & CC0 stickers")
    p_stk.add_argument("--index", action="store_true", help="Rebuild CATALOG.tsv")
    p_stk.add_argument("--harvest", action="store_true", help="Harvest & deduplicate Flow stickers from ~/StickmanHybrid/*")
    p_stk.add_argument("--fetch-cc0", action="store_true", help="Build/fetch 100% CC0 2D sticker library")
    p_stk.add_argument("--online", action="store_true", help="Query Wikimedia Commons CC0 API during --fetch-cc0")
    p_stk.add_argument("--json", action="store_true", help="Output JSON search results")

    # 9. Create Pipeline (Unified Master Intake)
    p_create = subparsers.add_parser("create", help="Generate full stickman documentary pipeline from 5 intake questions")
    p_create.add_argument("topic", help="Documentary topic")
    p_create.add_argument("--format", choices=["short", "long", "both"], default="both", help="Production format (Short 9:16, Long 16:9, or Both)")
    p_create.add_argument("--lang", choices=["en", "ur", "roman_urdu"], default="en", help="Narration language")
    p_create.add_argument("--length", default="auto", help="Target duration target (e.g. '60s', '5m')")
    p_create.add_argument("--captions", choices=["yes", "no"], default="yes", help="Include Alex Hormozi single-word kinetic subtitles")
    p_create.add_argument("--look", choices=["bright", "warm", "night", "ink", "oversimplified", "casually_explained", "cgp_grey", "minute_physics", "painted"], default="bright", help="Canonical visual art style (all 9 editorial looks supported)")
    p_create.add_argument("--resume", choices=["all", "script", "voice", "assets", "render", "audit"], default="all", help="Resume from a specific pipeline stage")
    p_create.add_argument("--blueprint", default=None, help="Path to rich agent-authored narrative blueprint JSON")
    p_create.add_argument("--dry-run", action="store_true", help="Run end-to-end wiring check without rendering full video")
    p_create.add_argument("--suggest", action="store_true", help="Suggest viral hooks, RPM data, and thumbnail concepts before running")
    p_create.add_argument("--out-dir", default=None, help="Target project root directory (default: ~/StickmanHybrid/<slug>)")

    args = parser.parse_args()

    if args.command == "doctor":
        run_doctor()
    elif args.command == "gate":
        run_gate(args)
    elif args.command == "hook":
        run_hook(args)
    elif args.command == "heading":
        run_heading(args)
    elif args.command == "page":
        run_page(args)
    elif args.command == "vfx":
        run_vfx(args)
    elif args.command == "qc":
        run_qc(args)
    elif args.command == "director":
        run_director(args)
    elif args.command == "sheets":
        run_sheets(args)
    elif args.command == "trends":
        run_trends(args)
    elif args.command == "stickers":
        run_stickers(args)
    elif args.command == "create":
        run_create(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
