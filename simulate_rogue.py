import json
import time
from datetime import datetime

def simulate_attack():
    print("-" * 40)
    print("⚠️  ROGUE CONTAINER SIMULATION INITIALIZED")
    print("-" * 40)

    # 1. Simulate Deployment
    print("\n[1] Deploying unmanaged container 'crypto-miner-v2'...")
    time.sleep(2)
    print("    ✔ Container Started (PID: 8821)")

    # 2. Simulate Traffic
    print("\n[2] Generating unauthorized outbound traffic...")
    time.sleep(1.5)
    print("    ⚠ Connecting to 192.168.1.100:666 (Bad Port)...")
    time.sleep(1)

    # 3. Inject Drift Data (The "Hack" for the Dashboard)
    drift_event = {
        "container": "crypto-miner-v2",
        "bad_ports": [666, 3333],
        "time": datetime.now().isoformat(),
        "reason": "Undeclared Service Detected",
        "severity": "High"
    }

    try:
        # Read existing or create new
        try:
            with open("drift_log.json", "r") as f:
                data = json.load(f)
                if not isinstance(data, list): data = []
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Add our rogue event
        data.append(drift_event)

        with open("drift_log.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print("\n[3] Drift Detected by Monitor!")
        print("    ✔ Log updated: drift_log.json")
        print("    👀 CHECK YOUR DASHBOARD NOW! (It should flash red)")

    except Exception as e:
        print(f"Error updating logs: {e}")

if __name__ == "__main__":
    simulate_attack()
