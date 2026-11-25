"""LINES.tsv -> takes/NN.wav with Kokoro (local, CPU, Apache 2.0, commercial OK)

    python scripts/kokoro_vo.py LINES.tsv --lang a --voice am_michael --out takes

--lang   a American English · b British English · e Spanish · f French
         i Italian · p Brazilian Portuguese · h Hindi / Urdu · j Japanese · z Mandarin
         (j needs: python -m pip install "misaki[ja]"; z needs "misaki[zh]")
--voice  e.g. af_heart, af_bella, am_michael, am_fenrir (US); bf_emma, bm_george (UK).
         The full list is at https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
--speed  1.0 is normal standard English pace (crisp, engaging, natural prosody)
--force  overwrite existing takes (default: False, resumes existing)
"""
import argparse, csv, os, re, sys
import numpy as np, soundfile as sf

# Autonomous Zero-Setup Bootstrapper
try:
    boot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../stickman-hybrid/scripts"))
    if boot_path not in sys.path:
        sys.path.insert(0, boot_path)
    import auto_bootstrap
    auto_bootstrap.ensure_environment()
except Exception:
    pass


def synthesize_line(pipe, text, voice="am_michael", speed=1.0):
    """Synthesizes text with natural English prosody at normal 1.0x speed.
    Kokoro's neural phonemizer automatically handles English punctuation,
    inflection, and clause cadence smoothly without dragging or artificial gaps.
    Enforces V6 studio purity: DC-offset removal + 15ms boundary micro-fades to kill transient clicks.
    """
    clean_text = text.strip()
    gen = pipe(clean_text, voice=voice, speed=speed)
    audios = [np.asarray(x[2], np.float32) for x in gen]
    if not audios:
        return np.zeros(0, dtype=np.float32)
    arr = np.concatenate(audios)
    if len(arr) == 0:
        return arr
    # 1. DC offset removal
    arr = arr - np.mean(arr)
    # 2. 0.015s boundary micro-fade to eliminate clicks/transients at take boundaries
    fade_len = int(0.015 * 24000)
    if len(arr) > 2 * fade_len:
        fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
        fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
        arr[:fade_len] *= fade_in
        arr[-fade_len:] *= fade_out
    return arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lines")
    ap.add_argument("--lang", default="a")
    ap.add_argument("--voice", default="am_michael")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--out", default="takes")
    ap.add_argument("--force", action="store_true", help="Overwrite existing takes")
    a = ap.parse_args()
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=a.lang)
    os.makedirs(a.out, exist_ok=True)
    with open(a.lines, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        p = f"{a.out}/{r['id']}.wav"
        if os.path.exists(p) and not a.force:
            continue                     # re-run safe unless --force
        audio = synthesize_line(pipe, r["text"], voice=a.voice, speed=a.speed)
        sf.write(p, audio, 24000)
        print(f"[{r['id']}] {len(audio) / 24000:.2f}s: {r['text'][:40]}...", flush=True)
    print(f"takes in {a.out}/ -- next: python scripts/vo_join.py {a.out} {a.lines}")


if __name__ == "__main__":
    main()
