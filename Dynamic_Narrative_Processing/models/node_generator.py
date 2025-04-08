<<<<<<< HEAD
import json
import os
import uuid
from typing import Dict

class NodeGenerator:
    def __init__(self, templates_path: str = None):
        self.templates_path = templates_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'templates'
        )
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load node templates from JSON files."""
        templates = {}
        if os.path.exists(self.templates_path):
            for filename in os.listdir(self.templates_path):
                if filename.endswith('.json'):
                    layer = filename.replace('.json', '')
                    with open(os.path.join(self.templates_path, filename), 'r') as f:
                        templates[layer] = json.load(f)
        return templates
    
    def generate_node(self, player_input: str, current_state: Dict, position_score: float) -> Dict:
        """Generate a new narrative node based on player input and current state."""
        # Determine node type based on position score
        if position_score < 1.5:
            layer = 'layer1'
        elif position_score < 2.5:
            layer = 'layer2'
        else:
            layer = 'layer3'
        
        # Generate unique node ID
        node_id = f"{int(position_score)}.{str(uuid.uuid4())[:8]}"
        
        # Create new node
        new_node = {
            'id': node_id,
            'title': self._generate_title(player_input, layer),
            'description': self._generate_description(player_input, layer),
            'position_score': position_score,
            'player_input': player_input,
            'is_generated': True
        }
        
        return new_node
    
    def _generate_title(self, player_input: str, layer: str) -> str:
        """Generate a title for the new node."""
        templates = {
            'layer1': [
                "Exploring {input}",
                "Investigating {input}",
                "Understanding {input}"
            ],
            'layer2': [
                "Dealing with {input}",
                "Addressing {input}",
                "Responding to {input}"
            ],
            'layer3': [
                "Resolving {input}",
                "Concluding {input}",
                "Finalizing {input}"
            ]
        }
        
        # Use a simple template-based approach for now
        import random
        template = random.choice(templates[layer])
        return template.format(input=player_input[:30] + "...")
    
    def _generate_description(self, player_input: str, layer: str) -> str:
        """Generate a description for the new node."""
        templates = {
            'layer1': [
                "The player shows interest in {input}. This could lead to new discoveries.",
                "Focusing on {input} might reveal important information.",
                "Exploring {input} could be the key to understanding the situation."
            ],
            'layer2': [
                "The situation becomes more complex as {input} comes into play.",
                "Dealing with {input} presents new challenges and opportunities.",
                "Addressing {input} requires careful consideration of the consequences."
            ],
            'layer3': [
                "The narrative reaches a turning point with {input}.",
                "Resolving {input} will determine the final outcome.",
                "The story concludes as {input} is addressed."
            ]
        }
        
        import random
        template = random.choice(templates[layer])
        return template.format(input=player_input)
||||||| 73f7c15e6
=======
import json
import os
import uuid
from typing import Dict

class NodeGenerator:
    def __init__(self, templates_path: str = None):
        self.templates_path = templates_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'templates'
        )
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load node templates from JSON files."""
        templates = {}
        if os.path.exists(self.templates_path):
            for filename in os.listdir(self.templates_path):
                if filename.endswith('.json'):
                    layer = filename.replace('.json', '')
                    with open(os.path.join(self.templates_path, filename), 'r') as f:
                        templates[layer] = json.load(f)
        return templates
    
    def generate_node(self, player_input: str, current_state: Dict, position_score: float) -> Dict:
        """Generate a new narrative node based on player input and current state."""
        # Determine node type based on position score
        if position_score < 1.5:
            layer = 'layer1'
        elif position_score < 2.5:
            layer = 'layer2'
        else:
            layer = 'layer3'
        
        # Generate unique node ID
        node_id = f"{int(position_score)}.{str(uuid.uuid4())[:8]}"
        
        # Create new node
        new_node = {
            'id': node_id,
            'title': self._generate_title(player_input, layer),
            'description': self._generate_description(player_input, layer),
            'position_score': position_score,
            'player_input': player_input,
            'is_generated': True
        }
        
        return new_node
    
    def _generate_title(self, player_input: str, layer: str) -> str:
        """Generate a title for the new node."""
        templates = {
            'layer1': [
                "Exploring {input}",
                "Investigating {input}",
                "Understanding {input}"
            ],
            'layer2': [
                "Dealing with {input}",
                "Addressing {input}",
                "Responding to {input}"
            ],
            'layer3': [
                "Resolving {input}",
                "Concluding {input}",
                "Finalizing {input}"
            ]
        }
        
        # Use a simple template-based approach for now
        import random
        template = random.choice(templates[layer])
        return template.format(input=player_input[:30] + "...")
    
    def _generate_description(self, player_input: str, layer: str) -> str:
        """Generate a description for the new node."""
        templates = {
            'layer1': [
                "The player shows interest in {input}. This could lead to new discoveries.",
                "Focusing on {input} might reveal important information.",
                "Exploring {input} could be the key to understanding the situation."
            ],
            'layer2': [
                "The situation becomes more complex as {input} comes into play.",
                "Dealing with {input} presents new challenges and opportunities.",
                "Addressing {input} requires careful consideration of the consequences."
            ],
            'layer3': [
                "The narrative reaches a turning point with {input}.",
                "Resolving {input} will determine the final outcome.",
                "The story concludes as {input} is addressed."
            ]
        }
        
        import random
        template = random.choice(templates[layer])
        return template.format(input=player_input)
>>>>>>> fe5206a7596bb44889a38717f23363f9e0fbf95e
