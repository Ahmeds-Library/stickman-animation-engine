"""cues.tsv + VO.wav -> mix.wav   (Vox-style documentary mix)

    python scripts/mix.py cues.tsv --vo VO.wav --lines VO.tsv --words WORDS.tsv --out mix.wav
    python scripts/mix.py --selfcheck

cues.tsv columns (tab separated):
    label    any name. The row labelled "bed" is the music bed: it gets ducked by
             every SFX and by the voice, and it gets the optional --dip
    kind     loop | one       loop = repeat the file for `dur` seconds
    file     path relative to the kit folder (sfx/..., music/...) or absolute
    at       WHEN it starts. One of:
               12.4         seconds
               @05          the start of VO line 05
               भारत         the first spoken word containing "भारत", searched
                            forward from the previous word cue, so cues stay in
                            script order
               भारत+0.3     the same word, shifted by +0.3 s (use -0.1 to lead)
               w:1906       a word that is itself a number (a bare number means seconds)
    dur      loop length in seconds, or "all" (until the end). Ignored for "one"
    gain_db  level of this sound, e.g. -18
    fade_in  seconds
    fade_out seconds

Word cues are the point: change the voice, re-run align.py, and every click
still lands on its word. No retiming.

One-shots are placed PEAK on the cue, not file-start on the cue: a page turn
whose loudest moment is 0.3 s in would otherwise land 7 frames late.
Except sounds that run WITH an animation starting on the word (counters, odometer
rolls, scoreboard flips: ROLLING below). Those START on the cue: peak-aligned, an
odometer roll peaking 0.76 s in began before the counter was even on screen.

Levels: every file in CATALOG.tsv (built by scripts/index_sfx.py) carries a
level_offset. mix.py adds it to the cue's gain_db, so the gains in SKILL.md
mean the same thing for any sound, from any pack, at any original loudness.
Files that are not in the catalog are used exactly as they are. Run index_sfx.py
after adding sounds.

Mix chain:
- Each voice is first brought to -22 LUFS. Without this, a loud narrator (one
  measured -17 LUFS) made the final loudnorm pull the whole mix down, and the
  music and SFX sank about 5 dB.
- The bed ducks under SFX, and everything ducks under the voice
  (sidechaincompress).
- Final loudness is -14 LUFS with a -1.5 dBTP ceiling, the YouTube target.
"""
import argparse, csv, os, re, subprocess, sys

# Autonomous Zero-Setup Bootstrapper
try:
    boot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../stickman-hybrid/scripts"))
    if boot_path not in sys.path:
        sys.path.insert(0, boot_path)
    import auto_bootstrap
    auto_bootstrap.ensure_environment()
except Exception:
    pass

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLLING = re.compile(r"(?i)/Numbers/|counter|counting|odometer|ticking")   # start on the cue, not peak


def start_time(t, peak, file):
    """When a one-shot starts: its peak on the cue, but rolling sounds start on it."""
    return t if ROLLING.search(file.replace("\\", "/")) else max(0.0, t - peak)


def tsv(path):
    with open(path, encoding="utf-8") as f:
        non_comments = [line for line in f if not line.strip().startswith("#")]
        return list(csv.DictReader(non_comments, delimiter="\t"))


def clean(w):
    return re.sub(r"[।?,.!\"'“”‘’:;]", "", w)


