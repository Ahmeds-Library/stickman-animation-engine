#!/usr/bin/env python3
"""render.py: Legacy Forwarding Stub -> render_pro.py
⚠️ DEPRECATION NOTICE: render.py has been upgraded to render_pro.py.
All video rendering now routes through render_pro.py which enforces:
1. 6 Broadcast Visual Archetypes (card_stat, split_compare, bar_timeline, stat_pie, virtual_multicam, verdict_stamps)
2. 2x Supersampled Lanczos anti-aliasing
3. Curated 4-font typography hierarchy
4. Real transparent sticker composition
5. Dynamic 9-look color palettes
6. Post-mux FFmpeg volume & audio stream verification
"""

import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RENDER_PRO = os.path.join(SCRIPT_DIR, "render_pro.py")

def main():
    print("ℹ️ [NOTICE]: Routing rendering call from legacy render.py -> render_pro.py...")
    if not os.path.exists(RENDER_PRO):
        sys.exit(f"❌ render_pro.py not found at {RENDER_PRO}")
    cmd = [sys.executable, RENDER_PRO] + sys.argv[1:]
    res = subprocess.run(cmd)
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
