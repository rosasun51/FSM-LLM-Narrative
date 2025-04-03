"""
This module provides a simple playable demo of the narrative game.
It sets up a small game world with tasks, subtasks, and NPCs.
"""

import os
import sys
import json
import random
from typing import Dict, List, Any, Optional

from Generate_branches.game.game_manager import GameManager
from Generate_branches.game.task_chain import TaskChain
from Generate_branches.game.branch_manager import BranchManager
from Generate_branches.game.npc import NPC
from Generate_branches.utils.helpers import parse_player_input, log_message, timestamp_to_readable

# Game constants - locations from our cyberpunk narrative
LOCATIONS = {
    "0": {
        "name": "Ronan's Office",
        "description": "A dimly-lit office with a polished desk. The gangster boss sits behind it, surrounded by high-tech screens and neon lighting."
    },
    "1": {
        "name": "Alley Meeting Spot",
        "description": "A dark alleyway with cracked concrete and rusting pipes. The air is filled with smoke and the scent of industrial decay."
    },
    "2": {
        "name": "Abandoned Factory",
        "description": "A dimly lit room on the second floor of an appropriated chow factory, with exposed cables and pipes. Trash bags pile in the corners."
    },
    "3": {
        "name": "Hacker Shop",
        "description": "A neon-lit backstreet shop buzzing with digital intrigue. Vintage cyber gear mixes with state-of-the-art tech in this gritty underworld hub."
    },
    "4": {
        "name": "Player's Apartment",
        "description": "A compact, cluttered apartment with neon lights seeping through the blinds. Multiple screens and tangled cables dominate the space."
    }
}

# Cyberpunk tasks for the demo
DEMO_TASKS = {
    "beginning": "Beginning",
    "meet_meredith": "Meet with Meredith Stout",
    "pickup_goods": "Picking Up Goods",
    "clear_virus": "Clear Virus", 
    "contact_meredith": "Contact Meredith Stout"
}

def create_demo_game(task_name: str = None):
    """
    Create a demo game with the cyberpunk narrative.
    
    This function creates a game manager, initializes relevant NPCs based on the task,
    and sets up the initial game state.
    
    Args:
        task_name: Optional specific task to start with
        
    Returns:
        GameManager instance with the demo game loaded
    """
    # Create game manager
    game_manager = GameManager(game_name="Cyberpunk Narrative Demo")
    
    # Create branch manager to handle tasks
    branch_manager = BranchManager()
    
    # Determine which task to load
    task_to_load = task_name if task_name else DEMO_TASKS["beginning"]
    
    # Generate task chain for the selected task
    task_chain = branch_manager.generate_task_chain(task_to_load)
    
    if not task_chain:
        # Fallback to a simple chain if generation fails
        task_chain = create_fallback_chain(task_to_load)
    
    # Determine task location for initializing relevant NPCs
    location_id = task_chain.location_id if task_chain else "0"
    
    # Dictionary mapping task names to required NPCs
    task_npcs = {
        "Beginning": ["ronan"],
        "Meet with Meredith Stout": ["meredith_stout"],
        "Picking Up Goods": ["royce", "dum_dum"],
        "Clear Virus": ["joe"],
        "Contact Meredith Stout": ["meredith_stout"]
    }
    
    # Default NPCs to initialize for all tasks
    default_npcs = ["ronan"]  # Always include key NPCs
    
    # Determine which NPCs to initialize based on the current task
    required_npcs = set(default_npcs).union(task_npcs.get(task_to_load, []))
    
    # Define all possible NPCs (only initialize those needed)
    available_npcs = {
        "ronan": {
            "name": "Ronan",
            "traits": {"authority": 90, "intimidation": 85, "cunning": 80},
            "background": "A powerful gangster boss who controls the local criminal activities. Known for being calculating and ruthless.",
            "location": "0"  # Ronan's Office
        },
        "meredith_stout": {
            "name": "Meredith Stout",
            "traits": {"aggression": 85, "caution": 80, "corporate": 90},
            "background": "A corporate agent who's investigating the missing goods. She's known for her no-nonsense approach and aggressive tactics.",
            "location": "1"  # Alley
        },
        "royce": {
            "name": "Royce",
            "traits": {"greed": 90, "volatility": 85, "tech_savvy": 75},
            "background": "The leader of the Maelstrom gang, who currently possesses the robot. He's unpredictable and opportunistic.",
            "location": "2"  # Factory
        },
        "dum_dum": {
            "name": "Dum Dum",
            "traits": {"loyalty": 90, "aggression": 85, "cybernetic": 95},
            "background": "Royce's right-hand man, heavily enhanced with cybernetics. He's intimidating and fiercely loyal to Royce.",
            "location": "2"  # Factory
        },
        "joe": {
            "name": "Joe",
            "traits": {"tech_expertise": 95, "street_smarts": 80, "pragmatism": 85},
            "background": "A skilled hacker who runs an underground tech shop. He's known for his practical approach to business and his technical knowledge.",
            "location": "3"  # Hacker Shop
        }
    }
    
    # Initialize only the needed NPCs
    for npc_id in required_npcs:
        if npc_id in available_npcs:
            npc_data = available_npcs[npc_id]
            npc = NPC(
                npc_id=npc_id,
                name=npc_data["name"],
                initial_traits=npc_data["traits"],
                background=npc_data["background"]
            )
            
            # Register NPC and set location
            game_manager.game_state.register_npc(npc.state)
            npc.state.move_to_location(npc_data["location"])
    
    # Add task chain to game manager
    game_manager.add_task_chain(task_chain)
    
    # Set initial game state
    game_manager.current_chain_id = task_chain.chain_id
    
    if task_chain.tasks:
        game_manager.current_task_id = task_chain.tasks[0].task_id
        
        if task_chain.tasks[0].subtasks:
            game_manager.current_subtask_id = task_chain.tasks[0].subtasks[0].subtask_id
    
    # Set player's initial location based on the task
    game_manager.game_state.player_location = location_id
    
    return game_manager

