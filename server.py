"""
FastAPI Server for SakthiDev Studio.
Provides SSE streaming, SQLite Persistent Memory, Image/Audio Uploads, and System Navigation.
"""
import os
import json
import asyncio
import shutil
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.llm_client import LLMClient
from core.agent import AutonomousAgent
from core.tools import list_directory, set_workspace_root, get_workspace_root
from core.db import (
    save_message, get_recent_messages, clear_all_messages, get_all_memories,
    list_sessions, get_session_messages, delete_session, create_or_update_session
)

CONFIG_FILE = "config.json"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "provider": "gemini",
        "model": "gemini-3.1-flash-lite",
        "api_key": os.environ.get("GEMINI_API_KEY", ""),
        "base_url": "http://localhost:11434",
        "current_workspace": os.path.abspath(os.getcwd())
    }

def save_config(cfg: Dict[str, Any]):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

app = FastAPI(title="SakthiDev Studio - Autonomous AI Software Engineer")

# Mount static & uploads folders
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

class ConfigUpdate(BaseModel):
    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class WorkspaceUpdate(BaseModel):
    workspace_path: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SakthiDev Studio</h1><p>Please make sure static/index.html is created.</p>"

@app.post("/api/set-icon")
async def update_active_icon(req: Request):
    data = await req.json()
    icon_filename = data.get("icon")
    valid_icons = [
        "icon_1_cyber_lion.svg",
        "icon_2_quantum_reactor.svg",
        "icon_3_cyber_samurai.svg",
        "icon_4_cyber_falcon.svg",
        "icon_5_glitch_monogram.svg"
    ]
    if icon_filename not in valid_icons:
        raise HTTPException(status_code=400, detail="Invalid icon selection")
    src = os.path.join("static", "icons", icon_filename)
    dst = os.path.join("static", "icon.svg")
    shutil.copyfile(src, dst)
    return {"status": "ok", "active_icon": icon_filename}

@app.get("/api/config")
async def read_config():
    cfg = get_config()
    key = cfg.get("api_key", "")
    masked_key = (key[:6] + "..." + key[-4:]) if len(key) > 10 else ("*" * len(key))
    current_ws = cfg.get("current_workspace", os.path.abspath(os.getcwd()))
    return {
        "provider": cfg.get("provider", "gemini"),
        "model": cfg.get("model", "gemini-3.1-flash-lite"),
        "has_key": bool(key),
        "raw_key": key,
        "masked_key": masked_key,
        "base_url": cfg.get("base_url", "http://localhost:11434"),
        "current_workspace": current_ws
    }

@app.post("/api/config")
async def update_config(payload: ConfigUpdate):
    cfg = get_config()
    cfg["provider"] = payload.provider
    cfg["model"] = payload.model
    if payload.api_key is not None and payload.api_key.strip():
        cfg["api_key"] = payload.api_key.strip()
    if payload.base_url is not None:
        cfg["base_url"] = payload.base_url.strip()
    save_config(cfg)
    return {"status": "success", "message": "Configuration saved successfully"}

@app.post("/api/workspace")
async def update_workspace(payload: WorkspaceUpdate):
    raw_path = payload.workspace_path.strip()
    if not raw_path:
        raise HTTPException(status_code=400, detail="Workspace path cannot be empty")
    
    full_path = os.path.abspath(os.path.expanduser(raw_path))
    os.makedirs(full_path, exist_ok=True)
    set_workspace_root(full_path)
    
    cfg = get_config()
    cfg["current_workspace"] = full_path
    save_config(cfg)
    return {
        "status": "success",
        "workspace_path": full_path,
        "files": list_directory(full_path)
    }

@app.get("/api/files")
async def get_workspace_files(workspace_path: Optional[str] = None):
    cfg = get_config()
    target = workspace_path or cfg.get("current_workspace") or os.getcwd()
    target = os.path.abspath(os.path.expanduser(target))
    os.makedirs(target, exist_ok=True)
    set_workspace_root(target)
    return list_directory(target)

@app.get("/api/sessions")
async def get_all_sessions():
    """Retrieve list of all stored missions/chat sessions for the history sidebar."""
    return {"sessions": list_sessions()}

@app.get("/api/sessions/{session_id}")
async def get_single_session(session_id: str):
    """Retrieve messages for a specific mission/session."""
    messages = get_session_messages(session_id)
    return {"session_id": session_id, "messages": messages}

@app.delete("/api/sessions/{session_id}")
async def remove_session(session_id: str):
    """Delete a specific mission/session from SQLite."""
    delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}

@app.get("/api/history")
async def get_chat_history():
    """Retrieve persistent conversation history from SQLite database."""
    messages = get_recent_messages(limit=50)
    return {"history": messages}

@app.post("/api/history/clear")
async def clear_chat_history():
    """Clear chat conversation history from SQLite database."""
    clear_all_messages()
    return {"status": "cleared", "message": "All mission history cleared successfully"}

@app.get("/api/memories")
async def get_agent_memories():
    """Retrieve long-term memory key-value pairs from SQLite database."""
    return {"memories": get_all_memories()}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload an image or audio/code file to the server for agent inspection."""
    safe_name = f"{int(time.time())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "status": "uploaded",
        "filename": file.filename,
        "file_path": os.path.abspath(file_path),
        "url": f"/uploads/{safe_name}",
        "is_image": file.content_type.startswith("image/") if file.content_type else False
    }

@app.get("/api/agent/stream")
async def stream_agent(instruction: str, workspace_path: Optional[str] = None, session_id: Optional[str] = None):
    if not instruction or not instruction.strip():
        raise HTTPException(status_code=400, detail="Instruction query parameter is required")

    cfg = get_config()
    provider = cfg.get("provider", "gemini")
    model = cfg.get("model", "gemini-3.1-flash-lite")
    api_key = cfg.get("api_key", "")
    base_url = cfg.get("base_url")
    
    target_ws = workspace_path or cfg.get("current_workspace") or os.getcwd()
    target_ws = os.path.abspath(os.path.expanduser(target_ws))
    os.makedirs(target_ws, exist_ok=True)
    set_workspace_root(target_ws)

    active_session_id = session_id.strip() if session_id and session_id.strip() else f"mission_{int(time.time())}"

    # Save user message into SQLite tagged by session_id
    save_message(
        role="user", 
        content=instruction.strip(), 
        session_id=active_session_id, 
        metadata={"workspace": target_ws}
    )

    client = LLMClient(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url
    )
    agent = AutonomousAgent(llm_client=client, workspace_path=target_ws)

    async def event_generator():
        try:
            # First notify client about active session ID
            yield f"data: {json.dumps({'type': 'session_info', 'session_id': active_session_id})}\n\n"
            
            async for event in agent.run(instruction.strip(), workspace_path=target_ws):
                # If completed, save assistant summary to SQLite under this session_id
                if event.get("type") == "completed":
                    summary = event.get("summary", "")
                    save_message(
                        role="assistant", 
                        content=summary, 
                        session_id=active_session_id, 
                        metadata={"step": event.get("step")}
                    )
                
                payload = json.dumps(event)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0.04)
        except Exception as e:
            err = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {err}\n\n"


    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.py:app", host="0.0.0.0", port=8000, reload=True)
