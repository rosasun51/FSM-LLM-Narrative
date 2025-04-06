import argparse
import json
import os
import sys
from typing import Dict, List
import matplotlib.pyplot as plt
import networkx as nx

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from processing.input_analyzer import InputAnalyzer

class DemoProcessor:
    def __init__(self):
        """
        Initialize the demo processor with input analyzer.
        """
        self.input_analyzer = InputAnalyzer()
        self.graph = nx.DiGraph()
        self.project_root = parent_dir
        
    def load_sample_nodes(self, episode: str):
        """
        Load sample nodes for the given episode.
        
        Args:
            episode: Name of the episode to load nodes for
        """
        # Construct the path to the original data
        episode_dir = os.path.join(self.project_root, "data", f"{episode}_20250403_110320")
        scripted_subtask_dir = os.path.join(episode_dir, "Scripted_subtask_20250403_110320")
        subtask_branches_dir = os.path.join(episode_dir, "Subtask_branches_20250403_110320")
        
        self.sample_nodes = []
        
        # Load scripted subtasks
        if os.path.exists(scripted_subtask_dir):
            for filename in os.listdir(scripted_subtask_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(scripted_subtask_dir, filename), 'r') as f:
                        node = json.load(f)
                        node['is_generated'] = False
                        self.sample_nodes.append(node)
        
        # Load generated subtasks
        if os.path.exists(subtask_branches_dir):
            for filename in os.listdir(subtask_branches_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(subtask_branches_dir, filename), 'r') as f:
                        node = json.load(f)
                        node['is_generated'] = True
                        self.sample_nodes.append(node)
        
        print(f"Loaded {len(self.sample_nodes)} nodes from original data")
            
    def process_input(self, player_input: str) -> Dict:
        """
        Process a player input and return the result.
        
        Args:
            player_input: The player's input text
            
        Returns:
            Dictionary containing the processing result
        """
        result = self.input_analyzer.analyze(player_input, self.sample_nodes)
        self._update_visualization(result)
        return result
        
    def _update_visualization(self, result: Dict):
        """
        Update the visualization with the processing result.
        
        Args:
            result: The processing result dictionary
        """
        # Add the current node to the graph
        current_node = result.get('selected_node', result.get('generated_node'))
        if current_node:
            node_id = current_node.get('id', 'unknown')
            self.graph.add_node(node_id, 
                              content=current_node.get('content', ''),
                              layer=current_node.get('layer', 0),
                              is_generated=current_node.get('is_generated', False))
            
        # Add edges for transitions
        if 'transition' in result:
            from_node = result['transition'].get('from')
            to_node = result['transition'].get('to')
            if from_node and to_node:
                self.graph.add_edge(from_node, to_node)
                
    def visualize(self):
        """
        Visualize the current state of the narrative graph.
        """
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)
        
        # Draw nodes with different colors based on whether they're generated
        node_colors = ['lightblue' if not data['is_generated'] else 'pink' 
                      for node, data in self.graph.nodes(data=True)]
        
        nx.draw_networkx_nodes(self.graph, pos,
                             node_color=node_colors,
                             node_size=2000)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos,
                             edge_color='gray',
                             arrows=True)
        
        # Draw labels
        labels = {node: f"{node}\n{data['content'][:50]}..." 
                 for node, data in self.graph.nodes(data=True)}
        nx.draw_networkx_labels(self.graph, pos, labels)
        
        plt.title("Narrative Structure Visualization")
        plt.axis('off')
        plt.show()

def main():
    """
    Main function to run the demo processor.
    """
    parser = argparse.ArgumentParser(description='Process player inputs and visualize narrative structure')
    parser.add_argument('--input', type=str, required=True,
                      help='Path to the input JSON file')
    parser.add_argument('--episode', type=str, required=True,
                      help='Name of the episode to process')
    
    args = parser.parse_args()
    
    # Initialize the processor
    processor = DemoProcessor()
    
    # Load sample nodes
    processor.load_sample_nodes(args.episode)
    
    # Load and process inputs
    try:
        input_path = os.path.join(processor.project_root, args.input)
        with open(input_path, 'r') as f:
            inputs = json.load(f)
            
        for input_data in inputs:
            print(f"\nProcessing input: {input_data['text']}")
            result = processor.process_input(input_data['text'])
            print(f"Result: {result}")
            
        # Show final visualization
        processor.visualize()
        
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in input file {input_path}")

if __name__ == "__main__":
    main() 