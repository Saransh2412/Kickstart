from dotenv import load_dotenv
load_dotenv(".env")
# from langchain.globals import set_debug , set_verbose

from requests_toolbelt import user_agent
from agent.prompts import *
from agent.states import *
from agent.tools import *
from langgraph.constants import END
from langgraph.graph import StateGraph
load_dotenv()
from langchain_groq import ChatGroq

llm=ChatGroq(model="openai/gpt-oss-120b")
# set_debug(True)
# set_verbose(True)
user_prompt = "create a 2 player uno game"
def planner_agent(state:dict)->dict:
    user_prompt=state["user_prompt"]


    resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    return {"plan":resp}

state={
    "user_prompt":user_prompt,
    "plan":"",
}

# breakpoint()
# print(resp)
def architect_agent(state:dict)->dict:
    plan:Plan =state["plan"]
    resp=llm.with_structured_output(TaskPlan).invoke(architect_prompt(plan))
    if resp is None:
        raise ValueError("Architect error")
    resp.plan=plan
    return {"task_plan":resp}


def coder_agent(state: dict) -> dict:
    """
    Safe ReAct-style coder agent.
    Replaces create_react_agent for LangChain 1.2.2
    """

    # --- 1. Initialize coder state ---
    coder_state: CoderState = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(
            task_plan=state["task_plan"],
            current_step_idx=0
        )

    steps = coder_state.task_plan.implementation_steps

    # --- 2. Stop condition ---
    if coder_state.current_step_idx >= len(steps):
        return {
            "coder_state": coder_state,
            "status": "DONE"
        }

    current_task = steps[coder_state.current_step_idx]

    # --- 3. Read existing file content ---
    existing_content = read_file.run(current_task.filepath)

    # --- 4. Build prompts ---
    system_prompt = coder_system_prompt()

    user_prompt = f"""
Task:
{current_task.task_description}

File:
{current_task.filepath}

Existing content:
{existing_content}

Rules:
- DO NOT use native tool calls.
- Output ONLY plain text.
- If you need to write a file, output EXACTLY in this format:
  write_file("path", "content")
- Do not explain anything.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # --- 5. Call LLM ---
    resp = llm.invoke(
        messages,
        tool_choice="none"  # force plain text output
    )
    output = resp.content.strip()

    # --- 6. SAFE tool execution (NO eval/exec) ---
    if output.startswith("write_file"):
        _safe_execute_write(output)

    elif output.startswith("read_file"):
        _safe_execute_read(output)

    else:
        raise ValueError(
            f"Coder produced invalid action:\n{output}"
        )

    # --- 7. Move to next step ---
    coder_state.current_step_idx += 1

    return {"coder_state": coder_state}

import re

def _safe_execute_write(text: str):

    match = re.match(
        r'write_file\(\s*"([^"]+)"\s*,\s*"(.*)"\s*\)$',
        text,
        re.DOTALL
    )
    if not match:
        raise ValueError(f"Invalid write_file syntax:\n{text}")

    path, content = match.groups()
    content = content.encode().decode("unicode_escape")

    write_file.run({
        "path": path,
        "content": content
    })


def _safe_execute_read(text: str):
    """
    Safely executes read_file("path")
    """
    match = re.match(
        r'read_file\(\s*"([^"]+)"\s*\)\s*$',
        text
    )
    if not match:
        raise ValueError(f"Invalid read_file syntax:\n{text}")

    path = match.group(1)
    return read_file.run(path)

def coder_router(state: dict):
    coder_state = state.get("coder_state")
    if coder_state and coder_state.current_step_idx >= len(
        coder_state.task_plan.implementation_steps
    ):
        return END
    return "Coder"


graph = StateGraph(dict)
graph.add_node("planner",planner_agent)
graph.add_node("Architect",architect_agent)
graph.add_node("Coder",coder_agent)
graph.add_edge("planner","Architect")
graph.add_edge("Architect", "Coder")
graph.add_conditional_edges(
    "Coder",
    coder_router,
    {
        "Coder": "Coder",
        END: END
    }
)
graph.set_entry_point("planner")

agent=graph.compile()

result =agent.invoke({"user_prompt":user_prompt})
print(result)