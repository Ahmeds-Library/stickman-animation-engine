---
name: stickman-hybrid
description: Make a complete stickman documentary explainer in the HYBRID look, end to end: clean full-colour scene pictures (Google Flow, Nano Banana 2) with cut-out stickers that pop in on the spoken words, animated counters and paper collage beats, in the style of the viral "ancient humans" explainer channels. Covers setup, topic ideas, the script, the voiceover (Kokoro for English, Indic Parler with Aman on Kaggle for Urdu, Roman Urdu and regional languages), a consistent stickman cast, LaMa watermark removal, word-timed cuts, Urdu, Roman Urdu and English on-screen text, sound design and the final MP4. Use when the user says "stickman hybrid", "hybrid stickman", "stickman sticker video", "stickman hybrid start", "stickman hybrid continue", or opens the stickman-animation (stickman-hybrid) zip.
---

# Stickman documentary, hybrid look, end to end

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
| 8 | Thumbnails & SEO | `thumbnail_generator.py` produces high-CTR 16:9 (`1280x720`) and 9:16 (`1080x1920`) thumbnails following the 3-element rule (stickman, glowing prop, tilted curiosity text). `trending_researcher.py` provides optimized high-RPM titles, Barnum hooks, and SEO tag clusters | Deliver clickable thumbnail PNG paths and ready-to-paste YouTube title/description/tags metadata |

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
  1. **Shorts (9:16):** Title banner shown ONLY during first 2.5s ($y \in [190, 250]$), auto-fading out. Scene concept pill at $y = 230$ (suppressed during first 2.5s to avoid double header). Right 220px margin preserved ($x \le 860$) for Instagram Reels / YouTube Shorts engagement rail (Like, Comment, Share). Bottom 660px ($y > 1250$) kept 100% clear of graphics/tags. Kinetic single-word subtitles centered at $y = 1180$. Sticker cutouts docked in upper side quadrants ($y \in [0.34H, 0.44H]$, height $\le 420\text{px}$) with bottom strictly above $y = 1040\text{px}$, leaving a $\ge 140\text{px}$ clear buffer above subtitles.
  2. **Long Video (16:9):** Topic/chapter slug placed at Top-Left ($x \approx 140, y \approx 100$), leaving bottom subtitles ($y = 920-940$) and center character completely uncluttered. Sticker callouts docked in upper side quadrants ($y \le 820$). Single visual focal point at all times.
- **Screen Heading Suppression & Zero-Clutter Standard (Rule 25):**
  1. **Zero Redundant Headings on Standard Scenes:** Floating scene heading pills (`draw_label` scene pills) and top title banners must NOT be rendered over normal background illustrations (`shots/*.png`) when animated stickers or kinetic subtitles are active (`render_pro.py --scene-labels=False --header=False`).
  2. **Elimination of "Slide Show" Clutter:** When an animated sticker pops up with its own clean label and single-word subtitles flash at the bottom, an extra heading banner ("THE MODERN HUM", "BEFORE FRIDGES", "DESERT ICE") creates visual confusion and makes the video feel like a slide presentation rather than a professional cinematic animation.
  3. **Title Card Exception:** Text headings are permitted ONLY on dedicated full-screen chapter splash cards (`img == "card"`), where the screen is intentionally cleared of character action to announce a major structural transition.
  4. **Pristine Triad Hierarchy:** Normal scenes must feature only three visual layers: (1) Full-bleed 2D stickman background illustration, (2) Clean transparent animated sticker props popping on cue, and (3) Alex Hormozi golden-amber single-word kinetic subtitles docked safely at the bottom.
- **High-Density Visual Pacing & Dynamic Image Frequency ("Ziada Image Use Kiya Karo" - Rule 26):**
  1. **Shorts (9:16 Viral Retention Standard):**
     - Target cut duration: **$\le 3.0\text{s}$ per cut** (minimum 16–20 distinct background scenes for a 45–60s video, earning an A+ in RL-QC).
     - Every narration line must be split into at least 2 visual beats: the opening beat (`@<line_id>`) and a mid-sentence action/concept cut (`@<line_id>:<keyword>`).
     - Hard limit: No single background image may linger on screen for $> 3.8\text{s}$. Fast visual variety sustains high audience dopamine and prevents swipe-away dropoff.
  2. **Long Documentary (16:9 Narrative Standard):**
     - Target cut duration: **$\le 6.0\text{s}$ per cut** (minimum 50–65 distinct widescreen scenes for a 5-minute video, earning an A in RL-QC).
     - Avoid static holds: each line, historical fact, diagrammatic explanation, and tone change must have its own dedicated shot (wide establishing landscapes, medium character interactions, blueprint technical drawings, and macro scientific cutaways).
     - Hard limit: No single background image may linger on screen for $> 7.5\text{s}$.
  3. **RL-QC Pacing Verification:** `evaluate_rl.py` automatically checks average cut duration and issues deductions if video pacing falls into sluggish grades (B or C).
