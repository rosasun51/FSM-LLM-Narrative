"""
This module contains tests for the Task class and related functionality.
"""

import unittest
from Generate_branches.models.task import Task
from Generate_branches.models.subtask import ScriptedSubTask
from Generate_branches.models.state import GameState

class TestTask(unittest.TestCase):
    """
    Tests for the Task class.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test task
        self.task = Task(
            task_id="test_task",
            title="Test Task",
            description="A task for testing",
            location_id="test_location",
            timestamp=0
        )
        
        # Create subtasks for testing
        self.subtask1 = ScriptedSubTask(
            subtask_id="test_subtask_1",
            title="Test Subtask 1",
            description="First test subtask",
            dialogue="This is test dialogue 1",
            layer=0
        )
        
        self.subtask2 = ScriptedSubTask(
            subtask_id="test_subtask_2",
            title="Test Subtask 2",
            description="Second test subtask",
            dialogue="This is test dialogue 2",
            layer=1
        )
        
        # Create game state
        self.game_state = GameState()
        
    def test_add_subtask(self):
        """Test adding subtasks to a task."""
        # Add subtasks
        self.task.add_subtask(self.subtask1)
        self.task.add_subtask(self.subtask2)
        
        # Check subtasks were added
        self.assertEqual(len(self.task.subtasks), 2)
        self.assertIn(self.subtask1, self.task.subtasks)
        self.assertIn(self.subtask2, self.task.subtasks)
        
        # Check they're sorted by layer
        self.assertEqual(self.task.subtasks[0], self.subtask1)
        self.assertEqual(self.task.subtasks[1], self.subtask2)
        
    def test_get_active_subtask(self):
        """Test getting the active subtask."""
        # Add subtasks
        self.task.add_subtask(self.subtask1)
        self.task.add_subtask(self.subtask2)
        
        # First subtask should be active initially
        active_subtask = self.task.get_active_subtask(self.game_state)
        self.assertEqual(active_subtask, self.subtask1)
        
        # Mark first subtask as completed
        self.subtask1.mark_completed()
        
        # Second subtask should now be active
        active_subtask = self.task.get_active_subtask(self.game_state)
        self.assertEqual(active_subtask, self.subtask2)
        
        # Mark second subtask as completed
        self.subtask2.mark_completed()
        
        # No active subtasks, task should be completed
        active_subtask = self.task.get_active_subtask(self.game_state)
        self.assertIsNone(active_subtask)
        self.assertTrue(self.task.completed)
        
    def test_to_dict(self):
        """Test converting task to dictionary."""
        # Add subtasks
        self.task.add_subtask(self.subtask1)
        
        # Convert to dict
        task_dict = self.task.to_dict()
        
        # Check dict contains expected fields
        self.assertEqual(task_dict["task_id"], "test_task")
        self.assertEqual(task_dict["title"], "Test Task")
        self.assertEqual(task_dict["description"], "A task for testing")
        self.assertEqual(task_dict["location_id"], "test_location")
        self.assertEqual(task_dict["timestamp"], 0)
        self.assertFalse(task_dict["completed"])
        self.assertEqual(len(task_dict["subtasks"]), 1)
        
    def test_from_dict(self):
        """Test creating task from dictionary."""
        # Create a task dict
        task_dict = {
            "task_id": "dict_task",
            "title": "Dict Task",
            "description": "A task from dict",
            "location_id": "dict_location",
            "timestamp": 5,
            "completed": True,
            "subtasks": [
                {
                    "subtask_id": "dict_subtask",
                    "title": "Dict Subtask",
                    "description": "A subtask from dict",
                    "dialogue": "Dict dialogue",
                    "layer": 0,
                    "completed": False,
                    "type": "ScriptedSubTask",
                    "npc_reactions": {},
                    "player_options": [],
                    "next_transitioning_question": None
                }
            ]
        }
        
        # Create task from dict
        task = Task.from_dict(task_dict)
        
        # Check task has expected attributes
        self.assertEqual(task.task_id, "dict_task")
        self.assertEqual(task.title, "Dict Task")
        self.assertEqual(task.description, "A task from dict")
        self.assertEqual(task.location_id, "dict_location")
        self.assertEqual(task.timestamp, 5)
        self.assertTrue(task.completed)
        self.assertEqual(len(task.subtasks), 1)
        self.assertEqual(task.subtasks[0].subtask_id, "dict_subtask")
        
if __name__ == "__main__":
    unittest.main() 