# 5. Work Plan for Next Semester

The second semester (February 2026 – June 2026) will focus on scaling the system, enhancing the intelligence layer, and hardening the security features for production-level environments.

## 5.1 Detailed Timeline and Milestones
The project will transition from a general-purpose prototype to a specialized research platform focusing on **Intent Reconstruction** for critical infrastructure, specifically 3GPP access control functions. This work will be conducted in collaboration with PhD candidate Daisy Munson.

### Phase 1: Intent Reconstruction for 3GPP Control Functions (Feb - Mar)
- **Objective**: Extract security intents from existing configurations of 3GPP workloads.
- **Tasks**:
    - Research the configuration schemas of containerized 3GPP functions (AMF, SMF, UPF).
    - Develop a "Bottom-Up" parser to translate these configuration files into structured Intent-JSON/YAML formats.
    - Implement a static analysis engine for Docker-based 3GPP deployments.

### Phase 2: Strategic Intent Comparison & Misconfiguration Detection (April)
- **Objective**: Identify security gaps between declared intents and actual configurations.
- **Tasks**:
    - Implement a comparison engine to cross-reference "Operator Intents" (Top-Down) with "Reconstructed Intents" (Bottom-Up).
    - Develop alerts for "Misconfiguration Drifts" where a 3GPP workload's configuration allows more than the security policy intended.

### Phase 3: Real-time Assurance for 5G/3GPP Workloads (May)
- **Objective**: Provide a live compliance dashboard for distributed 3GPP networks.
- **Tasks**:
    - Integrate the comparison results into the React management dashboard.
    - Implement automated CTI (Cyber Threat Intelligence) reporting for infrastructure compliance audits.

### Phase 4: Final Dissertation and Defense Preparation (June)
- **Objective**: Finalize documentation and prepare for the graduation defense.
- **Tasks**:
    - Complete the 60+ page final technical dissertation at IMT Atlantique.
    - Prepare the oral presentation and physical demo of the 3GPP Intent-Based Security prototype.

## 5.2 Deliverables
1. **Intent Reconstruction Engine**: Capable of parsing 3GPP container configurations.
2. **Strategic Comparison Framework**: Cross-referencing top-down intents with reconstructed configs.
3. **3GPP Compliance Dashboard**: Providing visibility into misconfigurations.
4. **Final Technical Dissertation**: ~60-page research document.

## 5.3 Risk Assessment and Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Parsing Complexity** | High | Medium | Incremental testing with vendor-specific 3GPP config mocks. |
| **Intent Mismatch** | Medium | High | Heuristic-based alignment and human-in-the-loop review. |
| **State Desync** | Low | Medium | Use a persistent database (SQLite/PostgreSQL) for policy state. |
