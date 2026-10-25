"""
Core Tools for Autonomous Coding Agent.
Provides file manipulation, code search, and terminal command execution.
"""
import os
import subprocess
import glob
import re
from typing import Dict, Any, List, Optional

WORKSPACE_ROOT = os.path.abspath(os.getcwd())

def set_workspace_root(path: str) -> str:
    """Dynamically set the active workspace directory."""
    global WORKSPACE_ROOT
    full_path = os.path.abspath(path)
    os.makedirs(full_path, exist_ok=True)
    WORKSPACE_ROOT = full_path
    return WORKSPACE_ROOT

def get_workspace_root() -> str:
    """Get the currently active workspace directory."""
    return WORKSPACE_ROOT

def resolve_path(path: str, base_dir: Optional[str] = None) -> str:
    """Resolve a relative or absolute path within the workspace or anywhere on the laptop."""
    expanded = os.path.expanduser(path)
    if os.path.isabs(expanded):
        return os.path.abspath(expanded)
    base = base_dir or WORKSPACE_ROOT
    return os.path.abspath(os.path.join(base, expanded))

def list_directory(dir_path: str = ".") -> Dict[str, Any]:
    """List files and directories within a given directory."""
    full_path = resolve_path(dir_path)
    if not os.path.exists(full_path):
        return {"error": f"Directory not found: {dir_path}"}
    if not os.path.isdir(full_path):
        return {"error": f"Path is not a directory: {dir_path}"}

    items = []
    try:
        for entry in sorted(os.scandir(full_path), key=lambda e: (not e.is_dir(), e.name.lower())):
            # skip hidden git/venv internals if inside workspace to prevent clutter
            if entry.name in [".git", "__pycache__", "venv", ".pytest_cache", "node_modules"]:
                continue
            is_dir = entry.is_dir()
            size = entry.stat().st_size if not is_dir else None
            items.append({
                "name": entry.name,
                "is_dir": is_dir,
                "size_bytes": size,
                "rel_path": os.path.relpath(entry.path, WORKSPACE_ROOT)
            })
        return {"directory": dir_path, "items": items, "count": len(items)}
    except Exception as e:
        return {"error": str(e)}

def read_file(file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> Dict[str, Any]:
    """Read file content with line numbers and optional line range (1-indexed)."""
    full_path = resolve_path(file_path)
    if not os.path.exists(full_path):
        return {"error": f"File does not exist: {file_path}"}
    if os.path.isdir(full_path):
        return {"error": f"Path is a directory, not a file: {file_path}"}

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        s = max(1, start_line or 1)
        e = min(total_lines, end_line or total_lines)
        
        selected_lines = lines[s - 1:e]
        formatted_content = "".join([f"{i:4d} | {line}" for i, line in enumerate(selected_lines, start=s)])
        
        return {
            "file_path": file_path,
            "total_lines": total_lines,
            "range": [s, e],
            "content": formatted_content
        }
    except Exception as e:
        return {"error": str(e)}

def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """Create or overwrite a file with given content."""
    full_path = resolve_path(file_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        lines_count = len(content.splitlines())
        return {
            "success": True,
            "file_path": file_path,
            "lines_written": lines_count,
            "message": f"Successfully wrote {lines_count} lines to {file_path}"
        }
    except Exception as e:
        return {"error": str(e)}

def edit_file(file_path: str, target_text: str, replacement_text: str) -> Dict[str, Any]:
    """Replace an exact block of code inside a file."""
    full_path = resolve_path(file_path)
    if not os.path.exists(full_path):
        return {"error": f"File does not exist: {file_path}"}

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        if target_text not in content:
            return {
                "error": "Target text was not found in file. Make sure whitespace and line breaks match exactly.",
                "file_path": file_path
            }

        count = content.count(target_text)
        if count > 1:
            return {
                "error": f"Target text occurs {count} times in the file. Please provide more surrounding context to make it unique.",
                "file_path": file_path
            }

        new_content = content.replace(target_text, replacement_text, 1)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {
            "success": True,
            "file_path": file_path,
            "message": "File successfully updated with replacement."
        }
    except Exception as e:
        return {"error": str(e)}

def grep_search(query: str, search_path: str = ".", is_regex: bool = False) -> Dict[str, Any]:
    """Search for a text pattern or regex across files in search_path."""
    full_path = resolve_path(search_path)
    matches = []
    
    try:
        pattern = re.compile(query if is_regex else re.escape(query), re.IGNORECASE)
    except re.error as e:
        return {"error": f"Invalid regex pattern: {e}"}

    for root, dirs, files in os.walk(full_path):
        # Exclude ignored directories
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", "node_modules", ".pytest_cache"]]
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, WORKSPACE_ROOT)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, start=1):
                        if pattern.search(line):
                            matches.append({
                                "file": rel_path,
                                "line_number": line_no,
                                "line_content": line.strip()
                            })
                            if len(matches) >= 50:
                                return {"matches": matches, "truncated": True, "total": len(matches)}
            except Exception:
                continue

    return {"matches": matches, "truncated": False, "total": len(matches)}

