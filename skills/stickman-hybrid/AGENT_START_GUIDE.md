# 👑 MASTER AI AGENT STARTUP GUIDE: Stickman Hybrid Animation Engine
**Authoritative Onboarding Manual & System Architecture for Autonomous Agents**

> [!IMPORTANT]
> **MANDATORY INSTRUCTION FOR ALL AI AGENTS**:
> Whenever a user starts a session with: *"Read `AGENT_START_GUIDE.md` first"* or requests to create, continue, or edit a Stickman Hybrid documentary explainer video, **READ THIS ENTIRE DOCUMENT FIRST** before touching any files or executing commands.
> Following this guide guarantees zero wasted credits, zero hallucinated tools, frame-perfect sync, authentic 2D visual aesthetics, punchy sound design, and 100/100 broadcast quality.

---

## 🏛️ 1. Executive Summary & Core Mission

This engine produces **viral stickman documentary explainers** modeled after premier benchmark channels (14M, 8.5M, and 1.2M views).

### The Golden Rule of Stickman Explainer Animation
> **Still pictures, not AI video. Motion comes EXCLUSIVELY from stickers, counters, and cards.**
> 92–99% of screen time consists of frozen, hand-drawn 2D illustrations. What creates high viewer retention is an ultra-dense succession of **new pictures every 2–3 seconds** showing literally what is being narrated, punctuated by **cut-out stickers popping in on exact spoken syllables**, dynamic numbers rolling up, and tactile text cards. Never add AI video morphs or video generation models.

---

## ⚡ 2. The 10 Inviolable Golden Directives

Every AI agent must memorize and enforce these 10 non-negotiable rules:

| # | Directive | Law |
|---|---|---|
| **1** | **100% Google Flow Art** | All visuals (scenes and stickers) **MUST** be generated through Google Flow (`flow-auto`). **ZERO procedural PIL drawing** or AI video models. |
| **2** | **Zero Git Operations** | **NEVER** run `git commit`, `git push`, or alter git configuration. The user manages git manually. |
| **3** | **Canonical Visual Look** | Strictly follow `look: bright` from `boat_hi`. Clean 2D cartoon, black ink outlines, flat color with soft shading, bright daylight palette. **Never** use sepia or vintage brown paper unless explicitly commanded. |
| **4** | **Dual Decoupled Pipelines for "Both"** | When format is "Both", run **two completely decoupled pipelines**: `short/` (9:16 vertical, 40-70s) and `long/` (16:9 widescreen, 5-10m). **Never letterbox or pillarbox** between them. |
| **5** | **Zero-Waste Shared Sticker Registry** | **Never generate separate duplicate stickers** for Shorts and Long. Query `asset_registry.py` before prompting Flow. Sibling pipelines share `elements/cut/`. |
| **6** | **Native 9:16 Vertical Architecture** | For Shorts, front-load prompt with tall mobile directives, sanitize horizontal words, and enforce `verify_vertical_layout` guard. |
| **7** | **Mathematical Audio-Visual Sync** | Time-lock all scene cuts and sticker pops to Faster-Whisper `WORDS.tsv` (`line.i` notation). Zero guessed timestamps or visual drift. |
| **8** | **3-Stem Audio Mastering & Studio Cleanliness** | Route audio into `[vomix]` (voice with `highpass=85`, de-rumble EQ, presence boost, `afftdn=nf=-28` noise-floor and pause gate), `[sfxmix]` (tactile documentary SFX), and `[bed_ducked]` (melodic/rhythmic documentary bed with smooth `3.0:1 / 550ms` ducking at `-13.5 dB` constant floor; windy/ambient drone beds banned). Master target: **-14.0 LUFS**. |
| **9** | **Kinetic Editorial Motion & Rich 2D Animation** | Banned cheap color overlays (`danger` red vignette, `bw` desaturation snaps, `ice`). Drive animation via kinetic editorial transitions (`slide_wipe`, `whip_blur`, `punch_settle`, `zoom_punch`, soft `crossfade`), dynamic live ink annotations, spring physics stickers with entrance sparkles, and alive idle breathing. |
| **10** | **The 3 User Checkpoints** | Only pause for user input at: **1. Script Approval**, **2. Voice/Look Approval**, and **3. Final Video Delivery**. |
| **11** | **Standalone Music-Only Outro & Collision-Free Safe Zones** | Never overlay outro on active voiceover or story scenes. Full story finishes 100% cleanly first, then append a standalone music-only outro segment (`--outro-sec 8.0` on Long 16:9). Subtitles locked safely at Y: 81%–88% on Shorts with `split_compare` bottom panel above Y: 72% for zero visual collisions. |

---

## 📁 3. System Architecture & Directory Layout

### Workspace Structure
```
/home/mirza-ahmed-hassan/Desktop/stickman-animation/
├── AGENT_START_GUIDE.md               # This authoritative onboarding manual
├── studio.py                          # Unified CLI studio orchestrator & QC validator
├── skills/
│   ├── stickman-hybrid/              # Core visual generation, sync & rendering engine
│   │   ├── SKILL.md                  # Comprehensive skill specification (Rules 1-65)
│   │   ├── PLAYBOOK.md               # Production rules, pacing metrics & benchmarks
│   │   ├── scripts/
│   │   │   ├── script_architect.py   # 6-Act YouTube Retention Curve script generator
│   │   │   ├── align_hybrid_scenes.py# Deterministic word-level scene & sticker synchronizer
│   │   │   ├── asset_registry.py     # Semantic NLP mutual asset registry (Shorts <-> Long)
│   │   │   ├── vfx_smart_designer.py # Emotion & contextual visual effects director
│   │   │   ├── sfx_smart_designer.py # Semantic sound design generator
│   │   │   ├── flow_smart_generator.py# Google Flow prompt builder with 9:16 guards
│   │   │   ├── validate_pipeline.py  # 5-Gate Pre-Render Quality Gate
│   │   │   ├── render_pro.py         # Broadcast multi-layer video renderer with active sticker caps
│   │   │   ├── evaluate_rl.py        # Autonomous RL QC evaluator with deduction aggregation
│   │   │   └── rl_memory.py          # Continuous RL learning memory & self-tightening policies
│   │   └── looks/                    # Visual style definitions (bright.md is canonical)
│   └── vox-doc-sound/                # Voiceover, alignment & audio mixing engine
│       ├── SKILL.md                  # Voice & psychoacoustic sound specifications
│       ├── CATALOG.tsv               # 1,600+ indexed CC0 SFX and music files
│       └── scripts/
│           ├── kokoro_vo.py          # English neural voiceover (am_michael / am_fenrir)
│           ├── kaggle_runner.py      # Automated native Urdu Parler-TTS voice via Kaggle API (.env root)
│           ├── vo_join.py            # Sentence joins with calibrated acoustic gaps
│           ├── align.py              # Whisper forced word-level alignment (WORDS.tsv)
│           └── mix.py                # 3-stem loudness mixer with sidechain ducking (-14 LUFS)
```

