#!/usr/bin/env python3
"""
detect_drift_batch_pretty.py
Multi-container drift detector with professional formatted output.
Automatically matches intent_*.yaml files to tcpdump logs.
"""

import os
import re
import yaml
import socket
import argparse
from collections import defaultdict
from datetime import datetime

# ───────────────────────────────────────────────
# Color codes for readable terminal output
# ───────────────────────────────────────────────
class Color:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# ───────────────────────────────────────────────
# Utility Functions
# ───────────────────────────────────────────────
def load_intent(path):
    """Load ports/domains from YAML intent file."""
    with open(path, "r") as f:
        doc = yaml.safe_load(f)

    meta = doc.get("metadata", {})
    spec = doc.get("spec", {})

    name = meta.get("name", "unknown")
    allowed_ports = {int(p.get("port") or p.get("number", 0))
                     for e in spec.get("egress", [])
                     for p in (e.get("ports") or []) if p.get("port") or p.get("number")}
    allowed_domains = {d for e in spec.get("egress", [])
                       for d in (e.get("domains") or [])}
    return name, allowed_ports, allowed_domains


def reverse_lookup(ip):
    """Try reverse DNS lookup."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None


def parse_log(path):
    """Extract ports and IPs from tcpdump log."""
    port_re = re.compile(r'\.(\d{1,5})\b')
    ip_re = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    ports, ips = defaultdict(int), defaultdict(int)

    with open(path, "r", errors="ignore") as f:
        for line in f:
            for p in port_re.findall(line):
                ports[int(p)] += 1
            for ip in ip_re.findall(line):
                ips[ip] += 1
    return ports, ips


def summarize_ports(ports, allowed_ports):
    observed = sorted(ports.keys())
    undeclared = [p for p in observed if p not in allowed_ports]
    return observed, undeclared


def clean_print(text):
    print(f"{Color.CYAN}{Color.BOLD}{text}{Color.RESET}")


# ───────────────────────────────────────────────
# Drift Analyzer for one container
# ───────────────────────────────────────────────
def analyze_container(intent_path, log_path):
    name, allowed_ports, allowed_domains = load_intent(intent_path)
    ports, ips = parse_log(log_path)
    observed, undeclared_ports = summarize_ports(ports, allowed_ports)

    print(f"\n{Color.CYAN}{Color.BOLD}───────────────────────────────")
    print(f" Drift Report for {name}")
    print(f"───────────────────────────────{Color.RESET}")
    print(f"{Color.BOLD}Intent file:{Color.RESET} {intent_path}")
    print(f"{Color.BOLD}Log file:{Color.RESET}    {log_path}\n")

    print(f"{Color.BOLD}Allowed ports:{Color.RESET} {sorted(allowed_ports) or '[]'}")
    print(f"{Color.BOLD}Declared domains:{Color.RESET} {sorted(allowed_domains) or '[]'}")
    print(f"{Color.BOLD}Observed ports:{Color.RESET} {observed[:15]}")
    if undeclared_ports:
        print(f"{Color.BOLD}Undeclared ports:{Color.RESET} {Color.RED}{undeclared_ports[:10]}{Color.RESET}")
    else:
        print(f"{Color.GREEN}No undeclared ports found.{Color.RESET}")

    # Reverse lookup IPs
    internal_ips, external_ips, undeclared_hosts = [], [], []
    for ip in list(ips.keys())[:20]:
        if ip.startswith("172."):
            internal_ips.append(ip)
        else:
            external_ips.append(ip)
        r = reverse_lookup(ip)
        if not r:
            undeclared_hosts.append((ip, None))
        else:
            if not any(d in r for d in allowed_domains):
                undeclared_hosts.append((ip, r))

    print(f"\n{Color.BOLD}Internal IPs:{Color.RESET} {internal_ips[:10]}")
    print(f"{Color.BOLD}External IPs:{Color.RESET} {external_ips[:10]}")

    if undeclared_hosts:
        print(f"\n{Color.BOLD}{Color.YELLOW}Undeclared Hosts (Top 5):{Color.RESET}")
        for ip, r in undeclared_hosts[:5]:
            print(f"  - {ip} → {r or 'no reverse lookup'}")
    else:
        print(f"\n{Color.GREEN}No undeclared hosts found.{Color.RESET}")

    print(f"\n{Color.CYAN}───────────────────────────────")
    print(" Drift Analysis Complete")
    print(f"───────────────────────────────{Color.RESET}\n")


# ───────────────────────────────────────────────
# Batch Driver
# ───────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Batch Drift Detector")
    parser.add_argument("--logs", required=True, help="Directory containing logs")
    parser.add_argument("--intents", default="intent_*.yaml", help="Intent file pattern (glob style)")
    args = parser.parse_args()

    if not os.path.isdir(args.logs):
        print(f"{Color.RED}Error: log directory not found:{Color.RESET} {args.logs}")
        return

    intent_files = [f for f in os.listdir('.') if f.startswith('intent_') and f.endswith('.yaml')]
    log_files = [f for f in os.listdir(args.logs) if f.endswith('.log')]

    if not intent_files or not log_files:
        print(f"{Color.RED}No intent or log files found.{Color.RESET}")
        return

    print(f"{Color.BOLD}Intents detected:{Color.RESET} {len(intent_files)}")
    print(f"{Color.BOLD}Logs detected:{Color.RESET}    {len(log_files)}\n")

    # 1. Analyze Known Containers
    for intent in intent_files:
        container_name = intent.replace("intent_", "").replace(".yaml", "")
        matched_logs = [l for l in log_files if container_name in l]
        if not matched_logs:
            continue

        log_path = os.path.join(args.logs, matched_logs[0])
        analyze_container(intent, log_path)

    # 2. Flag Unrecognized Containers
    known_names = [i.replace("intent_", "").replace(".yaml", "") for i in intent_files]
    for log in log_files:
        is_known = any(name in log for name in known_names)
        
        if not is_known:
             print(f"\n{Color.BOLD}{Color.RED}[!] UNMANAGED CONTAINER: {log}{Color.RESET}")
             print(f"    Traffic detected without corresponding intent policy.")
             print(f"  Action: Recommended to QUARANTINE.")
             # Create a dummy "drift" entry for frontend
             drift_entry = {
                 "container": log, 
                 "undeclared_ports": ["ALL (Unauthorized Container)"], 
                 "undeclared_hosts": []
             }
             # Append to existing json if exists (not implemented effectively here as overwrite, but print is enough for console)



# ───────────────────────────────────────────────
if __name__ == "__main__":
    main()
