import ollama
from langchain.agents import create_react_agent
from langchain_ollama.llms import OllamaLLM
from langgraph.graph import START, END, StateGraph
from typing import Annotated, TypedDict, Union
from langgraph.graph.message import add_messages
from prompt import prompt

# Initialize Ollama client
client = ollama.Client
model = "deepseek-r1:latest"
prompt = prompt
llm = OllamaLLM(model=model)

class State(TypedDict):
    messages : [str]

graph_builder = StateGraph(State)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1])


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break