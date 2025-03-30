"""
This module defines the SubTask classes that represent different stages within a Task.
There are two types: ScriptedSubTask (manually created) and GeneratedSubTask (LLM generated).
"""

from abc import ABC, abstractmethod

class SubTask(ABC):
    """
    Base abstract class for all subtasks.
    """
    def __init__(self, subtask_id, title, description, layer=0):
        self.subtask_id = subtask_id
        self.title = title
        self.description = description
        self.layer = layer  # Layer to organize subtasks within a Task
        self.completed = False
        
    @abstractmethod
    def execute(self, game_state, player_input=None):
        """
        Execute this subtask based on game state and optional player input.
        Should be implemented by subclasses.
        """
        pass
        
    def mark_completed(self):
        """Mark this subtask as completed."""
        self.completed = True
        
    def is_completed(self, game_state):
        """Check if this subtask is completed."""
        return self.completed
        
    def to_dict(self):
        """Convert subtask to dictionary for storage/serialization."""
        return {
            "subtask_id": self.subtask_id,
            "title": self.title,
            "description": self.description,
            "layer": self.layer,
            "completed": self.completed,
            "type": self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a SubTask instance from dictionary data."""
        if data["type"] == "ScriptedSubTask":
            return ScriptedSubTask.from_dict(data)
        elif data["type"] == "GeneratedSubTask":
            return GeneratedSubTask.from_dict(data)
        else:
            raise ValueError(f"Unknown subtask type: {data['type']}")


class ScriptedSubTask(SubTask):
    """
    A manually designed subtask with predefined content and transitions.
    """
    def __init__(self, subtask_id, title, description, dialogue, npc_reactions=None, 
                 player_options=None, layer=0, next_transitioning_question=None):
        super().__init__(subtask_id, title, description, layer)
        self.dialogue = dialogue  # Main narrative text for this subtask
        self.npc_reactions = npc_reactions or {}  # Dict of NPC ID to reaction text
        self.player_options = player_options or []  # List of possible player responses
        self.next_transitioning_question = next_transitioning_question  # Question to next subtask
        
    def execute(self, game_state, player_input=None):
        """Execute this scripted subtask."""
        # Update game state based on this subtask
        # For a scripted subtask, this might involve updating NPC states,
        # advancing time, or triggering events
        
        result = {
            "dialogue": self.dialogue,
            "npc_reactions": self.npc_reactions,
            "player_options": self.player_options,
            "transitioning_question": self.next_transitioning_question
        }
        
        # If player has made a choice, process it
        if player_input and player_input in self.player_options:
            # Handle the player's choice
            pass
        
        return result
        
    def to_dict(self):
        """Convert to dictionary, adding scripted-specific fields."""
        base_dict = super().to_dict()
        base_dict.update({
            "dialogue": self.dialogue,
            "npc_reactions": self.npc_reactions,
            "player_options": self.player_options,
            "next_transitioning_question": self.next_transitioning_question
        })
        return base_dict
        
    @classmethod
    def from_dict(cls, data):
        """Create a ScriptedSubTask from dict data."""
        subtask = cls(
            subtask_id=data["subtask_id"],
            title=data["title"],
            description=data["description"],
            dialogue=data["dialogue"],
            npc_reactions=data.get("npc_reactions", {}),
            player_options=data.get("player_options", []),
            layer=data.get("layer", 0),
            next_transitioning_question=data.get("next_transitioning_question")
        )
        subtask.completed = data.get("completed", False)
        return subtask


class GeneratedSubTask(SubTask):
    """
    An LLM-generated subtask created based on a transitioning question.
    """
    def __init__(self, subtask_id, title, description, dialogue, npc_reactions=None,
                 player_options=None, layer=0, generation_score=0, 
                 transitioning_question=None):
        super().__init__(subtask_id, title, description, layer)
        self.dialogue = dialogue
        self.npc_reactions = npc_reactions or {}
        self.player_options = player_options or []
        self.generation_score = generation_score  # How highly this was rated by LLM
        self.transitioning_question = transitioning_question  # Question that led to this generation
        
    def execute(self, game_state, player_input=None):
        """Execute this generated subtask."""
        # Similar to ScriptedSubTask but might have additional logic
        # for generated content
        
        result = {
            "dialogue": self.dialogue,
            "npc_reactions": self.npc_reactions,
            "player_options": self.player_options,
            # Generated subtasks might lead to another generation
            "needs_generation": True
        }
        
        # Process player input if provided
        if player_input:
            # This might trigger further generation based on player choice
            pass
            
        return result
        
    def to_dict(self):
        """Convert to dictionary, adding generated-specific fields."""
        base_dict = super().to_dict()
        base_dict.update({
            "dialogue": self.dialogue,
            "npc_reactions": self.npc_reactions,
            "player_options": self.player_options,
            "generation_score": self.generation_score,
            "transitioning_question": self.transitioning_question
        })
        return base_dict
        
    @classmethod
    def from_dict(cls, data):
        """Create a GeneratedSubTask from dict data."""
        subtask = cls(
            subtask_id=data["subtask_id"],
            title=data["title"],
            description=data["description"],
            dialogue=data["dialogue"],
            npc_reactions=data.get("npc_reactions", {}),
            player_options=data.get("player_options", []),
            layer=data.get("layer", 0),
            generation_score=data.get("generation_score", 0),
            transitioning_question=data.get("transitioning_question")
        )
        subtask.completed = data.get("completed", False)
        return subtask 