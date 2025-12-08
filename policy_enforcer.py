#!/usr/bin/env python3
import os
import yaml
import subprocess
from datetime import datetime

def run(cmd):
    """Run a command list, print it, and return CompletedProcess."""
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
    try:
        out = subprocess.check_output(["docker", "inspect", "-f", "{{.State.Running}}", name], text=True).strip()
        if out != "true":
            print(f"{name} not running, starting")
            subprocess.run(["docker", "start", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def read_watch():
    if not os.path.exists("port_watch.yaml"):
        return {"bad_ports": [], "safe_ports": []}
    try:
        with open("port_watch.yaml") as f:
            return yaml.safe_load(f) or {"bad_ports": [], "safe_ports": []}
    except Exception as e:
        print("read_watch error:", e)
        return {"bad_ports": [], "safe_ports": []}

def read_ports(policy):
    try:
        with open(policy) as f:
            doc = yaml.safe_load(f)
    except Exception as e:
        print("read_ports: failed to read", policy, e)
        return []
    items = []
    for rule in doc.get("spec", {}).get("egress", []) or []:
        for p in rule.get("ports", []) or []:
            port = p.get("port") or p.get("number")
            proto = (p.get("protocol") or "TCP").upper() if isinstance(p.get("protocol", None), str) or p.get("protocol") is None else "TCP"
            if port:
                items.append((str(port), proto))
    return items

def enforce(name, policy, bad_ports):
    print("Enforcing for:", name)
    ensure_running(name)
    ip = get_ip(name)
    print("Resolved IP:", ip)
    if not ip:
        print(name, "no ip found, skipping")
        return

    allowed = read_ports(policy)
    print("Allowed ports for", name, ":", allowed)
    print("Bad ports set:", sorted(list(bad_ports))[:40])

    # add allow rules for declared ports (only NEW)
    for port, proto in allowed:
        proto_flag = "tcp" if proto == "TCP" else "udp"
        cmd = ["sudo", "iptables", "-A", "DOCKER-USER", "-s", ip, "-p", proto_flag, "--dport", port, "-m", "conntrack", "--ctstate", "NEW", "-j", "ACCEPT"]
        run(cmd)

    # block bad ports (both tcp and udp) for NEW connections
    for bp in sorted(list(bad_ports)):
        # skip if bad port is listed as allowed explicitly
        if any(bp == p for p, _ in allowed):
            continue
        cmd_tcp = ["sudo", "iptables", "-A", "DOCKER-USER", "-s", ip, "-p", "tcp", "--dport", str(bp), "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"]
        cmd_udp = ["sudo", "iptables", "-A", "DOCKER-USER", "-s", ip, "-p", "udp", "--dport", str(bp), "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"]
        run(cmd_tcp)
        run(cmd_udp)

    # final catch-all: drop any other NEW outbound connection from this source
    cmd_drop = ["sudo", "iptables", "-A", "DOCKER-USER", "-s", ip, "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"]
    run(cmd_drop)

    print(name, "rules applied")

def main():
    watch = read_watch()
    bad_ports = set(watch.get("bad_ports", []) or [])

    if not os.path.isdir("policies"):
        print("no policies folder found")
        return
#!/usr/bin/env python3
import os
import yaml
import subprocess
from datetime import datetime

def run(cmd):
    """Run a command list, print it, and return CompletedProcess."""
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
    try:
        out = subprocess.check_output(["docker", "inspect", "-f", "{{.State.Running}}", name], text=True).strip()
        if out != "true":
            print(f"{name} not running, starting")
            subprocess.run(["docker", "start", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def read_watch():
    if not os.path.exists("port_watch.yaml"):
        return {"bad_ports": [], "safe_ports": []}
    try:
        with open("port_watch.yaml") as f:
            return yaml.safe_load(f) or {"bad_ports": [], "safe_ports": []}
    except Exception as e:
        print("read_watch error:", e)
        return {"bad_ports": [], "safe_ports": []}

def read_ports(policy):
    try:
        with open(policy) as f:
            doc = yaml.safe_load(f)
    except Exception as e:
        print("read_ports: failed to read", policy, e)
        return []
    items = []
    for rule in doc.get("spec", {}).get("egress", []) or []:
        for p in rule.get("ports", []) or []:
            port = p.get("port") or p.get("number")
            proto = (p.get("protocol") or "TCP").upper() if isinstance(p.get("protocol", None), str) or p.get("protocol") is None else "TCP"
            if port:
                items.append((str(port), proto))
    return items

def enforce(name, policy, bad_ports):
    print("Enforcing for:", name)
    ensure_running(name)
    ip = get_ip(name)
    print("Resolved IP:", ip)
    if not ip:
        print(name, "no ip found, skipping")
        return

    allowed = read_ports(policy)
    print("Allowed ports for", name, ":", allowed)
    print("Bad ports set:", sorted(list(bad_ports))[:40])

    # add allow rules for declared ports (only NEW)
    for port, proto in allowed:
        proto_flag = "tcp" if proto == "TCP" else "udp"
        cmd = ["sudo", "iptables", "-A", "DOCKER-USER", "-s", ip, "-p", proto_flag, "--dport", port, "-m", "conntrack", "--ctstate", "NEW", "-j", "ACCEPT"]
        run(cmd)

    # block bad ports (both tcp and udp) for NEW connections
    for bp in sorted(list(bad_ports)):
        # skip if bad port is listed as allowed explicitly
        if any(bp == p for p, _ in allowed):
            continue
        cmd_tcp = ["sudo", "iptables", "-A", "DOCKER-USER", "-s", ip, "-p", "tcp", "--dport", str(bp), "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"]
        cmd_udp = ["sudo", "iptables", "-A", "DOCKER-USER", "-s", ip, "-p", "udp", "--dport", str(bp), "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"]
        run(cmd_tcp)
        run(cmd_udp)

    # final catch-all: drop any other NEW outbound connection from this source
    cmd_drop = ["sudo", "iptables", "-A", "DOCKER-USER", "-s", ip, "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"]
    run(cmd_drop)

    print(name, "rules applied")

def main():
    watch = read_watch()
    bad_ports = set(watch.get("bad_ports", []) or [])

    if not os.path.isdir("policies"):
        print("no policies folder found")
        return

    files = sorted([f for f in os.listdir("policies") if f.endswith(".yaml")])
    if not files:
        print("no policy files found")
        return

    # --- ATOMIC UPDATE START ---
    chain_name = "INTENT_SEC"
    temp_chain = "INTENT_SEC_TMP"
    
    print(f"Creating temporary chain {temp_chain}")
    # Create new chain or flush if exists
    run(["sudo", "iptables", "-N", temp_chain])
    run(["sudo", "iptables", "-F", temp_chain])
    
    # 1. Allow Established Traffic First (Efficiency)
    run(["sudo", "iptables", "-A", temp_chain, "-m", "conntrack", "--ctstate", "RELATED,ESTABLISHED", "-j", "ACCEPT"])

    # 2. Populate rules for all containers
    for f in files:
        name = f.replace("-networkpolicy.yaml", "")
        policy_path = os.path.join("policies", f)
        
        # We need to inline the enforce logic here to target the temp_chain
        ensure_running(name)
        ip = get_ip(name)
        if not ip: 
            continue
            
        allowed = read_ports(policy_path)
        print(f"Adding rules for {name} ({ip}) to {temp_chain}")
        
        # Allow declared ports
        for port, proto in allowed:
            proto_flag = "tcp" if proto == "TCP" else "udp"
            run(["sudo", "iptables", "-A", temp_chain, "-s", ip, "-p", proto_flag, "--dport", port, "-m", "conntrack", "--ctstate", "NEW", "-j", "ACCEPT"])
            
        # Block bad ports
        for bp in sorted(list(bad_ports)):
            if any(bp == p for p, _ in allowed): continue
            run(["sudo", "iptables", "-A", temp_chain, "-s", ip, "-p", "tcp", "--dport", str(bp), "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"])
            run(["sudo", "iptables", "-A", temp_chain, "-s", ip, "-p", "udp", "--dport", str(bp), "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"])
            
        # Drop anything else from this container
        run(["sudo", "iptables", "-A", temp_chain, "-s", ip, "-m", "conntrack", "--ctstate", "NEW", "-j", "DROP"])

    # 3. The Atomic Swap
    print("Swapping chains atomically...")
    
    # Ensure the main INTENT_SEC chain exists
    run(["sudo", "iptables", "-N", chain_name])
    
    # Insert the Jump to the NEW chain at the top of DOCKER-USER
    # This is the moment the new rules take effect.
    run(["sudo", "iptables", "-I", "DOCKER-USER", "1", "-j", temp_chain])
    
    # Remove references to the OLD chain (INTENT_SEC)
    # We delete the rule jumping to INTENT_SEC. 
    # Since we just inserted at 1, the old rule is likely at 2 (or lower).
    # We can delete by rule specification to be safe.
    run(["sudo", "iptables", "-D", "DOCKER-USER", "-j", chain_name])
    
    # Now DOCKER-USER points to TMP.
    # We want to rename TMP to INTENT_SEC to keep things clean for next time.
    # But we can't rename if INTENT_SEC exists.
    run(["sudo", "iptables", "-F", chain_name])
    run(["sudo", "iptables", "-X", chain_name])
    
    # Rename TMP -> INTENT_SEC
    run(["sudo", "iptables", "-E", temp_chain, chain_name])
    
    # Note: The rule in DOCKER-USER now points to strict UUID or name? 
    # iptables tracks chain renames. So the rule "-j INTENT_SEC_TMP" automatically becomes "-j INTENT_SEC".
    
    print("Atomic update complete. No downtime.")
    print("done at", datetime.now().isoformat())

if __name__ == "__main__":
    main()
