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


def _trim_and_fade(arr, sr=24000, floor=0.006, fade_sec=0.012):
    if len(arr) == 0:
        return arr
    arr = arr - np.mean(arr)
    loud = np.abs(arr) > floor
    if loud.any():
        pad = int(0.008 * sr)
        i0 = max(0, int(np.argmax(loud)) - pad)
        i1 = min(len(arr), len(arr) - int(np.argmax(loud[::-1])) + pad)
        arr = arr[i0:i1]
    fade_len = int(fade_sec * sr)
    if len(arr) > 2 * fade_len:
        arr[:fade_len] *= np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
        arr[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
    return arr


def _split_prosody_clauses(text):
    """Detects enumerated comma lists (2-4 items) and explicit dramatic pauses for breathable spoken prosody."""
    clean = re.sub(r"\s+", " ", text.strip())
    if "[pause]" in clean.lower():
        segs = [s.strip() for s in re.split(r"\[pause\]", clean, flags=re.I) if s.strip()]
        if len(segs) >= 2:
            return [(s, 0.36) for s in segs[:-1]] + [(segs[-1], 0.0)]

    if "..." in clean or " — " in clean:
        segs = [s.strip() for s in re.split(r"\s*(?:\.\.\.|—)\s*", clean) if s.strip()]
        if len(segs) >= 2:
            return [(s + ("," if not s.endswith((".", "!", "?", ",")) else ""), 0.34) for s in segs[:-1]] + [(segs[-1], 0.0)]

    # Detect enumerated lists with commas: e.g. 'Then came modern sugar, coffee, and soda!' or 'fiber, water, zero sugar.'
    m_list = re.match(
        r"^(.*?),\s+([^,]{2,28}),\s+(?:(and|or)\s+)?([^,]{2,28}[.!?]?)$",
        clean, flags=re.IGNORECASE
    )
    if m_list:
        head = m_list.group(1).strip() + ","
        mid = m_list.group(2).strip() + ","
        conj = (m_list.group(3) + " ") if m_list.group(3) else ""
        tail = conj + m_list.group(4).strip()
        if len(head.split()) <= 8 and len(mid.split()) <= 4 and len(tail.split()) <= 5:
            return [(head, 0.28), (mid, 0.28), (tail, 0.0)]

    return [(clean, 0.0)]


def _clean_pronunciation(text):
    """Applies phonetic respellings for ancient/historical proper nouns mispronounced by English G2P."""
    t = re.sub(r"\bBaal\b", "Bahl", text)
    t = re.sub(r"\bbaal\b", "bahl", t)
    t = re.sub(r"\bBa'al\b", "Bahl", t)
    t = re.sub(r"\bIshbaal\b", "Ish-bahl", t)
    t = re.sub(r"\bBeeliada\b", "Bee-el-eye-ada", t)
    t = re.sub(r"\bZebul\b", "Zeh-bool", t)
    t = re.sub(r"\bZevuv\b", "Zeh-voov", t)
    return t


def synthesize_line(pipe, text, voice="am_michael", speed=1.0):
    """Synthesizes text with natural English prosody and Clause/Enumeration Breath Pacing.
    Enforces V10 studio purity: enumerated list spacing (0.34s between items), DC-offset removal, & 14ms micro-fades.
    """
    clauses = _split_prosody_clauses(_clean_pronunciation(text))
    chunks = []
    for clause_txt, pause_after in clauses:
        gen = pipe(clause_txt.strip(), voice=voice, speed=speed)
        audios = [np.asarray(x[2], np.float32) for x in gen]
        if not audios:
            continue
        seg = _trim_and_fade(np.concatenate(audios), sr=24000)
        if len(seg) > 0:
            chunks.append(seg)
            if pause_after > 0.0:
                chunks.append(np.zeros(int(pause_after * 24000), dtype=np.float32))
    if not chunks:
        return np.zeros(0, dtype=np.float32)
    return _trim_and_fade(np.concatenate(chunks), sr=24000)


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
