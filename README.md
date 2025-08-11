# Game Theory with AI Agents

A computational implementation of the classic Prisoner's Dilemma using AI agents powered by LangGraph and Ollama LLM.

## Overview

This project simulates the famous Prisoner's Dilemma using two AI agents with distinct strategic personalities. The implementation uses LangGraph for multi-agent orchestration and Ollama's Mistral model for decision-making, creating an environment where agents can interact over multiple rounds while maintaining memory of previous choices.
This projects tries to replicate Robert Axelrod’s Prisoner’s Dilemma tournaments in the late 1970s.

### Key Insights from Axelrod
- Being nice (never defect first) is critical.
- Strategies that were clear and forgiving promoted cooperation and scored better.
- Overly aggressive or overly random strategies lost in the long run.
- Even in a competitive setting, mutual cooperation often beats constant exploitation.

## The Prisoner's Dilemma

In this implementation, two agents are arrested and must choose between **COOPERATE** (stay silent) or **DEFECT** (betray the other) without communication.

### Payoff Structure
- **Both COOPERATE**: Both get 3 points (reward for mutual cooperation)
- **Both DEFECT**: Both get 1 point (punishment for mutual defection)
- **One COOPERATES, one DEFECTS**: Cooperator gets 0 points (sucker's payoff), Defector gets 5 points (temptation payoff)

### Payoff Matrix
```
                Agent 2
              C       D
Agent 1   C  (3,3)   (0,5)
          D  (5,0)   (1,1)
```

This creates the classic Prisoner's Dilemma tension:
- **Temptation (5)** > **Reward (3)** > **Punishment (1)** > **Sucker's payoff (0)**
- Individual incentive to defect, but mutual cooperation yields better outcomes than mutual defection

## Project Architecture

The system uses a **two-tier LangGraph architecture** with distinct state management for game orchestration and agent interactions.

### Core Components

#### 1. Agent Personalities
- **Agent1**: Strategic, rational player who considers mutual benefit and long-term outcomes
- **Agent2**: Random player who always makes random choices
- Both agents receive opponent's **latest and second-latest choices** for enhanced strategic context

#### 2. Dual-Graph Architecture

**Subgraph (Agent Interaction Layer)**:
- **State**: `SubgraphState` tracks individual choices, counters, and prompts
- **Nodes**: `Agent1()` and `Agent2()` functions for decision-making
- **Flow Control**: `should_continue()` manages the 5-round limit per game
- **Loop Logic**: Continues until both agents complete 5 decisions

**Main Graph (Game Orchestration Layer)**:
- **State**: `ParentState` manages overall game data and payoff calculations
- **Nodes**: 
  - `get_subgraph_output()`: Executes the agent subgraph and collects results
  - `get_payoff()`: Calculates total payoffs using direct mathematical computation
- **Flow**: Linear execution from subgraph → payoff calculation

#### 3. Technical Stack
- **LLM**: Ollama Mistral (temperature: 0.5) for balanced decision-making
- **Memory**: InMemorySaver with thread-based checkpointing
- **Output Format**: JSON-structured agent responses
- **Payoff Calculation**: Direct mathematical computation based on choice pairs

## File Structure

```
├── main.py                    # Complete game implementation with dual-graph architecture
├── prompt.py                  # Agent prompt definitions (agent1_prompt, agent2_prompt)
├── graph_visualization.ipynb  # Jupyter notebook for graph visualization
└── README.md                  # This documentation
```

## Key Features

- **Dual Personality Agents**: Contrasting strategic approaches (rational vs. selfish)
- **5-Round Game Sessions**: Fixed iteration count with automatic termination
- **Enhanced Choice History**: Agents receive both latest and second-latest opponent choices for improved strategic adaptation
- **Direct Payoff Calculation**: Mathematical computation of scores based on classic Prisoner's Dilemma payoff matrix
- **Prompt Masking**: Agents know opponent choices but not opponent strategies
- **Memory Persistence**: InMemorySaver maintains game state throughout execution
- **JSON-Structured Communication**: Standardized agent response format

## Implementation Details

### Game Flow
1. **Initialization**: Set up dual-graph architecture with agent prompts
2. **Subgraph Execution**: Agents alternate decisions for 5 rounds each
3. **Choice Aggregation**: Collect all agent decisions from subgraph
4. **Payoff Calculation**: Direct mathematical computation using the payoff matrix
5. **Results Output**: Display final scores and game summary

### Agent Decision Process
- Each agent receives their base prompt + opponent's latest and second-latest choices
- LLM processes enhanced strategic context and returns JSON-formatted choice
- Choices are validated and added to the running game state
- Agents start with counter = 1 and increment after each decision
- Counter increments track progress toward 5-decision limit

## Future Directions

Potential expansions and research directions:

- **Multi-round tournaments** with different agent personalities
- **Learning agents** that adapt strategies based on opponent behavior
- **Population dynamics** with multiple agents competing
- **Alternative game theory scenarios** (Stag Hunt, Chicken Game, etc.)
- **Reinforcement learning** integration for strategy optimization

## Getting Started

### Prerequisites
- Python 3.8+
- Ollama with Mistral model installed and running
- Required Python packages:
  ```bash
  pip install langchain-ollama langgraph
  ```

### Running the Game
```bash
python main.py
```

### Visualization
Open `graph_visualization.ipynb` in Jupyter to see the LangGraph structure and game flow.
