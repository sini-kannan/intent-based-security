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

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IntentRequest(BaseModel):
    text: str
    container_name: str = "default-container"

class IntentResponse(BaseModel):
    id: str
    text: str
    container_name: str
    yaml_content: str
    created_at: str

# In-memory storage for intents (mock db)
intents_db = []

@app.get("/")
async def root():
    return {"message": "Intent-Based Security API", "status": "running"}

# --- INTENT MANAGEMENT ---

@app.post("/api/intents/", response_model=IntentResponse)
async def create_intent(intent: IntentRequest):
    try:
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
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/intents/", response_model=List[dict])
async def list_intents():
    return intents_db

# --- PIPELINE CONTROLS ---

@app.post("/api/run_pipeline")
async def run_pipeline():
    """Trigger the auto_reconcile execution."""
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

@app.get("/api/drift")
async def get_drift_logs():
    """Get the latest drift log."""
    log_path = PARENT_DIR / "drift_log.json"
    if not log_path.exists():
        return {"drift": [], "message": "No drift log found"}
    
    try:
        with open(log_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/ports")
async def get_port_watch():
    """Get the malicious port database."""
    path = PARENT_DIR / "port_watch.yaml"
    if not path.exists():
        return {"bad_ports": [], "safe_ports": []}
    
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return data or {}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/policies")
async def list_policies():
    """List generated policies."""
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

@app.get("/api/containers")
async def list_containers():
    """List active containers using docker ps."""
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
