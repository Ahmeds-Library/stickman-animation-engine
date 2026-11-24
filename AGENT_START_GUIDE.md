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
| **8** | **3-Stem Audio Mastering** | Route audio into `[vomix]` (voice), `[sfxmix]` (SFX), and `[bed_ducked]` (music bed). **SFX is NEVER ducked under voice**. Broadcast target: **-14.0 LUFS**. |
| **9** | **Intelligent Emotion & VFX Directing** | Automatically inject contextual visual FX (`vfx_smart_designer.py`): hazard vignettes, frost vignettes, monochrome flashbacks, camera shake, and punch zooms. |
| **10** | **The 3 User Checkpoints** | Only pause for user input at: **1. Script Approval**, **2. Voice/Look Approval**, and **3. Final Video Delivery**. |

---

## 📁 3. System Architecture & Directory Layout

### Workspace Structure
```
/home/mirza-ahmed-hassan/Desktop/stickman-animation/
├── AGENT_START_GUIDE.md               # This authoritative onboarding manual
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
│   │   │   ├── validate_pipeline.py  # 4-Gate Pre-Render Quality Gate
│   │   │   ├── render_pro.py         # Broadcast multi-layer video renderer with active sticker caps
│   │   │   ├── evaluate_rl.py        # Autonomous RL QC evaluator with deduction aggregation
│   │   │   ├── rl_memory.py          # Continuous RL learning memory & self-tightening policies
│   │   │   └── studio.py             # CLI studio orchestrator & QC validator
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
- **Calibrated Damped Spring Pop-in**: `spring_p(p) = 1.0 - exp(-8.5 * p) * cos(8.0 * p)`. Replaces harsh linear jumps with a crisp, tactile 2D paper pop-in that settles smoothly within 240ms without oscillating jitter.
- **Micro Ken Burns Drift**: Background shots subtly scale from `1.0` to `1.025` over the scene duration, giving cinematic organic life without dizzying pans.
- **Edge Restraint Rule**: When a sticker is docked near safe boundaries or subtitle buffers, motion translation amplitudes (`drop`, `slam`, `hover`) are automatically dampened by 70% to prevent transient boundary clipping.

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

### D. The 4 Mandatory Pre-Render Quality Gates (`validate_pipeline.py`)
Rendering via `render_pro.py` is locked behind `validate_pipeline.py`. If ANY gate fails, rendering immediately aborts with explicit line-numbered diagnostics:
1. **Gate 1: Scene & Sticker Manifest Completeness + Cutout QC**: All shots and stickers referenced in `SCENES_HYBRID.tsv` must exist on disk and pass cutout transparency, halo (<1.8%), and clipping (<15%) checks.
2. **Gate 2: Native 9:16 Vertical Framing Purity**: For Shorts, all scene shots must pass aspect ratio and letterbox border inspection.
3. **Gate 3: 3-Stem Master Audio Integrity**: `mix_pro.wav` and `VO.wav` must exist, be non-silent (RMS $> 0.003$), have valid duration, and `cues_pro.tsv` must contain calibrated cues.
4. **Gate 4: Multi-Track Synchronization**: Verifies word-level alignment across `WORDS.tsv` $\leftrightarrow$ `SCENES_HYBRID.tsv` $\leftrightarrow$ `cues_pro.tsv`. Flags drift $> 100\text{ms}$ between visual reveals and sound cues, and verifies audio duration locks to the visual scene timeline.

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
| `drop` / `slam` | Vertical drop entrance with bounce impact | Heavy object, weapon, stone tool, fossil reveal |
| `hover` / `breathing` | Subtle sinusoidal float ($\pm 5\text{px}$) | Keeps sticker props organically alive while lingering on screen |

---

## 🎨 8.1 The 6-Archetype Visual Variety Engine & Real Sticker Integration

To hold audience retention without overwhelming image generation, our pipeline dynamically interweaves 6 distinct visual archetypes in `SCENES_HYBRID.tsv`. All programmatic cards are rendered with **2x Supersampled Anti-Aliasing (LANCZOS downsampling)**, comic drop shadows, warm paper texture matching primary shots, and native transparent sticker compositing:

1. **Archetype 1: Flow Hero Illustrations** (`shots/*.png`): Primary narrative anchors. Hand-drawn 2D cartoon style on warm paper with bold black ink outlines. 1-2 word-synced stickers per shot.
2. **Archetype 2: Virtual Multi-Cam Cuts** (`crop_focus`, `zoom_in_tight`, `pan_left`, `pan_right` in `extra`/`pos`/`space`): Re-uses the high-res Flow illustration (1536x2752 / 2752x1536) to cut instantly into close-up (1.32x), tight punch (1.38x), or pan framing on narrative beats without waiting on new image generation.
3. **Archetype 3: Minimalist Kinetic Impact Cards** (`img: card_stat` or `card_phrase`, `text: 53,000 MILES | Built by hand`): Big bold stat/number with spring animation and accent bar on clean paper card. **Pairs natively with 1 real sticker** (`roman_soldier.png`) positioned in balanced negative space with a soft comic ground shadow.
4. **Archetype 4: 50/50 Split Contrast Frames** (`img: split_compare` or `split_contrast`, `text: MYTH: Slaves Built It | REALITY: Professional Soldiers`): Clean center dashed ink divider with dual tint halves and label pills. **Supports 1 sticker per side** (Left vs Right) centered inside each half with optional verdict stamps (`stamp_x` / `stamp_check`) stamped over each side.
5. **Archetype 5: Animated Myth-Buster Verdict Stamps** (Overlay `img: stamp_x`, `stamp_check`, `stamp_false`, `stamp_true`, `stamp_myth`): Big animated red cross (✕) or green checkmark (✓) stamp with 2x supersampled ink rings, physical impact spring hit, and audio slam/chime.
6. **Archetype 6: Programmatic Data & Timeline Cards** (`img: bar_timeline`, `text: STATUMEN: Deep sand | RUDUS: Crushed rock | NUCLEUS: Gravel | PAVIMENTUM: Basalt slabs` or `img: stat_pie`, `text: 75% | OF EMPIRE CONNECTED`): Animated progressive timeline bar and donut metric cards. **Supports contextual accent sticker(s)** anchored cleanly outside the chart/bar bounding box without covering any labels or numbers.

### High-Density Visual Pacing & Beat Velocity
- **Opening 15s Hook Density**: 1.2s–2.2s visual beat (scene cut or animated overlay).
- **Shorts Body (9:16)**: Target cut 1.5s–2.5s; max hold 3.0s (flagged if > 3.0s).
- **Long-Form Body (16:9)**: Target cut 2.2s–3.8s; max hold 4.5s (flagged if > 4.5s).
- **Rapid List Micro-Beats**: 0.8s–1.4s per beat with synchronized micro-SFX on each reveal.

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
>    - English (Kokoro `am_michael`, local CPU)
>    - Urdu / Roman Urdu (Indic Parler `Aman` on Kaggle free GPU)
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
[5 Questions Answered] ──> Generate Script ──> [CHECKPOINT 1: Approve Script]
                                                           │ (Approved)
                                                           ▼
                    Generate Voice, Look & Assets ──> [CHECKPOINT 2: Approve Voice & Style]
                                                           │ (Approved)
                                                           ▼
                         Render Video & QC ─────────> [CHECKPOINT 3: Deliver Final Video]
```



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

# 14. End-to-End Quality Control & RL Verification
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/studio.py qc .
```

---

## 🚨 13. Troubleshooting & Anti-Patterns Reference

| Symptom | Root Cause | Immediate Fix |
|---|---|---|
| **Stickers completely missing in rendered video** | `+` overlay rows were placed at bottom of TSV, or seconds treated as invalid word indices | `align_hybrid_scenes.py` now resolves float seconds to nearest words and `render_pro.py` enforces automatic chronological overlay re-parenting. |
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
- **`skills/stickman-hybrid/`**: Master visual, layout, sticker cutout, kinetic captioning, and video rendering engine.
- **`skills/vox-doc-sound/`**: Voiceover synthesis, Whisper alignment, 1,600+ sound catalog, and 3-stem psychoacoustic audio mixing.
- **`skills/youtube-seo-optimizer/`**: High-RPM metadata, search intent keywords, and chapter markers.
- **`skills/emotional-arc-designer/`**: Peak-end rule emotional arousal curve modeling.
- **`skills/visual-emotion-engineer/`**: Arousal-valence visual contrast and color temperature engineering.
- **`skills/loss-aversion-designer/`**: Framing high-stakes evolutionary survival consequences.
- **`skills/data-storytelling/`**: Narrative structure for complex archaeological/scientific data.

---
*End of Master AI Agent Startup Guide. Pin this file as your primary instruction set for all Stickman Hybrid animation production.*
