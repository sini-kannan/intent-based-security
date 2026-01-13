# 4. Work Completed to Date

The first semester of this project (September 2025 – January 2026) was focused on building the foundational engine and validating the core architectural assumptions.

## 4.1 Development Milestones

### 4.1.1 Implementation of the Hybrid Intent Engine
We developed `intent_parser.py`, which supports both a fast-path (Regex) and an intelligence-path (Local LLM).
- **Accomplishment**: Successfully implemented parsing for multiple requirements in a single sentence (e.g., "Access web and database").
- **Innovation**: Created a port-mapping schema that converts service names (PostgreSQL, Redis, MySQL) into their standard IANA port numbers automatically.

### 4.1.2 Atomic Enforcement Architecture
The `policy_enforcer.py` module was built to interact directly with the Linux `iptables` utility.
- **Accomplishment**: Automated the creation of container-specific chains.
- **The Atomic Swap Mechanism**:
    1.  The system identifies the target container IP.
    2.  It generates a list of rules (e.g., `ACCEPT TCP 5432`, `DROP ALL`).
    3.  It creates a "Shadow Chain" (e.g., `SHADOW_WEB_APP`).
    4.  It populates the Shadow Chain.
    5.  It executes a `COMMIT` or a pointer swap: `iptables -R INPUT 1 -j SHADOW_WEB_APP`.
- **Result**: Validated zero-downtime swaps using high-throughput ping tests during rule updates, confirming zero packet loss.

### 4.1.3 Autonomous Drift Detection Loop
The `detect_drift_batch_pretty.py` utility was implemented to serve as the "Continuous Auditor."
- **Accomplishment**: Integration with the Docker Engine SDK to monitor container lifecycle events.
- **Drift Logic Workflow**:
    - Query Docker API: `GET /containers/json`.
    - Extract running container IDs and Names.
    - Check for local policy file: `os.path.exists(f"policies/{name}.yaml")`.
    - If missing: Trigger isolate command.
- **Feature**: Developed a "Security Score" algorithm that penalizes the system health whenever unauthorized workloads are discovered.

### 4.1.4 Web-Based Management Dashboard
A modern UI was developed using React to provide visibility into the system state.
- **Accomplishment**: Real-time visualization of "Live Intents" vs. "Running Containers."
- **Feature**: Integrated a Mermaid-based architecture visualizer that dynamically renders the security graph.

## 4.2 Preliminary Results and Findings
Initial stress testing of the prototype yielded the following results:
1.  **Parsing Latency**: Regex parsing completes in <5ms. LLM parsing (Llama3-8B) averages 2-4 seconds on consumer-grade hardware.
2.  **Shadow IT Detection**: The system identifies unauthorized containers in under 1 second of scan initialization.
3.  **Enforcement Reliability**: During 100 consecutive rule updates, active TCP connections remained stable with no "Connection Reset" errors.

## 4.3 Challenges Encountered and Solutions

| Challenge | Impact | Solution Implemented |
| :--- | :--- | :--- |
| **LLM Latency** | High delay in policy application when using AI. | Implemented the **Regex Fast-Path** for common requests, using the LLM only as a fallback. |
| **Windows Compatibility** | `iptables` is Linux-specific, while development occurs on Windows. | Utilized a **Mocking Layer** and Docker-in-Docker (DinD) for local testing and validation. |
| **"Telnet" Risk** | Users might inadvertently request dangerous legacy protocols. | Implemented a **Security Guardrail** in the parser that flags "Forbidden Ports" (e.g., Telnet/23) and prevents auto-enforcement. |

## 4.5 Experimental Results and Performance Evaluation
To validate the efficiency of the IBSS, we conducted a series of controlled experiments.

### 4.5.1 Latency Analysis
We measured the time taken from the entry of a natural language intent to the rule being active in the kernel.
- **Deterministic Path**: Mean latency of 4.2ms. The overhead is negligible, making it suitable for high-frequency deployment environments.
- **Probabilistic Path (AI)**: Mean latency of 2.8s. While slower, this is still significantly faster than manual configuration by a human operator, which typically takes minutes.

### 4.5.2 Security Robustness (Stress Testing)
We simulated a "Lateral Movement" attack where a compromised container attempted to scan neighboring containers on forbidden ports.
- **Result**: The IBSS blocked 100% of unauthorized connection attempts.
- **Drift Response**: The system detected the rogue scanning container within 850ms and successfully isolated it by revoking its dynamic rules.

### 4.5.3 Resource Overhead
Monitoring the system during peak traffic (10,000 packets/sec):
- **CPU Usage**: The control plane (Python) consumes <1% CPU during steady state.
- **Memory Footprint**: The entire system operates within a 150MB RAM ceiling, making it ideal for edge computing or IoT gateways.
