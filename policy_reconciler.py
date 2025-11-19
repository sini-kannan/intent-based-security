import json
import subprocess
from datetime import datetime
import os

def load_drifts():
    if not os.path.exists("drift_log.json"):
        return []
    with open("drift_log.json") as f:
        return json.load(f)

def reconcile():
    drifts = load_drifts()
    if not drifts:
        print("no drifts found")
        return
    fixed = []
    for d in drifts:
        name = d.get("container")
        if not name:
            continue
        subprocess.run(["sudo", "python3", "policy_enforcer.py"], stdout=subprocess.DEVNULL)
        fixed.append({"container": name, "time": datetime.now().isoformat(), "status": "re-enforced"})
    if fixed:
        with open("reconciliation_log.json", "a") as f:
            json.dump(fixed, f, indent=2)
        print("reconciliation done for", [x["container"] for x in fixed])
    else:
        print("no valid drift entries")

if __name__ == "__main__":
    reconcile()
