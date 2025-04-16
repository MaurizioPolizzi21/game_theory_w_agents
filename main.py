import uuid
import re
from operator import add
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph, START, MessagesState
from langgraph.types import Command
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
import subprocess



games_payoff = """
### PAYOFF MATRIX ###

- Both cooperate → 3 points each  
- One cooperate, one defects → You: 0, User: 5  
- One defects, one cooperates → You: 5, User: 0  
- Both defect → 1 point each  
"""

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
- ONLY OUTPUT: I cooperate or I defect (NO OTHER OUTPUT ALLOWED) <----- VERY VERY IMPORTANT!!!!
- No extra text, no explanation, just one of the two responses
- I do not want to read your thought process, just one of the two responses"""

def normalize(move: str) -> str:
    move = move.strip().lower()
    move = re.sub(r'[^\w\s]', '', move)  # Remove punctuation
    if "defect" in move:
        return "defect"
    elif "cooperate" in move:
        return "cooperate"
    else:
        return "unknown"

def verify_score(history: list[str]) -> tuple[int, int]:
    good_score = 0
    bad_score = 0
    for i in range(0, len(history), 2):
        good = normalize(history[i].split(":", 1)[1])
        bad = normalize(history[i+1].split(":", 1)[1])
        
        if good == "cooperate" and bad == "cooperate":
            good_score += 3
            bad_score += 3
        elif good == "cooperate" and bad == "defect":
            good_score += 0
            bad_score += 5
        elif good == "defect" and bad == "cooperate":
            good_score += 5
            bad_score += 0
        elif good == "defect" and bad == "defect":
            good_score += 1
            bad_score += 1
        else:
            print(f"⚠️ Could not interpret moves:\nGood: {good}\nBad: {bad}")
    
    return good_score, bad_score



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

MAX_ROUNDS = 30


class OverallState(TypedDict):
    history: Annotated[list[str], add]
    round: Annotated[float, add]
    last_good: str
    last_bad: str
    agent_good_score: Annotated[int, add]
    agent_bad_score: Annotated[int, add]


# Define the LangGraph node
def good_agent(state: OverallState)-> Command[Literal["bad_agent"]]:

    last_moves = f"""You said ->{state["last_good"] if state["last_good"] else "None"} 
    and the other agent said ->{state["last_bad"] if state["last_bad"] else "None"}"""
    prompt_good = f"""{good_agent_prompt}\n{games_payoff}\n. 
    In the last round these were the moves: 
    {last_moves}"""

    content_good = run_mistral_locally(prompt_good)

    next_node = "bad_agent"

    return Command(
        update={"history": [f"Good Agent: {content_good}"],
        "last_good": content_good},
        goto=next_node
    )

def bad_agent(state: OverallState) -> Command[Literal["tracking_tool"]]:


    last_moves = f"""The other agent said ->{state["last_good"] if state["last_good"] else "None"} 
    and you said ->{state["last_bad"] if state["last_bad"] else "None"}"""
    prompt_bad = f"""{bad_agent_prompt}\n{games_payoff}\n. In the last round these were the moves: 
    {last_moves}"""

    content_bad = run_mistral_locally(prompt_bad)
    current_round = state["round"]

    next_node = "good_agent" if current_round < MAX_ROUNDS else "tracking_tool"


    return Command(
        update={"history": [f"Bad Agent: {content_bad}"],
        "round": 1,
        "last_bad": content_bad},
        goto=next_node
    )

def tracking_tool(state: OverallState) -> Command[Literal[END]]:
    good_score, bad_score = verify_score(state["history"])

    return Command(
        update={
            "agent_good_score": good_score,
            "agent_bad_score": bad_score
        },
        goto=END
    )


# Build and compile the LangGraph
graph = StateGraph(OverallState)
graph.add_node("good_agent", good_agent)
graph.add_node("bad_agent", bad_agent)
graph.add_node("tracking_tool", tracking_tool)

# Add transitions
graph.add_edge(START, "good_agent") 
graph.add_conditional_edges

app = graph.compile(checkpointer=memory)

# Run the graph
if __name__ == "__main__":
    thread_id = f"game-session-{uuid.uuid4()}"  
    output = app.invoke({"history": [], "round": 1, "last_good": "", "last_bad": "", "agent_good_score": 0, "agent_bad_score": 0}, config={"recursion_limit": 200,"configurable": {"thread_id": thread_id}})
    print("Interaction History:")
    for i, entry in enumerate(output["history"], start=1):
        print(f"Round {((i + 1) // 2)}:")
        print(entry)
    
    print("Final Scores")
    print(f"Good Agent: {output['agent_good_score']}")
    print(f"Bad Agent: {output['agent_bad_score']}")