def run_command(command: str, cwd: str = ".", timeout_seconds: int = 30) -> Dict[str, Any]:
    """Execute a bash command in the specified directory."""
    full_cwd = resolve_path(cwd)
    if not os.path.exists(full_cwd):
        return {"error": f"Working directory does not exist: {cwd}"}

    # Safety checks against catastrophic accidental commands
    dangerous_patterns = [r"rm\s+-rf\s+/(?:\s|$)", r":\(\)\s*\{", r"mkfs", r"dd\s+if="]
    for dp in dangerous_patterns:
        if re.search(dp, command):
            return {"error": f"Command rejected due to safety policy: {command}"}

    try:
        res = subprocess.run(
            command,
            shell=True,
            cwd=full_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds
        )
        return {
            "command": command,
            "exit_code": res.returncode,
            "stdout": res.stdout[-4000:] if len(res.stdout) > 4000 else res.stdout,
            "stderr": res.stderr[-4000:] if len(res.stderr) > 4000 else res.stderr,
            "success": res.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout_seconds} seconds: {command}"}
    except Exception as e:
        return {"error": str(e)}

# Registry of tools in JSON Schema format for LLM function calling
TOOL_DEFINITIONS = [
    {
        "name": "list_directory",
        "description": "Lists files and subdirectories at a given directory path. Use this to explore codebase structure.",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {"type": "string", "description": "Relative or absolute directory path (defaults to '.')."}
            }
        }
    },
    {
        "name": "read_file",
        "description": "Reads the content of a file with line numbers. Use to inspect code before editing.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to read."},
                "start_line": {"type": "integer", "description": "Starting line number (1-indexed, optional)."},
                "end_line": {"type": "integer", "description": "Ending line number (1-indexed, optional)."}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Creates a new file or completely replaces the contents of an existing file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file."},
                "content": {"type": "string", "description": "The complete content to write."}
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "Replaces an exact snippet of code in a file with new code.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to modify."},
                "target_text": {"type": "string", "description": "Exact text to find and replace."},
                "replacement_text": {"type": "string", "description": "The replacement code."}
            },
            "required": ["file_path", "target_text", "replacement_text"]
        }
    },
    {
        "name": "grep_search",
        "description": "Searches for matching text or regex across the project repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search term or regex."},
                "search_path": {"type": "string", "description": "Directory to search in (defaults to '.')."},
                "is_regex": {"type": "boolean", "description": "Whether query is a regex."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "run_command",
        "description": "Runs a terminal command in the project environment (e.g. pytest, python script.py, npm test, git status).",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The exact shell command to run."},
                "cwd": {"type": "string", "description": "Working directory (defaults to '.')."}
            },
            "required": ["command"]
        }
    },
    {
        "name": "task_completed",
        "description": "Call this tool when you have fully completed the user's task, verified it, and want to present the final summary.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Comprehensive explanation of what was done, files changed, and verification result."}
            },
            "required": ["summary"]
        }
    },
    {
        "name": "remember",
        "description": "Store a user preference, important project fact, or key detail permanently in SQLite memory database.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Memory key identifier (e.g. 'user_identity', 'project_notes')"},
                "value": {"type": "string", "description": "Value to remember"}
            },
            "required": ["key", "value"]
        }
    }
]

def _remember_wrapper(key: str, value: str) -> Dict[str, Any]:
    try:
        from core.db import set_memory
        set_memory(key, value)
        return {"status": "success", "message": f"Stored in database memory: {key} = {value}"}
    except Exception as e:
        return {"error": str(e)}

TOOL_MAP = {
    "list_directory": list_directory,
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "grep_search": grep_search,
    "run_command": run_command,
    "remember": _remember_wrapper,
    "task_completed": lambda summary: {"status": "completed", "summary": summary}
}

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a registered tool by name with arguments."""
    func = TOOL_MAP.get(tool_name)
    if not func:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return func(**arguments)
    except Exception as e:
        return {"error": f"Error executing tool {tool_name}: {str(e)}"}
