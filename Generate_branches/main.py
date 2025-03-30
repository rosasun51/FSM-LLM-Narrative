"""
This is the main entry point for the narrative generation system.
"""

import argparse
import os
import importlib
import unittest
import sys

from Generate_branches.game.branch_manager import BranchManager
from Generate_branches.visualization.illustration import ChainVisualizer, create_illustration_notebook
from Generate_branches.demo.demo_game import run_demo, create_demo_game
from Generate_branches.utils.helpers import log_message
from Generate_branches.utils.constants import (
    DEBUG_MODE,
    TEST_TASK_NAME,
    VISUALIZATION_PATH
)

def main():
    """
    Main entry point for the narrative generation system.
    Parses command line arguments and executes the appropriate function.
    """
    parser = argparse.ArgumentParser(description='Narrative Generation System with LLM')
    
    # Add arguments
    parser.add_argument('--demo', action='store_true', help='Run the demo game')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations of task chains')
    parser.add_argument('--notebook', action='store_true', help='Create a Jupyter notebook for visualization')
    parser.add_argument('--test', action='store_true', help='Run tests')
    parser.add_argument('--module', type=str, default='all', help='Module to test (default: all)')
    parser.add_argument('--task', type=str, default=TEST_TASK_NAME, help=f'Task to run or visualize (default: {TEST_TASK_NAME})')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        log_message("Debug mode enabled", "INFO")
        # Debug mode is already set in constants.py, but this allows overriding via command line
    
    # Execute the appropriate function based on arguments
    if args.demo:
        log_message("Running demo game", "INFO")
        run_demo(args.task)
    elif args.test:
        log_message("Running tests", "INFO")
        run_tests(args.module)
    elif args.visualize:
        log_message("Generating visualizations for task chains", "INFO")
        visualize_task_chains(args.task)
    elif args.notebook:
        log_message("Creating visualization notebook", "INFO")
        create_illustration_notebook()
        log_message(f"Notebook created in Generate_branches/{VISUALIZATION_PATH}/illustration.ipynb", "INFO")
    else:
        # Print help if no arguments provided
        parser.print_help()

def run_tests(module_name="all"):
    """
    Run unit tests for the specified module.
    
    Args:
        module_name: Module to test (all, task, subtask, etc.)
    """
    if module_name == "all":
        # Run all tests in the tests directory
        test_path = os.path.join(os.path.dirname(__file__), "tests")
        suite = unittest.defaultTestLoader.discover(test_path)
    else:
        # Run tests for the specified module
        try:
            module = importlib.import_module(f"Generate_branches.tests.test_{module_name}")
            suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        except ImportError:
            log_message(f"Test module not found: {module_name}", "ERROR")
            return
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    log_message(f"Tests run: {result.testsRun}", "INFO")
    log_message(f"Failures: {len(result.failures)}", "INFO" if len(result.failures) == 0 else "ERROR")
    log_message(f"Errors: {len(result.errors)}", "INFO" if len(result.errors) == 0 else "ERROR")

def visualize_task_chains(task_name=None):
    """
    Generate visualizations for task chains.
    
    Args:
        task_name: Name of a specific task to visualize (optional)
    """
    # Create a branch manager
    branch_manager = BranchManager()
    
    # Create a visualizer
    visualizer = ChainVisualizer()
    
    if task_name:
        # Generate and visualize a specific task chain
        log_message(f"Generating visualization for task: {task_name}", "INFO")
        task_chain = branch_manager.generate_task_chain(task_name)
        if task_chain:
            # Save the task chain for later use
            branch_manager.save_task_chain(task_chain.chain_id)
            
            # Visualize the task chain
            visualizer.visualize_task_chain(task_chain)
            
            # Visualize the subtask flow for each task
            for task in task_chain.tasks:
                visualizer.visualize_subtask_flow(task)
    else:
        # Generate and visualize all available task chains
        for task_data in branch_manager.scripted_tasks:
            task_name = task_data.get("name")
            if task_name:
                log_message(f"Generating visualization for task: {task_name}", "INFO")
                task_chain = branch_manager.generate_task_chain(task_name)
                if task_chain:
                    # Save the task chain for later use
                    branch_manager.save_task_chain(task_chain.chain_id)
                    
                    # Visualize the task chain
                    visualizer.visualize_task_chain(task_chain)
                    
                    # Visualize the subtask flow for each task
                    for task in task_chain.tasks:
                        visualizer.visualize_subtask_flow(task)
    
    log_message("Visualization complete", "INFO")

if __name__ == "__main__":
    main() 