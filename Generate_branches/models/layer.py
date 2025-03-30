"""
This module defines the Layer class used to organize SubTasks within a Task.
Layers help align subtasks in a structured way within the game narrative.
"""

class Layer:
    """
    Represents a layer that organizes SubTasks within a Task.
    Layers can be used to group subtasks that represent alternative paths
    or to structure the narrative flow.
    """
    def __init__(self, layer_id, name, description, priority=0):
        self.layer_id = layer_id
        self.name = name
        self.description = description
        self.priority = priority  # Higher priority layers are considered first
        self.subtasks = []  # SubTasks assigned to this layer
        
    def add_subtask(self, subtask):
        """Add a subtask to this layer."""
        self.subtasks.append(subtask)
        # Update the subtask's layer attribute
        subtask.layer = self.layer_id
        
    def get_subtasks(self):
        """Get all subtasks in this layer."""
        return self.subtasks
        
    def get_active_subtasks(self, game_state):
        """Get subtasks that are active based on the current game state."""
        active_subtasks = []
        for subtask in self.subtasks:
            if not subtask.is_completed(game_state):
                active_subtasks.append(subtask)
        return active_subtasks
    
    def to_dict(self):
        """Convert layer to dictionary for storage/serialization."""
        return {
            "layer_id": self.layer_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "subtask_ids": [subtask.subtask_id for subtask in self.subtasks]
        }
    
    @classmethod
    def from_dict(cls, data, subtasks_dict=None):
        """
        Create a Layer instance from dictionary data.
        
        Args:
            data: Dictionary containing layer data
            subtasks_dict: Dictionary mapping subtask_id to SubTask objects
        """
        layer = cls(
            layer_id=data["layer_id"],
            name=data["name"],
            description=data["description"],
            priority=data.get("priority", 0)
        )
        
        # Add subtasks if provided
        if subtasks_dict:
            for subtask_id in data.get("subtask_ids", []):
                if subtask_id in subtasks_dict:
                    layer.add_subtask(subtasks_dict[subtask_id])
                    
        return layer 