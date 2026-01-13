# 3. Project Description

## 3.1 Subject Matter
The core subject of this project is the development of an autonomous security control plane for containerized environments. The system acts as a "Security Middleware" that sits between the user (developer/admin) and the underlying operating system kernel firewall (Netfilter/iptables).

## 3.2 Technical Approach and Methodology
The project follows a modular, layer-based architecture designed for extensibility and reliability. The methodology is centered around "The Three Pillars of Intent-Based Security":

### 3.2.1 Pillar 1: Semantic Translation (The Parser)
The translation layer is responsible for converting unstructured or semi-structured high-level intents into a machine-executable security specification.
- **Hybrid Engine**: We implemented a "Driver" pattern. The system first attempts to parse input using a high-performance **Deterministic Regex Engine**. This handles 99% of common scenarios (database access, web traffic, common ports like SSH, DNS, SMTP).
- **LLM Integration**: For complex or ambiguous intents, the system includes an interface to a **Local LLM (Ollama/Llama3)**. This allows the system to "reason" about the requirements and handle various linguistic styles without manual regex updates.

### 3.2.2 Pillar 2: Atomic Enforcement (The Enforcer)
A critical challenge in network security is "Update Jitter"—the brief period during which firewall rules are being updated where connections might be dropped.
- **Methodology**: We utilize a **Shadow Chain Strategy**.
    1.  A temporary chain (`INTENT_EXT_TMP`) is created in the kernel.
    2.  The new ruleset is fully populated in this temporary chain.
    3.  A single, atomic `iptables` command is issued to swap the live pointer with the new chain.
- **Outcome**: This ensures that security updates do not cause downtime or partial rule states, maintaining "Consistency" in the security posture.

### 3.2.3 Pillar 3: Continuous Drift Detection (The Drifter)
Static enforcement is insufficient in dynamic environments. Our approach includes a continuous "Feedback Loop."
- **Methodology**: The Drifter component periodically scans the Docker runtime API and compares the running container list against the "Inventory of Registered Intents."
- **Detection Logic**: If a container is found running without a corresponding policy file, it is flagged as a "Drift Event."
- **Reconciliation**: Depending on the configuration, the system can automatically block the rogue container's traffic or alert the administrator.

## 3.3 Expected Outcomes
Upon full implementation, the IBSS is expected to provide:
- **90% Reduction in Configuration Time**: Developers can describe needs in seconds rather than hours of debugging firewall rules.
- **Enhanced Security Posture**: A "Default Deny" posture that is automatically maintained.
- **Quantifiable Compliance**: Instant generation of audit reports showing NIST CSF 2.0 alignment for every container in the system.
- **Visual Visibility**: A real-time dashboard showing the mapping of "Intent" to "Reality."