### Production Project Structure (`~/StickmanHybrid/<project_slug>/`)
```
~/StickmanHybrid/<project_slug>/
├── PROGRESS.md                       # Persistent session state & decision history
├── SCRIPT.md                         # Full approved documentary script
├── LINES.tsv                         # Narration lines with calibrated acoustic gaps
├── STICKERS_REGISTRY.json            # Global mutual asset index (Shorts <-> Long)
├── elements/
│   └── cut/                          # Centralized transparent sticker cutouts (.png)
├── short/                            # Dedicated Shorts Pipeline (9:16 Vertical, 40-70s)
│   ├── VO.wav / WORDS.tsv            # Punchy narration & word timestamps
│   ├── shots/                        # Native 9:16 Flow illustrations (1536x2752)
│   ├── elements/cut/                 # Symlinked/shared transparent stickers
│   ├── SCENES_HYBRID.tsv             # Word-synchronized scene cuts & overlays
│   ├── cues_pro.tsv / mix_pro.wav    # Multi-layered sound cues & master audio
│   └── <project>_short_9x16.mp4      # Final rendered vertical Shorts video
└── long/                             # Dedicated Long Documentary Pipeline (16:9, 5-10m)
    ├── VO.wav / WORDS.tsv            # Calm documentary narration & word timestamps
    ├── shots/                        # Native 16:9 Flow illustrations (2752x1536)
    ├── elements/cut/                 # Symlinked/shared transparent stickers
    ├── SCENES_HYBRID.tsv             # Word-synchronized scene cuts & overlays
    ├── cues_pro.tsv / mix_pro.wav    # Multi-layered sound cues & master audio
    └── <project>_long_16x9.mp4       # Final rendered widescreen documentary video
```

---

## 🧠 5. Autonomous Creative Director & Visual QC Intelligence Layer (Phase 2)

Phase 2 upgrades the engine from passive execution into an active **Autonomous Creative Director** with multi-layer visual QC, spatial intelligence, and deterministic pre-render quality enforcement.

### A. Spatial & Negative Space Placement Solver (`render_pro.py`)
Stickers are NEVER composited at static or blind coordinates. For every overlay, `render_pro.py` runs `calculate_intelligent_sticker_anchor`:
1. **Platform UI Safe Zone Enforcement**:
   - **Shorts (9:16)**: Strictly clears right-side engagement column (`x <= 860px` of 1080px width) and bottom control area (`y <= 1250px` of 1920px height).
   - **Long (16:9)**: Strictly clears television overscan and action safety boundaries (5% outer padding).
2. **Subtitle & Caption Collision Avoidance**:
   - Subtitle bounding box (`subtitles_center_y = 1180` in Shorts, `930` in Long) has a guaranteed minimum vertical buffer ($\ge 140\text{px}$ in Shorts, $\ge 80\text{px}$ in Long). No sticker ever touches or overlaps subtitles.
3. **Background Edge Density & Negative Space Evaluation**:
   - The scene background is sliced into candidate anchor regions (`top_right`, `top_left`, `mid_right`, `mid_left`, `center_high`).
   - `compute_negative_space_score(bg_im, x0, y0, x1, y1)` computes spatial luminance and gradient edge density across each candidate region.
   - The engine automatically docks the sticker into the candidate region with the highest open negative space and least visual clutter.
   - If the entire frame is densely cluttered, the sticker is auto-scaled down by `0.82x` to prevent overcrowding.

### B. Controlled, Tasteful Motion Physics
Sticker motion is calibrated for tactile, professional weight:
- **Calibrated Damped Spring Pop-in**: `spring_p(p) = 1.0 - (1.0 - p)**3`. Smooth cubic ease-out pop-in that settles cleanly within ~350ms with zero erratic overshoot wobble or hover jitter.
- **Smooth Continuous Drift**: Background shots subtly drift from `1.0` to `1.045` via smooth cosine easing (`_smooth_shot_motion`) across the scene duration with calm `0.22s` crossfades.
- **Multi-Slot Collision-Free Sticker Composition**: Unlimited simultaneous logical stickers (typically 1–4+ props) automatically distribute across distinct negative-space slots (`top_left`, `top_right`, `mid_left`, `mid_right`, `upper_center`, fine grid) with **`>= 32px` inter-sticker padding**, locked spawn-time `overlay_anchor_cache` (zero jitter/teleporting), and automatic spawn-time cohort scaling (`0.83x` at 3 props, `0.78x` at 4+).
- **Edge Restraint Rule**: When a sticker is docked near safe boundaries or subtitle buffers, entrance translation amplitudes are automatically dampened to prevent boundary clipping.

### C. Google Flow Visual QC & Bounded Auto-Rebuild Loop (`flow_smart_generator.py`)
Google Flow visual generation is continuously guarded by a self-healing verification loop:
- **Scene Aspect & Anti-Letterbox Guard (`verify_vertical_layout`)**:
  - Catches aspect ratio drift ($w/h > 0.65$ in Shorts) and detects horizontal letterbox or pillarbox bars ($\text{std} < 3.5$ in outer 12% pixel bands).
  - On failure, auto-refines the prompt with vertical composition directives (`"Tight vertical portrait shot, centered vertical composition, full bleed tall frame..."`) and retries.
- **Sticker Cutout Quality Guard (`verify_sticker_cutout`)**:
  - **Alpha Purity**: Verifies `alpha.min() == 0` and transparency ratio between $12\%$ and $98.5\%$.
  - **Chroma Halo Rejection**: Scans opaque subject pixels for unkeyed magenta fringe (`R > 175, B > 175, G < 90, (R-G) > 90, (B-G) > 90`). Rejects if magenta halo exceeds $1.8\%$ of subject pixels.
  - **Boundary Clipping Rejection**: Scans the 1-pixel outer border of the canvas. Rejects if opaque subject pixels occupy $> 15\%$ of the border perimeter.
  - On failure, auto-refines the prompt with high-contrast isolation directives (`"Isolated subject centered on pure solid flat magenta background #FF00FF, crisp clean dark outlines, ample negative margin..."`) and retries.
