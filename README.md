# Intent-Based Security System

A natural language-driven container security platform that automatically translates plain English security requirements into enforced firewall rules, with continuous drift detection and zero-downtime policy updates.

## Overview

This system eliminates the complexity of manual firewall configuration by allowing administrators to describe security requirements in plain English. The platform automatically translates these natural language intents into precise iptables rules, monitors runtime behavior for policy violations, and enforces security boundaries without service interruption.

**Example Intent:**
```
"My web application requires access to the database and api.stripe.com"
```

**System Response:**
- Translates intent into firewall rules
- Detects dangerous protocols (Telnet, FTP, etc.)
- Enables Layer 7 domain filtering
- Monitors runtime traffic for drift
- Updates rules atomically without downtime

## Core Features

### 1. Natural Language Intent Parser
- Processes security policies written in plain English
- Supports complex multi-service intent declarations
- Automatically infers required ports (DNS, HTTP, HTTPS)
- Example: `"Allow access to web services"` generates rules for ports 80, 443, 53

### 2. Dangerous Port Detection
- Identifies and warns against insecure protocols (Telnet, FTP, unencrypted SMTP)
- Annotates policies with `security_risk: High` classification
- Prevents accidental exposure of vulnerable services

### 3. Layer 7 Domain Filtering
- Whitelists specific domains (e.g., `api.stripe.com`)
- Automatically enables DNS resolution
- Blocks unauthorized external connections

### 4. Zero-Downtime Enforcement
- Implements atomic iptables chain swapping
- Eliminates security gaps during rule updates
- Maintains active connections during policy changes

### 5. Drift Detection
- Captures live network traffic via tcpdump
- Compares runtime behavior against declared intents
- Generates alerts for undeclared ports and domains
- Identifies rogue containers

### 6. Real-Time Dashboard
- Displays security score (0-100 scale)
- Provides live drift analysis
- Visualizes pipeline status
- Monitors container health

## System Architecture

```
┌─────────────────┐
│  React Dashboard│  ← User Interface
└────────┬────────┘
         │
    ┌────▼─────┐
    │ FastAPI  │  ← Backend API
    │ Backend  │
    └────┬─────┘
         │
    ┌────▼──────────────────────┐
    │  Intent Parser (NLP)      │
    │  Policy Enforcer (iptables)│
    │  Traffic Collector (tcpdump)│
    │  Drift Detector           │
    └───────────────────────────┘
```

## Installation

### Prerequisites
- Docker
- Python 3.8 or higher
- Node.js 14 or higher
- Linux operating system (for iptables support)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd dashboard
npm install
npm start
```

### Access Points
- Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## Usage

### Creating an Intent

1. Navigate to "New Intent" in the dashboard
2. Enter container name (e.g., `web-server`)
3. Describe intent in plain English:
   ```
   Allow access to web services and postgres database
   ```
4. Click "Generate Policy" to preview YAML output
5. Click "Apply Policy" to enforce rules

### Running the Security Pipeline

1. Navigate to "Overview" page
2. Click "Run Full Pipeline"
3. System executes:
   - 10-second network traffic capture
   - Drift detection analysis
   - Firewall rule updates
   - Results visualization

### Viewing Drift Analysis

1. Navigate to "Drift Analysis" page
2. Review:
   - High/Medium/Low severity classifications
   - Detailed drift event table
   - Per-container drift summaries

## Testing

### Automated Test Suite
```bash
python run_all_tests.py
```

Test coverage includes:
- Intent parsing (web, database, email services)
- Dangerous port detection
- Layer 7 domain filtering
- Complex multi-service intent handling

### Manual Testing
Refer to `dashboard/TESTING_GUIDE.md` for comprehensive step-by-step test procedures.

## Project Structure

```
intent-based-security/
├── backend/
│   └── main.py              # FastAPI server
├── dashboard/
│   ├── src/
│   │   ├── pages/           # React components
│   │   └── services/        # API client
│   └── TESTING_GUIDE.md     # Manual test procedures
├── intent_parser.py         # NLP to YAML converter
├── policy_enforcer.py       # iptables manager
├── traffic_collector.py     # tcpdump wrapper
├── detect_drift_batch_pretty.py  # Drift analyzer
├── auto_reconcile.py        # Pipeline orchestrator
├── run_all_tests.py         # Unit test suite
└── README.md                # Project documentation
```

## Security Model

- **Zero-Trust Architecture**: Deny-all default policy
- **Least Privilege Principle**: Only declared ports permitted
- **Continuous Monitoring**: 24/7 drift detection
- **Atomic Updates**: No security gaps during policy changes
- **Audit Trail**: Comprehensive drift event logging

## Use Cases

### Microservices Security
```
Frontend: "Allow web services"
Backend: "Allow postgres and redis"
Payment: "Allow access to api.stripe.com"
```

### Intrusion Detection
- Identifies undeclared SSH access (port 22)
- Alerts on connections to unknown domains
- Detects data exfiltration attempts

### Compliance Auditing
- Exportable drift reports
- Least-privilege enforcement verification
- Policy change tracking

## Technical Stack

- FastAPI (Python backend framework)
- React with Material-UI (Frontend interface)
- iptables (Linux firewall)
- Docker (Container runtime)
- tcpdump (Network traffic capture)

## Contributing

This project was developed as part of cybersecurity coursework for academic purposes.

## License

Educational use only.
