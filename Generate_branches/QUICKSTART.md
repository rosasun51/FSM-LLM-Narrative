# FSM-LLM Narrative System - Quick Start Guide

This quick-start guide will help you get up and running with the FSM-LLM Narrative System in minutes.

## Setup

1. Clone the repository and navigate to the project directory:

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

4. Set your OpenAI API key (required for LLM functionality):

```bash
# On macOS/Linux
export OPENAI_API_KEY="your-api-key-here"

# On Windows
set OPENAI_API_KEY="your-api-key-here"
```

5. Ensure necessary directories exist:

```bash
mkdir -p Generate_branches/data/key_questions Generate_branches/data/subtasks Generate_branches/visualization
```

## Running the Demo Game

Try the interactive demo to see the narrative system in action:

```bash
python -m Generate_branches.main --demo
```

This will start the default "Beginning" task. Follow the on-screen prompts to interact with the narrative.

## Generating Visualizations

Create visualizations of the narrative structure:

```bash
python -m Generate_branches.main --visualize --task "Beginning"
```

This will generate three types of visualizations in the `Generate_branches/visualization/` directory:
- Task chain visualization
- Subtask flow visualization
- Hierarchical structure visualization

## Next Steps

1. **Explore different tasks**:
   ```bash
   python -m Generate_branches.main --demo --task "Meet with Meredith Stout"
   ```

2. **Create a visualization notebook**:
   ```bash
   python -m Generate_branches.main --notebook
   jupyter notebook Generate_branches/visualization/illustration.ipynb
   ```

3. **Examine the generated task chain**:
   ```bash
   python -c "import json; print(json.dumps(json.load(open('Generate_branches/data/generated_chains/beginning_chain.json')), indent=2))"
   ```

4. **Generate a single task structure visualization**:
   ```bash
   python -c "from Generate_branches.visualization.illustration import visualize_task_structure_example; visualize_task_structure_example()"
   ```

5. **Extract narrative content to a text file**:
   ```bash
   python -m Generate_branches.utils.extract_narratives --task "Beginning"
   ```
   This creates a readable text file with all narrative content from key questions, scripted subtasks, and alternatives.

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `python -m Generate_branches.main --demo` | Run the interactive demo |
| `python -m Generate_branches.main --visualize` | Generate visualizations |
| `python -m Generate_branches.main --notebook` | Create visualization notebook |
| `python -m Generate_branches.main --test` | Run all tests |
| `python -m Generate_branches.utils.extract_narratives` | Extract narrative content from task folders |
| `python -m Generate_branches.main --help` | Show help with all options |

## Interactive Demo Commands

When in the interactive demo, use these commands:

- `help` - Show available commands
- `look` - Examine the current environment
- `tasks` - Show active tasks
- `load [task_name]` - Load a specific task
- `exit` or `quit` - Exit the demo

## Troubleshooting

- **ImportError: No module named 'Generate_branches'**
  - Make sure you're running commands from the project root directory (`FSM-LLM-Narrative`)

- **Missing API Key**
  - Ensure your OpenAI API key is set as shown in step 4

- **Visualization Issues**
  - Install visualization dependencies: `pip install networkx matplotlib ipython`

For more detailed information, refer to the full [README.md](README.md). 