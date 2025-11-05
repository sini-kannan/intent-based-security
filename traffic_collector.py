#!/usr/bin/env python3
"""
traffic_collector.py

Automated runtime traffic collector for Docker containers.

Features:
- Discovers running containers and their IPs (safe JSON inspect).
- Starts tcpdump for each container IP and writes logs to a timestamped directory.
- Optional built-in traffic simulation to generate internal and external traffic.
- Time-limited capture with clean shutdown and log summary.

Usage:
    sudo python3 traffic_collector.py --network micro-net --duration 30 --simulate
"""

from __future__ import annotations
import subprocess
import time
import os
import argparse
import json
import signal
from datetime import datetime
from typing import Dict, List
import shutil
import sys

def running_as_root() -> bool:
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows fallback (not relevant here)
        return False

# Helper to prefix commands with sudo if not running as root
def maybe_prefix_sudo(cmd: List[str]) -> List[str]:
    if running_as_root():
        return cmd
    return ["sudo"] + cmd

def get_container_ips(network: str | None = None) -> Dict[str, str]:
    """
    Return dict of {container_name: ip_address} for running containers.
    If `network` is provided, prefer that network's IP.
    """
    try:
        out = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"], text=True)
    except subprocess.CalledProcessError:
        return {}

    container_names = [line.strip() for line in out.splitlines() if line.strip()]
    result: Dict[str, str] = {}

    for name in container_names:
        try:
            raw = subprocess.check_output(["docker", "inspect", name], text=True)
            info = json.loads(raw)[0]
            networks = info.get("NetworkSettings", {}).get("Networks", {}) or {}

            ip = ""
            if network:
                netinfo = networks.get(network)
                if netinfo:
                    ip = netinfo.get("IPAddress", "") or ""
            if not ip:
                # fallback: first non-empty IP
                for netname, netinfo in networks.items():
                    ip = netinfo.get("IPAddress", "") or ""
                    if ip:
                        break
            if ip:
                result[name] = ip
        except Exception:
            # ignore containers we cannot inspect
            continue
    return result

def start_tcpdump_process(ip: str, logfile_path: str) -> subprocess.Popen:
    """
    Start tcpdump capturing traffic for `ip` and write to logfile_path.
    Returns the Popen object.
    """
    # Use numeric-only options and full timestamps; no ascii (-A) by default to avoid binary noise.
    cmd = ["tcpdump", "-i", "any", "-nn", "-tttt", "host", ip]
    # If not root, prefix sudo
    cmd = maybe_prefix_sudo(cmd)

    # Open the logfile in binary mode
    logfile_dir = os.path.dirname(logfile_path)
    os.makedirs(logfile_dir, exist_ok=True)
    f = open(logfile_path, "wb")

    # Start the process in new process group so we can terminate the whole group later
    proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
    return proc

