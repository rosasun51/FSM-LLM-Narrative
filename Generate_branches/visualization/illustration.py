"""
This module provides visualization tools for task chains and subtask branches.
It uses langraph for generating visual representations of narrative structures.
"""

import os
import json
from typing import Dict, List, Any, Optional

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    from IPython.display import display
except ImportError:
    print("Warning: Visualization requires networkx, matplotlib, and IPython")

from Generate_branches.game.task_chain import TaskChain
from Generate_branches.models.task import Task
from Generate_branches.models.subtask import ScriptedSubTask, GeneratedSubTask
from Generate_branches.utils.helpers import log_message

class ChainVisualizer:
    """
    Visualizer for task chains and subtask branches.
    
    This class provides methods for creating visual representations of narrative
    structures, including task chains, subtask flows, and branching possibilities.
    """
    
    def __init__(self, output_dir: str = "visualization"):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualizations in
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        full_path = os.path.join("Generate_branches", output_dir)
        os.makedirs(full_path, exist_ok=True)
    
    def visualize_task_chain(self, task_chain: TaskChain, save_to_file: bool = True) -> Optional[nx.DiGraph]:
        """
        Create a visualization of a task chain.
        
        Args:
            task_chain: The task chain to visualize
            save_to_file: Whether to save the visualization to a file
            
        Returns:
            The generated graph or None if visualization failed
        """
        try:
            # Create directed graph
            G = nx.DiGraph()
            
            # Add chain node
            chain_id = task_chain.chain_id
            G.add_node(chain_id, label=task_chain.name, type="chain")
            
            # Process tasks
            for task in task_chain.tasks:
                self._add_task_to_graph(G, task, chain_id)
            
            # Draw the graph
            if save_to_file:
                self._draw_and_save_graph(G, f"task_chain_{chain_id}")
            
            return G
        except Exception as e:
            log_message(f"Error visualizing task chain: {e}", "ERROR")
            return None
    
    def visualize_subtask_flow(self, task: Task, save_to_file: bool = True) -> Optional[nx.DiGraph]:
        """
        Create a visualization of subtask flow within a task.
        
        Args:
            task: The task containing subtasks to visualize
            save_to_file: Whether to save the visualization to a file
            
        Returns:
            The generated graph or None if visualization failed
        """
        try:
            # Create directed graph
            G = nx.DiGraph()
            
            # Add task node
            task_id = task.task_id
            G.add_node(task_id, label=task.title, type="task")
            
            # Add subtasks
            last_subtask_id = None
            for layer_id in range(2):  # Layer 0 is main path, Layer 1 is alternatives
                for subtask in task.subtasks:
                    if subtask.layer == layer_id:
                        subtask_id = subtask.subtask_id
                        
                        # Add node
                        node_type = "scripted" if isinstance(subtask, ScriptedSubTask) else "generated"
                        G.add_node(subtask_id, label=subtask.title, type=node_type)
                        
                        # Connect to task
                        G.add_edge(task_id, subtask_id)
                        
                        # Connect sequential subtasks in the same layer
                        if last_subtask_id and subtask.layer == 0:
                            G.add_edge(last_subtask_id, subtask_id)
                        
                        last_subtask_id = subtask_id if subtask.layer == 0 else last_subtask_id
            
            # Draw the graph
            if save_to_file:
                self._draw_and_save_graph(G, f"subtask_flow_{task_id}")
            
            return G
        except Exception as e:
            log_message(f"Error visualizing subtask flow: {e}", "ERROR")
            return None
    
    def _add_task_to_graph(self, G: nx.DiGraph, task: Task, parent_id: str):
        """
        Add a task and its subtasks to the graph.
        
        Args:
            G: The graph to add to
            task: The task to add
            parent_id: ID of the parent node
        """
        task_id = task.task_id
        
        # Add task node
        G.add_node(task_id, label=task.title, type="task")
        
        # Connect to parent
        G.add_edge(parent_id, task_id)
        
        # Add scripted subtasks (main path only)
        scripted_subtasks = [s for s in task.subtasks if isinstance(s, ScriptedSubTask) and s.layer == 0]
        
        last_subtask_id = None
        for subtask in scripted_subtasks:
            subtask_id = subtask.subtask_id
            
            # Add node
            G.add_node(subtask_id, label=subtask.title, type="scripted")
            
            # Connect to task
            G.add_edge(task_id, subtask_id)
            
            # Connect sequential subtasks
            if last_subtask_id:
                G.add_edge(last_subtask_id, subtask_id)
            
            last_subtask_id = subtask_id
    
    def _draw_and_save_graph(self, G: nx.DiGraph, filename: str):
        """
        Draw and save a graph visualization.
        
        Args:
            G: The graph to draw
            filename: Base filename to save as
        """
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Get node types for coloring
        node_types = nx.get_node_attributes(G, 'type')
        
        # Define colors for node types
        color_map = {
            'chain': 'lightblue',
            'task': 'lightgreen',
            'scripted': 'orange',
            'generated': 'pink'
        }
        
        # Set node colors
        node_colors = [color_map.get(node_types.get(node, 'default'), 'gray') for node in G.nodes()]
        
        # Define node positions
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1500, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=1.5, arrows=True, arrowsize=20)
        
        # Draw labels
        labels = {node: G.nodes[node].get('label', node) for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
        
        # Save figure
        file_path = os.path.join("Generate_branches", self.output_dir, f"{filename}.png")
        plt.tight_layout()
        plt.axis('off')
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        log_message(f"Saved visualization to {file_path}", "INFO")

def create_illustration_notebook():
    """
    Create a Jupyter notebook for task chain visualization.
    
    This generates an illustration.ipynb file with code to visualize
    task chains using the ChainVisualizer.
    """
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Task Chain Visualization\n",
                    "\n",
                    "This notebook demonstrates how to visualize task chains and narrative branches."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "import os\n",
                    "import json\n",
                    "import sys\n",
                    "# Add parent directory to path\n",
                    "sys.path.append('..')\n",
                    "\n",
                    "from Generate_branches.game.task_chain import TaskChain\n",
                    "from Generate_branches.game.branch_manager import BranchManager\n",
                    "from Generate_branches.visualization.illustration import ChainVisualizer"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Load and Generate Task Chains"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Initialize branch manager\n",
                    "branch_manager = BranchManager()\n",
                    "\n",
                    "# Generate task chains\n",
                    "task_chains = []\n",
                    "task_names = ['Beginning', 'Meet with Meredith Stout', 'Picking Up Goods', 'Clear Virus', 'Contact Meredith Stout']\n",
                    "\n",
                    "for task_name in task_names:\n",
                    "    print(f\"Generating task chain for: {task_name}\")\n",
                    "    task_chain = branch_manager.generate_task_chain(task_name)\n",
                    "    if task_chain:\n",
                    "        task_chains.append(task_chain)\n",
                    "        # Save the chain\n",
                    "        branch_manager.save_task_chain(task_chain.chain_id)\n",
                    "\n",
                    "print(f\"Generated {len(task_chains)} task chains\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Create Visualizations"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Initialize visualizer\n",
                    "visualizer = ChainVisualizer()\n",
                    "\n",
                    "# Visualize each task chain\n",
                    "for task_chain in task_chains:\n",
                    "    print(f\"Visualizing task chain: {task_chain.name}\")\n",
                    "    visualizer.visualize_task_chain(task_chain)\n",
                    "    \n",
                    "    # Visualize subtask flow for each task\n",
                    "    for task in task_chain.tasks:\n",
                    "        print(f\"Visualizing subtask flow for task: {task.title}\")\n",
                    "        visualizer.visualize_subtask_flow(task)"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Display Visualizations"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "import matplotlib.pyplot as plt\n",
                    "from IPython.display import Image, display\n",
                    "\n",
                    "# Display the generated visualizations\n",
                    "visualization_dir = os.path.join('Generate_branches', 'visualization')\n",
                    "for filename in os.listdir(visualization_dir):\n",
                    "    if filename.endswith('.png'):\n",
                    "        print(f\"\\n## {filename}\")\n",
                    "        display(Image(os.path.join(visualization_dir, filename)))"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Save the notebook
    try:
        notebook_path = os.path.join("Generate_branches", "visualization", "illustration.ipynb")
        with open(notebook_path, 'w') as f:
            json.dump(notebook_content, f, indent=2)
        
        log_message(f"Created illustration notebook at {notebook_path}", "INFO")
    except Exception as e:
        log_message(f"Error creating illustration notebook: {e}", "ERROR") 