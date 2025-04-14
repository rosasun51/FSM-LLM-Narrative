"""
This module provides integration with LLM services.
It handles prompting, response parsing, and other LLM-related functionality.
"""

import os
import json
import random
import datetime
from typing import Dict, List, Tuple, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import warnings

from Generate_branches.utils.constants import (
    LLM_MODEL, 
    LLM_BASE_URL, 
    LLM_API_KEY, 
    LLM_MAX_TOKENS, 
    LLM_MAX_TOKENS_BRANCHES,
    DEFAULT_NUM_ALTERNATIVES,
    MIN_RATING_THRESHOLD,
    NUM_LAYERS,
    ROOT_TASK_ID,
    DATA_ROOT_PATH,
    SCRIPTED_SUBTASK_FOLDER,
    SUBTASK_BRANCHES_FOLDER,
    KEY_QUESTIONS_FILE
)
from Generate_branches.utils.helpers import log_message
from Generate_branches.llm.prompt_templates import (
    SYSTEM_PROMPT,
    GENERATE_SUBTASK_PROMPT,
    GENERATE_NPC_RESPONSE_PROMPT,
    GENERATE_KEY_QUESTIONS_PROMPT
)

def _ensure_consistent_folder_structure(task_name: str) -> Tuple[str, str]:
    """
    Ensure consistent folder structure for a given task name.
    
    This helper function finds or creates the appropriate folder structure for a task,
    ensuring all files are saved with consistent organization and timestamps.
    
    Args:
        task_name: The name of the task
        
    Returns:
        Tuple of (task_dir, timestamp) where task_dir is the path to the task directory
        and timestamp is the timestamp to use for file naming
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Format task name for file system use
    safe_task_name = task_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    
    # Check if we already have an existing directory for this task
    existing_dir = None
    data_root = os.path.join("Generate_branches", DATA_ROOT_PATH)
    
    if os.path.exists(data_root):
        # Look for folders starting with the task name
        matching_dirs = [
            d for d in os.listdir(data_root) 
            if os.path.isdir(os.path.join(data_root, d)) and d.startswith(safe_task_name)
        ]
        
        if matching_dirs:
            # Use the most recent directory if multiple exist
            matching_dirs.sort(reverse=True)  # Sort by timestamp (newest first)
            existing_dir = matching_dirs[0]
    
    if existing_dir:
        # Use existing directory and extract its timestamp
        task_dir = os.path.join(data_root, existing_dir)
        # Extract timestamp from directory name
        dir_timestamp = existing_dir.replace(f"{safe_task_name}_", "")
        # Use the directory's timestamp for consistent naming
        timestamp = dir_timestamp
    else:
        # Create a new task-specific directory with a fresh timestamp
        task_dir = os.path.join(data_root, f"{safe_task_name}_{timestamp}")
    
    # Create the main task directory if it doesn't exist
    os.makedirs(task_dir, exist_ok=True)
    
    # Create subdirectories with the same timestamp
    scripted_subtask_dir = os.path.join(task_dir, f"{SCRIPTED_SUBTASK_FOLDER}_{timestamp}")
    os.makedirs(scripted_subtask_dir, exist_ok=True)
    
    branches_dir = os.path.join(task_dir, f"{SUBTASK_BRANCHES_FOLDER}_{timestamp}")
    os.makedirs(branches_dir, exist_ok=True)
    
    return task_dir, timestamp

# Add a function to save responses to JSON files
def save_llm_response(response_type, prompt, response, task_info=None):
    """
    Save LLM prompt and response to a JSON file for debugging.
    
    Args:
        response_type: Type of response (key_questions, scripted_subtask, etc.)
        prompt: The prompt sent to the LLM
        response: The raw response from the LLM
        task_info: Optional task information for context
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Prepare data to save
    data = {
        "timestamp": timestamp,
        "prompt": prompt,
        "raw_response": response,
        "task_info": task_info
    }
    
    # If we have task info with a name, use the organized folder structure
    if task_info and ('name' in task_info or 'scene_name' in task_info):
        # Get task name from task_info
        task_name = task_info.get('name', task_info.get('scene_name', ''))
        if task_name:
            # Use our helper function to ensure consistent folder structure
            task_dir, timestamp = _ensure_consistent_folder_structure(task_name)
            
            # Save files based on response type
            if response_type == "key_questions":
                # Save key questions to the task root directory
                file_path = os.path.join(task_dir, f"{KEY_QUESTIONS_FILE}_{timestamp}.json")
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                log_message(f"Saved key questions to {file_path}", "INFO")
                
            elif response_type == "scripted_subtask":
                # Extract layer information
                layer = task_info.get("layer", "unknown_layer") if isinstance(task_info, dict) else "unknown_layer"
                
                # Save to the scripted subtask directory
                subtask_dir = os.path.join(task_dir, f"{SCRIPTED_SUBTASK_FOLDER}_{timestamp}")
                file_path = os.path.join(subtask_dir, f"{response_type}_layer{layer}_{timestamp}.json")
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                log_message(f"Saved scripted subtask (layer {layer}) to {file_path}", "INFO")
                
            elif response_type == "subtask_branches":
                # Extract layer information
                layer = task_info.get("layer", "unknown_layer") if isinstance(task_info, dict) else "unknown_layer"
                
                # Save to the subtask branches directory
                branches_dir = os.path.join(task_dir, f"{SUBTASK_BRANCHES_FOLDER}_{timestamp}")
                file_path = os.path.join(branches_dir, f"{response_type}_layer{layer}_{timestamp}.json")
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                log_message(f"Saved subtask branches (layer {layer}) to {file_path}", "INFO")
                
            else:
                # For other types, save to the task root directory
                file_path = os.path.join(task_dir, f"{response_type}_{timestamp}.json")
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                log_message(f"Saved {response_type} to {file_path}", "INFO")
                
            return
    
    # Legacy path fallback (for backward compatibility or if we don't have task_info)
    # Create the responses directory if it doesn't exist
    os.makedirs("Generate_branches/llm/responses", exist_ok=True)
    
    # Create a unique filename with layer number if applicable
    if response_type in ["scripted_subtask", "subtask_branches"] and task_info and "layer" in task_info:
        layer = task_info["layer"]
        filename = f"Generate_branches/llm/responses/{response_type}_layer{layer}_{timestamp}.json"
    else:
        filename = f"Generate_branches/llm/responses/{response_type}_{timestamp}.json"
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Also append to aggregated file (legacy format)
    if response_type in ["scripted_subtask", "subtask_branches"] and task_info and "layer" in task_info:
        layer = task_info["layer"]
        aggregated_file = f"Generate_branches/llm/LLM_{response_type}_layer{layer}.json"
    else:
        aggregated_file = f"Generate_branches/llm/LLM_{response_type}.json"
    
    # If the file exists, load existing data
    if os.path.exists(aggregated_file):
        try:
            with open(aggregated_file, 'r') as f:
                aggregated_data = json.load(f)
                if not isinstance(aggregated_data, list):
                    aggregated_data = [aggregated_data]
        except:
            aggregated_data = []
    else:
        aggregated_data = []
    
    # Append new data
    aggregated_data.append(data)
    
    # Save updated data
    with open(aggregated_file, 'w') as f:
        json.dump(aggregated_data, f, indent=2)

