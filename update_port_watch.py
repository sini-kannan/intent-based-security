#!/usr/bin/env python3
import yaml, json, os

def load_watch():
    if not os.path.exists("port_watch.yaml"):
        return {"bad_ports": [], "safe_ports": []}
    with open("port_watch.yaml") as f:
        return yaml.safe_load(f) or {"bad_ports": [], "safe_ports": []}

def load_drift():
    if not os.path.exists("drift_log.json"):
        return []
    with open("drift_log.json") as f:
        return json.load(f)

def collect_new_bad_ports(drift_list):
    out = set()
    for entry in drift_list:
        ports = entry.get("undeclared_ports", [])
        for p in ports:
            try:
                p = int(p)
            except:
                continue
            out.add(p)
    return out

def save_watch(cfg):
    with open("port_watch.yaml", "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

def main():
    watch = load_watch()
    drift_list = load_drift()

    current = set(watch.get("bad_ports", []))
    new_ports = collect_new_bad_ports(drift_list)

    merged = sorted(current.union(new_ports))

    watch["bad_ports"] = merged
    save_watch(watch)

    print("Updated port_watch.yaml with ports:", merged)

if __name__ == "__main__":
    main()