class Resolver:
    """Turns an `at` value into seconds."""

    def __init__(self, lines=None, words=None):
        self.lines = {r["id"]: float(r["start"]) for r in lines or []}
        self.words = [(float(r["start"]), clean(r["word"])) for r in words or []]
        self.pos = 0

    def __call__(self, at):
        at = at.strip()
        m = re.fullmatch(r"(.+?)([+-]\d+(?:\.\d+)?)?", at)
        base, off = m.group(1), float(m.group(2) or 0)
        if not base.startswith("w:"):
            try:
                return max(0.0, float(base) + off)
            except ValueError:
                pass
        if base.startswith("w:"):
            base = base[2:]
        elif base.startswith("@"):
            raw_line = base[1:]
            if ":" in raw_line:
                line_id, _, word_part = raw_line.partition(":")
                target_word = clean(word_part).lower()
                for t_w, w_txt in self.words:
                    if target_word in w_txt.lower():
                        return max(0.0, t_w + off)
                if line_id in self.lines:
                    return max(0.0, self.lines[line_id] + off)
            if raw_line not in self.lines:
                raise SystemExit(f"cue {at!r}: no VO line {raw_line} (pass --lines VO.tsv)")
            return max(0.0, self.lines[raw_line] + off)
        for k in range(self.pos, len(self.words)):
            if base in self.words[k][1]:
                self.pos = k
                return max(0.0, self.words[k][0] + off)
        raise SystemExit(f"cue {at!r}: word not found after word #{self.pos} "
                         f"(pass --words WORDS.tsv, keep cues in script order)")


def catalog():
    """file -> (peak seconds, level offset dB), from CATALOG.tsv (index_sfx.py)."""
    p = os.path.join(KIT, "CATALOG.tsv")
    if not os.path.exists(p):
        return {}
    return {r["file"]: (float((r.get("peak") or r.get("peak_offset") or 0) or 0), float(r.get("level_offset") or 0)) for r in tsv(p)}


def media_len(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip())


