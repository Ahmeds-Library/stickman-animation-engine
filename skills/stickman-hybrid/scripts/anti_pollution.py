#!/usr/bin/env python3
"""anti_pollution.py: Strict Repository Anti-Pollution Shield
Enforces Rule 23 & Pillar 5:
Generated projects, manifests, audio/video renders, and caches must live strictly
OUTSIDE the repository root. Rejects any internal path or current working directory
with a clear, informative ValueError.
"""

import os
import sys

def get_repo_root():
    """Detects repository root by searching upward for CLAUDE.md and skills directory."""
    curr = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    while curr and curr != os.path.dirname(curr):
        if os.path.exists(os.path.join(curr, "CLAUDE.md")) and os.path.isdir(os.path.join(curr, "skills")):
            return os.path.realpath(curr)
        curr = os.path.dirname(curr)
    # Secondary check from cwd
    curr = os.path.realpath(os.getcwd())
    while curr and curr != os.path.dirname(curr):
        if os.path.exists(os.path.join(curr, "CLAUDE.md")) and os.path.isdir(os.path.join(curr, "skills")):
            return os.path.realpath(curr)
        curr = os.path.dirname(curr)
    return os.path.realpath("/home/mirza-ahmed-hassan/Desktop/stickman-animation")


def validate_external_output_dir(target_dir):
    """
    Validates that target_dir is strictly OUTSIDE the repo root.
    Raises ValueError with explanatory guidance if target_dir is inside repo root.
    Returns normalized absolute real path of target_dir.
    """
    if not target_dir:
        raise ValueError("🚨 [ANTI-POLLUTION GUARD REJECTION]: Target output directory cannot be empty.")

    target_abs = os.path.realpath(os.path.abspath(os.path.expanduser(target_dir)))
    repo_root = get_repo_root()

    try:
        common = os.path.commonpath([repo_root, target_abs])
        if common == repo_root:
            raise ValueError(
                f"🚨 [ANTI-POLLUTION GUARD REJECTION]: Target output directory '{target_abs}' "
                f"is located INSIDE repository root '{repo_root}'. "
                f"All generated projects, manifests, and media must live strictly outside the repo, "
                f"e.g. in ~/StickmanHybrid/<project_slug>/"
            )
    except ValueError as ve:
        if "ANTI-POLLUTION" in str(ve):
            raise ve
        # If paths are on different drives/mounts, commonpath throws ValueError; that means it's outside!
        pass

    return target_abs


if __name__ == "__main__":
    test_path = sys.argv[1] if len(sys.argv) > 1 else "."
    try:
        valid = validate_external_output_dir(test_path)
        print(f"✅ External output directory allowed: {valid}")
        sys.exit(0)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
