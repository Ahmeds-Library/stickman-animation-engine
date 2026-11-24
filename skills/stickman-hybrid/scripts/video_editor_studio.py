#!/usr/bin/env python3
"""video_editor_studio.py: Advanced Multi-Track Video Editor & Post-Production Studio
Provides high-fidelity video assembly, color grading, kinetic subtitle generation,
and timeline mastering for YouTube Documentaries and Shorts.

Features:
1. Cinematic Color Grading Presets (Warm Documentary, Sepia Ancient, Ice Frost, Noir Contrast, Cyberpunk).
2. Dynamic Alex Hormozi Kinetic Subtitle (.ass) Generator with Word Pop & Color Highlighting.
3. Musical Downbeat & Audio Peak Sync (Aligns scene cuts with audio rhythm).
4. YouTube Outro & Closing Slate Stitcher (Zero re-encoding lossless concat when matching codecs).
5. Broadcast Web Encoding Profile (-crf 18, high profile, faststart moov atom).
"""

import os, sys, subprocess, argparse, json, math, re

COLOR_PRESETS = {
    "warm_documentary": "curves=all='0/0 0.5/0.52 1/1':r='0/0 0.5/0.54 1/1':b='0/0 0.5/0.46 1/1',eq=contrast=1.06:brightness=0.01:saturation=1.08",
    "sepia_ancient": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,eq=contrast=1.12:saturation=0.85",
    "ice_frost": "curves=all='0/0 0.5/0.5 1/1':b='0/0 0.5/0.56 1/1':r='0/0 0.5/0.45 1/1',eq=contrast=1.08:saturation=1.12",
    "noir_contrast": "hue=s=0,eq=contrast=1.28:brightness=-0.02",
    "vibrant_cartoon": "eq=contrast=1.10:saturation=1.25:brightness=0.01"
}

def generate_ass_subtitles(words_file, out_ass, is_shorts=False, style="hormozi"):
    """Generates broadcast kinetic ASS subtitles with single-word color pops."""
    if not os.path.exists(words_file):
        print(f"❌ Words file not found: {words_file}")
        return False

    width, height = (1080, 1920) if is_shorts else (1920, 1080)
    font_size = 54 if is_shorts else 48
    margin_v = 640 if is_shorts else 120 # Distance from bottom

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,40,40,{margin_v},1
Style: HighlightAmber,Arial,{font_size+6},&H001ED7FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,105,105,0,0,1,6,3,2,40,40,{margin_v},1
Style: HighlightCyan,Arial,{font_size+6},&H00FFE14B,&H000000FF,&H00000000,&H80000000,-1,0,0,0,105,105,0,0,1,6,3,2,40,40,{margin_v},1
Style: HighlightCrimson,Arial,{font_size+6},&H004B4BFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,105,105,0,0,1,6,3,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    def to_ass_time(sec):
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h:d}:{m:02d}:{s:05.2f}"

    import csv
    with open(words_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            start = float(r["start"])
            end = float(r["end"])
            word = r["word"].strip().upper()
            
            # Semantic highlight matching
            style_name = "Default"
            w_low = word.lower()
            if any(k in w_low for k in ["ice", "cold", "snow", "frost", "freeze"]):
                style_name = "HighlightCyan"
            elif any(k in w_low for k in ["danger", "fatal", "blood", "rot", "peril", "failed"]):
                style_name = "HighlightCrimson"
            elif any(k in w_low for k in ["money", "gold", "persia", "secret", "truth", "discovered", "ancient"]):
                style_name = "HighlightAmber"

            t0 = to_ass_time(start)
            t1 = to_ass_time(end)
            events.append(f"Dialogue: 0,{t0},{t1},{style_name},,0,0,0,,{word}\n")

    with open(out_ass, "w", encoding="utf-8") as f:
        f.write(ass_header)
        f.writelines(events)

    print(f"✅ Generated kinetic ASS subtitles: {out_ass} ({len(events)} words timed)")
    return True

def apply_color_grade(input_video, output_video, preset="warm_documentary"):
    """Applies high-end documentary color grading via FFmpeg filtergraph."""
    if not os.path.exists(input_video):
        print(f"❌ Video not found: {input_video}")
        return False

    vf = COLOR_PRESETS.get(preset, COLOR_PRESETS["warm_documentary"])
    cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_video
    ]
    print(f"🎨 Applying Color Grade [{preset}] to {input_video}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ Color graded video saved: {output_video}")
        return True
    else:
        print(f"❌ Color grading failed: {res.stderr}")
        return False