def create_fallback_chain(task_name: str) -> TaskChain:
    """
    Create a fallback task chain if LLM generation fails.
    
    Args:
        task_name: Name of the task
    
    Returns:
        A simple TaskChain with basic content
    """
    # Find matching task data
    task_id = None
    location_id = "0"
    
    for task_id_key, name in DEMO_TASKS.items():
        if name == task_name:
            task_id = task_id_key
            break
    
    # Find location for the task
    for location in LOCATIONS:
        if location == location_id:
            break
    
    # Create a simple chain
    chain_id = f"{task_id}_chain" if task_id else "fallback_chain"
    
    chain = TaskChain(
        chain_id=chain_id,
        location_id=location_id,
        name=task_name,
        description=LOCATIONS.get(location_id, {}).get("description", "A cyberpunk location.")
    )
    
    # Create a simple task
    from Generate_branches.models.task import Task
    from Generate_branches.models.subtask import ScriptedSubTask
    from Generate_branches.models.layer import Layer
    
    task = Task(
        task_id=task_id if task_id else "fallback_task",
        title=task_name,
        description=f"A task related to {task_name}",
        location_id=location_id,
        timestamp=0
    )
    
    # Create a layer
    main_layer = Layer(
        layer_id=0,
        name="Main Path",
        description="The primary narrative path",
        priority=100
    )
    
    # Create a basic subtask
    subtask = ScriptedSubTask(
        subtask_id=f"{task_id}_intro" if task_id else "fallback_subtask",
        title=f"Introduction to {task_name}",
        description=f"Beginning the {task_name} task",
        dialogue=f"You are about to begin the {task_name} task in this cyberpunk world.",
        npc_reactions={},
        player_options=[
            "Continue with the task",
            "Ask for more information",
            "Look around the area"
        ],
        layer=0,
        next_transitioning_question="What happens next in this scenario?"
    )
    
    # Add the subtask to the layer and task
    main_layer.add_subtask(subtask)
    task.add_subtask(subtask)
    
    # Add the task to the chain
    chain.add_task(task)
    
    return chain

def display_subtask(subtask, game_state):
    """
    Display a subtask to the player.
    
    Args:
        subtask: The subtask to display
        game_state: Current game state
    """
    # Get game timestamp
    timestamp_str = timestamp_to_readable(game_state.game_timestamp)
    
    # Get location name
    location_id = game_state.player_location
    location_name = LOCATIONS.get(location_id, {}).get("name", f"Location {location_id}")
    
    print("\n" + "=" * 60)
    print(f"\n{timestamp_str} - {location_name}")
    print(f"\n{subtask.title.upper()}\n")
    print(subtask.dialogue)
    print()
    
    # Display NPC reactions
    for npc_id, reaction in subtask.npc_reactions.items():
        npc_name = "Unknown"
        for npc_state in game_state.npcs.values():
            if npc_state.npc_id == npc_id:
                npc_name = npc_state.name
                break
        print(f"{npc_name} {reaction}")
    
    # Display player options
    if subtask.player_options:
        print("\nWhat will you do?")
        for i, option in enumerate(subtask.player_options, 1):
            print(f"{i}. {option}")
    
    print("\n" + "=" * 60)
    print("\nEnter your choice (number or text), or type 'help' for commands.")

