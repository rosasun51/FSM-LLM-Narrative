# FSM-LLM Narrative Generation System

A hierarchical narrative game engine that uses Large Language Models (LLMs) to generate branching storylines with scripted and dynamically generated content. This system creates interactive, non-linear storytelling experiences by organizing narrative elements in a hierarchical tree structure.

## Overview

The FSM-LLM Narrative system implements:

1. A hierarchical task structure with three layers of subtasks (initial scenario, complications, resolution)
2. Clear parent-child relationships between subtasks with proper ID formatting (e.g., 1.1, 1.1.1, 1.1.1.1)
3. Integration with LLM services to generate narrative branches and alternative paths
4. Rich visualization tools for exploring narrative structures
5. Configurable constants for easy testing and customization

## Directory Structure

```
Generate_branches/
├── data/
│   ├── generated_chains/      # Generated task chains
│   ├── key_questions/         # Key transitioning questions for narrative flow
│   ├── Scripted_tasks.json    # Task templates
│   └── subtasks/              # Subtask structure examples
├── demo/
│   ├── demo_game.py           # Interactive demo game
│   ├── sample_dialogues.py    # Example dialogue templates
│   └── sample_tasks.py        # Example task definitions
├── game/
│   ├── branch_manager.py      # Manages narrative branches
│   ├── game_manager.py        # Core game management
│   ├── npc.py                 # NPC functionality
│   ├── subtask_chain.py       # Manages subtask sequences
│   └── task_chain.py          # Manages task sequences
├── llm/
│   ├── LLM_integration.py     # LLM API integration
│   └── prompt_templates.py    # Templates for LLM calls
├── models/
│   ├── layer.py               # Layer model
│   ├── state.py               # Game state model
│   ├── subtask.py             # Subtask model
│   └── task.py                # Task model
├── tests/
│   ├── test_game.py           # Game mechanics tests
│   ├── test_llm.py            # LLM integration tests
│   └── test_task.py           # Task model tests
├── utils/
│   ├── config.py              # Configuration settings
│   ├── constants.py           # Centralized constants
│   └── helpers.py             # Utility functions
├── visualization/
│   ├── illustration.ipynb     # Jupyter notebook for visualizations
│   ├── illustration.py        # Visualization tools
│   └── README.md              # Visualization guide
├── main.py                    # Main entry point
└── requirements.txt           # Project dependencies
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/FSM-LLM-Narrative.git
cd FSM-LLM-Narrative
```

2. Create and activate a virtual environment:

```bash
# On macOS/Linux
python -m venv Generate_branches_env
source Generate_branches_env/bin/activate

# On Windows
python -m venv Generate_branches_env
Generate_branches_env\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r Generate_branches/requirements.txt
```

4. Set your OpenAI API key:

```bash
# On macOS/Linux
export OPENAI_API_KEY="your-api-key-here"

# On Windows
set OPENAI_API_KEY="your-api-key-here"
```

5. (Optional) Install additional visualization dependencies:

```bash
# For better hierarchical visualizations
pip install pygraphviz
```

## Usage

### Running the Demo Game

```bash
# Run demo game with default task
python -m Generate_branches.main --demo

# Run with a specific task
python -m Generate_branches.main --demo --task "Beginning"
```

### Generating Visualizations

```bash
# Generate visualizations for all tasks
python -m Generate_branches.main --visualize

# Generate visualization for a specific task
python -m Generate_branches.main --visualize --task "Beginning"

# Generate a single hierarchical structure visualization
python -c "from Generate_branches.visualization.illustration import visualize_task_structure_example; visualize_task_structure_example()"
```

### Creating a Visualization Notebook

```bash
# Create Jupyter notebook for interactive visualization
python -m Generate_branches.main --notebook

# Run the notebook
cd Generate_branches/visualization
jupyter notebook illustration.ipynb
```

### Running Tests

```bash
# Run all tests
python -m Generate_branches.main --test

# Run tests for a specific module
python -m Generate_branches.main --test --module task
python -m Generate_branches.main --test --module llm
python -m Generate_branches.main --test --module game
```

### Debug Mode

```bash
# Enable debug mode for verbose output
python -m Generate_branches.main --debug
```

## Key Features

### Hierarchical Narrative Structure

The system organizes narrative elements in a hierarchical tree structure:

- **Root Task (ID: 1)**: The main narrative task (e.g., "Beginning")
- **Layer 1 (ID: 1.1)**: Initial situation and task parameters
- **Layer 2 (ID: 1.2)**: Complications and challenges
- **Layer 3 (ID: 1.3)**: Resolution and outcomes

Each layer contains:
- One scripted subtask (manually defined)
- Multiple generated subtasks (created by LLM) that serve as alternatives

### Visualization Tools

The system provides three visualization types:

