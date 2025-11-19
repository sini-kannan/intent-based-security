import os, subprocess, re, json
from datetime import datetime

def get_latest_log_dir():
    dirs = [d for d in os.listdir("/tmp") if d.startswith("runtime_logs_")]
    if not dirs:
        print("no runtime logs found")
        return None
    dirs.sort(key=lambda x: os.path.getmtime(os.path.join("/tmp", x)), reverse=True)
    return os.path.join("/tmp", dirs[0])

def run_drift_detection(log_dir):
    cmd = ["python3", "detect_drift_auto.py", "--logs", log_dir, "--intents", "."]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    return os.path.exists("drift_log.json")

def run_reconciliation():
    cmd = ["sudo", "python3", "policy_reconciler.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

def main():
    log_dir = get_latest_log_dir()
    if not log_dir:
        return
    print("using latest log folder:", log_dir)
    if run_drift_detection(log_dir):
        run_reconciliation()
    else:
        print("no drift_log.json created, nothing to reconcile")
    if os.path.exists("reconciliation_log.json"):
        with open("reconciliation_log.json") as f:
            data = f.read()
        print("\n=== reconciliation log ===")
        print(data)

if __name__ == "__main__":
    main()
