"""
This module provides utility functions used throughout the project.
"""

import os
import json
import datetime
import re
from typing import Dict, Any, List, Optional

from Generate_branches.utils.constants import DEBUG_MODE

def generate_id(prefix=""):
    """
    Generate a unique ID for use in the system.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Generated ID string
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_{timestamp}"

def timestamp_to_readable(timestamp):
    """
    Convert a numeric timestamp to a human-readable format.
    
    Args:
        timestamp: Numeric timestamp
        
    Returns:
        String with formatted date and time
    """
    try:
        # For Unix timestamps (seconds since epoch)
        if isinstance(timestamp, (int, float)):
            dt = datetime.datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Try to parse common date formats
            formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y%m%d%H%M%S"]
            for fmt in formats:
                try:
                    dt = datetime.datetime.strptime(str(timestamp), fmt)
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
            return str(timestamp)  # Return as string if parsing fails
    except:
        return str(timestamp)  # Return as string if any exception

def ensure_directory_exists(directory_path):
    """
    Create directory if it doesn't exist.
    
    Args:
        directory_path: Path to create
    """
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            return True
        except Exception as e:
            log_message(f"Failed to create directory {directory_path}: {e}", "ERROR")
            return False
    return True

def save_json(data, filename):
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: File to save to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Save the file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        log_message(f"Error saving JSON file {filename}: {e}", "ERROR")
        return False

def load_json(filename):
    """
    Load data from a JSON file.
    
    Args:
        filename: File to load from
        
    Returns:
        Loaded data or None if loading failed
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_message(f"Error loading JSON file {filename}: {e}", "ERROR")
        return None

def auto_save_filename(game_name):
    """
    Generate a filename for auto-saving.
    
    Args:
        game_name: Name of the game
        
    Returns:
        Autosave filename
    """
    # Clean the game name for use in a filename
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', game_name)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"autosave_{clean_name}_{timestamp}.json"

def log_message(message, message_type="INFO"):
    """
    Log a message with timestamp and type.
    
    Args:
        message: The message to log
        message_type: Type of message (INFO, WARNING, ERROR, DEBUG)
    """
    # Only display DEBUG messages if debug mode is enabled
    if message_type == "DEBUG" and not DEBUG_MODE:
        return
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] [{message_type}] {message}"
    
    # Print to console
    print(formatted_message)
    
    # In a full implementation, this could also write to a log file or send logs to a monitoring service

def parse_player_input(input_text, available_options=None):
    """
    Parse player input and map to available options if needed.
    
    Args:
        input_text: Input text from the player
        available_options: List of available options to map to
        
    Returns:
        Standardized input or closest match from available options
    """
    if not input_text:
        return None
        
    # Convert to lowercase for case-insensitive matching
    standardized_input = input_text.strip().lower()
    
    # If no available options, just return the standardized input
    if not available_options:
        return standardized_input
        
    # Try to match to an available option
    # First, check for exact matches
    for option in available_options:
        if standardized_input == option.lower():
            return option
            
    # Next, check if input is a number corresponding to an option
    try:
        option_index = int(standardized_input) - 1  # 1-indexed for user friendliness
        if 0 <= option_index < len(available_options):
            return available_options[option_index]
    except ValueError:
        pass
        
    # Finally, check for partial matches
    for option in available_options:
        if option.lower().startswith(standardized_input):
            return option
            
    # Return the original input if no matches found
    return standardized_input 