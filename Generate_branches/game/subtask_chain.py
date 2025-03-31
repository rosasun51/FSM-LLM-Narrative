"""
This module defines the SubTaskChain class that organizes subtasks within a task.
A SubTaskChain contains subtasks organized into layers, representing different
narrative paths within a task.
"""

from Generate_branches.models.subtask import SubTask, ScriptedSubTask, GeneratedSubTask
from Generate_branches.llm.LLM_integration import LLMHandler

class SubTaskChain:
    """
    Represents a chain of subtasks within a task.
    Subtasks are organized into layers, and each layer may contain
    multiple subtasks representing different possibilities.
    """
    def __init__(self, chain_id, task_id, name, description):
        self.chain_id = chain_id
        self.task_id = task_id
        self.name = name
        self.description = description
        self.layers = {}  # Layer ID to Layer object mapping
        self.current_layer_id = None
        self.llm_handler = LLMHandler()  # For generating subtasks
        
    def add_layer(self, layer):
        """Add a layer to this chain."""
        self.layers[layer.layer_id] = layer
        # If this is the first layer, set it as current
        if self.current_layer_id is None:
            self.current_layer_id = layer.layer_id
            
    def get_layers(self):
        """Get all layers in this chain."""
        return list(self.layers.values())
        
    def get_layer(self, layer_id):
        """Get a layer by its ID."""
        return self.layers.get(layer_id)
        
    def get_current_layer(self):
        """Get the currently active layer."""
        return self.layers.get(self.current_layer_id)
        
    def advance_to_next_layer(self):
        """Advance to the next layer in the chain."""
        # This is a simplified version - in a real game, you might
        # have more complex logic for determining the next layer
        sorted_layers = sorted(self.layers.values(), key=lambda x: x.layer_id)
        
        for i, layer in enumerate(sorted_layers):
            if layer.layer_id == self.current_layer_id and i < len(sorted_layers) - 1:
                self.current_layer_id = sorted_layers[i + 1].layer_id
                return True
                
        return False  # No next layer
    
    def get_active_subtasks(self, game_state):
        """Get all active subtasks in the current layer."""
        current_layer = self.get_current_layer()
        if not current_layer:
            return []
            
        return current_layer.get_active_subtasks(game_state)
        
    def generate_subtasks(self, transitioning_question, previous_subtask, game_state, count=3, threshold=50):
        """
        Generate subtasks using the LLM based on a transitioning question.
        
        This method now uses the hierarchical narrative structure approach internally,
        while maintaining backward compatibility with the original interface.
        
        Args:
            transitioning_question: Question that transitions between subtasks
            previous_subtask: The subtask that led to this generation
            game_state: Current game state
            count: Number of subtasks to generate
            threshold: Minimum rating threshold for subtasks (0-100)
            
        Returns:
            List of generated SubTask objects
        """
        generated_subtasks = []
        
        try:
            # Create a minimal task_info for the hierarchical generator
            task_info = {
                "name": f"Generated from {transitioning_question}",
                "description": transitioning_question,
                "environment": "Continuing from previous narrative context"
            }
            
            # Get current layer if available
            current_layer = 1
            if hasattr(previous_subtask, 'layer'):
                current_layer = previous_subtask.layer
            
            # Get parent ID
            parent_id = getattr(previous_subtask, 'subtask_id', "1")
            
            # Use the hierarchical narrative generator internally
            narrative_structure = self.llm_handler.generate_hierarchical_narrative(task_info)
            
            # Extract only the generated alternatives that are relevant
            alt_subtasks = [
                subtask for subtask in narrative_structure.get("generated_subtasks", [])
                if subtask.get("layer", 0) == current_layer
            ]
            
            # Sort by rating if available and limit to requested count
            alt_subtasks.sort(
                key=lambda x: x.get("rating", 0), 
                reverse=True
            )
            alt_subtasks = alt_subtasks[:count]
            
            # Convert to GeneratedSubTask objects
            for i, subtask_data in enumerate(alt_subtasks):
                subtask = GeneratedSubTask(
                    subtask_id=f"gen_{self.task_id}_{i}",
                    title=subtask_data.get("title", f"Alternative {i+1}"),
                    description=subtask_data.get("description", ""),
                    dialogue=subtask_data.get("dialogue", ""),
                    npc_reactions=subtask_data.get("npc_reactions", {}),
                    player_options=subtask_data.get("player_options", []),
                    layer=current_layer,
                    generation_score=subtask_data.get("rating", 80),
                    transitioning_question=transitioning_question,
                    parent_id=parent_id
                )
                generated_subtasks.append(subtask)
                
            return generated_subtasks
            
        except Exception as e:
            # Fallback to original implementation for backward compatibility
            from Generate_branches.utils.helpers import log_message
            log_message(f"Error using hierarchical generation: {e}. Falling back to legacy method.", "WARNING")
            
            # Generate multiple subtask possibilities
            for i in range(count):
                generated_data = self.llm_handler.generate_subtask(
                    game_state, 
                    transitioning_question,
                    previous_subtask
                )
                
                # Create a generated subtask from the data
                subtask = GeneratedSubTask(
                    subtask_id=f"gen_{self.task_id}_{len(generated_subtasks)}",
                    title=generated_data["title"],
                    description=generated_data["description"],
                    dialogue=generated_data["dialogue"],
                    npc_reactions=generated_data.get("npc_reactions", {}),
                    player_options=generated_data.get("player_options", []),
                    transitioning_question=transitioning_question
                )
                
                generated_subtasks.append(subtask)
                
            # Rate the generated subtasks
            rated_subtasks = self.llm_handler.rate_generated_subtasks(
                game_state,
                transitioning_question,
                previous_subtask,
                [subtask.__dict__ for subtask in generated_subtasks],
                threshold
            )
            
            # Update subtasks with their ratings and return those that pass the threshold
            result_subtasks = []
            for i, (subtask_dict, rating) in enumerate(rated_subtasks):
                generated_subtasks[i].generation_score = rating
                result_subtasks.append(generated_subtasks[i])
                
            return result_subtasks
    
    def to_dict(self):
        """Convert subtask chain to dictionary for storage/serialization."""
        return {
            "chain_id": self.chain_id,
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "current_layer_id": self.current_layer_id,
            "layers": {layer_id: layer.to_dict() for layer_id, layer in self.layers.items()}
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a SubTaskChain instance from dictionary data."""
        from Generate_branches.models.layer import Layer
        
        chain = cls(
            chain_id=data["chain_id"],
            task_id=data["task_id"],
            name=data["name"],
            description=data["description"]
        )
        
        chain.current_layer_id = data.get("current_layer_id")
        
        # First pass: load all subtasks
        all_subtasks = {}
        for layer_data in data.get("layers", {}).values():
            for subtask_id in layer_data.get("subtask_ids", []):
                # In a real implementation, you would load the subtask from storage
                # For now, we'll assume subtasks are loaded elsewhere
                pass
                
        # Second pass: load all layers
        for layer_id, layer_data in data.get("layers", {}).items():
            layer = Layer.from_dict(layer_data, all_subtasks)
            chain.add_layer(layer)
            
        return chain 