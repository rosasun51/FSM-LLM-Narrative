"""
Main entry point for the LLM Narrative Game system.
This module provides a command-line interface to run the game or access utilities.
"""

import os
import sys
import argparse
import unittest
from Generate_branches.demo.demo_game import run_demo
from Generate_branches.utils.helpers import log_message
from Generate_branches.game.branch_manager import BranchManager
from Generate_branches.visualization.illustration import ChainVisualizer, create_illustration_notebook

def main():
    """
    Main entry point for the LLM Narrative Game system.
    Parses command-line arguments and runs the appropriate function.
    """
    parser = argparse.ArgumentParser(description="LLM Narrative Game System")
    
    # Define command-line arguments
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the demo game"
    )
    
    parser.add_argument(
        "--load",
        type=str,
        help="Load a saved game file"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with extra logging"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the test suite"
    )
    
    parser.add_argument(
        "--test-module",
        type=str,
        choices=["task", "llm", "game", "all"],
        default="all",
        help="Specify which test module to run"
    )
    
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualizations for task chains"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="Specify a task to process or visualize"
    )
    
    parser.add_argument(
        "--create-notebook",
        action="store_true",
        help="Create a Jupyter notebook for visualizations"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Enable debug mode if requested
    if args.debug:
        from Generate_branches.utils.config import GAME_CONFIG
        GAME_CONFIG["debug_mode"] = True
        log_message("Debug mode enabled", "INFO")
    
    # Run the requested function
    if args.test:
        run_tests(args.test_module)
    elif args.visualize:
        visualize_task_chains(args.task)
    elif args.create_notebook:
        create_illustration_notebook()
        log_message("Created visualization notebook at Generate_branches/visualization/illustration.ipynb", "INFO")
    elif args.demo:
        log_message("Running demo game", "INFO")
        run_demo(args.task)
    elif args.load:
        log_message(f"Loading saved game: {args.load}", "INFO")
        # In a full implementation, this would load a saved game
        print(f"Loading saved games is not implemented in this version.")
    else:
        # Default to showing help if no arguments provided
        parser.print_help()

def run_tests(module_name="all"):
    """
    Run the test suite.
    
    Args:
        module_name: Which test module to run (task, llm, game, or all)
    """
    if module_name == "all":
        # Run all tests
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover("Generate_branches/tests", pattern="test_*.py")
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_runner.run(test_suite)
    else:
        # Run specific test module
        test_module = f"Generate_branches.tests.test_{module_name}"
        suite = unittest.defaultTestLoader.loadTestsFromName(test_module)
        unittest.TextTestRunner(verbosity=2).run(suite)

def visualize_task_chains(task_name=None):
    """
    Generate visualizations for task chains.
    
    Args:
        task_name: Name of a specific task to visualize (optional)
    """
    log_message("Generating visualizations for task chains", "INFO")
    
    # Initialize branch manager and visualizer
    branch_manager = BranchManager()
    visualizer = ChainVisualizer()
    
    if task_name:
        # Visualize a specific task
        log_message(f"Generating visualization for task: {task_name}", "INFO")
        task_chain = branch_manager.generate_task_chain(task_name)
        
        if task_chain:
            visualizer.visualize_task_chain(task_chain)
            
            # Visualize subtask flow for each task
            for task in task_chain.tasks:
                visualizer.visualize_subtask_flow(task)
            
            log_message("Visualization complete", "INFO")
        else:
            log_message(f"Failed to generate task chain for: {task_name}", "ERROR")
    else:
        # Visualize all tasks
        from Generate_branches.demo.demo_game import DEMO_TASKS
        
        for _, task_name in DEMO_TASKS.items():
            log_message(f"Generating visualization for task: {task_name}", "INFO")
            task_chain = branch_manager.generate_task_chain(task_name)
            
            if task_chain:
                visualizer.visualize_task_chain(task_chain)
                
                # Visualize subtask flow for each task
                for task in task_chain.tasks:
                    visualizer.visualize_subtask_flow(task)
            else:
                log_message(f"Failed to generate task chain for: {task_name}", "ERROR")
        
        log_message("All visualizations complete", "INFO")

if __name__ == "__main__":
    main() 