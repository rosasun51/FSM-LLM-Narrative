<<<<<<< HEAD
from typing import Dict, List, Optional
import json
import os

class LayerTransitionManager:
    def __init__(self, questions_path: str = None):
        self.questions_path = questions_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'key_questions.json'
        )
        self.questions = self._load_questions()
    
    def _load_questions(self) -> Dict:
        """Load key questions from JSON files."""
        if os.path.exists(self.questions_path):
            with open(self.questions_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_key_question(self, current_layer: str, next_layer: str, 
                        episode: str = "Beginning") -> Optional[str]:
        """Get key question for transitioning between layers."""
        transition_key = f"{current_layer}_to_{next_layer}"
        return self.questions.get(episode, {}).get(
            'layer_transitions', {}
        ).get(transition_key, {}).get('question')
    
    def get_next_layer(self, current_layer: str) -> Optional[str]:
        """Get next layer based on current layer."""
        if current_layer == "Layer 1":
            return "Layer 2"
        elif current_layer == "Layer 2":
            return "Layer 3"
        return None
    
    def can_transition(self, current_state: Dict) -> bool:
        """Check if transition to next layer is possible."""
        current_layer = current_state.get('current_layer')
        if not current_layer:
            return False
        
        # Check if all nodes in current layer are completed
        current_nodes = current_state.get('layers', {}).get(current_layer, {}).get('nodes', [])
        completed_nodes = current_state.get('completed_nodes', [])
        
        return all(node['id'] in completed_nodes for node in current_nodes)
    
    def transition_to_next_layer(self, current_state: Dict) -> Dict:
        """Transition to next layer if possible."""
        new_state = current_state.copy()
        current_layer = new_state.get('current_layer')
        next_layer = self.get_next_layer(current_layer)
        
        if next_layer and self.can_transition(current_state):
            new_state['current_layer'] = next_layer
            # Initialize available nodes for new layer
            if next_layer not in new_state['layers']:
                new_state['layers'][next_layer] = {'nodes': []}
            new_state['available_nodes'] = [
                node['id'] for node in new_state['layers'][next_layer]['nodes']
            ]
        
        return new_state
    
    def get_layer_info(self, layer: str, episode: str = "Beginning") -> Dict:
        """Get information about a specific layer."""
        return {
            'number': int(layer.split()[-1]),
            'key_question': self.get_key_question(layer, self.get_next_layer(layer), episode),
            'description': f"Layer {layer.split()[-1]} of the narrative"
        }
    
    def get_all_layers(self) -> List[str]:
        """Get list of all available layers."""
        return ["Layer 1", "Layer 2", "Layer 3"] 
||||||| 73f7c15e6
=======
from typing import Dict, List, Optional
import json
import os

class LayerTransitionManager:
    def __init__(self, questions_path: str = None):
        self.questions_path = questions_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'key_questions.json'
        )
        self.questions = self._load_questions()
    
    def _load_questions(self) -> Dict:
        """Load key questions from JSON files."""
        if os.path.exists(self.questions_path):
            with open(self.questions_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_key_question(self, current_layer: str, next_layer: str, 
                        episode: str = "Beginning") -> Optional[str]:
        """Get key question for transitioning between layers."""
        transition_key = f"{current_layer}_to_{next_layer}"
        return self.questions.get(episode, {}).get(
            'layer_transitions', {}
        ).get(transition_key, {}).get('question')
    
    def get_next_layer(self, current_layer: str) -> Optional[str]:
        """Get next layer based on current layer."""
        if current_layer == "Layer 1":
            return "Layer 2"
        elif current_layer == "Layer 2":
            return "Layer 3"
        return None
    
    def can_transition(self, current_state: Dict) -> bool:
        """Check if transition to next layer is possible."""
        current_layer = current_state.get('current_layer')
        if not current_layer:
            return False
        
        # Check if all nodes in current layer are completed
        current_nodes = current_state.get('layers', {}).get(current_layer, {}).get('nodes', [])
        completed_nodes = current_state.get('completed_nodes', [])
        
        return all(node['id'] in completed_nodes for node in current_nodes)
    
    def transition_to_next_layer(self, current_state: Dict) -> Dict:
        """Transition to next layer if possible."""
        new_state = current_state.copy()
        current_layer = new_state.get('current_layer')
        next_layer = self.get_next_layer(current_layer)
        
        if next_layer and self.can_transition(current_state):
            new_state['current_layer'] = next_layer
            # Initialize available nodes for new layer
            if next_layer not in new_state['layers']:
                new_state['layers'][next_layer] = {'nodes': []}
            new_state['available_nodes'] = [
                node['id'] for node in new_state['layers'][next_layer]['nodes']
            ]
        
        return new_state
    
    def get_layer_info(self, layer: str, episode: str = "Beginning") -> Dict:
        """Get information about a specific layer."""
        return {
            'number': int(layer.split()[-1]),
            'key_question': self.get_key_question(layer, self.get_next_layer(layer), episode),
            'description': f"Layer {layer.split()[-1]} of the narrative"
        }
    
    def get_all_layers(self) -> List[str]:
        """Get list of all available layers."""
        return ["Layer 1", "Layer 2", "Layer 3"] 
>>>>>>> fe5206a7596bb44889a38717f23363f9e0fbf95e
