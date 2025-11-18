from typing import List, TypedDict
from typing_extensions import Annotated

from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from chains import first_responder, revisor
from tool_executer import execute_tools

MAX_ITERATIONS = 3

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

builder = StateGraph(AgentState)
builder.add_node("draft", first_responder)
builder.add_node("execute_tools", execute_tools)
builder.add_node("revise", revisor)

builder.add_edge("draft", "execute_tools")
builder.add_edge("execute_tools", "revise")

def event_loop(state: AgentState) -> str:
    # Count only assistant messages (each LLM attempt)
    attempts = sum(msg.type == "ai" for msg in state["messages"])
    
    if attempts >= MAX_ITERATIONS:
        return END
    
    # If last message contains no tool calls → no reason to run execute_tools again
    last = state["messages"][-1]
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return END
    
    return "execute_tools"

builder.add_conditional_edges(
    "revise",
    event_loop,
    {END: END, "execute_tools": "execute_tools"},
)

builder.set_entry_point("draft")
graph = builder.compile()

print(graph.get_graph().draw_mermaid())

res = graph.invoke(
    {"messages": ["Write about AI-Powered SOC and startups that raised capital."]}
)

final_msg = res["messages"][-1]

if hasattr(final_msg, "tool_calls") and final_msg.tool_calls:
    tool_call = final_msg.tool_calls[0]
    args = tool_call["args"]
    if "answer" in args:
        print("\nFINAL ANSWER:\n", args["answer"])
    else:
        print("\nTOOL OUTPUT:\n", args)
else:
    print("\nLLM RESPONSE:\n", final_msg.content)