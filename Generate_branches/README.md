# LLM Narrative Game Engine

A narrative game engine that uses Large Language Models (LLMs) to generate branching storylines. This system creates dynamic, interactive storytelling experiences with scripted and generated narrative paths.

## Overview

This project implements a narrative game system that:

1. Loads scripted task templates from JSON data
2. Uses LLM calls to generate scripted and alternative subtasks
3. Creates branching narrative paths based on player choices
4. Visualizes task chains and narrative structures
5. Provides an interactive demo experience

The system is designed to work with OpenAI's GPT models, specifically gpt-4o-mini.

## Directory Structure

```
Generate_branches/
├── __init__.py
├── data/
│   ├── Scripted_tasks.json           # Task templates
│   └── generated_chains/             # Generated task chains
├── demo/
│   ├── __init__.py
│   └── demo_game.py                  # Interactive demo game
├── game/
│   ├── __init__.py
│   ├── branch_manager.py             # Manages narrative branches
│   ├── game_manager.py               # Core game management
│   ├── npc.py                        # NPC functionality
│   ├── subtask_chain.py              # Manages subtask sequences
│   └── task_chain.py                 # Manages task sequences
├── llm/
│   ├── __init__.py
│   ├── LLM_integration.py            # LLM API integration
│   └── prompt_templates.py           # Templates for LLM calls
├── models/
│   ├── __init__.py
│   ├── layer.py                      # Layer model
│   ├── state.py                      # Game state model
│   ├── subtask.py                    # Subtask model
│   └── task.py                       # Task model
├── tests/
│   ├── __init__.py
│   ├── test_game.py                  # Game mechanics tests
│   ├── test_llm.py                   # LLM integration tests
│   └── test_task.py                  # Task model tests
├── utils/
│   ├── __init__.py
│   ├── config.py                     # Configuration settings
│   └── helpers.py                    # Utility functions
├── visualization/
│   ├── __init__.py
│   ├── illustration.ipynb            # Jupyter notebook for visualizations
│   └── illustration.py               # Visualization tools
├── main.py                           # Main entry point
└── requirements.txt                  # Project dependencies
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r Generate_branches/requirements.txt
```

3. Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Running the Demo Game

```bash
python -m Generate_branches.main --demo
```

You can also specify a particular task to start with:

```bash
python -m Generate_branches.demo.demo_game beginning
```

Available tasks:
- `beginning`: Initial meeting with Ronan
- `meet_meredith`: Meeting with Meredith Stout
- `pickup_goods`: Picking up goods at the factory
- `clear_virus`: Clearing a virus at the hacker shop
- `contact_meredith`: Making initial contact with Meredith

### Running Tests

```bash
python -m Generate_branches.main --test
```

To run specific test modules:

```bash
python -m Generate_branches.main --test --test-module task
python -m Generate_branches.main --test --test-module llm
python -m Generate_branches.main --test --test-module game
```

### Generating Visualizations

You can visualize the task chains and narrative structures using the provided Jupyter notebook:

```bash
cd Generate_branches/visualization
jupyter notebook illustration.ipynb
```

## How It Works

### Task Generation Process

1. **Load Scripted Tasks**: The system loads task templates from `Scripted_tasks.json`
2. **Generate Key Questions**: The LLM generates transitioning questions for each task
3. **Create Scripted Subtasks**: Main path subtasks are generated for each question
4. **Generate Alternative Branches**: The LLM creates alternative narrative branches
5. **Assemble Task Chain**: All components are assembled into a complete task chain

### Playing the Game

In the interactive demo:
- Navigate through the narrative by selecting options
- Use commands like `help`, `look`, and `tasks` to interact with the game
- Switch between different tasks using the `load [task_id]` command

## Customization

### Adding New Tasks

1. Add your task definition to `data/Scripted_tasks.json`
2. Update the `DEMO_TASKS` dictionary in `demo_game.py`
3. Add relevant NPCs and locations

### Modifying LLM Prompts

Edit the prompt templates in `llm/LLM_integration.py` to change how narrative content is generated.

## Troubleshooting

- **API Key Issues**: Make sure your OpenAI API key is properly set
- **Import Errors**: Ensure you're running from the project root directory
- **Visualization Problems**: Check that networkx, matplotlib, and IPython are installed

## Future Improvements

Potential areas for enhancement:
1. Add persistence for game state (save/load functionality)
2. Implement more sophisticated NPC behavior models
3. Enhance the visualization with interactive web-based graphs
4. Add more complex narrative structures with conditional branches

## Contact

For questions or suggestions, please open an issue on GitHub.

---

Happy storytelling! 