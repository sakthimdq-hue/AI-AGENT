# ⚡ SakthiDev Studio - Autonomous AI Software Engineer

> **A Full-Stack Autonomous AI Software Engineer running locally. Capable of end-to-end project scaffolding, file operations, bash command execution, and automated self-healing.**  
> **Developed by: Sakthi**

---

## 🎯 1. Project Abstract & Motivation

Modern software development involves repetitive cycles of exploring code, writing boilerplate, executing terminal build commands, debugging errors, and running tests. While traditional AI chatbots can only generate static snippets of text, **SakthiDev Studio** is an **active autonomous agent**:

- It possesses direct, secure access to the local filesystem and bash terminal.
- It operates via a multi-step **ReAct (Reason + Act + Observe)** execution loop.
- Given a high-level instruction or even an empty folder, it autonomously architects the solution, writes all necessary files, executes setup commands, runs tests, inspects failures, self-heals any errors, and delivers verified, working software.
- Built with **100% Zero-Cost Architecture**: Operates on Google Gemini Free Tier or completely offline using local open-source models via Ollama.

---

## 🏗️ 2. System Architecture & Flowchart

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Instruction Input                          │
│               (Web Studio UI :8000 / Terminal CLI)                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   SakthiDev Autonomous Agent Core                      │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │               ReAct State Machine (Step Loop)                  │   │
│   │                                                                │   │
│   │   1. REASON  : Formulate execution strategy & analyze output   │   │
│   │   2. ACT     : Select & invoke tool with validated schema      │   │
│   │   3. OBSERVE : Ingest tool output (file data / bash stdout)    │   │
│   │   4. CORRECT : Inspect error traces & patch code if failed     │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
└───────────────────────────────────┼────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌─────────────────┐       ┌────────────────────┐     ┌───────────────────┐
│ Filesystem API  │       │ Terminal Execution │     │ Multi-Model Hub   │
│ • read_file     │       │ • run_command      │     │ • Gemini Free     │
│ • write_file    │       │   (pytest, npm,    │     │ • Local Ollama    │
│ • edit_file     │       │    git, builds)    │     │   (Offline mode)  │
│ • grep_search   │       │ • Execution Safety │     │ • Fallback Engine │
└─────────────────┘       └────────────────────┘     └───────────────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Server-Sent Events (SSE) Stream                      │
│                                   │                                    │
│  ┌────────────────────────────────┴─────────────────────────────────┐  │
│  │                     Modern Web Studio UI                         │  │
│  │  • Neural HUD Activity Monitor (Live Radar & Stopwatch)          │  │
│  │  • Dynamic Workspace Directory Switcher                          │  │
│  │  • Real-time Terminal Log & Thought Stream                       │  │
│  │  • Live Workspace File Explorer                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 3. Key Technical Innovations

1. **Zero-Hesitation Autonomous Scaffolding**:
   Unlike conversational chatbots that only list ideas, SakthiDev is primed with an action-biased system prompt: when given an empty folder, it immediately plans, writes real files using `write_file`, installs dependencies, and verifies with unit tests.

2. **Self-Healing Test-Driven Development (TDD)**:
   When running unit tests or bash commands via `run_command`, if an `AssertionError` or syntax error occurs, the agent reads the exact stack trace, locates the faulty file/line, edits the code via `edit_file`, and re-runs the tests until the suite turns green.

3. **Multi-Model Provider with Auto-Fallback**:
   Supports both Google Cloud Gemini Free Tier (0-cost) and Local Ollama (100% offline, privacy-first). Features an automated fallback mechanism: if a model returns a 503 spike or 404 deprecation, it smoothly shifts across alternative models without interrupting the user.

4. **Neural HUD Real-Time Visual Monitor**:
   An interactive UI featuring a rotating radar ring, active operation label (`✏️ Writing code...`, `⚡ Running bash...`), and live stopwatch timer so the user observes every action the agent executes in real time.

---

## 🚀 4. How to Run the Project (Live Demo)

### 1. Launch SakthiDev Studio
```bash
cd "/home/sakthi/Documents/AI AGENT"
./start.sh
```
Or manually:
```bash
./venv/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at: **`http://localhost:8000`**

### 2. Run Comprehensive Agent Tools Verification
```bash
./venv/bin/python3 -c "from core.tools import list_directory; print(list_directory('.'))"
```

---

## 🎬 5. Step-by-Step Evaluator Demo Script (Tomorrow's Presentation)

When presenting to your evaluator or manager, follow this 3-minute winning demo sequence:

1. **Show the Studio Dashboard**:
   - Open `http://localhost:8000`.
   - Point out the branding (**SakthiDev Studio**), the **Neural HUD**, the **Dynamic Workspace Selector**, and the **1-Click Cloud vs Offline Toggle**.

2. **Demo 1: The Self-Healing Bug Fixer**:
   - Click the quick action: **`🐞 Self-Healing Demo`**.
   - Watch the agent run the failing test in `demo_project/test_payment.py` ➔ see the `AssertionError: 120.0 != 99.0` ➔ read `payment_processor.py` ➔ fix the math bug ➔ re-run tests ➔ all 4 tests turn green!
   - Highlight: *"Sir, as you can see, the agent didn't just write code; it tested it, found its own error, self-healed, and verified the fix autonomously."*

3. **Demo 2: Scaffolding a Complete Project in an Empty Folder**:
   - In the top workspace bar, type any folder path (e.g., `/home/sakthi/Downloads/my_new_service`).
   - Type in chat: *"Build a full task management REST API with SQLite and unit tests in this folder."*
   - Watch the agent create the files live in the right-side File Explorer, run tests, and report completion!

---

## 🎓 6. Viva Voce & Evaluator Q&A

**Q1: What is the core difference between an LLM Chatbot and an AI Agent?**
> *Answer:* A chatbot takes text in and outputs text out without environment agency. An AI Agent implements a ReAct loop: it has tools to read/write the filesystem and execute terminal commands, evaluates observations from the environment, and takes autonomous actions until the goal is achieved.

**Q2: How does the agent prevent infinite loops if a test keeps failing?**
> *Answer:* We enforced a deterministic step bound (`max_steps = 35`) in `core/agent.py`. Additionally, the prompt instructs the agent to analyze previous failure traces to prevent repeating identical erroneous tool calls.

**Q3: How are security risks mitigated when running shell commands?**
> *Answer:* In `core/tools.py`, `run_command` contains regex safety filters that reject destructive commands (e.g. `rm -rf /`, fork bombs, disk formatting). Commands execute with strict timeouts (default 30s) to prevent runaway processes.

**Q4: Can this agent run without internet access?**
> *Answer:* Yes. Through our multi-provider architecture, the user can toggle to **Offline Mode (Ollama)** with one click, utilizing local open-source models like `qwen2.5-coder:7b` without internet or API keys.
# AI-AGENT