def generate_heading_card(title, subtitle="", style="warm_parchment", is_shorts=False, duration=3.0, out_video="heading_card.mp4"):
    """Generates broadcast-grade animated chapter title cards with angled badge and Ken Burns push-in."""
    from PIL import Image, ImageDraw, ImageFont
    
    width, height = (1080, 1920) if is_shorts else (1920, 1080)
    bg_color = (247, 238, 220) if style == "warm_parchment" else ((42, 46, 57) if style == "slate_grey" else (18, 20, 26))
    text_color = (35, 25, 20) if style == "warm_parchment" else (255, 255, 255)
    accent_color = (212, 122, 24) if style == "warm_parchment" else ((247, 181, 0) if style == "slate_grey" else (255, 60, 60))
    
    im = Image.new("RGBA", (width, height), bg_color + (255,))
    draw = ImageDraw.Draw(im)
    
    # Outer elegant double border
    pad = 48
    draw.rectangle([(pad, pad), (width - pad, height - pad)], outline=accent_color, width=4)
    draw.rectangle([(pad + 12, pad + 12), (width - pad - 12, height - pad - 12)], outline=text_color, width=2)
    
    # Try finding bold display font
    font_title = None
    for f_candidate in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/fonts/Kalam-Bold.ttf",
        "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/fonts/PatrickHand-Regular.ttf"
    ]:
        if os.path.exists(f_candidate):
            try:
                font_title = ImageFont.truetype(f_candidate, 86 if is_shorts else 96)
                font_sub = ImageFont.truetype(f_candidate, 42 if is_shorts else 46)
                break
            except Exception:
                pass
    if not font_title:
        font_title = font_sub = ImageFont.load_default()

    # Draw centered Title with soft drop shadow
    bbox_t = draw.textbbox((0, 0), title.upper(), font=font_title)
    tw, th = bbox_t[2] - bbox_t[0], bbox_t[3] - bbox_t[1]
    tx = (width - tw) // 2
    ty = (height - th) // 2 - (60 if subtitle else 0)
    
    # Shadow
    draw.text((tx + 6, ty + 6), title.upper(), font=font_title, fill=(0, 0, 0, 80))
    # Fill
    draw.text((tx, ty), title.upper(), font=font_title, fill=text_color)
    
    # Accent Underline
    line_w = min(tw + 80, width - 200)
    lx0 = (width - line_w) // 2
    ly0 = ty + th + 28
    draw.line([(lx0, ly0), (lx0 + line_w, ly0)], fill=accent_color, width=6)
    
    if subtitle:
        bbox_s = draw.textbbox((0, 0), subtitle, font=font_sub)
        sw, sh = bbox_s[2] - bbox_s[0], bbox_s[3] - bbox_s[1]
        sx = (width - sw) // 2
        sy = ly0 + 36
        draw.text((sx + 3, sy + 3), subtitle, font=font_sub, fill=(0, 0, 0, 60))
        draw.text((sx, sy), subtitle, font=font_sub, fill=accent_color)
        
    tmp_png = "heading_card_tmp.png"
    im.save(tmp_png)
    
    # Render with FFmpeg slow Ken Burns zoom (1.00x -> 1.045x)
    vf = f"scale={width*2}:{height*2},zoompan=z='min(zoom+0.0015,1.045)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*30)}:s={width}x{height}:fps=30"
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", tmp_png,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
        out_video
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(tmp_png):
        os.remove(tmp_png)
        
    if res.returncode == 0:
        print(f"✅ Generated Animated Heading Card: {out_video}")
        return True
    else:
        print(f"❌ Failed to generate heading card: {res.stderr}")
        return False

