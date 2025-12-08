import time
import subprocess
import datetime
import sys

def run_pipeline():
    print(f"\n[{datetime.datetime.now()}] Starting pipeline check...")
    try:
        # Run auto_reconcile which handles drift detection coverage
        result = subprocess.run(
            [sys.executable, "auto_reconcile.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except Exception as e:
        print(f"Error executing pipeline: {e}")

def main():
    interval = 30  # seconds
    print(f"Starting Continuous Security Monitor (Interval: {interval}s)")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            run_pipeline()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopping monitor.")

if __name__ == "__main__":
    main()
