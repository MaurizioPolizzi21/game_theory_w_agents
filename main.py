from langgraph.prebuilt import create_react_agent
from langchain_ollama.llms import OllamaLLM
from langgraph.graph import START, END, StateGraph
from typing import Annotated, TypedDict, Union
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from prompt import prompt
import json

model = "mistral:latest"
llm = OllamaLLM(model=model)


class State(TypedDict):
    messages : list[str]
    agent_choice : Annotated[list[str],add_messages]

config = {"configurable": {"thread_id": "1"}}
graph_builder = StateGraph(State)


def chatbot(state: State):
    messages = llm.invoke(state["messages"])
    if isinstance(messages, str):
        response= json.loads(messages)
    return {"messages": messages, "agent_choice": response["agent_choice"]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["agent_choice"])


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if user_input.lower() in ["let's play", "let's play!"]:
            stream_graph_updates(user_input=prompt)
    except KeyboardInterrupt:
        print("Goodbye!")
        break