prompt = """
You are an agent participating in a single round of the Prisoner's Dilemma game.

Game rules:
- You and another agent have been arrested for a crime. You cannot communicate with each other.
- Each of you must independently choose one of two actions: COOPERATE (stay silent) or DEFECT (betray the other).
- The outcomes are as follows:
    - If you both COOPERATE: both receive a moderate sentence (1)
    - If you DEFECT and the other COOPERATES: you go free (0), the other receives a heavy sentence (2).
    - If you COOPERATE and the other DEFECTS: you receive a heavy sentence (2), the other goes free (0).
    - If you both DEFECT: both receive a harsh sentence (3).

Your task:
- Decide whether to COOPERATE or DEFECT.
- Remember, this is a one-time decision (no future rounds).

***IMPORTANT***
- the output must be in json format:
{
    "agent_choice": "COOPERATE" or "DEFECT" ,
}
"""