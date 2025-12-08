import os, subprocess, re, json
from datetime import datetime

import sys

def get_latest_log_dir():
    # Check for existing logs
    if os.path.exists("/tmp"):
        dirs = [d for d in os.listdir("/tmp") if d.startswith("runtime_logs_")]
        if dirs:
            dirs.sort(key=lambda x: os.path.getmtime(os.path.join("/tmp", x)), reverse=True)
            # If latest log is recent (< 1 min), use it. Otherwise capture new.
            latest = os.path.join("/tmp", dirs[0])
            if (datetime.now().timestamp() - os.path.getmtime(latest)) < 60:
                print(f"Using recent logs: {latest}")
                return latest

    # No recent logs, trigger capture
    print("No recent runtime logs found. Triggering 10s capture...")
    cmd = [sys.executable, "traffic_collector.py", "--network", "micro-net", "--duration", "10"]
    try:
        # traffic_collector might need sudo in some envs, but we try as is
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Extract log path from output
        match = re.search(r"Logs stored in:\s*(/tmp/runtime_logs[^\s]+)", result.stdout)
        if match:
            return match.group(1)
        match = re.search(r"Logs directory:\s*(/tmp/runtime_logs[^\s]+)", result.stdout)
        if match:
            return match.group(1)
            
        print("Capture failed or no logs output found.")
        print(result.stdout)
        return None
    except Exception as e:
        print(f"Capture failed: {e}")
        return None

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