def get_npc_response(npc_id, dialogue_type, game_state):
    """
    Get a response from an NPC based on their dialogue type.
    This is a simplified version that returns generic responses.
    
    Args:
        npc_id: ID of the NPC
        dialogue_type: Type of dialogue to retrieve
        game_state: Current game state
        
    Returns:
        Dialogue text
    """
    # Simple generic responses based on NPC
    responses = {
        "ronan": [
            "Ronan narrows his eyes, clearly weighing your words carefully.",
            "With a dismissive gesture, Ronan makes it clear he expects results, not excuses.",
            "A slight nod from Ronan indicates his approval of your approach."
        ],
        "meredith_stout": [
            "Meredith's cold stare betrays no emotion as she processes your response.",
            "With corporate efficiency, Meredith cuts straight to the point.",
            "A flash of suspicion crosses Meredith's face before she composes herself."
        ],
        "royce": [
            "Royce laughs maniacally, clearly enjoying the tension of the situation.",
            "With a dangerous gleam in his eye, Royce fingers his weapon while considering your words.",
            "Royce spits on the ground, showing his disdain for your position."
        ],
        "dum_dum": [
            "Dum Dum's cybernetic implants whir as he processes what you've said.",
            "With mechanical precision, Dum Dum shifts his stance to a more threatening position.",
            "Dum Dum grunts, his modified face impossible to read."
        ],
        "joe": [
            "Joe's fingers continue typing even as he responds to you.",
            "With a tech-savvy smirk, Joe seems to find your situation amusing.",
            "Joe nods professionally, already calculating the cost of his services."
        ]
    }
    
    if npc_id in responses:
        return random.choice(responses[npc_id])
    else:
        return "They acknowledge your presence but say nothing specific."

def run_demo(task_name: str = None):
    """
    Run the demo game in an interactive console loop.
    
    Args:
        task_name: Optional specific task to start with
    """
    # Create the demo game
    game_manager = create_demo_game(task_name)
    
    print("\n" + "=" * 60)
    print("CYBERPUNK NARRATIVE DEMO")
    print("A Demo of the LLM Narrative Game Engine")
    print("=" * 60)
    
    task_desc = task_name if task_name else DEMO_TASKS["beginning"]
    print(f"\nStarting task: {task_desc}")
    print("\nType 'help' at any time to see available commands.")
    print("\nPress Enter to begin...")
    input()
    
    # Main game loop
    running = True
    while running:
        # Get current subtask
        current_subtask = game_manager.get_current_subtask()
        
        if not current_subtask:
            print("\nThe end of this narrative branch has been reached.")
            print("Thank you for playing!")
            running = False
            continue
            
        # Display current subtask
        display_subtask(current_subtask, game_manager.game_state)
        
        # Get player input
        player_input = input("\n> ").strip()
        
        # Parse input
        parsed_input = parse_player_input(player_input, current_subtask.player_options)
        
        # Handle commands
        if parsed_input["type"] == "command":
            if parsed_input["value"] == "quit":
                print("Goodbye! Thanks for playing.")
                running = False
                continue
            elif parsed_input["value"] == "help":
                print("\nAvailable commands:")
                print("  help - Show this help message")
                print("  quit - Exit the game")
                print("  save - Save the game (not implemented in demo)")
                print("  load - Load a saved game (not implemented in demo)")
                print("  look - Look around the current location")
                print("  tasks - Show available tasks")
                print("\nYou can also enter the number or text of an option to choose it.")
                input("\nPress Enter to continue...")
                continue
            elif parsed_input["value"] == "look":
                location_id = game_manager.game_state.player_location
                location_desc = LOCATIONS.get(location_id, {}).get("description", "You see nothing special.")
                print(f"\n{location_desc}")
                
                # Show NPCs in the location
                npcs_here = []
                for npc_id, npc_state in game_manager.game_state.npcs.items():
                    if npc_state.current_location == location_id:
                        npcs_here.append(npc_state.name)
                
                if npcs_here:
                    print(f"\nPresent here: {', '.join(npcs_here)}")
                else:
                    print("\nThere's no one else here.")
                    
                input("\nPress Enter to continue...")
                continue
            elif parsed_input["value"] == "tasks":
                print("\nAvailable tasks:")
                for task_id, task_name in DEMO_TASKS.items():
                    print(f"  {task_id} - {task_name}")
                print("\nUse 'load [task_id]' to switch to a different task.")
                input("\nPress Enter to continue...")
                continue
            elif parsed_input["value"].startswith("load "):
                task_id = parsed_input["value"].split(" ")[1].strip()
                if task_id in DEMO_TASKS:
                    print(f"\nSwitching to task: {DEMO_TASKS[task_id]}")
                    # Restart the game with the new task
                    game_manager = create_demo_game(DEMO_TASKS[task_id])
                    print("\nTask loaded. Press Enter to continue...")
                    input()
                    continue
                else:
                    print(f"\nUnknown task ID: {task_id}")
                    print("Available task IDs:", ", ".join(DEMO_TASKS.keys()))
                    input("\nPress Enter to continue...")
                    continue
            elif parsed_input["value"] in ["save", "load"]:
                print(f"Note: {parsed_input['value']} functionality is not implemented in this demo.")
                input("\nPress Enter to continue...")
                continue
        
        # Handle player choice
        response = game_manager.handle_player_input(player_input)
        
        # Advance the game state
        game_manager.game_state.advance_time(1)
        
if __name__ == "__main__":
    # Check if a specific task was specified
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
        if task_id in DEMO_TASKS:
            run_demo(DEMO_TASKS[task_id])
        else:
            print(f"Unknown task ID: {task_id}")
            print("Available task IDs:", ", ".join(DEMO_TASKS.keys()))
    else:
        run_demo() 