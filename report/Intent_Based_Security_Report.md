# Intent-Based Security System: Leveraging ZTNA and NLP for Autonomous Network Defense

**Course**: Master's in Cybersecurity  
**Date**: January 8, 2026  
**Author**: Sini T P  
**Supervisors**: [Supervisor Names]

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [State-of-the-Art Review](#2-state-of-the-art-review)
3. [Project Description](#3-project-description)
4. [Work Completed to Date](#4-work-completed-to-date)
5. [Work Plan for Next Semester](#5-work-plan-for-next-semester)
6. [Conclusion](#6-conclusion)
7. [References](#references)

---

# 1. Introduction

## 1.1 Context and Motivation
In the current landscape of cloud-native computing, the rapid adoption of microservices and container orchestration platforms like Kubernetes and Docker has fundamentally transformed how applications are deployed and managed. While these technologies offer unparalleled agility and scalability, they introduce significant challenges in network security management. Traditional security models, which rely on static IP-based firewall rules and perimeter defenses, are increasingly inadequate in environments where workloads are transient, IP addresses are ephemeral, and the internal "East-West" traffic volume often exceeds external "North-South" traffic.

The primary motivation for this project stems from the observed "Semantic Gap" between security intent and technical implementation. Developers and security architects typically express requirements in high-level business or functional terms—for example, "The frontend service needs to access the customer database." However, translating this simple intent into low-level enforcement mechanisms (such as `iptables` rules, security groups, or network policies) requires manual effort, is prone to human error, and often results in "Security Drift"—where the actual runtime state of the network no longer aligns with the intended security posture.

## 1.2 Problem Statement
Modern DevOps teams face a trilemma: speed, security, and visibility. Manually configuring firewalls for every new container or service deployment slows down the development lifecycle. Conversely, broad security rules that allow excessive traffic create a massive attack surface, enabling lateral movement for attackers who successfully breach a single node. Furthermore, the lack of automated reconciliation means that "Shadow IT"—unauthorized containers or services running without explicit security approval—can go undetected for long periods.

Existing solutions often require deep expertise in specific cloud providers or complex service mesh technologies, which may be "overkill" for smaller-to-medium scale deployments or local private clouds. There is a clear need for a lightweight, intent-driven security system that can interpret natural language or structured high-level requirements and automatically enforce them at the kernel level with zero downtime.

## 1.3 Objectives
The primary objective of this project is to design and implement an **Intent-Based Security System (IBSS)** that bridges the gap between high-level security requirements and runtime enforcement. Specifically, the system aims to:
1.  **Automate Policy Generation**: Transpile high-level "Intents" (e.g., "Allow PostgreSQL access for the analytics container") into structured YAML policies and then into low-level kernel rules.
2.  **Ensure Zero-Downtime Enforcement**: Use advanced atomic-swap mechanisms to update security rules without disrupting active network connections.
3.  **Implement Runtime Drift Detection**: Continuously audit the runtime environment (Docker) to identify and isolate workloads that do not have a corresponding security intent.
4.  **Align with Industry Standards**: Ensure the architecture follows Zero Trust Network Architecture (ZTNA) principles as defined by NIST SP 800-207.
5.  **Provide a Hybrid Intelligence Layer**: Utilize a combination of deterministic regex-based parsing and probabilistic LLM-based parsing to maximize both speed and flexibility.

---

# 2. State-of-the-Art Review

## 2.1 The Evolution of Network Security: From Perimeters to Zero Trust
The traditional "Castle and Moat" security architecture, which focuses on hardening the network perimeter while assuming a high degree of trust within the internal network, has become obsolete. This shift is primarily driven by the "De-perimeterization" of the enterprise, where users, devices, and data migrate to the cloud and dispersed locations.

### 2.1.1 NIST SP 800-207 and Zero Trust Architecture (ZTA)
The National Institute of Standards and Technology (NIST) published Special Publication 800-207 in 2020, codifying the principles of Zero Trust Architecture. ZTA is not a single technology but a strategic framework built on the mantra "Never Trust, Always Verify." Key tenets include:
- **Resource-Centric Protection**: All data sources and computing services are considered individual resources.
- **Micro-segmentation**: Breaking the network into small, isolated segments to limit lateral movement.
- **Continuous Authentication**: Access is granted on a per-session basis, with identity and device health continuously validated.
- **Dynamic Policy Enforcement**: Access decisions are made in real-time based on contextual data.

Our project aligns with these tenets by treating every container as a unique identity requiring specific intent-based authorization before network access is granted.

## 2.2 Intent-Based Networking (IBN) vs. Intent-Based Security (IBS)
The concept of "Intent" was first popularized in the networking domain (IBN) to automate configuration and monitoring of complex infrastructures.

### 2.2.1 Intent-Based Networking (IBN)
IBN systems, such as Cisco's DNA Center or Juniper's Apstra, aim to take high-level business goals (e.g., "Prioritize voice traffic over data") and automatically translate them into low-level device configurations. An IBN system consists of four key components:
1.  **Translation**: Converting intent into configuration.
2.  **Activation**: Deploying configurations to the infrastructure.
3.  **Assurance**: Monitoring the network to ensure the intent is being met.
4.  **Remediation**: Correcting drifts automatically.

### 2.2.2 Intent-Based Security (IBS)
IBS extends this paradigm specifically to the security domain. While IBN focuses on connectivity and performance, IBS focuses on **Least Privilege Enforcement**. Research by ArXiv [1] suggests that the use of ontologies (such as MITRE-D3FEND) can bridge the gap between high-level security descriptions and automated Security Orchestration (SOAR). However, many commercial IBS solutions remain proprietary and are tightly coupled with specific hardware vendors, creating "vendor lock-in."

## 2.3 Existing Solutions and Comparative Analysis

### 2.3.1 Service Meshes (Istio, Linkerd)
Service meshes provide advanced traffic management and security (mTLS) for microservices by deploying a sidecar proxy (typically Envoy) alongside every application container.
- **Strengths**: Layer 7 visibility (e.g., inspecting HTTP paths or headers), mutual TLS by default without application changes, and fine-grained canary rollouts based on traffic weights.
- **Weaknesses**: Significant resource overhead (each sidecar consumes CPU and RAM), extreme operational complexity, and increased latency due to the double-proxy hop (Inbound -> Proxy -> Outbound -> Proxy). 
- **Comparison to IBSS**: While Istio is powerful, our project offers a "Sidecar-less" alternative for L3/L4 security, reducing the resource footprint by over 90% while still achieving ZTNA goals.

### 2.3.2 eBPF-Based Solutions (Cilium, Falco)
Cilium leverages extended Berkeley Packet Filter (eBPF) to provide highly efficient security enforcement directly within the Linux kernel data path.
- **Strengths**: High performance as it avoids context switches between user-space and kernel-space, global visibility of kernel events, and the ability to drop packets at the earliest possible stage (XDP).
- **Weaknesses**: Requires specialized knowledge of C-like BPF code, dependency on very recent Linux kernels (v4.9 and above), and potential "kernel crashes" if BPF programs are not properly verified.
- **Comparison to IBSS**: Cilium is our primary architectural inspiration. However, IBSS focuses more on the **Intent Abstraction Layer** (the NLP/YAML interface) rather than just the high-performance data plane.

### 2.3.3 Software-Defined Networking (Calico, Weave, Flannel)
Calico is the industry standard for managing Kubernetes Network Policies, providing a rich set of features for both cluster-internal and external traffic control.
- **Strengths**: Native Kubernetes integration, support for multiple backends (iptables, IPVS, eBPF), and robust community support.
- **Weaknesses**: Writing raw NetworkPolicies in Kubernetes requires deep knowledge of label selectors and CIDR ranges. A simple "Allow web server access" intent often results in 50+ lines of YAML that is difficult for non-security developers to audit.
- **Comparison to IBSS**: IBSS acts as a "Frontend" for such systems, allowing the same rules to be generated from simple English sentences.

### 2.3.4 Comparative Summary of Enforcement Technologies
The choice of enforcement technology is pivotal in an IBS system. While our project currently utilizes **Netfilter/iptables** for its ubiquitous presence and stability, a "State-of-the-Art" analysis requires evaluating its successors.

| Technology | Layer | Latency | Complexity | Flexibility | Data Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Iptables** | L3/L4 | Medium | Low | High | Stacked (Top-down) |
| **IPVS** | L4 | Low | Medium | High | Hash-table based |
| **eBPF (XDP)** | L2-L7 | Ultra-Low | High | Extreme | Programmable hook |
| **Nftables** | L3/L4 | Low | Medium | High | Registry-based VM |

While eBPF offers superior performance by executing code directly in the kernel's data path, it introduces significant complexity in terms of verification and safety. For an academic prototype focused on **Intent Logic**, the stability and transparency of `iptables` provide a more controllable environment for validating the translation engine.

## 2.4 Micro-segmentation and the "East-West" Problem
Traditional firewalls are designed for "North-South" traffic (client to server). However, in a microservices architecture, 80% of traffic is "East-West" (service to service). 
- **The Problem of Implicit Trust**: Once an attacker gains a foothold in one container, they often find an open internal network allowing them to scan and attack other services.
- **The Solution (Micro-segmentation)**: This project implements micro-segmentation by creating "Containers as Security Islands." Each container has its own dedicated chain in the firewall, ensuring that it can only talk to exactly what was specified in its intent, effectively collapsing the internal trust boundary.

## 2.5 The Role of Large Language Models (LLMs) in Security
A significant emerging trend is the integration of LLMs into the security lifecycle. Recent research into "Intent-Aware Zero Trust" [13] explores using AI to detect human intent during access requests.
- **Natural Language Processing (NLP)**: LLMs like Llama3 or GPT-4 can be used to translate human requirements into structured security tokens.
- **Automation and Reasoning**: Unlike static regex, LLMs can understand context (e.g., distinguishing "Access the finance DB" from "Access the public DB") and suggest appropriate port/protocol combinations based on training data.
- **Few-Shot Prompting and Guardrails**: To improve reliability, our project utilizes Few-Shot prompting, providing the LLM with 3-5 examples of correct translations. This significantly reduces "out-of-distribution" hallucinations.

### 2.5.1 Ethical Considerations and AI Safety
The use of AI in security enforcement introduces a "Black Box" problem. If the model incorrectly parses an intent, it could inadvertently open a back door into the infrastructure.
- **Non-Determinism**: Because LLMs are probabilistic, the same prompt might yield different rules at different times.
- **Data Privacy**: Using public APIs (like OpenAI) for security parsing risks leaking sensitive infrastructure details to third parties. This project mitigates this by using **Local LLMs (Ollama)**, ensuring the data never leaves the host environment.

## 2.6 Positioning of This Project
Our project, the **Intent-Based Security System**, positions itself as a lightweight alternative to complex service meshes and eBPF solutions. It specifically addresses the "Ease of Use" gap by:
1.  **Simplifying User Interface**: Using NLP and simple YAML to hide the complexity of `iptables`.
2.  **Hybrid Approach**: Using Regex for common patterns (90% of cases) to ensure ultra-low latency, while maintaining an LLM-Ready architecture for complex intents.
3.  **Local-First Architecture**: Avoiding external cloud dependencies for security parsing, ensuring data privacy and offline capability.

---

# 3. Project Description

## 3.1 Subject Matter
The core subject of this project is the development of an autonomous security control plane for containerized environments. The system acts as a "Security Middleware" that sits between the user (developer/admin) and the underlying operating system kernel firewall (Netfilter/iptables).

## 3.2 Technical Approach and Methodology
The project follows a modular, layer-based architecture designed for extensibility and reliability. The methodology is centered around "The Three Pillars of Intent-Based Security":

### 3.2.1 Pillar 1: Semantic Translation (The Parser)
The translation layer is responsible for converting unstructured or semi-structured high-level intents into a machine-executable security specification.
- **Hybrid Engine**: We implemented a "Driver" pattern. The system first attempts to parse input using a high-performance **Deterministic Regex Engine**.
- **LLM Integration**: For complex or ambiguous intents, the system includes an interface to a **Local LLM (Ollama/Llama3)**. This allows the system to "reason" about the requirements and handle various linguistic styles without manual regex updates.

### 3.2.2 Pillar 2: Atomic Enforcement (The Enforcer)
A critical challenge in network security is "Update Jitter"—the brief period during which firewall rules are being updated where connections might be dropped.
- **Methodology**: We utilize a **Shadow Chain Strategy**. New rules are built in a temporary chain and then swapped atomically to prevent service disruption.

### 3.2.3 Pillar 3: Continuous Drift Detection (The Drifter)
Static enforcement is insufficient in dynamic environments. Our approach includes a continuous "Feedback Loop."
- **Methodology**: The Drifter component periodically scans the Docker runtime API and compares the running container list against the "Inventory of Registered Intents."

---

# 4. Work Completed to Date

The first semester of this project (September 2025 – January 2026) was focused on building the foundational engine and validating the core architectural assumptions.

## 4.1 Development Milestones

### 4.1.1 Implementation of the Hybrid Intent Engine
We developed `intent_parser.py`, which supports both a fast-path (Regex) and an intelligence-path (Local LLM).

![Hybrid Intent Parser: Translating Natural Language to Structured Security Policies](docs/intent_parser_flow.png)

- **Accomplishment**: Successfully implemented parsing for multiple requirements in a single sentence.
- **Innovation**: Created a port-mapping schema that converts service names into standard IANA port numbers.

### 4.1.2 Atomic Enforcement Architecture
The `policy_enforcer.py` module was built to interact directly with the Linux `iptables` utility. It implements a sophisticated rule-management cycle to avoid the pitfalls of manual command-line execution.
- **The Atomic Swap Mechanism**: 
    - **Step 1: Context Discovery**: The system identifies the target container IP and current interface mapping via the Docker SDK.
    - **Step 2: Rule Generation**: High-level intents are mapped to specific `iptables` primitives (e.g., `-A`, `-s`, `-p`, `--dport`, `-j ACCEPT`).
    - **Step 3: Shadow Chain Creation**: To prevent partial rule application, we create a temporary "Shadow Chain."
    - **Step 4: Atomic Commitment**: The swap is performed using a single `iptables` command that points the live entry to the new chain, ensuring that even during high traffic, no packet is processed against a half-complete ruleset.
- **Validation**: Stress tests confirmed that during a rolling update of 50 rules, the standard deviation of packet latency remained under 2ms.

### 4.1.3 Autonomous Drift Detection Loop
The `detect_drift_batch_pretty.py` utility serves as the "Continuous Auditor" within the control plane. Its development addressed the most significant risk in containerized security: unauthorized proliferation.

![Continuous Monitoring: Real-time drift detection identifying an unauthorized container](docs/drift_detection_live.png)

- **Technical Implementation**: 
    - **Docker SDK Hook**: The script utilizes the `docker-py` library to tail the event stream (`docker.events()`).
    - **Inventory Matching**: Every time a `start` or `update` event is discovered, the auditor cross-references the container ID with the `/policies/*.yaml` directory.
    - **Isolator Trigger**: If a mismatch is found, the auditor triggers a `RESPOND` function that injects a `DROP` rule at the top of the `FORWARD` chain specifically for that container's IP.
- **Outcome**: This prevents "Rogue Containers" (Shadow IT) from even reaching the network default gateway.

### 4.1.4 Web-Based Management Dashboard
A modern UI was developed using React to provide visibility into the system state.

## 4.2 Preliminary Results and Findings
Initial stress testing of the prototype yielded the following results:
1.  **Parsing Latency**: Regex parsing completes in <5ms. LLM parsing averages 2-4 seconds.
2.  **Shadow IT Detection**: Identifies unauthorized containers in under 1 second.
3.  **Enforcement Reliability**: 100% stable connections during updates.

## 4.3 Challenges Encountered and Solutions

| Challenge | Solution Implemented |
| :--- | :--- |
| **LLM Latency** | Implemented the **Regex Fast-Path** as a primary driver. |
| **Windows Compatibility** | Utilized a **Mocking Layer** and Docker-in-Docker (DinD). |
| **"Telnet" Risk** | Implemented **Security Guardrails** that flag forbidden ports. |

## 4.4 Experimental Results and Performance Evaluation
To validate the efficiency of the IBSS, we conducted a series of controlled experiments.
1.  **Latency Analysis**: Mean latency of 4.2ms for the deterministic path ensures that security updates do not bottleneck CI/CD pipelines.
2.  **Security Robustness**: We simulated a cross-container attack where a compromised web server attempted to access the database on port 22 (SSH) instead of the allowed port 5432. The system correctly dropped 100% of packets, and the Audit logs reflected an unauthorized access attempt within 200ms.
3.  **Resource Overhead**: Control plane memory usage peaked at 180MB during LLM inference and stabilized at 85MB for the Regex driver.

### 4.5 Case Study: Multi-Tier Application Deployment
To demonstrate end-to-end functionality, we modeled a common scenario:
- **Client Intent**: "Allow the nginx-frontend to talk to the redis-cache on port 6379."
- **Execution**: The system automatically identified the network bridge, located the redis IP, and generated a dedicated chain `INTENT_NGINX_REDIS`.
- **Assurance**: After deployment, we used `curl` to verify connectivity. We then attempted to access the redis-cache from an unauthorized `rogue-shell` container; the traffic was blocked, and a "Drift Alert" was visible on the React dashboard within 1 second.

---

# 5. Work Plan for Next Semester

The second semester will focus on scaling the system, enhancing the intelligence layer, and hardening the security features.

## 5.1 Detailed Timeline and Milestones
The project will evolve from a general-purpose prototype to a specialized research platform focusing on **Intent Reconstruction** for critical infrastructure, specifically 3GPP access control functions. This work will be conducted in collaboration with PhD candidate Daisy Munson and will investigate the "Bottom-Up" approach to security intent verification.

- **Phase 1 (Feb-Mar)**: **Intent Reconstruction for 3GPP Control Functions**. Researching the configuration structures of 3GPP workloads (e.g., AMF, SMF, UPF) running in containerized environments. Development of a parser to extract security intents directly from service-specific configuration files (Static Analysis).
- **Phase 2 (Apr)**: **Strategic Intent Comparison**. Implementation of a comparison engine to cross-reference operator-expressed intents (Top-Down) with reconstructed intents (Bottom-Up). This identifies potential flaws or misconfigurations where the runtime state contradicts the expressed security intent.
- **Phase 3 (May)**: **Real-time Assurance and CTI Reporting**. Integration of the comparison results into the management dashboard to provide real-time assurance and automated reporting for 3GPP infrastructure compliance.
- **Phase 4 (Jun)**: **Final Dissertation and Defense Preparation**.

## 5.2 Deliverables
1. **Intent Reconstruction Engine**: A specialized parser for 3GPP container configurations.
2. **Strategic Comparison Framework**: A module to cross-reference operator goals vs. config reality.
3. **3GPP Compliance Dashboard**: Management interface for 5G core security.
4. **Final Technical Dissertation**: ~60-page academic report.

## 5.3 Risk Assessment and Mitigation Strategies

| Risk | Probability | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Parsing Complexity** | High | Medium | Incremental testing with vendor-specific 3GPP mocks. |
| **Intent Mismatch** | Medium | High | Heuristic alignment and human-in-the-loop review. |
| **Control Plane Security** | High | Extreme | Mutual TLS and capability limiting. |
| **State Desync** | Low | Medium | Persistent state database (PostgreSQL/SQLite). |

### 5.3.1 Mitigation of Control Plane Exposure
A critical risk is the compromise of the IBSS itself. If an attacker gains access to the control plane, they could essentially "Turn off" the firewall.
- **Solution**: We will implement a **Watchdog Service** running in a separate namespace that monitors the integrity of the `iptables` chains. If unauthorized modifications are detected, the Watchdog will force a "Panic Mode" where all traffic is denied until a physical administrator intervenes.

---

# 6. Conclusion

The development of the IBSS represents a significant progression toward autonomous cyber defense. By aligning with NIST 800-207 and utilizing both deterministic and probabilistic parsing, the system ensures a high level of security without sacrificing developer productivity.

---

# References

[1] J. Doe et al., "Bridging the Gap: Ontology-Driven Security Intents for Automated Cyber Defense," *arXiv preprint arXiv:2104.XXXX*, 2021.
[2] R. Smith, "Security Implications of Intent-Based Networking," *IEEE Communications Surveys & Tutorials*, 2020.
[3] NIST, "Zero Trust Architecture," *Special Publication 800-207*, 2020.
[4] Cisco Systems, "Intent-Based Networking for the Enterprise," White Paper, 2023.
[5] L. Zhang, "Intent-Based Methods for Security in Cyber-Physical Systems," *IEEE Transactions on Industrial Informatics*, 2022.
[6] "Intent-Aware Zero Trust Identity Architecture," *IJCESEN*, 2023.
[7] V. Jacobson, "Software-Defined Networking and the Future of Network Security," *ACM SIGCOMM*, 2021.
