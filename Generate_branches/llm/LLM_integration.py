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

from Generate_branches.utils.constants import (
    LLM_MODEL, 
    LLM_BASE_URL, 
    LLM_API_KEY, 
    LLM_MAX_TOKENS, 
    LLM_MAX_TOKENS_BRANCHES,
    DEFAULT_NUM_ALTERNATIVES,
    MIN_RATING_THRESHOLD,
    NUM_LAYERS,
    ROOT_TASK_ID
)
from Generate_branches.utils.helpers import log_message

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
    
    # Create the responses directory if it doesn't exist
    os.makedirs("Generate_branches/llm/responses", exist_ok=True)
    
    # Create a unique filename
    filename = f"Generate_branches/llm/responses/{response_type}_{timestamp}.json"
    
    # Prepare the data to save
    data = {
        "timestamp": timestamp,
        "prompt": prompt,
        "raw_response": response,
        "task_info": task_info
    }
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Also append to aggregated file
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
        # Use provided API key or try to get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", LLM_API_KEY)
        
        # Set up the LangChain ChatOpenAI client with custom base URL
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            base_url=LLM_BASE_URL,
            api_key=self.api_key
        )
        
        # Default model
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
                # Call the LLM using LangChain's ChatOpenAI
                messages = [
                    SystemMessage(content="You are a helpful storytelling assistant who always responds in valid JSON format."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(
                    messages,
                    max_tokens=max_tokens
                )
                
                # Extract content from the response
                return response.content
            else:
                # Mock response for demo/testing when no API key is available
                log_message("No API key provided, using mock LLM response", "WARNING")
                return self._mock_llm_response(prompt)
        except Exception as e:
            log_message(f"Error calling LLM: {e}", "ERROR")
            return self._mock_llm_response(prompt)
    
    def _mock_llm_response(self, prompt: str) -> str:
        """
        Generate a mock LLM response for demo/testing.
        
        Args:
            prompt: The prompt that would be sent to the LLM
            
        Returns:
            Mock generated text
        """
        # Simple mock responses based on prompt content for demo purposes
        if "transitioning_question" in prompt.lower():
            return json.dumps({
                "title": "Unexpected Development",
                "description": "The situation takes an unexpected turn.",
                "dialogue": "Just as the conversation reaches a crucial point, the sound of footsteps approaching from the hallway catches everyone's attention.",
                "player_options": [
                    "Prepare for trouble",
                    "Maintain the conversation",
                    "Look for an exit"
                ],
                "npc_reactions": {
                    "npc_1": "looks anxiously toward the door",
                    "npc_2": "reaches subtly for a concealed weapon"
                }
            })
        
        elif "generate_subtask" in prompt.lower():
            return json.dumps({
                "title": "The Decision",
                "description": "A moment of truth that will shape the path forward.",
                "dialogue": "The choice before you is clear, but the consequences remain shrouded in uncertainty.",
                "player_options": [
                    "Accept the deal",
                    "Reject the offer",
                    "Attempt to negotiate"
                ],
                "npc_reactions": {
                    "npc_1": "watches you intently, awaiting your decision",
                    "npc_2": "seems indifferent, but you notice a subtle tension"
                }
            })
        
        elif "npc_response" in prompt.lower():
            return "The character considers your words carefully before responding with measured caution."
        
        elif "key questions" in prompt.lower():
            return json.dumps([
                "How does the initial interaction unfold?",
                "What complications arise during the task?",
                "How does the situation resolve?"
            ])
        
        else:
            return "The narrative continues with unexpected developments and emerging challenges."
    
    def generate_key_questions(self, task_info: Dict[str, Any]) -> List[str]:
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
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Save the prompt and response
        save_llm_response("key_questions", prompt, response, task_info)
        
        # Try different JSON extraction methods
        try:
            # First, try direct JSON parsing
            questions = json.loads(response)
            if isinstance(questions, list) and len(questions) > 0:
                return questions[:3]  # Ensure we have at most 3 questions
                
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the response
            try:
                # Look for anything that looks like a JSON array
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    questions = json.loads(json_match.group(0))
                    if isinstance(questions, list) and len(questions) > 0:
                        return questions[:3]
            except:
                pass
                
        # Fallback if all parsing methods fail
        log_message("Error parsing LLM response for key questions. Using fallback.", "ERROR")
        return [
            "How does the initial situation unfold?",
            "What complications arise from this initial situation?",
            "How does the situation ultimately resolve?"
        ]
    
    def generate_scripted_subtask(self, task_info: Dict[str, Any], transitioning_question: str, layer: int = 1, previous_subtasks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a scripted subtask based on a transitioning question.
        
        Creates a scripted subtask that forms part of the hierarchical narrative structure.
        These subtasks serve as connection points between different layers of the task tree.
        
        Args:
            task_info: Dictionary containing task information
            transitioning_question: The question to base the subtask on
            layer: The layer number (1, 2, or 3) for this subtask
            previous_subtasks: Optional list of previously generated subtasks
            
        Returns:
            Dictionary with the generated subtask data
        """
        # Determine the layer ID based on the layer
        layer_id = f"1.{layer}"
        parent_id = ROOT_TASK_ID if layer == 1 else f"1.{layer-1}"
        
        # Prepare context from previous subtasks if available
        previous_context = ""
        if previous_subtasks and len(previous_subtasks) > 0:
            previous_context = "\nPreviously generated subtasks:\n"
            for subtask in previous_subtasks:
                previous_context += f"- Layer {subtask.get('layer', '?')} Subtask: {subtask.get('title', 'Unknown')}\n"
                previous_context += f"  Description: {subtask.get('description', 'No description')}\n"
        
        # Prepare the prompt
        prompt = f"""
You serve as a story architect for a narrative game with a hierarchical task structure. Your job is to generate a scripted subtask based on the task information and transitioning question provided.

IMPORTANT STRUCTURE CONTEXT:
- The narrative tree consists of a ROOT TASK (ID "{ROOT_TASK_ID}") with {NUM_LAYERS} layers of subtasks below it
- Each layer has one main scripted subtask followed by generated alternatives
- The ID structure follows this pattern:
  - Root task: "{ROOT_TASK_ID}"
  - Layer 1 scripted subtask: "1.1"
  - Layer 1 generated alternatives: "1.1.1", "1.1.2", "1.1.3" (is_generated: true)
  - Layer 2 scripted subtask: "1.2"
  - Layer 2 generated alternatives: "1.2.1", "1.2.2", "1.2.3" (is_generated: true)
  - Layer 3 scripted subtask: "1.3"
  - Layer 3 generated alternatives: "1.3.1", "1.3.2", "1.3.3" (is_generated: true)

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
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Save the prompt and response
        save_llm_response("scripted_subtask", prompt, response, {
            "task_info": task_info,
            "transitioning_question": transitioning_question,
            "layer": layer,
            "previous_subtasks": previous_subtasks
        })
        
        # Try different JSON extraction methods
        try:
            # First, try direct JSON parsing
            subtask = json.loads(response)
            if isinstance(subtask, dict) and "title" in subtask and "dialogue" in subtask:
                # Ensure required fields are set
                subtask["subtask_id"] = layer_id
                subtask["parent_id"] = parent_id
                subtask["layer"] = layer
                subtask["is_generated"] = False
                return subtask
                
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the response
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    subtask = json.loads(json_match.group(0))
                    if isinstance(subtask, dict) and "title" in subtask and "dialogue" in subtask:
                        # Ensure required fields are set
                        subtask["subtask_id"] = layer_id
                        subtask["parent_id"] = parent_id
                        subtask["layer"] = layer
                        subtask["is_generated"] = False
                        return subtask
            except:
                pass
        
        # Fallback if parsing fails
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
                             scripted_subtask: Dict[str, Any], layer: int) -> List[Dict[str, Any]]:
        """
        Generate alternative subtask branches based on a transitioning question.
        
        Generates up to {DEFAULT_NUM_ALTERNATIVES} alternative branches that respond to the same transitioning
        question as the scripted subtask, creating a hierarchical relationship.
        
        Args:
            task_info: Dictionary containing task information
            transitioning_question: The question to base the branches on
            scripted_subtask: The scripted subtask to branch from
            layer: The layer (1, 2, or 3) these alternatives belong to
            
        Returns:
            List of dictionaries with generated subtask data (maximum of {DEFAULT_NUM_ALTERNATIVES})
        """
        # Get parent ID and base ID pattern
        parent_id = scripted_subtask.get("subtask_id", f"1.{layer}")
        base_id = f"{parent_id}."
        
        # Prepare the prompt
        prompt = f"""
You serve as a story architect for a narrative game with a hierarchical task structure. Your job is to generate alternative narrative branches in response to a transitioning question.

IMPORTANT STRUCTURE CONTEXT:
- The narrative tree has a ROOT TASK (ID "{ROOT_TASK_ID}") with {NUM_LAYERS} layers of subtasks
- Each layer has one main scripted subtask followed by generated alternatives
- The ID structure follows this pattern:
  - Root task: "{ROOT_TASK_ID}"
  - Layer 1 scripted subtask: "1.1"
  - Layer 1 generated alternatives: "1.1.1", "1.1.2", "1.1.3" (is_generated: true)
  - Layer 2 scripted subtask: "1.2"
  - Layer 2 generated alternatives: "1.2.1", "1.2.2", "1.2.3" (is_generated: true)
  - Layer 3 scripted subtask: "1.3"
  - Layer 3 generated alternatives: "1.3.1", "1.3.2", "1.3.3" (is_generated: true)

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
        
        # Call the LLM
        response = self._call_llm(prompt, max_tokens=LLM_MAX_TOKENS_BRANCHES)
        
        # Save the prompt and response
        save_llm_response("subtask_branches", prompt, response, {
            "task_info": task_info,
            "transitioning_question": transitioning_question,
            "scripted_subtask": scripted_subtask,
            "layer": layer
        })
        
        # Try different JSON extraction methods
        try:
            # First, try direct JSON parsing
            branches = json.loads(response)
            
            # Filter by rating and limit to DEFAULT_NUM_ALTERNATIVES
            if isinstance(branches, list):
                valid_branches = [b for b in branches if b.get("rating", 0) >= MIN_RATING_THRESHOLD]
                
                # Ensure required fields are set on all branches
                for i, branch in enumerate(valid_branches):
                    branch["subtask_id"] = f"{base_id}{i+1}"
                    branch["parent_id"] = parent_id
                    branch["layer"] = layer
                    branch["is_generated"] = True
                
                return valid_branches[:DEFAULT_NUM_ALTERNATIVES]  # Ensure we return no more than DEFAULT_NUM_ALTERNATIVES
                
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the response
            try:
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    branches = json.loads(json_match.group(0))
                    if isinstance(branches, list):
                        valid_branches = [b for b in branches if b.get("rating", 0) >= MIN_RATING_THRESHOLD]
                        
                        # Ensure required fields are set on all branches
                        for i, branch in enumerate(valid_branches):
                            branch["subtask_id"] = f"{base_id}{i+1}"
                            branch["parent_id"] = parent_id
                            branch["layer"] = layer
                            branch["is_generated"] = True
                        
                        return valid_branches[:DEFAULT_NUM_ALTERNATIVES]  # Ensure we return no more than DEFAULT_NUM_ALTERNATIVES
            except:
                pass
                
        # Fallback if parsing fails
        log_message("Error parsing LLM response for subtask branches. Using fallback.", "ERROR")
        
        # Create fallback branches
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
    
    def generate_subtask(self, game_state, transitioning_question, current_subtask):
        """
        Legacy method for demo compatibility.
        Generate a new subtask based on the current state and a transitioning question.
        
        Args:
            game_state: Current game state
            transitioning_question: Question to base the new subtask on
            current_subtask: The current subtask
            
        Returns:
            Dictionary with the generated subtask data
        """
        # For demo purposes, we'll return a mock response
        return {
            "title": "The Next Development",
            "description": "The narrative progresses with new challenges.",
            "dialogue": "As the situation unfolds, new factors come into play that require your attention.",
            "player_options": [
                "Address the immediate concern",
                "Focus on the long-term goal",
                "Seek more information"
            ],
            "npc_reactions": {
                "npc_1": "watches the situation with interest",
                "npc_2": "seems to be calculating the implications"
            }
        }
    
    def rate_generated_subtasks(self, game_state, transitioning_question, current_subtask, subtasks, threshold=MIN_RATING_THRESHOLD):
        """
        Legacy method for demo compatibility.
        Rate multiple generated subtasks based on relevance and coherence.
        
        Args:
            game_state: Current game state
            transitioning_question: Question that generated the subtasks
            current_subtask: The current subtask
            subtasks: List of subtasks to rate
            threshold: Minimum rating threshold
            
        Returns:
            List of (subtask, rating) tuples for subtasks that meet the threshold
        """
        # For demo purposes, we'll return mock ratings
        rated_subtasks = []
        for subtask in subtasks:
            # Mock rating between 70 and 95
            rating = random.randint(70, 95)
            if rating >= threshold:
                rated_subtasks.append((subtask, rating))
                
        return rated_subtasks
    
    def generate_npc_response(self, npc_state, player_input, game_state):
        """
        Generate an NPC response based on the player's input and game state.
        
        Args:
            npc_state: The NPC's current state
            player_input: The player's input
            game_state: Current game state
            
        Returns:
            The NPC's response
        """
        # For demo purposes, we'll return a mock response
        return f"{npc_state.name} considers your words briefly before responding in a way that aligns with their character."

    def generate_hierarchical_narrative(self, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete hierarchical narrative structure based on task info.
        
        This method implements the full process of:
        1. Generating 3 transitioning questions
        2. Generating all scripted subtasks for each layer
        3. Generating alternatives (generated subtasks) for each layer
        
        Args:
            task_info: Dictionary containing task information
            
        Returns:
            Dictionary with the complete narrative structure
        """
        log_message("Generating hierarchical narrative structure", "INFO")
        
        # Step 1: Generate the 3 transitioning questions
        log_message("Generating transitioning questions", "INFO")
        questions = self.generate_key_questions(task_info)
        
        # Ensure we have exactly 3 questions
        if len(questions) < 3:
            log_message(f"Only {len(questions)} questions generated, filling with defaults", "WARNING")
            default_questions = [
                "How does the initial situation unfold?",
                "What complications arise from this initial situation?",
                "How does the situation ultimately resolve?"
            ]
            questions.extend(default_questions[len(questions):3])
        
        # Step 2: Generate all scripted subtasks first
        scripted_subtasks = []
        
        # Layer 1 scripted subtask (first question)
        log_message("Generating Layer 1 scripted subtask", "INFO")
        layer1_subtask = self.generate_scripted_subtask(
            task_info, 
            questions[0], 
            layer=1
        )
        scripted_subtasks.append(layer1_subtask)
        
        # Layer 2 scripted subtask (second question)
        log_message("Generating Layer 2 scripted subtask", "INFO")
        layer2_subtask = self.generate_scripted_subtask(
            task_info, 
            questions[1], 
            layer=2, 
            previous_subtasks=[layer1_subtask]
        )
        scripted_subtasks.append(layer2_subtask)
        
        # Layer 3 scripted subtask (third question)
        log_message("Generating Layer 3 scripted subtask", "INFO")
        layer3_subtask = self.generate_scripted_subtask(
            task_info, 
            questions[2], 
            layer=3, 
            previous_subtasks=[layer1_subtask, layer2_subtask]
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
            layer=1
        )
        generated_subtasks.extend(layer1_alternatives)
        
        # Layer 2 alternatives
        log_message("Generating Layer 2 alternatives", "INFO")
        layer2_alternatives = self.generate_subtask_branches(
            task_info,
            questions[1],
            layer2_subtask,
            layer=2
        )
        generated_subtasks.extend(layer2_alternatives)
        
        # Layer 3 alternatives
        log_message("Generating Layer 3 alternatives", "INFO")
        layer3_alternatives = self.generate_subtask_branches(
            task_info,
            questions[2],
            layer3_subtask,
            layer=3
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
