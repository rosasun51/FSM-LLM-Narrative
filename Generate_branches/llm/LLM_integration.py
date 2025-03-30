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
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "sk-SdjbKZ455Psww0ZoKvSl4as8dKai9i3CUQWikdz4w2QBA4Vq")
        
        # Set up the LangChain ChatOpenAI client with custom base URL
        self.llm = ChatOpenAI(
            model="gpt-4o",
            base_url="https://api2.aigcbest.top/v1",
            api_key=self.api_key
        )
        
        # Default model (though this is now set in the ChatOpenAI initialization)
        self.model = "gpt-4o"
    
    def _call_llm(self, prompt: str, max_tokens: int = 1000) -> str:
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
                return self._mock_llm_response(prompt)
        except Exception as e:
            print(f"Error calling LLM: {e}")
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
        
        Args:
            task_info: Dictionary containing task information
            
        Returns:
            List of three transitioning questions
        """
        # Prepare the prompt
        prompt = f"""
You serve as a story teller, and your job is to analyze the task information we give you and generate three key questions (Transitioning_question) that form a sequential narrative flow for this task.

IMPORTANT: These three questions MUST follow a clear chronological sequence where:
1. The first question establishes the initial situation and sets up the first narrative twist
2. The second question builds upon the first question's developments and asks about complications or challenges that arise
3. The third question depends on the previous two and addresses how the situation resolves or concludes

Here are the definitions to help you understand the task:
- Transitioning_question: A key narrative question that drives the story forward and creates branching paths.
- Scripted_sub_task: A predetermined narrative segment with fixed dialogue, NPC reactions, and player options.
- Generated_sub_task: A dynamically generated narrative segment created in response to a Transitioning_question.

Here is the task information:
{json.dumps(task_info, indent=2)}

Please respond with a JSON array containing exactly three transitioning questions in chronological order, like this:
["First question about the initial situation?", "Second question about complications that arise?", "Third question about resolution?"]

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
        print("Error parsing LLM response for key questions. Using fallback.")
        return [
            "How does the initial interaction unfold?",
            "What complications arise during the task?",
            "How does the situation resolve?"
        ]
    
    def generate_scripted_subtask(self, task_info: Dict[str, Any], transitioning_question: str) -> Dict[str, Any]:
        """
        Generate a scripted subtask based on a transitioning question.
        
        Args:
            task_info: Dictionary containing task information
            transitioning_question: The question to base the subtask on
            
        Returns:
            Dictionary with the generated subtask data
        """
        # Prepare the prompt
        prompt = f"""
You serve as a story teller, and your job is to generate a scripted subtask based on the task information and transitioning question provided.

Here are the definitions to help you understand the task:
- Scripted_sub_task: A predetermined narrative segment with fixed dialogue, NPC reactions, and player options.
- Transitioning_question: A key narrative question that drives the story forward and creates branching paths.

Task Information:
{json.dumps(task_info, indent=2)}

Transitioning Question: {transitioning_question}

Please respond with a JSON object representing a scripted subtask that addresses this question. 
Your response should have EXACTLY this format:
{{
  "title": "Brief, catchy title for the subtask",
  "description": "Clear description of what happens in this subtask",
  "dialogue": "The main narrative text that will be shown to the player",
  "npc_reactions": {{"npc_name": "reaction description", ...}},
  "player_options": ["option 1", "option 2", "option 3"],
  "next_transitioning_question": "What happens next?"
}}

YOUR RESPONSE MUST BE VALID JSON: A single JSON object with the exact keys shown above. Do not include any text, markdown formatting, or explanation outside of the JSON object.
"""
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Save the prompt and response
        save_llm_response("scripted_subtask", prompt, response, {
            "task_info": task_info,
            "transitioning_question": transitioning_question
        })
        
        # Try different JSON extraction methods
        try:
            # First, try direct JSON parsing
            subtask = json.loads(response)
            if isinstance(subtask, dict) and "title" in subtask and "dialogue" in subtask:
                return subtask
                
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the response
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    subtask = json.loads(json_match.group(0))
                    if isinstance(subtask, dict) and "title" in subtask and "dialogue" in subtask:
                        return subtask
            except:
                pass
        
        # Fallback if parsing fails
        print("Error parsing LLM response for scripted subtask. Using fallback.")
        return {
            "title": f"Response to {transitioning_question}",
            "description": "A scripted response to the transitioning question.",
            "dialogue": "The situation unfolds according to narrative expectations.",
            "npc_reactions": {},
            "player_options": ["Continue", "Ask questions", "Take another approach"],
            "next_transitioning_question": "What happens next?"
        }
    
    def generate_subtask_branches(self, task_info: Dict[str, Any], transitioning_question: str, 
                               scripted_subtask: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate alternative subtask branches based on a transitioning question.
        
        Args:
            task_info: Dictionary containing task information
            transitioning_question: The question to base the branches on
            scripted_subtask: The scripted subtask to branch from
            
        Returns:
            List of dictionaries with generated subtask data
        """
        # Prepare the prompt
        prompt = f"""
You serve as a story teller, and your job is to analyze the task information we give you and generate possible Generated_sub_task branches.

Here are the definitions to help you understand the task:
- Scripted_sub_task: A predetermined narrative segment with fixed dialogue, NPC reactions, and player options.
- Generated_sub_task: A dynamically generated narrative segment created in response to a Transitioning_question.
- Transitioning_question: A key narrative question that drives the story forward and creates branching paths.

Task Information:
{json.dumps(task_info, indent=2)}

Transitioning Question: {transitioning_question}

Scripted Subtask (the main path):
{json.dumps(scripted_subtask, indent=2)}

You should generate alternative narrative branches that could occur in response to the same transitioning question. 
Rate each possibility on a 100-point scale. Only possibilities rated over 80 should be considered viable.
Generate no more than 3 alternative branches.

Your response should be a JSON array of objects with EXACTLY this format:
[
  {{
    "title": "Brief, catchy title for the branch",
    "description": "Clear description of what happens in this branch",
    "dialogue": "The main narrative text that will be shown to the player",
    "npc_reactions": {{"npc_name": "reaction description", ...}},
    "player_options": ["option 1", "option 2", "option 3"],
    "next_transitioning_question": "What happens next in this branch?",
    "rating": 85
  }},
  ...
]

YOUR RESPONSE MUST BE VALID JSON: An array containing objects with the exact keys shown above. Do not include any text, markdown formatting, or explanation outside of the JSON array.
"""
        
        # Call the LLM
        response = self._call_llm(prompt, max_tokens=2000)
        
        # Save the prompt and response
        save_llm_response("subtask_branches", prompt, response, {
            "task_info": task_info,
            "transitioning_question": transitioning_question,
            "scripted_subtask": scripted_subtask
        })
        
        # Try different JSON extraction methods
        try:
            # First, try direct JSON parsing
            branches = json.loads(response)
            
            # Filter by rating and limit to 3
            if isinstance(branches, list):
                valid_branches = [b for b in branches if b.get("rating", 0) >= 80]
                return valid_branches[:3]
                
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the response
            try:
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    branches = json.loads(json_match.group(0))
                    if isinstance(branches, list):
                        valid_branches = [b for b in branches if b.get("rating", 0) >= 80]
                        return valid_branches[:3]
            except:
                pass
                
        # Fallback if parsing fails
        print("Error parsing LLM response for subtask branches. Using fallback.")
        return []
    
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
    
    def rate_generated_subtasks(self, game_state, transitioning_question, current_subtask, subtasks, threshold=80):
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
