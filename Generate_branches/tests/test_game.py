"""
This module contains tests for the game mechanics.
"""

import unittest
from Generate_branches.game.game_manager import GameManager
from Generate_branches.game.task_chain import TaskChain
from Generate_branches.models.task import Task
from Generate_branches.models.subtask import ScriptedSubTask
from Generate_branches.game.npc import NPC

class TestGameMechanics(unittest.TestCase):
    """
    Tests for the game mechanics.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a game manager
        self.game_manager = GameManager(game_name="Test Game")
        
        # Create an NPC
        self.npc = NPC(
            npc_id="test_butler",
            name="Test Butler",
            initial_traits={"loyalty": 80, "knowledge": 70},
            background="A loyal butler for testing purposes."
        )
        
        # Register the NPC with the game state
        self.game_manager.game_state.register_npc(self.npc.state)
        
        # Create a task chain
        self.task_chain = TaskChain(
            chain_id="test_chain",
            location_id="test_location",
            name="Test Chain",
            description="A chain for testing"
        )
        
        # Create a task
        self.task = Task(
            task_id="test_task",
            title="Test Task",
            description="A task for testing",
            location_id="test_location",
            timestamp=0
        )
        
        # Create subtasks
        self.subtask1 = ScriptedSubTask(
            subtask_id="test_subtask_1",
            title="Test Subtask 1",
            description="First test subtask",
            dialogue="This is test dialogue 1",
            npc_reactions={"test_butler": "nods politely"},
            player_options=["Option 1", "Option 2"],
            layer=0,
            next_transitioning_question="What happens after subtask 1?"
        )
        
        self.subtask2 = ScriptedSubTask(
            subtask_id="test_subtask_2",
            title="Test Subtask 2",
            description="Second test subtask",
            dialogue="This is test dialogue 2",
            npc_reactions={"test_butler": "looks concerned"},
            player_options=["Option A", "Option B"],
            layer=0,
            next_transitioning_question="What happens after subtask 2?"
        )
        
        # Add subtasks to task
        self.task.add_subtask(self.subtask1)
        self.task.add_subtask(self.subtask2)
        
        # Add task to chain
        self.task_chain.add_task(self.task)
        
        # Add chain to game manager
        self.game_manager.add_task_chain(self.task_chain)
        
        # Set current states
        self.game_manager.current_chain_id = "test_chain"
        self.game_manager.current_task_id = "test_task"
        self.game_manager.current_subtask_id = "test_subtask_1"
        
    def test_get_current_subtask(self):
        """Test getting the current subtask."""
        current_subtask = self.game_manager.get_current_subtask()
        self.assertEqual(current_subtask, self.subtask1)
        
    def test_advance_to_next_subtask(self):
        """Test advancing to the next subtask."""
        # Advance to next subtask
        next_subtask = self.game_manager.advance_to_next_subtask()
        
        # Check that we advanced to the second subtask
        self.assertEqual(next_subtask, self.subtask2)
        self.assertTrue(self.subtask1.completed)
        self.assertEqual(self.game_manager.current_subtask_id, "test_subtask_2")
        
        # Advance again (should complete the task)
        next_subtask = self.game_manager.advance_to_next_subtask()
        
        # Check that the task is completed
        self.assertIsNone(next_subtask)
        self.assertTrue(self.subtask2.completed)
        self.assertTrue(self.task.completed)
        
    def test_handle_player_input(self):
        """Test handling player input."""
        # Handle player input
        response = self.game_manager.handle_player_input("Option 1")
        
        # Check response
        self.assertIn("dialogue", response)
        self.assertIn("npc_reactions", response)
        self.assertIn("player_options", response)
        
        # Check that we advanced to the next subtask
        current_subtask = self.game_manager.get_current_subtask()
        self.assertEqual(current_subtask, self.subtask2)
        
    def test_npc_interaction(self):
        """Test NPC interaction."""
        # Update the NPC state
        self.npc.update_state(
            trait_updates={"knowledge": 90},
            relationship_updates={"player": 60}
        )
        
        # Check that the state was updated
        state_summary = self.npc.get_state_summary()
        self.assertEqual(state_summary["traits"]["knowledge"], 90)
        self.assertEqual(state_summary["relationships"]["player"], 60)
        
        # Add a memory
        self.npc.add_memory("The player asked about the secret passage.")
        
        # Check that the memory was added
        state_summary = self.npc.get_state_summary()
        self.assertIn("The player asked about the secret passage.", state_summary["recent_memories"])
        
if __name__ == "__main__":
    unittest.main() 