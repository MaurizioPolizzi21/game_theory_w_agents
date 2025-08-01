from langgraph.prebuilt import create_react_agent
from langchain_ollama.llms import OllamaLLM
from langgraph.graph import START, END, StateGraph, MessagesState
from typing import Annotated, TypedDict, Union
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.checkpoint.memory import MemorySaver
from prompt import prompt
import json
from operator import add

model = "mistral:latest"
llm = OllamaLLM(model=model)


class State(MessagesState):
    agent_choice : list[str]

graph_builder = StateGraph(State)


def Agent1(state: State):
    messages = llm.invoke(state["messages"])
    if isinstance(messages, str):
        response= json.loads(messages)
    return {"agent_choice": state["agent_choice"] + [response["agent_choice"]]}

def Agent2(state: State):
    messages = llm.invoke(state["messages"])
    if isinstance(messages, str):
        response= json.loads(messages)
    return {"agent_choice": state["agent_choice"] + [response["agent_choice"]]}

graph_builder.add_node("Agent1", Agent1)
graph_builder.add_node("Agent2", Agent2)
graph_builder.add_edge(START, "Agent1")
graph_builder.add_edge("Agent1", "Agent2")
graph_builder.add_edge("Agent2", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}], "agent_choice": []}):
        for value in event.values():
            print("Agents choices:", value["agent_choice"])


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