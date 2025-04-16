import uuid
from operator import add
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph, START, MessagesState
from langgraph.types import Command
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from langchain.storage import InMemoryStore
import subprocess
from langgraph.checkpoint.memory import MemorySaver



games_payoff = """
### PAYOFF MATRIX ###

- Both cooperate → 3 points each  
- You cooperate, user defects → You: 0, User: 5  
- You defect, user cooperates → You: 5, User: 0  
- Both defect → 1 point each  

Based on this, choose: I cooperate or I defect.  
Look at the last round moves if it's not the first to understand your next move based on your instructions."""

good_agent_prompt = """YOU ARE A COOPERATIVE AGENT IN A MULTI-ROUND PRISONER’S DILEMMA GAME.

STRATEGY:
You will have a look a the last interaction you had with your opponent,if it is not the first round, and from this info you will follow this strategy:
- Always start with: I cooperate  
- If opponent defected last round → You defect in this round 
 
IMPORTANT TO REMEMBER ALWAYS:
Your goal is to cooperate if the other agent is cooperative, 
but to defect if the other agent defects. You should learn 
from previous rounds!

RULES:
- Never defect first
- ONLY OUTPUT: I cooperate or I defect (NO OTHER OUTPUT ALLOWED)  
- No extra text, no explanation!!!
- I do not want to read your thought process, just one of the two responses"""

bad_agent_prompt = """YOU ARE A SELFISH AGENT IN A MULTI-ROUND PRISONER’S DILEMMA. YOUR GOAL: MAXIMIZE YOUR POINTS.

STRATEGY:
You will have a look a the last interaction you had with your opponent,if it is not the first round, and from this info you will follow this strategy:
- Usually defect  
- Cooperate only to reset trust or avoid punishment  
- Watch for patterns in the user's retaliation  
- Exploit forgiveness (you know the other opponents tends to forgive)

RULES:
- NEVER explain your thinking!!!  
- ONLY OUTPUT: I cooperate or I defect (NO OTHER OUTPUT ALLOWED)
- No extra text, no explanation, just one of the two responses
- I do not want to read your thought process, just one of the two responses"""



def run_mistral_locally(prompt: str) -> str:
    command = [
        "/Users/mauriziopolizzi/projects/game_theory/llama.cpp/build/bin/llama-cli",
        "-m", "/Users/mauriziopolizzi/Documents/LLM_weights/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        "-p", f"<s>[INST] {prompt} [/INST]",
        "-n", "200",
        "--temp", "0.5",
        "--repeat_penalty", "1.1",
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout

    # Split by '[/INST]' and take what's after it
    if '[/INST]' in output:
        response = output.split('[/INST]', 1)[1]
        # Optional: clean up special tokens like [end of text]
        response = response.replace("[end of text]", "").strip()
        return response

memory = MemorySaver()

MAX_ROUNDS = 4 


class OverallState(TypedDict):
    history: Annotated[list[str], add]
    round: Annotated[float, add]
    last_good: str
    last_bad: str


# Define the LangGraph node
def good_agent(state: OverallState)-> Command[Literal["bad_agent"]]:

    last_moves = f"""You said ->{state["last_good"] if state["last_good"] else "None"} 
    and the other agent said ->{state["last_bad"] if state["last_bad"] else "None"}"""
    prompt_good = f"""{good_agent_prompt}\n{games_payoff}\n. 
    In the last round these were the moves: 
    {last_moves}"""

    content_good = run_mistral_locally(prompt_good)
    current_round = state["round"]

    next_node = "bad_agent"

    return Command(
        update={"history": [f"Good Agent: {content_good}"],
        "last_good": content_good},
        goto=next_node
    )

def bad_agent(state: OverallState) -> Command[Literal["good_agent", END]]:


    last_moves = f"""The other agent said ->{state["last_good"] if state["last_good"] else "None"} 
    and you said ->{state["last_bad"] if state["last_bad"] else "None"}"""
    prompt_bad = f"""{bad_agent_prompt}\n{games_payoff}\n. In the last round these were the moves: 
    {last_moves}"""

    content_bad = run_mistral_locally(prompt_bad)
    current_round = state["round"]

    next_node = END if current_round >= MAX_ROUNDS else "good_agent"

    return Command(
        update={"history": [f"Bad Agent: {content_bad}"],
        "round": 1,
        "last_bad": content_bad},
        goto=next_node
    )



# Build and compile the LangGraph
graph = StateGraph(OverallState)
graph.add_node("good_agent", good_agent)
graph.add_node("bad_agent", bad_agent)

# Add transitions
graph.add_edge(START, "good_agent") 

app = graph.compile(checkpointer=memory)

# Run the graph
if __name__ == "__main__":
    thread_id = f"game-session-{uuid.uuid4()}"  
    output = app.invoke({"history": [], "round": 1, "last_good": "", "last_bad": ""}, config={"recursion_limit": 50,"configurable": {"thread_id": thread_id}})
    print("Interaction History:")
    for entry in output["history"]:
        print(entry)