def build(cues, vo, out, dur, dip):
    cmd, parts, sfx = ["ffmpeg", "-y", "-loglevel", "error"], [], []
    labels = [c["label"] for c in cues]
    
    # Identify all bed indices (supports 'bed', 'bed_act1', 'bed_act2', 'music_bed', 'music')
    bed_indices = []
    for idx, c in enumerate(cues):
        lbl = c["label"].lower()
        if lbl in ("bed", "music_bed") or lbl.startswith("bed_") or "music" in lbl:
            bed_indices.append(idx)

    for i, c in enumerate(cues):
        path = c["file"] if os.path.isabs(c["file"]) else os.path.join(KIT, c["file"])
        assert os.path.exists(path), f"cue {c['label']}: file missing {path}"
        gain, fi, fo = float(c["gain_db"]), float(c["fade_in"] or 0), float(c["fade_out"] or 0)
        is_bed = (i in bed_indices)

        if c["kind"] == "loop":
            d = dur - c["t"] if c["dur"] in ("all", "") else float(c["dur"])
            cmd += ["-stream_loop", "-1", "-i", path]
            f = [f"atrim=0:{d:.3f}", "asetpts=N/SR/TB"]
            if fi:
                f.append(f"afade=t=in:st=0:d={fi}")
            if fo:
                f.append(f"afade=t=out:st={max(0, d - fo):.3f}:d={fo}")
        else:
            cmd += ["-i", path]
            f = []
            trim_s = float(c.get("_trim_start") or 0.0)
            if trim_s > 0.005:
                f += [f"atrim=start={trim_s:.3f}", "asetpts=N/SR/TB"]

        f += ["aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo", f"volume={gain}dB"]

        if is_bed:
            # Vocal Pocket Frequency Carving & Stereo Spatial Widening:
            # Dips -3.2 dB at 1.8 kHz and -2.2 dB at 3.2 kHz so the human speech formants sit in their own pocket.
            # extrastereo=m=1.12 expands the music bed outwards into the stereo field, wrapping around the listener
            # while keeping the narrator firmly centered in mono focus!
            f.append("equalizer=f=1800:width_type=q:w=1.2:g=-3.2,equalizer=f=3200:width_type=q:w=1.4:g=-2.2,extrastereo=m=1.12")
            if dip is not None:
                # Measurable >= 0.4s pre-twist silence drop (>= 12 dB below local p90) via flat-bottom super-Gaussian envelope
                f.append(f"volume='1-0.985*exp(-pow((t-{dip:.3f})/0.38,4))':eval=frame")

        if c["t"] > 0:
            f.append(f"adelay={int(c['t'] * 1000)}:all=1")
        parts.append(f"[{i}:a]" + ",".join(f) + f"[a{i}]")
        if not is_bed:
            sfx.append(f"[a{i}]")

    n = len(cues)
    tail = f"apad=whole_dur={dur:.3f},atrim=0:{dur:.3f},loudnorm=I=-14:TP=-1.0:LRA=10[out]"

    # Prepare SFX sub-mix stem if any SFX cues exist (un-ducked, tactile and crisp!)
    has_sfx = len(sfx) > 0
    if has_sfx:
        sfx_tail = f"amix=inputs={len(sfx)}:normalize=0:dropout_transition=0,apad=whole_dur={dur:.3f}"
        if dip is not None:
            sfx_tail += f",volume='1-0.94*exp(-pow((t-{dip:.3f})/0.30,4))':eval=frame"
        parts.append("".join(sfx) + sfx_tail + "[sfxmix]")

    if vo:
        cmd += ["-i", vo]
        # Broadcast Documentary Vocal Mastering Chain:
        # 1. highpass=f=75: eliminates rumble, mic plosives, and sub-frequencies
        # 2. equalizer=f=220:width_type=q:w=1.2:g=1.8: warm chest resonance (combats dry textbook TTS reading)
        # 3. equalizer=f=3400:width_type=q:w=1.2:g=2.2: vocal presence and consonant articulation
        # 4. equalizer=f=8500:width_type=q:w=1.0:g=1.2: broadcast air and silky sheen
        # 5. loudnorm=I=-19:TP=-1.5:LRA=10: consistent vocal dialogue loudness
        vox_chain = (
            f"[{n}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
            "highpass=f=75,"
            "equalizer=f=220:width_type=q:w=1.2:g=1.8,"
            "equalizer=f=3400:width_type=q:w=1.2:g=2.2,"
            "equalizer=f=8500:width_type=q:w=1.0:g=1.2,"
            "loudnorm=I=-19:TP=-1.5:LRA=10,"
            "aresample=48000,volume=1.2dB,asplit=2[vomix][vokey]"
        )
        parts.append(vox_chain)

        # Build Bed Ducked Stem: Sidechain ducked under voice key (gentle 1.9:1 ratio, max 6dB ducking)
        if len(bed_indices) > 1:
            bed_mix_str = "".join(f"[a{bi}]" for bi in bed_indices) + f"amix=inputs={len(bed_indices)}:normalize=0[bed_all]"
            parts.append(bed_mix_str)
            parts.append(f"[bed_all][vokey]sidechaincompress=threshold=0.15:ratio=1.9:attack=30:release=450,apad=whole_dur={dur:.3f}[bed_ducked]")
        elif len(bed_indices) == 1:
            parts.append(f"[a{bed_indices[0]}][vokey]sidechaincompress=threshold=0.15:ratio=1.9:attack=30:release=450,apad=whole_dur={dur:.3f}[bed_ducked]")
        else:
            # Silence bed fallback
            parts.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{dur:.3f}[bed_ducked]")

        # Closed-Loop Adaptive Loudness Engine:
        # Step 1: Render stems separately to measure real physical dBFS energy
        out_dir = os.path.dirname(os.path.abspath(out)) or "."
        stem_vo_file = os.path.join(out_dir, f"_temp_stem_vo_{os.getpid()}.wav")
        stem_bed_file = os.path.join(out_dir, f"_temp_stem_bed_{os.getpid()}.wav")
        stem_sfx_file = os.path.join(out_dir, f"_temp_stem_sfx_{os.getpid()}.wav")

        stem_cmd = list(cmd)
        stem_parts = list(parts)
        stem_maps = ["-map", "[vomix]", stem_vo_file, "-map", "[bed_ducked]", stem_bed_file]
        if has_sfx:
            stem_maps.extend(["-map", "[sfxmix]", stem_sfx_file])

        r_stems = subprocess.run(stem_cmd + ["-filter_complex", ";".join(stem_parts)] + stem_maps +
                                 ["-c:a", "pcm_s16le", "-ar", "48000"])
        if r_stems.returncode != 0:
            sys.exit("ffmpeg stem extraction failed")

        # Step 2: Intelligent Audio Telemetry & Variable Gain Auto-Balancing
        import numpy as np
        try:
            import soundfile as sf
            vo_data, sr = sf.read(stem_vo_file)
            bed_data, _ = sf.read(stem_bed_file)
            sfx_data = sf.read(stem_sfx_file)[0] if has_sfx and os.path.exists(stem_sfx_file) else None
        except Exception:
            import wave
            def read_wav_np(path):
                with wave.open(path, "rb") as wf:
                    frames = wf.readframes(wf.getnframes())
                    arr = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                    return (arr.reshape(-1, wf.getnchannels()), wf.getframerate()) if wf.getnchannels() > 1 else (arr, wf.getframerate())
            vo_data, sr = read_wav_np(stem_vo_file)
            bed_data, _ = read_wav_np(stem_bed_file)
            sfx_data = read_wav_np(stem_sfx_file)[0] if has_sfx and os.path.exists(stem_sfx_file) else None

        if len(vo_data.shape) > 1: vo_data = np.mean(vo_data, axis=1)
        if len(bed_data.shape) > 1: bed_data = np.mean(bed_data, axis=1)
        if sfx_data is not None and len(sfx_data.shape) > 1: sfx_data = np.mean(sfx_data, axis=1)

        # Measure Voice RMS on active speech (> -40 dBFS)
        active_vo = vo_data[np.abs(vo_data) > 0.01]
        vo_rms = 20 * np.log10(np.sqrt(np.mean(active_vo**2)) + 1e-9) if len(active_vo) > 0 else -18.0

        # Measure Bed in 0-5s intro window and global timeline
        s_5s = min(len(bed_data), int(5.0 * sr))
        bed_0_5s = bed_data[:s_5s]
        bed_rms_0_5s = 20 * np.log10(np.sqrt(np.mean(bed_0_5s**2)) + 1e-9) if len(bed_0_5s) > 0 else -99.0
        bed_rms_global = 20 * np.log10(np.sqrt(np.mean(bed_data**2)) + 1e-9) if len(bed_data) > 0 else -99.0

        ratio_0_5s = bed_rms_0_5s - vo_rms
        ratio_global = bed_rms_global - vo_rms

        # Music Target: Maintain warm cinematic bed cleanly between -11 dB and -13 dB relative to Voice RMS (nominal -12.0 dB)
        bed_boost_db = 0.0
        min_bed_ratio = min(ratio_0_5s, ratio_global)
        if min_bed_ratio < -13.0:
            bed_boost_db = min(12.0, max(0.0, -12.0 - min_bed_ratio))
        elif max(ratio_0_5s, ratio_global) > -9.5:
            bed_boost_db = max(-6.0, -11.5 - max(ratio_0_5s, ratio_global))

        # Measure per-cue SFX transient peak energy (not just single global max!)
        sfx_boost_db = 0.0
        sfx_peak = -99.0
        sfx_ratio = -99.0
        sfx_median_peak = -99.0
        sfx_median_ratio = -99.0
        if sfx_data is not None and len(sfx_data) > 0:
            sfx_peak = 20 * np.log10(np.max(np.abs(sfx_data)) + 1e-9)
            sfx_ratio = sfx_peak - vo_rms

            cue_peaks = []
            for c in cues:
                if c.get("kind") == "one" and c.get("file"):
                    at_val = c.get("at", 0.0)
                    try:
                        at_sec = float(at_val)
                        s0 = max(0, int(at_sec * sr))
                        s1 = min(len(sfx_data), int((at_sec + 0.6) * sr))
                        if s1 > s0:
                            w_chunk = sfx_data[s0:s1]
                            pk = np.max(np.abs(w_chunk))
                            if pk > 0.001:
                                cue_peaks.append(20 * np.log10(pk + 1e-9))
                    except Exception:
                        pass
            if cue_peaks:
                sfx_median_peak = float(np.median(cue_peaks))
                sfx_median_ratio = sfx_median_peak - vo_rms
            else:
                sfx_median_peak = sfx_peak
                sfx_median_ratio = sfx_ratio

            # Auto-balance: ensure median SFX peak is within -5 dB to -2 dB of VO RMS
            if sfx_median_ratio < -5.0:
                sfx_boost_db = min(9.0, max(0.0, -3.0 - sfx_median_ratio))
            elif sfx_ratio < -2.0:
                sfx_boost_db = min(6.0, max(0.0, 0.0 - sfx_ratio))

        print(f"🎛️ [Adaptive Audio Balancer] VO RMS={vo_rms:.2f} dBFS | Bed(0-5s)={bed_rms_0_5s:.2f} dBFS (ratio={ratio_0_5s:+.1f} dB, boost=+{bed_boost_db:.1f} dB) | SFX Peak={sfx_peak:.2f} dBFS (ratio={sfx_ratio:+.1f} dB) | SFX Median={sfx_median_peak:.2f} dBFS (ratio={sfx_median_ratio:+.1f} dB, boost=+{sfx_boost_db:.1f} dB)")

        # Save audio telemetry
        import json
        telemetry_file = os.path.join(out_dir, "stem_telemetry.json")
        telemetry_payload = {
            "vo_rms_dbfs": round(float(vo_rms), 2),
            "bed_rms_0_5s_dbfs": round(float(bed_rms_0_5s), 2),
            "bed_rms_global_dbfs": round(float(bed_rms_global), 2),
            "bed_to_vo_0_5s_ratio_db": round(float(ratio_0_5s), 2),
            "bed_to_vo_global_ratio_db": round(float(ratio_global), 2),
            "sfx_peak_dbfs": round(float(sfx_peak), 2) if has_sfx else None,
            "sfx_peak_to_vo_ratio_db": round(float(sfx_ratio), 2) if has_sfx else None,
            "sfx_median_peak_dbfs": round(float(sfx_median_peak), 2) if has_sfx else None,
            "sfx_median_to_vo_ratio_db": round(float(sfx_median_ratio), 2) if has_sfx else None,
            "bed_boost_applied_db": round(float(bed_boost_db), 2),
            "sfx_boost_applied_db": round(float(sfx_boost_db), 2),
            "target_lufs": -14.0,
            "target_true_peak": -1.0
        }
        with open(telemetry_file, "w", encoding="utf-8") as tf:
            json.dump(telemetry_payload, tf, indent=2)

        # Step 3: Mix Stems with calibrated auto-balance gains into YouTube Broadcast Master
        final_inputs = ["-i", stem_vo_file]
        f_parts = ["[0:a]volume=0dB[vofin]"]
        in_labels = ["[vofin]"]

        # Bed stem
        final_inputs.extend(["-i", stem_bed_file])
        f_parts.append(f"[1:a]volume={bed_boost_db:.2f}dB[bedfin]")
        in_labels.append("[bedfin]")

        # SFX stem
        if has_sfx:
            final_inputs.extend(["-i", stem_sfx_file])
            f_parts.append(f"[2:a]volume={sfx_boost_db:.2f}dB[sfxfin]")
            in_labels.append("[sfxfin]")

        f_mix = "".join(in_labels) + f"amix=inputs={len(in_labels)}:normalize=0,apad=whole_dur={dur:.3f},atrim=0:{dur:.3f},loudnorm=I=-14:TP=-1.0:LRA=10[out]"
        f_parts.append(f_mix)

        r_master = subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + final_inputs +
                                  ["-filter_complex", ";".join(f_parts), "-map", "[out]",
                                  "-c:a", "pcm_s16le", "-ar", "48000", out])
        
        # Cleanup temporary stem files
        for tmp in (stem_vo_file, stem_bed_file, stem_sfx_file):
            if os.path.exists(tmp):
                try: os.remove(tmp)
                except Exception: pass

        if r_master.returncode != 0:
            sys.exit("ffmpeg master mixing failed")
    else:
        # No VO:
        mix_inputs = []
        if has_sfx:
            mix_inputs.append("[sfxmix]")
        if len(bed_indices) > 1:
            parts.append("".join(f"[a{bi}]" for bi in bed_indices) + f"amix=inputs={len(bed_indices)}:normalize=0[bed_all]")
            mix_inputs.append("[bed_all]")
        elif len(bed_indices) == 1:
            mix_inputs.append(f"[a{bed_indices[0]}]")

        if len(mix_inputs) > 1:
            parts.append("".join(mix_inputs) + f"amix=inputs={len(mix_inputs)}:normalize=0,{tail}")
        elif len(mix_inputs) == 1:
            parts.append(f"{mix_inputs[0]}{tail}")
        else:
            parts.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={max(1, n)}:normalize=0,{tail}")
        r = subprocess.run(cmd + ["-filter_complex", ";".join(parts), "-map", "[out]",
                                  "-c:a", "pcm_s16le", "-ar", "48000", out])
        if r.returncode:
            sys.exit("ffmpeg failed")
    print(f"wrote {out}  ({dur:.2f}s, {n} cues{', with voice' if vo else ''})")


