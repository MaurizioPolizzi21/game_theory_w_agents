# Game Theory with AI Agents

A computational implementation of the classic Prisoner's Dilemma using AI agents powered by LangGraph and Large Language Models.

## Overview

This project explores game theory concepts through the lens of artificial intelligence by simulating the famous Prisoner's Dilemma scenario. Two AI agents make strategic decisions (cooperate or defect) in an iterative game environment, allowing us to study emergent behaviors, strategic thinking, and decision-making patterns in multi-agent systems.

## The Prisoner's Dilemma

The Prisoner's Dilemma is a fundamental concept in game theory that illustrates why rational individuals might not cooperate even when it's in their mutual interest. In this scenario:

- **Two players** must simultaneously choose to either **cooperate** or **defect**
- **Mutual cooperation** yields moderate rewards for both
- **Mutual defection** results in poor outcomes for both
- **One defects, one cooperates**: the defector gets the highest reward, the cooperator gets the worst outcome

### Payoff Matrix
```
                Player 2
              C       D
Player 1  C  (3,3)   (0,5)
          D  (5,0)   (1,1)
```

## Project Architecture

This implementation uses **LangGraph** to create a sophisticated multi-agent system where:

### Core Components

1. **AI Agents**: Two distinct agents with different strategic approaches
   - Each agent uses a Large Language Model (LLM) for decision-making
   - Agents maintain memory of previous interactions
   - Strategic prompts guide agent behavior (currently under development)

2. **Game Engine**: 
   - Sequential execution with controlled iteration loops
   - Each agent can make up to 5 decisions per game session
   - State management tracks choices and counters for both agents

3. **LangGraph Framework**:
   - **Subgraph**: Manages individual agent interactions and game flow
   - **Main Graph**: Orchestrates the overall game session
   - **State Management**: Tracks agent choices, counters, and game history

### Technical Implementation

- **AI Framework**: LangGraph for multi-agent orchestration
- **LLM**: Ollama with Mistral model for agent decision-making
- **Memory**: In-memory checkpointing for game session persistence

## File Structure

```
├── main.py                    # Main game implementation
├── prompt.py                  # Agent prompt definitions (under development)
├── graph_visualization.ipynb  # Jupyter notebook for graph visualization
└── README.md                  # This file
```

## Key Features

- **Iterative Gameplay**: Agents play multiple rounds, building strategic understanding
- **Memory Persistence**: Game state is maintained across interactions
- **Configurable Agents**: Different prompting strategies can be tested
- **Visual Graph Representation**: LangGraph provides clear visualization of agent interactions
- **Extensible Design**: Framework allows for easy modification of game rules and agent behaviors

## Current Development Status

🚧 **Work in Progress** 🚧

This project is actively under development. Current focus areas include:

- **Agent Prompt Engineering**: Refining the strategic prompts that guide agent decision-making
- **Behavioral Analysis**: Studying patterns in agent choices and strategies
- **Game Variations**: Exploring different payoff matrices and game rules
- **Performance Metrics**: Implementing analysis tools for strategy effectiveness

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
- Ollama with Mistral model
- Required Python packages (see imports in main.py)

### Running the Game
```bash
python main.py
```

### Visualization
Open `graph_visualization.ipynb` in Jupyter to see the LangGraph structure and game flow.
