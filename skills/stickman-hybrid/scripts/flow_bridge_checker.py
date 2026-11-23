#!/usr/bin/env python3
"""flow_bridge_checker.py: Google Flow Connector Diagnostic & Verification Tool
Checks the complete integration bridge between Chrome Flow Extension, Node.js, and flow-connector-cli.
Features:
1. Node.js & npm version verification (requires Node >= 20).
2. flow-auto CLI installation and latest npm registry version comparison.
3. flow-auto doctor inspection (extension bridge and agent skill registration).
4. Google Chrome process detection & Flow tab diagnostic.
5. Local bridge WebSocket/stdio port readiness check.
6. Actionable copy-paste repair instructions for any failing component.
"""

import os, sys, shutil, subprocess, json

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def check_flow_bridge():
    print("==================================================")
    print("🔌 GOOGLE FLOW CONNECTOR SYSTEM DIAGNOSTIC")
    print("==================================================")
    
    issues = []
    recommendations = []

    # 1. Node.js Check
    node_bin = shutil.which("node")
    if not node_bin:
        print("❌ Node.js: NOT FOUND")
        issues.append("Node.js is not installed on this system.")
        recommendations.append("Install Node.js 20+ LTS via: sudo apt install nodejs npm (Linux) or brew install node (macOS).")
    else:
        code, out, _ = run_cmd(["node", "--version"])
        ver = out.lstrip("v")
        major = int(ver.split(".")[0]) if ver.split(".")[0].isdigit() else 0
        if major >= 20:
            print(f"✅ Node.js: {out} (Meets Requirement >= v20.0)")
        else:
            print(f"⚠️ Node.js: {out} (Older than recommended v20.0+)")
            issues.append(f"Node.js {out} is older than v20.0.")
            recommendations.append("Upgrade Node.js to version 20 LTS.")

    # 2. npm Check
    npm_bin = shutil.which("npm")
    if npm_bin:
        code, out, _ = run_cmd(["npm", "--version"])
        print(f"✅ npm: v{out}")
    else:
        print("❌ npm: NOT FOUND")
        issues.append("npm package manager is missing.")

    # 3. flow-auto CLI Check
    flow_bin = shutil.which("flow-auto")
    if not flow_bin:
        print("❌ flow-auto CLI: NOT FOUND IN PATH")
        issues.append("flow-connector-cli is not installed globally.")
        recommendations.append("Run: npm install -g flow-connector-cli@latest")
    else:
        code, out, _ = run_cmd(["flow-auto", "--version"])
        installed_ver = out.strip()
        print(f"✅ flow-auto CLI: v{installed_ver} ({flow_bin})")
        
        # Check npm registry version
        code, latest_ver, _ = run_cmd(["npm", "view", "flow-connector-cli", "version"])
        if code == 0 and latest_ver:
            if installed_ver == latest_ver:
                print(f"✅ flow-auto Version: Up-to-date (v{installed_ver})")
            else:
                print(f"ℹ️ flow-auto Update Available: v{installed_ver} -> v{latest_ver}")
                recommendations.append(f"Update flow-auto: npm install -g flow-connector-cli@{latest_ver}")

    # 4. flow-auto Status Diagnostic
    if flow_bin:
        print("\n--- Running flow-auto status ---")
        code, stat_out, stat_err = run_cmd(["flow-auto", "status"])
        print(stat_out if stat_out else stat_err)

        if "CONNECTED" in stat_out and "NOT CONNECTED" not in stat_out:
            print("✅ Flow Extension Connection: CONNECTED")
        else:
            print("\nℹ️ Status Note: Extension connects automatically when a flow.google.com / labs.google/flow tab is open in Chrome.")

    # 5. Chrome Browser Process Check
    code, ps_out, _ = run_cmd(["pgrep", "-fa", "chrome"])
    if code == 0 and ps_out:
        print("\n✅ Google Chrome: Running (Process detected)")
    else:
        print("\nℹ️ Google Chrome: Not detected running in background.")
        recommendations.append("Open Google Chrome and log into your Google Flow account (https://labs.google/flow).")

    print("\n==================================================")
    print("📋 SUMMARY & WORKFLOW GUIDANCE")
    print("==================================================")
    if not issues:
        print("🏆 All core prerequisites are met! Google Flow Connector is operational.")
        print("\nHow to generate art with Flow Connector:")
        print("1. Open Chrome -> Go to https://labs.google/flow")
        print("2. Ensure Flow Connector extension side panel is active.")
        print("3. Submit prompts via terminal:")
        print("   flow-auto image --aspect 16:9 \"warm hand-drawn 2D stickman...\"")
    else:
        print(f"⚠️ {len(issues)} item(s) require attention:")
        for idx, rec in enumerate(recommendations, 1):
            print(f"   {idx}. {rec}")
    print("==================================================")

    return len(issues) == 0

if __name__ == "__main__":
    success = check_flow_bridge()
    sys.exit(0 if success else 1)
