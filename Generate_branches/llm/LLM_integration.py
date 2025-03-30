"""
This module provides integration with LLM services.
It handles prompting, response parsing, and other LLM-related functionality.
"""

import os
import json
import random
from typing import Dict, List, Tuple, Any, Optional
import openai

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
        
        # Set up the OpenAI client
        if self.api_key:
            openai.api_key = self.api_key
        
        # Default model
        self.model = "gpt-4o-mini"
    
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
                # Call the OpenAI API
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful storytelling assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
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
You serve as a story teller, and your job is to analyze the task information we give you and give us three key questions (Transitioning_question) that you think can cover the main flow of this task. Please pay attention that these three key questions should be in a time precedence as the task proceeds in your analysis.

Here are the definitions to help you understand the task:
- Transitioning_question: A key narrative question that drives the story forward and creates branching paths.
- Scripted_sub_task: A predetermined narrative segment with fixed dialogue, NPC reactions, and player options.
- Generated_sub_task: A dynamically generated narrative segment created in response to a Transitioning_question.

Here is the task information:
{json.dumps(task_info, indent=2)}

Please respond with a JSON array containing exactly three transitioning questions in chronological order, like this:
["First question?", "Second question?", "Third question?"]
"""
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        try:
            # Parse the response
            questions = json.loads(response)
            if isinstance(questions, list) and len(questions) > 0:
                return questions[:3]  # Ensure we have at most 3 questions
            else:
                # Fallback if parsing fails
                return [
                    "How does the initial interaction unfold?",
                    "What complications arise during the task?",
                    "How does the situation resolve?"
                ]
        except:
            # Fallback if parsing fails
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
Your response should have this format:
{{
  "title": "",
  "description": "",
  "dialogue": "",
  "npc_reactions": {{"npc_name": "reaction description", ...}},
  "player_options": ["option 1", "option 2", "option 3"],
  "next_transitioning_question": ""
}}
"""
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        try:
            # Parse the response
            subtask = json.loads(response)
            return subtask
        except:
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

Your response should be a JSON array of objects with this format:
[
  {{
    "title": "",
    "description": "",
    "dialogue": "",
    "npc_reactions": {{"npc_name": "reaction description", ...}},
    "player_options": ["option 1", "option 2", "option 3"],
    "next_transitioning_question": "",
    "rating": 85
  }},
  ...
]
"""
        
        # Call the LLM
        response = self._call_llm(prompt, max_tokens=2000)
        
        try:
            # Parse the response
            branches = json.loads(response)
            
            # Filter by rating and limit to 3
            if isinstance(branches, list):
                valid_branches = [b for b in branches if b.get("rating", 0) >= 80]
                return valid_branches[:3]
            else:
                return []
        except:
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
