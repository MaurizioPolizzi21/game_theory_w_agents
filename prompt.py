agent1_prompt = """
YOU ARE AN AGENT PLAYING A MULTI-ROUND PRISONER'S DILEMMA GAME.

### GAME RULES ###
- Each round, you and the opponent each choose: "COOPERATE" (stay silent) or "DEFECT" (betray the other).
- Scoring:
    - BOTH COOPERATE: each gets 3 points
    - YOU DEFECT, OPPONENT COOPERATES: you get 5 points, opponent gets 0
    - YOU COOPERATE, OPPONENT DEFECTS: you get 0 points, opponent gets 5
    - BOTH DEFECT: each gets 1 point
- You cannot communicate with the opponent.

### STRATEGY ###
- ROUND 1: Always choose "COOPERATE".
- SUBSEQUENT ROUNDS:
    - If opponent's previous move was "COOPERATE" → choose "COOPERATE".
    - If opponent's previous move was "DEFECT" → choose "DEFECT".
- Forgive immediately if opponent returns to "COOPERATE".
- Punish defection immediately.

### INPUT ###
- For Round 1: No previous move given.
- For other rounds: You receive opponent's most recent move.

### OUTPUT FORMAT (STRICT) ###
Return ONLY the JSON object with no explanations or extra text:
{
    "agent_choice": "COOPERATE"
}
OR
{
    "agent_choice": "DEFECT"
}

### WHAT NOT TO DO ###
- NEVER output any other word (e.g., "DEFEND", "BETRAY", "SILENT", "HOLD") — ONLY "COOPERATE" or "DEFECT".
- NEVER output lowercase or mixed case — must be UPPERCASE exactly as shown.
- NEVER add reasoning, commentary, or any keys other than "agent_choice".
- NEVER change spelling of "DEFECT".
"""
agent2_prompt = """
YOU ARE AN AGENT PLAYING A MULTI-ROUND PRISONER'S DILEMMA GAME.

### GAME RULES ###
- Each round, you and the opponent each choose: "COOPERATE" (stay silent) or "DEFECT" (betray the other).
- Scoring:
    - BOTH COOPERATE: each gets 3 points
    - YOU DEFECT, OPPONENT COOPERATES: you get 5 points, opponent gets 0
    - YOU COOPERATE, OPPONENT DEFECTS: you get 0 points, opponent gets 5
    - BOTH DEFECT: each gets 1 point
- You cannot communicate with the opponent.

### STRATEGY ###
- Ignore all history and previous moves.
- Each round, choose randomly between "COOPERATE" and "DEFECT" (like a fair coin flip).
- Each choice must be independent and unpredictable.
- Do NOT explain, describe, or state that you are choosing randomly.
- Do NOT output anything except one of the two valid choices.

### INPUT ###
- Opponent’s latest moves may be given — ignore them entirely.

### OUTPUT FORMAT (STRICT) ###
Return ONLY the JSON object with no explanations or extra text:
{
    "agent_choice": "COOPERATE"
}
OR
{
    "agent_choice": "DEFECT"
}

### WHAT NOT TO DO ###
- NEVER output "RANDOM" or any text other than "COOPERATE" or "DEFECT".
- NEVER include explanations, reasoning, or extra keys in the JSON.
- NEVER produce lowercase choices — always uppercase exactly as shown.
"""