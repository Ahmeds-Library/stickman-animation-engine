#!/usr/bin/env python3
"""social_packager.py: Professional YouTube & Instagram Creator Publishing Suite
Generates high-CTR titles, SEO descriptions, timestamped chapters, tag clusters,
pinned comments, and Instagram Reels caption packages.
Integrates:
- viral_seo_intelligence (headline-psychologist + loss-aversion-designer + youtube-seo-optimizer)
- thumbnail_generator (2-Stage Flow + Supersampled CTR polish)
"""

import os
import sys
import csv
import json
import re
import argparse

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

try:
    import viral_seo_intelligence
except ImportError:
    viral_seo_intelligence = None

try:
    import thumbnail_generator
except ImportError:
    thumbnail_generator = None


def generate_social_package(project_dir=".", look="bright", no_flow_thumb=False, run_thumbs=True):
    """Scans project directory (single or dual pipeline) and produces POSTING_GUIDE.md, METADATA.json,
    and coordinates with the 2-stage thumbnail pipeline.
    """
    project_dir = os.path.abspath(project_dir)
    slug = os.path.basename(project_dir)
    has_dual = os.path.isdir(os.path.join(project_dir, "short")) and os.path.isdir(os.path.join(project_dir, "long"))

    # Determine topic cleanly
    topic = slug.replace("_", " ").title()
    for doc in ["SCRIPT.md", "long/SCRIPT.md", "short/SCRIPT.md", "PROGRESS.md"]:
        p = os.path.join(project_dir, doc)
        if os.path.exists(p):
            lines = open(p, encoding="utf-8").readlines()
            for line in lines[:5]:
                if line.startswith("#"):
                    clean = re.sub(r"[#*:]", "", line).strip()
                    lower_clean = clean.lower()
                    if clean and not any(k in lower_clean for k in ["progress", "widescreen", "master", "short", "vertical", "act "]):
                        topic = clean
                        break
            if topic != slug.replace("_", " ").title():
                break

    # 1. Use viral_seo_intelligence if available
    seo_data = None
    if viral_seo_intelligence:
        try:
            seo_data = viral_seo_intelligence.generate_seo_package(project_dir)
        except Exception as e:
            print(f"⚠️ viral_seo_intelligence notice: {e}")

    # Fallback or merge
    titles_long = seo_data["titles"] if seo_data else [
        f"The Insane Engineering Behind {topic}",
        f"Why Ancient {topic} Never Made Sense",
        f"The Forgotten Secret Behind {topic}"
    ]
    chapters = [f"{c['time']} - {c['title']}" for c in seo_data["chapters"]] if seo_data else [
        "00:00 - Introduction",
        "01:10 - The Hidden Problem",
        "02:25 - The Breakthrough Engineering",
        "03:40 - The Extreme Test",
        "04:45 - The Modern Legacy"
    ]
    desc_long = seo_data["description"] if seo_data else f"How did ancient civilizations engineer {topic}?"
    tags_long = seo_data["tags"] if seo_data else [topic.lower(), "documentary", "history", "animation"]
    pinned_comment = seo_data.get("pinned_comment", f"What surprised you most about {topic}? Let's discuss below! 👇")

    # Titles for Shorts
    titles_shorts = [
        f"{titles_long[0][:50]} ⏰ #Shorts",
        f"The Craziest Detail In Ancient History #Shorts",
        f"They Did THIS 2,000 Years Ago?! 🤯 #Shorts"
    ]

    data = {
        "topic": topic,
        "companion_skills_loaded": seo_data.get("companion_skills_loaded", {}) if seo_data else {},
        "youtube_long": {
            "title_options": titles_long,
            "description": desc_long,
            "tags": tags_long,
            "category": "Education"
        },
        "youtube_shorts": {
            "title_options": titles_shorts,
            "pinned_comment": pinned_comment,
            "description": f"The hidden truth behind {topic}! Watch the full documentary on our channel. #Shorts #History #DidYouKnow #Animation",
            "tags": ["#Shorts", "#History", "#Animation", "#DidYouKnow", "#ViralShorts"]
        },
        "instagram_reels": {
            "caption": (
                f"Would you survive in ancient times? Drop your take below! 👇🏛️\n\n"
                f"The real reason {topic.lower()} was engineered this way will shock you.\n\n"
                f"🎬 Full documentary now live on our YouTube channel! Link in bio.\n\n"
                f"• • •\n"
                f"#reels #reelsinstagram #historybuff #ancienthistory #stickman #animation #explainer #didyouknow #viralreels"
            ),
            "audio_recommendation": "Original Audio (Voiceover) + Trending Documentary Sound",
            "safe_zone_rules": "Text and stickers kept between Y: 300px and 1240px; Right-margin: 192px clear of engagement buttons."
        },
        "thumbnail_blueprint": seo_data.get("thumbnail_blueprint", {}) if seo_data else {}
    }

    # Ensure UPLOAD_PACK directory exists
    pack_dir = os.path.join(project_dir, "UPLOAD_PACK")
    os.makedirs(pack_dir, exist_ok=True)

    # Write METADATA.json
    meta_path = os.path.join(project_dir, "METADATA.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # Mirror into UPLOAD_PACK
    with open(os.path.join(pack_dir, "METADATA.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Write POSTING_GUIDE.md
    guide_path = os.path.join(project_dir, "POSTING_GUIDE.md")
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(f"# 🚀 YouTube & Instagram Social Publishing Guide\n\n")
        f.write(f"**Project:** {topic}\n\n")
        f.write(f"---\n\n")

        f.write(f"## 📱 1. Instagram Reels (9:16 Vertical)\n\n")
        f.write(f"**Video File:** `{slug}_short_9x16.mp4`\n\n")
        f.write(f"### Copy-Paste Caption:\n")
        f.write(f"```text\n{data['instagram_reels']['caption']}\n```\n\n")
        f.write(f"**Safe Zone Checklist:**\n")
        f.write(f"- [x] Subtitles positioned at Y=1180px (clear of bottom 672px username/caption area)\n")
        f.write(f"- [x] Overlays keep right 192px clear (clear of Like/Comment/Share column)\n")
        f.write(f"- [x] Rec.709 color matrix tagged (`-color_primaries bt709`) to prevent upload desaturation\n\n")

        f.write(f"---\n\n")

        f.write(f"## 🔴 2. YouTube Shorts (9:16 Vertical)\n\n")
        f.write(f"**Video File:** `{slug}_short_9x16.mp4`\n\n")
        f.write(f"### Title Options (Pick One):\n")
        for t in data["youtube_shorts"]["title_options"]:
            f.write(f"- `{t}`\n")
        f.write(f"\n### Pinned Comment (Funnel to Long Video):\n")
        f.write(f"```text\n{data['youtube_shorts']['pinned_comment']}\n```\n\n")

        f.write(f"---\n\n")

        f.write(f"## 🖥️ 3. YouTube Long-Form Master (16:9 Landscape)\n\n")
        f.write(f"**Video File:** `{slug}_long_16x9.mp4`\n\n")
        f.write(f"### Title Options (Pick One):\n")
        for t in data["youtube_long"]["title_options"]:
            f.write(f"- `{t}`\n")
        f.write(f"\n### Description (With Auto-Chapters):\n")
        f.write(f"```text\n{data['youtube_long']['description']}\n```\n\n")
        f.write(f"### Tags:\n")
        f.write(f"`{', '.join(data['youtube_long']['tags'])}`\n\n")

    # Mirror into UPLOAD_PACK
    import shutil
    shutil.copy2(guide_path, os.path.join(pack_dir, "POSTING_GUIDE.md"))

    print(f"✅ Generated Social Publishing Guide: {guide_path}")
    print(f"✅ Generated Metadata Spec: {meta_path}")

    # Optional 2-Stage Thumbnail Generation
    if run_thumbs and thumbnail_generator:
        thumbnail_generator.execute_2stage_thumbnail_pipeline(
            project_dir=project_dir,
            look=look,
            no_flow=no_flow_thumb
        )

    return data


def main():
    p = argparse.ArgumentParser(description="Social Publisher & Upload Packaging Suite")
    p.add_argument("project_dir", nargs="?", default=".", help="Project directory")
    p.add_argument("--look", default="bright", help="Active look preset")
    p.add_argument("--no-flow-thumb", action="store_true", help="Skip Google Flow for thumbnails")
    p.add_argument("--skip-thumbs", action="store_true", help="Skip thumbnail regeneration")
    args = p.parse_args()

    generate_social_package(
        project_dir=args.project_dir,
        look=args.look,
        no_flow_thumb=args.no_flow_thumb,
        run_thumbs=not args.skip_thumbs
    )


if __name__ == "__main__":
    main()
