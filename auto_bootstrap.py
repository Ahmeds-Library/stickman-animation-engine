#!/usr/bin/env python3
"""auto_bootstrap.py: Root Entrypoint for Autonomous Engine Bootstrapper
Single source of truth located at skills/stickman-hybrid/scripts/auto_bootstrap.py.
"""
import os
import sys

ENGINE_BOOTSTRAP = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "skills", "stickman-hybrid", "scripts", "auto_bootstrap.py"
)

if os.path.exists(ENGINE_BOOTSTRAP):
    import importlib.util
    spec = importlib.util.spec_from_file_location("engine_auto_bootstrap", ENGINE_BOOTSTRAP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "main"):
        mod.main()
    elif hasattr(mod, "bootstrap_engine"):
        mod.bootstrap_engine()
else:
    sys.exit(f"❌ Core engine bootstrapper not found at {ENGINE_BOOTSTRAP}")
