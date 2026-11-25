# Stickman Hybrid: Installer & Orchestrator (Instructions for Claude / Antigravity)

The user has opened this unzipped folder, pointed you at it, or given a prompt like:
"read all files and make me an animation", "start", "stickman hybrid start", "nayi video banao", or "continue".

Follow this exact protocol:

## 1. Global Skills Installation & Sync
- Ensure every skill in `skills/` is installed and synced identically:
  - Copy `skills/stickman-hybrid/` to `~/.claude/skills/stickman-hybrid/` and `~/.gemini/config/skills/stickman-hybrid/`.
  - Copy `skills/stickman-stickers/` to `~/.claude/skills/stickman-stickers/` and `~/.gemini/config/skills/stickman-stickers/`.
  - Copy `skills/vox-doc-sound/` to `~/.claude/skills/vox-doc-sound/` and `~/.gemini/config/skills/vox-doc-sound/`.
  - Copy companion intelligence skills (`youtube-seo-optimizer`, `emotional-arc-designer`, `visual-emotion-engineer`, `headline-psychologist`, `loss-aversion-designer`, `data-storytelling`, `viral-generator-builder`) to `~/.claude/skills/` and `~/.gemini/config/skills/`.
  - Preserve any existing user `.env`, `SETUP_STATUS.md`, `CATALOG.tsv`.

## 2. Project Intake & Zero-State Rule (Start from 0 vs. Edit Existing)
Never assume or reuse any previous project (like `clothes` or any past topic) unless the user explicitly asks to edit or continue it.

When the user asks to make an animation or says "start":
1. **Determine User Intent**:
   - **A) New Video (Fresh 0-Start)**: The default when starting or asking for an animation.
   - **B) Edit / Continue**: Only if the user says "continue", "edit", or specifies an existing project name.

2. **If Starting a NEW Video (Fresh 0-Start)**:
   > [!CAUTION]
   > **HARD RULE: NEVER start generating scripts, assets, or running studio creation until all 5 answers are collected.** Do NOT assume defaults.
   Respond in the user's language (Roman Urdu / Urdu / English) and ask the **5 Intake Questions** in ONE concise message (with no pre-selected defaults):
   - **1. Topic**: What topic do you want the video on? (Aap apna topic bata dein ya main 10 viral topics suggest karoon?)
   - **2. Language**: Narration kis language me chahiye?
     - *English* (Kokoro am_michael, local CPU)
     - *Urdu / Roman Urdu* (Indic Parler Aman on Kaggle free GPU)
     - *Other languages*
   - **3. Length**: Video kitni lambi chahiye? (e.g. 1 minute, 2 minutes, 5 minutes, or any length)
   - **4. Format**:
     - `1) Long (16:9 Landscape)`: Full 1920x1080 documentary for YouTube / TV
     - `2) Shorts (9:16 Vertical)`: Fast 1080x1920 viral video for YouTube Shorts / TikTok / Reels
     - `3) Both (16:9 Long + 9:16 Short Clip)`: Full documentary + standalone vertical viral short
   - **5. Captions**:
     - `1) Yes (With Captions)`: Alex Hormozi single-word kinetic subtitles with golden glow
     - `2) No (Without Captions)`: Clean cinematic visuals without subtitles

3. **When the User Answers**:
   - Create a brand new project folder: `~/StickmanHybrid/<new-topic-slug>/` (lowercase, no spaces, short).
   - Start completely from zero: `PROGRESS.md`, `SCRIPT.md`, `LINES.tsv`, `STYLE.txt`.
   - Never copy old images, old audio, or old TSVs from another project.

4. **If Editing / Continuing an Existing Video**:
   - Check `~/StickmanHybrid/` for the requested project.
   - Inspect its `PROGRESS.md` to see the current stage.
   - Apply only the requested edits or resume where it was left off.

## 3. Production Pipeline (Strict Quality Standards)
Follow `skills/stickman-hybrid/PLAYBOOK.md` Rules 1–45:
- **Stage 1 (Script & Narrative Architecture)**: Research topic, structure 6-Act tension curve via `narrative_intelligence.py` and open loops via `curiosity_engine.py`, write `SCRIPT.md` + `LINES.tsv` -> **Wait for User Approval**.
- **Stage 2 & 3 (Look, Pictures & Voice)**: Start in parallel upon script approval:
  - Select look (`looks/`), write `STYLE.txt`, character sheet -> `pictures.py refs` -> `SHOTS.tsv` -> submit shots.
  - Voice with intelligent documentary cadence (`kokoro_vo.py` for English, Parler Aman for Urdu/Roman Urdu) -> `vo_join.py` -> `align.py` -> `WORDS.tsv`.
