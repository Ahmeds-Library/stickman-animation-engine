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
│   │   │   ├── render_pro.py         # Broadcast multi-layer video renderer
│   │   │   └── studio.py             # CLI studio orchestrator & QC validator
│   │   └── looks/                    # Visual style definitions (bright.md is canonical)
│   └── vox-doc-sound/                # Voiceover, alignment & audio mixing engine
│       ├── SKILL.md                  # Voice & psychoacoustic sound specifications
│       ├── CATALOG.tsv               # 1,600+ indexed CC0 SFX and music files
│       └── scripts/
│           ├── kokoro_vo.py          # English neural voiceover (am_michael / am_fenrir)
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

## 🎨 4. Google Flow Visual Engineering & Strict 9:16 Vertical Rules

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
2. **Semantic NLP Matching**: Uses token containment and synonym trees (e.g., `"sabertooth skull"` matches `"sabretooth tiger skull"` or `"skull"`).
3. **Automatic Sibling Sharing**: If an asset was generated in `short/elements/cut/`, it is automatically registered and symlinked/copied to `long/elements/cut/` (and centralized in `<project_root>/elements/cut/`).
4. **Zero Duplicate Generation**: Flow is called **only** when no semantic match exists in the registry.

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
1. **Layer 1: Scene Transitions**: Subtle paper whoosh or swish (`-20 dB` to `-23 dB`) on every scene cut. Pre-lapped by 120ms (J-cut) so the ear prepares the eye.
2. **Layer 2: Sticker Pops**: Tactile paper card place or bubble pop (`-15 dB` to `-17 dB`) exactly when transparent cutouts appear. Pre-lapped by 90ms.
3. **Layer 3: Spoken Keyword Hits**: High-tension words (*danger, freezing, predator, blackout*) trigger 60Hz resonant sub-thuds (`-17 dB` to `-19 dB`).
4. **Layer 4: Continuous Foley & Music Bed**: Thematic ambient foley loop (`-23 dB`) + documentary music score at `-17 dB` (Long) / `-16 dB` (Shorts) with vocal pocket carving (-3.2 dB at 1.8 kHz) and gentle 2.8:1 sidechain ducking.
5. **Broadcast Normalization**: Normalized to **-14.0 LUFS** ($\pm 1.0$ LUFS) and true peak $\le -1.0$ dBFS.

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

## ✍️ 9. High-Retention Scriptwriting Engine (`script_architect.py`)

Scripts must never be flat, generic, or read like a textbook. They must follow the **6-Act YouTube Retention Tension Curve**:

```
Act 1: Modern Paradox Hook (0-15s)  ──> Relatable modern comfort vs brutal evolutionary baseline
Act 2: The Rewind (15-60s)           ──> Time jump into raw prehistoric stakes
Act 3: Mechanical Breakthrough (1-3m)──> Fire, tools, social sentinel sleep, evolutionary adaptation
Act 4: The Crisis / Peril (3-5m)     ──> Catastrophic predator siege, sensory deprivation, nightmare
Act 5: Twist Revelation (5-7m)       ──> The Vox Drop-Out (0.8s silence) + paradigm-shifting discovery
Act 6: Philosophical Return (7-10m)  ──> Connect back to viewer's modern life (NO subscribe begging)
```

- **Pacing**: Vary sentence length. Short 2–4 word punch lines follow explanatory clauses.
- **Bilingual Support**: For Urdu/Roman Urdu audiences, narrate via Indic Parler (Aman) at 1.0x with warm conversational cadence.

---

## 💬 10. The 3 User Checkpoints & Interaction Etiquette

Do not badger the user with minor technical questions. Present only these 3 clean checkpoints:

```
[Start Session] ──> Generate Script ──> [CHECKPOINT 1: Approve Script]
                                                    │ (OK)
                                                    ▼
             Generate Voice, Look & Assets ──> [CHECKPOINT 2: Approve Voice & Style]
                                                    │ (OK)
                                                    ▼
                   Render Video & QC ────────> [CHECKPOINT 3: Deliver Final Video]
```

### Conversational Etiquette
- Talk to the user in their own language (typically Roman Urdu or English), simply and politely.
- Keep commands, filenames, and file paths strictly in English.
- Always provide clickable markdown links with absolute paths: `[video.mp4](file:///path/to/video.mp4)`.
- Never guess URLs or fabricate API keys.

---

## 🛠️ 11. Master Command Cheat Sheet

Run all commands from within the project directory (`cd ~/StickmanHybrid/<slug>/<short_or_long>`):

```bash
# 1. System Health Check
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/studio.py doctor

# 2. Start Flow Bridge (Local Chrome Extension on port 8791)
flow-auto bridge start

# 3. Generate Script (Dual Retention Architecture)
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

# 10. Generate Flow Visuals (Stickers & Scenes with 9:16 validation)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/flow_smart_generator.py elements
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/flow_smart_generator.py shots --aspect=9:16  # (or 16:9)

# 11. Generate Psychoacoustic Sound Design & 3-Stem Mix
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/sfx_smart_designer.py .
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/vox-doc-sound/scripts/mix.py \
    cues_pro.tsv --vo VO.wav --lines VO.tsv --words WORDS.tsv --out mix_pro.wav

# 12. Render Final Video (Hormozi Captions, Kinetic VFX, 0-Clutter Layout)
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/render_pro.py \
    --format 9:16 --audio mix_pro.wav --scenes SCENES_HYBRID.tsv --words WORDS.tsv --out video_short_9x16.mp4

# 13. End-to-End Quality Control & RL Verification
python3 /home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/scripts/studio.py qc .
```

---

## 🚨 12. Troubleshooting & Anti-Patterns Reference

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
