"""
SQLite Persistent Memory & Conversation Database.
Stores multi-session chat histories (clickable mission logs), memory pairs, and project telemetry.
"""
import sqlite3
import os
import json
import time
import uuid
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Sessions table (Missions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            workspace TEXT,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
    """)

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT DEFAULT 'default',
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            timestamp REAL NOT NULL
        )
    """)
    
    # Ensure session_id column exists
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    if "session_id" not in columns:
        cursor.execute("ALTER TABLE messages ADD COLUMN session_id TEXT DEFAULT 'default'")
        
    # Long-term agent memory key-value table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_memory (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at REAL NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def create_or_update_session(session_id: str, title: str, workspace: str = ""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = time.time()
    cursor.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE sessions SET title = ?, workspace = ?, updated_at = ? WHERE id = ?",
            (title, workspace, now, session_id)
        )
    else:
        cursor.execute(
            "INSERT INTO sessions (id, title, workspace, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, title, workspace, now, now)
        )
    conn.commit()
    conn.close()

def list_sessions() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.title, s.workspace, s.created_at, s.updated_at, COUNT(m.id) as msg_count
        FROM sessions s
        LEFT JOIN messages m ON s.id = m.session_id
        GROUP BY s.id
        ORDER BY s.updated_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    sessions = []
    for r in rows:
        sessions.append({
            "id": r[0],
            "title": r[1],
            "workspace": r[2],
            "created_at": r[3],
            "updated_at": r[4],
            "msg_count": r[5]
        })
    return sessions

def save_message(role: str, content: str, session_id: str = "default", metadata: Optional[Dict[str, Any]] = None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    meta_json = json.dumps(metadata or {})
    now = time.time()
    
    cursor.execute(
        "INSERT INTO messages (session_id, role, content, metadata, timestamp) VALUES (?, ?, ?, ?, ?)",
        (session_id, role, content, meta_json, now)
    )
    
    # Update or create session entry
    workspace = (metadata or {}).get("workspace", "")
    cursor.execute("SELECT id, title FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
    else:
        # Generate friendly mission title from prompt
        title = content[:38] + "..." if len(content) > 38 else content
        # Clean attachment prefix from title if present
        if "Attachment:" in title:
            title = title.split("]")[-1].strip() or "Image / Media Inspection"
        title = title.strip() or "Autonomous Mission"
        cursor.execute(
            "INSERT INTO sessions (id, title, workspace, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, title, workspace, now, now)
        )
        
    conn.commit()
    conn.close()

def get_session_messages(session_id: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, role, content, metadata, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    messages = []
    for r in rows:
        messages.append({
            "id": r[0],
            "role": r[1],
            "content": r[2],
            "metadata": json.loads(r[3]) if r[3] else {},
            "timestamp": r[4]
        })
    return messages

def get_recent_messages(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, role, content, metadata, timestamp, session_id FROM messages ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    messages = []
    for r in reversed(rows):
        messages.append({
            "id": r[0],
            "role": r[1],
            "content": r[2],
            "metadata": json.loads(r[3]) if r[3] else {},
            "timestamp": r[4],
            "session_id": r[5] if len(r) > 5 else "default"
        })
    return messages

def delete_session(session_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def clear_all_messages():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()

def set_memory(key: str, value: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO agent_memory (key, value, updated_at) VALUES (?, ?, ?)",
        (key, value, time.time())
    )
    conn.commit()
    conn.close()

def get_all_memories() -> Dict[str, str]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM agent_memory")
    rows = cursor.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}

# Initialize DB on load
init_db()
