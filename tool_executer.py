from typing import List
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

# Initialize Tavily search tool
search = TavilySearch(max_results=2)

def execute_tools(state: dict) -> dict:
    """Execute tools based on the last message's tool calls."""
    messages = state["messages"]
    tool_invocation = messages[-1]
    
    # Get tool calls from the last message
    if hasattr(tool_invocation, 'tool_calls') and tool_invocation.tool_calls:
        tool_calls = tool_invocation.tool_calls
        
        # Execute each tool call
        for tool_call in tool_calls:
            if "search" in tool_call.get("name", "").lower():
                # Execute search with queries from args
                queries = tool_call["args"].get("search_queries", [])
                results = []
                for query in queries:
                    result = search.invoke({"query": query})
                    results.extend(result)
                
                # Create tool message with result
                tool_message = ToolMessage(
                    content=str(results),
                    tool_call_id=tool_call["id"]
                )
                messages.append(tool_message)
    
    return {"messages": messages}