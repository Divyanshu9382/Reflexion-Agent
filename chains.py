import datetime
from vertexai import init

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.openai_tools import PydanticToolsParser

from langchain_google_vertexai import ChatVertexAI

from schemas import AnswerQuestion, ReviseAnswer

init(
    project="my-search-agent-oct2",
    location="us-central1"
)

llm = ChatVertexAI(model="gemini-2.5-flash")
parser = PydanticToolsParser(tools=[AnswerQuestion])

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert researcher.\nCurrent time: {time}"),
        MessagesPlaceholder("messages"),
    ]
).partial(time=lambda: datetime.datetime.now().isoformat())

first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Write a detailed answer in 250 words."
)

revise_instructions = """Revise your answer using search results and critique."""

def first_responder(state):
    result = first_responder_prompt_template | llm.bind_tools(
        tools=[AnswerQuestion], tool_choice="AnswerQuestion"
    )
    output = result.invoke({"messages": state["messages"]})
    return {"messages": [output]}

def revisor(state):
    result = actor_prompt_template.partial(
        first_instruction=revise_instructions
    ) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")
    
    output = result.invoke({"messages": state["messages"]})
    return {"messages": [output]}