- **Multi-Layered Sound Design & SFX Density Standard ("Ziada Se Ziada Sounds Use Karo" - Rule 27):**
  1. **Zero Silent Visual Events & Storytelling Golden Ratio:** Every visual cut, sticker entrance, and keyword punch must be paired with tactile sound. Videos with fewer than 15 sound cues are strictly flagged as under-designed. Music bed is calibrated to **-17.0 dB** (Long) / **-16.0 dB** (Shorts) with a **vocal pocket notch EQ** (-3.2 dB at 1.8 kHz) in `mix.py`. Sidechain ducking is set to a gentle **2.8:1 ratio** with a 550ms release so music remains clearly audible, rhythmic, and emotional throughout narration instead of collapsing into a dry "reading" vacuum.
  2. **Four Mandatory Audio Layers (`sfx_smart_designer.py`):**
     - **Layer 1 (Visual Cut Transitions):** Every scene cut (`@<line_id>`) triggers a subtle whoosh, paper swipe, zoom snap, or swish (`-20 dB` to `-23 dB`).
     - **Layer 2 (Sticker Pop & Semantic SFX):** Every transparent sticker reveal (`+@...`) plays a semantically matched sound (bubble pop, notification ping, wood tap, water drop, coin drop, ice crack) (`-15 dB` to `-17 dB`).
     - **Layer 3 (Keyword Spoken Impact Hits):** High-curiosity spoken words in `WORDS.tsv` ("freezing", "danger", "starvation", "conquered", "impossible", "secret", "space") trigger synchronized micro-hits or sub-thuds (`-17 dB` to `-19 dB`).
     - **Layer 4 (Continuous Foley Bed & Music Score):** Continuous environmental loop (`-23 dB`) plus ambient documentary music bed at `-17 dB` with vocal pocket carving and warm vocal conditioning.
  3. **Broadcast Loudness Verification:** The final mix must verify at **-14.0 LUFS** ($\pm 1.0$ LUFS) and true peak $\le -1.0\text{ dBFS}$ via `evaluate_rl.py`.
- **Dynamic Visual FX (VFX) & Motion Transitions Standard (Rule 28):**
  1. **Scene Transition VFX:** Hard cuts are replaced or enhanced by contextual visual effects specified in `SCENES_HYBRID.tsv`:
     - `fade` / `crossfade`: Smooth 0.20s dissolve between consecutive scenes.
     - `flash`: 0.12s warm exposure bloom for big historical leaps, scientific discoveries, and opening hook reveals.
     - `zoom_punch`: Subtle 0.25s kinetic snap-in (1.04x $\rightarrow$ 1.0x).
  2. **Sticker Entrance & Living Motion VFX:**
     - `pop`: Harmonic damped spring bounce (0 $\rightarrow$ 1.08 $\rightarrow$ 1.00).
     - `drop` / `slam`: Vertical drop from top with bounce impact.
     - `slide_left` / `slide_right`: Horizontal inertia slide from off-frame.
     - `hover` / `breathing`: Organic sinusoidal vertical hovering ($\pm 5\text{px}$) after settling, keeping stickers alive throughout the scene.
- **Dynamic Sticker Lifetime & Clean Exit Standard (Rule 29):**
  1. **Word-Onset Synchronization:** Stickers must appear precisely when the keyword is spoken (`o["t"] = words_map["@<line>:<keyword>"]`). Never trigger stickers prematurely before the narrator speaks the object.
  2. **Strict Time-to-Live (TTL):** Stickers must NOT linger indefinitely until the scene cuts. Default duration is **1.8s–2.2s in Shorts** and **2.4s–2.8s in Long videos** (or explicit `dur:X.X` in `extra`).
  3. **Smooth Exit Animation:** During the final **0.22s** of its lifespan, the sticker smoothly shrinks (`1.0 -> 0.0`) and fades out cleanly (`render_pro.py`). The screen returns to pure background illustration, preventing visual stagnation and screen clutter.
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