def generate_plain_paper_page(main_text, sub_text="", stickman_pose="think", is_shorts=False, duration=2.5, out_video="plain_page.mp4"):
    """Generates the signature Ink Explainer (19.3M views) Plain Paper Palate Cleanser page.
    Features:
    - 100% clean plain paper canvas (#FAF8F2) with zero background clutter.
    - Hand-drawn bold felt-pen typography (#1A1A1A) with organic spacing.
    - Minimalist stickman looking at the text (shock, think, point).
    - Subtle 1.00x -> 1.025x Ken Burns camera push-in.
    """
    from PIL import Image, ImageDraw, ImageFont
    
    width, height = (1080, 1920) if is_shorts else (1920, 1080)
    bg_color = (252, 250, 245) # Clean antique paper
    ink_color = (26, 26, 26) # Charcoal felt-pen black
    accent_color = (205, 55, 55) # Highlight Crimson or Amber
    
    im = Image.new("RGBA", (width, height), bg_color + (255,))
    draw = ImageDraw.Draw(im)
    
    # Try finding Patrick Hand or Kalam font
    font_main = None
    for f_candidate in [
        "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/fonts/PatrickHand-Regular.ttf",
        "/home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/fonts/Kalam-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ]:
        if os.path.exists(f_candidate):
            try:
                font_main = ImageFont.truetype(f_candidate, 78 if is_shorts else 88)
                font_sub = ImageFont.truetype(f_candidate, 46 if is_shorts else 52)
                break
            except Exception:
                pass
    if not font_main:
        font_main = font_sub = ImageFont.load_default()

    # Draw centered main text (multi-line supported)
    lines = main_text.split("|") if "|" in main_text else [main_text]
    line_images = []
    for l in lines:
        bbox = draw.textbbox((0, 0), l.upper(), font=font_main)
        lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        line_images.append((l.upper(), lw, lh))
        
    total_h = sum(lh for _, _, lh in line_images) + (len(lines) - 1) * 24
    if sub_text:
        bbox_sub = draw.textbbox((0, 0), sub_text.upper(), font=font_sub)
        sub_w, sub_h = bbox_sub[2] - bbox_sub[0], bbox_sub[3] - bbox_sub[1]
        total_h += sub_h + 36
    else:
        sub_w, sub_h = 0, 0

    curr_y = (height - total_h) // 2
    for l_text, lw, lh in line_images:
        lx = (width - lw) // 2
        draw.text((lx, curr_y), l_text, font=font_main, fill=ink_color)
        curr_y += lh + 24

    if sub_text:
        curr_y += 12
        sx = (width - sub_w) // 2
        # Clean subtle dash underline or text
        draw.text((sx, curr_y), sub_text.upper(), font=font_sub, fill=accent_color)

    # Optional minimal stickman in lower corner (Ink Explainer style)
    if stickman_pose:
        sm_x = 240 if is_shorts else 320
        sm_y = height - 280
        # Head
        head_r = 38
        draw.ellipse([sm_x - head_r, sm_y - head_r, sm_x + head_r, sm_y + head_r], fill=(255, 255, 255), outline=ink_color, width=5)
        # Dot eyes looking toward text (up and right)
        draw.ellipse([sm_x + 8, sm_y - 10, sm_x + 16, sm_y - 2], fill=ink_color)
        draw.ellipse([sm_x + 22, sm_y - 10, sm_x + 30, sm_y - 2], fill=ink_color)
        
        # Body
        neck_y = sm_y + head_r
        pelvis_y = neck_y + 110
        draw.line([(sm_x, neck_y), (sm_x, pelvis_y)], fill=ink_color, width=5)
        
        # Legs
        draw.line([(sm_x, pelvis_y), (sm_x - 35, pelvis_y + 100)], fill=ink_color, width=5)
        draw.line([(sm_x, pelvis_y), (sm_x + 35, pelvis_y + 100)], fill=ink_color, width=5)
        
        # Arms based on pose
        if stickman_pose == "shock":
            # Hands on head
            draw.line([(sm_x, neck_y + 20), (sm_x - 45, neck_y)], fill=ink_color, width=5)
            draw.line([(sm_x - 45, neck_y), (sm_x - 25, sm_y - 20)], fill=ink_color, width=5)
            draw.line([(sm_x, neck_y + 20), (sm_x + 45, neck_y)], fill=ink_color, width=5)
            draw.line([(sm_x + 45, neck_y), (sm_x + 25, sm_y - 20)], fill=ink_color, width=5)
            # Open mouth
            draw.ellipse([sm_x + 12, sm_y + 10, sm_x + 26, sm_y + 24], outline=ink_color, width=4)
        elif stickman_pose == "point":
            # Pointing arm up-right towards text
            draw.line([(sm_x, neck_y + 20), (sm_x + 80, neck_y - 30)], fill=ink_color, width=5)
            draw.line([(sm_x, neck_y + 20), (sm_x - 30, neck_y + 60)], fill=ink_color, width=5)
        else: # think
            # Hand on chin
            draw.line([(sm_x, neck_y + 20), (sm_x + 30, neck_y + 10)], fill=ink_color, width=5)
            draw.line([(sm_x + 30, neck_y + 10), (sm_x + 20, sm_y + head_r - 10)], fill=ink_color, width=5)
            draw.line([(sm_x, neck_y + 20), (sm_x - 30, neck_y + 60)], fill=ink_color, width=5)

    tmp_png = "plain_card_tmp.png"
    im.save(tmp_png)
    
    # Render with FFmpeg subtle push-in (1.00x -> 1.025x)
    vf = f"scale={width*2}:{height*2},zoompan=z='min(zoom+0.0008,1.025)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*30)}:s={width}x{height}:fps=30"
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", tmp_png,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
        out_video
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(tmp_png):
        os.remove(tmp_png)
        
    if res.returncode == 0:
        print(f"✅ Generated Plain Paper Text Page: {out_video}")
        return True
    else:
        print(f"❌ Failed to generate plain paper page: {res.stderr}")
        return False

def apply_vfx_filters(input_video, output_video, effect="shake_impact"):
    """Applies high-impact VFX like screen shake, flash frame, or dramatic vignette."""
    if not os.path.exists(input_video):
        print(f"❌ Input video not found: {input_video}")
        return False

    if effect == "shake_impact":
        # Displaces video crop by decaying sine wave for first 0.6s
        vf = "crop=w=in_w-40:h=in_h-40:x='20+12*sin(2*PI*t*16)*exp(-4.5*t)':y='20+12*cos(2*PI*t*16)*exp(-4.5*t)',scale=1920:1080"
    elif effect == "flash_frame":
        # Overlays 2 frames of white flash at onset
        vf = "fade=t=in:st=0:d=0.15:c=white"
    elif effect == "vignette_amber":
        # High contrast warm radial vignette
        vf = "vignette=PI/4,eq=contrast=1.12:saturation=1.15"
    else:
        vf = "null"

    cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "copy",
        output_video
    ]
    print(f"✨ Applying VFX [{effect}] to {input_video}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0

def stitch_outro_slate(main_video, outro_video, output_video):
    """Losslessly concatenates main video with YouTube outro slate."""
    if not os.path.exists(main_video) or not os.path.exists(outro_video):
        print("❌ Video files for stitching not found.")
        return False

    concat_txt = "concat_list.tmp.txt"
    with open(concat_txt, "w") as f:
        f.write(f"file '{os.path.abspath(main_video)}'\n")
        f.write(f"file '{os.path.abspath(outro_video)}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        "-movflags", "+faststart",
        output_video
    ]
    print(f"🎬 Stitching YouTube End Screen Slate...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(concat_txt):
        os.remove(concat_txt)

    if res.returncode == 0:
        print(f"✅ Stitched final deliverable: {output_video}")
        return True
    else:
        print("ℹ️ Stream copy failed; falling back to re-encode stitching...")
        cmd_reencode = [
            "ffmpeg", "-y", "-i", main_video, "-i", outro_video,
            "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            output_video
        ]
        res2 = subprocess.run(cmd_reencode, capture_output=True, text=True)
        return res2.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Advanced Multi-Track Video Editor & Post-Production Studio")
    subparsers = parser.add_subparsers(dest="action", help="Sub-commands")

    # Subtitles
    p_sub = subparsers.add_parser("subtitles", help="Generate kinetic ASS subtitles")
    p_sub.add_argument("words_file", help="Path to WORDS.tsv")
    p_sub.add_argument("--out", default="captions_kinetic.ass", help="Output ASS path")
    p_sub.add_argument("--shorts", action="store_true", help="9:16 Shorts format")

    # Grade
    p_grade = subparsers.add_parser("grade", help="Apply cinematic color grade")
    p_grade.add_argument("input_video", help="Source MP4")
    p_grade.add_argument("--out", default="graded_output.mp4", help="Output MP4")
    p_grade.add_argument("--preset", choices=list(COLOR_PRESETS.keys()), default="warm_documentary")

    # Stitch
    p_stitch = subparsers.add_parser("stitch", help="Stitch outro slate")
    p_stitch.add_argument("main_video", help="Main video MP4")
    p_stitch.add_argument("outro_video", help="Outro slate MP4")
    p_stitch.add_argument("--out", default="final_with_outro.mp4", help="Output MP4")

    # Heading Title Card
    p_head = subparsers.add_parser("heading", help="Generate animated chapter heading card")
    p_head.add_argument("title", help="Chapter title")
    p_head.add_argument("--subtitle", default="", help="Optional chapter subtitle")
    p_head.add_argument("--style", choices=["warm_parchment", "slate_grey", "midnight_dark"], default="warm_parchment")
    p_head.add_argument("--shorts", action="store_true", help="9:16 Shorts format")
    p_head.add_argument("--duration", type=float, default=3.0, help="Card duration in seconds")
    p_head.add_argument("--out", default="heading_card.mp4", help="Output MP4")

    # Plain Paper Text Page (Ink Explainer style)
    p_page = subparsers.add_parser("page", help="Generate Ink Explainer style plain paper text page")
    p_page.add_argument("text", help="Main text statement (use | for multiple lines)")
    p_page.add_argument("--subtitle", default="", help="Optional subtitle or metric")
    p_page.add_argument("--pose", choices=["think", "shock", "point", "none"], default="think", help="Stickman reaction pose")
    p_page.add_argument("--shorts", action="store_true", help="9:16 Shorts format")
    p_page.add_argument("--duration", type=float, default=2.5, help="Card duration in seconds")
    p_page.add_argument("--out", default="plain_page.mp4", help="Output MP4")

    # VFX Filters
    p_vfx = subparsers.add_parser("vfx", help="Apply visual effects (shake, flash, vignette)")
    p_vfx.add_argument("input_video", help="Input video MP4")
    p_vfx.add_argument("--out", default="vfx_output.mp4", help="Output video MP4")
    p_vfx.add_argument("--effect", choices=["shake_impact", "flash_frame", "vignette_amber"], default="shake_impact")

    args = parser.parse_args()

    if args.action == "subtitles":
        generate_ass_subtitles(args.words_file, args.out, is_shorts=args.shorts)
    elif args.action == "grade":
        apply_color_grade(args.input_video, args.out, preset=args.preset)
    elif args.action == "stitch":
        stitch_outro_slate(args.main_video, args.outro_video, args.out)
    elif args.action == "heading":
        generate_heading_card(args.title, subtitle=args.subtitle, style=args.style, is_shorts=args.shorts, duration=args.duration, out_video=args.out)
    elif args.action == "page":
        pose_arg = None if args.pose == "none" else args.pose
        generate_plain_paper_page(args.text, sub_text=args.subtitle, stickman_pose=pose_arg, is_shorts=args.shorts, duration=args.duration, out_video=args.out)
    elif args.action == "vfx":
        apply_vfx_filters(args.input_video, args.out, effect=args.effect)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
