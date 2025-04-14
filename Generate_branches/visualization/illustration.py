"""
This module provides visualizations of task chains, subtask flows, and hierarchical structures.
It creates visual representations of the narrative tree, showing relationships between
scripted subtasks and generated subtasks.
"""

import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
import matplotlib.patches as mpatches

from Generate_branches.utils.constants import VISUALIZATION_PATH
from Generate_branches.utils.helpers import log_message, ensure_directory_exists
from Generate_branches.game.branch_manager import BranchManager

class ChainVisualizer:
    """
    Provides visualization tools for task chains and subtask structures.
    """
    def __init__(self):
        """
        Initialize the chain visualizer.
        """
        self.visualization_dir = os.path.join("Generate_branches", VISUALIZATION_PATH)
        ensure_directory_exists(self.visualization_dir)
        
    def visualize_task_chain(self, task_chain):
        """
        Visualize a task chain as a graph.
        
        Args:
            task_chain: TaskChain object to visualize
        """
        G = nx.DiGraph()
        
        # Add the chain as the root node
        G.add_node(task_chain.chain_id, type="chain")
        
        # Add tasks and connect to chain
        for task in task_chain.tasks:
            G.add_node(task.task_id, type="task")
            G.add_edge(task_chain.chain_id, task.task_id)
            
            # Add the root subtask
            G.add_node(f"{task.task_id}_root", type="subtask_root")
            G.add_edge(task.task_id, f"{task.task_id}_root")
            
            # Add first level subtasks
            for subtask in task.subtasks:
                G.add_node(subtask.subtask_id, type="subtask", is_generated=subtask.is_generated)
                G.add_edge(f"{task.task_id}_root", subtask.subtask_id)
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes with different colors based on type
        nx.draw_networkx_nodes(G, pos, nodelist=[n for n, d in G.nodes(data=True) if d['type'] == "chain"], 
                            node_color='skyblue', node_size=1500)
        nx.draw_networkx_nodes(G, pos, nodelist=[n for n, d in G.nodes(data=True) if d['type'] == "task"], 
                            node_color='lightgreen', node_size=1200)
        nx.draw_networkx_nodes(G, pos, nodelist=[n for n, d in G.nodes(data=True) if d['type'] == "subtask_root"], 
                            node_color='yellow', node_size=800)
        nx.draw_networkx_nodes(G, pos, nodelist=[n for n, d in G.nodes(data=True) if d['type'] == "subtask" and not d['is_generated']], 
                            node_color='orange', node_size=600)
        nx.draw_networkx_nodes(G, pos, nodelist=[n for n, d in G.nodes(data=True) if d['type'] == "subtask" and d['is_generated']], 
                            node_color='pink', node_size=600)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7)
        
        # Draw labels with smaller font
        node_labels = {n: n.split('_')[-1] for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
        
        # Create a legend
        legend_elements = [
            mpatches.Patch(color='skyblue', label='Chain'),
            mpatches.Patch(color='lightgreen', label='Task'),
            mpatches.Patch(color='yellow', label='Subtask Root'),
            mpatches.Patch(color='orange', label='Scripted Subtask'),
            mpatches.Patch(color='pink', label='Generated Subtask')
        ]
        plt.legend(handles=legend_elements, loc='best')
        
        # Set title and remove axes
        plt.title(f"Task Chain: {task_chain.name}")
        plt.axis('off')
        
        # Save the visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task_chain_{task_chain.chain_id}.png"
        filepath = os.path.join(self.visualization_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        log_message(f"Task chain visualization saved to {filepath}", "INFO")
        
    def visualize_subtask_flow(self, task):
        """
        Visualize the sequential flow of subtasks within a task.
        
        Args:
            task: Task object to visualize
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add subtasks by layer
        subtasks_by_layer = {}
        for subtask in task.subtasks:
            layer = subtask.layer
            if layer not in subtasks_by_layer:
                subtasks_by_layer[layer] = []
            subtasks_by_layer[layer].append(subtask)
            
            # Add the node
            G.add_node(subtask.subtask_id, 
                    title=subtask.title,
                    layer=layer,
                    is_generated=subtask.is_generated)
            
            # Add edge from parent to this subtask
            if subtask.parent_id:
                G.add_edge(subtask.parent_id, subtask.subtask_id)
        
        # Create the plot
        plt.figure(figsize=(15, 10))
        
        # Use hierarchical layout
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=LR')
        except:
            # Fall back to normal layout if graphviz is not available
            pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes by layer and type
        for layer in sorted(subtasks_by_layer.keys()):
            # Get scripted subtasks for this layer
            scripted_nodes = [s.subtask_id for s in subtasks_by_layer[layer] if not s.is_generated]
            if scripted_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=scripted_nodes, 
                                    node_color='orange', node_size=800)
            
            # Get generated subtasks for this layer
            generated_nodes = [s.subtask_id for s in subtasks_by_layer[layer] if s.is_generated]
            if generated_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=generated_nodes, 
                                    node_color='pink', node_size=800)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7)
        
        # Prepare labels
        labels = {}
        for subtask in task.subtasks:
            labels[subtask.subtask_id] = f"{subtask.title}\n(Layer {subtask.layer})"
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=6)
        
        # Create a legend
        legend_elements = [
            mpatches.Patch(color='orange', label='Scripted Subtask'),
            mpatches.Patch(color='pink', label='Generated Subtask')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Set title and remove axes
        plt.title(f"Subtask Flow: {task.title}")
        plt.axis('off')
        
        # Save the visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task.title.replace(' ', '_')}_subtask_chain_{timestamp}.png"
        filepath = os.path.join(self.visualization_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        log_message(f"Subtask flow visualization saved to {filepath}", "INFO")
        
    def visualize_hierarchical_structure(self, task):
        """
        Visualize the hierarchical structure of a task with its subtasks.
        
        Args:
            task: Task object to visualize
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add the task as root node
        G.add_node(task.task_id, title=task.title, type="task")
        
        # Add subtasks
        for subtask in task.subtasks:
            G.add_node(subtask.subtask_id, 
                      title=subtask.title,
                      layer=subtask.layer,
                      is_generated=subtask.is_generated)
            
            # Add edge from parent (task or another subtask)
            if subtask.parent_id == task.task_id:
                G.add_edge(task.task_id, subtask.subtask_id)
            elif subtask.parent_id:
                G.add_edge(subtask.parent_id, subtask.subtask_id)
            else:
                # Connect to task if no parent specified
                G.add_edge(task.task_id, subtask.subtask_id)
        
        # Create the plot
        plt.figure(figsize=(15, 10))
        
        # Use hierarchical layout
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            # Fall back to normal layout if graphviz is not available
            pos = nx.spring_layout(G, seed=42)
        
        # Draw task node (root)
        nx.draw_networkx_nodes(G, pos, nodelist=[task.task_id], 
                            node_color='lightgreen', node_size=1000)
        
        # Draw scripted subtasks
        scripted_nodes = [n for n, d in G.nodes(data=True) 
                         if n != task.task_id and 'is_generated' in d and not d['is_generated']]
        if scripted_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=scripted_nodes, 
                                node_color='orange', node_size=700)
        
        # Draw generated subtasks
        generated_nodes = [n for n, d in G.nodes(data=True) 
                          if n != task.task_id and 'is_generated' in d and d['is_generated']]
        if generated_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=generated_nodes, 
                                node_color='pink', node_size=700)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7, arrows=True, arrowsize=15)
        
        # Prepare labels
        labels = {task.task_id: f"{task.title}"}
        for subtask in task.subtasks:
            labels[subtask.subtask_id] = f"{subtask.title} (L{subtask.layer})"
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
        
        # Create a legend
        legend_elements = [
            mpatches.Patch(color='lightgreen', label='Task (Root)'),
            mpatches.Patch(color='orange', label='Scripted Subtask'),
            mpatches.Patch(color='pink', label='Generated Subtask')
        ]
        plt.legend(handles=legend_elements, loc='best')
        
        # Set title and remove axes
        plt.title(f"Hierarchical Structure: {task.title}")
        plt.axis('off')
        
        # Save the visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task.title.replace(' ', '_')}_hierarchical_{timestamp}.png"
        filepath = os.path.join(self.visualization_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        log_message(f"Hierarchical structure visualization saved to {filepath}", "INFO")

    def visualize_subtask_relationships(self, task):
        """
        Visualize the relationships between scripted_subtasks and generated_subtasks 
        within a task, emphasizing the branching structure.
        
        Args:
            task: Task object to visualize
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add the task as root node
        G.add_node(task.task_id, title=task.title, type="task")
        
        # Add subtasks and track relationships
        subtasks_by_parent = {}
        
        # First pass: add all nodes
        for subtask in task.subtasks:
            G.add_node(subtask.subtask_id, 
                      title=subtask.title,
                      layer=subtask.layer,
                      is_generated=subtask.is_generated)
            
            # Group subtasks by parent
            parent_id = subtask.parent_id if subtask.parent_id else task.task_id
            if parent_id not in subtasks_by_parent:
                subtasks_by_parent[parent_id] = []
            subtasks_by_parent[parent_id].append(subtask)
        
        # Second pass: add all edges
        for subtask in task.subtasks:
            parent_id = subtask.parent_id if subtask.parent_id else task.task_id
            G.add_edge(parent_id, subtask.subtask_id)
        
        # Create the plot
        plt.figure(figsize=(15, 10))
        
        # Use hierarchical layout
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            # Fall back to normal layout if graphviz is not available
            pos = nx.spring_layout(G, seed=42)
        
        # Draw task node (root)
        nx.draw_networkx_nodes(G, pos, nodelist=[task.task_id], 
                            node_color='lightgreen', node_size=1000)
        
        # Collect nodes by layer and type for better visualization
        scripted_by_layer = {}
        generated_by_layer = {}
        
        for subtask in task.subtasks:
            layer = subtask.layer
            if subtask.is_generated:
                if layer not in generated_by_layer:
                    generated_by_layer[layer] = []
                generated_by_layer[layer].append(subtask.subtask_id)
            else:
                if layer not in scripted_by_layer:
                    scripted_by_layer[layer] = []
                scripted_by_layer[layer].append(subtask.subtask_id)
        
        # Draw scripted subtasks by layer with different color intensities
        orange_cmap = plt.cm.Oranges
        for i, layer in enumerate(sorted(scripted_by_layer.keys())):
            nodes = scripted_by_layer[layer]
            if nodes:
                color_val = 0.5 + (i * 0.5 / (len(scripted_by_layer) or 1))  # Avoid division by zero
                nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                                    node_color=[orange_cmap(color_val)], 
                                    node_size=700)
        
        # Draw generated subtasks by layer with different color intensities
        pink_cmap = plt.cm.RdPu
        for i, layer in enumerate(sorted(generated_by_layer.keys())):
            nodes = generated_by_layer[layer]
            if nodes:
                color_val = 0.5 + (i * 0.5 / (len(generated_by_layer) or 1))  # Avoid division by zero
                nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                                    node_color=[pink_cmap(color_val)], 
                                    node_size=700)
        
        # Draw edges differently between different types of nodes
        # Scripted-to-scripted edges
        scripted_edges = [(u, v) for u, v in G.edges() 
                          if u != task.task_id and v != task.task_id and 
                          not G.nodes[u].get('is_generated', False) and 
                          not G.nodes[v].get('is_generated', False)]
        if scripted_edges:
            nx.draw_networkx_edges(G, pos, edgelist=scripted_edges, 
                                width=1.5, alpha=0.8, edge_color='darkorange', 
                                arrows=True, arrowsize=15)
        
        # Generated-to-generated edges
        generated_edges = [(u, v) for u, v in G.edges() 
                           if u != task.task_id and v != task.task_id and 
                           G.nodes[u].get('is_generated', False) and 
                           G.nodes[v].get('is_generated', False)]
        if generated_edges:
            nx.draw_networkx_edges(G, pos, edgelist=generated_edges, 
                                width=1.5, alpha=0.8, edge_color='hotpink', 
                                arrows=True, arrowsize=15)
        
        # Scripted-to-generated edges
        mixed_edges_1 = [(u, v) for u, v in G.edges() 
                        if u != task.task_id and v != task.task_id and 
                        not G.nodes[u].get('is_generated', False) and 
                        G.nodes[v].get('is_generated', False)]
        if mixed_edges_1:
            nx.draw_networkx_edges(G, pos, edgelist=mixed_edges_1, 
                                width=1.5, alpha=0.8, edge_color='purple', 
                                style='dashed', arrows=True, arrowsize=15)
        
        # Generated-to-scripted edges
        mixed_edges_2 = [(u, v) for u, v in G.edges() 
                        if u != task.task_id and v != task.task_id and 
                        G.nodes[u].get('is_generated', False) and 
                        not G.nodes[v].get('is_generated', False)]
        if mixed_edges_2:
            nx.draw_networkx_edges(G, pos, edgelist=mixed_edges_2, 
                                width=1.5, alpha=0.8, edge_color='blue', 
                                style='dotted', arrows=True, arrowsize=15)
        
        # Root-to-any edges
        root_edges = [(u, v) for u, v in G.edges() if u == task.task_id]
        if root_edges:
            nx.draw_networkx_edges(G, pos, edgelist=root_edges, 
                                width=2.0, alpha=0.9, edge_color='green', 
                                arrows=True, arrowsize=20)
        
        # Prepare labels
        labels = {task.task_id: f"{task.title} (Root)"}
        for subtask in task.subtasks:
            labels[subtask.subtask_id] = f"{subtask.title} (L{subtask.layer})"
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
        
        # Create a legend
        legend_elements = [
            mpatches.Patch(color='lightgreen', label='Task (Root)'),
            mpatches.Patch(color=orange_cmap(0.7), label='Scripted Subtask'),
            mpatches.Patch(color=pink_cmap(0.7), label='Generated Subtask'),
            mpatches.Patch(color='green', label='Root Connection'),
            mpatches.Patch(color='darkorange', label='Scripted-to-Scripted'),
            mpatches.Patch(color='hotpink', label='Generated-to-Generated'),
            mpatches.Patch(color='purple', label='Scripted-to-Generated'),
            mpatches.Patch(color='blue', label='Generated-to-Scripted')
        ]
        plt.legend(handles=legend_elements, loc='best')
        
        # Set title and remove axes
        plt.title(f"Subtask Relationships in {task.title}")
        plt.axis('off')
        
        # Save the visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task.title.replace(' ', '_')}_subtask_relationships_{timestamp}.png"
        filepath = os.path.join(self.visualization_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        log_message(f"Subtask relationships visualization saved to {filepath}", "INFO")

def visualize_task_structure_example(task_name=None):
    """
    Run a simple example that demonstrates the structure visualization capabilities.
    
    This function loads the specified task or default test task and generates visualizations for it.
    
    Args:
        task_name: Optional task name to visualize. If None, uses the default TEST_TASK_NAME
                  
    Returns:
        bool: True if visualization succeeded, False otherwise
    """
    from Generate_branches.utils.constants import TEST_TASK_NAME
    
    # Use provided task name or fall back to default
    task_name = task_name or TEST_TASK_NAME
    log_message(f"Attempting to visualize task: {task_name}", "INFO")
    
    # Create a branch manager
    branch_manager = BranchManager()
    
    # Generate a task chain
    task_chain = branch_manager.generate_task_chain(task_name)
    
    # Check if task_chain generation was successful
    if not task_chain or not task_chain.tasks:
        log_message(f"Could not generate task chain for {task_name}", "ERROR")
        
        # If using the default task failed, try with a fallback task
        if task_name == TEST_TASK_NAME:
            fallback_task = "Beginning" if TEST_TASK_NAME != "Beginning" else "Meet with Meredith Stout"
            log_message(f"Attempting fallback visualization with task: {fallback_task}", "INFO")
            return visualize_task_structure_example(fallback_task)
        
        return False
    
    try:
        # Create a visualizer
        visualizer = ChainVisualizer()
        
        # Get the task
        task = task_chain.tasks[0]
        
        # Save the task chain for reference
        branch_manager.save_task_chain(task_chain.chain_id)
        
        # Visualize the hierarchical structure
        visualizer.visualize_hierarchical_structure(task)
        
        # Visualize the relationship structure
        visualizer.visualize_subtask_relationships(task)
        
        log_message(f"Task structure visualizations created for {task.title}", "INFO")
        return True
    
    except Exception as e:
        log_message(f"Error generating visualizations: {e}", "ERROR")
        return False

if __name__ == "__main__":
    visualize_task_structure_example()