def stop_process_group(proc: subprocess.Popen, timeout: float = 5.0) -> None:
    """
    Terminate the process group started by proc (using preexec_fn=os.setpgrp).
    """
    try:
        pgid = os.getpgid(proc.pid)
        # send SIGTERM to process group
        os.killpg(pgid, signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass
    try:
        proc.wait(timeout=timeout)
    except Exception:
        try:
            pgid = os.getpgid(proc.pid)
            os.killpg(pgid, signal.SIGKILL)
        except Exception:
            pass

def summarize_logs(folder: str) -> None:
    print("\nCapture summary:")
    entries = sorted(os.listdir(folder))
    for e in entries:
        path = os.path.join(folder, e)
        try:
            size_kb = os.path.getsize(path) / 1024.0
        except Exception:
            size_kb = 0.0
        print(f"  {e:25s} {size_kb:8.1f} KB")

def simulate_traffic(containers: Dict[str, str], external_test: bool = True) -> None:
    """
    Run a small set of docker exec commands to generate traffic.
    Behavior:
      - If a container name contains 'front' or 'frontend', it will call the API and external sites.
      - If a container name contains 'api', it will attempt to reach the DB port 3306.
      - For other containers, it will perform a ping to a discovered other container (if any).
    """
    print("Simulating container traffic...")
    # Prepare container name lists
    names = list(containers.keys())
    ip_map = containers

    # Helper to run a docker exec command (no tty)
    def run_exec(cmd_list: List[str]) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(cmd_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        except Exception:
            return subprocess.CompletedProcess(args=cmd_list, returncode=1)

    # Find likely frontend, api, db by substring
    frontend = next((n for n in names if "front" in n or "frontend" in n), None)
    api = next((n for n in names if n == "api-service" or "api" in n), None)
    db = next((n for n in names if n == "db-service" or "db" in n), None)

    # Frontend -> API and external
    if frontend and api:
        cmd = ["docker", "exec", frontend, "sh", "-c",
               "apk add --no-cache curl >/dev/null 2>&1 || true; curl -I --max-time 5 http://api-service || true"]
        run_exec(cmd)
        if external_test:
            cmd_google = ["docker", "exec", frontend, "sh", "-c",
                          "apk add --no-cache curl >/dev/null 2>&1 || true; curl -I --max-time 5 https://www.google.com || true"]
            run_exec(cmd_google)

    # API -> DB (attempt to reach port 3306)
    if api and db:
        cmd = ["docker", "exec", api, "sh", "-c",
               "apk add --no-cache curl >/dev/null 2>&1 || true; curl -I --max-time 5 http://db-service:3306 || true"]
        run_exec(cmd)

    # DB -> API ping
    if db and api:
        cmd = ["docker", "exec", db, "sh", "-c", "ping -c 2 api-service || true"]
        run_exec(cmd)

    # For any other containers, make a short DNS lookup to generate DNS traffic
    for name in names:
        if name not in (frontend, api, db):
            cmd = ["docker", "exec", name, "sh", "-c", "apk add --no-cache drill >/dev/null 2>&1 || true; drill example.com >/dev/null 2>&1 || true"]
            run_exec(cmd)

    print("Traffic simulation done.")

def main():
    parser = argparse.ArgumentParser(description="Automated traffic collector for Docker containers.")
    parser.add_argument("--network", help="Docker network name (optional).", default=None)
    parser.add_argument("--duration", type=int, help="Capture duration in seconds.", default=30)
    parser.add_argument("--output", help="Base directory to store logs.", default="/tmp")
    parser.add_argument("--simulate", action="store_true", help="Automatically simulate traffic during capture.")
    args = parser.parse_args()

    if shutil.which("docker") is None:
        print("Error: docker not found in PATH.")
        sys.exit(1)
    if shutil.which("tcpdump") is None:
        print("Error: tcpdump not found in PATH.")
        sys.exit(1)

    containers = get_container_ips(args.network)
    if not containers:
        print("No running containers found.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outdir = os.path.join(args.output, f"runtime_logs_{timestamp}")
    os.makedirs(outdir, exist_ok=True)

    print(f"Discovered containers ({len(containers)}):")
    for name, ip in containers.items():
        print(f"  {name:20s} {ip}")

    print(f"\nStarting tcpdump for {args.duration} seconds...")
    print(f"Logs directory: {outdir}")

    procs: List[subprocess.Popen] = []
    try:
        # start tcpdump per container
        for name, ip in containers.items():
            logfile = os.path.join(outdir, f"{name}.log")
            proc = start_tcpdump_process(ip, logfile)
            procs.append(proc)

        # give tcpdump a second to settle
        time.sleep(2)

        # optionally simulate traffic (this will run docker exec commands)
        if args.simulate:
            # run simulation in background not to block forever
            simulate_traffic(containers, external_test=True)

        # continue capturing for the requested duration (simulation already ran)
        time.sleep(max(0, args.duration - 2))

    finally:
        # stop all started tcpdump processes
        for p in procs:
            try:
                stop_process_group(p, timeout=3.0)
            except Exception:
                pass

    summarize_logs(outdir)
    print(f"\nAll captures stopped. Logs stored in: {outdir}\n")

if __name__ == "__main__":
    main()
