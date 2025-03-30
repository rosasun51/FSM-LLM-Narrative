"""
This module defines the NPC class that manages non-player characters in the game.
NPCs can have different states and respond to player inputs using the LLM.
"""

from Generate_branches.models.state import NPCState
from Generate_branches.llm.LLM_integration import LLMHandler

class NPC:
    """
    Represents a non-player character (NPC) in the game.
    NPCs can interact with the player, have states, and generate dynamic responses.
    """
    def __init__(self, npc_id, name, initial_traits=None, initial_relationships=None, background=None):
        self.npc_id = npc_id
        self.name = name
        self.background = background or ""  # Backstory and personality description
        self.state = NPCState(npc_id, name, initial_traits, initial_relationships)
        self.llm_handler = LLMHandler()
        
    def generate_response(self, player_input, game_state):
        """
        Generate a response to player input.
        
        Args:
            player_input: The player's input text
            game_state: Current game state
            
        Returns:
            Generated response text
        """
        return self.llm_handler.generate_npc_response(self.state, player_input, game_state)
        
    def update_state(self, trait_updates=None, relationship_updates=None, new_location=None):
        """
        Update the NPC's state.
        
        Args:
            trait_updates: Dict of trait name to new value
            relationship_updates: Dict of character ID to new relationship value
            new_location: New location ID for the NPC
        """
        # Update traits
        if trait_updates:
            for trait_name, value in trait_updates.items():
                self.state.update_trait(trait_name, value)
                
        # Update relationships
        if relationship_updates:
            for char_id, value in relationship_updates.items():
                self.state.update_relationship(char_id, value)
                
        # Update location
        if new_location:
            self.state.move_to_location(new_location)
            
    def add_memory(self, interaction):
        """
        Add a memory of an interaction to the NPC's state.
        
        Args:
            interaction: Description of the interaction with the player
        """
        self.state.add_memory(interaction)
        
    def get_state_summary(self):
        """Get a summary of the NPC's current state."""
        return self.state.get_state_summary()
        
    def to_dict(self):
        """Convert NPC to dictionary for storage/serialization."""
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "background": self.background,
            "state": self.state.get_state_summary()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an NPC instance from dictionary data."""
        npc = cls(
            npc_id=data["npc_id"],
            name=data["name"],
            background=data.get("background", ""),
            initial_traits=data.get("state", {}).get("traits", {}),
            initial_relationships=data.get("state", {}).get("relationships", {})
        )
        
        # Restore memories if available
        for memory in data.get("state", {}).get("recent_memories", []):
            npc.add_memory(memory)
            
        # Set location if available
        location = data.get("state", {}).get("location")
        if location:
            npc.state.move_to_location(location)
            
        return npc 