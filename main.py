from langchain_ollama.llms import OllamaLLM
from langgraph.graph import START, END, StateGraph
from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from prompt import good_player_prompt, bad_player_prompt
import json

# model setup
model = "mistral:latest"
llm = OllamaLLM(model=model)

#memory setup
checkpointer = InMemorySaver()
config = { "configurable": { "thread_id": "1" } }

# Individual agent state classes for prompt isolation
class SubgraphStateAgent1(TypedDict):
    agent_1_prompt: str
    agent_1_choice: list[str]
    agent_1_counter: int
    agent_2_choice: list[str]
    agent_2_counter: int

class SubgraphStateAgent2(TypedDict):
    agent_2_prompt: str
    agent_1_choice: list[str]
    agent_1_counter: int
    agent_2_choice: list[str]
    agent_2_counter: int

# Main subgraph state setup
class SubgraphState(TypedDict):
    agent_1_prompt: str
    agent_1_choice: list[str]
    agent_1_counter: int
    agent_2_prompt: str
    agent_2_choice: list[str]
    agent_2_counter: int

# subgraph nodes setup with prompt masking
def Agent1(state: SubgraphState):
    """
    Node Agent1 invokes the LLM with its own prompt. It can see:
    - Its own prompt (agent_1_prompt)
    - Both agents' choices and counters
    - But NOT agent_2_prompt (masked)
    """
    # Create masked state for Agent1, so he can't see agent_2_prompt
    masked_state: SubgraphStateAgent1 = {
        "agent_1_prompt": state["agent_1_prompt"],
        "agent_1_choice": state["agent_1_choice"],
        "agent_1_counter": state["agent_1_counter"],
        "agent_2_choice": state["agent_2_choice"],  # He can see the other agent's choices
        "agent_2_counter": state["agent_2_counter"]
    
    }
    
    messages = llm.invoke(masked_state["agent_1_prompt"])
    if isinstance(messages, str):
        response = json.loads(messages)
    return {"agent_1_choice": state["agent_1_choice"] + [response["agent_choice"]], "agent_1_counter": state["agent_1_counter"] + 1}

def Agent2(state: SubgraphState):
    """
    Node Agent2 invokes the LLM with its own prompt. It can see:
    - Its own prompt (agent_2_prompt)
    - Both agents' choices and counters
    - But NOT agent_1_prompt (masked)
    """
    # Create masked state for Agent2, so he can't see agent_1_prompt
    masked_state: SubgraphStateAgent2 = {
        "agent_2_prompt": state["agent_2_prompt"],
        "agent_1_choice": state["agent_1_choice"],  # He can see the other agent's choices
        "agent_1_counter": state["agent_1_counter"],
        "agent_2_choice": state["agent_2_choice"],
        "agent_2_counter": state["agent_2_counter"]
    }
    
    messages = llm.invoke(masked_state["agent_2_prompt"])
    if isinstance(messages, str):
        response = json.loads(messages)
    return {"agent_2_choice": state["agent_2_choice"] + [response["agent_choice"]], "agent_2_counter": state["agent_2_counter"] + 1}


def should_continue(state: SubgraphState) -> str:
    """This node checks if each agent has made 5 attempts.

    If either agent has fewer than 5 attempts, it returns 'loop' to continue.
    If both agents have made 5 attempts, it returns 'exit' to terminate.
    """
    if state["agent_1_counter"] < 5 or state["agent_2_counter"] < 5:
        return "loop"
    else:
        return "exit"

# subgraph setup
subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node("Agent1", Agent1)
subgraph_builder.add_node("Agent2", Agent2)
# adding parallel edges
subgraph_builder.add_edge(START, "Agent1")
subgraph_builder.add_edge(START, "Agent2")
subgraph_builder.add_conditional_edges("Agent1",
                                should_continue,
                                {
                                    "loop": "Agent1",  # If 'loop', repeat the loop
                                    "exit": END,       # If 'exit', terminate the workflow
                                })
subgraph_builder.add_conditional_edges("Agent2",
                                should_continue,
                                {
                                    "loop": "Agent2",  # If 'loop', repeat the loop
                                    "exit": END,       # If 'exit', terminate the workflow
                                })
subgraph = subgraph_builder.compile(checkpointer=checkpointer)

# graph state setup
class ParentState(TypedDict):
    agent_1_choice_parent : list[str]
    agent_2_choice_parent : list[str]
    
# graph node setup
def transform(state: ParentState):
    response = subgraph.invoke({"agent_1_choice": state["agent_1_choice_parent"], 
    "agent_2_choice": state["agent_2_choice_parent"], "agent_1_prompt": good_player_prompt,
    "agent_2_prompt": bad_player_prompt, "agent_1_counter": 1, "agent_2_counter": 1}, config=config)

    print("Subgraph State History:")
    print("\n")
    print(list(subgraph.get_state_history(config)))
    print("\n")
    print("Subgraph State History End")
    print("\n")
    return {"agent_1_choice_parent": response["agent_1_choice"], "agent_2_choice_parent": response["agent_2_choice"]}  


graph_builder = StateGraph(ParentState)
graph_builder.add_node("transform", transform)
graph_builder.add_edge(START, "transform")
graph_builder.add_edge("transform", END)
graph = graph_builder.compile(checkpointer=checkpointer)

def run_game():
    for event in graph.stream({ 
        "agent_1_choice_parent": [], 
        "agent_2_choice_parent": []
    }, subgraphs=True, config=config):
        print(event)

run_game()