import os, subprocess, re, json, sys, tempfile
from datetime import datetime

def get_latest_log_dir():
    # Check for existing logs
    tmp_dir = tempfile.gettempdir()
    if os.path.exists(tmp_dir):
        dirs = [d for d in os.listdir(tmp_dir) if d.startswith("runtime_logs_")]
        if dirs:
            dirs.sort(key=lambda x: os.path.getmtime(os.path.join(tmp_dir, x)), reverse=True)
            # If latest log is recent (< 1 min), use it. Otherwise capture new.
            latest = os.path.join(tmp_dir, dirs[0])
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
        # Handle both Windows and Linux paths
        match = re.search(r"Logs stored in:\s*([^\s]+runtime_logs[^\s]+)", result.stdout)
        if match:
            return match.group(1).strip()
        match = re.search(r"Logs directory:\s*([^\s]+runtime_logs[^\s]+)", result.stdout)
        if match:
            return match.group(1).strip()
            
        print("Capture failed or no logs output found.")
        print(result.stdout)
        return None
    except Exception as e:
        print(f"Capture failed: {e}")
        return None

def run_drift_detection(log_dir):
    cmd = [sys.executable, "detect_drift_auto.py", "--logs", log_dir, "--intents", "."]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    return os.path.exists("drift_log.json")

def run_reconciliation():
    # Remove sudo for Windows compatibility, check for Linux for sudo if needed
    cmd = [sys.executable, "policy_reconciler.py"]
    if sys.platform != "win32":
        cmd = ["sudo"] + cmd
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
