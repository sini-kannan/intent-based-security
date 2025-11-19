#!/usr/bin/env python3
import os, yaml, subprocess
from datetime import datetime

def run(cmd):
    return subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_ip(name):
    try:
        out = subprocess.check_output(
            ["docker","inspect","-f","{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",name],
            text=True
        ).strip()
        return out
    except:
        return ""

def ensure_running(name):
    try:
        out = subprocess.check_output(["docker","inspect","-f","{{.State.Running}}",name],text=True).strip()
        if out != "true":
            subprocess.run(["docker","start",name],stdout=subprocess.DEVNULL)
    except:
        pass

def read_watch():
    if not os.path.exists("port_watch.yaml"):
        return {"bad_ports":[], "safe_ports":[]}
    with open("port_watch.yaml") as f:
        return yaml.safe_load(f) or {"bad_ports":[], "safe_ports":[]}

def read_ports(policy):
    with open(policy) as f:
        doc = yaml.safe_load(f)
    items=[]
    for rule in doc.get("spec",{}).get("egress",[]) or []:
        for p in rule.get("ports",[]) or []:
            port=p.get("port") or p.get("number")
            proto=(p.get("protocol") or "TCP").upper()
            if port:
                items.append((str(port),proto))
    return items

def enforce(name, policy, bad_ports):
    ensure_running(name)
    ip=get_ip(name)
    if not ip:
        print(name,"no ip")
        return

    allowed=read_ports(policy)

    # allow declared ports
    for port, proto in allowed:
        proto_flag="tcp" if proto=="TCP" else "udp"
        run(f"sudo iptables -A DOCKER-USER -s {ip} -p {proto_flag} --dport {port} -m conntrack --ctstate NEW -j ACCEPT")

    # block bad ports
    for bp in bad_ports:
        run(f"sudo iptables -A DOCKER-USER -s {ip} -p tcp --dport {bp} -m conntrack --ctstate NEW -j DROP")
        run(f"sudo iptables -A DOCKER-USER -s {ip} -p udp --dport {bp} -m conntrack --ctstate NEW -j DROP")

    # drop any other new traffic
    run(f"sudo iptables -A DOCKER-USER -s {ip} -m conntrack --ctstate NEW -j DROP")

    print(name,"rules applied")

def main():
    watch=read_watch()
    bad_ports=set(watch.get("bad_ports",[]))

    if not os.path.isdir("policies"):
        print("no policies folder")
        return

    files=[f for f in os.listdir("policies") if f.endswith(".yaml")]

    run("sudo iptables -F DOCKER-USER")
    run("sudo iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")

    for f in files:
        name=f.replace("-networkpolicy.yaml","")
        enforce(name, os.path.join("policies",f), bad_ports)

    print("done at",datetime.now())
