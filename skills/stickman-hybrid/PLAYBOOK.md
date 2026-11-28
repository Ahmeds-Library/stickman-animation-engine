# Stickman explainer playbook

> [!IMPORTANT]
> **SINGLE SOURCE OF TRUTH & ARCHITECTURAL MANDATES**:
> All agents must follow [AGENT_START_GUIDE.md](file:///home/mirza-ahmed-hassan/Desktop/stickman-animation/AGENT_START_GUIDE.md) and [SKILL.md](file:///home/mirza-ahmed-hassan/Desktop/stickman-animation/skills/stickman-hybrid/SKILL.md).
> 1. **5 Mandatory Intake Questions**: Never assume defaults on new videos; collect all 5 answers before code execution.
> 2. **External Project Directory**: All project media, scripts, and upload packs live strictly in `~/StickmanHybrid/<project_slug>/` outside this repo.
> 3. **Production Renderer**: Rendering is executed via `render_pro.py` (multi-font hierarchy, anti-aliased archetypes, active sticker caps, and post-mux audio validation). `render_pro.py` now routes directly to `render_pro.py`.

These are the rules and the method behind stickman documentaries in the style of the big
"ancient humans" and stick-figure explainer channels. The method was worked out by studying
nine reference videos (14M, 1.2M, 855K, 385K views and others) and then making test films
until the reviewer approved them.

---

## Part 1: The rules (each one came from a measurement or a rejection)

1. **Still pictures, not animation (motion only from stickers).** Over two-minute stretches, the reference videos are
   92-99% frozen frames: no pan, no zoom, no AI video. What keeps viewers watching is a new
   picture every 2-3 seconds that shows exactly what is being said. Never add Ken Burns
   moves or video-model clips. In this pack the stills carry cut-out stickers that pop in on
   the words (§9); that is the only motion.

2. **Pace like the viral video, and measure it.** `validate_pipeline.py` checks every hold where nothing
   changes on screen: over 2 s in the first 30 s, over 3.5 s after that. Fix every hold with a beat
   on a spoken word before rendering:
   - a cut to another picture
   - a sticker
   - a counter or a tag
   - a "no" sticker for "no fridge, no freezer, no packet" (see §9)

   Each beat must be something the line names; never add one just to fill time. A reviewer found
   12-16 s spans with one frame and asked for "zyada frame, lekin script ke acc". The re-paced Urdu / Roman Urdu film went from 60 to 96 changes, with 24 in the hook.
   The viral reference:  The 14M-view reference has 292 shots in 11 minutes:
   - first 30 s: one picture every ~1.2 s
   - 30-120 s: one every ~1.8 s
   - after that: one every ~2.6 s

   Its median shot is 2.1 s. Aim for a mean of 2.0-2.6 s, a faster hook, and no shot
   longer than ~6 s.

3. **The picture shows the sentence, literally.** Plan every scene from the voiceover line it
   serves:
   - "Rice. Bread. Curry." means three quick close-ups.
   - "A chimpanzee spends six hours chewing" means a chimp chewing, with a clock.

   A shot list written before the narration produced films where nothing matched. Cut on the
   spoken word (WORDS.tsv), never on a guessed time.

4. **One cast, one look, all video long.**
   - Make one character sheet.
   - Split it into one reference per character (`pictures.py refs`).
   - Attach the right reference to every shot that has that character.

   With the whole sheet attached, Flow pasted the sheet's line-up into the scene, and drew
   the wrong character.

5. **Every picture is a full, colourful scene.**
   - White or empty backgrounds were rejected.
   - A whole film in golden ochre was "too brownish".
   - Pick the look by topic (`looks/README.md`) and keep its palette line in every prompt.
   - Before the batch, test 2 shots and look at them.

6. **Text only where the picture cannot say it.** The reference channels let the picture
   carry the line. A label on every shot was rejected ("they don't use captions, remove
   them"). Put text only on:
   - a number or date: "~6 HOURS A DAY", "1498"
   - a person's name: "RICHARD WRANGHAM | HARVARD"
   - a place on a map: "NORTHERN ITALY"
   - a term that cannot be drawn: "BEESWAX", "DATUN (NEEM)"

   That came to 11-13 tags in a 2-minute film. In Urdu text, put digits and Latin punctuation on a line of their own (`पीटर ड्यूरंड|1810`) and leave out colons: in the handwritten font a `1` reads as `।` and a `:` as `ः`. A line that is only digits and Latin letters is drawn in the Latin font. Text is drawn in code, so spelling is always
   right, and it is placed automatically in the quietest corner, never over a face. Tags
   placed by hand ended up "in the characters' mouths".

7. **Data is drawn in code.** Percentages go in a bar chart (`bars:RAW=51,COOKED=91`). Text
   cards ("AND HERE'S THE STRANGE PART...") work as beats; use 6-10 in 2 minutes. Cards and
   charts cost no picture credits.

8. **The hook follows a fixed formula.**
   1. Start with the viewer's normal day: "This morning, you picked up a plastic stick..."
   2. Rewind: "Rewind fourteen thousand years."
   3. Ask the big question.
   4. Answer it with escalating discoveries and a twist.
   5. End by sending the viewer back to their own life, with no "subscribe" ending.

9. **Facts are checked, and doubt is said aloud.** Use numbers and names that come from
   sources. Phrase debated ideas as "some scientists think... others say the evidence isn't
   strong enough yet". Never invent studies, dates or quotes.

10. **Flow returns pictures under the wrong number.** In every batch, 2-6 pictures came back
    swapped. One file was named "sofa" but showed the savanna animals. Always look at
    `review.jpg` and fix swaps in `PICK.tsv`. Never trust file numbers.

11. **Duplicate text elimination.** Never display the same text twice simultaneously. If an overlay
    tag displays an object name (e.g. `BONE NEEDLE`), suppress the scene header banner. Scene text is
    reserved for full-screen question/beat cards or major chapter markers.

12. **Pure transparent cutouts only (no opaque boxes).** Never use circular cream badges or crop
    the scene image onto itself. All sticker props must have `alpha.min() == 0`, be chroma-keyed
    on pure magenta `#FF00FF` with `key.py`, and be positioned strictly in peripheral zones
    (`0.78, 0.28` or `0.22, 0.28`), never blocking the center focal point (`0.5, 0.48`).

13. **Strict single-word kinetic subtitles (Alex Hormozi style).** When captions are enabled,
    render strictly the single word currently spoken by the voice at that exact millisecond. Never
    display a multi-word window showing past or future words. Screen stays clean during natural
    speech pauses.

14. **Dedicated 30–60s viral shorts (Both format).** When "Both" format is selected, generate a
    dedicated 30–60 second viral hook clip (typically Lines 01–14) with native 9:16 vertical
    illustrations and an animated cliffhanger CTA card driving viewers to the full 16:9 documentary.

15. **Self-healing Flow generation.** Use `flow_smart_generator.py` with automatic error dialog
    clearing (`flow-auto cancel` + `reload`), prompt synonym sanitization (replacing filter words
    like "louse" with "microscopic bug creature"), and `flow-auto assets --json` download fallback
    to guarantee zero skipped props.

16. **Intelligent VFX & sound design mapping.** Sound effects must serve the narrative with surgical
    precision. Never add generic arcade pops, plucks, or clicks. Use this strict mapping:
    - **Hook / Question / Title card**: Subtle paper whoosh (`Paper/whoosh_subtle.ogg`, -24 dB) or soft riser.
    - **Time Jump / Rewind**: Cassette rewind or clock tick (`rewind_clock.ogg`, -22 dB).
    - **Sticker / Prop Pop**: Quiet paper card-place (`Paper/card-place-1.ogg`, -26 dB).
    - **Dramatic Twist / Danger / Climax**: Sub-bass soft thud impact (`impact_soft_thud.ogg`, -22 dB).
    - **Environmental Ambience** (Campfire, Blizzard, Savanna): Low-level ambient loop (-28 dB).

17. **Intelligent prop placement & anti-occlusion guard.** Every prop's screen location is validated
    before placement:
    - **Subject Safety Zone**: The center bounding box ($0.35 \le x \le 0.65, 0.35 \le y \le 0.65$) is
      strictly reserved for the main scene subject and characters. Stickers are NEVER placed here.
    - **Peripheral Anchor Zones**: Stickers are strictly anchored to quiet peripheral quadrants:
      Top-Right (`0.78, 0.28`), Top-Left (`0.22, 0.28`), Bottom-Right (`0.80, 0.68`), Bottom-Left (`0.20, 0.68`).
    - **Collision Avoidance**: If two stickers appear in the same scene, they are automatically separated.
    - **No Redundant Overlays**: If the full scene picture already shows the subject in close-up
      (e.g., a macro shot of the body louse or bone needle), no sticker overlay is added on top.

18. **Strict visual style lock & universal negative prompt engine.** To guarantee 100% style
    uniformity across all 36+ frames:
    - **Style Anchor Lock**: Every scene prompt must inherit the exact style tokens from `STYLE.txt`
      (e.g., warm painterly digital art, golden ochre and fur tones, storybook illustration).
    - **Universal Negative Prompt**: Enforced in `pictures.py` and `flow_smart_generator.py`:
      `3D CGI, hyperrealistic photography, glossy 3D render, realistic human face, photorealistic skin texture, stock photo, watermark, logo, text, subtitles, distorted anatomy, modern artifacts in prehistoric scenes, anime, inconsistent art style`.
    - **Character Reference Locking**: Individual cropped character references (`img/ref_<name>.jpg`)
      must be attached to every scene prompt featuring that character.

19. **Intelligent voice cadence & punctuation pauses.** Narration must never rush:
    - **Punctuation Breathing Room**: `kokoro_vo.py` automatically detects punctuation and inserts
      natural human acoustic pauses: commas (0.42s), full stops (0.52s), list items (0.65s),
      ellipses (0.70s), question marks (0.60s), exclamation marks (0.55s).
    - **List Pacing**: Short 1-word punchy items (e.g. "Shirt. Pants. Socks.") are synthesized
      at a calm 0.82x cadence with a deliberate 0.65s pause between each item so visual stickers
      pop with ample breathing room. Short 2-3 word clauses speak at 0.86x.

20. **Absolute visual style lock & zero style mixing (Cartoon & Stickman Purity).**
    - **100% Artistic Cohesion**: If the chosen look is 2D stickman cartoon, EVERY SINGLE visual element
      (scenes, props, sticker cutouts, cards, shorts) must strictly adhere to that exact 2D cartoon style.
      Never allow a single frame, background, or prop to drift into photorealism, 3D CGI, glossy digital
      gradients, or realistic human depiction.
    - **Strict Stickman Character Anatomy**: Every human character across all scenes must have stickman
      anatomy: clean round white/paper head, dot eyes, simple ink line mouth/brows, and thin stick limbs.
      No realistic faces, no photorealistic skin textures, and no detailed anatomical musculature.
    - **Stickers & Props Style Match**: All cutout props (`elements/cut/*.png`) must be illustrated in the
      same hand-drawn 2D cartoon aesthetic with matching ink stroke weights, painterly texture, and
      warm palette from `STYLE.txt`.
    - **Universal Negative Prompt**: Appended to every Flow prompt to permanently ban photorealism, 3D
      renders, realistic faces, anime, and style drift.

21. **Mutual Sticker & Asset Registry Standard (Zero-Waste Reuse).**
    - **Zero Duplicate Cutouts**: Transparent prop cutouts are format-agnostic 1:1 elements. A sticker made for Shorts can and must be reused in Long (and vice versa).
    - **Registry Query (`asset_registry.py`)**: Sibling pipelines check `<project_root>/STICKERS_REGISTRY.json` before prompting Google Flow.
    - **Semantic NLP Matching**: Token containment and synonym trees prevent duplicate generation (e.g. "sabertooth skull" matches "sabretooth tiger skull").
    - **Centralized Assets**: Cutouts are saved to `<project_root>/elements/cut/` and symlinked/copied to `short/` and `long/`.

22. **Strict Native Vertical 9:16 Flow Architecture & Letterbox Guard.**
    - **Positional Token Weighting**: Flow/Imagen text encoders prioritize the first 15–20 tokens. Prompts must be front-loaded with:
      `"A true full-height vertical 9:16 portrait illustration, tall mobile smartphone wallpaper framing: {scene}. Tall vertical composition filling the complete mobile screen from top to bottom, vertical smartphone portrait orientation."`
    - **Keyword Sanitizer**: Automatically converts horizontal words (`landscape` $\to$ `vertical scene`, `horizon` $\to$ `vertical vista`, `panoramic` $\to$ `tall framing`).
    - **Universal Shorts Negative Prompt**: Enforces exclusion of horizontal composition, widescreen framing, letterbox bars, and borders.
    - **Validation Guard (`verify_vertical_layout`)**: Before rendering, every image is tested for vertical aspect ratio ($\le 0.65$) and top/bottom band variance ($\sigma > 3.5$) to reject letterbox bars.

23. **Deterministic Audio-Visual Synchronization (`align_hybrid_scenes.py`).**
    - All cuts, transitions, and sticker reveals are mathematically time-locked to Whisper `WORDS.tsv` coordinates (`line.i` notation).
    - Resolves timeline drift and orphan overlays.

24. **Intelligent Emotion & Contextual VFX Directing (`vfx_smart_designer.py`).**
    - Automatically enriches scenes with contextual visual effects: `blood`/`danger` (pulsing crimson vignette), `ice`/`cold` (cyan crystalline frost vignette), `bw`/`grayscale` (flashback), `zoom_punch` (kinetic snap), `shake`/`rumble` (peril impacts), and `hover` (living motion).

25. **3-Stem Psychoacoustic Audio Mastering (`mix.py`).**
    - Audio is routed into 3 dedicated stems: `[vomix]` (voiceover), `[sfxmix]` (SFX and foley), and `[bed_ducked]` (music bed).
    - **SFX is NOT ducked by voice**, ensuring tactile pops, whooshes, and paper slides remain crisp and punchy while dialogue speaks. Music bed is sidechain-ducked under voice. Broadcast target: -14.0 LUFS.

26. **Mandatory Visual Sticker Verification & Zero-Empty-Scene Gate.**
    - Every non-card scene must feature at least one contextual sticker cutout, dynamic counter, or infographic bar chart landing on a spoken keyword.
    - Bare image holds exceeding 3.5s with zero stickers or counters are strictly flagged as defective.

27. **Overlay Placement & Local Parenting Gate.**
    - In `SCENES_HYBRID.tsv`, every `+` overlay row MUST be placed immediately under the scene row it belongs to.
    - Appending overlays at the end of the TSV file is strictly forbidden. `render_pro.py` and `align_hybrid_scenes.py` enforce automatic chronological re-parenting.

28. **Multi-Column VFX & Transition Robustness Gate.**
    - `render_pro.py` inspects `extra`, `pos`, and `space` for transition tags (`fade`, `crossfade`, `flash`, `cut`) and VFX tags (`danger`, `blood`, `ice`, `shake`, `zoom_punch`, `bw`).
    - Eliminates silent VFX dropouts caused by minor TSV column misalignments.

29. **Semantic Asset Naming Standard (Ban on Numeric IDs).**
    - Sticker files must use descriptive semantic nouns/slugs (e.g., `mattress.png`, `sabertooth_skull.png`) rather than arbitrary numeric filenames (`01.png`, `02.png`).
    - Eliminates cross-pipeline namespace collisions between Shorts and Long.

30. **Adaptive Sticker Lifetime & Screen Density Standard.**
    - In long-form documentary scenes ($>5.0\text{s}$), sticker hold duration must dynamically adapt to $3.5\text{s} - 5.5\text{s}$ ($\approx 70\%$ of scene duration) to prevent premature disappearance and empty screens.

---

## Part 2: The pipeline

```
topic + language + length
  └─ SCRIPT.md ──> LINES.tsv (id, text, gap)                    [user approves the script]
        ├─ in parallel ─> STYLE.txt + cast ──> character sheet ──> pictures.py refs
        │                   └─> SHOTS.tsv ──> pictures.py submit 1 N (test) ──> submit (rest)
        └─ in parallel ─> voice (vox-doc-sound) ──> VO.wav + VO.tsv ──> align.py ──> WORDS.tsv
  WORDS.tsv + SHOTS.tsv ──> SCENES.tsv (cue on words, text only where needed)
  downloads ──> pictures.py review ──> PICK.tsv ──> pictures.py pick ──> img/sNN.jpg
  cues.tsv ──> mix.py ──> mix.wav
  render_pro.py ──> <project>.mp4 ──> pictures.py qc ──> qc.jpg (Claude checks it, fixes, re-renders)
```

---

## Part 3: Step by step

### §1 Topic and script

**Topic list,** if the user wants one:
- Give 8-10 titles that each carry one sharp question ("How Did Ancient Humans Clean Their
  Teeth?", "Why Are Humans the Only Animals That Cook?").
- Each needs a visual journey: from today, to the past, through discoveries, and back.
- Urdu / Roman Urdu audiences: give the title in both languages, for example "انسانوں نے ممالک کیوں بنائے؟ / Insano ne mulk kyu banaye? Why Did Humans Create Countries?".
- Proven niches: ancient humans' daily life, survival, food, the body, inventions, "what if".

**SCRIPT.md:** conversational and spoken.
- Address the viewer as "you", "imagine", "here's the strange part".
- Vary sentence length, with short punch lines after longer ones.
- Every paragraph answers one question and opens the next (a curiosity loop).
- Structure: hook → big question → context → first discovery → problem → bigger discovery →
  twist → bigger picture → modern ending. No timestamps, no headings in the narration.

**Length:** English Kokoro speaks about 155-165 words a minute. Urdu / Roman Urdu narration (Indic Parler, Aman) runs about 25% longer for the same meaning: a 2-minute English script became 2:47 in Urdu / Roman Urdu. Write about 25% fewer words for Urdu / Roman Urdu: the voice is never sped up (§4). Always join Parler
takes with `vo_join.py`; if it still runs long, cut words, do not go faster. Write to the user's chosen length. After the voice is made, cut lines if it runs
long.

**LINES.tsv:**
- One sentence or short beat per row: `id  text  gap`.
- Short lines give more cut points.
- `gap` is the silence after the line:
  - 0.15-0.3 inside a thought
  - 0.4-0.6 at a full stop or a question
  - 1.0-1.2 after the last line

Example: `example/teeth/LINES.tsv`.

### §2 Look and cast
1. Pick the look from `looks/README.md`. Write `STYLE.txt`: line 1 `look: <name>`, then the
   look's STYLE paragraph, adapted to the topic.
2. Decide the cast from the script:
   - "you" (the modern person)
   - one or two story characters, such as a caveman, a farmer or a scientist

   Background people are not cast. Costumes such as an Egyptian or a Ming craftsman are
   changes written into a shot's prompt, on top of the same face.
3. Character sheet:
   - One Flow text-to-image with `--outputs 2`, using the look's sheet prompt and
     `--folder stick_<project>_sheet --wait`.
   - Keep the cleaner one. All views must be the same person, with no text.
4. Split it: `python <skill>/scripts/pictures.py refs <sheet.jpg> --names modern,caveman`.
   - Characters must not be cut in half.
   - If they are not evenly spaced, pass `--cuts 0.51` (a fraction of the width).
   - Look at each `img/ref_*.jpg`.

### §3 SHOTS.tsv (pictures)

**Columns:** `id  ref  prompt`.
- `ref` is `-` for no character, a cast name, or `sheet` for a shot with the whole cast.
- Write the prompt as one literal scene: who does what, where, with what, plus the light and
  colour of that moment.

**Budget:**
- About one picture per 3 seconds of film (2 min = 38-44 pictures), plus 6-10 text cards.
- Reuse a picture when the narration stays on it:
  - a second scene with a tag added
  - a bar chart that grows from one value to two

**Prompt rules:**
- Objects and food: add "no people", or random background characters appear.
- Maps: "simple cartoon map of <region>, no text, no borders, a red location pin on
  <place>". Rough is fine; text is added in code.
- A costume change: "The modern man as a professor, now wearing round glasses and a tweed
  jacket...". The face stays from the reference.
- Never ask the image for words, numbers or labels. `pictures.py` adds "no text" to every
  prompt.
- Model: Nano Banana 2 (Flow labels it "Nano Banana 2.1") for scenes and stickers, never Pro.
  `pictures.py` uses it by default (`STICK_MODEL`).
- Ask for clean, clear pictures: the project's STYLE.txt ends with "Crisp clean linework,
  clear readable composition, sharp high-quality detail, no blur, no muddy colours."

**Order:**
1. `pictures.py submit 1 <a character shot>` (2 shots). Look at both. If the look or the cast
   is wrong, fix STYLE.txt or the refs now.
2. `pictures.py submit <the rest>`. It submits everything without waiting, in batches of
   `STICK_BATCH` (default 4).

### §4 Voice: in parallel with the pictures
Use the vox-doc-sound skill.

**Which engine:**
| Narration language | Engine | First speaker |
|---|---|---|
| Urdu, Roman Urdu | **Indic Parler-TTS** on Kaggle (`kaggle/make_parler_job.py --speaker Aman`) | **Aman, always first** |
| Bengali, Marathi, Tamil, Telugu, Gujarati and other Indian languages | **Indic Parler-TTS** on Kaggle | a native speaker of that language (see the vox-doc-sound docs) |
| English, Spanish, French and other non-Indian languages | Kokoro (`kokoro_vo.py --speed 1.0`), local | `am_michael` |

- Never use Kokoro for Urdu: it sounds flat.
- Urdu / Roman Urdu fallbacks, only if the user wants a different voice after hearing Aman: Kabir,
  Bhanu, Dinesh, Aakash. Rohit sounds robotic.

**Then:** `vo_join.py` gives `VO.wav` and `VO.tsv`, and `align.py --lang <code>` gives
`WORDS.tsv`. The user approves the voice from two lines.

**Pace and pauses (approved by ear, 2026-10-20):** Indian languages: make_parler_job.py's defaults (`natural` description, seed 11) and NO speed-up; `vo_join.py` adds +0.3 s to every pause. English and other languages: Kokoro `--speed 1.0`, every pause +0.35 s (~3.0 words/s). Never pass `--tempo`: speeding Parler up 1.10-1.25x is what made every first Urdu film sound robotic. A line vo_join flags `RE-MAKE` gets voiced again with another seed (`--only NN --seed 12`), never sped up. The full rules are in the vox-doc-sound
SKILL.md, "Narration that sounds alive".

**Kaggle queue: reassure the user, ask, never decide alone.**

Sometimes `kaggle kernels status <user>/<job>` says `QUEUED` for 30 minutes to 2 hours. **This
is normal, not an error.** Kaggle's free T4 GPUs are shared by everyone, and the queue is
longest in the Indian evening and night (the US daytime). Now and then a job also sits in the
queue with no visible reason. Nothing is wrong with the job, and nothing is lost.

1. **Tell the user at once, calmly, in their language**, so they don't worry. In Hinglish,
   for example: "Kaggle ka free GPU abhi busy hai, isliye Aman ki awaaz queue mein hai. Yeh
   normal hai, koi error nahi. Tab tak main pictures ka kaam kar raha hoon."
2. Check `kaggle kernels list --mine`. Any other job of the user's that is `RUNNING` takes one
   of the 2 GPU slots; mention it. Push only ONE voice job at a time. Two queued copies do not
   start faster.
3. Keep working on everything that does not need the voice: pictures, review, PICK.
4. Check the status every ~10 minutes, without asking the user each time.
5. After ~60 minutes of `QUEUED`, ask the user in one message:
   - **a) Keep waiting.** It usually starts within 1-2 hours.
   - **b) Push the same job once more.** Run `kaggle kernels push -p <job folder>`. A stuck
     job sometimes starts at once after this. It is harmless, but not guaranteed.
   - **c) Push it in the Indian morning,** when the queue is shortest. Meanwhile the
     pictures can be finished.
   - **d) Check the weekly GPU quota** (about 30 h a week) on https://www.kaggle.com/settings.
     When it is used up, the job cannot start until the quota resets.
   - **e) Run Parler on this computer.** Give the honest cost for THIS machine, using its
     RAM and GPU from SETUP_STATUS.md:
     - strong machine: a separate `parlerenv` (SETUP Step 6)
     - weak machine: may be very slow, may swap, or may crash

     The user may still choose it.
   - **f) Their own recording, or their ElevenLabs key.**
