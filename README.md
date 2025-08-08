# Game Theory with AI Agents

A computational implementation of the classic Prisoner's Dilemma using AI agents powered by LangGraph and Ollama LLM.

## Overview

This project simulates the famous Prisoner's Dilemma using two AI agents with distinct strategic personalities. The implementation uses LangGraph for multi-agent orchestration and Ollama's Mistral model for decision-making, creating an environment where agents can interact over multiple rounds while maintaining memory of previous choices.

## The Prisoner's Dilemma

In this implementation, two agents are arrested and must choose between **COOPERATE** (stay silent) or **DEFECT** (betray the other) without communication.

### Payoff Structure
- **Both COOPERATE**: Both get -1 (moderate sentence)
- **Both DEFECT**: Both get -3 (harsh sentence)
- **One COOPERATES, one DEFECTS**: Cooperator gets -2 (heavy sentence), Defector gets 0 (goes free)

### Payoff Matrix
```
                Agent 2
              C       D
Agent 1   C  (-1,-1) (-2,0)
          D  (0,-2)  (-3,-3)
```

## Project Architecture

The system uses a **two-tier LangGraph architecture** with distinct state management for game orchestration and agent interactions.

### Core Components

#### 1. Agent Personalities
- **Good Player Agent**: Strategic, rational player who considers mutual benefit and long-term outcomes
- **Bad Player Agent**: Selfish, short-sighted player who always seeks individual advantage
- Both agents receive opponent's choice history but **not the opponent's prompt/strategy**

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
  - `get_payoff()`: Calculates total payoffs using the payoff agent
- **Flow**: Linear execution from subgraph → payoff calculation

#### 3. Technical Stack
- **LLM**: Ollama Mistral (temperature: 0.4) for consistent decision-making
- **Memory**: InMemorySaver with thread-based checkpointing
- **Output Format**: JSON-structured agent responses
- **Payoff Agent**: Dedicated LLM agent for calculating game outcomes

## File Structure

```
├── main.py                    # Complete game implementation with dual-graph architecture
├── prompt.py                  # Agent prompt definitions (good_player, bad_player, payoff_agent)
├── graph_visualization.ipynb  # Jupyter notebook for graph visualization
└── README.md                  # This documentation
```

## Key Features

- **Dual Personality Agents**: Contrasting strategic approaches (rational vs. selfish)
- **5-Round Game Sessions**: Fixed iteration count with automatic termination
- **Choice History Tracking**: Agents see opponent's previous decisions for strategic adaptation
- **Automated Payoff Calculation**: Dedicated LLM agent computes total scores
- **Prompt Masking**: Agents know opponent choices but not opponent strategies
- **Memory Persistence**: InMemorySaver maintains game state throughout execution
- **JSON-Structured Communication**: Standardized agent response format

## Implementation Details

### Game Flow
1. **Initialization**: Set up dual-graph architecture with agent prompts
2. **Subgraph Execution**: Agents alternate decisions for 5 rounds each
3. **Choice Aggregation**: Collect all agent decisions from subgraph
4. **Payoff Calculation**: Process choice pairs through payoff agent
5. **Results Output**: Display final scores and game summary

### Agent Decision Process
- Each agent receives their base prompt + opponent's choice history
- LLM processes strategic context and returns JSON-formatted choice
- Choices are validated and added to the running game state
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
