---
name: stickman-hybrid
description: Make a complete stickman documentary explainer in the HYBRID look, end to end: clean full-colour scene pictures (Google Flow, Nano Banana 2) with cut-out stickers that pop in on the spoken words, animated counters and paper collage beats, in the style of the viral "ancient humans" explainer channels. Covers setup, topic ideas, the script, the voiceover (Kokoro for English, Indic Parler with Aman on Kaggle for Urdu, Roman Urdu and regional languages), a consistent stickman cast, LaMa watermark removal, word-timed cuts, Urdu, Roman Urdu and English on-screen text, sound design and the final MP4. Use when the user says "stickman hybrid", "hybrid stickman", "stickman sticker video", "stickman hybrid start", "stickman hybrid continue", or opens the stickman-animation (stickman-hybrid) zip.
---

# Stickman documentary, hybrid look, end to end

> [!IMPORTANT]
> **MANDATORY AI AGENT INSTRUCTION**: Before generating or editing, read [AGENT_START_GUIDE.md](file:///home/mirza-ahmed-hassan/Desktop/stickman-animation/AGENT_START_GUIDE.md) and [AI_AGENT_GUIDE.md](file:///home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/AI_AGENT_GUIDE.md). Follow the 10 Golden Directives: Mutual sticker sharing across formats, Flow-only high-density generation, true vertical 9:16 prompts, tactile sound design with 3-stem mixing (un-ducked SFX), exact word sync, and strict adherence to the `boat_hi` bright aesthetic.

You make the whole video for the user. They choose the topic, language and length; you do
the rest and show them only three checkpoints: the script, the voice and the finished video.

**Talk to the user in their own language** (often Roman Urdu / Urdu), simply. Commands, file names and
file contents stay in English. Always give full absolute paths. Give a `https://` link only
when you are certain it is right (one written in these files, or one a tool printed); never
guess a URL. If unsure, give the menu path or let the tool say it.

`<skill>` means this skill's folder: `~/.claude/skills/stickman-hybrid/` (Windows:
`C:\Users\<me>\.claude\skills\stickman-hybrid\`). The companion skill **vox-doc-sound**
(`~/.claude/skills/vox-doc-sound/`) makes the voice and the sound; read its SKILL.md at
those stages.

**Before planning any video, read `<skill>/PLAYBOOK.md` fully and `<skill>/looks/README.md`.**
The Part 1 rules are what made the test films work; follow them without exception.
`<skill>/example/` holds the approved films. **`boat_hi` is the current target** (follow it first). `food` (English) and `food_hi` (Urdu / Roman Urdu, the same
pictures re-voiced) and `teeth_hybrid` are the target: their SCENES (with `+` sticker rows),
ELEMENTS, PICK/ELPICK, cues and contact sheets show it. `teeth` and `cooking` are the plain-stills
ancestors.

**This pack makes the HYBRID look by default** (PLAYBOOK §9): every film has scene pictures plus
ELEMENTS.tsv stickers, counters and a few paper collage beats. Make plain stills only if the user
asks for them.

## Every time this skill starts ("start", "continue", a topic, anything)

1. **Setup check.** Read `<skill>/SETUP_STATUS.md`. If it is missing or any required row is
   not ✅, run or resume `<skill>/SETUP.md` from the first unfinished step, then come back.
   Prerequisite: Flow Connector, set up by the user from the extension's own setup prompt.
   At setup only check `flow-auto --version`. "Extension not connected" is NOT a setup
   failure; Flow is connected at the picture stage.
2. **Find or Start the Project (Intelligent Mode Router: Edit vs. New Video)**:
   - **Check user intent first:**
     - **MODE A: EDIT / MODIFY EXISTING VIDEO (Trigger: "edit", "edit karo", "change voice", "scene 3 badlo", "pacing fix karo"):**
       - **NEVER delete, wipe, or overwrite the project folder or its assets.**
       - **NEVER ask the 5 intake questions.**
       - Open `~/StickmanHybrid/<slug>/` and inspect `PROGRESS.md`.
       - Ask the user in their language (Urdu / Roman Urdu / English) specifically what needs editing:
         1. **Script / Storyline:** Re-write specific lines or reformulate the hook.
         2. **Voice & Narration:** Re-voice specific takes with new seeds, alternative speaker timbres, or adjusted pacing.
         3. **Visual Imagery & Stickers:** Re-prompt specific shots in Flow, re-key stickers, or adjust positioning.
         4. **Audio & Sound Design:** Re-balance SFX levels, change the music bed, or tweak ducking thresholds.
         5. **Subtitles & Layout:** Change kinetic caption size, positioning, colors, or safe zones.
       - Apply surgical modifications ONLY to the targeted files and re-render only the affected sub-pipeline without destroying other assets.
     - **MODE B: NEW VIDEO (Trigger: "start", "read the file and make a stickman animation video", "nayi video", names a topic from scratch):**
       - **HARD RULE: NEVER start generating scripts, assets, or running studio.py until all 5 answers are collected.**
       - **DO NOT assume, reuse, or mix files from any previous project.** Everything starts completely from 0.
       - Ask in ONE short, structured message in the user's language (Urdu / Roman Urdu / English), with no pre-selected defaults:
         - **Topic**: Their own, or "Want me to suggest 10 viral topics?" (PLAYBOOK §1). For Urdu / Roman Urdu audiences provide bilingual titles.
         - **Language** of narration: English (Kokoro local CPU), Urdu / Roman Urdu (Indic Parler Aman on Kaggle free GPU), or any other language.
         - **Length**: Their choice (e.g. 1, 2, 5, 8 or 10 minutes, or any number).
         - **Format**:
           1) **Long (16:9 Landscape)**: Full documentary explainer (1920x1080) for YouTube / Desktop / TV.
           2) **Shorts (9:16 Vertical)**: Fast viral mobile video (1080x1920, 40-60s) for YouTube Shorts / TikTok / Reels.
           3) **Both (Dual Independent Pipelines)**: Creates TWO distinct videos on the same topic:
              - **Shorts (9:16, 40–60s):** Viral 0-3s hook, rapid 2-3s cuts, native 9:16 Flow art (generated separately in Google Flow with `--aspect 9:16`), clean uncluttered spatial layout (Rule 24: top title only in first 2.5s, scene label at y=230, kinetic subtitle at y=1180, stickers docked in upper quadrants clearing right 192px Instagram column), and a mandatory ending CTA directing viewers to the full documentary on the channel.
              - **Long-Form (16:9, user length e.g. 5m):** Deep 6-act documentary narrative, native 16:9 Flow art (generated separately in Google Flow with `--aspect 16:9`), elegant broadcast documentary lower-thirds, atmospheric soundscape.
              - **Zero Cross-Copying:** The scene backgrounds for the long and short videos are generated independently from Flow in their native aspect ratios. Never copy or pillarbox vertical images in 16:9 or letterbox 16:9 in shorts!
              - **Shared Character Identity:** Both share `img/ref_<name>.jpg` for 100% visual cast continuity.
         - **Captions (Subtitles)**:
           1) **Yes (With Captions)**: Alex Hormozi single-word kinetic subtitles (golden-amber glow on spoken word).
           2) **No (Without Captions)**: Clean cinematic aesthetic visuals without on-screen subtitles.
       - Once the user responds, create a fresh directory `~/StickmanHybrid/<slug>/` (short, lowercase, no spaces) with a clean `PROGRESS.md`. When "Both" is selected, sub-pipelines operate in `~/StickmanHybrid/<slug>/short/` and `~/StickmanHybrid/<slug>/long/`.
3. Work only inside the project folder; run every script from there.
4. After each stage update `PROGRESS.md`: stage, ✅, decisions (look, cast, voice, language,
   length), what the user approved. Then "continue" in any new chat resumes correctly.

## Stages

| # | Stage | Do | Checkpoint |
|---|---|---|---|
| 1 | Script | `SCRIPT.md` + `LINES.tsv` (PLAYBOOK §1). Urdu / Roman Urdu narration runs about 25% longer than English: write about 15% fewer words for the chosen length. Check facts on the web if available; word debated points as such | **Wait for the user's OK** |
| 2 | Look, cast, pictures: START IMMEDIATELY after the OK, in parallel with stage 3 | Choose the look by topic (`looks/`), write `STYLE.txt`, decide the cast. Also write `ELEMENTS.tsv` (PLAYBOOK §9) and run `pictures.py elements 1 <a pose>` as the sticker test, then the rest. Connect Flow: `flow-auto bridge start` in the background, then `flow-auto doctor --site flow` (relay its words if a line fails; never write your own Flow URL). Make the character sheet, then `pictures.py refs`. Write `SHOTS.tsv` from the script (PLAYBOOK §3). `pictures.py submit` 2 test shots, look at them, then submit the rest, and start `delama.py --watch` in the background (LaMa cleans each picture as it arrives) | One line: "look X, N pictures generating while the voice is made" |
| 3 | Voice: same turn as stage 2 | vox-doc-sound. **Voice rule:** Urdu, Roman Urdu or regional language → **Indic Parler-TTS** on Kaggle (`kaggle/make_parler_job.py`), never Kokoro; for Urdu and Roman Urdu the first take is **always speaker Aman**. English and other languages → Kokoro. The user's own ElevenLabs key or recording only if they ask. Then `vo_join.py`, then `align.py --lang <code>` gives `WORDS.tsv` | Play 2 lines; the user approves Aman or asks for another speaker (Kabir, Bhanu, Dinesh, Aakash) |
| 4 | Scenes | `SCENES.tsv` on the words (PLAYBOOK §5, §9), then `render.py --pacing` and fix EVERY long hold with a beat the line names (cut, sticker, counter, tag, a "no" sticker) | A short table: line → what is on screen (no approval wait) |
| 5 | Collect pictures | When the queue is empty: re-submit refused ids once. `pictures.py review` → look → `PICK.tsv` for swaps → regenerate wrong ones → `pictures.py pick` → `delama.py` (copies the LaMa-cleaned pictures; instant) | One line: "N pictures in, fixed X" |
| 6 | Sound | vox-doc-sound: `cues.tsv` on words (PLAYBOOK §7), then `mix.py ... --out mix.wav` | Loudness numbers |
| 7 | Render + QC | `render_pro.py` (or `render.py`) with `--format 16:9 / 9:16` and `--captions / --no-captions`. Deduplicates on-screen labels automatically, ensures cutouts never block center focal points, and renders single-word kinetic pop subtitles. Automatically executes Broadcast VFX (camera shake, black-and-white flashbacks, crimson hazard vignettes, cyan frost vignettes) and attaches official YouTube End Screen slates (16:9) or Shorts subscribe callouts (9:16). Then test still frames via `--frame <T> --frame-out <path>` to QC without video encoding. Then `pictures.py qc` and read `qc.jpg` YOURSELF: wrong picture, tag over a face, sheet line-ups, leftover sparkle. Fix, re-render. Do not show the contact sheet to the user | Open the video for the user and give its full path. **They judge the final video** |
| 8 | Thumbnails & SEO | **2-Stage Intelligent Thumbnail Pipeline**: Stage 1 (`flow_thumbnail_generator.py`) generates dedicated 16:9 and native 9:16 Flow hero artwork (`thumbnail_16x9_flow_raw.png`, `thumbnail_9x16_flow_raw.png`) with strict NO-TEXT enforcement, negative space preservation, look palette alignment, and graceful high-contrast fallback. Stage 2 (`thumbnail_generator.py`) executes spatial negative-space solving (strictly avoiding 16:9 bottom-right timestamp and 9:16 mobile UI zones), 2x supersampled (`LANCZOS`) vector text rendering with curated fonts (`PermanentMarker-Regular.ttf`, `Bangers-Regular.ttf`, `Caveat-Bold.ttf`), auto-contrast luminance guard (ink pill / deep comic shadow), and look vignettes (`thumbnail_16x9.png`, `thumbnail_9x16.png`). `social_packager.py` and `viral_seo_intelligence.py` generate complete metadata (`METADATA.json`), publishing guides (`POSTING_GUIDE.md`), and high-CTR titles | Deliver clickable thumbnail PNG paths, raw flow base paths, and ready-to-paste YouTube title/description/tags metadata |

**Never run the voice first and the pictures later.** The pictures depend only on the
script's words; start them in the same turn the script is approved (users noticed and
objected when this was done in sequence).

## Rules that are easy to forget

- **Voice:** Urdu, Roman Urdu and regional languages are voiced with Indic Parler-TTS (Kaggle), never Kokoro, whose Urdu sounds flat. Urdu and Roman Urdu start with speaker **Aman**; offer Kabir, Bhanu, Dinesh or Aakash only if the user wants a change (Rohit sounds robotic). English and other languages use Kokoro at normal 1.0x standard speed (`kokoro_vo.py --speed 1.0` for Long documentary 2.2–2.6 words/s, or `--speed 1.05` for Shorts 2.6–3.2 words/s), with native English punctuation cadence (Rule 19), avoiding artificial slow-downs or excessive gaps. Parler uses make_parler_job.py's defaults (`natural` description, seed 11) and is NEVER sped up: no `--tempo`, ever (1.10x made Urdu robotic). vo_join adds natural pauses (+0.10s English, +0.20s regional); a line it flags `RE-MAKE` is voiced again with another seed. Counter sounds go on the same word as the counter's `+cue`.
- **Never swap in another voice engine on your own** (Edge/Azure voices such as Madhur,
  Google TTS, Piper, MMS, gTTS), not even "temporarily". The user did not choose it, the film
  would need re-timing, and those licences are not cleared for this pack.
- **Where Parler runs is the user's decision.**
  - SETUP Step 0 records the machine as strong (an NVIDIA GPU with ≥ 8 GB VRAM, or ≥ 16 GB
    RAM) or weak. Kaggle is the default either way.
  - If the Kaggle job is QUEUED, or the user would rather run it locally, follow PLAYBOOK §4
    "Kaggle queue": stop and ASK, with the options and their honest cost on THIS machine.
  - Do what the user picks. Never decide alone.
- Scene pictures are full, natural scenes (leave SHOTS `space` empty). Stickers go to the picture's quiet
  spots (`auto`) or onto plain collage cards; never spoil a scene for a sticker.
  On-screen text only on beat/question cards and collage cards (English), never on scene pictures.
  Urdu / Roman Urdu emphasis comes from short punch lines ending in "!" with ONE doc voice for all lines; per-line
  styles made the voice robotic (vox-doc-sound 2b).
- Scene pictures stay still. Motion comes only from stickers, counters and tags popping on the spoken
  words (PLAYBOOK §9). A new picture every ~2-3 s, more often in the hook. No zooms, no AI video.
- Pictures and stickers use Nano Banana 2 (Flow shows it as "Nano Banana 2.1"), never Pro: `pictures.py`
  already does this.
- Two stickers must never overlap; render.py separates them. Pin a sticker that sits near a face.
- A sticker only for a thing the line NAMES that the picture does NOT already show. No repeats of the
  picture, no decorations. If none fits, use a cut to a relevant picture.
- Flow swaps files between the scene and sticker folders too: check both `review.jpg` and
  `cutouts.jpg` before picking.
- Every picture is a full-colour scene in the chosen look. Test 2 shots before the batch.
- **Absolute Style Consistency & Zero Style Mixing (Cartoon & Stickman Purity - Rule 20):** If the video look is chosen as 2D cartoon/stickman, 100% of all visual assets (scenes, character poses, prop cutouts, cards, vertical shorts) must strictly adhere to that exact 2D cartoon style. Never allow a single frame, background, or prop to drift into photorealism, 3D CGI, glossy digital gradients, or realistic human depiction. Every human character across all scenes must have stickman anatomy (clean round white head, dot eyes, simple ink mouth, thin stick limbs). Every prop sticker must have matching 2D dark ink outlines and painterly textures. Every prompt must inherit `STYLE.txt` and append the Universal Negative Prompt.
- **Full-Bleed Zero-Crop Artwork Scaling (Rule 21):** Google Flow provides native high-resolution images ($1536 \times 2752$ for 9:16 and $2752 \times 1536$ for 16:9). All native images must be scaled 100% direct without ANY cropping or edge slicing (`render_pro.py`). Zoom-in Ken Burns camera drift is strictly opt-in (`--kenburns`).
- **Dual Independent Pipelines for Format "Both" (Rule 22):** When the user selects "Both", NEVER letterbox, crop, or copy assets between pipelines. Run two decoupled pipelines on the same topic:
  1. **Shorts (9:16, 40–60s):** Viral 0–3s scroll-stopping hook, rapid 1.8–2.8s cuts, dedicated native 9:16 vertical Flow art ($1536 \times 2752$), punchy voice (2.6–3.2 w/s), and a mandatory closing CTA directing viewers to the full documentary on the channel.
  2. **Long-Form (16:9, user length e.g. 5m):** 6-Act deep documentary narrative, dedicated native 16:9 widescreen Flow art ($2752 \times 1536$), calm documentary voice (2.2–2.6 w/s), and atmospheric soundscape (-14 LUFS). Zero cross-copying of vertical images into 16:9 long form.
  3. **Shared Cast Continuity:** Both share `img/ref_<name>.jpg` so character visual identity is 100% consistent.
- **Surgical Edit Mode & Asset Preservation (Rule 23):** When the user commands "edit" / "edit karo", NEVER delete project folders, wipe existing assets, or prompt the 5 intake questions. Inspect `PROGRESS.md`, ask the user what needs editing (Script, Voice pace/speaker, Scene visuals, Sound FX, Formatting/Captions), and apply surgical modifications only to the targeted files without destroying unaffected assets.
- **Spatial Hierarchy & Clutter-Free Layout Standard (Rule 24):**
  1. **Shorts (9:16) & Multi-Sticker Composition:** Title banner shown ONLY during first 2.5s ($y \in [190, 250]$), auto-fading out. Right 220px margin preserved ($x \le 860$) and bottom 660px ($y > 1250$) kept clear; kinetic single-word subtitles at $y = 1180$. Unlimited simultaneous multi-stickers (1–4+ props) are supported via `calculate_intelligent_sticker_anchor` across distinct negative-space slots with $\ge 32\text{px}$ inter-sticker padding, locked spawn-time anchors, automatic cohort scaling (`0.83x` at 3 props, `0.78x` at 4+), and $\ge 140\text{px}$ buffer above subtitles.
  2. **Long Video (16:9) & 3-Tier Sticker Vault:** Topic/chapter slug at Top-Left ($x \approx 140, y \approx 100$), subtitles at $y = 920-940$, stickers cleanly docked with $\ge 80\text{px}$ subtitle buffer. Resolve stickers via `skills/stickman-stickers/` (Tier 1 `flow_vault/` -> Tier 2 `cc0_library/` -> Tier 3 Live Flow auto-harvest).
- **Screen Heading Suppression & Zero-Clutter Standard (Rule 25):**
  1. **Zero Redundant Headings on Standard Scenes:** Floating scene heading pills (`draw_label` scene pills) and top title banners must NOT be rendered over normal background illustrations (`shots/*.png`) when animated stickers or kinetic subtitles are active (`render_pro.py --scene-labels=False --header=False`).
  2. **Elimination of "Slide Show" Clutter:** When an animated sticker pops up with its own clean label and single-word subtitles flash at the bottom, an extra heading banner ("THE MODERN HUM", "BEFORE FRIDGES", "DESERT ICE") creates visual confusion and makes the video feel like a slide presentation rather than a professional cinematic animation.
  3. **Title Card Exception:** Text headings are permitted ONLY on dedicated full-screen chapter splash cards (`img == "card"`), where the screen is intentionally cleared of character action to announce a major structural transition.
  4. **Pristine Triad Hierarchy:** Normal scenes must feature only three visual layers: (1) Full-bleed 2D stickman background illustration, (2) Clean transparent animated sticker props popping on cue, and (3) Alex Hormozi golden-amber single-word kinetic subtitles docked safely at the bottom.
- **Calm, Clause-Locked Documentary Pacing & Real Shot Diversity (Rule 26):**
  1. **Shorts (9:16 Standard):** Target **2.5s–4.0s** per complete spoken clause (min **1.8s**; max **4.2s**; chaotic `< 1.5s` rapid flickering rejected). Requires **15–20 unique Flow shots** (`A -> B -> C` linear progression; never ping-pong back to old shots).
  2. **Long Documentary (16:9 Standard):** Target **3.5s–5.5s** per clause (min **2.2s**; max **6.5s**; chaotic `< 1.5s` rapid flickering rejected). Requires **50–70 unique Flow shots**.
  3. **Full-Bleed Editorial Archetypes & Logical Stickers:** `card_stat`, `split_compare` (progressive Left $\to$ Right reveal), `bar_timeline`, and `stat_pie` render full-bleed onto the canvas without corporate UI banners or nested boxes. Stickers hold $\ge 2.5\text{s}$ cleanly on exact spoken nouns and are banned when redundant with the underlying shot.
  4. **RL-QC Verification:** `evaluate_rl.py` and `validate_pipeline.py` (Gate 6) strictly reject both dead stagnation and chaotic `< 1.5s` flickering, fake shot recycling, and sparse/broken card or split layouts.
- **Multi-Layered Sound Design & Warm Cinematic Balance (Rule 27):**
  1. **Closed-Loop Adaptive Mixing (`mix.py`):** Warm documentary music bed maintained at **-11.0 dB to -13.0 dB** relative to Voice RMS (`0.0s` smooth start, vocal pocket EQ `-3.2 dB @ 1.8 kHz`, gentle `1.9:1` sidechain ducking).
  2. **Four Tactile Audio Layers (`sfx_smart_designer.py`):** Scene swishes, logical sticker pops (`-4.5 dB` to `-2.0 dB` rel to VO), restrained dramatic keyword impacts, and normalized `-14.0 LUFS` / `-1.0 dBTP` master.
- **Restrained Emotion & Smooth VFX Standard (Rule 28):**
  1. **Smooth Transitions:** Calm narrative cuts use clean **0.22s crossfades** (`_smooth_shot_motion` calm `1.00 -> 1.045` drift); `zoom_punch`, `shake`, `danger`, `ice`, and `bw` trigger strictly on authentic high-emotion twists or catastrophe beats—never randomly mid-sentence.
  2. **Director-Supervised Motion & Animated Choreography (`director_supervisor.py` -> `DIRECTOR_PLAN.json`):** Rejects redundant stickers, binds every prop cleanly to its `WORDS.tsv` trigger at `-0.06s`, and drives 6 physics motion archetypes (`slide_arc_left`/`right`, `drop_weight`, `peel_reveal`, `bloom_focus`, `swing_strike`), group formations (`duo_converge`, `cause_effect` with animated trim-path Bezier arrows, `trio_cascade`, `quad_showcase`), alive idle breathing (`±3.2px`), clean `0.22s` ease-out exit, and physics-matched SFX (`sfx_smart_designer.py`).
- **Dynamic Sticker Lifetime & Clean Exit Standard (Rule 29):**
  1. **Word-Onset Synchronization:** Stickers must appear precisely when the spoken noun hits (`-0.05s` to `+0.05s` around `words_map["@<line>:<keyword>"]`). Never trigger stickers prematurely before the narrator speaks the object.
  2. **Clean Thought-Bound Duration:** Hold stickers cleanly until the thought finishes (**minimum `2.5s`** in Shorts and **`3.0s`** in Long videos unless pre-empted by a new scene/beat).
  3. **Smooth Exit Animation:** During the final **0.25s** of its lifespan, the sticker eases out smoothly with the scene (`render_pro.py`), zero jarring snap or flicker.
- **Viral Engagement, Barnum Effect & Trending Edits Architecture (Rule 30):**
  1. **The Barnum Hook Standard:** Hook the viewer within the first 3 seconds using universal personal relatability ("You do this every morning...", "If you think you understand X, you're missing the terrifying truth...", "Every single human alive relies on this secret...").
  2. **Zeigarnik Open Loops:** Plant an unanswered mystery or contradiction in the hook that is only resolved in the second half of the video.
  3. **Trending Semantic Subtitle Color Highlighting:** Alex Hormozi single-word subtitles must dynamically accent keywords:
     - **Green (`#48EB78`):** Money, wealth, profit, survival, victory, fresh dates, food.
     - **Red (`#FF4B4B`):** Danger, rot, bacteria, peril, war, starvation, blackout, fatal.
     - **Cyan (`#4BE1FF`):** Ice, cold, freezing, snow, frost, physics, vacuum, space, science.
     - **Golden Amber (`#FFD71E`):** Core historical and conceptual keywords.
- **100% Monetization & Copyright-Free Safe Standard (Rule 31):**
  1. **YouTube Partner Program (YPP) Compliance:** Every asset in the production must be 100% cleared for commercial monetization with zero risk of Content ID claims or copyright strikes:
     - **Visuals:** 100% original generative 2D stickman art from Google Flow prompts.
     - **Music:** Exclusively 100% CC0 Public Domain instrumentals (`music/CC0_PublicDomain/`) or original AI Lyria stems (`music/Gemini/`). Never use commercial or copyrighted audio.
     - **SFX:** Exclusively CC0 Public Domain (`Kenney_CC0`) and licensed Foley (`StableAudio`).
     - **Narration:** Permissive Apache 2.0 open-weights models (Kokoro-82M / Indic Parler-TTS). No unauthorized celebrity or commercial voice clones.
     - **Typography:** Open-source Google / OFL fonts only (e.g. Luckiest Guy, Bangers, Montserrat).
  2. **Broadcast Quality Lock:** Integrated loudness strictly calibrated to **-14.0 LUFS** with true peak $\le -1.0\text{ dBFS}$ to pass algorithmic platform audio quality thresholds without clipping distortion.
- **Broadcast Dynamic VFX Suite (Rule 32):**
  1. **Dynamic Camera Shake & Tension Rumble:** Keyword impact shake on catastrophe words ("EXPLOSION", "DANGER", "FREEZING") and scene `extra` tags (`shake` $\pm 12\text{px}$, `rumble` $\pm 2.8\text{px}$).
  2. **Grayscale / Flashback (`bw`, `grayscale`):** Instant 92% desaturation with high-contrast ink tinting for historical or retrospective flashbacks.
  3. **Crimson Hazard Vignette (`blood`, `danger`, `hazard`):** Dynamic 1.2 Hz pulsating crimson red perimeter gradient for moments of extreme biological/physical peril.
  4. **Cyan Frost Vignette (`ice`, `frost`, `cold`):** Electric blue/cyan crystalline border vignetting for freezing temperatures or extreme climate.
  5. **Kinetic Punch Zoom (`zoom_punch`):** Dynamic snap zoom (.06\times \rightarrow 1.00\times$) in the opening 0.22s of critical scenes.
- **High-Converting YouTube Outro & Closing Slate Standard (Rule 33):**
  1. **Long-Form 16:9 End Screen Slate:** Rendered on `img == "outro"` or during the final 12s of the video. Displays YouTube-compliant safe zone boxes for "Watch Next" (10 \times 344\text{px}$ at =120, y=250$), "Best for You" (10 \times 344\text{px}$ at =1190, y=250$), and center subscribe bubble (=88\text{px}$ at =960, y=422$) with animated waving stickman.
  2. **Shorts 9:16 Seamless Loop & Follow Callout:** Bottom safe zone (=1550$) displays floating animated golden-amber pill `[ 🔔 SUBSCRIBE FOR MORE ]` during final 3.5s while narration loops cleanly back to opening beat.
- **Trending Topic Research & High-RPM SEO Engine (Rule 34):**
  1. Run `trending_researcher.py` to identify viral, evergreen topics in 2 - 8 RPM niches (Ancient High-Tech, Catastrophic What-Ifs, Hidden Biology, Dark Money).
  2. Generates 3 CTR-optimized title variations, Barnum opening hooks, SEO tag clusters, and thumbnail badges.
- **High-CTR Viral Thumbnail Generator (Rule 35):**
  1. Run `thumbnail_generator.py --project-dir <path>` to generate both 16:9 (`1280x720`) and 9:16 (`1080x1920`) thumbnails.
  2. Enforces the 3-element rule: Expressive Stickman, Glowing Hero Prop, and Bold -3.5° Tilted Curiosity Text with $\ge 14\text{px}$ dark outline and drop shadow.
- **Continuous Reinforcement Learning & Self-Correction Hub (Rule 36):**
  1. `evaluate_rl.py` automatically logs every generation run to `rl_memory.py` (`rl_feedback_memory.json`).
  2. Tracks quantitative metrics (LUFS, pacing, safe-zone clearance, SFX density) and qualitative user feedback to auto-calibrate future generation weights without manual intervention.
- **Daily Viral Trends & Production Intelligence (Rule 37):**
  1. `trend_updater.py` maintains live viral intelligence across 4 pillars: high-converting audio (sub-thud, vinyl rewind, bubble pops), dynamic broadcast VFX (shake, rumble, vignettes), trending aesthetics (storybook ink, ancient blueprint, minimal vector), and viral hook formulas (Barnum paradox, 72-hour countdown).
- **Intelligent Google Flow Prompt Auditor & Negative Suite (Rule 38):**
  1. `flow_prompt_auditor.py` audits every prompt before submission to Google Flow.
  2. Injects multi-layered negative prompts (`NEGATIVE_STICKMAN`, `NEGATIVE_CLEANLINESS`, `NEGATIVE_ERA_ANCIENT`, `NEGATIVE_CHROMA_STICKER`), enforces 2D stickman anatomy, enforces spatial docking margins (left/right 40%), and auto-sanitizes policy filter trigger words.
- **Flow-Powered Thumbnail Generator with Computer Vision Analysis (Rule 39):**
  1. `flow_thumbnail_generator.py` crafts dedicated dramatic thumbnail prompts for Google Flow and runs a 4-pillar computer vision audit on the generated base image.
  2. If elements are already optimal, it leaves them untouched; if missing, it auto-composites the expressive stickman, glowing hero prop (24px radial glow), adaptive dark gradient scrim, and bold -3.5° tilted curiosity text.
- **AI Narrative & Emotional Arc Director (Rule 40):**
  1. `narrative_intelligence.py` parses script lines into the 6-Act YouTube Retention Tension Curve (Hook Paradox $\rightarrow$ Historical Struggle $\rightarrow$ Mechanical Breakthrough $\rightarrow$ Crisis Peril $\rightarrow$ Twist Revelation $\rightarrow$ Philosophical Return).
  2. Identifies the pivotal twist line and orchestrates **The Vox Drop-Out** (0.8s - 1.2s complete musical silence before the twist reveal).
  3. Directs 60Hz resonant sub-bass impacts on statistical and historical turning points.
  4. Dynamically guides visual VFX (flash blooms, camera shake, rumble, monochrome flashbacks) to match emotional arousal.
- **The 4–7 Second Pattern Interrupt Standard (Rule 41):**
  1. Prevents viewer dopamine dropoff by guaranteeing a visual or acoustic pattern interrupt every 2.4s–4.0s (scene cuts, transparent sticker pop on spoken word, camera shake, punch zoom snap).
  2. For visual holds exceeding 3.0s, `render_pro.py` automatically applies a subtle, cinematic slow push-in ($1.00\times \rightarrow 1.045\times$ over 4.0s) to keep frames dynamic without jarring distraction.
- **Visual Metaphor Entropy Standard (Rule 42):**
  1. Inspired by Vox and Kurzgesagt documentary editing, the visual metaphor must evolve every 2.5s–4.5s. Consecutive scenes avoid reusing the same visual composition.
  2. Alternates between 4 distinct visual states: (A) Character + Context Prop interaction, (B) Infographic / Diagrammatic Map, (C) Cinematic Close-up with Focal Vignette, and (D) Expressive Stickman Reaction.
- **Kurzgesagt Auditory Highlighter Pen Architecture (Rule 43):**
  1. Micro-sound effects act as acoustic highlighters: spoken numbers, percentages, dates, and historical shifts are automatically punctuated with tactile micro-SFX (bubble pops, digital blips, parchment slides, typewriter ticks) at calibrated -22 dB.
  2. Implemented via `sfx_smart_designer.py` scanning `WORDS.tsv` with an anti-clashing guard (min 2.8s between micro-highlights) to keep the mix crisp and immersive.
- **Curiosity Architecture & Open-Loop Retention Engine (Rule 44):**
  1. Implements George Loewenstein's *Information Gap Theory* and the psychological *Zeigarnik Effect*.
  2. Act 1 (0–15s) opens a high-arousal Macro Curiosity Loop (an unresolved paradoxical premise).
  3. Chain-link Micro-Loop bridges are deployed every 45–75s ("That discovery should have solved everything... but it revealed an even stranger flaw"), keeping the brain in constant task-tension until the climax.
  4. Audited by `curiosity_engine.py`, guaranteeing a retention score $\ge 85/100$ and zero retention cliffs.
- **High-CTR 3-Element Thumbnail & Mobile 140px Readability Standard (Rule 45):**
  1. Thumbnails strictly enforce the 3-Element Constraint: (1) Hero Stickman (45–55% height), (2) Glowing Hero Context Prop (25–30%), and (3) Bold -3.5° Tilted Curiosity Text Hook ($\le 3$ words).
  2. Low-contrast dark radial vignette background ensures foreground elements pop instantly.
  3. Every thumbnail must pass the Mobile Test: clear legibility and instant silhouette recognition when downscaled to 140px mobile feed dimensions.
- **Integrated Companion Skills Ecosystem:**
  The stickman animation suite incorporates specialized companion intelligence from:
  - `skills/youtube-seo-optimizer`: Search intent keyword clustering, high-RPM metadata, and chaptering.
  - `skills/emotional-arc-designer`: Affective sequence mapping and peak-end moment placement.
  - `skills/visual-emotion-engineer`: Arousal-valence visual design and contrast hierarchy.
  - `skills/headline-psychologist`: Loewenstein prediction error headlines and self-relevance triggers.
  - `skills/loss-aversion-designer`: Credible downside consequence framing.
  - `skills/data-storytelling`: Data/Narrative/Visual 3-pillar narrative progression.
  - `skills/viral-generator-builder`: Screenshot-tested virality formulas and high-shareability identity hooks.
- **100% Working 3-Second Viral Hook Engine & Procedural Auditory Shock Suite (Rule 46):**
  1. `viral_hook_engine.py` implements the battle-tested 2025/2026 YouTube Shorts / Reels / TikTok **3-Second A-E-T Hook Architecture**:
     - **A (Attention Spike, 0–1s):** Procedural frame-0 sub-bass boom (50Hz exponential decay sine) + whoosh riser + radial speedlines to halt thumb scrolling with zero dead air.
     - **E (Emotional Anchor, 1–2s):** 6 Psychological Archetypes (`barnum`, `counter_intuitive`, `paradox`, `transformation`, `forbidden`, `warning`) that create irresistible curiosity gaps.
     - **T (Tease the Outcome, 2–3s):** Open-loop cliffhanger that demands completion to achieve >80% APV (Average Percentage Viewed).
  2. **Zero External Audio Dependency:** Procedural sound synthesis via NumPy & SciPy generates cinematic sub-drops, tension sweeps, and tactile word pop transients mathematically.
  3. **Hormozi-Style Kinetic Typography:** Generates high-contrast glowing pill badges (`#FFE500` yellow, `#00F0FF` cyan, `#FF0055` crimson) with word-by-word active scale punch and millisecond alignment via `faster-whisper`.
  4. **Expressive Stickman Vector Animation:** Renders responsive vector characters in 4 distinct emotional shock poses (`shock`, `warning`, `mystery`, `intense`) with dynamic $1.00\times \rightarrow 1.18\times$ camera push-in.
  5. **Hardware-Accelerated Output:** Compiles 9:16 vertical (1080x1920) or 16:9 landscape (1920x1080) MP4s in seconds using Intel VA-API (`h264_vaapi`) with zero CPU overload.
  6. **CLI Command:**
     ```bash
     python3 scripts/viral_hook_engine.py --topic "Your Topic" --archetype paradox --ratio 9x16 --out hook.mp4
     python3 scripts/viral_hook_engine.py --list-archetypes
     ```
- **Psychoacoustic Sound Layering, J-Cuts & Tactile Synesthesia (Rule 47):**
  1. **Audio Pre-Lapping (J-Cuts):** Scene transition whooshes lead by 120ms; sticker entrance foley leads by 90ms before visual graphic appearance so the ear prepares the eye.
  2. **Tactile Synesthesia:** Organic foley (wood taps, paper rustles, typewriter ticks) assigned to 2D vector elements so data feels physically weighty.
  3. **The "Scare & Release" Micro-Silence Vacuum:** Cuts music bed and ambient noise to complete digital silence for 0.4s to 0.8s immediately before the twist reveal (*The Vox Drop-Out*).
  4. **Frequency Slotting:** Voice (120Hz–4.5kHz), Highlighters (2.5kHz–8kHz at -22 dB), Sub-Bass (40Hz–65Hz), Bed (-17 dB with -4 dB sidechain ducking).
- **Autonomous Zero-Setup Self-Healing Standard (Rule 48):**
  1. `auto_bootstrap.py` provides a **Clone-and-Run Guarantee**: Any user cloning this repository on Linux, macOS, or Windows can run any script immediately with zero manual dependency installation.
  2. Automatically audits and installs missing Python packages (`kokoro`, `faster-whisper`, `scipy`, `soundfile`, `pillow`) via pip.
  3. Auto-discovers hardware acceleration (Intel VA-API, Nvidia NVENC, Apple VideoToolbox, or CPU fallback).
  4. Pre-warms Kokoro-82M and Faster-Whisper models, preventing first-run crashes.
- **The Hypnotic Modernity to Void Inversion Standard (Rule 49):**
  1. Benchmarked from **Ink Explainer** (19.3M views) and **Zenn** (8.1M views).
  2. In the first 0–6 seconds, hook subconscious retention by contrasting a hyper-relatable modern sensory comfort against the brutal evolutionary baseline.
  3. Structural Formula: *Modern Habit (0–3s)* $\to$ *Void Inversion Wipe (3–6s)* $\to$ *Visceral Survival Stakes (6–12s)*.
  4. Available natively in `viral_hook_engine.py --archetype modern_inversion` and `--archetype perspective_inversion`.
- **Dual-Tone Canvas Harmony & Dynamic Contrast Palette (Rule 50):**
  1. Benchmarked from the top 1% explainer channels to eliminate monochrome visual fatigue.
  2. Daytime / Modern scenes: Warm vintage parchment (`#F7E8C0` to `#ECD6B4`) with charcoal ink (`#1A1A1A`) and white head fills.
  3. Night / Peril scenes: Midnight Indigo & Navy Shadow (`#181A2A` to `#303D97`) with radiant campfire amber (`#FFAE33`).
  4. Firelight Island of Safety: Campfire light acts as a focal circle of safety; outer shadows contain low-opacity silhouettes of lurking threats to maximize psychological retention.
- **The OverSimplified Comic Contrast Law (Rule 51):**
  1. Benchmarked from **OverSimplified** (8.3M subscribers, 52M+ views).
  2. Ground grand historical crises in ridiculous human pettiness and exaggerated stickman facial expressions (oversized bug-eyes, shouting mouths, slapstick impacts).
  3. Supported via `look: oversimplified` and `viral_hook_engine.py --archetype oversimplified_folly`.
- **The Deadpan Flowchart Classification Standard (Rule 52):**
  1. Benchmarked from **Casually Explained** (4.4M subscribers, 23M+ views).
  2. Dissect agonizing social or lifestyle dilemmas with clinical decision trees, multiple-choice options, and un-hyped monotone delivery.
  3. Supported via `look: casually_explained` and `viral_hook_engine.py --archetype deadpan_quiz`.
- **The Mechanical Incentive & Keyflow Principle (Rule 53):**
  1. Benchmarked from **CGP Grey** (6.2M subscribers, 26M+ views).
  2. Strip away moral illusions and explain political/economic history through cold mathematical game theory and "Keys to Power".
  3. Supported via `look: cgp_grey` and `viral_hook_engine.py --archetype keys_of_power`.
- **The Kinetic Marker & Vector Drawing Standard (Rule 54):**
  1. Benchmarked from **MinutePhysics** (5.7M subscribers, 10M+ views).
  2. Shatter everyday intuition on physics/cosmic topics and solve paradoxes using real-time hand-drawn vector arrows and whiteboard marker squeaks in under 180 seconds.
  3. Supported via `look: minute_physics` and `viral_hook_engine.py --archetype everyday_axiom`.
- **The Strategic Dead Air & Comedic Timing Law (Rule 55):**
  1. Insert a strict 0.4s to 0.8s total audio drop-out immediately before punchlines or twist reveals.
  2. The visual reaction freezes in absolute silence; the reaction SFX or vocal punchline fires on the release.
- **The 5-Pillar Visual Effects (VFX) Anatomy (Rule 56):**
  1. Screen shake on bass impacts via decaying sine crop displacement.
  2. 2-frame pure white flash frames on sudden reality wipes.
  3. Radial speedlines focused on the stickman protagonist.
  4. 24px ambient bloom on hero props.
  5. Comic micro-emotes (sweat drops, question marks, steam puffs).
- **Dynamic Sticker Physics & Anti-Occlusion Staging (Rule 57):**
  1. Elastic spring entrance ($1.15\times \to 1.00\times$) with subtle tilt.
  2. J-cut audio pre-lapping leads visual by 90ms–120ms.
  3. Anti-occlusion guard prevents covering stickman face.
  4. 2.5s bounded lifetime before smooth zip-out whoosh.
- **Kinetic Typography & Angled Chapter Headings (Rule 58):**
  1. Single-word Hormozi kinetic badges in active glowing pills.
  2. Animated chapter heading cards via `video_editor_studio.py heading` with Ken Burns push-in ($1.00\times \to 1.045\times$).
  3. -3.5° to -5.0° angled text badges with 14px dark outline.
- **The 5-Layer Broadcast Foley Mix (SFX Hierarchy) (Rule 59):**
  1. Sub-bass boom (40–65Hz) $\to$ Tactile foley $\to$ Auditory highlighters $\to$ Vox drop-out silence $\to$ Sidechain ducked music bed (-24 dB).
- **Dynamic Camera Kinetics & Multi-Track Editing (Rule 60):**
  1. Continuous Ken Burns slow push-in on any hold $>2.0\text{s}$.
  2. OverSimplified dialogue cuts alternating every 0.8s–1.4s.
  3. Split-screen comparisons with thin vertical divider.
- **The Plain Paper Palate Cleanser Standard (Rule 61):**
  1. Plain off-white paper page (`#FAF8F2`) cut every 45–75s for sensory reset.
  2. Bold hand-drawn felt-pen typography with $>70\%$ negative breathing space.
  3. Expressive reaction stickman in the corner (`shock`, `think`, `point`).
  4. Subtle micro push-in ($1.00\times \to 1.025\times$) over 2.0s–3.0s via `studio.py page`.
- **Mutual Sticker & Asset Registry Standard (Zero-Waste Reuse - Rule 62):**
  1. **Zero Duplicate Generations**: Cutout props (`elements/cut/*.png`) are format-agnostic 1:1 transparent stickers. A sticker generated for Shorts can and must be reused in Long (and vice versa).
  2. **Registry Lookup (`asset_registry.py`)**: Before submitting any element to Google Flow, the engine queries `<project_root>/STICKERS_REGISTRY.json`.
  3. **Semantic NLP Token Matching**: Automatic resolution of synonyms and plural forms (e.g. "sabertooth skull" matches "sabretooth tiger skull" or "skull").
  4. **Centralized Repository**: Reusable elements are centralized in `<project_root>/elements/cut/` and automatically symlinked or copied into active pipelines (`short/` and `long/`). Flow is prompted only if no semantic match exists.
- **Strict Native Vertical 9:16 Flow Architecture & Letterbox Guard (Rule 63):**
  1. **Positional Token Weighting**: Google Flow / Imagen models place primary spatial attention on the first 15–20 tokens. Prompts that mention landscape terms early produce letterboxed horizontal compositions even with `--aspect 9:16`.
  2. **Front-Loaded Vertical Directives**: All 9:16 prompts must be front-loaded with:
     `"A true full-height vertical 9:16 portrait illustration, tall mobile smartphone wallpaper framing: {scene}. Tall vertical composition filling the complete mobile screen from top to bottom, vertical smartphone portrait orientation."`
  3. **Horizontal Keyword Sanitizer**: Automatically converts horizontal tokens (`landscape` $\to$ `vertical scene`, `horizon` $\to$ `vertical vista`, `panoramic` $\to$ `tall framing`, `wide shot` $\to$ `full-body tall shot`, `split screen` $\to$ `vertically stacked frame`).
  4. **Universal Shorts Negative Prompt**: Enforced across all Shorts prompts:
     `horizontal composition, widescreen framing, landscape layout, 16:9, letterbox bars, pillarbox, black bars, white borders, split frame horizontally, cinematic letterbox, panoramic view, wide angle horizon, distorted vertical stretch`.
  5. **Mandatory Letterbox Guard (`verify_vertical_layout`)**: Every generated image is verified before rendering: aspect ratio must be $\le 0.65$ and top/bottom 12% pixel bands must have variance $\sigma > 3.5$ (detecting solid/near-solid letterbox bars). Flagged images are rejected and re-prompted.
- **Deterministic Word-Level Audio-Visual Synchronization (Rule 64):**
  1. **Zero Guessed Timestamps**: Scene cuts and sticker overlay entrances are strictly time-locked to Whisper word timestamps from `WORDS.tsv` using `line.i` coordinates (`01.0` for sentence onset, `+01.6` for keyword sticker reveal).
  2. **Deterministic Alignment (`align_hybrid_scenes.py`)**: Automatically resolves timeline drift, locks scene durations to narration beats, and ensures overlays never linger beyond their intended time-to-live.
- **Intelligent Emotion & Contextual Visual Effects (VFX) Director (Rule 65):**
  1. **Narrative Emotion Parsing (`vfx_smart_designer.py`)**: Script lines are analyzed for emotional arousal, danger, tension, and temperature.
  2. **Contextual VFX Application**:
     - `blood` / `danger`: Dynamic 1.2 Hz pulsating crimson perimeter vignette for predator attacks and biological peril.
     - `ice` / `cold`: Cyan crystalline edge vignette for freezing temperatures and blizzards.
     - `bw` / `grayscale`: 92% desaturation with ink contrast tinting for deep-time historical flashbacks.
     - `zoom_punch`: Kinetic 0.22s snap-in ($1.04\times \to 1.00\times$) for shocking paradigm shifts and opening hooks.
     - `shake` / `rumble`: Camera shake ($\pm 12\text{px}$) for physical impacts, explosions, and catastrophe.
     - `hover` / `breathing`: Sinusoidal vertical hovering ($\pm 5\text{px}$) to keep stickers organically alive on screen.
- **Mandatory Visual Sticker Verification & Zero-Empty-Scene Gate (Rule 66):**
  1. **Zero Empty Scenes**: Every standard illustrated scene (`shots/*.png`) must contain at least one contextual sticker cutout, dynamic rolling counter, or infographic bar chart that lands on a spoken keyword. Videos with stretches of bare illustrations without stickers are strictly rejected.
  2. **Pre-Render Manifest Verification Gate**: Before starting `render_pro.py`, the pipeline must parse `SCENES_HYBRID.tsv` and verify that each scene's `ov` list is populated and that all referenced cutouts exist on disk in `elements/cut/`.
- **Overlay Ordering & Chronological Placement Gate (Rule 67):**
  1. **Strict Local Parenting**: In `SCENES_HYBRID.tsv`, every `+` overlay row MUST be placed immediately under the scene row it belongs to. Never append overlay rows at the bottom of the file.
  2. **Automatic Re-Parenting Guard**: `render_pro.py` and `align_hybrid_scenes.py` must automatically re-parent any misplaced or out-of-order overlay row to the active scene whose `[t0, t1)` window contains the overlay's timestamp.
- **Multi-Column VFX Robustness & Schema Enforcement Gate (Rule 68):**
  1. **6-Column TSV Schema Integrity**: All TSV files must strictly enforce the 6-column header: `cue \t img \t text \t pos \t extra \t space`.
  2. **Multi-Column Extraction**: `render_pro.py` must inspect `extra`, `pos`, and `space` for transition tags (`fade`, `crossfade`, `flash`, `cut`) and VFX tags (`danger`, `blood`, `ice`, `shake`, `zoom_punch`, `bw`), ensuring that minor column misalignments never cause VFX to fail silently.
- **Semantic Asset Naming Standard (Ban on Conflicting Numeric IDs - Rule 69):**
  1. **Descriptive Semantic Slugs**: Sticker cutouts must be named by descriptive nouns or concept slugs (e.g. `mattress.png`, `sabertooth_skull.png`, `deadbolt_lock.png`) rather than arbitrary numeric filenames (`01.png`, `02.png`).
  2. **Cross-Format Collision Prevention**: Prevents namespace collisions between Shorts and Long pipelines where `01.png` could refer to two completely different objects.
- **Adaptive Sticker Lifetime & Screen Density Standard (Rule 70):**
  1. **Long-Form Scene Hold Adaptation**: In long-form documentary scenes ($>5.0\text{s}$), sticker hold time must dynamically scale to $3.5\text{s} - 5.5\text{s}$ (or $\approx 70\%$ of scene duration) rather than prematurely expiring after 2.2s.
  2. **Seamless Exit**: The sticker smoothly scales down and fades out during the final 0.28s of its lifetime, transitioning smoothly into the next visual beat.
- **Autonomous Spatial & Negative Space Placement Solver (Rule 71):**
  1. **Dynamic Negative Space Evaluation**: `render_pro.py` evaluates candidate docking anchors (`top_right`, `top_left`, `mid_right`, `mid_left`, `center_high`) by computing background luminance and spatial edge density gradients (`compute_negative_space_score`).
  2. **Zero Subtitle Overlap**: Guaranteed vertical buffer ($\ge 140\text{px}$ in Shorts, $\ge 80\text{px}$ in Long) prevents stickers from touching or obscuring subtitles.
  3. **Platform UI Clearance**: Shorts layout strictly reserves right-side engagement column ($x \le 860$) and bottom control overlay ($y \le 1250$).
  4. **Crowding Auto-Scale**: Automatically downscales stickers to $0.82\times$ if background scene elements are visually dense.
- **Calibrated Tasteful Motion Physics (Rule 72):**
  1. **Tactile Damped Spring**: Pop-in physics use calibrated spring function `spring_p(p) = 1.0 - exp(-8.5 * p) * cos(8.0 * p)`, producing a crisp, organic 2D sticker reveal settling in 240ms without oscillating jitter.
  2. **Micro Ken Burns Drift**: Slow background scale ($1.00\times \to 1.025\times$) imparts subtle documentary life without dizzying motion.
  3. **Boundary Restraint Rule**: Automatically damps motion amplitudes by 70% when stickers are anchored within 30px of boundaries or subtitle boxes.
- **Google Flow Visual QC & Bounded Auto-Rebuild (Rule 73):**
  1. **Sticker Cutout QC (`verify_sticker_cutout`)**: Rejects unkeyed magenta chroma halos ($>1.8\%$ of opaque subject pixels) and canvas boundary clipping ($>15\%$ border coverage).
  2. **Vertical 9:16 QC (`verify_vertical_layout`)**: Rejects horizontal aspect ratios and solid letterbox/pillarbox borders.
  3. **Bounded Retries**: Prompt refinements (isolated magenta background / tight vertical portrait) retry up to 3 attempts maximum, avoiding infinite loops.
- **The 5 Mandatory Pre-Render Quality Gates (`validate_pipeline.py` - Rule 74):**
  1. **Gate 1**: Scene & Sticker Manifest Completeness + Cutout Quality QC (procedural stamps and programmatic archetypes bypass disk image lookup).
  2. **Gate 2**: Native 9:16 Vertical Framing Purity (Shorts aspect $\le 0.65$, no letterboxing).
  3. **Gate 3**: 3-Stem Master Audio Integrity (non-silent VO, SFX, music, -14 LUFS loudness calibrated, `~45%` silent cuts on calm transitions, peak-aligned slams, pre-twist `--dip`).
  4. **Gate 4**: Multi-Track Synchronization (`WORDS.tsv` $\leftrightarrow$ `SCENES_HYBRID.tsv` $\leftrightarrow$ `cues_pro.tsv`, $<100\text{ms}$ drift, timeline duration locked).
  5. **Gate 5**: Autonomous RL Feedback & Policy Compliance (pacing, visual holds, sticker density, loudness, structured F-codes + 4-of-6 novelty tracking).
  6. **Gate 0 / Gate 6 & Pre-Delivery Clean-Context Critic Pass**: `studio.py director <dir> --pre-spend` audits single `DIRECTOR_PLAN.json` (`thesis`, `terms`, `cast_anchors`, `facts`, `shot_size`, `angle`, `camera_move`, `reads_min_sec`) before TTS/Flow; after render, `studio.py sheets <mp4>` exports `qa/hook_sheet.jpg`, `qa/phone_sheet.jpg`, and `qa/beats_sheet.jpg` + `<10s` signal QA for a 1-round critic check before delivery.
- **Unified Studio Orchestrator (Rule 75):**
  1. **Single CLI Entry Point**: `python3 studio.py create "<Topic>" --format both --captions [--dry-run]` orchestrates the entire script-to-master dual pipeline.
  2. **Safe Pre-Flight Verification**: Supports `--dry-run` to execute and validate all generation and sync stages through the **6 Quality Gates** without triggering video rendering passes.
- **The 6-Archetype Visual Variety Engine & Multi-Sticker Composition (Rule 76):**
  1. **Archetype 1: Flow Hero Illustrations** (`shots/*.png`): Primary narrative anchors. Hand-drawn 2D cartoon style on warm paper with bold black ink outlines, continuous smooth cosine ease drift ($1.00 \to 1.045$), $0.22\text{s}$ crossfades, and unlimited 1–4+ collision-free word-synced stickers (`>= 32px` padding, locked anchors).
  2. **Archetype 2: Authoritative Camera Motion** (`pan_left`, `pan_right` across unique shots): Smooth directional drifts across native Flow illustrations (strictly NO abrupt mid-shot snap-cuts or recycled-image jitter).
  3. **Archetype 3: Full-Bleed Minimalist Impact Frame** (`img: card_stat` or `card_phrase`, `text: 1177 BC | Eight Empires Connected`): Rendered at 2x supersampling onto organic paper grain & faint dot-grid canvas with giant `PermanentMarker` hero metric, tapered highlighter stroke, radial corner ticks, curved ink arrow, and grounded sticker shadow.
  4. **Archetype 4: Aspect-Aware Split Contrast Frames** (`img: split_compare` or `split_contrast`, `text: MYTH: ... | REALITY: ...`): **Top-vs-Bottom horizontal split (`Y: 6%–72%`) on `9:16` Shorts** and **full-height Left-vs-Right vertical split on `16:9` Long** with balanced contrasting stickers on both sides and compact corner verdict badges (`stamp_x` / `stamp_check`).
  5. **Archetype 5: Hand-Drawn Verdict Accents** (`stamp_x`, `stamp_check`, `stamp_false`, `stamp_true`, `stamp_myth`): Crisp crimson brush `X` or emerald `✓` marks with physical impact spring hit (`compact=True` circular seal in split corners).
  6. **Archetype 6: Progressive Data & Timeline Cards** (`img: bar_timeline`, `text: PART 1: Label | PART 2: Label...` or `img: stat_pie`, `text: 75% | Description`): Vertical stepped spine (`Y: 8%–70%`) on `9:16` Shorts or horizontal timeline on `16:9` Long with bold nodes, chevrons, tinted strips, and highlighted climax sticker.
- **Calm Clause-Locked Pacing & Linear Flow (Rule 77):**
  1. **Opening 15s Hook Density**: Smooth natural visual transitions every 2.0s–3.5s (NEVER sub-1.5s chaotic flicker).
  2. **Shorts Body (9:16)**: Target cut **2.5s–4.0s** (min **1.8s**, max **4.2s**, zero `< 1.5s` flicker). Min **15–20 unique Flow shots**.
  3. **Long-Form Body (16:9)**: Target cut **3.5s–5.5s** (min **2.2s**, max **6.5s**, zero `< 1.5s` flicker). Min **50–70 unique Flow shots**.
  4. **Strict Linear Progression**: Always advance linearly ($A \to B \to C \to D$); never ping-pong back to a previous shot across an archetype card.
- **Competitor Retention Narrative Blueprint (Rule 78):**
  1. **0–15s Present-Day Mirror Hook**: Start with 2nd-person direct address ("Tum", "Aap", "Imagine you") connecting a mundane modern experience to the ancient mystery.
  2. **Myth-Flip + Named Proof Loop**: State a common misconception, smash it with `stamp_x`, then provide historical/scientific proof.
  3. **Escalation & Open-Loop Bridges**: "Lekin yeh sirf shuruat thi...", "Asal kahani yahan se shuru hoti hai..."
  4. **Full-Circle Emotional Payoff Ending**: Callback to the opening hook question in the final seconds.
  5. **Natural Conversational Spoken Urdu / Roman Urdu**: Clear, flowing narration without robotic filler phrases.
- **Micro-SFX Synergy for Procedural Archetypes (Rule 79):**
  1. `card_stat`: Tactile paper slap / slam (`-10 dB`).
  2. `split_compare`: Smooth paper swish (`-11 dB`).
  3. `bar_timeline` / `stat_pie`: Modern tactile data ping (`-11 dB`).
  4. `stamp_x` / `stamp_check`: Physical impact thud (`-10 dB`) or resonant positive chime (`-11 dB`).
  5. Sticker entrance / exit: Quick tactile pop (`-11 dB`) / soft zip-out (`-13 dB`). Master mix locked at `-14.0 LUFS`.
- **Curated Typographic Hierarchy & 9 Editorial Looks (Rule 80):**
  1. **4 Curated Fonts**: `PermanentMarker-Regular.ttf` for hero stats and split headers, `Bangers-Regular.ttf` for stamps and hook words, `Caveat-Bold.ttf` for annotations and timeline sub-labels, `SedgwickAve-Regular.ttf` for title cards, and `PatrickHand-Regular.ttf` for kinetic captions.
  2. **9 Editorial Looks**: `bright` (canonical), `warm`, `night`, `ink`, `oversimplified`, `cgp_grey`, `casually_explained`, `minute_physics`, `painted` natively driving paper, ink, card fills, accent highlights, and Flow prompts.
- **Production Upload Packaging & Self-Healing Fallback (Rule 81):**
  1. **Automated Upload Pack (`UPLOAD_PACK/`)**: Every completed render auto-generates 16:9 YouTube thumbnail, 9:16 Shorts cover, `METADATA.json` (chapters, SEO tags, titles), and `POSTING_GUIDE.md` (publishing workflow & pinned comments).
  2. **Self-Healing Sticker Cutouts**: When chroma-keying fails alpha or halo checks, engine auto-runs `cutout.py` (luminance/border flood-fill) and `delama.py` corner cleaning locally before Flow re-generation.
  3. **Hardware-Safe Auto-Routing**: Detects CPU/GPU profile via `low_resource_engine.py` and routes to `low_resource_whisper.py` int8 alignment and VA-API/ultrafast FFmpeg encoding.
- Text on pictures only for numbers and dates, names, map places and unseen terms. Never
  over a face (render.py places tags itself). 6-10 text cards per 2 minutes.
- Pick pictures by what they show, not by file number. Flow swaps them in batches.
- Never paste or ask for API keys or tokens in the chat. Keys go in `.env` files the user
  edits.
- On machines with 8 GB of RAM or less, keep ffmpeg at `-threads 3` (the scripts do) and run
  one heavy job at a time.
- Urdu and other non-Latin labels go through libass automatically; if a font lacks the
  script, set `STICK_FONT_COMPLEX` to a .ttf that covers it.
- For Claude usage: QC from grids, and suggest a new chat per new video.