6. Do what the user picks. Never fill the wait with another TTS voice, and never start a local
   install without the user's OK.

### §5 SCENES.tsv: cut on the words
Columns are `cue  img  text  pos  extra`:
- `cue`: `line.word`, for example `14.5` is the 6th word of line 14 (counting from 0).
- Leave `pos` empty; render_pro.py chooses the spot.

**How to cut:**
- Read each line in WORDS.tsv and cut when the line names a new thing.
  Example: "Bread(10.0). Porridge(10.1). Grain(10.2)" gives three scenes.
- **Hook** (first ~30 s): cut on every noun.
- **Later:** cut on each new idea, at most ~6 s per shot.
- **Text cards:** `card` with the words in `text`, using `|` for a new line. Use them for
  beats, questions and twists.
- **Reusing one picture:**
  - add a tag on its second scene, on the word that names the number
  - two consecutive rows with the same picture and the same text are one scene; merge them
- **Bar charts:** `extra` = `bars:RAW=51,COOKED=91`. The picture stays; the chart sits on
  the right.

Example: `example/teeth/SCENES.tsv` (51 scenes, 2:10, 13 tags).

### §6 Collect the pictures
**Theme consistency comes first.** Every picture of a film must match that film's own chosen
look (STYLE.txt): the same detail level, brightness and palette. Do not add a fixed style
sentence to every prompt; the look differs per topic.
- In `review.jpg`, look for an outlier that does not match the others and regenerate only that
  shot. A reviewer spotted one dense, detailed jungle shot among flat bright ones ("theme se
  match nahi kar raha").
- Fix it by describing that one scene more simply, in the same terms as its neighbours.

1. `pictures.py review`: look at `review.jpg`. Each tile shows the download's number.
2. For every picture that belongs to another shot, write it in `PICK.tsv` (`shot  file`).
3. If a picture is wrong, regenerate only that shot: `pictures.py submit <id>`. A rewritten
   prompt keeps the same id.
4. `pictures.py pick` copies the pictures into `img/sNN.jpg` and warns about byte-identical
   duplicates.
5. LaMa erases the Flow sparkle **in parallel**:
   - Right after the first `pictures.py submit`, start
     `python <skill>/scripts/delama.py --watch` in the background. It cleans every download
     the moment it lands, about 3 s each, into a cache keyed by the file's content. Flow's
     mispaired numbers therefore do not matter.
   - After `pictures.py pick`, run `python <skill>/scripts/delama.py`. It only copies the
     cleaned pictures into `img/clean/`, so it is instant. render_pro.py uses them.
   - Do not render or run `align.py` while the watcher is still running on a machine with 8 GB
     of RAM or less. Whisper alignment died with `mkl_malloc: failed to allocate memory` when
     both ran together. Stop the watcher first (`delama.py` without --watch finishes the rest),
     and always check that WORDS.tsv was actually written.
   - If LaMa was skipped at setup, render_pro.py's smooth fill is used instead.

### §7 Sound
Use the vox-doc-sound skill: write `cues.tsv` on words, then `mix.py`. Keep it light:
- a music bed at -23: the `explainer` mood for most videos, `explainer_lofi` for cosy ones,
  `mystery` or `tension` for `night`. Keep `history_serious` for truly grave topics: under a
  curious explainer it made the narration sound flat
- about 10 one-shots in 2 minutes, only where the picture shows the sound:
  - a film rewind on "Rewind"
  - a soft paper slam on a twist card
  - fire crackle on fire
  - a quiet paper "card-place" (`sfx/Kenney_CC0/Paper/card-place-1/2.ogg`, gain -25) on a map pin
    or a sticker, sparingly
  - NEVER pops, plucks, clicks or pizzicato jingles (`PopClick/*`, `Tonal/jingles_*`,
    `Map/b5_country_pop_*`) on stickers or beats. A reviewer called the pop sound "bahut bekar".
  - Not every sticker needs a sound. A run of stickers (a list) gets one sound on the first

Silence is fine. If a sound is missing, vox-doc-sound says how to make one.

### §8 Render and check
1. `python <skill>/scripts/render_pro.py`. It uses mix.wav if present, else VO.wav. The look
   comes from STYLE.txt, and it writes `<project>.mp4`.
2. `python <skill>/scripts/pictures.py qc`, then open `qc.jpg` yourself. Check:
   - pictures in the right order
   - no tag over a face
   - no Flow sparkle left (delama.py, or render_pro.py's fallback fill)
   - no leftover sheet line-ups
3. Fix the problems, re-render, and only then show the user.

### §9 The hybrid look (the default of this pack): stills + cut-out stickers

**Three rules from the reviewer's last round:**
1. **The scene picture comes first; never shape it for a sticker.** Write SHOTS prompts as full,
   natural scenes, the way the approved `food` film was made.
   - Stickers go to the quietest spot the picture already has, such as sky, ground or a wall
     (`auto`). render_pro.py keeps them off faces, white stickman bodies, skin and the centre.
   - When a picture has no calm spot, put that line's stickers on a plain collage card right
     after it.
   - A test that forced empty left/right/top areas into the pictures (the `space` column) was
     rejected: "left right center wala aacha nahi lag raha". Leave `space` empty. It still exists
     in pictures.py but is not used by default.
2. **Split the work: the scene shows the place and the action; the line's named objects are
   stickers.**
   - Write SHOTS prompts without the small objects the line names. Example: "the caveman stands
     on the bank staring across the river", without "a fruit tree and fish".
   - Put those objects in ELEMENTS: fruit, fish, rope, a kangaroo.
   - They then pop into the scene's quiet spot on the word, and every main frame gets 1-2 related
     stickers.
   - When Flow paints the object into the scene anyway, a sticker of it would only repeat it.
     That is how a film ends up with few stickers; the reviewer asked for more and for no repeats.
   - Maps get a sticker of what the line says happened there: a kangaroo on Australia, the
     dugout on the Netherlands.
3. **More stickers, all related.** About one sticker per scene picture, plus collage cards with
   2-4 stickers. A film with few stickers "felt boring". Every sticker shows something the line
   names that the picture does not already show.
4. **Text: none on scene pictures.** On-screen text lives only on the big beat and question cards
   ("SO HOW DID PEOPLE TELL TIME?") and on collage cards, in English even for an Urdu / Roman Urdu narration.
   No tags, labels or counters on scene pictures.
This is the stills film with Vox-style cut-outs added on top. It has the same script, voice
and scene pictures. A small set of sticker PNGs then pops in on the spoken words:
- objects such as the toothbrush, the beeswax or a flint
- character poses
- animated counters ("0 → 14,000 YEARS AGO")
- tags
- now and then a paper collage beat, for example three toothbrushes on a timeline:
  1498 → c. 1780 → 1938

This pack always makes it. A reviewer approved it as the main style.

1. **ELEMENTS.tsv** (`id  ref  object`): about 1 sticker per 6-8 seconds. Each row is one
   object, or one character pose (ref = a cast name). Write what the narration names but the
   picture does not already show large.
   - **Never a sticker that repeats the picture.** No match sticker on a match-striking scene,
     no grass nest when the caveman already holds one.
   - **Never a decoration on a word that does not name it.** No spark on "garam".
   - Where no sticker truly fits, fill the hold with a CUT to a picture the line describes
     ("kabhi bujhne nahi diya" cut to the man guarding the fire). A reviewer called repeated
     and unrelated stickers out.
2. `pictures.py elements 1 4` to test two, then `pictures.py elements` for the rest. They are
   generated on magenta, 1:1.
3. `pictures.py cutouts` keys them to `elements/cut/NN.png`. Look at `cutouts.jpg`. Flow swaps
   these too: fix them in `ELPICK.tsv` (`shot  file`), then delete `elements/cut` and run
   cutouts again.
4. **SCENES.tsv overlay rows.** A row whose cue starts with `+` belongs to the scene above it
   and pops in on that word:
   - `+15.5  elements/cut/10.png  tiny scratch marks  auto,0.4  pop`
   - `+06.1  count  14000|YEARS AGO  0.7,0.5,0.42  rise`
   - `+03.0  tag  2 MINUTES  auto,0.3  pop`
   - A paper collage beat is a scene row with `card` and no text, plus overlay rows with
     fixed `x,y,h`.
   - Motions: `pop` (default), `slideL`, `slideR`, `rise`.
   - **"No X" moments** ("no smoke, no fire", "no fridge"): generate the sticker with the sign
     already inside it. A red X drawn in code looked cheap to a reviewer; do not use `pop+x`.
     The ELEMENTS row:

     "<object>, with a bold red prohibition sign drawn directly over it: one thick solid red circle
     and one thick red diagonal slash, flat red with a thin dark outline, NO white outline, NO
     white border, NO sticker edge around the sign or the object, the magenta background shows
     through inside the circle around the object"

     In SCENES use `pop+plain`, so render_pro.py adds no white sticker border. A white rim and a black
     and white stroke looked wrong on these. Keep them small, 0.32-0.36 high, close together near
     the centre; big ones looked odd.
5. `render_pro.py` sees the `+` rows and renders frame by frame at 30 fps (about 1.5 minutes for a
   2-minute film). `auto` picks the quietest free spot.
   - Big white stickman heads are counted as busy, because plain edge detection called them
     empty and a sticker landed on a head.
   - Auto placement prefers the corners and the top, and keeps off the centre, where the main
     element usually is. Auto stickers are at most 0.34 of the frame high (default 0.3), and tag
     text is small (70 px; 60 px under a sticker). A reviewer found bigger text and centred
     stickers covered the main subject.
   - Two stickers in one scene never overlap: render_pro.py measures each one with its label and
     pushes them apart, shrinking them if they cannot fit.
   - After `pictures.py qc`, pin any sticker that still sits near a face to a fixed `x,y,h`.
   - Flow also swaps files ACROSS folders: a scene picture once landed among the stickers and a
     sticker among the scenes. Move such a file into the right folder, renamed to the right
     number, then pick and cut out again.
6. **Re-voicing in another language:**
   - The new voice is usually longer (Urdu / Roman Urdu ran about 13-25% longer). Keeping the same beats
     stretches every hold, so run `validate_pipeline.py` and add beats on the new language's words
     until no hold is left.
   - Copy `img/`, `elements/`, `STYLE.txt`, SHOTS and ELEMENTS, then translate LINES.tsv line by
     line, keeping the ids.
   - Make the new voice and WORDS.tsv (`align.py --lang hi`).
   - Rewrite only SCENES.tsv: cues on the new words, text in the new language.
   - No new pictures are needed. See `example/food_hi`.

Examples: `example/food/` (17 stickers, 28 overlays, 37 scenes), `example/food_hi/` (the same
film in Urdu / Roman Urdu), `example/teeth_hybrid/` (20 stickers, 29 overlays, 47 scenes).

---

## Part 4: Flow, as it actually behaves

- **Swapped pictures** happen in every batch (see rule 10). Fix them with PICK.tsv.
- **Repeated submissions.** One extension build re-submitted the same prompt up to 4 times
  when it missed a finished picture. The duplicates arrive as "N - name (1).jpg";
  `pictures.py` always takes the first.
- **"We noticed some unusual activity"** refuses one prompt and pauses the queue 5-10
  minutes on its own. When the queue is empty, re-submit only those ids. Never retry at
  once.
- **After `flow-auto stop` or `queue clear`, wait 1-2 minutes before submitting again.**
  Submitting at once drew a warning.
- **`--new-project` on its own can leave Flow sitting on the project gallery.** If nothing
  starts within a few minutes:
  1. `flow-auto stop --site flow`, then `flow-auto reload-extension --site flow`.
  2. Test one shot without `--new-project`.
  3. Submit the rest.
- **The plan reads "free" and the queue is PAUSED:** the extension's own side panel must be
  open, or the extension licence must be active. Ask the user to open the panel. Flow's PRO
  badge is the Google plan, not the extension licence.
- `flow-auto doctor --site flow` is the first command for anything unexplained. Relay its
  own words.

---

## Part 5: Credits

- **Flow credits** go only on pictures: about 40 for a 2-minute film, plus the sheet and
  any retries. The hybrid look adds about 20 stickers. Cards, tags, charts, the voice, the mix and the render are free.
- **Claude usage** grows with conversation length and with every image looked at.
  - QC from grids (`review.jpg`, `qc.jpg`), never frame by frame. One grid costs the same as
    one frame.
  - Start a new chat for each new video. PROGRESS.md makes "continue" work anywhere.

---

## Checklist before showing the video

- [ ] Script approved; facts checked, debated points worded as such
- [ ] Look matches the topic; 2 test shots looked at before the batch
- [ ] Every character shot used the right per-character reference
- [ ] SCENES cut on spoken words: mean shot 2.0-2.6 s, hook faster, none over ~6 s
- [ ] Text only for numbers and dates, names, map places and unseen terms; 6-10 cards
- [ ] review.jpg checked and PICK.tsv written; no duplicates
- [ ] Mix at -14 LUFS, voice on top, a few SFX on the words
- [ ] qc.jpg checked by you; tags off faces; re-rendered after fixes
- [ ] Licence check, written in PROGRESS.md:
  - **Voice:** Kokoro or Indic Parler (both Apache 2.0), or the user's own recording or key.
    Never edge-tts or Edge/Azure "Neural" voices: edge-tts drives the Edge browser's
    read-aloud service without a commercial licence.
  - **Sound:** every file comes from the kit's `sfx/StableAudio`, `sfx/Kenney_CC0` or
    `music/Gemini`, or from a source the user owns.
  - **Pictures:** the user's own Flow generations.
  - **Tools:** faster-whisper (MIT) only times the words; nothing from it is in the video.


---

## Part 6: Next-Gen Intelligence Architecture (Rules 11 – 19)

### Rule 11: Text Label Deduplication & On-Screen Hygiene
- **Zero Duplicate Text:** Scene text banners and overlay sticker tags must NEVER display the same text simultaneously on the same frame.
- If a scene has an overlay prop with a tag (e.g. `BONE NEEDLE`), the scene's title banner column must be left empty.
- Automated deduplication in `render_pro.py`: the renderer automatically scans active overlays in the scene; if `scene_text` matches or is contained in an active overlay tag, the scene banner is automatically suppressed.
- Scene text column is strictly reserved for:
  1. Full-screen title/question cards (`card | NOT ONE. | big`)
  2. Major chapter milestone transitions (`REWIND | 170,000 YEARS | auto`)

### Rule 12: Pure Transparent Cutouts Only (Alpha Keying)
- All sticker props in `elements/cut/*.png` must be genuine transparent cutouts (`alpha.min() == 0` with >15% transparent pixels).
- **Prohibited:** Never use opaque circular cards, fake cream badges, or cropped rectangular copies of the scene image.
- **Never duplicate the scene subject:** If a scene already displays a dedicated close-up of a subject (e.g. an eyed needle or a microbe), do not overlay an additional sticker of that exact same subject onto the scene. Full-bleed 1080p close-ups already carry the visual weight.

### Rule 13: Strict Single-Word Kinetic Subtitles (Alex Hormozi Style)
- **Single Spoken Word:** Displays strictly the single word currently being spoken by the voiceover at millisecond precision ($t \in [w_{\text{start}}, w_{\text{end}} + 0.08]$). Zero preceding or trailing words are visible.
- **Kinetic Punch:** First 80ms of word onset applies an elastic micro-spring punch ($1.16\times \to 1.0\times$).
- **Color & Hierarchy:** Active word rendered in bold golden-amber (`#FFD21E` / `#FFC107`) with heavy 6px black stroke (`#000000`), drop-shadow, and a compact translucent pill backing (`rgba(15, 12, 10, 0.85)`).
- **Silence Blanking:** During natural breath pauses or silence between clauses, the subtitle completely blanks out. The screen remains clean and uncluttered.
- **Screen Positioning:**
  - 16:9 Master: Centered horizontally at $y = 940$ (safe lower third).
  - 9:16 Shorts: Centered horizontally at $y = 1350$ (sweet spot above mobile controls).

### Rule 14: Standalone 30–60s Viral Shorts Architecture
- **Dedicated Viral Funnel:** Rather than awkwardly re-rendering a 2-minute documentary into 9:16, a Short is a standalone, fast-paced teaser (45–55s) designed to maximize loop retention on YouTube Shorts, Instagram Reels, and TikTok.
- **Native 9:16 Art:** Uses native vertical 1080×1920 illustrations generated via Flow Connector (`--aspect-ratio 9:16`) with characters and focal action composed vertically.
- **Cliffhanger Hook & CTA:** Ends on a high-stakes dramatic mystery (e.g. *"Hypothermia could kill in hours... How did an ancient needle save humanity?"*) followed by a 2.5s teaser card with an arrow pointing viewers to the full documentary.
- **Safe Zone Enforcement:** Overlays and text must remain between $y = 0.15$ and $y = 0.75$, keeping the top 15% and bottom 25% clear of mobile UI icons (like, comment, share, sound disc).

### Rule 15: Self-Healing Flow Generation Engine
- **Automated Modal & Stall Recovery:** Detects policy warnings or stuck generation loops; issues `flow-auto cancel` and `flow-auto reload` to restore clean extension state.
- **Dynamic Prompt Sanitizer:** Automatically substitutes sensitive keywords (e.g., "louse", "parasite") with pre-tested policy-safe descriptive synonyms ("tiny microscopic science bug creature specimen").
- **Asset Verification & Retry:**
  - Verifies file size > 80 KB and valid image headers.
  - Automatically chroma-keys stickers via `key.key()`, verifies `alpha.min() == 0`, and retries up to 3 times if keying fails.
  - Zero-skip guarantee: never falls back to blank cards or placeholder crops.

### Rule 16: Intelligent VFX, Camera Drift & SFX Mapping Table
Visual events, camera physics, and sound effects are automatically mapped from the script:

| Script Trigger Type | Visual VFX / Camera Behavior | Screen Element | Sound SFX Assignment |
| :--- | :--- | :--- | :--- |
| **Tangible Noun** (*shirt, pants, needle, fire*) | Spring physics pop-in ($0 \to 1.08 \to 1.0$) | Transparent cutout sticker | Crisp tactile pop (`pop_01` .. `pop_05`) |
| **Statistical Figure / Date** (*170,000 years, 51%*) | Smooth cubic roll-up / animated growing bar | `count` or `bars:` overlay | Rapid data counter ticker / chime |
| **Dramatic Negation** (*Not one, Death trap*) | Subtle camera punch + vignette pulse | High-contrast bold card | Heavy wood/paper slam (`slam_wood`) |
| **Chapter Shift / Time Travel** (*Rewind*) | Ken Burns camera drift (push/pull/pan) | Full-bleed scene transition | Tape rewind / deep whoosh |
| **Microscopic / Scientific Discovery** | Subtle radial zoom into artifact | Transparent science cutout | Clean UI click / subtle tonal bell |
| **Prehistoric Cold / Ice Age** | Slow icy pull-back with mist wisp | Full-bleed Ice Age vista | Low howling wind ambient |
| **Fire / Warmth Ignition** | Subtle warm pulse / flicker | Flame cutout sticker | Stove click + flame whoosh |

### Rule 17: Collision-Free Multi-Sticker Placement & Safe Screen Zones
- **Dead-Center Protection & Unlimited Simultaneous Multi-Stickers:** Overlays avoid the focal center zone ($0.35 \le x \le 0.65, 0.35 \le y \le 0.65$) whenever characters occupy center stage. Simultaneous multi-sticker storytelling (2, 3, or 4+ props) is fully supported via the Multi-Slot Collision-Free Spatial Solver (`calculate_intelligent_sticker_anchor`).
- **Guaranteed Inter-Sticker Clearance & Spawn-Time Scaling:** Every simultaneous sticker is locked once in `overlay_anchor_cache` at spawn time with **`>= 32px` inter-sticker padding** (zero overlap/teleporting/jitter) and graceful spawn-time scaling (`1.0x` for 1–2 props, `0.83x` at 3 props, `0.78x` at 4+ props).
- **3-Tier Permanent Sticker Reuse (`skills/stickman-stickers/`):** Resolve Tier 0 Local -> Tier 1 `assets/flow_vault/` -> Tier 2 `assets/cc0_library/` -> Tier 3 Live Flow (auto-harvested back to `flow_vault/`).
- **Subtitle Zone Clearance:** Bottom safe zone ($y > 1120$ Shorts, $y > 880$ Long) is strictly reserved for kinetic single-word subtitles; stickers remain above safe buffers ($\ge 140\text{px}$ Shorts, $\ge 80\text{px}$ Long).

### Rule 18: Strict Visual Style Lock & Universal Negative Prompt Engine
- Every generation call must append the Universal Negative Prompt:
  `NEGATIVE_PROMPT = " Negative: photorealistic, hyperrealistic 3D render, glossy CGI, photograph, real human face, photorealistic skin texture, stock photo, watermark, logo, text, subtitles, distorted anatomy, modern artifacts in prehistoric scenes, anime, manga, inconsistent art style, cluttered background, blurry, multiple duplicate heads"`
- **Artistic Consistency:** All scenes and stickers in a project share the exact same style definition from `STYLE.txt` (line weight, color palette, paper grain, stickman anatomy) ensuring visual harmony across the entire documentary.

### Rule 19: Intelligent Voice Cadence & Natural English Prosody Rules (1.0x Standard Pace)
- **Natural Punctuation Breathing Pauses (English Cadence):**
  - Comma (`,`): **0.18s** (natural micro-breath, not a dead halt)
  - Semicolon (`;`) & Colon (`:`): **0.25s** (clause transition)
  - Ellipsis (`...`): **0.45s** (dramatic anticipation)
  - Full Stop (`.`): **0.28s** (sentence conclusion)
  - Question Mark (`?`): **0.32s** (contemplative silence)
  - Exclamation Mark (`!`): **0.30s** (punchline impact)
- **Speech Speed Standards (Zero Dragging, Normal 1.0x Flow):**
  - **Long Documentary (16:9):** Normal **1.0x** speed (`kokoro_vo.py --speed 1.0`, authoritative documentary cadence, $2.2 - 2.6$ words/s).
  - **Viral Shorts / Reels (9:16):** Energetic **1.05x** speed (`kokoro_vo.py --speed 1.05`, punchy viral delivery, $2.6 - 3.2$ words/s).
  - **Strictly Prohibited:** Never apply artificially slow $0.82\times - 0.90\times$ sluggish speeds or heavy gap paddings that drag down pacing and disengage viewers. All takes use clean 1.0x neural prosody with natural pauses.


### Rule 20: Absolute Visual Style Lock & Zero Style Mixing (Cartoon & Stickman Purity)
- **Zero Style Drift Across the Entire Video:**
  - If the project style is **2D Cartoon Stickman Explainer**, **100% of all visual assets** (scenes, props, sticker cutouts, character poses, background details, charts, and vertical shorts) MUST be executed in that exact same 2D cartoon stickman style.
  - **Strictly Prohibited:** Never allow a single frame, background, or prop to drift into photorealism, 3D CGI rendering, glossy digital gradients, or realistic human depiction. A 2D explainer that suddenly inserts a photorealistic 3D render or a realistic stock photo breaks immersion and destroys visual cohesion.
- **Strict Stickman Character Anatomy:**
  - Every human character across the entire documentary must strictly possess stickman anatomy: clean round white/paper head, expressive dot eyes, simple line mouth/eyebrows, minimalist stick or tubular ink limbs, and simplified stylized clothing.
  - **No Realistic Faces:** Absolutely no detailed realistic facial anatomy, no photorealistic skin textures, no 3D-shaded faces, and no hyper-detailed anatomical musculature.
- **Prop & Sticker Stylistic Alignment:**
  - Every prop cutout in `elements/cut/*.png` (e.g., shirts, pants, tools, sewing needles, fire, microbes, animals) must be illustrated in the exact same 2D hand-drawn cartoon aesthetic:
    - Thick, clean dark ink outlines (matching the line weight of the scene backgrounds).
    - Flat warm colors with gentle painterly texture (matching the project palette from `STYLE.txt`).
    - Hand-drawn illustrative charm rather than sharp corporate vector icons or digital 3D models.
- **Character Reference Locking (Image-to-Image):**
  - Any shot containing a character must attach the character's reference image (`--image img/ref_<name>.jpg`). Never generate characters freehand without the reference, as Flow will drift away from the established stickman design.
- **Universal Style & Negative Prompt Enforcement:**
  - Every single Flow prompt generated by `pictures.py` or `flow_smart_generator.py` automatically pulls the core style description from `STYLE.txt` and appends the comprehensive `NEGATIVE_PROMPT`:
    `" Negative: photorealistic, hyperrealistic 3D render, glossy CGI, photograph, real human face, photorealistic skin texture, stock photo, watermark, logo, text, subtitles, distorted anatomy, modern artifacts in prehistoric scenes, anime, manga, inconsistent art style, cluttered background, blurry, multiple duplicate heads, extra limbs, 3D model, realistic eyes, detailed facial features."`

### Rule 21: Full-Frame Composition Preservation & Zero Unwanted Cropping
- **Zero Cropping of Native Format Artwork:**
  - Google Flow generates native high-resolution compositions according to the requested aspect ratio:
    - **Shorts (9:16):** Flow generates $1536 \times 2752$. When composited into the 9:16 vertical canvas ($1080 \times 1920$), the engine scales the complete image directly via high-quality Lanczos interpolation (`raw.resize((W, H), Image.LANCZOS)`).
    - **Master (16:9):** Flow generates $2752 \times 1536$. When composited into the 16:9 widescreen canvas ($1920 \times 1080$), the engine scales the complete image directly.
  - **Strictly Prohibited:** Never crop, slice, or zoom into native artwork by default. Cropping destroys character staging, cuts off heads/limbs near frame boundaries, and degrades visual framing carefully planned in the prompt.
- **Ken Burns Opt-In Constraint:**
  - Zoom-in / drift camera motion (`--kenburns`) is strictly opt-in and disabled by default (`default=False`).
- **Cross-Orientation Presentation (Without Distortion):**
  - If a 16:9 landscape image must appear in a 9:16 vertical short, display the complete uncropped image within a framed stage card backed by a subtle blurred extension. Never force-crop a 16:9 landscape image to fill a 9:16 screen.
  - If a 9:16 vertical image appears in a 16:9 widescreen master, pillarbox the complete uncropped image centered with blurred edge fills. Zero artwork content is ever discarded.

### Rule 22: Dual Independent Pipelines for Shorts (9:16) vs. Long Video (16:9)
- **Zero Cross-Contamination of Formats:**
  - When the user selects **Format: Both**, the engine must NEVER simply stretch, squash, or letterbox the long documentary into vertical video. Shorts and Long videos serve completely different algorithmic and viewer psychology functions:
    1. **Shorts (YouTube Shorts / Instagram Reels / TikTok):** Discovery, viral reach, high scroll-stopping velocity.
    2. **Long-Form (YouTube Main Video / Desktop / TV):** In-depth retention, educational satisfaction, watch time, and monetization.
- **Dedicated Independent Flow Generations for Scenes (Zero Cross-Asset Sharing):**
  - **Shorts (9:16):** Scene backgrounds in `short/shots/` MUST be generated separately from Flow in native vertical aspect (`--aspect 9:16`, $1536 \times 2752$) with vertical composition prompts.
  - **Long-Form (16:9):** Scene backgrounds in `long/shots/` MUST be generated separately from Flow in native widescreen aspect (`--aspect 16:9`, $2752 \times 1536$) with wide cinematic landscape prompts.
  - **Strictly Prohibited:** Neither pipeline ever copies, reuses, or pillarboxes scene backgrounds from the other. Pillarboxing vertical images inside the 16:9 long documentary is an immediate RL failure.
- **Shorts Specifications (Strict 40–60 Seconds):**
  - **Viral Hook (0–3s):** Must open with a high-stakes psychological question, unbelievable historical fact, or counter-intuitive dilemma.
  - **Pacing & Cadence:** Fast-cutting visual beats every 1.8–2.8s with pop-in transparent stickers and tactile SFX. Speech pace is energetic and punchy ($2.6 - 3.2$ words/s).
  - **Mandatory Funnel CTA Handoff (Final 5–8s):** The short MUST end with an explicit call-to-action directing the audience to the long-form video on the channel:
    - *English:* "Want to see the screaming water clocks and human alarm clocks? Watch the full 5-minute documentary on our channel!"
    - *Urdu / Roman Urdu:* "Puri hairat-angez kahani dekhne ke liye channel par full 5-minute video zaroor check karein!"
- **Long-Form Specifications (User Duration e.g. 5–10 Minutes):**
  - **Deep Narrative Architecture:** 6-Act documentary structure with curiosity loops, deep context, historical anecdotes, and rich soundscapes.
  - **Native 16:9 Flow Prompts:** Prompts authored for cinematic landscape framing (`--aspect 16:9`, $2752 \times 1536$) with wide staging.
  - **Pacing & Cadence:** Authoritative, calm documentary delivery ($2.2 - 2.6$ words/s), -24 dB ambient music bed, and subtle Foley effects.
- **Shared Identity Continuity:**
  - Both pipelines share the exact same character sheet (`img/sheet.jpg`) and reference (`img/ref_<name>.jpg`), ensuring 100% visual identity consistency between the Short and the Long video.
- **Decoupled Folder Architecture:**
  - `short/`: Holds `SCRIPT.md`, `LINES.tsv`, `VO.wav`, `WORDS.tsv`, `SHOTS.tsv` (9:16), `ELEMENTS.tsv`, `SCENES_HYBRID.tsv`, `mix_pro.wav`, and outputs `<slug>_short_9x16.mp4`.
  - `long/`: Holds `SCRIPT.md`, `LINES.tsv`, `VO.wav`, `WORDS.tsv`, `SHOTS.tsv` (16:9), `ELEMENTS.tsv`, `SCENES_HYBRID.tsv`, `mix_pro.wav`, and outputs `<slug>_long_16x9.mp4`.

### Rule 23: Surgical Edit Mode & Asset Preservation
- **Preservation Invariant:** When a user requests an edit ("edit karo", "edit scene 3", "change voice", "fix pacing"):
  - **NEVER** delete the project folder, wipe out assets, or restart from 0.
  - **NEVER** prompt the 5 intake questions.
- **Interactive Clarification Protocol:**
  - Inspect `PROGRESS.md` and current assets.
  - Present the user with clear, numbered modification categories:
    1. **Script / Storyline:** Re-write specific lines or reformulate the hook.
    2. **Voice & Narration:** Re-voice specific takes with new seeds, alternative speaker timbres, or adjusted pacing.
    3. **Visual Imagery & Stickers:** Re-prompt specific shots in Flow, re-key stickers, or adjust positioning.
    4. **Audio & Sound Design:** Re-balance SFX levels, change the music bed, or tweak ducking thresholds.
    5. **Subtitles & Layout:** Change kinetic caption size, positioning, colors, or safe zones.
  - Apply surgical modifications only to the targeted files and re-render only the affected sub-pipeline.

### Rule 24: Spatial Hierarchy & Clutter-Free Layout Standard (Text & Stickers)
- **Instagram Reels & YouTube Shorts Safe Zone Boundaries (9:16 Canvas 1080x1920):**
  - **Top System Area ($y \in [0, 180\text{px}]$):** Exclusion zone (phone status bar, camera pill/punch-hole, audio search). The ambient progress bar sits at $y \in [0, 8\text{px}]$.
  - **Opening Title Header:** Displayed at $y \in [190, 250\text{px}]$ (mobile safe area) **ONLY during the first 2.5s** ($t \le 2.5$), then fades out completely.
  - **Scene Concept Pill (`draw_label`):** Centered at $y = 230\text{px}$. During the first 2.5s, it is automatically suppressed to prevent stacked double-header pollution.
  - **Right Engagement Rail ($x \in [860, 1080\text{px}]$):** Exclusion zone (Like, Comment, Share, Remix, Audio disc). All stickers and labels MUST maintain $x + nw/2 \le 860\text{px}$ (220px right margin).
  - **Bottom Social & Caption Band ($y \in [1260, 1920\text{px}]$):** Exclusion zone (Creator avatar, handle `@name`, 2-line caption, seek bar, nav bar). Zero text or stickers permitted.
  - **Kinetic Subtitles Zone:** Single-word Hormozi style subtitles centered horizontally at $x = 540$, vertically at $y = 1180\text{px}$.
  - **Dynamic Sticker Docking Safe Harbor:**
    - Size: $fh \approx 0.22H$ (~420px max).
    - Docking: Left quadrant ($fx \approx 0.24, fy \approx 0.38$) or Right quadrant ($fx \approx 0.68, fy \approx 0.38$) opposite the stickman character.
    - Subtitle Clearance: Sticker bottom + label MUST stay strictly above $y = 1040\text{px}$ ($fy \le 0.44$), guaranteeing a $\ge 140\text{px}$ clear buffer above subtitles. If the label would encroach below 1040px, it automatically docks ABOVE the sticker.
- **YouTube Landscape Safe Zone Boundaries (16:9 Canvas 1920x1080):**
  - **Documentary Chapter/Topic Tag:** Default position is a sleek **Top-Left Slug** ($x \approx 140 + tw/2, y \approx 100 + th/2$) backed with translucent paper texture, following Vox and Kurzgesagt broadcast documentary hierarchy. This completely separates scene context from bottom speech subtitles.
  - **Kinetic Subtitles:** Centered horizontally at $x = 960$, positioned vertically at $y = 920-940\text{px}$, safely above player controls ($y > 990\text{px}$).
  - **Stickers & Props:** Docked in upper quadrants ($fx \approx 0.22 \text{ or } 0.78, fy \approx 0.38$), bounded by $y \le 820\text{px}$ to never crowd subtitles.
- **Single Focal Hierarchy:**
  - At any moment, the viewer's eye focuses on ONE primary concept (either the scene action OR the popping sticker), anchored by the kinetic Hormozi subtitle in the eye-level safe zone. Multiple stacked text pills or overlapping graphics are an immediate RL layout violation.

### Rule 25: Screen Heading Suppression & Pristine Triad Hierarchy
- **The Core Problem:** Floating heading pill banners on regular illustration scenes create redundant visual text and clutter when animated stickers and kinetic captions are active.
- **Suppression Invariant:** Floating heading pill banners are strictly disabled by default (`--scene-labels` default: `False`, `--header` default: `False`).
- **Title Card Exception:** Text headings are permitted ONLY on dedicated full-screen chapter cards (`img == "card"`), where the screen is intentionally cleared of character action to announce a major structural transition.
- **Pristine Triad Hierarchy:** Normal scenes must feature only three visual layers: (1) Full-bleed 2D stickman background illustration, (2) Clean transparent animated sticker props popping on cue, and (3) Alex Hormozi golden-amber single-word kinetic subtitles docked safely at the bottom.

### Rule 26: High-Density Visual Pacing & Dynamic Image Frequency ("Ziada Image Use Kiya Karo")
- **Shorts (9:16 Viral Retention Standard):**
  - Target cut duration: **$\le 3.0\text{s}$ per cut** (minimum 16–20 distinct background scenes for a 45–60s video, earning an A+ in RL-QC).
  - Every narration line must be split into at least 2 visual beats: the opening beat (`@<line_id>`) and a mid-sentence action/concept cut (`@<line_id>:<keyword>`).
  - Hard limit: No single background image may linger on screen for $> 3.8\text{s}$. Fast visual variety sustains high audience dopamine and prevents swipe-away dropoff.
- **Long Documentary (16:9 Narrative Standard):**
  - Target cut duration: **$\le 6.0\text{s}$ per cut** (minimum 50–65 distinct widescreen scenes for a 5-minute video, earning an A in RL-QC).
  - Avoid static holds: each line, historical fact, diagrammatic explanation, and tone change must have its own dedicated shot (wide establishing landscapes, medium character interactions, blueprint technical drawings, and macro scientific cutaways).
  - Hard limit: No single background image may linger on screen for $> 7.5\text{s}$.
- **RL-QC Pacing Verification:** `evaluate_rl.py` automatically checks average cut duration and issues deductions if video pacing falls into sluggish grades (B or C).

### Rule 27: Multi-Layered Sound Design & SFX Density Standard ("Ziada Se Ziada Sounds Use Karo")
- **Zero Silent Visual Events:** Every visual cut, sticker entrance, and keyword punch must be paired with tactile sound. Videos with fewer than 15 sound cues are strictly flagged as under-designed.
- **The Storytelling Golden Ratio (Anti-Reading Audio Mix):**
  - **The "Reading" vs "Storytelling" Trap:** When background music is ducked too low (-36 dB to -42 dB), the human brain processes the voice as an analytical lecture or dry textbook reading. To evoke immersive documentary storytelling (like Vox, Kurzgesagt, or Lemmino), the music must remain clearly audible, rich, and rhythmic throughout the entire narrative.
  - **Vocal Pocket Equalization:** A psychoacoustic notch EQ (-3.2 dB at 1.8 kHz, Q=1.2; -2.2 dB at 3.2 kHz, Q=1.4) is carved into the music bed in `mix.py`. Because the narrator's vocal formants sit in their own dedicated frequency pocket, the music can sit **4 to 6 dB louder** without masking or clashing with the words!
  - **Calibrated Music Bed Gain:** Baseline gain is **-17.0 dB** for Long documentaries and **-16.0 dB** for fast Shorts (never -24 dB to -26 dB!).
  - **Gentle Musical Ducking (NOT Voice Crushing):** Sidechain ducking is calibrated to a gentle **2.8:1 ratio** with a high threshold (0.08) and slow **550ms release**. During speech, the music dips by only -4.5 dB (sitting at -21.5 dB, clearly heard). During pauses and between sentences, the music swells warmly (+4.5 dB), giving the film cinematic breathing room.
  - **Broadcast Vocal Warmth Chain:** Kokoro and Indic Parler voices pass through a broadcast warmth and presence chain (`highpass=f=75`, `220 Hz (+1.8 dB)` chest warmth, `3400 Hz (+2.2 dB)` clarity presence, and `8500 Hz (+1.2 dB)` broadcast air), removing the sterile text-to-speech reading feel.
- **Four Mandatory Audio Layers (`sfx_smart_designer.py`):**
  - **Layer 1 (Visual Cut Transitions):** Every scene cut (`@<line_id>`) triggers a subtle whoosh, paper swipe, zoom snap, or swish from Wyzowl CC0 / Kenney CC0 (`-20 dB` to `-23 dB`).
  - **Layer 2 (Sticker Pop & Semantic SFX):** Every transparent sticker reveal (`+@...`) plays a semantically matched sound (bubble pop, notification ping, wood tap, water drop, coin drop, ice crack) (`-15 dB` to `-17 dB`).
  - **Layer 3 (Keyword Spoken Impact Hits):** High-curiosity spoken words in `WORDS.tsv` ("freezing", "danger", "starvation", "conquered", "impossible", "secret", "space") trigger synchronized micro-hits or sub-thuds (`-17 dB` to `-19 dB`).
  - **Layer 4 (Continuous Foley Bed & Music Score):** Continuous environmental loop (`-23 dB`) plus ambient documentary music score (`-17 dB`) with vocal pocket EQ.
- **Broadcast Loudness Verification:** The final mix must verify at **-14.0 LUFS** ($\pm 1.0$ LUFS) and true peak $\le -1.0\text{ dBFS}$ via `evaluate_rl.py`.

### Rule 28: Dynamic Visual FX (VFX) & Motion Transitions Standard
- **Scene Transition VFX:** Hard cuts are replaced or enhanced by contextual visual effects specified in `SCENES_HYBRID.tsv`:
  - `fade` / `crossfade`: Smooth 0.20s dissolve between consecutive scenes.
  - `flash`: 0.12s warm exposure bloom for big historical leaps, scientific discoveries, and opening hook reveals.
  - `zoom_punch`: Subtle 0.25s kinetic snap-in (1.04x $\rightarrow$ 1.0x).
- **Sticker Entrance & Living Motion VFX:**
  - `pop`: Harmonic damped spring bounce (0 $\rightarrow$ 1.08 $\rightarrow$ 1.00).
  - `drop` / `slam`: Vertical drop from top with bounce impact.
  - `slide_left` / `slide_right`: Horizontal inertia slide from off-frame.
  - `hover` / `breathing`: Organic sinusoidal vertical hovering ($\pm 5\text{px}$) after settling, keeping stickers alive throughout the scene.

### Rule 29: Dynamic Sticker Lifetime, Voice-Word Synchronization, and Clean Exit
- **Spoken Word Synchronization (`resolve_word_time`):** Stickers must pop up on screen at the EXACT timestamp of the spoken keyword from `WORDS.tsv`. The engine intelligently matches keywords, multi-word stems (e.g. `icecream` $\rightarrow$ `ice`), synonyms (e.g. `fridge` $\rightarrow$ `refrigerators`), and line contexts. Stickers NEVER default to 0.0s.
- **Strict Time-to-Live (TTL):** Stickers must NOT linger indefinitely on screen.
  - **Shorts:** Standard duration is **1.8s** (or custom `dur:X.X`).
  - **Long Documentary:** Standard duration is **2.2s** (or custom `dur:X.X`).
- **Smooth Ease-In & Exit Dissolve:**
  - Entrance: Harmonic damped spring bounce over 0.35s with 0.18s opacity fade-in.
  - Life: Sinusoidal floating hover ($\pm 5\text{px}$).
  - Exit: In the final 0.28s, the sticker smoothly shrinks (`q = q * exit_p**1.6`), dissolves opacity (`alpha = min(alpha, exit_p)`), and floats upward (`cy -= (1.0 - exit_p) * 16`), cleanly evaporating before the next visual beat.
- **Exit Sound Effect:** A subtle soft zip-out or pop-out SFX (`Wyzowl_CC0/sounds/swishes-and-zips/zip-out-soft.wav` at `-26 dB`) accompanies the visual disappearance.

### Rule 30: Viral Psychology, Barnum Effect & Dynamic Subtitles
- **The Barnum Hook Standard:** Hook the viewer within the first 3 seconds using universal personal relatability:
  - *Template 1 (The Invisible Daily Habit):* "You probably do this 5 times every single day without realizing it. But 400 years ago, doing this would make you the most dangerous emperor alive."
  - *Template 2 (The Secret Vulnerability):* "If you're like 99% of people, you think you understand how this works. But right now, you are 48 hours away from a total blackout."
  - *Template 3 (The Ancient Cheat Code):* "Notice how you always feel this way when you wake up? Ancient desert kings figured out the cheat code 2,400 years before modern science."
- **Zeigarnik Open Loops:** Plant an unanswered paradox or counter-intuitive dilemma in the hook that is only resolved in Act 5/6.
- **Dynamic Semantic Kinetic Subtitles:** Alex Hormozi single-word subtitles accent words based on psychological meaning:
  - **Green (`#48EB78`):** Money, wealth, profit, survival, victory, fresh food, growth.
  - **Red (`#FF4B4B`):** Danger, rot, bacteria, peril, war, starvation, blackout, death.
  - **Cyan (`#4BE1FF`):** Ice, cold, freezing, snow, frost, physics, vacuum, space, night, stars.
  - **Golden Amber (`#FFD71E`):** Core historical and conceptual words.

### Rule 31: 100% YouTube Monetization & Copyright Purity Standard
- **YouTube Partner Program (YPP) Clearance:** Every asset across audio, visuals, code, fonts, and scripts is certified 100% royalty-free, public domain, or open-source permissive for full ad revenue monetization with zero Content ID claim risks:
  - **Visuals:** 100% original generative 2D stickman art from Google Flow prompts.
  - **Audio SFX:** 100% CC0 Public Domain (`Wyzowl_CC0` 320 sounds, `Kenney_CC0` 218 sounds, `StableAudio` Foley).
  - **Music:** 100% CC0 Public Domain (`CC0_PublicDomain` 23 FreePD & Duru tracks) and original AI Lyria stems.
  - **Voices:** Apache 2.0 open-weight neural TTS (Kokoro-82M / Indic Parler-TTS). No celebrity voice clones.
  - **Typography:** SIL Open Font License (Patrick Hand, Kalam, Montserrat) / Apache 2.0 (Luckiest Guy).
  - **Broadcast Audio Standards:** Integrated loudness -14.0 LUFS ($\pm 1.0$ LUFS) and true peak $\le -1.0\text{ dBFS}$.

### Rule 32: Dynamic Camera Shake, Tension Rumble & Broadcast VFX Suite
- **Dynamic Camera Shake & Rumble:**
  - When high-impact words ("DANGER", "BLACKOUT", "WAR", "STARVATION", "EXPLOSION", "FREEZING", "COLLAPSE") are spoken, or when `extra` contains `shake`, `render_pro.py` applies a fast decaying impulse displacement ($\pm 12\text{px}$).
  - When `extra` contains `rumble`, a continuous high-frequency vibration ($\pm 2.8\text{px}$) is applied for ominous tension.
- **Historical Black-and-White Flashbacks (`bw`, `grayscale`, `monochrome`):**
  - Desaturates the scene by 92% and lifts ink contrast, visually transporting the viewer back in time.
- **Crimson Hazard Vignette (`blood`, `danger`, `hazard`):**
  - Renders a pulsing red perimeter gradient ($1.2\text{ Hz}$ heartbeat pulse) signaling imminent peril.
- **Cyan Frost Vignette (`ice`, `frost`, `cold`):**
  - Renders an electric cyan/blue crystalline border vignette for sub-zero climates and extreme cold.
- **Kinetic Punch Zoom (`zoom_punch`):**
  - Snaps the camera from $1.06\times$ down to $1.00\times$ in the first 0.22s of a cut for high-energy visual impact.

### Rule 33: High-Converting YouTube Outro & Closing Slate Standard
- **Long-Form 16:9 End Screen Slate:**
  - Triggered automatically on `img == "outro"` or during the final 12s of a 16:9 documentary.
  - Implements YouTube's strict safe-zone guidelines:
    - Left Card: "Watch Next" ($610 \times 344\text{px}$ at $x=120, y=250$).
    - Right Card: "Best for You" ($610 \times 344\text{px}$ at $x=1190, y=250$).
    - Center Channel Bubble: Subscribe Avatar ($r=88\text{px}$ at $x=960, y=422$) with animated waving stickman.
  - Clear spacing ($\ge 100\text{px}$) from all viewport borders ensures 100% compatibility with YouTube's interactive End Screen elements.
- **Shorts 9:16 Seamless Loop & Subscribe Callout:**
  - Loops narration seamlessly into the opening 0-3s hook.
  - Renders an animated floating golden-amber pill `[ 🔔 SUBSCRIBE FOR MORE ]` in the lower safe area ($y=1550, x=540$) during the final 3.5s without obscuring platform UI.

### Rule 34: Trending Topic Research & SEO Ranking Suite (`trending_researcher.py`)
- **High-RPM Niches ($12 - $28 RPM):**
  - Ancient High-Tech & Lost Civilizations ($14 - $19.50 RPM)
  - Catastrophic "What If" & Survival Crises ($16.50 - $22.00 RPM)
  - Hidden Human Biology & Brain Secrets ($15 - $24.00 RPM)
  - Dark Money, Empire Economics & Historical Scams ($18 - $28.00 RPM)
- **Automated Metadata Deliverables:**
  - 3 High-CTR Title Variations (curiosity gap, paradox, catastrophic shock).
  - High-Retention Barnum Opening Hooks (first 3 seconds).
  - SEO Tag Clusters (Tier 1 broad, Tier 2 niche specific, Tier 3 long-tail search queries).
  - Viral Thumbnail Badges (e.g. `[FORBIDDEN]`, `[DAY 14]`, `[CLASSIFIED]`).

### Rule 35: High-CTR Viral Thumbnail Generator (`thumbnail_generator.py`)
- **The 3-Element High-CTR Rule:**
  1. **Expressive Stickman:** Dominant white figure with oversized shock/wonder eyes and dynamic hand gestures, docked on the left/right.
  2. **Glowing Hero Prop:** High-contrast mystery artifact with a 24px soft radial gaussian glow (e.g. glowing ice block, ticking clock, radioactive vial).
  3. **Curiosity Text:** Maximum 2–4 high-impact words (e.g. "THE FORBIDDEN COLD", "NEVER WAKE UP"), tilted at -3.5° for psychological velocity, rendered in ultra-bold font (Luckiest Guy / Montserrat-Black) with 14px dark outline and 18px drop shadow.
- **Dual Format Output:**
  - 16:9 Landscape (`1280x720`) for YouTube Desktop / TV browsing.
  - 9:16 Vertical (`1080x1920`) for YouTube Shorts feed, Instagram Reels, and TikTok cover frames.

### Rule 36: Continuous Reinforcement Learning & Self-Correcting Experience Replay Hub (`rl_memory.py`)
- **Automated Audit Logging:** Every run of `evaluate_rl.py` records measured metrics (cut duration, hold times, LUFS loudness, SFX count, subtitle-cutout clearance) to `rl_feedback_memory.json`.
- **Adaptive Policy Vector:** If pacing slips into grade B or C, `rl_memory.py` automatically tightens cut targets (Shorts $\le 2.6\text{s}$, Long $\le 4.8\text{s}$) for the next script generation.
- **Persistent Feedback Replay:** Logs user corrections ("ziada image use kro", "heading na aaye", "vfx use kro") so future video pipelines inherit them automatically.

### Rule 37: Daily Viral Trends & Production Intelligence (`trend_updater.py`)
- **Four-Pillar Tracking:** Tracks viral sound design (sub-bass impacts, tape rewinds, bubble pops), dynamic broadcast VFX (shake, rumble, frost/crimson vignettes), high-CTR visual aesthetics (storybook ink, blueprint cutouts), and viral hook psychology (Barnum paradox, countdowns).
- **Automated Cache:** Keeps cached intelligence in `trending_insights.json` for instant prompt crafting.

### Rule 38: Intelligent Google Flow Prompt Auditor & Negative Suite (`flow_prompt_auditor.py`)
- **Multi-Layered Negative Prompts:**
  - `NEGATIVE_STICKMAN`: Blocks photorealism, realistic human skin, 3D CGI, uncanny valley, anime, and distorted limbs.
  - `NEGATIVE_CLEANLINESS`: Blocks watermarks, logos, text, letters, subtitles, and blur.
  - `NEGATIVE_ERA_ANCIENT`: Blocks modern cars, smartphones, power lines, and plastic bottles in historical scenes.
  - `NEGATIVE_CHROMA_STICKER`: Blocks complex backgrounds, floor contact shadows, and gradients for pure #FF00FF magenta sticker downloads.
- **Automated Policy Sanitizer:** Replaces sensitive filter trigger words ("corpse", "blood", "lice", "kill") with safe illustrative terms to prevent Flow queue halts.

### Rule 39: Flow-Powered Thumbnail Generator with Computer Vision Analysis (`flow_thumbnail_generator.py`)
- **Dedicated Flow Thumbnail Prompts:** Crafts high-drama, high-curiosity prompts for Google Flow.
- **4-Pillar Computer Vision Audit:** Evaluates base image; preserves elements that are already optimal; auto-composites missing expressive stickman, glowing hero prop (24px radial glow), adaptive dark gradient scrim, and bold -3.5° tilted curiosity text (14px outline).

### Rule 40: AI Narrative & Emotional Arc Director (`narrative_intelligence.py`)
- **6-Act YouTube Retention Tension Curve:**
  - Act 1: The Paradox Hook (0-15%, Arousal 8.5/10) - Provocative premise & counter-intuitive daily dilemma.
  - Act 2: The Historical Complication (15-35%, Arousal 5.5/10) - Ancient struggles and world-building.
  - Act 3: The Ingenious Breakthrough (35-60%, Arousal 7.5/10) - Engineering wonder, step-by-step logic.
  - Act 4: The Crisis / Catastrophic Peril (60-78%, Arousal 9.2/10) - Mortal danger, systemic failure.
  - Act 5: The Twist / Revelation (78-90%, Arousal 10.0/10) - The peak aha moment.
  - Act 6: Philosophical Payoff (90-100%, Arousal 6.0/10) - Modern integration & YouTube Outro Slate.
- **The Vox Drop-Out Silence:** Scans for the pivotal reveal line and marks the exact timestamp for a 0.8s–1.2s complete musical silence (`--dip`), forcing viewer attention to spike right before the reveal lands.
- **Sub-Bass Impact Direction:** Automatically injects a 60Hz resonant sub-thud on key statistical metrics and historical turning points.

### Rule 41: The 4–7 Second Pattern Interrupt Standard
- **The Attention Physics:** If an audio or visual element stays identical for $> 6.0\text{s}$, the brain marks it as predictable and retention plummets.
- **Micro-Interrupt Cadence:** Guarantees a pattern interrupt every 2.4s–4.0s (scene cut, sticker pop, camera shake, punch zoom, or kinetic subtitle).
- **Subtle Cinematic Push-In:** On any visual hold exceeding 3.0s, `render_pro.py` automatically applies a slow, continuous scale push-in ($1.00\times \rightarrow 1.045\times$ over 4.0s) so frames never remain completely static.

### Rule 42: Visual Metaphor Entropy Standard
- **Cognitive Flow over Scene Clutter:** Following Vox and Kurzgesagt documentary editing, the visual metaphor evolves every 2.5s–4.5s.
- **4-Stage Visual Pacing Alternation:**
  1. *Character + Context Prop Interaction* (Character active in the environment).
  2. *Infographic & Diagrammatic Map* (Spatial movement, dashed arrows, statistical callouts).
  3. *Cinematic Focus Vignette* (Macro close-up, dramatic lighting, low-pass depth).
  4. *Expressive Reaction / Exaggeration* (Squash and stretch, comic disbelief, eye pop).

### Rule 43: Kurzgesagt Auditory Highlighter Pen Architecture
- **SFX as Information Anchors:** In Kurzgesagt, sound effects are not random background noise; they act as auditory highlighters guiding the viewer's gaze.
- **Micro-Transient Highlighting:** Dates (e.g. 1912, 400 BC), numbers, percentages, and paradigm shifts trigger tactile micro-SFX (`pop-medium-bubble`, `digital-process`, `threeTone1`, `props-slide`) at calibrated -22 dB.
- **Acoustic Anti-Clashing Guard:** Implemented in `sfx_smart_designer.py` with a 2.8s separation window so the mix stays clean, distinct, and broadcast-ready.

### Rule 44: Curiosity Architecture & Open-Loop Retention Engine (`curiosity_engine.py`)
- **George Loewenstein's Information Gap Theory:** Creates psychological tension between what the audience knows and what they need to know.
- **The Zeigarnik Effect:** Humans cannot tolerate unfinished tasks. By deploying chain-link micro-loops every 45-75s ("That discovery solved one riddle, but it exposed an even stranger detail in the records..."), viewers remain locked in through the climax.
- **Automated Retention Audit:** `curiosity_engine.py` audits scripts for macro hooks, bridge gaps, and philosophical payoffs, scoring retention health (target $\ge 85/100$).

### Rule 45: High-CTR 3-Element Thumbnail & Mobile 140px Readability Standard (`viral_seo_intelligence.py`)
- **The Three-Element Rule:**
  1. *Primary Subject (45-55% frame)*: Expressive stickman face/silhouette.
  2. *Supporting Context Prop (25-30% frame)*: Glowing hero artifact with intense cyan/gold radial bloom.
  3. *Text Hook ($\le 3$ words)*: Angled at -3.5° with $\ge 14\text{px}$ dark stroke.
- **Mobile Readability Test:** Tested at 140px width (mobile sidebar/feed size) ensuring text is legible in $< 0.5\text{s}$ of visual scan.

### Rule 46: 100% Working 3-Second A-E-T Viral Hook Architecture (`viral_hook_engine.py`)
- **The A-E-T Sequence:**
  1. *A (Attention Spike, 0–1s)*: Frame-0 procedural 50Hz sub-bass boom + swept whoosh riser + speedline burst with zero dead air.
  2. *E (Emotional Anchor, 1–2s)*: Calibrated to 6 psychological archetypes (`barnum`, `counter_intuitive`, `paradox`, `transformation`, `forbidden`, `warning`).
  3. *T (Tease Outcome, 2–3s)*: High-stakes open loop securing $\ge 80\%$ Average Percentage Viewed.
- **Word-by-Word Kinetic Badges**: Glowing rounded pill badges (`#FFE600`, `#00F0FF`, `#FF0055`) with active-word scale punches and millisecond alignment via Faster-Whisper.
- **Hardware-Accelerated 9:16 & 16:9 Export**: Renders standalone MP4 clips in seconds using Intel VA-API (`h264_vaapi`).

### Rule 47: Psychoacoustic Sound Layering, J-Cuts & Tactile Synesthesia (`sfx_smart_designer.py`)
- **Audio Pre-Lapping (J-Cuts)**: Scene transitions lead by 120ms; sticker entrance foley leads by 90ms before visual graphic appearance. The ear prepares the eye.
- **Tactile Synesthesia (Foley for Abstract Concepts)**: Assigns real-world organic foley (wood taps, paper rustles, typewriter ticks) to 2D vector elements so data feels physically weighty.
- **The "Scare & Release" Micro-Silence Vacuum**: Cuts music bed and ambient noise to complete digital silence for 0.4s to 0.8s immediately before the twist reveal (*The Vox Drop-Out*).
- **Frequency Slotting**: Voice (120Hz–4.5kHz), Highlighters (2.5kHz–8kHz at -22 dB), Sub-Bass (40Hz–65Hz), Bed (-17 dB with -4 dB sidechain ducking).

### Rule 48: Autonomous Zero-Setup Self-Healing Standard (`auto_bootstrap.py`)
- **Clone-and-Run Guarantee**: Any user cloning this repository on Linux, macOS, or Windows can run any script immediately with zero manual dependency installation.
- **Autonomous Auto-Provisioning**: Detects missing packages (`kokoro`, `faster-whisper`, `scipy`, `soundfile`, `pillow`) and installs them automatically via pip.
- **Pre-Warms Models**: Verifies local Kokoro-82M and Faster-Whisper int8 models, ensuring zero first-run crashes.

### Rule 49: The Hypnotic Modernity $\to$ Evolutionary Void Inversion Standard
- **The Psychology of the Void Inversion (Ink Explainer 19.3M & Zenn 8.1M Benchmark)**:
  - Viewers are numb to generic documentary openings ("Thousands of years ago..."). 
  - To hook the subconscious, the first 0–6 seconds must establish a hyper-relatable modern comfort, then violently erase it:
    - *0–3s (Modern Sensory Anchor)*: "Tonight, when the sun goes down, you're going to flip a switch. A warm bulb will flood your room..." or "This morning, a machine yelled at you until you woke up."
    - *3–6s (The Void Inversion)*: "Now erase all of that. Step back 50,000 years. For 99.9% of human history, that switch did not exist."
    - *6–12s (The Visceral Peril)*: "When the sun went down, your world didn't just get dark—it became lethal."
- **Visual Staging**: Begin with modern everyday props (alarm clock, light switch, coffee cup), then apply a sound-lapping whoosh wipe (`jcut_whoosh`) that clears the screen, leaving the naked white-head stickman stranded in the ancient dark.

### Rule 50: Dual-Tone Canvas Harmony & Dynamic Contrast Palette
- **The Visual Contrast Physics (The Zenn & Ink Color Temperature Law)**:
  - Explainer videos with 100% white backgrounds feel cold, sterile, and amateur. Explainer videos with 100% sepia brown backgrounds feel muddy and cause visual drop-off after 90 seconds.
  - Top-tier channels maintain audience retention via dynamic color temperature shifts:
    - *Daytime / Knowledge / Modern Canvas*: Warm vintage parchment (`#F7E8C0` to `#ECD6B4` or `#EEEBE1`) with 6–8px clean charcoal outlines (`#1A1A1A`) and opaque white head fills.
    - *Night / Peril / Wilderness Canvas*: Midnight Indigo & Deep Space Navy (`#181A2A` to `#303D97`) with high-contrast radiant campfire amber (`#FFAE33` / `#FF7800`).
- **The Island of Safety Composition**: In night or peril sequences, the firelight forms a warm circular mask ($r \approx 450\text{px}$) around the stickman. Outside the glow, predator silhouettes and cold terrain fade into deep indigo vignette, locking the viewer's eyes onto the protagonist's survival space.

### Rule 51: The OverSimplified Comic Contrast Law (OverSimplified 52M Benchmark)
- **The Petty Human vs Grand History Tension**:
  - Never present historical conflicts, revolutions, or treaties as dry dates or academic summaries.
  - Ground grand geopolitical crises in ridiculous, relatable human pettiness: character vanity, petty arguments, weird habits, or absurd misunderstandings between stickman figures.
- **Visual Caricature & Exaggeration**:
  - Use recognizable period costumes (tricorne hats, powdered wigs, crowns) draped on simple stick bodies.
  - Characters react with extreme comic emotions: oversized white eyes with tiny black pupils for panic, streaming tears for despair, shouting open mouths, and comical slapstick impacts (`chop.ogg`, `impact-light-hard.wav`).

### Rule 52: The Deadpan Flowchart Classification Standard (Casually Explained 23M Benchmark)
- **The Clinical Irony Architecture**:
  - Treat emotionally agonizing or awkward human dilemmas (dating signals, social anxiety, fitness plateaus) with the cold, sterile demeanor of a corporate training manual or scientific flowchart.
  - Deploy multiple-choice decision trees on screen: *Scenario 1: She looks at you and smiles. Option A: She likes you. Option B: She is being polite. Option C: She is from Canada. Option D: Can't really be sure.*
- **Understated Delivery**:
  - Narrate in a steady, un-hyped, deadpan cadence.
  - Pair with ultra-minimal 3px clean black lines on stark white canvas, letting the contrast between the absurd text and the calm visuals generate the humor.

### Rule 53: The Mechanical Incentive & Keyflow Principle (CGP Grey 26M Benchmark)
- **The Cold Mechanics of Systems**:
  - In political, economic, or institutional explainers, strip away moral illusions. Explain history through the lens of game theory and selfish mechanical incentives.
  - "Dictators don't rule alone. There are Keys to Power. Keep your keys loyal, or they replace you."
- **Visual Node & Flowchart Kinetics**:
  - Visualize power as concrete objects (glowing golden keys, treasure chests, tax revenue pipes) flowing between stickman node networks.
  - Maintain a rapid, authoritative rhythmic speech cadence (175–195 WPM) with instant visual state updates synced to mechanical clicks.

### Rule 54: The Kinetic Marker & Vector Drawing Standard (MinutePhysics 10M Benchmark)
- **The Counter-Intuitive Everyday Axiom**:
  - Start with a physical truth everyone observes but nobody understands ("Why is the solar system flat? If space is 3D, why isn't it a sphere?").
  - Reveal that 99% of common intuition is flawed, and resolve the cosmic mystery in under 180 seconds using pure, intuitive 2D geometry.
- **Dynamic Physics Vectors**:
  - Animate real-time collision vectors, velocity arrows, and gravitational planes as if sketched with a fresh felt-tip marker on paper, accompanied by tactile marker squeaks and sliding paper foley.

### Rule 55: The Strategic Dead Air & Comedic Timing Law
- **The Vacuum Before the Punchline**:
  - Both dramatic revelations and comedic punchlines require auditory breathing room to register in the viewer's brain.
  - Immediately before any high-stakes punchline or ironic twist, apply a strict **0.4s to 0.8s total audio drop-out** (muting background music and room tone).
  - The character's frozen reaction lands in absolute silence; the kinetic reaction SFX or vocal punchline fires on the release.

### Rule 56: The 5-Pillar Visual Effects (VFX) Anatomy (`video_editor_studio.py vfx`)
- **Screen Shake on Impact**: On sub-bass drops, cannon fire, or dramatic punches, displace frame using a damped sine wave:
  `crop=w=in_w-40:h=in_h-40:x='20+12*sin(2*PI*t*16)*exp(-4.5*t)':y='20+12*cos(2*PI*t*16)*exp(-4.5*t)',scale=1920:1080`
- **White Flash Frame**: 2 frames (0.06s–0.10s) of pure white flash (`fade=t=in:st=0:d=0.10:c=white`) on sudden reveals, explosions, or reality wipes.
- **Radial Action Lines (Speed Lines)**: High-energy comic radial speedlines focused toward screen center, leaving a clear focal circle for the stickman protagonist.
- **Hero Prop Bloom**: 24px gaussian blur ambient glow around focal items (golden keys, glowing bulbs, fire, ancient needles) to signal value.
- **Micro-Emote Popups**: Expressive comic symbols (question marks, sweat drops, exclamation marks, steam puffs) popping over stickman heads for instant non-verbal storytelling.

### Rule 57: Dynamic Sticker Physics & Anti-Occlusion Staging (`render_pro.py`)
- **Damped Harmonic Spring Physics**: Stickers enter with an elastic overshoot ($1.15\times \to 1.00\times$) paired with a subtle -3.5° to +4° rotation tilt.
- **J-Cut Audio Pre-Lapping**: Every sticker entrance sound (bubble pop, wood click, paper slide) leads the visual graphic appearance by **90ms to 120ms**. The ear prepares the eye.
- **Strict Anti-Occlusion Guard**: Stickers are automatically staged in the outer quadrants (top-left, top-right, or lower-third flank). They must NEVER obscure the stickman's eyes, mouth, or central face.
- **2.5s Bounded Lifetime**: Overlay props automatically exit after 1.8s–3.2s with a soft zip-out whoosh, preventing screen clutter and visual fatigue.

### Rule 58: Kinetic Typography & Angled Chapter Headings (`video_editor_studio.py heading`)
- **Single-Word Hormozi Badges**: Displays strictly the active spoken word with millisecond precision, highlighted in high-contrast amber/cyan/crimson with a translucent dark backing pill.
- **Animated Chapter Heading Cards**: Generated via `video_editor_studio.py heading "Chapter Title"` with double border frames, parchment or slate backdrops, and continuous Ken Burns push-in ($1.00\times \to 1.045\times$).
- **Angled Text Badges**: Chapter subheadings and curiosity tags tilted at -3.5° to -5.0° with heavy 12–16px dark stroke and soft drop shadow.

### Rule 59: The 5-Layer Broadcast Foley Mix (SFX Hierarchy) (`sfx_smart_designer.py`)
- **Layer 1 (Sub-Bass Foundation)**: 40Hz–65Hz resonant boom (-1.5 dBFS) at frame 0 and major chapter transitions.
- **Layer 2 (Tactile Foley)**: Real-world physical textures (wood clacks, paper rustles, marker squeaks, coin drops) at -14 dBFS synced to cuts and stickers.
- **Layer 3 (Auditory Highlighters)**: Micro-transient pings, chimes, and bell tones at -22 dBFS marking dates, percentages, and metrics.
- **Layer 4 (The Vox Drop-Out)**: Strict 0.4s–0.8s digital silence vacuum immediately before punchlines or twist reveals.
- **Layer 5 (Ducked Music Bed)**: 100% CC0 background music ducked to -24 dBFS during voiceover with smooth 120ms release.

### Rule 60: Dynamic Camera Kinetics & Split-Screen Multi-Track Editing
- **The Ken Burns Law**: Any visual hold exceeding 2.0s must apply a continuous slow scale push-in ($1.00\times \to 1.045\times$). Static, lifeless frames are strictly prohibited.
- **Dialogue Shot-Reverse-Shot**: During multi-character dialogue (OverSimplified style), camera cuts alternate between characters every 0.8s–1.4s.
- **Split-Screen Comparisons**: "Then vs Now" or "Expectation vs Reality" visual comparisons split by a clean vertical divider line with sound-swapping audio balance.

### Rule 61: The Plain Paper Palate Cleanser Standard (Ink Explainer 19.3M Benchmark)
- **The Visual Reset Principle**: Instead of flashy lower-third badges or 3D title cards, the visual cuts every 45–75 seconds to a **100% Plain Off-White Paper Page** (`#FAF8F2` or `#FFFFFF`).
- **Cognitive Purpose**: Acts as a biological sensory palate cleanser. Breaks visual overstimulation, resets eye fatigue, and concentrates 100% of the viewer's cognitive bandwidth onto a single shocking statistic, study attribution, or existential question.
- **Visual Composition**:
  1. **Background**: Pure, uncluttered off-white parchment with ultra-subtle grain.
  2. **Typography**: Hand-drawn felt-pen aesthetic (`#1A1A1A` charcoal ink), centered with generous negative breathing space ($>70\%$ empty canvas).
  3. **Reaction Stickman**: Optional minimalist stickman positioned in a lower third or side corner in an expressive reaction pose (`shock`, `think`, or `point`), silently processing the text alongside the audience.
  4. **Kinetics**: Micro push-in ($1.00\times \to 1.025\times$) over 2.0s–3.0s duration; never static.
  5. **CLI Generation**: `python3 studio.py page "40,000 HOURS" --subtitle "OF YOUR LIFE — WORKING" --pose shock`

### Multi-Skill Orchestration Ecosystem
The pipeline is fortified with 7 integrated companion skills:
- `skills/youtube-seo-optimizer`: High-intent search keyword discovery, optimized descriptions, curiosity timestamps.
- `skills/emotional-arc-designer`: Affective sequence mapping from skeptical entry to awe-inspired exit.
- `skills/visual-emotion-engineer`: Arousal-valence visual design, typography personality, cognitive load minimization.
- `skills/headline-psychologist`: Loewenstein prediction error headlines and self-relevance triggers.
- `skills/loss-aversion-designer`: Downside risk framing and credible cost of inaction.
- `skills/data-storytelling`: Data/Narrative/Visual 3-pillar narrative structure.
- `skills/viral-generator-builder`: Screenshot-tested identity moments and viral mechanics.





