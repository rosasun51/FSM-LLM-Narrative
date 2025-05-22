# FSM-LLM Dynamic Narrative System

A comprehensive interactive narrative game engine that combines hierarchical task management with dynamic narrative processing. This system uses Large Language Models (LLMs) to generate branching storylines with both scripted and dynamically generated content, creating immersive, non-linear storytelling experiences.

## Overview

The FSM-LLM Dynamic Narrative System integrates two core components:

1. **FSM-LLM Narrative Generation**:
   - Hierarchical task structure with three layers of subtasks (initial scenario, complications, resolution)
   - Clear parent-child relationships between subtasks
   - LLM integration for generating narrative branches and alternative paths
   - Rich visualization tools for exploring narrative structures
   - Configurable constants for easy testing and customization
   - Transitioning questions that guide narrative flow across layers

2. **Dynamic Narrative Processing**:
   - Three-stage input processing pipeline based on similarity analysis
   - Dynamic node generation and selection based on player input
   - Layer transition management with position tracking
   - One-directional narrative progression enforcement

## Key Features

### Hierarchical Narrative Structure
- Organizes narrative elements in a hierarchical tree structure
- Supports three layers: initial situation, complications, and resolution
- Each layer contains both scripted and generated content

### Dynamic Content Generation
- Uses LLMs to generate narrative branches and alternative paths
- Dynamically generates new nodes based on player input and context
- Maintains narrative coherence through position tracking

### Interactive Processing
- Analyzes player input using embedding models for similarity scoring
- Implements three-stage processing based on similarity thresholds
- Updates narrative structure based on player choices

### Visualization Tools
- Visualizes task chains and subtask flows
- Displays hierarchical structures with clear node differentiation
- Supports multiple visualization types for different analysis needs

## Directory Structure

```
FSM-LLM-Narrative/
├── .git/
├── Middle_data.zip
├── Middle_data/
│ ├── Beginning_20250415_180747/
│ └── Meet_with_Meredith_Stout_20250421_223148/
├── Generate_branches/
│ ├── dynamic_outputs/
│ ├── utils/
│ ├── visualization/
│ ├── data/
│ ├── llm/
│ ├── game/
│ ├── models/
│ ├── test_visualization.py
│ ├── main.py
│ ├── QUICKSTART.md
│ ├── README.md
│ ├── requirements.txt
│ └── Generate_branches_env/
├── temp_script.py
├── README.md
└── Generate_branches_waste/
├── tests/
└── demo/
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
python -m venv fsm_llm_env
source fsm_llm_env/bin/activate

# On Windows
python -m venv fsm_llm_env
fsm_llm_env\Scripts\activate
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

## Usage

### Extract Narratives

```bash
# Run Extract Narratives with specific task
python -m utils.extract_narratives --task "data/Beginning_20250415_180747"

# Run Extract Narratives with default task
python -m Generate_branches.utils.extract_narratives
```

### Running the Demo Game

```bash
python -m pytest Generate_branches/utils/sys_controller.py
```

### Generating Visualizations

```bash
# Generate visualizations for all tasks
python -m Generate_branches.main --visualize

# Generate visualization for a specific task
python -m Generate_branches.main --visualize --task "Beginning"
```

## Testing

Run all tests:

```bash
python -m pytest Generate_branches/tests/
python -m pytest Dynamic_Narrative_Processing/tests/
```

Run specific test suites:

```bash
python -m pytest Generate_branches/tests/test_llm.py
python -m pytest Dynamic_Narrative_Processing/tests/test_embedding.py
```

## Customization

### Adding New Tasks

1. Create a new task definition in `Generate_branches/data/Scripted_tasks.json`:

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

2. The system will automatically generate key questions, scripted subtasks, and alternative generated subtasks.

### Modifying Constants

Edit `Generate_branches/utils/constants.py` to change:

- LLM settings (model, API key, token limits)
- Narrative structure (number of layers, ID formats)
- File paths for data and visualizations
- Debug and testing parameters

## Troubleshooting

- **ImportError: No module named 'Generate_branches' or 'Dynamic_Narrative_Processing'**
  - Ensure you're running commands from the project root directory
  - Check that your Python path includes the project directory

- **Missing API Key**
  - Set the `OPENAI_API_KEY` in `Generate_branches/utils/constants.py` or as an environment variable

- **ModuleNotFoundError: No module named 'langchain_openai'**
  - Install the LangChain OpenAI package: `pip install langchain_openai`
  - Check that your installation is up to date: `pip install --upgrade langchain_openai langchain`

- **Visualization Issues**
  - Install visualization dependencies: `pip install networkx matplotlib ipython`
  - For better hierarchical layouts, install: `pip install pygraphviz`

- **LLM Generation Errors**
  - Check your API key and internet connection
  - Verify the LLM model is available and correctly set in `constants.py`
  - Try increasing the timeout settings in `constants.py` if requests are timing out

## License

[MIT License](LICENSE)

## Contact

For questions or suggestions, please open an issue on GitHub.

---

Happy storytelling!
