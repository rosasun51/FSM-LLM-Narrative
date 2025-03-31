"""
This module defines the Task class which represents a single task in a game episode.
Tasks are organized into Task_chains based on physical location.
"""

class Task:
    """
    Represents a single task in a game episode, which happens at a specific location and time.
    """
    def __init__(self, task_id, title, description, location_id, timestamp):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.location_id = location_id  # The physical spot where this task happens
        self.timestamp = timestamp  # When this task happens in the game timeline
        self.subtasks = []  # List of SubTask objects for this task
        self.completed = False
        
    def add_subtask(self, subtask):
        """Add a subtask to this task."""
        self.subtasks.append(subtask)
        # Sort subtasks by layer
        self.subtasks.sort(key=lambda x: x.layer)
        
    def get_active_subtask(self, game_state):
        """
        Get the currently active subtask based on game state.
        
        This method returns the first uncompleted subtask in order.
        If all subtasks are completed, the task is marked as completed.
        
        Args:
            game_state: Current game state containing completion information
            
        Returns:
            The active subtask or None if all are completed or no subtasks exist
        """
        # Quick return if there are no subtasks
        if not self.subtasks:
            return None
        
        # Check for completed subtasks
        completed_subtasks = [
            subtask for subtask in self.subtasks 
            if subtask.is_completed(game_state)
        ]
        
        # If all subtasks are completed, mark the task as completed
        if len(completed_subtasks) == len(self.subtasks):
            self.completed = True
            return None
        
        # Find the first uncompleted subtask (they're already sorted by layer)
        for subtask in self.subtasks:
            if subtask not in completed_subtasks:
                return subtask
        
        # Fallback (should not reach here if logic is correct)
        return None
        
    def mark_completed(self):
        """Mark this task as completed."""
        self.completed = True
        
    def to_dict(self):
        """Convert task to dictionary for storage/serialization."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "location_id": self.location_id,
            "timestamp": self.timestamp,
            "completed": self.completed,
            "subtasks": [subtask.to_dict() for subtask in self.subtasks]
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a Task instance from dictionary data."""
        from Generate_branches.models.subtask import SubTask  # Import here to avoid circular imports
        
        task = cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data["description"],
            location_id=data["location_id"],
            timestamp=data["timestamp"]
        )
        
        task.completed = data.get("completed", False)
        
        # Load subtasks
        for subtask_data in data.get("subtasks", []):
            subtask = SubTask.from_dict(subtask_data)
            task.add_subtask(subtask)
            
        return task 