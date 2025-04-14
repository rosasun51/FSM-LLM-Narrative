"""
This module contains prompt templates for LLM interactions.
These templates are used to generate prompts for various game functions.
"""

# System prompt for the narrative game LLM
SYSTEM_PROMPT = """
You are the narrative engine for an interactive story game. Your role is to generate creative,
engaging, and coherent narrative elements that fit the game world and respond to player actions.
You should maintain consistency with established characters, locations, and plot points.

Game world context:
- {game_world_description}
"""

# Template for generating subtasks based on a transitioning question
# GENERATE_SUBTASK_PROMPT = """
# Based on the current game state and the transitioning question, create a possible next subtask
# that would make sense in the narrative flow.

# Current subtask: {current_subtask_title}
# Current subtask description: {current_subtask_description}
# Current dialogue: {current_subtask_dialogue}

# Transitioning question: {transitioning_question}

# Generate a new possible subtask that answers this transitioning question and advances the narrative.
# The subtask should be creative but consistent with the established narrative.

# Your response should be in JSON format with the following structure:
# {{
#   "title": "Brief, catchy title for the subtask",
#   "description": "Clear description of what happens in this subtask",
#   "dialogue": "The main narrative text that will be shown to the player",
#   "npc_reactions": {{ 
#     "npc_id1": "How this NPC reacts to the situation",
#     "npc_id2": "How another NPC reacts to the situation"
#   }},
#   "player_options": [
#     "First option for the player to choose",
#     "Second option for the player to choose",
#     "Third option for the player to choose"
#   ]
# }}

# Make your generated subtask surprising but logical given the context.
# """

# Template for rating generated subtasks
RATE_SUBTASK_PROMPT = """
Rate how well the following generated subtask fits as a response to the transitioning question
and as a continuation of the narrative from the previous subtask.

Previous subtask: {previous_subtask_title}
Previous subtask description: {previous_subtask_description}

Transitioning question: {transitioning_question}

Generated subtask to rate:
Title: {generated_subtask_title}
Description: {generated_subtask_description}
Dialogue: {generated_subtask_dialogue}

Rate this generated subtask on a scale from 0 to 100, where:
- 0-25: Poor fit, illogical or inconsistent with the narrative
- 26-50: Acceptable fit but not particularly compelling
- 51-75: Good fit with the narrative and addresses the question well
- 76-100: Excellent fit, creative, compelling, and perfectly addresses the question

Provide your rating as a single number between 0 and 100, followed by a brief explanation
of your reasoning.
"""

# Template for generating NPC responses
# GENERATE_NPC_RESPONSE_PROMPT = """
# Generate a response from the character {npc_name} to the player's input.

# Character background:
# {npc_background}

# Character traits:
# {npc_traits}

# Current relationships:
# {npc_relationships}

# Recent interactions:
# {npc_recent_memories}

# Current scene context:
# {scene_description}

# Player's input: "{player_input}"

# Generate {npc_name}'s response in a way that's consistent with their character,
# traits, relationships, and memories. The response should feel natural and reflect
# the character's personality.
# """

# Template for dynamic branching evaluation
EVALUATE_BRANCH_PROMPT = """
Evaluate whether the player's input should trigger a dynamic branch or continue
along the scripted path.

Current task: {current_task_title}
Current subtask: {current_subtask_title}
Current subtask description: {current_subtask_description}

Next scripted subtask: {next_subtask_title}
Next subtask description: {next_subtask_description}

Transitioning question: {transitioning_question}

Player's input: "{player_input}"

Evaluate on a scale of 0-100 how well the player's input aligns with proceeding to the
next scripted subtask. A low score means the player's input doesn't align well with the
scripted path and a dynamic branch should be generated instead.

Provide your rating as a single number between 0 and 100, followed by a brief explanation
of your reasoning.
"""

# def get_prompt_template(prompt_type):
#     """
#     Get a prompt template by type.
    
#     Args:
#         prompt_type: Type of prompt template to return
        
#     Returns:
#         Prompt template string
#     """
#     prompt_map = {
#         "system": SYSTEM_PROMPT,
#         "generate_subtask": GENERATE_SUBTASK_PROMPT,
#         "rate_subtask": RATE_SUBTASK_PROMPT,
#         "npc_response": GENERATE_NPC_RESPONSE_PROMPT,
#         "evaluate_branch": EVALUATE_BRANCH_PROMPT,
#     }
    
#     return prompt_map.get(prompt_type.lower(), "") 