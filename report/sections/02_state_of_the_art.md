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
Service meshes provide advanced traffic management and security (mTLS) for microservices.
- **Strengths**: Layer 7 visibility, mutual TLS by default, fine-grained canary rollouts.
- **Weaknesses**: High resource overhead (sidecar pattern), extreme complexity for small teams, and latency introduced by the proxy layer (Envoy).

### 2.3.2 eBPF-Based Solutions (Cilium, Falco)
Cilium uses extended Berkeley Packet Filter (eBPF) to provide highly efficient L3-L7 security.
- **Strengths**: Negligible performance overhead, kernel-level visibility without sidecars, high scalability.
- **Weaknesses**: Requires modern Linux kernels (v4.9+), steep learning curve for custom BPF programs.

### 2.3.4 Comparative Summary of Enforcement Technologies
The choice of enforcement technology is pivotal in an IBS system. While our project currently utilizes **Netfilter/iptables** for its ubiquitous presence and stability, a "State-of-the-Art" analysis requires evaluating its successors.

| Technology | Layer | Latency | Complexity | Flexibility |
| :--- | :--- | :--- | :--- | :--- |
| **Iptables (Netfilter)** | L3/L4 | Medium | Low | High (stable) |
| **IPVS** | L4 | Low | Medium | High (load balancing) |
| **eBPF (XDP)** | L2-L7 | Ultra-Low | High | Extreme (programmable) |
| **Nftables** | L3/L4 | Low | Medium | High (replaces iptables) |

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
- **Challenges**: "Hallucinations" (where the model suggests non-existent or dangerous ports) and high latency are the primary hurdles to using LLMs for real-time enforcement. Our transition to a hybrid model directly addresses this by using AI as a "Co-Pilot" rather than a blind executor.

## 2.5 Positioning of This Project
Our project, the **Intent-Based Security System**, positions itself as a lightweight alternative to complex service meshes and eBPF solutions. It specifically addresses the "Ease of Use" gap by:
1.  **Simplifying User Interface**: Using NLP and simple YAML to hide the complexity of `iptables`.
2.  **Hybrid Approach**: Using Regex for common patterns (90% of cases) to ensure ultra-low latency, while maintaining an LLM-Ready architecture for complex intents.
3.  **Local-First Architecture**: Avoiding external cloud dependencies for security parsing, ensuring data privacy and offline capability.
