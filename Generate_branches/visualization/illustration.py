"""
This module provides visualization tools for task chains and subtask branches.
It uses langraph (NetworkX) for generating visual representations of narrative structures.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    from IPython.display import display
    
    # Try to import pygraphviz for better hierarchical layouts
    try:
        import pygraphviz
        HAS_PYGRAPHVIZ = True
    except ImportError:
        HAS_PYGRAPHVIZ = False
        
except ImportError:
    print("Warning: Visualization requires networkx, matplotlib, and IPython")
    HAS_PYGRAPHVIZ = False

from Generate_branches.game.task_chain import TaskChain
from Generate_branches.models.task import Task
from Generate_branches.models.subtask import ScriptedSubTask, GeneratedSubTask
from Generate_branches.utils.helpers import log_message
from Generate_branches.utils.constants import (
    VISUALIZATION_PATH,
    ROOT_TASK_ID,
    TEST_TASK_NAME,
    DATA_ROOT_PATH
)

class ChainVisualizer:
    """
    Visualizer for task chains and subtask branches.
    
    This class provides methods for creating visual representations of narrative
    structures, including task chains, subtask flows, and branching possibilities.
    """
    
    def __init__(self, output_dir: str = VISUALIZATION_PATH):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualizations in
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        full_path = os.path.join("Generate_branches", output_dir)
        os.makedirs(full_path, exist_ok=True)
        
        # Log available visualization features
        if HAS_PYGRAPHVIZ:
            log_message("Hierarchical layout available using pygraphviz", "INFO")
        else:
            log_message("Pygraphviz not found, using spring layout for visualizations", "INFO")
    
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
    
    def visualize_hierarchical_structure(self, task: Task, save_to_file: bool = True) -> Optional[nx.DiGraph]:
        """
        Create a visualization of the complete hierarchical structure of a task including all subtasks.
        
        This creates a detailed tree-like visualization that shows:
        - The task as the root node
        - All subtasks organized by their layers
        - Clear parent-child relationships between subtasks
        - Visual differentiation between scripted and generated subtasks
        
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
            
            # Create a mapping of parent_id to subtask_id for connecting nodes
            subtask_map = {}
            
            # First pass: Add all subtasks to the graph
            for subtask in sorted(task.subtasks, key=lambda x: x.layer):
                subtask_id = subtask.subtask_id
                parent_id = subtask.parent_id if subtask.parent_id else task_id
                
                # Store for second pass
                subtask_map[subtask_id] = subtask
                
                # Add node
                node_type = "scripted" if isinstance(subtask, ScriptedSubTask) else "generated"
                is_generated = "Gen" if node_type == "generated" else "Scripted"
                label = f"{subtask.title} (L{subtask.layer}, {is_generated})"
                G.add_node(subtask_id, label=label, type=node_type, layer=subtask.layer)
            
            # Second pass: Connect nodes based on parent-child relationships
            for subtask_id, subtask in subtask_map.items():
                parent_id = subtask.parent_id if subtask.parent_id else task_id
                G.add_edge(parent_id, subtask_id)
            
            # Draw the graph
            if save_to_file:
                # Generate timestamp for unique filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = task.title.replace(' ', '_').replace('/', '_').replace('\\', '_')
                
                # Check if we should save to the new task-specific folder structure
                task_dir = os.path.join("Generate_branches", DATA_ROOT_PATH, f"{safe_title}_{timestamp}")
                
                # If the task directory already exists (created by LLM response saving), use it
                # Otherwise, save to the default visualization path
                if os.path.exists(task_dir):
                    # Save to the task-specific directory
                    file_path = os.path.join(task_dir, f"{safe_title}_{timestamp}.png")
                    self._draw_and_save_graph(G, f"{safe_title}_structure", custom_path=file_path)
                    log_message(f"Saved visualization to task folder: {file_path}", "INFO")
                else:
                    # Save to the default visualization directory
                    self._draw_and_save_graph(G, f"{safe_title}_structure_{timestamp}")
            
            return G
        except Exception as e:
            log_message(f"Error visualizing hierarchical structure: {e}", "ERROR")
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
    
    def _draw_and_save_graph(self, G: nx.DiGraph, filename: str, custom_path: str = None):
        """
        Draw and save a graph visualization.
        
        Args:
            G: The graph to draw
            filename: Base filename to save as
            custom_path: Custom path to save the file to (overrides standard path)
        """
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Use pygraphviz for better hierarchical layout if available
        if HAS_PYGRAPHVIZ:
            pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
        else:
            pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Get node types for coloring
        node_types = nx.get_node_attributes(G, 'type')
        
        # Prepare node colors based on type
        node_colors = []
        for node in G.nodes():
            node_type = node_types.get(node, 'unknown')
            if node_type == 'task':
                node_colors.append('lightgreen')
            elif node_type == 'scripted':
                node_colors.append('orange')
            elif node_type == 'generated':
                node_colors.append('pink')
            elif node_type == 'chain':
                node_colors.append('lightblue')
            else:
                node_colors.append('gray')
        
        # Draw nodes with labels
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color=node_colors, alpha=0.8)
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15, min_target_margin=15)
        
        # Add title and legend
        plt.title(f"Task Structure: {filename}", fontsize=16)
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=15, label='Task'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=15, label='Scripted Subtask'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='pink', markersize=15, label='Generated Subtask')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Save figure
        if custom_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(custom_path), exist_ok=True)
            file_path = custom_path
        else:
            # Use default path
            file_path = os.path.join("Generate_branches", self.output_dir, f"{filename}.png")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
        plt.tight_layout()
        plt.axis('off')
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        log_message(f"Saved visualization to {file_path}", "INFO")


