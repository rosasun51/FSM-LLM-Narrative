"""
This module defines the TaskChain class that organizes tasks at a specific physical location.
A TaskChain contains tasks sorted by their timestamp, representing the narrative flow at a location.
"""

class TaskChain:
    """
    Represents a chain of tasks at a specific physical location.
    Tasks in a chain are sorted by timestamp.
    """
    def __init__(self, chain_id, location_id, name, description):
        self.chain_id = chain_id
        self.location_id = location_id  # Physical spot where all tasks happen
        self.name = name
        self.description = description
        self.tasks = []  # List of Task objects
        
    def add_task(self, task):
        """
        Add a task to this chain.
        Ensures the task is for the correct location and sorts by timestamp.
        """
        if task.location_id != self.location_id:
            raise ValueError(f"Task location {task.location_id} doesn't match chain location {self.location_id}")
            
        self.tasks.append(task)
        # Sort tasks by timestamp
        self.tasks.sort(key=lambda x: x.timestamp)
        
    def get_tasks(self):
        """Get all tasks in this chain."""
        return self.tasks
        
    def get_active_task(self, game_state):
        """Get the currently active task based on game state."""
        # Find the first uncompleted task
        for task in self.tasks:
            if not task.completed:
                return task
        return None
        
    def get_next_task(self, current_task):
        """Get the next task after the current one."""
        if current_task not in self.tasks:
            return None
            
        current_index = self.tasks.index(current_task)
        if current_index < len(self.tasks) - 1:
            return self.tasks[current_index + 1]
        return None
        
    def get_task_by_id(self, task_id):
        """Get a task by its ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def to_dict(self):
        """Convert task chain to dictionary for storage/serialization."""
        return {
            "chain_id": self.chain_id,
            "location_id": self.location_id,
            "name": self.name,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks]
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a TaskChain instance from dictionary data."""
        from Generate_branches.models.task import Task  # Import here to avoid circular imports
        
        chain = cls(
            chain_id=data["chain_id"],
            location_id=data["location_id"],
            name=data["name"],
            description=data["description"]
        )
        
        # Load tasks
        for task_data in data.get("tasks", []):
            task = Task.from_dict(task_data)
            chain.add_task(task)
            
        return chain 