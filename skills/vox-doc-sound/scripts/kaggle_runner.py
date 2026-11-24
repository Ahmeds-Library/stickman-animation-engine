#!/usr/bin/env python3
"""kaggle_runner.py: Automated Native Language Voiceover Engine via Kaggle API
Automates Urdu/Roman Urdu Indic Parler-TTS voice synthesis:
1. Locates credentials from repo root .env (/home/mirza-ahmed-hassan/Desktop/stickman-animation/.env),
   ~/.kaggle/kaggle.json, or environment variables.
2. If interactive and missing, prompts the user, verifies .env in .gitignore, and saves with 0600 permissions.
   If non-interactive, outputs a structured actionable prompt for the AI agent to ask the user.
3. Automatically pushes the Parler kernel, polls status every 15s, downloads takes, joins them into VO.wav,
   and executes Whisper alignment into WORDS.tsv.
"""

import os, sys, json, re, time, shutil, subprocess, getpass, argparse

DEFAULT_REPO_ROOT = "/home/mirza-ahmed-hassan/Desktop/stickman-animation"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARLER_JOB_MAKER = os.path.abspath(os.path.join(SCRIPT_DIR, "../kaggle/make_parler_job.py"))
VO_JOIN = os.path.join(SCRIPT_DIR, "vo_join.py")
ALIGN_VO = os.path.join(SCRIPT_DIR, "align.py")


def find_repo_root(start_dir="."):
    """Traverses upward to find repository root containing .git or skills/."""
    curr = os.path.abspath(start_dir)
    while curr != os.path.dirname(curr):
        if os.path.exists(os.path.join(curr, ".git")) or os.path.exists(os.path.join(curr, "skills")):
            return curr
        curr = os.path.dirname(curr)
    return os.path.abspath(DEFAULT_REPO_ROOT)


def parse_env_file(env_path):
    """Parses key=value pairs from a .env file."""
    creds = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        creds[k.strip()] = v.strip().strip("'\"")
        except Exception as e:
            print(f"⚠️ Error reading {env_path}: {e}")
    return creds


def ensure_env_in_gitignore(repo_root):
    """Verifies that .env is present in repo_root/.gitignore before writing."""
    gi_path = os.path.join(repo_root, ".gitignore")
    if os.path.exists(gi_path):
        try:
            with open(gi_path, "r", encoding="utf-8") as f:
                content = f.read()
            if re.search(r"^\.env\b", content, re.MULTILINE):
                return True
            with open(gi_path, "a", encoding="utf-8") as f:
                f.write("\n.env\n")
            print(f"🛡️ Appended '.env' to {gi_path}")
            return True
        except Exception as e:
            print(f"⚠️ Warning checking .gitignore: {e}")
    return False


def get_kaggle_credentials(repo_root=None, prompt_if_missing=False):
    """Retrieves Kaggle credentials with fallback order:
    1. Environment variables (KAGGLE_USERNAME, KAGGLE_KEY)
    2. Repo root .env file (/home/mirza-ahmed-hassan/Desktop/stickman-animation/.env)
    3. User home config (~/.kaggle/kaggle.json)
    4. Interactive prompt (if prompt_if_missing=True and stdin is tty) with 0600 permissions
    """
    if not repo_root:
        repo_root = find_repo_root()

    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")

    # 2. Check repo root .env
    env_path = os.path.join(repo_root, ".env")
    if not (username and key) and os.path.exists(env_path):
        env_vars = parse_env_file(env_path)
        username = username or env_vars.get("KAGGLE_USERNAME")
        key = key or env_vars.get("KAGGLE_KEY")

    # 3. Check ~/.kaggle/kaggle.json
    home_kaggle = os.path.expanduser("~/.kaggle/kaggle.json")
    if not (username and key) and os.path.exists(home_kaggle):
        try:
            with open(home_kaggle, "r", encoding="utf-8") as jf:
                kj = json.load(jf)
                username = username or kj.get("username")
                key = key or kj.get("key")
        except Exception as e:
            print(f"⚠️ Warning reading ~/.kaggle/kaggle.json: {e}")

    if username and key:
        return username.strip(), key.strip()

    # 4. Handle Missing Credentials
    if prompt_if_missing and sys.stdin.isatty():
        print("\n🔑 [KAGGLE CREDENTIALS SETUP]")
        print("To automate Urdu/Roman Urdu Indic Parler voiceover, Kaggle API credentials are required.")
        try:
            u = input("Enter Kaggle Username: ").strip()
            k = getpass.getpass("Enter Kaggle API Key (invisible): ").strip()
            if u and k:
                ensure_env_in_gitignore(repo_root)
                existing_lines = []
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        existing_lines = [l for l in f if not l.startswith("KAGGLE_")]
                existing_lines.append(f"KAGGLE_USERNAME={u}\n")
                existing_lines.append(f"KAGGLE_KEY={k}\n")
                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(existing_lines)
                try:
                    os.chmod(env_path, 0o600)
                except Exception:
                    pass
                print(f"✅ Saved Kaggle credentials to {env_path} (mode 0600)")
                return u, k
        except (EOFError, KeyboardInterrupt):
            pass

    print(f"\n❌ [Kaggle Runner] Missing Kaggle credentials for native Urdu/Roman Urdu TTS.")
    print(f"   Please add KAGGLE_USERNAME and KAGGLE_KEY to: {env_path}")
    print(f"   or ~/.kaggle/kaggle.json. Run with --interactive to configure via terminal.")

    return None, None