class LLMHandler:
    """
    Handler for LLM interactions.
    
    This class provides methods for generating content using LLM models,
    including generating subtasks, NPC responses, and evaluating narrative branches.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the LLM handler.
        
        Args:
            api_key: API key for the LLM service (optional, defaults to env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", LLM_API_KEY)
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            base_url=LLM_BASE_URL,
            api_key=self.api_key
        )
        self.model = LLM_MODEL
        log_message(f"Initialized LLMHandler with model: {self.model}", "INFO")
    
    def _call_llm(self, prompt: str, max_tokens: int = LLM_MAX_TOKENS) -> str:
        """
        Call the LLM with a prompt and get a response.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text from the LLM
        """
        try:
            if self.api_key:
                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(
                    messages,
                    max_tokens=max_tokens
                )
                
                return response.content
            else:
                log_message("No API key provided, using mock LLM response", "WARNING")
                return log_message("No API key provided, using mock LLM response", "WARNING")
        except Exception as e:
            log_message(f"Error calling LLM: {e}", "ERROR")
            return log_message(f"Error calling LLM: {e}", "ERROR")
    
    # def _mock_llm_response(self, prompt: str) -> str:
    #     """
    #     Generate a mock LLM response for demo/testing.
        
    #     Args:
    #         prompt: The prompt that would be sent to the LLM
            
    #     Returns:
    #         Mock generated text
    #     """
    #     # Simple mock responses based on prompt content for demo purposes
    #     if "transitioning_question" in prompt.lower():
    #         return json.dumps({
    #             "title": "Unexpected Development",
    #             "description": "The situation takes an unexpected turn.",
    #             "dialogue": "Just as the conversation reaches a crucial point, the sound of footsteps approaching from the hallway catches everyone's attention.",
    #             "player_options": [
    #                 "Prepare for trouble",
    #                 "Maintain the conversation",
    #                 "Look for an exit"
    #             ],
    #             "npc_reactions": {
    #                 "npc_1": "looks anxiously toward the door",
    #                 "npc_2": "reaches subtly for a concealed weapon"
    #             }
    #         })
        
    #     elif "generate_subtask" in prompt.lower():
    #         return json.dumps({
    #             "title": "The Decision",
    #             "description": "A moment of truth that will shape the path forward.",
    #             "dialogue": "The choice before you is clear, but the consequences remain shrouded in uncertainty.",
    #             "player_options": [
    #                 "Accept the deal",
    #                 "Reject the offer",
    #                 "Attempt to negotiate"
    #             ],
    #             "npc_reactions": {
    #                 "npc_1": "watches you intently, awaiting your decision",
    #                 "npc_2": "seems indifferent, but you notice a subtle tension"
    #             }
    #         })
        
    #     elif "npc_response" in prompt.lower():
    #         return "The character considers your words carefully before responding with measured caution."
        
    #     elif "key questions" in prompt.lower():
    #         return json.dumps([
    #             "How does the initial interaction unfold?",
    #             "What complications arise during the task?",
    #             "How does the situation resolve?"
    #         ])
        
    #     else:
    #         return "The narrative continues with unexpected developments and emerging challenges."
    
    def generate_key_questions(self, task_info: Dict[str, Any]) -> List[str]: # ToDo: use  extract_key_questions() to obtain the questions from Scripted_tasks.json
        """
        Generate three key transitioning questions for a task.
        
        These questions form a sequential, hierarchical narrative flow:
        1. First question: Initial situation and first narrative twist
        2. Second question: Complications arising from the first situation
        3. Third question: Resolution based on both previous stages
        
        Args:
            task_info: Dictionary containing task information
            
        Returns:
            List of three transitioning questions
        """
        # Prepare the prompt
        prompt = f"""
You serve as a story architect for a narrative game with a hierarchical task structure. Your job is to analyze the task information and generate THREE key transitioning questions that form a sequential narrative flow for this task.

IMPORTANT STRUCTURE: 
The narrative structure consists of a ROOT TASK (Level 0) with {NUM_LAYERS} layers of subtasks below it:
- Level 1: Main scripted subtasks responding to the first transitioning question
- Level 2: Subtasks branching from Level 1, responding to the second transitioning question
- Level 3: Subtasks branching from Level 2, responding to the third transitioning question

The ID structure follows this hierarchical pattern:
- Root task has ID "{ROOT_TASK_ID}"
- Layer 1 scripted subtask: "1.1"
- Layer 1 generated subtasks: "1.1.1", "1.1.2", "1.1.3" (alternatives, is_generated: True)
- Layer 2 scripted subtask: "1.2"
- Layer 2 generated subtasks: "1.2.1", "1.2.2", "1.2.3" (alternatives, is_generated: True)
- Layer 3 scripted subtask: "1.3"
- Layer 3 generated subtasks: "1.3.1", "1.3.2", "1.3.3" (alternatives, is_generated: True)

YOUR TASK: Generate THREE key transitioning questions that MUST follow this structure:
1. First question: Establishes the initial situation and task parameters
2. Second question: Directly builds upon the first question, introducing complications/challenges
3. Third question: Addresses how the situation resolves based on developments from questions 1 and 2

Task Information:
{json.dumps(task_info, indent=2)}

You MUST respond with a JSON array containing EXACTLY THREE transitioning questions in sequential order:
["First question about the initial situation?", "Second question about complications?", "Third question about resolution?"]

YOUR RESPONSE MUST BE VALID JSON: A single array containing exactly three string elements.
"""
        
        response = self._call_llm(prompt)
        
        save_llm_response("key_questions", prompt, response, task_info)
        
        try:
            questions = json.loads(response)
            if isinstance(questions, list) and len(questions) > 0:
                return questions[:3]  # Ensure we have at most 3 questions
                
        except json.JSONDecodeError:
            try:
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    questions = json.loads(json_match.group(0))
                    if isinstance(questions, list) and len(questions) > 0:
                        return questions[:3]
            except:
                pass
                
        log_message("Error parsing LLM response for key questions. Using fallback.", "ERROR")
        return [
            "How does the initial situation unfold?",
            "What complications arise from this initial situation?",
            "How does the situation ultimately resolve?"
        ]
    
    def generate_scripted_subtask(self, task_info: Dict[str, Any], transitioning_question: str, layer: int = 1, previous_subtasks: List[Dict[str, Any]] = None, root_id: str = ROOT_TASK_ID) -> Dict[str, Any]:
        """
        Generate a scripted subtask based on a transitioning question.
        
        Creates a scripted subtask that forms part of the hierarchical narrative structure.
        These subtasks serve as connection points between different layers of the task tree.
        
        Args:
            task_info: Dictionary containing task information
            transitioning_question: The question to base the subtask on
            layer: The layer number (1, 2, or 3) for this subtask
            previous_subtasks: Optional list of previously generated subtasks
            root_id: ID for the root task (default: ROOT_TASK_ID from constants)
            
        Returns:
            Dictionary with the generated subtask data
        """
        layer_id = f"{root_id}.{layer}"
        parent_id = root_id if layer == 1 else f"{root_id}.{layer-1}"
        
        previous_context = ""
        if previous_subtasks and len(previous_subtasks) > 0:
            previous_context = "\nPreviously generated subtasks:\n"
            for subtask in previous_subtasks:
                previous_context += f"- Layer {subtask.get('layer', '?')} Subtask: {subtask.get('title', 'Unknown')}\n"
                previous_context += f"  Description: {subtask.get('description', 'No description')}\n"
        
        prompt = f"""
You serve as a story architect for a narrative game with a hierarchical task structure. Your job is to generate a scripted subtask based on the task information and transitioning question provided.

IMPORTANT STRUCTURE CONTEXT:
- The narrative tree consists of a ROOT TASK (ID "{root_id}") with {NUM_LAYERS} layers of subtasks below it
- Each layer has one main scripted subtask followed by generated alternatives
- The ID structure follows this pattern:
  - Root task: "{root_id}"
  - Layer 1 scripted subtask: "{root_id}.1"
  - Layer 1 generated alternatives: "{root_id}.1.1", "{root_id}.1.2", "{root_id}.1.3" (is_generated: true)
  - Layer 2 scripted subtask: "{root_id}.2"
  - Layer 2 generated alternatives: "{root_id}.2.1", "{root_id}.2.2", "{root_id}.2.3" (is_generated: true)
  - Layer 3 scripted subtask: "{root_id}.3"
  - Layer 3 generated alternatives: "{root_id}.3.1", "{root_id}.3.2", "{root_id}.3.3" (is_generated: true)
  the following layers have the same structure (Layer 4, Layer 5, etc.)

You are generating a scripted subtask for Layer {layer} with ID "{layer_id}" that has parent_id "{parent_id}".
{previous_context}

Task Information:
{json.dumps(task_info, indent=2)}

Transitioning Question: {transitioning_question}

YOUR TASK: Create a scripted subtask that will serve as the main canonical path in Layer {layer} of the narrative structure. This subtask:
1. Directly addresses the transitioning question
2. Will be the primary response at this layer level 
3. Forms a parent for the next level's subtask or alternatives
4. Has a parent_id of "{parent_id}"
5. Has is_generated set to "False" (as this is a scripted, not generated subtask)

Your response MUST be a JSON object with this format:
{{
  "subtask_id": "{layer_id}",
  "title": "Brief, catchy title for the subtask",
  "description": "Clear description of what happens in this subtask",
  "dialogue": "The main narrative text for the player",
  "npc_reactions": {{"npc_name": "reaction description", ...}},
  "player_options": ["option 1", "option 2", "option 3"],
  "parent_id": "{parent_id}",
  "layer": {layer},
  "is_generated": false
}}

YOUR RESPONSE MUST BE VALID JSON: A single JSON object with the exact keys shown above.
"""
        
        response = self._call_llm(prompt)
        
        save_llm_response("scripted_subtask", prompt, response, {
            **task_info,  # Include original task_info fields directly 
            "layer": layer,
            "previous_subtasks": previous_subtasks,
            "root_id": root_id,
            "_original_task_info": task_info  # Keep original for reference if needed
        })
        
        try:
            subtask = json.loads(response)
            if isinstance(subtask, dict) and "title" in subtask and "dialogue" in subtask:
                subtask["subtask_id"] = layer_id
                subtask["parent_id"] = parent_id
                subtask["layer"] = layer
                subtask["is_generated"] = False
                return subtask
                
        except json.JSONDecodeError:
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    subtask = json.loads(json_match.group(0))
                    if isinstance(subtask, dict) and "title" in subtask and "dialogue" in subtask:
                        subtask["subtask_id"] = layer_id
                        subtask["parent_id"] = parent_id
                        subtask["layer"] = layer
                        subtask["is_generated"] = False
                        return subtask
            except:
                pass
        
        log_message("Error parsing LLM response for scripted subtask. Using fallback.", "ERROR")
        return {
            "subtask_id": layer_id,
            "title": f"Response to {transitioning_question}",
            "description": f"A scripted response to the transitioning question for Layer {layer}.",
            "dialogue": "The situation unfolds according to narrative expectations.",
            "npc_reactions": {},
            "player_options": ["Continue", "Ask questions", "Take another approach"],
            "parent_id": parent_id,
            "layer": layer,
            "is_generated": False
        }
    
    def generate_subtask_branches(self, task_info: Dict[str, Any], transitioning_question: str, 
                             scripted_subtask: Dict[str, Any], layer: int, root_id: str = ROOT_TASK_ID) -> List[Dict[str, Any]]:
        """
        Generate alternative subtask branches based on a transitioning question.
        
        Generates up to {DEFAULT_NUM_ALTERNATIVES} alternative branches that respond to the same transitioning
        question as the scripted subtask, creating a hierarchical relationship.
        
        Args:
            task_info: Dictionary containing task information
            transitioning_question: The question to base the branches on
            scripted_subtask: The scripted subtask to branch from
            layer: The layer (1, 2, or 3) these alternatives belong to
            root_id: ID for the root task (default: ROOT_TASK_ID from constants)
            
        Returns:
            List of dictionaries with generated subtask data (maximum of {DEFAULT_NUM_ALTERNATIVES})
        """
        parent_id = scripted_subtask.get("subtask_id", f"{root_id}.{layer}")
        base_id = f"{parent_id}."
        
        prompt = f"""
You serve as a story architect for a narrative game with a hierarchical task structure. Your job is to generate alternative narrative branches in response to a transitioning question.

IMPORTANT STRUCTURE CONTEXT:
- The narrative tree has a ROOT TASK (ID "{root_id}") with {NUM_LAYERS} layers of subtasks
- Each layer has one main scripted subtask followed by generated alternatives
- The ID structure follows this pattern:
  - Root task: "{root_id}"
  - Layer 1 scripted subtask: "{root_id}.1"
  - Layer 1 generated alternatives: "{root_id}.1.1", "{root_id}.1.2", "{root_id}.1.3" (is_generated: true)
  - Layer 2 scripted subtask: "{root_id}.2"
  - Layer 2 generated alternatives: "{root_id}.2.1", "{root_id}.2.2", "{root_id}.2.3" (is_generated: true)
  - Layer 3 scripted subtask: "{root_id}.3"
  - Layer 3 generated alternatives: "{root_id}.3.1", "{root_id}.3.2", "{root_id}.3.3" (is_generated: true)
  the following layers have the same structure (Layer 4, Layer 5, etc.)

You are generating {DEFAULT_NUM_ALTERNATIVES} alternative branches for Layer {layer}.
These alternatives will have:
- Parent ID: "{parent_id}" (the scripted subtask of this layer)
- Layer: {layer}
- IDs: "{base_id}1", "{base_id}2", "{base_id}3" (for each alternative)
- is_generated: true (as these are generated alternatives)

Task Information:
{json.dumps(task_info, indent=2)}

Transitioning Question: {transitioning_question}

Scripted Subtask (the main path for Layer {layer}):
{json.dumps(scripted_subtask, indent=2)}

YOUR TASK: Generate EXACTLY {DEFAULT_NUM_ALTERNATIVES} alternative narrative branches that could occur in response to the transitioning question. These alternatives should:
1. Be alternative responses to the same transitioning question as the scripted subtask
2. Offer meaningfully different narrative paths than the scripted subtask
3. Maintain logical consistency with the task information
4. Have the scripted subtask as their parent

Rate each possibility on a 100-point scale (only those rated {MIN_RATING_THRESHOLD}+ will be considered viable).

Your response MUST be a JSON array of EXACTLY {DEFAULT_NUM_ALTERNATIVES} objects with this format:
[
  {{
    "subtask_id": "{base_id}1",
    "title": "Brief, catchy title for the branch",
    "description": "Clear description of what happens in this branch",
    "dialogue": "The main narrative text for the player",
    "npc_reactions": {{"npc_name": "reaction description", ...}},
    "player_options": ["option 1", "option 2", "option 3"],
    "parent_id": "{parent_id}",
    "layer": {layer},
    "is_generated": true,
    "rating": 85
  }},
  {{
    "subtask_id": "{base_id}2",
    "title": "Second alternative branch title",
    "description": "Description of the second alternative",
    "dialogue": "Dialogue for the second alternative",
    "npc_reactions": {{"npc_name": "reaction description", ...}},
    "player_options": ["option 1", "option 2", "option 3"],
    "parent_id": "{parent_id}",
    "layer": {layer},
    "is_generated": true,
    "rating": 82
  }},
  {{
    "subtask_id": "{base_id}3",
    "title": "Third alternative branch title",
    "description": "Description of the third alternative",
    "dialogue": "Dialogue for the third alternative",
    "npc_reactions": {{"npc_name": "reaction description", ...}},
    "player_options": ["option 1", "option 2", "option 3"],
    "parent_id": "{parent_id}",
    "layer": {layer},
    "is_generated": true,
    "rating": 80
  }}
]

YOUR RESPONSE MUST BE VALID JSON: An array with EXACTLY {DEFAULT_NUM_ALTERNATIVES} objects.
"""
        
        response = self._call_llm(prompt)
        
        save_llm_response("subtask_branches", prompt, response, {
            **task_info,  # Include original task_info fields directly
            "transitioning_question": transitioning_question,
            "scripted_subtask": scripted_subtask,
            "layer": layer,
            "root_id": root_id,
            "_original_task_info": task_info  # Keep original for reference if needed
        })
        
        try:
            branches = json.loads(response)
            
            if isinstance(branches, list):
                valid_branches = [b for b in branches if b.get("rating", 0) >= MIN_RATING_THRESHOLD]
                
                for i, branch in enumerate(valid_branches):
                    branch["subtask_id"] = f"{base_id}{i+1}"
                    branch["parent_id"] = parent_id
                    branch["layer"] = layer
                    branch["is_generated"] = True
                
                return valid_branches[:DEFAULT_NUM_ALTERNATIVES]  # Ensure we return no more than DEFAULT_NUM_ALTERNATIVES
                
        except json.JSONDecodeError:
            try:
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    branches = json.loads(json_match.group(0))
                    if isinstance(branches, list):
                        valid_branches = [b for b in branches if b.get("rating", 0) >= MIN_RATING_THRESHOLD]
                        
                        for i, branch in enumerate(valid_branches):
                            branch["subtask_id"] = f"{base_id}{i+1}"
                            branch["parent_id"] = parent_id
                            branch["layer"] = layer
                            branch["is_generated"] = True
                        
                        return valid_branches[:DEFAULT_NUM_ALTERNATIVES]  # Ensure we return no more than DEFAULT_NUM_ALTERNATIVES
            except:
                pass
                
        log_message("Error parsing LLM response for subtask branches. Using fallback.", "ERROR")
        
        fallback_branches = []
        for i in range(DEFAULT_NUM_ALTERNATIVES):
            fallback_branches.append({
                "subtask_id": f"{base_id}{i+1}",
                "title": f"Alternative {i+1} for Layer {layer}",
                "description": f"An alternative approach to the situation in Layer {layer}.",
                "dialogue": "The situation unfolds with a different perspective.",
                "npc_reactions": {},
                "player_options": ["Continue", "Ask questions", "Take another approach"],
                "parent_id": parent_id,
                "layer": layer,
                "is_generated": True,
                "rating": 80
            })
        
        return fallback_branches
    
    # def generate_subtask(self, game_state, transitioning_question, current_subtask):
    #     """
    #     DEPRECATED: Legacy method for demo compatibility.
    #     Please use generate_hierarchical_narrative() for new code.
        
    #     Generate a new subtask based on the current state and a transitioning question.
    #     This method is maintained for backward compatibility.
        
    #     Args:
    #         game_state: Current game state
    #         transitioning_question: Question to base the new subtask on
    #         current_subtask: The current subtask
            
    #     Returns:
    #         Dictionary with the generated subtask data
    #     """
    #     warnings.warn(
    #         "generate_subtask() is deprecated. Use generate_hierarchical_narrative() instead.",
    #         DeprecationWarning, 
    #         stacklevel=2
    #     )
        
    #     try:
            
    #         task_info = {
    #             "name": "Generated Task",
    #             "description": transitioning_question
    #         }
            
    #         # Get parent info if available
    #         parent_id = getattr(current_subtask, "subtask_id", ROOT_TASK_ID)
    #         parent_layer = getattr(current_subtask, "layer", 0)
            
    #         # Generate a simple subtask using the modern approach internals
    #         subtask_data = {
    #             "title": f"Response to {transitioning_question[:30]}...",
    #             "description": f"Generated response to the question.",
    #             "dialogue": f"The situation continues to develop. {transitioning_question}",
    #             "player_options": [
    #                 "Continue with the current approach",
    #                 "Take a different direction",
    #                 "Ask for more information"
    #             ],
    #             "npc_reactions": {}
    #         }
            
    #         return subtask_data
    #     except Exception as e:
    #         log_message(f"Error in deprecated generate_subtask: {e}", "WARNING")
    #         # Fall back to the original mock implementation
    #         return {
    #             "title": "The Next Development",
    #             "description": "The narrative progresses with new challenges.",
    #             "dialogue": "As the situation unfolds, new factors come into play that require your attention.",
    #             "player_options": [
    #                 "Address the immediate concern",
    #                 "Focus on the long-term goal",
    #                 "Seek more information"
    #             ],
    #             "npc_reactions": {
    #                 "npc_1": "watches the situation with interest",
    #                 "npc_2": "seems to be calculating the implications"
    #             }
    #         }
    
    # def rate_generated_subtasks(self, game_state, transitioning_question, current_subtask, subtasks, threshold=MIN_RATING_THRESHOLD):
    #     """
    #     DEPRECATED: Legacy method for demo compatibility.
    #     Please use generate_hierarchical_narrative() for new code.
        
    #     Rate multiple generated subtasks based on relevance and coherence.
    #     This method is maintained for backward compatibility.
        
    #     Args:
    #         game_state: Current game state
    #         transitioning_question: Question that generated the subtasks
    #         current_subtask: The current subtask
    #         subtasks: List of subtasks to rate
    #         threshold: Minimum rating threshold
            
    #     Returns:
    #         List of (subtask, rating) tuples for subtasks that meet the threshold
    #     """
    #     warnings.warn(
    #         "rate_generated_subtasks() is deprecated. Use generate_hierarchical_narrative() instead.",
    #         DeprecationWarning, 
    #         stacklevel=2
    #     )
        
    #     try:
    #         rated_subtasks = []
    #         for i, subtask in enumerate(subtasks):
    #             base_rating = 85  # Start with a good base rating
                
    #             title_length = len(subtask.get("title", "")) if isinstance(subtask, dict) else 0
    #             options_count = len(subtask.get("player_options", [])) if isinstance(subtask, dict) else 0
                
    #             rating = min(95, base_rating + (title_length // 10) + (options_count * 2))
                
    #             if rating >= threshold:
    #                 rated_subtasks.append((subtask, rating))
        
    #         return rated_subtasks
    #     except Exception as e:
    #         log_message(f"Error in deprecated rate_generated_subtasks: {e}", "WARNING")
    #         rated_subtasks = []
    #         for subtask in subtasks:
    #             rating = random.randint(70, 95)
    #         if rating >= threshold:
    #             rated_subtasks.append((subtask, rating))
                
    #         return rated_subtasks
    
    # def generate_npc_response(self, npc_state, player_input, game_state):
    #     """
    #     Generate an NPC response based on the player's input and game state.
        
    #     Args:
    #         npc_state: The NPC's current state
    #         player_input: The player's input
    #         game_state: Current game state
            
    #     Returns:
    #         The NPC's response
    #     """
    #     return f"{npc_state.name} considers your words briefly before responding in a way that aligns with their character."

    def generate_hierarchical_narrative(self, task_info: Dict[str, Any], root_id: str = ROOT_TASK_ID) -> Dict[str, Any]:
        """
        Generate a complete hierarchical narrative structure based on task info.
        
        This method implements the full process of:
        1. Generating 3 transitioning questions
        2. Generating all scripted subtasks for each layer
        3. Generating alternatives (generated subtasks) for each layer
        
        Args:
            task_info: Dictionary containing task information
            root_id: ID for the root task (default: ROOT_TASK_ID from constants)
            
        Returns:
            Dictionary with the complete narrative structure
        """
        log_message("Generating hierarchical narrative structure", "INFO")
        
        log_message("Generating transitioning questions", "INFO")
        questions = self.generate_key_questions(task_info)## ToDo: use  extract_key_questions() to obtain the questions
        
        scripted_subtasks = []
        
        log_message("Generating Layer 1 scripted subtask", "INFO")
        layer1_subtask = self.generate_scripted_subtask(
            task_info, 
            questions[0], 
            layer=1,
            root_id=root_id
        )
        scripted_subtasks.append(layer1_subtask)
        
        log_message("Generating Layer 2 scripted subtask", "INFO")
        layer2_subtask = self.generate_scripted_subtask(
            task_info, 
            questions[1], 
            layer=2, 
            previous_subtasks=[layer1_subtask],
            root_id=root_id
        )
        scripted_subtasks.append(layer2_subtask)
        
        log_message("Generating Layer 3 scripted subtask", "INFO")
        layer3_subtask = self.generate_scripted_subtask(
            task_info, 
            questions[2], 
            layer=3, 
            previous_subtasks=[layer1_subtask, layer2_subtask],
            root_id=root_id
        )
        scripted_subtasks.append(layer3_subtask)
        
        # Step 3: Go back and generate alternatives for each layer
        generated_subtasks = []
        
        # Layer 1 alternatives
        log_message("Generating Layer 1 alternatives", "INFO")
        layer1_alternatives = self.generate_subtask_branches(
            task_info,
            questions[0],
            layer1_subtask,
            layer=1,
            root_id=root_id
        )
        generated_subtasks.extend(layer1_alternatives)
        
        # Layer 2 alternatives
        log_message("Generating Layer 2 alternatives", "INFO")
        layer2_alternatives = self.generate_subtask_branches(
            task_info,
            questions[1],
            layer2_subtask,
            layer=2,
            root_id=root_id
        )
        generated_subtasks.extend(layer2_alternatives)
        
        # Layer 3 alternatives
        log_message("Generating Layer 3 alternatives", "INFO")
        layer3_alternatives = self.generate_subtask_branches(
            task_info,
            questions[2],
            layer3_subtask,
            layer=3,
            root_id=root_id
        )
        generated_subtasks.extend(layer3_alternatives)
        
        # Combine everything into a complete structure
        narrative_structure = {
            "task_info": task_info,
            "transitioning_questions": questions,
            "scripted_subtasks": scripted_subtasks,
            "generated_subtasks": generated_subtasks
        }
        
        log_message("Completed hierarchical narrative generation", "INFO")
        return narrative_structure
