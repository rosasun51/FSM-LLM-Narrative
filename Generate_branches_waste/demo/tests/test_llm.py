"""
This module contains tests for the LLM integration.
"""

import unittest
from Generate_branches.llm.LLM_integration import LLMHandler
from Generate_branches.models.state import GameState, NPCState
from Generate_branches.models.subtask import GeneratedSubTask

class TestLLMIntegration(unittest.TestCase):
    """
    Tests for the LLM integration functionality.
    Note: These tests use mock implementations since we're not connecting
    to a real LLM API in the demo.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create LLM handler
        self.llm_handler = LLMHandler()
        
        # Create a game state for testing
        self.game_state = GameState()
        
        # Create an NPC state
        self.npc_state = NPCState(
            npc_id="test_npc",
            name="Test NPC",
            initial_traits={"friendliness": 70, "intelligence": 80},
            initial_relationships={"player": 50}
        )
        
        # Create a test subtask
        self.subtask = GeneratedSubTask(
            subtask_id="test_subtask",
            title="Test Subtask",
            description="A subtask for testing",
            dialogue="This is test dialogue",
            transitioning_question="What happens next?",
            layer=0
        )
        
    def test_generate_subtask(self):
        """Test generating a subtask."""
        # Generate a subtask
        result = self.llm_handler.generate_subtask(
            self.game_state,
            "What happens next?",
            self.subtask
        )
        
        # Check that we got a valid result
        self.assertIsNotNone(result)
        self.assertIn("title", result)
        self.assertIn("description", result)
        self.assertIn("dialogue", result)
        self.assertIn("player_options", result)
        
    def test_rate_generated_subtasks(self):
        """Test rating generated subtasks."""
        # Create some test subtasks to rate
        subtasks = [
            {
                "id": "generated_subtask_1",
                "title": "Unexpected Visitor",
                "description": "A mysterious stranger enters the scene, changing the dynamics.",
                "dialogue": "As you're about to respond, the door swings open...",
                "npc_reactions": {"npc_1": "looks surprised", "npc_2": "reaches for their weapon"},
                "player_options": ["Ask who they are", "Hide", "Greet them friendly"]
            },
            {
                "id": "generated_subtask_2",
                "title": "Sudden Realization",
                "description": "The character realizes something important about the situation.",
                "dialogue": "Wait a minute. That symbol on the wall...",
                "npc_reactions": {"npc_1": "follows your gaze", "npc_2": "seems uncomfortable"},
                "player_options": ["Ask about the symbol", "Pretend not to notice", "Take a closer look"]
            }
        ]
        
        # Rate the subtasks
        rated_subtasks = self.llm_handler.rate_generated_subtasks(
            self.game_state,
            "What happens next?",
            self.subtask,
            subtasks,
            threshold=30  # Low threshold to ensure we get results
        )
        
        # Check that we got rated subtasks
        self.assertIsNotNone(rated_subtasks)
        self.assertTrue(len(rated_subtasks) > 0)
        
        # Check the format of the rated subtasks
        for subtask, rating in rated_subtasks:
            self.assertIsInstance(subtask, dict)
            self.assertIsInstance(rating, int)
            self.assertTrue(0 <= rating <= 100)
        
    def test_generate_npc_response(self):
        """Test generating an NPC response."""
        # Generate a response
        response = self.llm_handler.generate_npc_response(
            self.npc_state,
            "Hello, can you help me?",
            self.game_state
        )
        
        # Check that we got a valid response
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        self.assertIn(self.npc_state.name, response)
        
if __name__ == "__main__":
    unittest.main() 