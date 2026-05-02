# Kickstart 🚀

**Kickstart** is an AI-powered multi-agent system that takes a plain-English description of a software project and autonomously generates a fully structured, working codebase for it.

---

## How It Works

Kickstart uses a three-stage **LangGraph** pipeline where each stage is handled by a specialized AI agent:

```
User Prompt ──► Planner ──► Architect ──► Coder ──► Generated Project
```

### 1. 🗂️ Planner Agent
Takes the user's natural language request and produces a structured project plan, including:
- Application name & description
- Tech stack
- Feature list
- List of files to be created (with their purpose)

### 2. 🏛️ Architect Agent
Takes the project plan and breaks it down into granular, ordered **implementation tasks** — one or more tasks per file — each with:
- The target file path
- A detailed description of exactly what to implement (functions, classes, imports, data flow)

### 3. 💻 Coder Agent
Iterates through each implementation task and writes the actual code. For each step it:
1. Reads the existing file content (if any)
2. Calls the LLM to produce the new file content
3. Safely writes the result to disk inside `generated_project/`
4. Advances to the next task, looping until all steps are complete

---

## Architecture

```
agent/
├── graph.py      # LangGraph state machine wiring the three agents together
├── prompts.py    # System & user prompt templates for each agent
├── states.py     # Pydantic data models (Plan, TaskPlan, CoderState, …)
└── tools.py      # Safe file-system tools (read_file, write_file, list_files, run_cmd)
main.py           # Entry point (placeholder / PyCharm default)
generated_project/  # Output directory — all generated code lands here
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | `openai/gpt-oss-120b` (served via **Groq**) |
| Agent orchestration | **LangGraph** |
| LLM integration | **LangChain** (`langchain-groq`) |
| Data validation | **Pydantic v2** |
| Environment config | `python-dotenv` |
| Python version | Managed via `.python-version` / `uv` |

---

## Getting Started

### Prerequisites
- Python 3.11+
- A **[Groq API key](https://console.groq.com/)**

### Installation

```bash
# Clone the repo
git clone https://github.com/Saransh2412/Kickstart.git
cd Kickstart

# Install dependencies (using uv)
pip install uv
uv sync
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Running

Edit the `user_prompt` variable in `agent/graph.py` to describe the project you want to build:

```python
user_prompt = "create a 2 player uno game"
```

Then run:

```bash
python -m agent.graph
```

The generated project files will appear inside the `generated_project/` directory.

---

## Example

**Input prompt:**
```
create a 2 player uno game
```

**What Kickstart does:**
1. **Planner** produces a plan: game loop, deck logic, player turn management, win detection, CLI interface.
2. **Architect** breaks that into tasks: `deck.py` → `game.py` → `player.py` → `main.py`, each with precise implementation instructions.
3. **Coder** writes each file in order, reading previous files to stay consistent, until the full project is written.

---

## Tools Available to the Coder Agent

| Tool | Description |
|---|---|
| `write_file(path, content)` | Writes content to a file inside `generated_project/` |
| `read_file(path)` | Reads an existing file (returns empty string if not found) |
| `list_files(directory)` | Lists all files in a directory |
| `get_current_directory()` | Returns the project root path |
| `run_cmd(cmd, cwd, timeout)` | Runs a shell command inside the project root |

All file operations are sandboxed to the `generated_project/` directory — writes outside that root are rejected.

---

## Project Structure (Generated Output)

All output lands in:

```
generated_project/
└── ... (files generated based on your prompt)
```

---

## License

This project is open source. See [LICENSE](LICENSE) for details.