def get_kaggle_cmd():
    """Returns command prefix for running kaggle CLI."""
    if shutil.which("kaggle"):
        return ["kaggle"]
    return [sys.executable, "-m", "kaggle.cli"]


def run_parler_kaggle_job(sub_dir, lines_tsv="LINES.tsv", speaker="Aman", style="natural", seed=11, timeout_sec=900):
    """Executes full autonomous Kaggle workflow for Parler-TTS voice generation."""
    repo_root = find_repo_root(sub_dir)
    username, key = get_kaggle_credentials(repo_root)
    if not username or not key:
        return False

    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key

    cwd = os.getcwd()
    try:
        os.chdir(sub_dir)
        if not os.path.exists(lines_tsv):
            raise FileNotFoundError(f"Missing {lines_tsv} in {sub_dir}")

        slug = f"parler-vo-{os.path.basename(os.path.abspath(sub_dir))}"
        job_dir = "parler_job"
        
        # 1. Create Parler Job
        print(f"📦 Creating Kaggle Parler kernel for {sub_dir} (User: {username}, Speaker: {speaker})...")
        subprocess.run([
            sys.executable, PARLER_JOB_MAKER, lines_tsv,
            "--user", username,
            "--speaker", speaker,
            "--style", style,
            "--seed", str(seed),
            "--slug", slug,
            "--out", job_dir
        ], check=True)

        k_cmd = get_kaggle_cmd()

        # 2. Push Kernel
        print(f"🚀 Pushing kernel {username}/{slug} to Kaggle GPU runner...")
        subprocess.run(k_cmd + ["kernels", "push", "-p", job_dir], check=True)

        # 3. Poll Status Every 15s
        print(f"⏳ Monitoring Kaggle job {username}/{slug}...")
        start_t = time.time()
        kernel_ref = f"{username}/{slug}"
        
        while time.time() - start_t < timeout_sec:
            time.sleep(15)
            status_res = subprocess.run(
                k_cmd + ["kernels", "status", kernel_ref],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            out = status_res.stdout.strip().lower()
            print(f"   Status ({int(time.time() - start_t)}s elapsed): {out}")
            
            if "complete" in out:
                print(f"✅ Kaggle Parler job completed successfully!")
                break
            elif "error" in out or "failed" in out:
                raise RuntimeError(f"🚨 Kaggle kernel {kernel_ref} execution failed: {status_res.stdout}\n{status_res.stderr}")
        else:
            raise TimeoutError(f"⏱️ Kaggle job timed out after {timeout_sec}s")

        # 4. Download Takes Output
        takes_dir = "takes"
        os.makedirs(takes_dir, exist_ok=True)
        print(f"📥 Downloading audio takes from {kernel_ref}...")
        subprocess.run(
            k_cmd + ["kernels", "output", kernel_ref, "-p", takes_dir, "--file-pattern", r"\.wav$|\.log$"],
            check=True
        )

        # 5. Join takes into VO.wav and VO.tsv
        print(f"🎚️ Joining takes into VO.wav and VO.tsv...")
        subprocess.run([sys.executable, VO_JOIN, takes_dir, lines_tsv, "--out", "VO"], check=True)

        # 6. Align words into WORDS.tsv
        print(f"⏱️ Aligning spoken Urdu words with Whisper...")
        subprocess.run([
            sys.executable, ALIGN_VO,
            "--vo", "VO.wav",
            "--lines", "VO.tsv",
            "--out", "WORDS.tsv",
            "--lang", "ur",
            "--model", "base"
        ], check=True)

        print(f"🎉 Native Urdu voiceover successfully generated and aligned in {sub_dir}!")
        return True
    finally:
        os.chdir(cwd)


def main():
    parser = argparse.ArgumentParser(description="Automated Native Voiceover Engine via Kaggle API")
    parser.add_argument("lines", nargs="?", default="LINES.tsv", help="LINES.tsv path")
    parser.add_argument("--dir", default=".", help="Subdirectory containing LINES.tsv")
    parser.add_argument("--speaker", default="Aman", help="Parler speaker")
    parser.add_argument("--style", default="natural", help="Parler speaking style")
    parser.add_argument("--seed", type=int, default=11, help="RNG seed")
    parser.add_argument("--check-credentials", action="store_true", help="Check credentials and exit")
    parser.add_argument("--interactive", action="store_true", help="Prompt for credentials interactively if missing")

    args = parser.parse_args()

    if args.interactive:
        u, k = get_kaggle_credentials(prompt_if_missing=True)
        if u and k:
            print(f"✅ Kaggle credentials configured for user: {u}")
            sys.exit(0)
        else:
            sys.exit(1)

    if args.check_credentials:
        u, k = get_kaggle_credentials(prompt_if_missing=False)
        if u and k:
            print(f"✅ Kaggle credentials verified for user: {u}")
            sys.exit(0)
        else:
            print("❌ Kaggle credentials missing or unconfigured.")
            sys.exit(1)

    success = run_parler_kaggle_job(
        sub_dir=args.dir,
        lines_tsv=args.lines,
        speaker=args.speaker,
        style=args.style,
        seed=args.seed
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
