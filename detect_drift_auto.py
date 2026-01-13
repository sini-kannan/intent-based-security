import subprocess, json, re, sys, os
from datetime import datetime
import yaml

def load_watch():
    if os.path.exists("port_watch.yaml"):
        with open("port_watch.yaml") as f:
            return yaml.safe_load(f)
    return {"bad_ports": [], "safe_ports": []}

watch = load_watch()
auto_bad = set(watch.get("bad_ports", []))

cmd = [sys.executable, "detect_drift_batch_pretty.py"] + sys.argv[1:]
result = subprocess.run(cmd, capture_output=True, text=True)
out = result.stdout
print(out)

blocks = out.split("Drift Report for ")
drifts = []

for block in blocks[1:]:
    lines = block.strip().splitlines()
    name = lines[0].strip()
    ports = []

    for l in lines:
        if "Undeclared ports:" in l:
            nums = re.findall(r"\d+", l)
            ports = [int(x) for x in nums]

    learned = []
    for p in ports:
        if p in watch.get("bad_ports", []):
            learned.append(p)
        elif p == 3306 or p == 5432 or p == 1433:
            learned.append(p)
        elif p < 1024 and p not in watch.get("safe_ports", []):
            learned.append(p)

    if learned:
        auto_bad.update(learned)
        drifts.append({"container": name, "bad_ports": learned, "time": datetime.now().isoformat()})

# save updated bad port list
with open("port_watch.yaml", "w") as f:
    yaml.dump({"bad_ports": sorted(list(auto_bad)), "safe_ports": watch.get("safe_ports", [])}, f)

if drifts:
    with open("drift_log.json", "w") as f:
        json.dump(drifts, f, indent=2)
    print("saved drift_log.json")
else:
    print("no bad ports found")