1. **Task Chain Visualization**: Shows the overall structure of a task chain
   ```bash
   python -c "from Generate_branches.visualization.illustration import ChainVisualizer; \
              from Generate_branches.game.branch_manager import BranchManager; \
              branch_manager = BranchManager(); \
              task_chain = branch_manager.generate_task_chain('Beginning'); \
              visualizer = ChainVisualizer(); \
              visualizer.visualize_task_chain(task_chain)"
   ```

2. **Subtask Flow Visualization**: Shows the sequential flow of subtasks
   ```bash
   python -c "from Generate_branches.visualization.illustration import ChainVisualizer; \
              from Generate_branches.game.branch_manager import BranchManager; \
              branch_manager = BranchManager(); \
              task_chain = branch_manager.generate_task_chain('Beginning'); \
              visualizer = ChainVisualizer(); \
              visualizer.visualize_subtask_flow(task_chain.tasks[0])"
   ```

3. **Hierarchical Structure Visualization**: Shows complete parent-child relationships
   ```bash
   python -c "from Generate_branches.visualization.illustration import ChainVisualizer; \
              from Generate_branches.game.branch_manager import BranchManager; \
              branch_manager = BranchManager(); \
              task_chain = branch_manager.generate_task_chain('Beginning'); \
              visualizer = ChainVisualizer(); \
              visualizer.visualize_hierarchical_structure(task_chain.tasks[0])"
   ```

### Centralized Configuration

Key parameters are centralized in `utils/constants.py` for easy modification:

- LLM settings (model, API key, token limits)
- Narrative structure (number of layers, ID formats)
- File paths for data and visualizations
- Debug and testing parameters

## Interactive Demo Features

When running the demo game:

- **help**: Display available commands
- **look**: Examine the current environment
- **tasks**: Show active tasks
- **load [task_name]**: Load a specific task
- **exit/quit**: Exit the demo

## Working with Existing Task Chains

Load and visualize existing task chains with:

```bash
python -c "from Generate_branches.visualization.illustration import ChainVisualizer; \
           from Generate_branches.game.branch_manager import BranchManager; \
           branch_manager = BranchManager(); \
           branch_manager.load_task_chain('beginning_chain'); \
           task_chain = branch_manager.task_chains['beginning_chain']; \
           visualizer = ChainVisualizer(); \
           visualizer.visualize_hierarchical_structure(task_chain.tasks[0])"
```

## Available Tasks

The system includes several example tasks:

- **Beginning**: Initial meeting with Ronan
- **Meet with Meredith Stout**: Meeting with Meredith
- **Picking Up Goods**: Retrieving the goods
- **Clear Virus**: Dealing with a virus at the hacker shop
- **Contact Meredith Stout**: Making initial contact with Meredith

## Customization

### Adding New Tasks

1. Create a new task definition in `data/Scripted_tasks.json`:
   ```json
   {
     "name": "Your Task Name",
     "location": "location_id",
     "trigger_conditions": {
       "time_condition": "Chapter == 1 and GameDay == 1"
     },
     "environment": "Description of the environment...",
     "interactive_npc": [
       {
         "name": "NPC Name",
         "goal": "NPC goal description"
       }
     ],
     "scene_end_state_reference": {
       "end_condition1": "Condition for ending the scene"
     }
   }
   ```

2. The system will automatically generate:
   - Key transitioning questions for narrative flow
   - Scripted subtasks for each layer
   - Alternative generated subtasks

### Modifying Constants

Edit `utils/constants.py` to change:

- Number of layers (`NUM_LAYERS`)
- ID formats (`LAYER_1_ID_FORMAT`, etc.)
- LLM parameters (`LLM_MODEL`, `LLM_MAX_TOKENS`, etc.)
- Number of alternatives (`DEFAULT_NUM_ALTERNATIVES`)

## Troubleshooting

- **ImportError: No module named 'Generate_branches'**
  - Make sure you're running commands from the project root directory
  - Check that your Python path includes the project directory

- **Missing API Key**
  - Set the `LLM_API_KEY` in `utils/constants.py` or as an environment variable

- **Visualization Issues**
  - Install optional dependencies: `pip install pygraphviz networkx matplotlib ipython`
  - Ensure the visualization directory exists: `mkdir -p Generate_branches/visualization`

- **LLM Generation Errors**
  - Check your API key and internet connection
  - Verify the LLM model is available and correctly set in `constants.py`

## Development Guidelines

When extending the project:

1. Maintain the hierarchical ID structure for subtasks
2. Use constants from `constants.py` instead of hardcoded values
3. Add tests for new functionality in the `tests/` directory
4. Document new features in the README.md

## License

[MIT License](LICENSE)

## Contact

For questions or suggestions, please open an issue on GitHub.

---

Happy storytelling! 