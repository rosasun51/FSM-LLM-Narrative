"""
Test script for visualization of task chains with both scripted and generated subtasks.
"""

import os
import sys

# Add the root directory to the Python path to ensure imports work correctly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from Generate_branches.visualization.illustration import visualize_task_structure_example
from Generate_branches.utils.helpers import log_message

def main():
    """
    Main function to test the visualization functionality.
    """
    log_message("Starting visualization test...", "INFO")
    
    # Use the passed task name if provided, or use default
    task_name = None
    if len(sys.argv) > 1:
        task_name = sys.argv[1]
        log_message(f"Using task name from command line: {task_name}", "INFO")
    
    # Run the visualization function
    result = visualize_task_structure_example(task_name)
    
    if result:
        log_message(f"Visualization successfully created at: {result}", "INFO")
        log_message("Test completed successfully!", "INFO")
    else:
        log_message("Failed to create visualization.", "ERROR")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 