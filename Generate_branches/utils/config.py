# """
# This module contains configuration settings for the narrative game.
# """

# # LLM Integration Settings
# LLM_CONFIG = {
#     "model_name": "gpt-3.5-turbo",  # Default model
#     "temperature": 0.7,             # Controls randomness (0-1)
#     "max_tokens": 500,              # Maximum response length
#     "api_timeout": 30,              # API timeout in seconds
# }

# # Generation Settings
# GENERATION_CONFIG = {
#     "default_threshold": 50,         # Minimum rating to keep generated subtasks (0-100)
#     "default_generation_count": 3,   # Number of subtasks to generate per transition
#     "max_generation_depth": 3,       # Maximum depth of generated subtask chains
# }

# # Game Settings
# GAME_CONFIG = {
#     "save_directory": "saves/",      # Directory for saved games
#     "debug_mode": True,              # Enable debug output
#     "auto_save": True,               # Auto-save after each player action
#     "auto_save_interval": 5,         # Auto-save every N player actions
# }

# # NPC Settings
# NPC_CONFIG = {
#     "memory_limit": 20,              # Maximum number of memories per NPC
#     "default_traits": {              # Default traits for NPCs if none specified
#         "friendliness": 50,
#         "intelligence": 50,
#         "bravery": 50,
#     },
# }

# # Task Settings
# TASK_CONFIG = {
#     "default_layer_depth": 3,        # Default number of layers per task
#     "max_subtasks_per_layer": 5,     # Maximum subtasks per layer
# }

# def get_config(config_type):
#     """
#     Get configuration settings by type.
    
#     Args:
#         config_type: Type of configuration to return (llm, generation, game, npc, task)
        
#     Returns:
#         Dictionary of configuration settings
#     """
#     config_map = {
#         "llm": LLM_CONFIG,
#         "generation": GENERATION_CONFIG,
#         "game": GAME_CONFIG,
#         "npc": NPC_CONFIG,
#         "task": TASK_CONFIG,
#     }
    
#     return config_map.get(config_type.lower(), {}) 