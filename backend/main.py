from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import uvicorn
import os
import json
import yaml
import subprocess
from datetime import datetime

# Add parent directory to path to import intent_parser
PARENT_DIR = Path(__file__).parent.parent
sys.path.append(str(PARENT_DIR))
try:
    from intent_parser import parse_intent
except ImportError:
    # Fallback if running from a different context
    pass

app = FastAPI(
    title="Intent-Based Security API",
    description="""
    ## 🛡️ Autonomous Control Plane for Container Security
    This API handles the translation of high-level security intents into enforced kernel rules.
    It supports:
    * **Semantic Parsing** (Regex/LLM)
    * **Atomic Enforcement** (Zero-Downtime Swaps)
    * **Runtime Drift Detection** (Continuous Auditing)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---

class IntentRequest(BaseModel):
    text: str = "Allow web-service to access database on port 5432"
    container_name: str = "default-container"

class IntentResponse(BaseModel):
    id: str
    text: str
    container_name: str
    yaml_content: str
    created_at: str

class PipelineResponse(BaseModel):
    status: str
    output: str
    details: Optional[str] = None

class DriftEntry(BaseModel):
    container: str
    time: str
    reason: str
    severity: str

class DriftResponse(BaseModel):
    drift: List[DriftEntry] = []
    message: Optional[str] = None

class PortWatchResponse(BaseModel):
    bad_ports: List[int] = []
    safe_ports: List[int] = []

class PolicyFile(BaseModel):
    filename: str
    content: Any

class ContainerInfo(BaseModel):
    name: str
    status: str
    image: str

# In-memory storage for intents (mock db)
intents_db = []

@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint for the Security API."""
    return {"message": "Intent-Based Security API", "status": "running"}

# --- INTENT MANAGEMENT ---

@app.post("/api/intents/", response_model=IntentResponse, tags=["Intent Core"])
async def create_intent(intent: IntentRequest):
    """
    ### 🧠 Semantic Translation
    Takes a natural language string and converts it into a structured YAML Security Policy.
    """
    try:
        print(f"\nPOLICY CREATION REQUEST")
        print(f"{'='*31}")
        print(f"Container: {intent.container_name}")
        print(f"Intent: {intent.text}")
        
        # Import here to avoid circular dependency issues if any
        sys.path.append(str(PARENT_DIR))
        import intent_parser
        import importlib
        importlib.reload(intent_parser)
        
        yaml_content = intent_parser.parse_intent(intent.text, intent.container_name)
        
        # Save to file
        filename = f"intent_{intent.container_name}.yaml"
        file_path = PARENT_DIR / filename
        with open(file_path, "w") as f:
            f.write(yaml_content)
        
        print(f"✓ Policy generated successfully")
        print(f"✓ Saved to: {filename}\n")

        new_intent = {
            "id": str(len(intents_db) + 1),
            "text": intent.text,
            "container_name": intent.container_name,
            "yaml_content": yaml_content,
            "created_at": datetime.now().isoformat()
        }
        
        intents_db.append(new_intent)
        return new_intent
    except Exception as e:
        print(f"✗ Error creating policy: {str(e)}\n")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/intents/", response_model=List[IntentResponse], tags=["Intent Core"])
async def list_intents():
    """Lists all previously interpreted intents stored in the session."""
    return intents_db

# --- PIPELINE CONTROLS ---

@app.post("/api/run_pipeline", response_model=PipelineResponse, tags=["Enforcement"])
async def run_pipeline():
    """
    ### 🚀 Atomic Enforcement Pipeline
    Triggers the reconciliation script to perform the atomic swap in the Linux kernel.
    """
    try:
        script_path = PARENT_DIR / "auto_reconcile.py"
        # Run the script using the same interpreter as the server
        result = subprocess.run(
            [sys.executable, str(script_path)], 
            cwd=str(PARENT_DIR),
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            return {"status": "error", "output": result.stderr, "details": result.stdout}
            
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/drift", response_model=DriftResponse, tags=["Monitoring"])
async def get_drift_logs():
    """
    ### 🔍 Drift Detection
    Retrieves the latest audit logs identifying 'Shadow IT' or unauthorized container behaviors.
    """
    log_path = PARENT_DIR / "drift_log.json"
    if not log_path.exists():
        return DriftResponse(drift=[], message="No drift log found")
    
    try:
        with open(log_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return DriftResponse(drift=[], message=f"Error: {str(e)}")

@app.get("/api/ports", response_model=PortWatchResponse, tags=["Intelligence"])
async def get_port_watch():
    """
    ### 🕵️ Malicious Port Intelligence
    Returns the database of ports under watch for malicious activities.
    """
    path = PARENT_DIR / "port_watch.yaml"
    if not path.exists():
        return PortWatchResponse(bad_ports=[], safe_ports=[])
    
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return data or {}
    except Exception as e:
        return PortWatchResponse(bad_ports=[], safe_ports=[])

@app.get("/api/policies", response_model=List[PolicyFile], tags=["Governance"])
async def list_policies():
    """
    ### 📜 Policy Inventory
    Lists all generated Security Policies (YAML) currently stored in the system.
    """
    policies_dir = PARENT_DIR / "policies"
    if not policies_dir.exists():
        return []
        
    policies = []
    for f in os.listdir(policies_dir):
        if f.endswith(".yaml"):
            try:
                with open(policies_dir / f, "r") as pf:
                    content = yaml.safe_load(pf)
                policies.append({
                    "filename": f,
                    "content": content
                })
            except:
                pass
    return policies

@app.get("/api/containers", response_model=List[ContainerInfo], tags=["Monitoring"])
async def list_containers():
    """
    ### 🐳 Docker Runtime Status
    Monitors the active containers on the host system to cross-reference with security policies.
    """
    try:
        # Simple docker ps to get names
        cmd = ["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Image}}"]
        # Use shell=True on Windows sometimes helps with path resolution, but strict cmd list is safer.
        # We'll stick to list but handle the error.
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        containers = []
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        containers.append({
                            "name": parts[0],
                            "status": parts[1],
                            "image": parts[2]
                        })
            return containers
        else:
            # Docker failed or not running, return mock data for demo
            print(f"Docker check failed: {result.stderr}")
            return [
                {"name": "demo-frontend", "status": "Up (Mock)", "image": "nginx:alpine"},
                {"name": "demo-backend", "status": "Up (Mock)", "image": "python:3.9"},
                {"name": "demo-db", "status": "Up (Mock)", "image": "postgres:14"}
            ]
    except Exception as e:
        print(f"Docker check exception: {e}")
        # Return mock data if docker is not available (dev mode)
        return [
            {"name": "mock-error-fallback", "status": "Up (Fallback)", "image": "nginx:latest"}
        ]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# Force reload for intent_parser updates
