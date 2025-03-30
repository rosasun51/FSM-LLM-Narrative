"""
This module defines the GameManager class that orchestrates the entire game flow.
It manages task chains, game state, and player interactions.
"""

from Generate_branches.models.state import GameState
from Generate_branches.game.task_chain import TaskChain
from Generate_branches.models.subtask import SubTask, ScriptedSubTask, GeneratedSubTask
from Generate_branches.llm.LLM_integration import LLMHandler

class GameManager:
    """
    Manages the overall game flow, including tasks, subtasks, and game state.
    """
    def __init__(self, game_name="LLM Narrative Game"):
        self.game_name = game_name
        self.game_state = GameState()
        self.task_chains = {}  # Dict of chain_id to TaskChain
        self.current_chain_id = None
        self.current_task_id = None
        self.current_subtask_id = None
        self.llm_handler = LLMHandler()
        
    def add_task_chain(self, task_chain):
        """Add a task chain to the game."""
        self.task_chains[task_chain.chain_id] = task_chain
        # If this is the first chain, set it as current
        if self.current_chain_id is None:
            self.current_chain_id = task_chain.chain_id
            
    def get_current_chain(self):
        """Get the currently active task chain."""
        return self.task_chains.get(self.current_chain_id)
        
    def get_current_task(self):
        """Get the currently active task."""
        current_chain = self.get_current_chain()
        if not current_chain:
            return None
            
        if self.current_task_id:
            return current_chain.get_task_by_id(self.current_task_id)
        else:
            # Get the first active task in the chain
            return current_chain.get_active_task(self.game_state)
            
    def get_current_subtask(self):
        """Get the currently active subtask."""
        current_task = self.get_current_task()
        if not current_task:
            return None
            
        return current_task.get_active_subtask(self.game_state)
        
    def advance_to_next_subtask(self, complete_current=True):
        """
        Advance to the next subtask.
        
        Args:
            complete_current: Whether to mark the current subtask as completed
        
        Returns:
            The new current subtask, or None if there are no more
        """
        current_task = self.get_current_task()
        current_subtask = self.get_current_subtask()
        
        if current_subtask and complete_current:
            current_subtask.mark_completed()
            
        # Get the new active subtask (might be in the same task or a new one)
        new_subtask = current_task.get_active_subtask(self.game_state)
        
        # If no more subtasks in this task, move to the next task
        if not new_subtask and current_task:
            current_task.mark_completed()
            current_chain = self.get_current_chain()
            next_task = current_chain.get_next_task(current_task)
            
            if next_task:
                self.current_task_id = next_task.task_id
                new_subtask = next_task.get_active_subtask(self.game_state)
            else:
                # If no more tasks in this chain, could move to next chain
                # For now, we'll just end
                self.current_task_id = None
                
        if new_subtask:
            self.current_subtask_id = new_subtask.subtask_id
        else:
            self.current_subtask_id = None
            
        return new_subtask
        
    def handle_player_input(self, player_input):
        """
        Handle input from the player and progress the game accordingly.
        
        Args:
            player_input: The player's input text or choice
            
        Returns:
            Dict containing the game's response
        """
        current_subtask = self.get_current_subtask()
        if not current_subtask:
            return {"message": "No active subtask to respond to."}
            
        # Execute the current subtask with player input
        result = current_subtask.execute(self.game_state, player_input)
        
        # Check if we need to generate new subtasks
        if (isinstance(current_subtask, ScriptedSubTask) and 
                current_subtask.next_transitioning_question and 
                "transitioning_question" in result):
            
            # This is where we would integrate with the generation system
            # to create dynamic subtasks based on the transitioning question
            transitioning_question = result["transitioning_question"]
            
            # Here we'd check if the next scripted subtask is appropriate
            # or if we need to generate alternatives
            # For simplicity, we'll just log the question
            print(f"Transitioning question: {transitioning_question}")
            
        # Advance the game
        self.advance_to_next_subtask()
        
        # Prepare the response
        response = {
            "dialogue": result.get("dialogue", ""),
            "npc_reactions": result.get("npc_reactions", {}),
            "player_options": result.get("player_options", []),
        }
        
        return response
        
    def generate_subtasks_for_transition(self, scripted_subtask, next_scripted_subtask, player_input):
        """
        Generate alternative subtasks for a transition between scripted subtasks.
        
        Args:
            scripted_subtask: The current scripted subtask
            next_scripted_subtask: The next scripted subtask in the chain
            player_input: The player's input that triggered the transition
            
        Returns:
            List of generated subtasks that meet the threshold
        """
        if not scripted_subtask.next_transitioning_question:
            return []
            
        # Get the transitioning question
        transitioning_question = scripted_subtask.next_transitioning_question
        
        # Generate subtasks for the transition
        from Generate_branches.game.subtask_chain import SubTaskChain
        
        # Creating a temporary subtask chain for generation
        subtask_chain = SubTaskChain(
            chain_id="temp",
            task_id=self.current_task_id,
            name="Temporary Chain",
            description="Temporary chain for subtask generation"
        )
        
        # Generate possible subtasks
        generated_subtasks = subtask_chain.generate_subtasks(
            transitioning_question,
            scripted_subtask,
            self.game_state,
            count=3,
            threshold=50
        )
        
        return generated_subtasks
    
    def save_game(self, filename):
        """Save the current game state to a file."""
        import json
        
        game_data = {
            "game_name": self.game_name,
            "current_chain_id": self.current_chain_id,
            "current_task_id": self.current_task_id,
            "current_subtask_id": self.current_subtask_id,
            "game_state": self.game_state.get_state_summary(),
            "task_chains": {chain_id: chain.to_dict() for chain_id, chain in self.task_chains.items()}
        }
        
        with open(filename, 'w') as f:
            json.dump(game_data, f, indent=4)
            
        print(f"Game saved to {filename}")
        
    @classmethod
    def load_game(cls, filename):
        """Load a game from a saved file."""
        import json
        
        with open(filename, 'r') as f:
            game_data = json.load(f)
            
        # Create a new game manager
        manager = cls(game_name=game_data.get("game_name", "Loaded Game"))
        
        # Load task chains
        for chain_id, chain_data in game_data.get("task_chains", {}).items():
            chain = TaskChain.from_dict(chain_data)
            manager.add_task_chain(chain)
            
        # Set current state
        manager.current_chain_id = game_data.get("current_chain_id")
        manager.current_task_id = game_data.get("current_task_id")
        manager.current_subtask_id = game_data.get("current_subtask_id")
        
        # Load game state
        # In a real implementation, you would reconstruct the full GameState
        # from the saved data here
        
        return manager 