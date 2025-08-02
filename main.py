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
    agent_1_choice : list[str]
    agent_2_choice : list[str]
    agent_1_count : int
    agent_2_count : int
    

graph_builder = StateGraph(State)


def Agent1(state: State):
    messages = llm.invoke(state["messages"])
    if isinstance(messages, str):
        response= json.loads(messages)
    return {"agent_1_choice": state["agent_1_choice"] + [response["agent_choice"]]}

def Agent2(state: State):
    messages = llm.invoke(state["messages"])
    if isinstance(messages, str):
        response= json.loads(messages)
    return {"agent_2_choice": state["agent_2_choice"] + [response["agent_choice"]]}

def count(state: State):
    if state["agent_1_choice"][-1] == "COOPERATE" and state["agent_2_choice"][-1] == "COOPERATE":
        return {"agent_1_count": state["agent_1_count"] + 1, "agent_2_count": state["agent_2_count"] + 1}
    if state["agent_1_choice"][-1] == "DEFECT" and state["agent_2_choice"][-1] == "COOPERATE":
        return {"agent_1_count": state["agent_1_count"] + 2, "agent_2_count": state["agent_2_count"] + 0}
    if state["agent_1_choice"][-1] == "COOPERATE" and state["agent_2_choice"][-1] == "DEFECT":
        return {"agent_1_count": state["agent_1_count"] + 0, "agent_2_count": state["agent_2_count"] + 2}
    if state["agent_1_choice"][-1] == "DEFECT" and state["agent_2_choice"][-1] == "DEFECT":
        return {"agent_1_count": state["agent_1_count"] + 3, "agent_2_count": state["agent_2_count"] + 3}
    

graph_builder.add_node("Agent1", Agent1)
graph_builder.add_node("Agent2", Agent2)
graph_builder.add_node("Count", count)
graph_builder.add_edge(START, "Agent1")
graph_builder.add_edge("Agent1", "Agent2")
graph_builder.add_edge("Agent2", "Count")
graph_builder.add_edge("Count", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}], "agent_1_choice": [], "agent_2_choice": [], "agent_1_count": 0, "agent_2_count": 0}):
        for value in event.values():
            print("Agents choices:", value)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if user_input.lower() in ["let's play", "let's play!"]:
            stream_graph_updates(user_input=prompt)
    except KeyboardInterrupt:
        print("Goodbye!!")
        break