def visualize_task_structure_example():
    """
    Example function to generate a hierarchical task structure visualization.
    
    This function demonstrates the process of visualizing a task's hierarchical structure:
    1. Create a branch manager to generate a task chain
    2. Extract a task from the chain
    3. Create a visualizer to generate a hierarchical structure visualization
    4. Return the file path to the generated visualization
    
    Returns:
        String path to the generated visualization file or None if generation fails
    """
    import os
    import datetime
    from Generate_branches.utils.constants import (
        TEST_TASK_NAME,
        VISUALIZATION_PATH,
        DATA_ROOT_PATH
    )
    from Generate_branches.game.branch_manager import BranchManager
    from Generate_branches.utils.helpers import log_message
    
    # Step 1: Create a branch manager to generate the narrative structure
    branch_manager = BranchManager()
    
    # Step 2: Generate a task chain using the default test task name
    log_message(f"Generating task chain for the example visualization using '{TEST_TASK_NAME}'", "INFO")
    task_chain = branch_manager.generate_task_chain(TEST_TASK_NAME)
    
    if task_chain and task_chain.tasks:
        # Step 3: Extract the first task from the chain for visualization
        task = task_chain.tasks[0]
        log_message(f"Using task '{task.title}' for visualization", "INFO")
        
        # Step 4: Create the visualizer 
        visualizer = ChainVisualizer()
        
        # Step 5: Find or create a task-specific directory to save the visualization
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = task.title.replace(' ', '_').replace('/', '_').replace('\\', '_')
        
        # Check if a task directory already exists in the data path
        data_root = os.path.join("Generate_branches", DATA_ROOT_PATH)
        task_specific_dir = None
        
        # Look for existing task directories that match our task name
        if os.path.exists(data_root):
            matching_dirs = [d for d in os.listdir(data_root) 
                            if os.path.isdir(os.path.join(data_root, d)) and d.startswith(safe_title)]
            
            if matching_dirs:
                # Use the most recent directory if multiple exist
                matching_dirs.sort(reverse=True)  # Sort by timestamp (newest first)
                task_specific_dir = os.path.join(data_root, matching_dirs[0])
                log_message(f"Found existing task directory: {task_specific_dir}", "INFO")
        
        # If no existing directory found, create a new one
        if not task_specific_dir:
            task_specific_dir = os.path.join(data_root, f"{safe_title}_{timestamp}")
            os.makedirs(task_specific_dir, exist_ok=True)
            log_message(f"Created new task directory: {task_specific_dir}", "INFO")
            
            # Save the task chain to this new directory
            branch_manager.save_task_chain(task_chain.chain_id)
        
        # Step 6: Generate the hierarchical structure visualization with custom path
        log_message("Generating hierarchical structure visualization...", "INFO")
        
        # Define the custom path for the visualization file
        custom_file_path = os.path.join(task_specific_dir, f"{safe_title}_{timestamp}.png")
        
        # Call visualize_hierarchical_structure on the visualizer instance with a custom path
        G = visualizer.visualize_hierarchical_structure(task)
        
        # Save the visualization using the custom path
        if G is not None:
            visualizer._draw_and_save_graph(G, f"{safe_title}_structure", custom_path=custom_file_path)
        
        log_message(f"Generated hierarchical structure visualization for task: {task.title}", "INFO")
        log_message(f"Visualization saved to: {custom_file_path}", "INFO")
        
        return custom_file_path
    else:
        log_message(f"Failed to generate task chain for {TEST_TASK_NAME}", "ERROR")
        return None 