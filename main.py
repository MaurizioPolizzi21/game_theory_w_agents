from langgraph.prebuilt import create_react_agent
from langchain_ollama.llms import OllamaLLM
from langchain_core.tools import tool
from langgraph.graph import START, END, StateGraph, MessagesState
from typing import Annotated, TypedDict, Union
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.checkpoint.memory import InMemorySaver
from prompt import game_prompt, good_player_prompt, bad_player_prompt
import json
from operator import add

# model setup
model = "mistral:latest"
llm = OllamaLLM(model=model)

#memory setup
checkpointer = InMemorySaver()
config = { "configurable": { "thread_id": "1" } }

# child state setup
class SubgraphState(TypedDict):
    agent_1_prompt: str
    agent_1_choice: list[str]
    agent_2_prompt: str
    agent_2_choice: list[str]


def Agent1(state: SubgraphState):
    messages = llm.invoke(state["agent_1_prompt"])
    if isinstance(messages, str):
        response= json.loads(messages)
    return {"agent_1_choice": state["agent_1_choice"] + [response["agent_choice"]]}

def Agent2(state: SubgraphState):
    messages = llm.invoke(state["agent_2_prompt"])
    if isinstance(messages, str):
        response= json.loads(messages)
    return {"agent_2_choice": state["agent_2_choice"] + [response["agent_choice"]]}

subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node("Agent1", Agent1)
subgraph_builder.add_node("Agent2", Agent2)
subgraph_builder.add_edge(START, "Agent1")
subgraph_builder.add_edge("Agent1", "Agent2")
subgraph_builder.add_edge("Agent2", END)
subgraph = subgraph_builder.compile()

# parent state setup
class ParentState(MessagesState):
    agent_1_choice_parent : list[str]
    agent_2_choice_parent : list[str]
    

def transform(state: ParentState):
    response = subgraph.invoke({"agent_1_choice": state["agent_1_choice_parent"], "agent_2_choice": state["agent_2_choice_parent"], "agent_1_prompt": good_player_prompt, "agent_2_prompt": bad_player_prompt}, config=config)
    return {"agent_1_choice_parent": response["agent_1_choice"], "agent_2_choice_parent": response["agent_2_choice"]}  



graph_builder = StateGraph(ParentState)
graph_builder.add_node("transform", transform)
graph_builder.add_edge(START, "transform")
graph_builder.add_edge("transform", END)
graph = graph_builder.compile(checkpointer=checkpointer)


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}], "agent_1_choice_parent": [], "agent_2_choice_parent": []},subgraphs=True,stream_mode="updates", config=config):
        graph.get_state(config=config)
        print(event)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if user_input.lower() in ["let's play", "let's play!"]:
            stream_graph_updates(user_input=game_prompt)
    except KeyboardInterrupt:
        print("Goodbye!!")
        break