- **Bounded Retries**: All generation loops are bounded to **3 attempts maximum** to prevent runaway token/credit burn.

### D. The 6 Mandatory Pre-Render Quality Gates (`validate_pipeline.py`)
Rendering via `render_pro.py` is locked behind `validate_pipeline.py`. If ANY gate fails, rendering immediately aborts with explicit diagnostics:
1. **Gate 1: Scene & Sticker Manifest Completeness + Cutout QC**: All shots and stickers referenced in `SCENES_HYBRID.tsv` must exist cleanly via 3-tier resolution (Local -> `skills/stickman-stickers/assets/flow_vault/` -> `cc0_library/`) and pass alpha purity (`alpha.min() == 0`), halo (`<1.8%`), and boundary clipping checks.
2. **Gate 2: Native 9:16 Vertical Framing Purity**: For Shorts, all scene shots must pass aspect ratio ($w/h \le 0.65$) and letterbox/pillarbox border inspection ($\text{std} \ge 3.5$).
3. **Gate 3: 3-Stem Master Audio Integrity**: `mix_pro.wav` and `VO.wav` must exist, be non-silent (RMS $> 0.003$), broadcast voice chain verified (`highpass=85`, de-rumble, presence boost, `afftdn=nf=-28` noise floor, pause gate), with broadcast loudness calibrated to **-14.0 LUFS** ($\pm 1.0$) and melodic/rhythmic bed between **-12.5 dB and -14.5 dB** relative to Voice RMS (`0.0s` onset; windy/ambient drone beds banned; silky `3.0:1 / 550ms` ducking).
4. **Gate 4: Multi-Track Synchronization**: Verifies word-level alignment across `WORDS.tsv` $\leftrightarrow$ `SCENES_HYBRID.tsv` $\leftrightarrow$ `cues_pro.tsv`. Flags drift $> 100\text{ms}$ and ensures stickers bind tightly to spoken keywords.
5. **Gate 5: Dynamic Visual Effects & Archetype Enforcement**: Verifies editorial motion transitions (`slide_wipe`, `whip_blur`, `punch_settle`, `zoom_punch`, soft `crossfade`; cheap color overlays banned), sentiment-aware badges for `split_compare`, `card_stat` arrow clearance ($\ge 32\text{px}$), safe zone placement (subtitles at Y: 81%–88%, split content $\le \text{Y: 72\%}$), automated OCR text-leak detection, and standalone music-only outro separation.
6. **Gate 6: Real Unique Shot Density, Dual-Extreme Pacing, Director Plan & Pixel Balance Audit**: Rejects fake shot recycling (requires `max(10, dur/5.5)` unique shots in Shorts; `max(25, dur/7.5)` in Long), rejects BOTH dead stagnation (`>7.5s` Shorts / `>11.0s` Long) AND chaotic `<1.5s` flickering, rejects `A -> card -> A` ping-pong snap-backs, verifies `DIRECTOR_PLAN.json` via `director_supervisor.py` (0 `REJECTED_REDUNDANT` stickers, `-0.06s` `WORDS.tsv` lock, 6 motion archetypes, `cause_effect`/`duo_converge`/`trio_cascade`/`quad_showcase` choreography, animated draw-on Bezier arrows), and runs pixel inspection (`inspect_card_split_frame_pixels`) on `card_stat` and `split_compare` renders.

---

## 🔤 5.5. Editorial Typographic Hierarchy & The 9 Curated Editorial Looks

### A. The 4 Curated Fonts & Their Editorial Roles
Never use a single generic font for all text elements. The engine dynamically assigns dedicated typography for every editorial function:
| Font File | Role | Editorial Purpose |
|---|---|---|
| `PermanentMarker-Regular.ttf` | **Hero** | Giant stat numbers (`50,000 MILES`), split-screen headers (`BEFORE \| AFTER`), and chapter title cards |
| `Bangers-Regular.ttf` | **Stamp** | High-impact verdict stamps (`stamp_x`, `stamp_check`), shock callouts, and urgent hook words |
| `Caveat-Bold.ttf` | **Annotation** | Hand-drawn editorial annotations, timeline sub-labels, sketch callouts, and explanatory sub-texts |
| `SedgwickAve-Regular.ttf` | **Title** | Stylized title cards, evocative narrative phrases, and narrative chapter cards |
| `PatrickHand-Regular.ttf` | **Caption** | Alex Hormozi single-word kinetic subtitles with dynamic scaling and golden accent highlights |

### B. The 9 End-to-End Editorial Looks
Visual look presets define canvas paper background color, ink linework, card fills, accent highlights, and Flow prompt style tokens:
| Look Preset | Canvas Paper | Primary Ink | Card Fill | Accent | Characteristic Vibe |
|---|---|---|---|---|---|
| `bright` *(Canonical)* | `#FAF6ED` | `#111625` | `#FFFFFF` | `#FFCC00` | Clean 2D cartoon, daylight palette, fresh and modern |
| `warm` | `#F5ECD7` | `#2B1D0C` | `#FFFDF8` | `#D97706` | Warm parchment, amber tones, historic library bookplate |
| `night` | `#0B132B` | `#F0F4F8` | `#1C2541` | `#48CAE4` | Midnight navy paper, cyan neon glow, nocturnal science mystery |
| `ink` | `#F4F4F2` | `#0A0A0A` | `#FFFFFF` | `#E63946` | High-contrast black & white linework, editorial woodcut |
| `oversimplified` | `#FBF5E8` | `#18181B` | `#FFFFFF` | `#3B82F6` | Vibrant history comedy explainer, comic primary fills |
| `cgp_grey` | `#1E1E24` | `#FFFFFF` | `#2B2D42` | `#E76F51` | Minimalist grey slate, precise geometric diagrams |
| `casually_explained`| `#FCFBF7` | `#222222` | `#FFFFFF` | `#84A98C` | Pale ivory, deadpan cartoon, unhurried sketch aesthetic |
| `minute_physics` | `#181818` | `#FDFDFD` | `#242424` | `#FFE600` | Chalkboard aesthetic, fast white doodle illustrations |
| `painted` | `#F7F2E7` | `#1F2421` | `#FAF5EB` | `#9B5DE5` | Gouache brushwork, rich painterly washes, artistic texture |

---

