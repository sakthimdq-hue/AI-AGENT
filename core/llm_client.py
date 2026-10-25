"""
Multi-provider LLM client supporting Google Gemini Free Tier, Ollama (Local 0-cost), and OpenAI-compatible APIs.
Includes automatic fallback for high-demand Gemini models and Gemini 3.x thought signature support.
"""
import os
import json
import httpx
from typing import Dict, Any, List, Optional

GEMINI_FALLBACK_MODELS = ["gemini-flash-latest", "gemini-3.1-flash-lite", "gemini-3.8-flash"]

class LLMClient:
    def __init__(self, provider: str = "gemini", model: str = "gemini-flash-latest", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
        self.base_url = base_url or ("http://localhost:11434" if self.provider == "ollama" else None)

    def set_config(self, provider: str, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model
        if api_key is not None:
            self.api_key = api_key
        if base_url is not None:
            self.base_url = base_url

    async def call_gemini(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> Dict[str, Any]:
        """Call Google Gemini API via official REST endpoint with auto-fallback and thoughtSignature handling."""
        if not self.api_key:
            raise ValueError("Gemini API key is required. Get one for free at https://aistudio.google.com/")

        # Function declarations
        function_declarations = []
        for t in tools:
            function_declarations.append({
                "name": t["name"],
                "description": t["description"],
                "parameters": t.get("parameters", {})
            })

        # Convert chat history to Gemini format
        contents = []
        for msg in messages:
            role = msg["role"]
            gemini_role = "user" if role in ["user", "system"] else "model"
            
            parts = []
            if "content" in msg and msg["content"]:
                raw_text = str(msg["content"])
                parts.append({"text": raw_text})

                # Multimodal Image Injection for Gemini
                import re, base64, mimetypes
                match = re.search(r'\[Attachment:[^\]]*saved at\s+([^\]]+)\]', raw_text)
                if match:
                    img_path = match.group(1).strip()
                    if os.path.exists(img_path) and any(img_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']):
                        try:
                            mime_type, _ = mimetypes.guess_type(img_path)
                            if not mime_type:
                                mime_type = "image/png"
                            with open(img_path, "rb") as img_file:
                                b64_bytes = base64.b64encode(img_file.read()).decode("utf-8")
                            parts.append({
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": b64_bytes
                                }
                            })
                        except Exception:
                            pass

            
            if "tool_calls" in msg:
                for tc in msg["tool_calls"]:
                    p: Dict[str, Any] = {
                        "functionCall": {
                            "name": tc["name"],
                            "args": tc.get("arguments", {})
                        }
                    }
                    if tc.get("id"):
                        p["functionCall"]["id"] = tc["id"]
                    if tc.get("thoughtSignature"):
                        p["thoughtSignature"] = tc["thoughtSignature"]
                    parts.append(p)
            
            if "tool_response" in msg:
                fr: Dict[str, Any] = {
                    "name": msg["tool_name"],
                    "response": {"output": msg["tool_response"]}
                }
                if msg.get("tool_call_id") and not msg["tool_call_id"].startswith("call_"):
                    fr["id"] = msg["tool_call_id"]
                parts.append({"functionResponse": fr})

            if parts:
                contents.append({"role": gemini_role, "parts": parts})

        payload: Dict[str, Any] = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            }
        }

        if function_declarations:
            payload["tools"] = [{"functionDeclarations": function_declarations}]

        # Candidate models to try if the primary encounters 404/503
        models_to_try = [self.model]
        for m in GEMINI_FALLBACK_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        async with httpx.AsyncClient(timeout=60.0) as client:
            for current_model in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={self.api_key}"
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            raise RuntimeError(f"No candidates returned: {data}")

                        content_obj = candidates[0].get("content", {})
                        parts = content_obj.get("parts", [])
                        
                        thought_text = ""
                        tool_calls = []

                        for p in parts:
                            if "text" in p:
                                thought_text += p["text"]
                            elif "functionCall" in p:
                                fc = p["functionCall"]
                                tc_data = {
                                    "id": fc.get("id") or f"call_{len(tool_calls)}",
                                    "name": fc["name"],
                                    "arguments": fc.get("args", {})
                                }
                                if "thoughtSignature" in p:
                                    tc_data["thoughtSignature"] = p["thoughtSignature"]
                                tool_calls.append(tc_data)

                        # Update active model if fallback succeeded
                        self.model = current_model
                        return {
                            "content": thought_text.strip(),
                            "tool_calls": tool_calls
                        }
                    else:
                        last_error = f"Gemini API Error {resp.status_code} on model {current_model}: {resp.text}"
                        # Retry on 404, 503, or 429
                        if resp.status_code in [404, 503, 429]:
                            continue
                        else:
                            raise RuntimeError(last_error)
                except httpx.TimeoutException:
                    last_error = f"Timeout connecting to Gemini model {current_model}"
                    continue

        raise RuntimeError(last_error or "Failed to call Gemini API after trying all fallback models.")

    async def call_ollama(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> Dict[str, Any]:
        """Call local Ollama server (100% free & offline)."""
        base = self.base_url or "http://localhost:11434"
        url = f"{base}/api/chat"

        ollama_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            content = m.get("content", "")
            if "tool_calls" in m:
                content += f"\n[Requested Tools: {json.dumps(m['tool_calls'])}]"
            if "tool_response" in m:
                content = f"[Tool '{m.get('tool_name')}' Result]: {json.dumps(m.get('tool_response'))}"
            ollama_messages.append({
                "role": "assistant" if m["role"] == "assistant" else "user",
                "content": content
            })

        ollama_tools = [{"type": "function", "function": t} for t in tools]

        payload = {
            "model": self.model or "qwen2.5-coder:7b",
            "messages": ollama_messages,
            "tools": ollama_tools,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama Error {resp.status_code}: {resp.text}")
            
            data = resp.json()
            msg = data.get("message", {})
            tool_calls = []
            for tc in msg.get("tool_calls", []):
                fn = tc.get("function", {})
                tool_calls.append({
                    "id": tc.get("id", "call_0"),
                    "name": fn.get("name"),
                    "arguments": fn.get("arguments", {})
                })

            return {
                "content": msg.get("content", "").strip(),
                "tool_calls": tool_calls
            }

    async def call_openai_compatible(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> Dict[str, Any]:
        """Call OpenAI, Groq, or OpenRouter endpoint."""
        url = f"{self.base_url or 'https://api.openai.com/v1'}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        openai_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            role = m["role"]
            if role == "tool":
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": m.get("tool_call_id", "call_0"),
                    "content": json.dumps(m.get("tool_response", {}))
                })
            else:
                msg_dict = {"role": role, "content": m.get("content", "")}
                if "tool_calls" in m and m["tool_calls"]:
                    msg_dict["tool_calls"] = [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc.get("arguments", {}))
                            }
                        }
                        for tc in m["tool_calls"]
                    ]
                openai_messages.append(msg_dict)

        openai_tools = [{"type": "function", "function": t} for t in tools]

        payload = {
            "model": self.model,
            "messages": openai_messages,
            "tools": openai_tools
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"API Error {resp.status_code}: {resp.text}")
            
            data = resp.json()
            choice = data["choices"][0]["message"]
            tool_calls = []
            for tc in choice.get("tool_calls", []):
                tool_calls.append({
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"])
                })

            return {
                "content": choice.get("content", "") or "",
                "tool_calls": tool_calls
            }

    async def generate_step(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> Dict[str, Any]:
        """Dispatch generation to configured provider."""
        if self.provider == "gemini":
            return await self.call_gemini(messages, tools, system_prompt)
        elif self.provider == "ollama":
            try:
                return await self.call_ollama(messages, tools, system_prompt)
            except Exception as e:
                # If Ollama is unreachable locally, automatically fallback to Gemini Cloud
                if self.api_key:
                    return await self.call_gemini(messages, tools, system_prompt)
                raise RuntimeError(f"Ollama is offline/unreachable ({e}). Please start Ollama or switch to Cloud (Gemini) mode.")
        else:
            return await self.call_openai_compatible(messages, tools, system_prompt)

