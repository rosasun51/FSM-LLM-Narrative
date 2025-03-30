import json, os
from typing import Dict, List, Any, Optional

from Generate_branches.llm.LLM_integration import LLMHandler
from Generate_branches.utils.helpers import log_message
from Generate_branches.models.task import Task
from Generate_branches.models.subtask import ScriptedSubTask, GeneratedSubTask
from Generate_branches.models.layer import Layer
from Generate_branches.game.task_chain import TaskChain

class BranchManager:
    """
    Manages the generation and tracking of narrative branches in the game.
    
    This class handles loading task data, generating subtask chains with branching
    narrative paths, and managing the state of these branches during gameplay.
    """
    
    def __init__(self, task_data_path="data/Scripted_tasks.json"):
        """
        Initialize the branch manager.
        
        Args:
            task_data_path: Path to the JSON file containing scripted task data
        """
        self.task_data_path = task_data_path
        self.llm_handler = LLMHandler()
        self.task_chains = {}
        self.scripted_tasks = []
        
        # Load scripted tasks from JSON
        self._load_scripted_tasks()
    
    def _load_scripted_tasks(self):
        """
        Load scripted tasks from the JSON file.
        """
        try:
            # Build full path
            full_path = os.path.join("Generate_branches", self.task_data_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                log_message(f"Task data file not found: {full_path}", "ERROR")
                return
            
            # Load the JSON file
            with open(full_path, 'r') as f:
                self.scripted_tasks = json.load(f)
            
            log_message(f"Loaded {len(self.scripted_tasks)} scripted tasks", "INFO")
        except Exception as e:
            log_message(f"Error loading scripted tasks: {e}", "ERROR")
\
    def generate_task_chain(self, task_name):
        """
        Generate a task chain from a scripted task based on its name.
        
        Args:
            task_name: Name of the scripted task to generate a chain for
            
        Returns:
            Generated TaskChain or None if not found
        """
        # Find the task data
        task_data = None
        for task in self.scripted_tasks:
            if task.get("name") == task_name or task.get("scene_name") == task_name:
                task_data = task
                break
        
        if not task_data:
            log_message(f"Task not found: {task_name}", "ERROR")
            return None
        
        # Create a task chain
        location_id = task_data.get("location", "unknown")
        chain_id = f"{task_name.lower().replace(' ', '_')}_chain"
        
        task_chain = TaskChain(
            chain_id=chain_id,
            location_id=location_id,
            name=task_name,
            description=task_data.get("environment", "")
        )
        
        # Generate the task with subtasks
        task = self._generate_task_with_subtasks(task_data)
        
        # Add task to chain
        if task:
            task_chain.add_task(task)
            
            # Store in our dictionary
            self.task_chains[chain_id] = task_chain
            
            return task_chain
        
        return None
\
    def _generate_task_with_subtasks(self, task_data):
        """
        Generate a task with scripted and generated subtasks.
        
        Args:
            task_data: Dictionary containing task data
            
        Returns:
            Generated Task object or None if generation fails
        """
        try:
            # Create task ID from name
            task_name = task_data.get("name", task_data.get("scene_name", ""))
            task_id = task_name.lower().replace(' ', '_')
            
            # Create the task
            task = Task(
                task_id=task_id,
                title=task_name,
                description=task_data.get("environment", ""),
                location_id=task_data.get("location", "unknown"),
                timestamp=0  # Will be set during gameplay
            )
            
            # Generate key transitioning questions
            log_message(f"Generating transitioning questions for {task_name}", "INFO")
            key_questions = self.llm_handler.generate_key_questions(task_data)
            
            # Main path layer (scripted subtasks)
            main_layer = Layer(
                layer_id=0,
                name="Main Path",
                description="The primary scripted narrative path",
                priority=100
            )
            
            # Alternative paths layer (generated subtasks)
            alt_layer = Layer(
                layer_id=1,
                name="Alternative Paths",
                description="Branching narrative possibilities",
                priority=50
            )
            
            # Generate scripted subtasks for each question
            for i, question in enumerate(key_questions):
                subtask_id = f"{task_id}_scripted_{i+1}"
                
                # Generate the scripted subtask
                log_message(f"Generating scripted subtask for question: {question}", "INFO")
                subtask_data = self.llm_handler.generate_scripted_subtask(task_data, question)
                
                # Create the scripted subtask
                subtask = ScriptedSubTask(
                    subtask_id=subtask_id,
                    title=subtask_data.get("title", f"Subtask {i+1}"),
                    description=subtask_data.get("description", ""),
                    dialogue=subtask_data.get("dialogue", ""),
                    npc_reactions=subtask_data.get("npc_reactions", {}),
                    player_options=subtask_data.get("player_options", []),
                    layer=0,
                    next_transitioning_question=subtask_data.get("next_transitioning_question", "")
                )
                
                # Add to main layer
                main_layer.add_subtask(subtask)
                
                # Add to task
                task.add_subtask(subtask)
                
                # Generate alternative branches
                log_message(f"Generating alternative branches for question: {question}", "INFO")
                branches = self.llm_handler.generate_subtask_branches(task_data, question, subtask_data)
                
                # Create generated subtasks for branches
                for j, branch in enumerate(branches):
                    branch_id = f"{task_id}_generated_{i+1}_{j+1}"
                    
                    # Create the generated subtask
                    branch_subtask = GeneratedSubTask(
                        subtask_id=branch_id,
                        title=branch.get("title", f"Alternative {j+1}"),
                        description=branch.get("description", ""),
                        dialogue=branch.get("dialogue", ""),
                        npc_reactions=branch.get("npc_reactions", {}),
                        player_options=branch.get("player_options", []),
                        transitioning_question=branch.get("next_transitioning_question", ""),
                        layer=1
                    )
                    
                    # Add to alternative layer
                    alt_layer.add_subtask(branch_subtask)
                    
                    # Add to task
                    task.add_subtask(branch_subtask)
            
            return task
            
        except Exception as e:
            log_message(f"Error generating task with subtasks: {e}", "ERROR")
            return None
\
    def save_task_chain(self, chain_id, output_path="data/generated_chains"):
        """
        Save a generated task chain to a JSON file.
        
        Args:
            chain_id: ID of the chain to save
            output_path: Directory to save the file in
        """
        try:
            # Check if chain exists
            if chain_id not in self.task_chains:
                log_message(f"Chain not found: {chain_id}", "ERROR")
                return
            
            # Get the chain
            chain = self.task_chains[chain_id]
            
            # Create output directory if it doesn't exist
            full_path = os.path.join("Generate_branches", output_path)
            os.makedirs(full_path, exist_ok=True)
            
            # Save to JSON file
            file_path = os.path.join(full_path, f"{chain_id}.json")
            with open(file_path, 'w') as f:
                json.dump(chain.to_dict(), f, indent=2)
            
            log_message(f"Saved task chain to {file_path}", "INFO")
        except Exception as e:
            log_message(f"Error saving task chain: {e}", "ERROR")
    
    def load_task_chain(self, chain_id, input_path="data/generated_chains"):
        """
        Load a task chain from a JSON file.
        
        Args:
            chain_id: ID of the chain to load
            input_path: Directory to load the file from
            
        Returns:
            Loaded TaskChain or None if loading fails
        """
        try:
            # Build file path
            file_path = os.path.join("Generate_branches", input_path, f"{chain_id}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                log_message(f"Task chain file not found: {file_path}", "ERROR")
                return None
            
            # Load from JSON file
            with open(file_path, 'r') as f:
                chain_data = json.load(f)
            
            # Create task chain from data
            chain = TaskChain.from_dict(chain_data)
            
            # Store in our dictionary
            self.task_chains[chain_id] = chain
            
            log_message(f"Loaded task chain from {file_path}", "INFO")
            return chain
        except Exception as e:
            log_message(f"Error loading task chain: {e}", "ERROR")
            return None