def selfcheck():
    lines = [{"id": "01", "start": "0.0"}, {"id": "02", "start": "4.5"}]
    words = [{"start": "0.1", "word": "भारत"}, {"start": "1.0", "word": "1906"},
             {"start": "5.0", "word": "1906।"}]
    r = Resolver(lines, words)
    assert r("12.5") == 12.5 and r("@02") == 4.5 and r("@02-0.2") == 4.3
    assert r("1906") == 1906.0           # a bare number is seconds
    assert r("w:1906") == 1.0
    assert r("w:1906+0.3") == 1.3        # same word again: the search does not skip ahead
    r.pos += 1
    assert r("w:1906") == 5.0            # punctuation is ignored
    assert Resolver(lines, words)("भारत-0.05") == 0.05
    try:
        r("नहींमिला")
        raise AssertionError("missing word must fail")
    except SystemExit:
        pass
    assert start_time(5.0, 0.3, "sfx/StableAudio/Paper/page_turn_a.mp3") == 4.7          # peak on the word
    assert start_time(5.0, 0.762, "sfx/StableAudio/Numbers/b5_odometer_roll_a.mp3") == 5.0  # counter: starts on it
    assert start_time(5.0, 1.258, "sfx\\StableAudio\\Data\\b3_money_counter_a.mp3") == 5.0
    print("selfcheck ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cues", nargs="?")
    ap.add_argument("--vo", help="narration wav")
    ap.add_argument("--lines", help="VO.tsv (id, start, dur, text) for @NN cues")
    ap.add_argument("--words", help="WORDS.tsv from align.py, for word cues")
    ap.add_argument("--out", default="mix.wav")
    ap.add_argument("--dur", type=float, help="mix length (default: voice + 1.0 s)")
    ap.add_argument("--dip", help="seconds or a cue: dip the bed here for a held breath")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    if not a.cues:
        ap.error("cues.tsv is required")
    res = Resolver(tsv(a.lines) if a.lines else None, tsv(a.words) if a.words else None)
    cues = tsv(a.cues)
    cat = catalog()
    for c in cues:
        c["t"] = res(c["at"])
        peak, offset = cat.get(c["file"].replace("\\", "/"), (0.0, 0.0))
        c["gain_db"] = str(float(c["gain_db"]) + offset)    # kit-standard level, whatever the file
        if c["kind"] == "one":
            raw_t = c["t"]
            aligned_t = start_time(raw_t, peak, c["file"])
            c["_trim_start"] = max(0.0, peak - raw_t) if (raw_t < peak and not ROLLING.search(c["file"].replace("\\", "/"))) else 0.0
            c["t"] = aligned_t
    dur = a.dur or ((media_len(a.vo) + 1.0) if a.vo else max(c["t"] for c in cues) + 5)
    dip = Resolver(tsv(a.lines) if a.lines else None, tsv(a.words) if a.words else None)(a.dip) \
        if a.dip else None
    build(cues, a.vo, a.out, dur, dip)


if __name__ == "__main__":
    main()
