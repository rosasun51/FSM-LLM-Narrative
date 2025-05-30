import json, os
import datetime

from Generate_branches.llm.LLM_integration import LLMHandler
from Generate_branches.utils.helpers import log_message
from Generate_branches.models.task import Task
from Generate_branches.models.subtask import ScriptedSubTask, GeneratedSubTask
from Generate_branches.models.layer import Layer
from Generate_branches.game.task_chain import TaskChain
from Generate_branches.utils.constants import (
    NUM_LAYERS,
    LAYER_NAMES,
    LAYER_DESCRIPTIONS,
    LAYER_PRIORITIES,
    SCRIPTED_TASKS_PATH,
    GENERATED_CHAINS_PATH,
    DATA_ROOT_PATH
)

class BranchManager:
    """
    Manages the generation and tracking of narrative branches in the game.
    
    This class handles loading task data, generating subtask chains with branching
    narrative paths, and managing the state of these branches during gameplay.
    """
    
    def __init__(self, task_data_path=SCRIPTED_TASKS_PATH):
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

    def _generate_task_with_subtasks(self, task_data):
        """
        Generate a task with scripted and generated subtasks organized in a hierarchical tree structure.
        
        The tree structure has three layers below the root task:
        1. Layer 1: Sequential scripted subtasks based on the first transitioning question
        2. Layer 2: Generated subtasks based on the second transitioning question
        3. Layer 3: Generated subtasks based on the third transitioning question
        
        Args:
            task_data: Dictionary containing task data
            
        Returns:
            Generated Task object or None if generation fails
        """
        try:
            # Create task ID from name
            task_name = task_data.get("name", task_data.get("scene_name", ""))
            task_id = task_name.lower().replace(' ', '_')
            
            # Create the task (this is the root node with the proper task_id)
            task = Task(
                task_id=task_id,  # Use the derived task_id instead of hardcoded ROOT_TASK_ID
                title=task_name,
                description=task_data.get("environment", ""),
                location_id=task_data.get("location", "unknown"),
                timestamp=0  # Will be set during gameplay
            )
            
            # Use the new method to generate the complete narrative structure
            # Pass the task_id to use for the root ID instead of hardcoded "1"
            log_message(f"Generating hierarchical narrative for {task_name}", "INFO")
            narrative_structure = self.llm_handler.generate_hierarchical_narrative(task_data, task_id)
            
            # Create layers for organization
            layers = {}
            for i in range(1, NUM_LAYERS + 1):
                layers[i] = Layer(
                    layer_id=i,
                    name=LAYER_NAMES[i],
                    description=LAYER_DESCRIPTIONS[i],
                    priority=LAYER_PRIORITIES[i]
                )
            
            # Process all scripted subtasks
            for subtask_data in narrative_structure.get("scripted_subtasks", []):
                layer = subtask_data.get("layer", 1)
                
                scripted_subtask = ScriptedSubTask(
                    subtask_id=subtask_data.get("subtask_id", f"{task_id}.{layer}"),
                    title=subtask_data.get("title", f"Layer {layer} Subtask"),
                    description=subtask_data.get("description", ""),
                    dialogue=subtask_data.get("dialogue", ""),
                    npc_reactions=subtask_data.get("npc_reactions", {}),
                    player_options=subtask_data.get("player_options", []),
                    layer=layer,
                    next_transitioning_question="",  # Will be set later if needed
                    parent_id=subtask_data.get("parent_id", task_id)
                )
                
                # Set next transitioning question if not the last layer
                if layer < NUM_LAYERS and len(narrative_structure.get("transitioning_questions", [])) > layer:
                    scripted_subtask.next_transitioning_question = narrative_structure["transitioning_questions"][layer]
                
                # Add to layer and task
                layers[layer].add_subtask(scripted_subtask)
                task.add_subtask(scripted_subtask)
            
            # Process all generated subtasks (alternatives)
            for subtask_data in narrative_structure.get("generated_subtasks", []):
                layer = subtask_data.get("layer", 1)
                
                generated_subtask = GeneratedSubTask(
                    subtask_id=subtask_data.get("subtask_id", f"{task_id}.{layer}.{0}"),
                    title=subtask_data.get("title", f"Alternative for Layer {layer}"),
                    description=subtask_data.get("description", ""),
                    dialogue=subtask_data.get("dialogue", ""),
                    npc_reactions=subtask_data.get("npc_reactions", {}),
                    player_options=subtask_data.get("player_options", []),
                    transitioning_question=subtask_data.get("next_transitioning_question", ""),
                    layer=layer,
                    generation_score=subtask_data.get("rating", 80),
                    parent_id=subtask_data.get("parent_id", f"{task_id}.{layer}")
                )
                
                # Add to layer and task
                layers[layer].add_subtask(generated_subtask)
                task.add_subtask(generated_subtask)
            
            return task
            
        except Exception as e:
            log_message(f"Error generating task with subtasks: {e}", "ERROR")
            return None

    def save_task_chain(self, chain_id, output_path=GENERATED_CHAINS_PATH):
        """
        Save a generated task chain to a JSON file.
        
        Args:
            chain_id: ID of the chain to save
            output_path: Directory to save the file in (default will be overridden if task-specific directory exists)
        """
        try:
            # Check if chain exists
            if chain_id not in self.task_chains:
                log_message(f"Chain not found: {chain_id}", "ERROR")
                return
            
            # Get the chain
            chain = self.task_chains[chain_id]
            
            # Try to find a task-specific directory if one of the tasks has been processed
            task_specific_dir = None
            if chain.tasks:
                # Use first task in the chain for the directory name
                task = chain.tasks[0]
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = task.title.replace(' ', '_').replace('/', '_').replace('\\', '_')
                
                # Check if a task directory already exists in the data path
                data_root = os.path.join("Generate_branches", DATA_ROOT_PATH)
                
                # Look for existing task directories that match our task name
                if os.path.exists(data_root):
                    matching_dirs = [d for d in os.listdir(data_root) 
                                    if os.path.isdir(os.path.join(data_root, d)) and d.startswith(safe_title)]
                    
                    if matching_dirs:
                        # Use the most recent directory if multiple exist
                        matching_dirs.sort(reverse=True)  # Sort by timestamp (newest first)
                        task_specific_dir = os.path.join(data_root, matching_dirs[0])
                        log_message(f"Found existing task directory: {task_specific_dir}", "INFO")
                
                # If no existing directory found, create a new one
                if not task_specific_dir:
                    task_specific_dir = os.path.join(data_root, f"{safe_title}_{timestamp}")
                    os.makedirs(task_specific_dir, exist_ok=True)
                    log_message(f"Created new task directory: {task_specific_dir}", "INFO")
            
            # Determine where to save the file
            if task_specific_dir:
                # Save to the task-specific directory
                file_path = os.path.join(task_specific_dir, f"task_chain_{chain_id}.json")
            else:
                # Fall back to the default path
                full_path = os.path.join("Generate_branches", output_path)
                os.makedirs(full_path, exist_ok=True)
                file_path = os.path.join(full_path, f"{chain_id}.json")
            
            # Save to JSON file
            with open(file_path, 'w') as f:
                json.dump(chain.to_dict(), f, indent=2)
            
            log_message(f"Saved task chain to {file_path}", "INFO")
        except Exception as e:
            log_message(f"Error saving task chain: {e}", "ERROR")
    
    def load_task_chain(self, chain_id, input_path=GENERATED_CHAINS_PATH):
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