"""
Autonomous ReAct Execution Engine for the Software Engineer Agent.
Yields real-time streaming events for the Web UI and CLI.
"""
import os
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List, Optional
from core.tools import TOOL_DEFINITIONS, execute_tool, set_workspace_root, get_workspace_root
from core.llm_client import LLMClient
from core.prompts import SYSTEM_PROMPT

class AutonomousAgent:
    def __init__(self, llm_client: LLMClient, max_steps: int = 35, workspace_path: Optional[str] = None):
        self.llm = llm_client
        self.max_steps = max_steps
        self.workspace_path = workspace_path
        self.history: List[Dict[str, Any]] = []

    async def run(self, user_instruction: str, workspace_path: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute the user instruction autonomously in a multi-step ReAct loop.
        Yields structured event dicts at each step.
        """
        target_ws = os.path.abspath(workspace_path or self.workspace_path or get_workspace_root())
        set_workspace_root(target_ws)

        yield {
            "type": "start",
            "instruction": user_instruction,
            "workspace": target_ws,
            "provider": self.llm.provider,
            "model": self.llm.model
        }

        # Context message giving current workspace path to the model with strict action mandate
        context_msg = (
            f"[Active Workspace Directory: {target_ws}]\n"
            f"User Request: {user_instruction}\n\n"
            f"MANDATORY EXECUTION DIRECTIVE: You are an autonomous software engineering DOER. "
            f"Do NOT merely provide advice, bullet-point lists, or ask conversational questions. "
            f"Immediately pick the best architecture, create all necessary project files using `write_file`, "
            f"write complete code without placeholders, run verification commands using `run_command`, "
            f"and deliver a fully working implementation in the workspace."
        )

        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": context_msg}
        ]

        step = 0
        completed = False

        while step < self.max_steps and not completed:
            step += 1
            yield {"type": "step_begin", "step": step}

            try:
                # Ask LLM for next thought and tool calls
                response = await self.llm.generate_step(
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    system_prompt=SYSTEM_PROMPT
                )
            except Exception as e:
                yield {
                    "type": "error",
                    "step": step,
                    "message": f"LLM execution error: {str(e)}"
                }
                return

            thought = response.get("content", "")
            raw_tool_calls = response.get("tool_calls", [])

            # Filter out unnecessary dummy tool calls (e.g. echo) for conversational queries
            tool_calls = []
            for tc in raw_tool_calls:
                tname = tc.get("name")
                targs = tc.get("arguments", {})
                if tname == "run_command":
                    cmd = targs.get("command", "").strip()
                    if cmd.startswith("echo ") or cmd.startswith("printf "):
                        if not thought:
                            thought = cmd.split("echo ", 1)[-1].strip().strip('"').strip("'")
                        continue
                tool_calls.append(tc)

            if thought and tool_calls:
                yield {
                    "type": "thought",
                    "step": step,
                    "content": thought
                }

            # If model didn't call any tools (conversational response), finish immediately
            if not tool_calls:
                yield {
                    "type": "completed",
                    "step": step,
                    "summary": thought or "Sollu da machan, enna pannanum?"
                }
                completed = True
                break

            # Record model's assistant turn in history
            messages.append({
                "role": "assistant",
                "content": thought,
                "tool_calls": tool_calls
            })

            # Execute tool calls
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc.get("arguments", {})
                call_id = tc.get("id", f"call_{step}")

                yield {
                    "type": "tool_start",
                    "step": step,
                    "tool": tool_name,
                    "arguments": tool_args,
                    "call_id": call_id
                }

                # Run tool asynchronously (subprocess is handled synchronously in threadpool if needed)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, execute_tool, tool_name, tool_args)

                yield {
                    "type": "tool_result",
                    "step": step,
                    "tool": tool_name,
                    "result": result,
                    "call_id": call_id
                }

                # Check if this tool marks completion
                if tool_name == "task_completed":
                    completed = True
                    yield {
                        "type": "completed",
                        "step": step,
                        "summary": tool_args.get("summary", "Task completed successfully.")
                    }
                    break

                # Add tool response to messages
                messages.append({
                    "role": "tool",
                    "tool_name": tool_name,
                    "tool_call_id": call_id,
                    "tool_response": result
                })

        if not completed and step >= self.max_steps:
            yield {
                "type": "max_steps_reached",
                "step": step,
                "message": f"Reached maximum allowed autonomous steps ({self.max_steps})."
            }