## 📊 5.6. The 6 Broadcast Visual Archetypes (2x Lanczos Supersampling)
To match 10M+ view documentary benchmarks, all programmatic graphics are rendered at 2x resolution and downsampled via `Image.LANCZOS`:
1. `card_stat`: Full-bleed paper grain & dot-grid canvas with giant `PermanentMarker` hero stat (`75–85%` frame width), tapered highlighter swipe, annotation in `Caveat`, curved hand-drawn ink arrow, and grounded elliptical sticker shadow.
2. `split_compare`: Aspect-aware full-bleed contrast split — Top-vs-Bottom horizontal split above captions (`Y: 6%–72%`) on `9:16` Shorts, or full-height Left-vs-Right vertical split on `16:9` Long — with balanced stickers on both halves and compact corner `X`/`✓` verdict badges.
3. `bar_timeline`: Stepped editorial chronological spine (vertical in `Y: 8%–70%` on `9:16` Shorts, horizontal on `16:9` Long) with bold nodes, chevrons, tinted callout strips, and highlighted climax sticker.
4. `stat_pie`: Minimalist geometric percentage ring with prominent center stat, accent colored wedge, and negative-space sticker anchor.
5. `virtual_multicam`: Synthetic digital punch zooms (`zoom_in_tight`), panning tracking shots (`pan_left`), and crop focus on Flow hero art.
6. `verdict_stamps`: Animated `stamp_x` (red rejected) and `stamp_check` (green verified) with 3D drop shadows and physical impact shake.

---

## 📦 5.7. Production Upload Pack (`UPLOAD_PACK/`) & 2-Stage Intelligent Thumbnail Pipeline
- **Self-Healing Sticker Cutouts**: If chroma-keying (`key.py`) fails alpha transparency or fringe tests, the engine automatically routes to `cutout.py` (luminance/border flood-fill) and `delama.py` corner artifact eraser locally before requesting Flow re-generation.
- **2-Stage Intelligent Thumbnail Pipeline**:
  - **Stage 1 (Google Flow First Base Artwork - `flow_thumbnail_generator.py`)**:
    - Pre-flight check on Google Flow connector bridge (port 8791) via `flow-auto daemon status`.
    - Prompts crafted by `viral_seo_intelligence.py` + `headline-psychologist` + `loss-aversion-designer` with **STRICT NO-TEXT RULE** and intentional clean negative space (left 45% for 16:9, top-third for 9:16).
    - Multi-layer prompt audit with look palette directives (`warm`, `night`, `bright`, etc.) and strict negative prompts.
    - Dedicated 16:9 (`thumbnail_16x9_flow_raw.png`) and native vertical 9:16 (`thumbnail_9x16_flow_raw.png`) generation with non-blank QC and automatic high-contrast project candidate fallback if offline or `--no-flow-thumb`.
  - **Stage 2 (Spatial Solver & Supersampled CTR Polish - `thumbnail_generator.py`)**:
    - **Spatial Negative-Space & Safe-Zone Solver**: Scans edge density and luminance to place text away from faces. Strictly avoids the 16:9 bottom-right timestamp zone (18% W x 14% H) and Shorts 9:16 mobile UI margins (header, ticker, right-hand buttons).
    - **2x Supersampled Rendering (`LANCZOS` downsampling)**: Renders vector shapes, badges, and text at 2x resolution (`2560x1440` and `2160x3840`) before downscaling with `LANCZOS` for vector-grade crispness.
    - **Curated Font Hierarchy**: `PermanentMarker-Regular.ttf` for hero shock text, `Bangers-Regular.ttf` for curiosity badges, `Caveat-Bold.ttf` for editorial annotations.
    - **Auto-Contrast Guard**: Samples background luminance behind text bounding box, automatically injecting adaptive dark ink pills or heavy charcoal outlines.
    - **Selective Polish & 3-Element Rule**: High-emotion stickman + 1 visual anomaly + bold 2-4 word text + look-aligned subtle vignette.
- **Production Upload Packaging**: Every completed run populates `~/StickmanHybrid/<project>/UPLOAD_PACK/` with:
  - `thumbnail_16x9_flow_raw.png` & `thumbnail_9x16_flow_raw.png`: Dedicated Stage 1 raw base artwork.
  - `thumbnail_16x9.png` & `thumbnail_9x16.png`: Stage 2 broadcast-polished thumbnails.
  - `STAGE1_FLOW_AUDIT.json` & `STAGE2_CTR_AUDIT.json`: Detailed CTR, spatial placement, and prompt audit logs.
  - `METADATA.json`: SEO titles, description with timestamped chapters, and targeted tag clusters.
  - `POSTING_GUIDE.md`: Publishing instructions, pinned comment funnels, and platform safe-zone checklists.

---

## 🎨 6. Google Flow Visual Engineering & Strict 9:16 Vertical Rules

