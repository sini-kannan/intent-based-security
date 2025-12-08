# Intent-Based Security System: Testing Guide

This guide walks you through how to manually verify that our security dashboard is working as expected. I've broken this down into "Happy Path" tests (normal usage), "Security" tests (detecting bad things), and "Edge Cases" (trying to break it).

## Prerequisites
Before starting, make sure your environment is up:
1.  **Backend**: Running `python backend/main.py`.
2.  **frontend**: Running `npm start` in dashboard (localhost:3000).
3.  **Docker**: Must be running.

---

## 🟢 Part 1: Basic "Happy Path" Testing
*Goal: Prove the system understands simple English and creates firewall rules.*

### Test 1: Web Server Intent
1.  Go to the **"New Intent"** page.
2.  Type `web-server` as the container name.
3.  In the intent box, type: `Allow access to web services`.
4.  Click **"Generate Policy"**.
    *   **Verify**: Look at the code box. You should see port **80** (HTTP) and **443** (HTTPS).
5.  Click **"Apply Policy"**.
    *   **Verify**: You get a green "Policy saved!" success message.

### Test 2: Database Connection
1.  Go to **"New Intent"**.
2.  Type `backend-db`.
3.  Intent: `It needs to connect to postgres database`.
4.  Click **Generate**.
    *   **Verify**: Port **5432** is opened.

---

## 🟡 Part 2: Security & "Bad" Actions
*Goal: Prove the system notices dangerous inputs and unauthorized traffic.*

### Test 3: The "Dangerous Port" Warning
1.  Go to **"New Intent"**.
2.  Name: `risky-app`.
3.  Intent: `Allow access to telnet`.
4.  Click **Generate**.
    *   **Verify**: A **Yellow Warning Bar** appears saying "Port 23 (Telnet) is considered dangerous".
    *   **Verify**: The policy file has `security_risk: High` in it.

### Test 4: L7 Domain Intelligence
1.  Go to **"New Intent"**.
2.  Name: `payment-processor`.
3.  Intent: `My app needs access to api.stripe.com`.
4.  Click **Generate**.
    *   **Verify**: The policy includes `domains: ["api.stripe.com"]` automatically.
    *   **Verify**: It also intelligently opens port 443 (HTTPS) and 53 (DNS) for you.

---

## 🔴 Part 3: Robustness & Rogue Containers
*Goal: Verify the "Self-Healing" capabilities.*

### Test 5: The "Rogue Container" (Unauthorized)
*This is the coolest test. We will run a hidden container and watch the system catch it.*

1.  Open a terminal and run this command (it creates a container trying to ping Google):
    ```bash
    docker run -d --name rogue-hacker --network micro-net alpine sh -c "while true; do wget -qO- google.com; sleep 5; done"
    ```
2.  Wait about 10-15 seconds.
3.  Go to the **Overview** dashboard page.
4.  Click the blue **"▶ Run Full Pipeline"** button.
5.  **Verify**:
    *   Watch your terminal output. You should see: `🚨 ROGUE CONTAINER DETECTED`.
    *   The **Score Board** on the dashboard should drop (e.g., to 60 or 70).
    *   The **Drift Analysis** section might show "Unauthorized".

### Test 6: Complex Sentences
1.  Go to **"New Intent"**.
2.  Intent: `My app needs database. It also needs email.`
3.  Click **Generate**.
    *   **Verify**: It opens ports for BOTH services (3306/5432 for DB, 25/587 for Email).

---

## Troubleshooting
*   **"Network not found"**: If you restarted Docker, run `python intentflow.py start` to fix the network.
*   **Pipeline Stuck**: Check the terminal running `main.py`. If it froze, restart it.

Good luck with the demo! 🚀
