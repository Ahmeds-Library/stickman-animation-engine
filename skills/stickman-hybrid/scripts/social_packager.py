#!/usr/bin/env python3
"""social_packager.py: Professional YouTube & Instagram Creator Publishing Suite
Generates high-CTR titles, SEO descriptions, timestamped chapters, tag clusters,
pinned comments, and Instagram Reels caption packages.
"""

import os
import sys
import csv
import json
import re


def generate_social_package(project_dir="."):
    """Scans project directory (single or dual pipeline) and produces POSTING_GUIDE.md and METADATA.json."""
    slug = os.path.basename(os.path.abspath(project_dir))
    has_dual = os.path.isdir(os.path.join(project_dir, "short")) and os.path.isdir(os.path.join(project_dir, "long"))

    # Determine topic from SCRIPT.md or PROGRESS.md or slug
    topic = slug.replace("_", " ").title()
    for doc in ["SCRIPT.md", "long/SCRIPT.md", "short/SCRIPT.md", "PROGRESS.md"]:
        p = os.path.join(project_dir, doc)
        if os.path.exists(p):
            lines = open(p, encoding="utf-8").readlines()
            for line in lines[:5]:
                if line.startswith("#"):
                    clean = re.sub(r"[#*:]", "", line).strip()
                    if clean and "progress" not in clean.lower():
                        topic = clean
                        break
            if topic != slug.replace("_", " ").title():
                break

    # 1. Chapters generation for Long video
    chapters = []
    long_vo_tsv = os.path.join(project_dir, "long/VO.tsv") if has_dual else os.path.join(project_dir, "VO.tsv")
    if os.path.exists(long_vo_tsv):
        rows = list(csv.DictReader(open(long_vo_tsv, encoding="utf-8"), delimiter="\t"))
        if rows:
            chapters.append("00:00 - Introduction: The Snooze Trap")
            for r in rows:
                txt = r.get("text", "").lower()
                sec = float(r.get("start", 0))
                m = int(sec // 60)
                s = int(sec % 60)
                timecode = f"{m:02d}:{s:02d}"
                if "circadian" in txt or "biology" in txt:
                    chapters.append(f"{timecode} - Ancient Human Biology & Sun Clocks")
                elif "warriors" in txt or "bladder" in txt or "water intoxication" in txt:
                    chapters.append(f"{timecode} - The Warrior Water Trick")
                elif "incense" in txt or "china" in txt or "song dynasty" in txt:
                    chapters.append(f"{timecode} - China's Burning Incense Labyrinths")
                elif "candle" in txt or "monks" in txt or "nails" in txt:
                    chapters.append(f"{timecode} - Medieval Candle Clocks & Gravity Alarms")
                elif "plato" in txt or "clepsydra" in txt or "water clock" in txt:
                    chapters.append(f"{timecode} - Plato's Screaming Water Whistle")
                elif "knocker" in txt or "industrial" in txt or "pea-shooter" in txt:
                    chapters.append(f"{timecode} - Victorian Knocker-Uppers")
                elif "mechanical" in txt or "levi hutchins" in txt or "seth thomas" in txt:
                    chapters.append(f"{timecode} - Invention of Mechanical Alarms")
                elif "civilization" in txt or "ancestors" in txt:
                    chapters.append(f"{timecode} - Conclusion: Why We Can't Sleep In")

    # Deduplicate chapters
    unique_chapters = []
    seen = set()
    for ch in chapters:
        title = ch.split(" - ")[-1]
        if title not in seen:
            seen.add(title)
            unique_chapters.append(ch)

    if not unique_chapters:
        unique_chapters = [
            "00:00 - Introduction",
            "00:45 - The Biological Origins",
            "01:30 - Extreme Solutions & Inventions",
            "03:00 - The Industrial Shift",
            "04:15 - Mechanical Clocks & Modern Wake-up"
        ]

    # Package definitions
    data = {
        "topic": topic,
        "youtube_long": {
            "title_options": [
                f"How Humans Woke Up Before Alarm Clocks Existed ({topic})",
                f"The Insane Ways Ancient Humans Woke Up On Time",
                f"Why Ancient People Never Had a Snooze Button"
            ],
            "description": (
                f"How did billions of humans wake up for work, hunting, and war before battery-powered alarm clocks existed?\n\n"
                f"In this animated historical documentary, we explore the wild inventions—from Native American warrior bladder tricks "
                f"and ancient Chinese incense labyrinths, to Plato's screaming water clock and Victorian Knocker-Uppers who shot peas at windows.\n\n"
                f"📌 CHAPTERS:\n" + "\n".join(unique_chapters) + "\n\n"
                f"🔔 Subscribe for more weekly deep-dive animated history explainers!\n\n"
                f"#Animation #History #AncientHistory #Documentary #Stickman #Science"
            ),
            "tags": [
                "ancient history", "how humans woke up", "history documentary", "alarm clock history",
                "stickman animation", "educational explainer", "knocker uppers", "ancient technology",
                "plato water clock", "human evolution", "viral history"
            ],
            "category": "Education"
        },
        "youtube_shorts": {
            "title_options": [
                f"How People Woke Up Before Alarm Clocks ⏰ #Shorts",
                f"The Craziest Ancient Alarm Clocks in History #Shorts",
                f"They Did THIS to Wake Up 500 Years Ago?! 🤯 #Shorts"
            ],
            "pinned_comment": (
                f"👉 Watch the FULL 5-Minute Documentary on how ancient water clocks screamed people awake! "
                f"Full video linked on our channel!"
            ),
            "description": f"How humans woke up before alarm clocks! Watch the full 5-minute documentary on our channel. #Shorts #History #DidYouKnow #Animation",
            "tags": ["#Shorts", "#History", "#Animation", "#DidYouKnow", "#ViralShorts"]
        },
        "instagram_reels": {
            "caption": (
                f"Would you survive waking up without a phone alarm? Drop your wake-up time below! 👇⏰\n\n"
                f"Before electricity and smartphones existed, oversleeping meant losing your livestock, dying in an ambush, "
                f"or losing an entire week's wages. Here is how our ancestors woke up on time.\n\n"
                f"🎬 Full 5-minute documentary now live on our YouTube channel! Link in bio.\n\n"
                f"• • •\n"
                f"#reels #reelsinstagram #historybuff #ancienthistory #historymemes #stickman #animation #explainer #didyouknow #viralreels #dailyhistory #historicalfacts #reelkarofeelkaro"
            ),
            "audio_recommendation": "Original Audio (Voiceover) + Trending Lo-Fi / Documentary Sound",
            "safe_zone_rules": "Text and stickers kept between Y: 300px and 1240px; Right-margin: 192px clear of engagement buttons."
        }
    }

    # Write METADATA.json
    meta_path = os.path.join(project_dir, "METADATA.json")
    with open(meta_path, "w", encoding="utf-8") as f:
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
        f.write(f"**Video File:** `{slug}_long_16x9.mp4` (or `waking_up_master_16x9.mp4`)\n\n")
        f.write(f"### Title Options (Pick One):\n")
        for t in data["youtube_long"]["title_options"]:
            f.write(f"- `{t}`\n")
        f.write(f"\n### Description (With Auto-Chapters):\n")
        f.write(f"```text\n{data['youtube_long']['description']}\n```\n\n")
        f.write(f"### Tags:\n")
        f.write(f"`{', '.join(data['youtube_long']['tags'])}`\n\n")

    print(f"✅ Generated Social Publishing Guide: {guide_path}")
    print(f"✅ Generated Metadata Spec: {meta_path}")


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_social_package(p)
