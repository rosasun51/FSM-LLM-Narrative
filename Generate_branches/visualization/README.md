# Task Structure Visualization Guide

This module provides tools for visualizing the hierarchical structure of tasks and subtasks in the narrative generation system. It creates clear, visual representations of the task trees, showing parent-child relationships and distinguishing between scripted and generated subtasks.

## Features

The visualization module offers four main visualization types:

1. **Task Chain Visualization**: Shows the overall structure of a task chain with all its tasks.
2. **Subtask Flow Visualization**: Displays the sequential flow of subtasks within a task.
3. **Hierarchical Structure Visualization**: Creates a comprehensive tree diagram showing all subtasks with their parent-child relationships, organized by layers.
4. **Subtask Relationships Visualization**: Provides a detailed view of the relationships between scripted and generated subtasks, with color-coded edges to show different types of connections.

## Hierarchical Structure Visualization

The newest feature is the hierarchical structure visualization, which provides a complete view of a task's structure:

### How to Use

```python
from Generate_branches.visualization.illustration import ChainVisualizer
from Generate_branches.game.branch_manager import BranchManager

# Create a branch manager and load a task
branch_manager = BranchManager()
task_chain = branch_manager.generate_task_chain("Beginning")  # Use any task name
task = task_chain.tasks[0]  # Get the first task

# Create visualizer and generate hierarchical structure visualization
visualizer = ChainVisualizer()
visualizer.visualize_hierarchical_structure(task)
```

## Subtask Relationships Visualization

The newest feature is the subtask relationships visualization, which provides a more nuanced view of how scripted and generated subtasks relate to each other:

### How to Use

```python
from Generate_branches.visualization.illustration import ChainVisualizer
from Generate_branches.game.branch_manager import BranchManager

# Create a branch manager and load a task
branch_manager = BranchManager()
task_chain = branch_manager.generate_task_chain("Beginning")  # Use any task name
task = task_chain.tasks[0]  # Get the first task

# Create visualizer and generate subtask relationships visualization
visualizer = ChainVisualizer()
visualizer.visualize_subtask_relationships(task)
```

### Understanding the Output

The visualization creates a PNG image file with:

- **Filename Format**: `TaskName_subtask_relationships_YYYYMMDD_HHMMSS.png` (includes timestamp)
- **Location**: Saved in the directory specified by `VISUALIZATION_PATH` constant (default: "visualization")

### Reading the Visualization

The subtask relationships visualization uses:

- **Root Node (Light Green)**: The task itself
- **Orange Shades**: Scripted subtasks (manually defined) with darker shades for deeper layers
- **Pink Shades**: Generated subtasks (created by LLM) with darker shades for deeper layers
- **Node Labels**: Format is "SubtaskTitle (LX)" where X is the layer number
- **Edge Colors**:
  - **Green**: Connections from the root task to subtasks
  - **Dark Orange**: Connections between scripted subtasks
  - **Hot Pink**: Connections between generated subtasks
  - **Purple (dashed)**: Connections from scripted to generated subtasks
  - **Blue (dotted)**: Connections from generated to scripted subtasks

This visualization makes it easy to see:
- How tasks are organized in layers with different shade intensities
- Which subtasks are generated vs. scripted
- The different types of relationships between subtasks
- The complete flow of narrative branches

### Quick Start Example

For a quick example that generates all visualizations for the default test task:

```python
from Generate_branches.visualization.illustration import visualize_task_structure_example

# Run the example function
visualize_task_structure_example()
```

### Example Command-Line Usage

You can generate all visualizations directly from the command line:

```bash
python -m Generate_branches.main --visualize --task "Beginning"
```

Or just run the example:

```bash
python -c "from Generate_branches.visualization.illustration import visualize_task_structure_example; visualize_task_structure_example()"
```

## Requirements

The visualization module requires:
- `networkx`: For creating and manipulating the graph structure
- `matplotlib`: For rendering the visualization
- `pygraphviz` (optional): For improved hierarchical layouts

If `pygraphviz` is not available, the module will fall back to using a spring layout.

## Jupyter Notebook

An interactive Jupyter notebook is provided at `Generate_branches/visualization/illustration.ipynb` that demonstrates all visualization capabilities. You can run this notebook to explore different visualization options and see examples of the outputs. 