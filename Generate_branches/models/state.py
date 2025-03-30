"""
This module handles the state management for NPCs and game progression.
It keeps track of character states, player progress, and game world state.
"""

class NPCState:
    """
    Represents the current state of an NPC character.
    """
    def __init__(self, npc_id, name, initial_traits=None, initial_relationships=None):
        self.npc_id = npc_id
        self.name = name
        self.traits = initial_traits or {}
        self.relationships = initial_relationships or {}
        self.memory = []  # List of interactions with the player
        self.current_location = None
        
    def update_trait(self, trait_name, value):
        """Update a character trait."""
        self.traits[trait_name] = value
        
    def update_relationship(self, other_character_id, relationship_value):
        """Update relationship with another character."""
        self.relationships[other_character_id] = relationship_value
        
    def add_memory(self, interaction):
        """Add a new interaction to the NPC's memory."""
        self.memory.append(interaction)
        
    def move_to_location(self, location_id):
        """Move NPC to a new location."""
        self.current_location = location_id
        
    def get_state_summary(self):
        """Return a summary of the NPC's current state for LLM consumption."""
        return {
            "name": self.name,
            "traits": self.traits,
            "relationships": self.relationships,
            "recent_memories": self.memory[-5:] if self.memory else [],
            "location": self.current_location
        }


class GameState:
    """
    Represents the overall state of the game, including player progress and world state.
    """
    def __init__(self):
        self.npcs = {}  # NPC ID to NPCState mapping
        self.completed_tasks = []
        self.active_tasks = []
        self.player_inventory = []
        self.player_location = None
        self.world_state = {}  # Key-value pairs representing world state
        self.game_timestamp = 0  # Game time counter
        
    def register_npc(self, npc_state):
        """Register an NPC in the game state."""
        self.npcs[npc_state.npc_id] = npc_state
        
    def advance_time(self, time_units=1):
        """Advance the game time."""
        self.game_timestamp += time_units
        return self.game_timestamp
        
    def complete_task(self, task_id):
        """Mark a task as completed."""
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)
        self.completed_tasks.append(task_id)
        
    def activate_task(self, task_id):
        """Add a task to active tasks."""
        if task_id not in self.active_tasks and task_id not in self.completed_tasks:
            self.active_tasks.append(task_id)
            
    def update_world_state(self, key, value):
        """Update a world state variable."""
        self.world_state[key] = value
        
    def move_player(self, location_id):
        """Move player to a new location."""
        self.player_location = location_id
        
    def get_state_summary(self):
        """Return a summary of the game state for LLM consumption."""
        return {
            "timestamp": self.game_timestamp,
            "player_location": self.player_location,
            "active_tasks": self.active_tasks,
            "completed_tasks": self.completed_tasks,
            "world_state": self.world_state,
            "npcs": {npc_id: npc.get_state_summary() for npc_id, npc in self.npcs.items()}
        }