### A. The Canonical Art Style (`look: bright`)
All videos use the approved `look: bright` target from [boat_hi](file:///home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/example/boat_hi/STYLE.txt):
```
look: bright
hand-drawn 2D cartoon illustration for a history explainer channel, clean dark ink outlines, flat colours with soft shading, a bright natural and varied colour palette like a modern flat cartoon: clear blue skies, fresh greens, clean whites, light pastel walls, colourful objects, balanced neutral daylight. Not sepia, not brown, not golden or orange colour cast. Full-bleed background that fills the whole frame, simple and readable. People are simple round-head stick-figure characters with dot eyes and thin limbs. Crisp clean linework, clear readable composition, sharp high-quality detail, no blur, no muddy colours.
```

### B. Strict Native Vertical 9:16 Generation for Shorts
Flow/Imagen models place overwhelming spatial attention on the first 15–20 tokens. If a prompt mentions "landscape" or "savanna horizon", the model outputs a horizontal image inside a vertical frame. To guarantee true vertical composition:

1. **Front-Loaded Vertical Prefix**:
   ```
   A true full-height vertical 9:16 portrait illustration, tall mobile smartphone wallpaper framing: {scene description}. Tall vertical composition filling the complete mobile screen from top to bottom, vertical smartphone portrait orientation.
   ```
2. **Horizontal Keyword Sanitizer**: Automatically converts banned words:
   - `landscape` $\rightarrow$ `vertical scene`
   - `horizon` $\rightarrow$ `vertical vista`
   - `panoramic` $\rightarrow$ `tall framing`
   - `wide shot` $\rightarrow$ `full-body tall shot`
   - `split screen` $\rightarrow$ `vertically stacked frame`
3. **Universal Shorts Negative Prompt**:
   ```
   horizontal composition, widescreen framing, landscape layout, 16:9, letterbox bars, pillarbox, black bars, white borders, split frame horizontally, cinematic letterbox, panoramic view, wide angle horizon, distorted vertical stretch
   ```
4. **Mandatory Vertical Validation Guard (`verify_vertical_layout`)**:
   Before rendering, every image is tested:
   - Aspect ratio must be $\le 0.65$ (standard 9:16 is $0.5625$).
   - Standard deviation of top/bottom 12% pixel bands must exceed $3.5$ to detect letterbox bars. Any flagged image is automatically rejected and regenerated.

### C. Sticker Prop Generation (Chroma-Key Magenta `#FF00FF`)
All transparent stickers are generated at 1:1 aspect ratio against pure solid magenta `#FF00FF`:
```
One single isolated {object}, 2D cartoon style with clean dark ink outlines, flat colours with soft shading, matching the bright natural palette, placed perfectly centered against a solid flat pure magenta background #FF00FF, with no shadows, no floor, no table, no background clutter, no people. Absolutely no text, no watermark.
```
Keyed out using `key.py` (verifying `alpha.min() == 0` and transparency > 15%).

---

## ♻️ 5. Shared Sticker Prop Law (Mutual Asset Reuse)

> [!CAUTION]
> **NEVER generate separate duplicate stickers for Shorts and Long.**
> Cutout props are format-agnostic 1:1 transparent PNGs. An arrowhead or campfire created for Shorts can and must be reused in Long (and vice versa).

### Mutual Asset Registry Workflow (`asset_registry.py`)
1. **Registry Lookup**: Before asking Flow to generate any element, the engine queries `<project_root>/STICKERS_REGISTRY.json`.
2. **Semantic NLP & 80+ Concept Ontology**: Combines concept ontology families (40%), stemmed token Jaccard similarity (35%), and character 3-gram cosine similarity (25%). Matches abstract concepts (e.g., `"ancient footwear"` $\leftrightarrow$ `"leather sandals"`, `"dwelling"` $\leftrightarrow$ `"cave"`, `"weapon"` $\leftrightarrow$ `"spear"`). Threshold: 0.45.
3. **Bidirectional Format Sync**: The pipeline automatically re-scans and indexes `STICKERS_REGISTRY.json` after the Short visual asset pass and after the Long visual asset pass, guaranteeing mutual availability.
4. **Active Sticker Caps & Pre-emption (`render_pro.py`)**:
   - **Shorts (9:16)**: Max 1 active sticker at a time.
   - **Long (16:9)**: Max 2 active stickers at a time.
   - **Pre-emptive Ease-Out**: When a new sticker arrives, the oldest active sticker smoothly fades out over 0.22s before the new sticker pops in, eliminating visual clutter and subtitle overlap.
5. **Zero Duplicate Generation**: Flow is called **only** when no semantic match exists in the registry.

---

## ⏱️ 6. Mathematical Audio-Visual Synchronization

Never guess timestamps or use rough seconds in scene planning. Synchronization must be 100% time-locked:

1. **Forced Word Alignment (`align.py`)**: Whisper generates `WORDS.tsv` with start and end times for every spoken syllable.
2. **`line.i` Coordinate Notation**:
   - `01.0` = Line 01, Word 0 (exact millisecond start of sentence cut).
   - `+01.6` = Line 01, Word 6 (exact spoken onset of keyword where sticker reveals).
   - `03.11` = Line 03, Word 11 (instant mid-sentence pattern interrupt cut).
3. **Deterministic Alignment (`align_hybrid_scenes.py`)**:
   - Parses `SCENES_HYBRID.tsv` and maps every scene cut and overlay trigger to Whisper coordinates.
   - Prevents visual drift, orphan overlays, and cutouts persisting after scenes change.

---

## 🔊 7. Psychoacoustic Sound Design & 3-Stem Mastering

A video without professional sound design feels lifeless. Follow the Vox documentary psychoacoustic standard:

### A. The 3-Stem Routing Architecture (`mix.py`)
```
Voiceover (VO.wav) ───[vocal warmth eq]───> [vomix] ──────────────────────────┐
                                               │ (sidechain control)          │
SFX & Tactile Pops ───[catalog gain]──────> [sfxmix] (NOT ducked by voice) ───┼─> Master (-14 LUFS)
                                               │                              │
Music Bed ────────────[vocal notch eq]────> [bed_ducked] (ducked under voice) ┘
```

> [!IMPORTANT]
> **SFX is NEVER ducked by voice!**
> In previous versions, ducking the world track under voice caused dialogue to mute all sticker pops and tactile sound cues. In the upgraded engine, SFX routes cleanly to `[sfxmix]`, keeping tactile pops, paper slides, and keyword hits crisp and punchy while dialogue speaks.

### B. Sound Design Layers (`sfx_smart_designer.py`)
1. **Layer 1: Scene Transitions & Swishes**: Subtle paper whoosh or swish (`-11 dB` to `-12 dB`) on every scene cut. Pre-lapped by 120ms (J-cut) so the ear prepares the eye.
2. **Layer 2: Sticker Pops & Card Slams**: Tactile paper card slam, pop, or stamp hit (`-10 dB` to `-11 dB`) exactly when transparent cutouts appear. Pre-lapped by 90ms.
3. **Layer 3: Spoken Keyword Hits**: High-tension words (*danger, freezing, predator, blackout*) trigger resonant sub-thuds (`-11 dB` to `-13 dB`).
4. **Layer 4: Continuous Foley & Music Bed**: Thematic ambient foley loop (`-16 dB`) + documentary music score at `-12 dB` (Long) / `-11 dB` (Shorts) with vocal pocket carving (-3.2 dB at 1.8 kHz) and gentle 1.9:1 sidechain ducking.
5. **Broadcast Normalization**: Master mix strictly normalized to **-14.0 LUFS** ($\pm 1.0$ LUFS) and true peak $\le -1.0$ dBFS.

---

## 🎬 8. Intelligent Emotion & VFX Director (`vfx_smart_designer.py`)

Visual interest is maintained by dynamically matching visual effects to narration emotion:

| Effect Tag | Visual Effect | Narrative Trigger |
|---|---|---|
| `blood` / `danger` / `hazard` | Pulsating 1.2Hz crimson perimeter vignette | Biological peril, deadly predators, starvation, lethal wounds |
| `ice` / `cold` / `frost` | Cyan crystalline edge vignette | Freezing temperatures, blizzards, Ice Age, hypothermia |
| `bw` / `grayscale` | 92% desaturation with ink contrast tinting | Historical flashbacks, deep time rewind, extinct eras |
| `zoom_punch` | Kinetic 0.22s snap-in ($1.04\times \to 1.00\times$) | Opening hook reveals, paradigm shifts, shocking statistics |
| `shake` / `rumble` | Decaying sine camera shake ($\pm 12\text{px}$) | Explosions, catastrophic impacts, physical struggle |
| `drop` / `slam` | Vertical drop entrance with smooth ease | Heavy object, weapon, stone tool, fossil reveal |
| `calm_hold` *(default)* | Steady resting locked anchor (`overlay_anchor_cache`) | Keeps multi-sticker diagrams crisp without jitter/teleporting |

---

## 🎨 8.1 The 6 Full-Bleed Editorial Archetypes (Ink Explainer / Zenn / Mind Gems Standard)

All programmatic scenes are rendered full-bleed on the `--look` paper/slate canvas with **2x Supersampled Anti-Aliasing (LANCZOS downsampling)** — NO clunky boxed UI headers, NO heavy nested rectangles:

1. **Archetype 1: Flow Hero Illustrations** (`shots/*.png`): Primary narrative anchors in 2D stickman cartoon style with smooth continuous eased drift ($1.00 \to 1.045$) and 0.22s smooth crossfades between calm scenes.
2. **Archetype 2: Authoritative Camera Motion** (`pan_left`, `pan_right`, subtle ease): Smooth directional drifts across native Flow illustrations (NO abrupt mid-shot snap-cuts or recycled-image jitter).
3. **Archetype 3: Full-Bleed Minimalist Impact Frame** (`img: card_stat` or `card_phrase`, `text: 1177 BC | Eight Empires Connected`): Giant `PermanentMarker` hero metric accented with an organic highlighter marker swipe + minimal 2–5 word subtext directly on the canvas. **Seamless sticker pairing** uses a soft elliptical ground shadow beside/above typography with zero boxed trap.
4. **Archetype 4: Aspect-Aware Progressive Split Contrast** (`img: split_compare` or `split_contrast`, `text: MYTH: Barbarians Alone | REALITY: System Breakdown`): Warm-vs-cool full-bleed contrast halves separated by a dashed ink line (**Top-vs-Bottom horizontal split in `Y: 6%–72%` on `9:16` Shorts**; **full-height Left-vs-Right vertical split on `16:9` Long**), bold underlined headers, auto-resolved complementary stickers on both sides, compact corner `X`/`✓` badges, and progressive reveal synced to narration.
5. **Archetype 5: Hand-Drawn Verdict Accents** (`stamp_x`, `stamp_check`, `stamp_false`, `stamp_true`, `stamp_myth`): Crisp crimson brush `X` or emerald `✓` marks with clean underlined labels (no cheesy generic rubber stamps).
6. **Archetype 6: Progressive Data Timelines & Donut Rings** (`img: bar_timeline`, `img: stat_pie`): Progressive stepped spine timelines (vertical on 9:16 mobile, horizontal on 16:9 desktop) and animated donut percentage rings that build live as the narrator explains each step.

### Authoritative Clause-Locked Documentary Pacing (Zero Stagnation & Zero Rapid Flickering)
- **Shorts Body (9:16)**: Target **2.5s–4.0s** per clause-locked scene (min **1.8s** except explicit `rapid_list` beats; max **4.2s**; reject chaotic `< 1.5s` flickering). Minimum **15–20 unique Flow shots**.
- **Long-Form Body (16:9)**: Target **3.5s–5.5s** per clause-locked scene (min **2.2s**; max **6.5s**; reject `< 1.5s` flickering). Minimum **50–70 unique Flow shots**.
- **Strict Linear Progression**: Always advance linearly ($A \to B \to C \to D$); never ping-pong back to a previous shot across an archetype card.
- **Audio Target**: Warm cinematic bed between **-11 dB and -13 dB** relative to Voice RMS (`mix.py`), normalized to `-14.0 LUFS`.

---

## ✍️ 9. High-Retention Scriptwriting Engine (`script_architect.py`)

Scripts must never be flat, generic, or read like a textbook. They must follow the **Competitor Retention Narrative Blueprint**:

```
Act 1: Present-Day Mirror Hook (0-15s)    ──> Direct 2nd-person address ("Tum/Aap") linking modern daily life to ancient mystery
Act 2: Myth-Flip & Historical Complication ──> Popular misconception exposed, stamped FALSE (stamp_x), stakes established
Act 3: Mechanical / Named Proof Loop      ──> Exact named sources, archaeological proof, physical mechanism explained
Act 4: The Escalating Crisis / Siege      ──> Extreme environmental collapse, tactical conflict, or sensory breakdown
Act 5: Twist Revelation & Open Loop       ──> The Vox Drop-Out (0.8s micro-silence) + paradigm-shifting discovery
Act 6: Full-Circle Emotional Payoff       ──> Return to opening hook question with deep psychological revelation (NO subscribe begging)
```

- **Retention Rules**:
  - **Present-Day Mirror Hook**: Immediately place the viewer inside the premise within 3 seconds using 2nd person ("Tum", "Aap", "Imagine you").
  - **Myth-Flip Loop**: Challenge a widespread assumption before providing the real mechanism.
  - **Escalation & Open-Loop Bridges**: Maintain forward momentum across transitions ("Lekin yeh sirf shuruat thi...", "Asal twist yahan se shuru hota hai...").
  - **Conversational Spoken Urdu / Roman Urdu**: Natural, punchy spoken rhythm without robotic, archaic, or textbook Urdu.
- **Pacing**: Vary sentence length. Short 2–4 word punch lines follow explanatory clauses.
- **Dynamic 6 Companion Skills Extraction**: `script_architect.py` dynamically extracts actionable directives from `emotional-arc-designer`, `visual-emotion-engineer`, `data-storytelling`, `headline-psychologist`, `loss-aversion-designer`, and `youtube-seo-optimizer` directly into `SCRIPT_SPEC.json`.
- **Automated Bilingual Voiceover via Kaggle API (`kaggle_runner.py`)**: For Urdu/Roman Urdu audiences, narrate via Indic Parler (Aman). Uses credentials from repo root `.env` (`/home/mirza-ahmed-hassan/Desktop/stickman-animation/.env`) or `~/.kaggle/kaggle.json` (protected by `.gitignore`), pushes the kernel, polls status every 15s, downloads takes, joins, and aligns with Whisper.
- **Continuous RL Learning & Self-Tightening (`evaluate_rl.py` + `rl_memory.py`)**: Aggregates real deductions across pacing, broadcast LUFS, and spatial density to automatically tighten cuts and enforce active sticker caps in future runs.

---

## 💬 10. The 5 Mandatory Intake Questions & 3 User Checkpoints

> [!CAUTION]
> **HARD INTAKE RULE FOR ALL AGENTS**:
> **NEVER start generating scripts, assets, or running `studio.py` until all 5 answers are collected.**
> Do NOT assume any default topic, format, language, length, or caption style.
> When a new session starts (or the user asks to make an animation), ask these 5 questions in **ONE clean, structured message** in the user's language (Roman Urdu / Urdu / English) with no pre-selected defaults:
> 1. **Topic**: What topic do you want the video on? (Aap apna topic bata dein ya main 10 viral topics suggest karoon?)
> 2. **Language**: Narration language?
>    - English (Kokoro `am_michael`, 100% local CPU)
>    - Urdu / Roman Urdu (`urdu_vo.py`, Kokoro-82M + EspeakG2P, `hm_omega` / `hf_alpha`, 100% local CPU commercial-safe; Indic Parler Kaggle fallback)
>    - Other languages
> 3. **Format**:
>    - `1) Long (16:9 Landscape)`: Full 1920x1080 documentary for YouTube / TV
>    - `2) Shorts (9:16 Vertical)`: Fast 1080x1920 viral video for YouTube Shorts / TikTok / Reels
>    - `3) Both (16:9 Long + 9:16 Short)`: Dual decoupled pipelines (independent Flow art, shared stickers)
> 4. **Length**: Target duration? (e.g. 60s, 2m, 5m, or auto)
> 5. **Captions**:
>    - `1) Yes (With Captions)`: Alex Hormozi single-word kinetic subtitles with golden glow
>    - `2) No (Without Captions)`: Clean cinematic visuals without subtitles

Once the user answers all 5 questions, create the project and present only these **3 clean approval checkpoints**:

```
[5 Questions Answered] ──> Generate Script + Lock Storyboard (Gate 0) ──> [CHECKPOINT 1: Approve Script & Master Storyboard]
                                                                                   │ (Approved)
                                                                                   ▼
                             Generate Voice, Look & Assets ──────────────> [CHECKPOINT 2: Approve Voice & Style]
                                                                                   │ (Approved)
                                                                                   ▼
                                  Render Video & RL QC ──────────────────> [CHECKPOINT 3: Deliver Final Video]
```

> [!IMPORTANT]
> **MANDATORY CHECKPOINT 1 PRE-SPEND GATE 0 STORYBOARD LOCK:**
> At **Checkpoint 1**, the agent must generate `LINES.tsv`, `SCENES.tsv`, and immediately run:
> ```bash
> python3 studio.py storyboard <project_dir> --strict
> ```
> This compiles human-readable `STORYBOARD.md` and machine-readable `STORYBOARD.json`, and enforces Gate 0 pre-flight validation (auditing card spoken-word triggers, readable hold floors `>=2.0s`/`2.6s`, zero consecutive duplicate shots, zero red arrow leaks, and literal sticker matches) **BEFORE spending any Google Flow visual compute or TTS audio compute**. Only when Gate 0 passes is the storyboard presented to the user for Checkpoint 1 approval.



### Conversational Etiquette
- Talk to the user in their own language (typically Roman Urdu or English), simply and politely.
- Keep commands, filenames, and file paths strictly in English.
- Always provide clickable markdown links with absolute paths: `[video.mp4](file:///path/to/video.mp4)`.
- Never guess URLs or fabricate API keys.

---

## 🛠️ 12. Master Command Cheat Sheet

### The All-in-One Engine Orchestrator
Execute the complete, end-to-end pipeline with one unified command:
```bash
# Full creation pass with automatic Phase 2 Creative Director & Visual QC:
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/studio.py \
    create "What Did Ancient Humans Actually Do at Night?" \
    --lang en --format both --captions

# Test execution up to the 4 Quality Gates without rendering MP4:
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/studio.py \
    create "What Did Ancient Humans Actually Do at Night?" \
    --lang en --format both --captions --dry-run
```

### Granular Stage-by-Stage Commands
Run individual stages from within the project directory (`cd ~/StickmanHybrid/<slug>/<short_or_long>`):

```bash
# 1. System Health Check
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/studio.py doctor

# 2. Start Flow Bridge (Local Chrome Extension on port 8791)
flow-auto bridge start

# 3. Generate Script (Dual Retention Architecture & Narrative Intelligence)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/script_architect.py \
    --topic "What Did Ancient Humans Actually Do at Night?" --format both

# 4. Generate Voiceover (Kokoro English)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/vox-doc-sound/scripts/kokoro_vo.py \
    LINES.tsv --lang a --voice am_michael --speed 1.0

# 5. Join Takes & Calibrate Gaps
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/vox-doc-sound/scripts/vo_join.py \
    takes LINES.tsv --out VO

# 6. Whisper Forced Word Alignment
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/vox-doc-sound/scripts/align.py \
    --vo VO.wav --lines VO.tsv --lang en

# 7. Word-Level Scene & Sticker Synchronization
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/align_hybrid_scenes.py .

# 8. Enrich Contextual Visual Effects (VFX Director)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/vfx_smart_designer.py .

# 9. Query & Centralize Shared Asset Registry
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/asset_registry.py .

# 10. Generate Flow Visuals (Stickers & Scenes with Cutout & 9:16 Visual QC)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/flow_smart_generator.py elements
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/flow_smart_generator.py shots --aspect=9:16  # (or 16:9)

# 11. Generate Psychoacoustic Sound Design & 3-Stem Mix
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/sfx_smart_designer.py .
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/vox-doc-sound/scripts/mix.py \
    cues_pro.tsv --vo VO.wav --lines VO.tsv --words WORDS.tsv --out mix_pro.wav

# 12. Run the 4 Mandatory Pre-Render Quality Gates
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/validate_pipeline.py . --format 9:16

# 13. Render Final Video (Intelligent Spatial Placement, Calibrated Spring Motion, 0-Clutter Layout)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/render_pro.py \
    --format 9:16 --audio mix_pro.wav --scenes SCENES_HYBRID.tsv --words WORDS.tsv --out video_short_9x16.mp4

# 12b. Unified Director Gate 0 & Clean-Context Critic Pass (Max 1 Fix Round)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/studio.py director . --pre-spend --warn-only
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/studio.py sheets video_short_9x16.mp4

# 14. End-to-End Quality Control & RL Verification (includes fast 192px signal scan + qa/ sheets)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/studio.py qc .
```

### Pre-Delivery Clean-Context Critic Pass
Before handing any rendered `.mp4` to the user:
1. Run `studio.py sheets <mp4>` (or `studio.py qc .`) to export `qa/hook_sheet.jpg` (`0-3s`), `qa/phone_sheet.jpg` (`1fps`), and `qa/beats_sheet.jpg` (`12` narrative beats) plus the `<10s` signal QA report (`F_STUTTER`, `F_FLASH_FRAME`, `F_NO_SILENCE_DROP`, `F_METRONOME`, `F_READ_TOO_FAST`).
2. Inspect the 3 contact sheets fresh — verify `0-3s` hook clarity, exact 50/50 split balance, card hold legibility, and zero label/subtitle collision. Run **at most 1 targeted fix round** before delivery.

---

## 🚨 13. Troubleshooting & Anti-Patterns Reference

| Symptom | Root Cause | Immediate Fix |
|---|---|---|
| **Stickers completely missing in rendered video** | `render_pro.py` unconditionally added all scene indices to `natively_consumed_indices`, swallowing overlays on standard shots before compositing | `render_pro.py` now restricts `natively_consumed_indices` strictly to archetype cards (`card_stat`, `split_compare`). Added **Runtime Compositing Counter** exporting `sticker_telemetry.json` with fatal error if scheduled stickers render 0 frames. |
| **Intro background music silent or delayed** | Music had slow 1.0s-2.0s fade-in combined with VO sidechain ducking suppressing music below -35 dBFS | `sfx_smart_designer.py` sets Act 1 music to `0.0s` start with `fade_in: 0.3`. `mix.py` adaptive balancer enforces -12 to -15 dB Bed-to-VO ratio, logged in `stem_telemetry.json`. |
| **SFX / VFX too quiet or visually imperceptible** | SFX had static weak gains (-16 dB); VFX had tiny 12px shake and 1.06x zoom | Calibrated SFX gains (-3.5 to -5 dB). Camera shake boosted to 26–32px (power 1.8 spring decay); punch zoom boosted to 1.10–1.12x; edge vignettes boosted to 160–200px. |
| **Fake 100/100 RL-QC scores ignoring defects** | `evaluate_rl.py` only checked file presence and codecs without inspecting rendered MP4 pixels or stem telemetry | Upgraded `evaluate_rl.py` with real forensic checks: verifies `sticker_telemetry.json` (-25 pts if 0 stickers), stem audio ratios (-20 pts if music silent or SFX masked), and video motion deltas (-15 pts if static). |
| **Dynamic Bar Charts (`bars:`) skipped** | `render_pro.py` overlay loader checked only file existence, missing `bars:` tag | `render_pro.py` now directly delegates `bars:` overlay rows to `draw_bars`. |
| **VFX / Transitions fail silently** | Tags (`danger`, `ice`, `fade`) placed in wrong TSV columns (`pos` or `space`) | Multi-Column VFX Robustness Gate in `render_pro.py` inspects `extra`, `pos`, and `space` combined. |
| **Stickers vanish after 2s in long scenes** | Hardcoded 2.2s TTL left 4–8s of empty static frame | Adaptive Sticker Lifetime Gate scales hold duration to 3.5s–5.5s in Long documentary. |
| **Numeric sticker filenames collide across pipelines** | Sequential names (`01.png`) represent different items in Shorts vs Long | Use descriptive semantic slugs (`mattress.png`, `sabertooth_skull.png`) in `elements/cut/`. |
| **Shorts image generated in landscape** | Prompt started with landscape/environmental keywords | Front-load prompt with `"A true full-height vertical 9:16 portrait illustration..."` and ensure `verify_vertical_layout` passes. |
| **Sound effects inaudible during narration** | Previous double-ducking bug muted SFX when voice spoke | Use upgraded `mix.py` with 3-stem routing (`[sfxmix]` is NOT ducked by voice). |
| **Duplicate stickers generated** | Sibling pipeline didn't check central registry | Run `asset_registry.py .` before prompting Flow; check `STICKERS_REGISTRY.json`. |
| **Scene cuts or stickers drifting out of sync** | Guessed second timestamps used instead of words | Re-run `align_hybrid_scenes.py .` to time-lock cuts to Whisper `WORDS.tsv`. |
| **Flow generation times out or hangs** | Stale Chrome tab or dialog popup | Run `flow-auto cancel && flow-auto reload` and retry prompt submission. |
| **Audio loudness fails platform QC** | Manual volume tweaks broke normalization | Always run `mix.py`, which normalizes master output strictly to **-14.0 LUFS**. |
| **Stickers overlap character face** | Center occlusion guard violated | Stickers must be anchored strictly in peripheral quadrants ($y \le 0.44H$ in Shorts, $y \le 0.48H$ in Long). |

---

## 🗺️ 13. Skills Ecosystem Map

The repository integrates these specialized skill systems:
- **`skills/stickman-hybrid/`**: Master visual, full-bleed editorial archetype, collision-free multi-sticker, kinetic captioning, and video rendering engine.
- **`skills/stickman-stickers/`**: Permanent 3-tier reusable sticker vault (`assets/flow_vault/` Tier 1 + `assets/cc0_library/` Tier 2 + live Google Flow auto-harvest + `CATALOG.tsv`).
- **`skills/vox-doc-sound/`**: Voiceover synthesis, Whisper alignment, 1,600+ sound catalog, and 3-stem psychoacoustic audio mixing (-11 to -13 dB bed, -14 LUFS).
- **`skills/youtube-seo-optimizer/`**: High-RPM metadata, search intent keywords, and chapter markers.
- **`skills/emotional-arc-designer/`**: Peak-end rule emotional arousal curve modeling.
- **`skills/visual-emotion-engineer/`**: Arousal-valence visual contrast and color temperature engineering.
- **`skills/loss-aversion-designer/`**: Framing high-stakes evolutionary survival consequences.
- **`skills/data-storytelling/`**: Narrative structure for complex archaeological/scientific data.

---
*End of Master AI Agent Startup Guide. Pin this file as your primary instruction set for all Stickman Hybrid animation production.*