- **Stage 4 (Scenes, 3-Tier Sticker Vault & Multi-Sticker Solver)**: Map script keywords to transparent cutouts via `skills/stickman-stickers/` (Tier 1 `flow_vault/` -> Tier 2 `cc0_library/` -> Tier 3 Google Flow `#FF00FF` auto-harvested via `key.py`/`cutout.py` with alpha rim erosion). Supports unlimited simultaneous multi-stickers (1–4+ props) distributed via collision-free `>= 32px` slot layout, cached static anchors, and subtitle clearance.
- **Stage 5 (Warm Cinematic Sound Ratio)**: Tactile SFX and Kurzgesagt Auditory Highlighters (`sfx_smart_designer.py` -> `cues_pro.tsv`) -> `mix.py` (-11 dB to -13 dB bed rel to VO starting at 0.0s, vocal pocket EQ -3.2dB @ 1.8kHz, gentle 1.9:1 sidechain) -> -14.0 LUFS broadcast mix (`mix_pro.wav`).
- **Rule 21 (Zero-Crop Full-Frame)**: Direct 100% native resolution scaling ($1536 \times 2752$ for 9:16 and $2752 \times 1536$ for 16:9). No cropping or edge loss.
- **Rule 22 (Dual Independent Flow Pipelines)**: In Format "Both", `short/` and `long/` MUST have completely independent Flow generation:
  - `short/shots/`: Dedicated native 9:16 vertical Flow art (`--aspect 9:16`).
  - `long/shots/`: Dedicated native 16:9 widescreen Flow art (`--aspect 16:9`).
  - ZERO cross-copying or pillarboxing between pipelines.
- **Rule 23 (Surgical Edit Mode)**: When user commands edit, ask interactive category questions and surgically modify target files without destroying existing work.
- **Rule 24 (Spatial Hierarchy & Clutter-Free Layout)**:
  - Shorts (9:16): Opening title banner at $y \in [190, 250]$ only during first 2.5s; scene tag at $y = 230$ (suppressed during first 2.5s); right 220px margin preserved ($x \le 860$); bottom 660px preserved ($y > 1250$); kinetic subtitles at $y = 1180$; sticker bottom strictly above $y = 1040$ ($\ge 140\text{px}$ buffer above subtitles).
  - Long Form (16:9): Chapter slug at Top-Left ($x \approx 140, y \approx 100$); subtitles at $y = 920-940$; stickers at $y \le 820$.
- **Stage 6 (Render & QC - Phase 2 Intelligence)**:
  - **Single-Entry Orchestrator**: Run `studio.py create "<Topic>" --format both --captions [--look bright] [--suggest] [--dry-run]`.
  - **Curated Typography & 9 Editorial Looks**: 4 distinct fonts (`PermanentMarker`, `Bangers`, `Caveat`, `SedgwickAve`, `PatrickHand`) across 9 looks (`bright`, `warm`, `night`, `ink`, `oversimplified`, `cgp_grey`, `casually_explained`, `minute_physics`, `painted`).
  - **6 Full-Bleed Editorial Archetypes**: `card_stat`, `split_compare` (Top-vs-Bottom on 9:16 Shorts / Left-vs-Right on 16:9 Long), `bar_timeline`, `stat_pie`, calm eased Flow drift, and hand-drawn verdict accents (`stamp_x`, `stamp_check`) rendered at 2x Lanczos Supersampling onto paper-grain/dot-grid canvas.
  - **Rule 25 (Multi-Slot Collision-Free Placement)**: `render_pro.py` runs `calculate_intelligent_sticker_anchor` with negative-space scoring, `>= 32px` padding, cached spawn-time anchors/scales (0.83x at 3 props, 0.78x at 4+), zero subtitle overlap (`>= 140px` Shorts / `>= 80px` Long).
  - **Rule 26 (Director-Supervised Motion & Animated Choreography)**: `director_supervisor.py` emits `DIRECTOR_PLAN.json` auditing relevance (zero redundant stickers on matching shots), locking exact `WORDS.tsv` triggers at `-0.06s`, tracking `WIDE`/`MEDIUM`/`TIGHT`/`EDITORIAL_CARD` scale flow, and assigning 6 context-aware motion archetypes (`slide_arc_left`/`right`, `drop_weight`, `peel_reveal`, `bloom_focus`, `swing_strike`) + group choreography (`duo_converge`, `cause_effect` with `0%->100%` animated Bezier ink arrows, `trio_cascade`, `quad_showcase`) + subtle continuous alive idle breathing (`±3.2px`/`±0.45°`) and calm `0.22s` exit ease.
  - **Rule 27 (Bounded Flow Visual QC & Alpha Rim Erosion)**: `verify_sticker_cutout` + inward alpha rim erosion (`key.py`/`cutout.py`) eliminate white fringes; local fallbacks heal before re-generation.
  - **Rule 28 (6 Mandatory Pre-Render Quality Gates)**: `validate_pipeline.py` enforces Gates 1–5 plus Gate 6 (`DIRECTOR_PLAN.json` 0-redundancy check, unique Flow shot density, dual-extreme anti-stagnation/anti-flicker, zero ping-pong, and `card_stat`/`split_compare` pixel balance audit).
  - Single still frame test (`--frame T`) first before full video render. **Never render final video without user explicit command!**
- **Stage 7 (Viral SEO & Automated Upload Packaging)**: Run `social_packager.py` and `thumbnail_generator.py` to auto-populate `UPLOAD_PACK/` with `thumbnail_16x9.png`, `thumbnail_9x16.png`, `METADATA.json`, and `POSTING_GUIDE.md`. Explore trending topics via `studio.py trends`.

Prerequisite: Flow Connector extension CLI (`flow-auto`). Never ask for API keys in chat.
