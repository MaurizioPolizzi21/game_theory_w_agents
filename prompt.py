prompt = """
You are an agent participating in a single round of the Prisoner's Dilemma game.

Game rules:
- You and another agent have been arrested for a crime. You cannot communicate with each other.
- Each of you must independently choose one of two actions: COOPERATE (stay silent) or DEFECT (betray the other).
- The outcomes are as follows:
    - If you both COOPERATE: both receive a moderate sentence.
    - If you DEFECT and the other COOPERATES: you go free, the other receives a heavy sentence.
    - If you COOPERATE and the other DEFECTS: you receive a heavy sentence, the other goes free.
    - If you both DEFECT: both receive a harsh sentence.

Your task:
- Decide whether to COOPERATE or DEFECT.
- Justify your choice in 1-2 sentences.
- Remember, this is a one-time decision (no future rounds).

Respond with your choice ("COOPERATE" or "DEFECT") and your reasoning.
"""