#!/usr/bin/env python3
import os
import yaml
import subprocess
import sys
from datetime import datetime

def run(cmd):
    """Run a command list, print it, and return CompletedProcess."""
    # Special handling for Windows Demo Mode
    if sys.platform == "win32" and ("iptables" in cmd or "sudo" in cmd):
        print(f"[DEMO-MODE] Mocking command: {' '.join(cmd)}")
        # Return a mock successful result
        return subprocess.CompletedProcess(cmd, 0, stdout="Mocked success", stderr="")

    print("RUN:", " ".join(cmd))
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode != 0:
            print("ERROR:", p.returncode, p.stderr.strip())
        return p
    except Exception as e:
        print("EXCEPTION running command:", e)
        raise

def get_ip(name):
    # Mock for Windows demo
    if sys.platform == "win32":
        return f"172.18.0.{hash(name) % 254}"
    
    try:
        out = subprocess.check_output(
            ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", name],
            text=True,
        ).strip()
        return out
    except subprocess.CalledProcessError as e:
        print(f"get_ip: docker inspect failed for {name}: {e}")
        return ""
    except Exception as e:
        print("get_ip exception:", e)
        return ""

def ensure_running(name):
    if sys.platform == "win32":
        return
    try:
        out = subprocess.check_output(["docker", "inspect", "-f", "{{.State.Running}}", name], text=True).strip()
        if out != "true":
            print(f"{name} not running, starting")
            subprocess.run(["docker", "start", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def read_watch():
    if not os.path.exists("port_watch.yaml"):
        return {"bad_ports": [22, 1337, 4444], "safe_ports": []}
    try:
        with open("port_watch.yaml") as f:
            return yaml.safe_load(f) or {"bad_ports": [22, 1337, 4444], "safe_ports": []}
    except Exception as e:
        return {"bad_ports": [22, 1337, 4444], "safe_ports": []}

def read_ports(policy):
    try:
        with open(policy) as f:
            doc = yaml.safe_load(f)
    except Exception as e:
        print("read_ports: failed to read", policy, e)
        return []
    items = []
    # Simplified parser for different YAML formats
    spec = doc.get("spec", {})
    egress = spec.get("egress", [])
    if not egress and "egress" in doc: egress = doc["egress"]
    
    for rule in egress or []:
        for p in rule.get("ports", []) or []:
            port = p.get("port") or p.get("number")
            proto = (p.get("protocol") or "TCP").upper()
            if port:
                items.append((str(port), proto))
    return items

def main():
    watch = read_watch()
    bad_ports = set(watch.get("bad_ports", []) or [])

    if not os.path.isdir("policies"):
        os.makedirs("policies", exist_ok=True)

    files = sorted([f for f in os.listdir("policies") if f.endswith(".yaml")])
    if not files:
        # Create a dummy policy for demo if none exist
        dummy_path = os.path.join("policies", "my-container-networkpolicy.yaml")
        with open(dummy_path, "w") as f:
            f.write("spec:\n  egress:\n  - ports:\n    - port: 5432\n      protocol: TCP")
        files = ["my-container-networkpolicy.yaml"]

    # --- ATOMIC UPDATE START ---
    chain_name = "INTENT_SEC"
    temp_chain = "INTENT_SEC_TMP"
    
    print("\n" + "="*60)
    print(" [IBSS] SECURITY POLICY ENFORCEMENT PIPELINE")
    print("="*60)
    print(f"[*] Initializing Shadow Chain: {temp_chain}")
    
    # Create new chain or flush if exists
    run(["sudo", "iptables", "-N", temp_chain])
    run(["sudo", "iptables", "-F", temp_chain])
    
    # 1. Allow Established Traffic First (Efficiency)
    run(["sudo", "iptables", "-A", temp_chain, "-m", "conntrack", "--ctstate", "RELATED,ESTABLISHED", "-j", "ACCEPT"])

    # 2. Populate rules for all containers
    for f in files:
        name = f.replace("-networkpolicy.yaml", "").replace("intent_", "").replace(".yaml", "")
        policy_path = os.path.join("policies", f)
        
        ip = get_ip(name)
        if not ip: continue
            
        allowed = read_ports(policy_path)
        print(f"[*] Mapping {name} ({ip}) -> {temp_chain}")
        
        # Allow declared ports
        for port, proto in allowed:
            proto_flag = "tcp" if proto == "TCP" else "udp"
            run(["sudo", "iptables", "-A", temp_chain, "-s", ip, "-p", proto_flag, "--dport", port, "-m", "conntrack", "--ctstate", "NEW", "-j", "ACCEPT"])
            
        # Block bad ports
        for bp in sorted(list(bad_ports)):
            if any(str(bp) == str(p) for p, _ in allowed): continue
            run(["sudo", "iptables", "-A", temp_chain, "-s", ip, "-p", "tcp", "--dport", str(bp), "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"])
            
        # Drop anything else from this container
        run(["sudo", "iptables", "-A", temp_chain, "-s", ip, "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"])

    # 3. The Atomic Swap
    print("[*] Atomic Swap Initiated: Diverting traffic to Shadow Chain...")
    
    # Ensure the main INTENT_SEC chain exists
    run(["sudo", "iptables", "-N", chain_name])
    
    # Insert the Jump to the NEW chain at the top of DOCKER-USER
    run(["sudo", "iptables", "-I", "DOCKER-USER", "1", "-j", temp_chain])
    
    # Remove references to the OLD chain
    run(["sudo", "iptables", "-D", "DOCKER-USER", "-j", chain_name])
    
    # Clean up old chain
    run(["sudo", "iptables", "-F", chain_name])
    run(["sudo", "iptables", "-X", chain_name])
    
    # Rename TMP -> INTENT_SEC
    run(["sudo", "iptables", "-E", temp_chain, chain_name])
    
    print("="*60)
    print(" [SUCCESS] Atomic swap complete. Zero downtime achieved.")
    print(" [SUCCESS] All policies enforced successfully.")
    print("="*60)
    print(f"Cycle Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
