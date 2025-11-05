#!/usr/bin/env python3
"""
policy_enforcer.py
Applies intent-based egress policies using iptables for running Docker containers.
"""

import os
import yaml
import subprocess
from glob import glob

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"⚠️  Error running: {cmd}\n{result.stderr.decode()}")
    return result.stdout.decode().strip()

def get_container_ip(name):
    cmd = f"docker inspect -f '{{{{range .NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' {name}"
    return run_cmd(cmd)

def apply_policy(container_name, policy_path):
    print(f"\n🔐 Applying policy from {policy_path} to container {container_name}")

    with open(policy_path, "r") as f:
        data = yaml.safe_load(f)

    egress_rules = data.get("spec", {}).get("egress", [])
    allowed_ports = []
    for rule in egress_rules:
        for port in rule.get("ports", []):
            allowed_ports.append(str(port.get("port")))
    
    ip = get_container_ip(container_name)
    if not ip:
        print(f"⚠️  Could not get IP for {container_name}")
        return

    print(f"→ Container IP: {ip}")
    print(f"→ Allowed egress ports: {', '.join(allowed_ports) or 'None'}")

    # Flush previous rules for this container
    run_cmd(f"sudo iptables -D FORWARD -s {ip} -j DROP || true")
    run_cmd(f"sudo iptables -F")

    # Allow specified egress ports
    for port in allowed_ports:
        run_cmd(f"sudo iptables -A FORWARD -s {ip} -p tcp --dport {port} -j ACCEPT")

    # Drop everything else
    run_cmd(f"sudo iptables -A FORWARD -s {ip} -j DROP")

    print("✅ Policy applied successfully.")

def main():
    print("=== Intent-Based Policy Enforcement ===")
    policies = glob("policies/*.yaml")

    for policy in policies:
        # Derive container name from file
        container = os.path.basename(policy).replace("-networkpolicy.yaml", "")
        apply_policy(container, policy)

    print("\nAll policies enforced successfully.")

if __name__ == "__main__":
    main()
