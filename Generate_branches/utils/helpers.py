"""
This module contains utility helper functions for the narrative game system.
"""

import os
import json
import uuid
from datetime import datetime

def generate_id(prefix=""):
    """
    Generate a unique ID for game elements.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        A unique ID string
    """
    unique_id = str(uuid.uuid4())[:8]  # Take first 8 characters of UUID
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id

def timestamp_to_readable(timestamp):
    """
    Convert a numeric timestamp to a readable string.
    
    Args:
        timestamp: Numeric timestamp value
        
    Returns:
        Formatted string (e.g., "Day 2, 14:30")
    """
    # Convert game time to days and hours
    days = timestamp // 24  # Assuming 24 time units per day
    hours = timestamp % 24
    
    return f"Day {days + 1}, {hours:02d}:00"

def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        
def save_json(data, filename):
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: File path
    """
    directory = os.path.dirname(filename)
    ensure_directory_exists(directory)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        
def load_json(filename):
    """
    Load data from a JSON file.
    
    Args:
        filename: File path
        
    Returns:
        Loaded data or None if file doesn't exist
    """
    if not os.path.exists(filename):
        return None
        
    with open(filename, 'r') as f:
        return json.load(f)
        
def auto_save_filename(game_name):
    """
    Generate an auto-save filename based on game name and current time.
    
    Args:
        game_name: Name of the game
        
    Returns:
        Auto-save filename
    """
    from Generate_branches.utils.config import get_config
    
    # Get save directory from config
    save_dir = get_config("game").get("save_directory", "saves/")
    ensure_directory_exists(save_dir)
    
    # Format current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_game_name = game_name.replace(" ", "_").lower()
    
    return os.path.join(save_dir, f"{safe_game_name}_autosave_{timestamp}.json")
    
def log_message(message, message_type="INFO"):
    """
    Log a message with timestamp.
    
    Args:
        message: Message to log
        message_type: Type of message (INFO, WARNING, ERROR)
    """
    from Generate_branches.utils.config import get_config
    
    if not get_config("game").get("debug_mode", False) and message_type == "INFO":
        return
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{message_type}] {message}")
    
def parse_player_input(input_text, available_options=None):
    """
    Parse player input to determine intent.
    
    Args:
        input_text: Player's input text
        available_options: List of available options/choices
        
    Returns:
        Parsed input information
    """
    input_text = input_text.strip().lower()
    
    # Check if input matches an available option
    if available_options:
        for i, option in enumerate(available_options):
            # Check if player entered the option number or the text
            if input_text == str(i + 1) or input_text == option.lower():
                return {
                    "type": "option",
                    "value": option,
                    "index": i
                }
    
    # Check for common commands
    if input_text in ["quit", "exit", "q"]:
        return {
            "type": "command",
            "value": "quit"
        }
    elif input_text in ["help", "h", "?"]:
        return {
            "type": "command",
            "value": "help"
        }
    elif input_text in ["save"]:
        return {
            "type": "command",
            "value": "save"
        }
    elif input_text in ["load"]:
        return {
            "type": "command",
            "value": "load"
        }
        
    # If no match, treat as free text input
    return {
        "type": "text",
        "value": input_text
    } 