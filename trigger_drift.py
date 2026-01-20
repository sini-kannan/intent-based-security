import json
from datetime import datetime

# The Dashboard turns RED when the score drops. 
# Unauthorized containers or multiple drift events trigger this.

drift_data = {
    "drift": [
        {
            "container": "risky-app",
            "time": datetime.now().isoformat(),
            "reason": "Unauthorized Container Detected (Shadow IT)",
            "severity": "High",
            "bad_ports": [666, 1337]
        },
        {
            "container": "web-service",
            "time": datetime.now().isoformat(),
            "reason": "Port 22 (SSH) opened manually - SECURITY DRIFT",
            "severity": "Medium",
            "bad_ports": [22]
        }
    ],
    "message": "CRITICAL: 2 Security Drift Events Detected!"
}

with open("drift_log.json", "w") as f:
    json.dump(drift_data, f, indent=2)

print("\n" + "="*50)
print(" 🚀 DRIFT TRIGGERED!")
print("="*50)
print(" 1. The Dashboard score will now drop significantly.")
print(" 2. A warning banner will appear on the Overview page.")
print(" 3. The Drift Analysis page will show the details.")
print("="*50 + "\n")
