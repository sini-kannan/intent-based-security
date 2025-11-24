Project Progress - Current Working Features
1. Intent Validation

Validates all intent files (intent_api.yaml, intent_frontend.yaml, intent_db.yaml).

Checks structure, ports, domains, and formatting.

2. Policy Compilation

Converts intents into Kubernetes-style network policies.

Saves compiled YAMLs in the policies/ folder.

3. Traffic Capture

Captures live container traffic for a given duration.

Also supports simulation mode.

Saves logs under /tmp/runtime_logs_TIMESTAMP/.

4. Drift Detection

Compares expected behavior vs actual behavior.

Detects:

undeclared ports

unexpected hosts (internal/external)

domain mismatches

Saves structured results to drift_log.json.

5. Automatic Port Learning

Extracts dangerous ports from drift results.

Updates port_watch.yaml automatically.

This file becomes the source for blocked ports.

6. Policy Enforcement (iptables)

Rebuilds the DOCKER-USER chain cleanly.

For every container:

allows only declared ports

blocks all dangerous ports

drops everything else

Ensures consistent rule application.

7. Full Automation Pipeline

Run the entire system end-to-end using:

./intentflow full --duration 20


The pipeline performs:

build → cleanup → start → validate → compile → capture → drift detect → learn → update port_watch.yaml → enforce → test

How to Test the System
1. Make the script executable
chmod +x intentflow

2. Run full pipeline
./intentflow full --duration 20

3. Optional manual checks
Check drift results:
cat drift_log.json

Check learned dangerous ports:
cat port_watch.yaml

Inspect firewall rules:
sudo iptables -L DOCKER-USER -n --line-numbers

Run Individual Components
Validate intents
./intentflow validate

Compile policies
./intentflow compile

Capture traffic
./intentflow capture --duration 20

Detect drift
./intentflow drift --logs <path>

Enforce rules
./intentflow enforce

Test flows
./intentflow test

Summary

System now supports:

intent validation

policy generation

runtime capture

drift detection

automatic dangerous-port learning

per-container enforcement

full automated pipeline

Everything works end-to-end.

Next step: build the web dashboard.
