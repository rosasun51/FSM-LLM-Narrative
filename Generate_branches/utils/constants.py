"""
This module contains constant values used throughout the FSM-LLM-Narrative system.
These centralized constants make it easier to configure and test the system.
"""

import os

# Get the absolute path to the Generate_branches directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------
# LLM Integration Constants
# ---------------------------
# Model configuration
LLM_MODEL = "gpt-4o-mini"
LLM_BASE_URL = "https://api2.aigcbest.top/v1"
LLM_API_KEY = "sk-SdjbKZ455Psww0ZoKvSl4as8dKai9i3CUQWikdz4w2QBA4Vq"  # Default test key, replace with your own
LLM_MAX_TOKENS = 1000
LLM_MAX_TOKENS_BRANCHES = 2500  # Higher token limit for generating branches

# Generation settings
DEFAULT_NUM_ALTERNATIVES = 3    # Number of alternative branches to generate
MIN_RATING_THRESHOLD = 80       # Minimum acceptable rating for generated content

# ---------------------------
# Narrative Structure Constants
# ---------------------------
# Task and subtask organization
NUM_LAYERS = 3                  # Number of layers in the task hierarchy
ROOT_TASK_ID = "1"              # ID of the root task

# ID format patterns for each layer
LAYER_1_ID_FORMAT = "{}.1"       # Layer 1 scripted subtask ID
LAYER_2_ID_FORMAT = "{}.2"       # Layer 2 scripted subtask ID
LAYER_3_ID_FORMAT = "{}.3"       # Layer 3 scripted subtask ID

# Generated subtask ID formats
LAYER_1_GEN_ID_FORMAT = "{}.1.{}"  # Format for Layer 1 generated subtask IDs (e.g., "task_id.1.1")
LAYER_2_GEN_ID_FORMAT = "{}.2.{}"  # Format for Layer 2 generated subtask IDs (e.g., "task_id.2.1")
LAYER_3_GEN_ID_FORMAT = "{}.3.{}"  # Format for Layer 3 generated subtask IDs (e.g., "task_id.3.1")

# Layer names and descriptions
LAYER_NAMES = {
    1: "Layer 1",
    2: "Layer 2",
    3: "Layer 3"
}

LAYER_DESCRIPTIONS = {
    1: "First layer below root - initial scenario (Layer 1)",
    2: "Second layer - complications and challenges (Layer 2)",
    3: "Third layer - resolution and outcomes (Layer 3)"
}

LAYER_PRIORITIES = {
    1: 100,
    2: 75,
    3: 50
}

# ---------------------------
# File and Directory Constants
# ---------------------------
# Data paths
DATA_ROOT_PATH = "data"  # Main data directory

# Legacy paths (for backward compatibility)
SCRIPTED_TASKS_PATH = os.path.join(BASE_DIR, "data", "Scripted_tasks.json")
GENERATED_CHAINS_PATH = os.path.join(BASE_DIR, "data", "generated_chains")
KEY_QUESTIONS_PATH = os.path.join(BASE_DIR, "data", "key_questions")
SUBTASKS_PATH = os.path.join(BASE_DIR, "data", "subtasks")
VISUALIZATION_PATH = os.path.join(BASE_DIR, "visualization")

# New organized folder structure directories
# These will be created dynamically with task name and timestamp
# Example: data/Meet_with_Meredith_Stout_20250401_175439/
#          data/Meet_with_Meredith_Stout_20250401_175439/key_questions_20250401_175439.json
#          data/Meet_with_Meredith_Stout_20250401_175439/Meet_with_Meredith_Stout_20250401_175439.png
#          data/Meet_with_Meredith_Stout_20250401_175439/Scripted_subtask_20250401_175439/
#          data/Meet_with_Meredith_Stout_20250401_175439/Subtask_branches_20250401_175439/

# Folder and file name components
SCRIPTED_SUBTASK_FOLDER = "Scripted_subtask"
SUBTASK_BRANCHES_FOLDER = "Subtask_branches"
KEY_QUESTIONS_FILE = "key_questions"

# ---------------------------
# Debug and Testing Constants
# ---------------------------
DEBUG_MODE = True
TEST_CHAIN_ID = "test_chain"
TEST_TASK_NAME = "Beginning" 
#TEST_TASK_NAME = "Picking Up Goods"
