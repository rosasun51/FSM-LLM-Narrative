import json
import os
import sys
import requests
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple
import glob

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the SceneController
try:
    from utils.scene_controller import SceneController
    from utils.constants import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL  # Import constants
    from utils.m1_evaluation import InputEvaluator
    from utils.config import EVALUATION_METHOD

except ImportError:
    # Handle relative import
    from scene_controller import SceneController
    from .constants import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL  # Import constants
    from .m1_evaluation import InputEvaluator
    from .config import EVALUATION_METHOD

from .evaluation_strategies import (
    EvaluationStrategy,
    OriginalEvaluationStrategy,
    MethodIEvaluationStrategy,
    MethodIIEvaluationStrategy,
    HybridEvaluationStrategy
)

class BackgroundSimulator:
    def __init__(self, json_path: str = "../data/Scripted_tasks.json"):
        """Initialize the simulator with default values and load scene data"""
        # Game state
        self.chapter_num = 1
        self.day_num = 1
        self.energy_pt = 3
        self.special_info = []
        
        # Load scene data
        self.scenes = self.load_scenes(json_path)
        self.current_scene = None
        
        # Initialize scene controller
        self.scene_controller = SceneController(self)
        self.input_evaluator = InputEvaluator()

        # Initialize interaction state
        self.interaction_mode = "normal"  # Add this line
        self.current_layer = 1  # Add this line too for consistency

        self.evaluation_strategy = self.configure_evaluation_strategy()
    
    def configure_evaluation_strategy(self):
        """Configure which evaluation strategy to use"""
        # You can change this variable to switch between methods
        current_strategy = "original"  # Options: "original", "method_i", "method_ii", "hybrid"

        if current_strategy == "original":
            return OriginalEvaluationStrategy(self.input_evaluator)
        elif current_strategy == "method_i":
            # Initialize your Method I evaluator here
            return MethodIEvaluationStrategy(self.improved_prompt_evaluator)
        elif current_strategy == "method_ii":
            # Initialize your Method II evaluator here
            return MethodIIEvaluationStrategy(self.pde_classifier)
        elif current_strategy == "hybrid":
            # Initialize your hybrid evaluator here
            return HybridEvaluationStrategy(self.pde_classifier, self.improved_prompt_evaluator)
        else:
            return OriginalEvaluationStrategy(self.input_evaluator)
        
    def configure_evaluation_strategy(self):
        if EVALUATION_METHOD == "original":
            return OriginalEvaluationStrategy(self.input_evaluator)
        elif EVALUATION_METHOD == "method_i":
            return MethodIEvaluationStrategy(self.improved_prompt_evaluator)
        elif EVALUATION_METHOD == "method_ii":
            return MethodIIEvaluationStrategy(self.pde_classifier)
        elif EVALUATION_METHOD == "hybrid":
            return HybridEvaluationStrategy(self.pde_classifier, self.improved_prompt_evaluator)
        else:
            return OriginalEvaluationStrategy(self.input_evaluator)

    def load_scenes(self, json_path: str) -> List[Dict]:
        """Load scenes from the JSON file and associated subtask files."""
        scenes = []
        try:
            # Load main scenes
            base_dir = os.path.dirname(os.path.abspath(__file__))
            absolute_path = os.path.join(base_dir, json_path)
            
            if not os.path.exists(absolute_path):
                # Try with different path
                absolute_path = os.path.join(base_dir, "..", "data", "Scripted_tasks.json")
            
            with open(absolute_path, 'r') as file:
                scenes = json.load(file)
                print("Scenes loaded successfully:", scenes)  # Debug statement

            # Load subtasks from the relevant folders
            subtask_folders = [
                os.path.join(base_dir, "..", "data", "Beginning_20250415_180747", "Scripted_subtask_20250415_180747"),
                os.path.join(base_dir, "..", "data", "Beginning_20250415_180747", "Subtask_branches_20250415_180747")
            ]
            
            for folder in subtask_folders:
                layer_files = glob.glob(os.path.join(folder, "*.json"))  # Load all JSON files in the folder
                for layer_file in layer_files:
                    with open(layer_file, 'r') as f:
                        subtask_data = json.load(f)
                        raw_response = subtask_data.get("raw_response", "")
                        try:
                            subtask = json.loads(raw_response)
                            # Add the subtask to the corresponding scene
                            # Assuming you want to append it to the first scene for demonstration
                            if scenes:
                                scenes[0].setdefault('subtasks', []).append(subtask)
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON from {layer_file}: {raw_response}")

        except Exception as e:
            print(f"Error loading scene data: {e}")
        
        return scenes
    
    def is_scene_available(self, scene: Dict) -> bool:
        """Check if a scene is available based on current game state"""
        # Check if there's a time condition
        if "trigger_conditions" not in scene:
            return False
            
        time_condition = scene.get("trigger_conditions", {}).get("time_condition")
        if not time_condition:
            return False
            
        # Parse time condition
        try:
            chapter_str, day_str = time_condition.split(";")
            scene_chapter = int(chapter_str)
            
            # Check chapter match
            if scene_chapter != self.chapter_num:
                return False
                
            # Check day match - can be a single day or a range
            if "," in day_str:
                start_day, end_day = map(int, day_str.split(","))
                if not (start_day <= self.day_num <= end_day):
                    return False
            else:
                scene_day = int(day_str)
                if scene_day != self.day_num:
                    return False
                    
            # Check energy
            if self.energy_pt < 1:
                return False
                
            # Check additional conditions
            additional_conditions = scene.get("trigger_conditions", {}).get("additional_conditions")
            if additional_conditions and additional_conditions not in self.special_info:
                return False
                
            return True
            
        except Exception as e:
            print(f"Error parsing time condition '{time_condition}': {e}")
            return False
    
    def get_available_scenes(self) -> List[Dict]:
        """Get all scenes that are available with current game state"""
        return [scene for scene in self.scenes if self.is_scene_available(scene)]
    
    def enter_scene(self, scene_name: str) -> bool:
        """Try to enter a scene by name"""
        # Find the scene by name
        scene = None
        for s in self.scenes:
            if s.get("name", "") == scene_name or s.get("scene_name", "") == scene_name:
                scene = s
                break
                
        if not scene:
            print(f"Scene '{scene_name}' not found.")
            return False
            
        # Check if the scene is available
        if not self.is_scene_available(scene):
            print(f"Scene '{scene_name}' is not available yet.")
            return False
         # Reset interaction state when entering a scene
        self.interaction_mode = "normal"
        self.current_layer = 1    
          
        # Enter the scene
        self.current_scene = scene  # Ensure this is set correctly
        print(f"Current Scene: {self.current_scene}")  # Debugging output
        print("Current Scene Subtasks:", self.current_scene.get('subtasks', []))
        self.energy_pt -= 1
        
        scene_display_name = scene.get("name") or scene.get("scene_name")
        print(f"Entered scene: {scene_display_name}")
        print(f"Energy points: {self.energy_pt}")
        
        # Launch scene controller for this scene
        self._launch_scene_controller()

        # Display all available nodes after entering the scene
        self.display_all_nodes()  # Call the new method to display all nodes# Call the new method to display all nodes# Call the new method to display all nodes# Call the new method to display all nodes

        # Display subtasks for each layer after entering the scene
        for layer in range(1, 2):  # Adjust the range based on the number of layers you have
            self.display_subtasks_by_layer(layer)

        # Allow player to provide input after entering the scene
        while self.current_scene:
            if self.interaction_mode == "continue":
                player_message = input("Your response: ")
                if player_message.lower() == "quit scene":
                    self.exit_scene()
                    break
                self.evaluate_player_input(player_message)
            else:
                self.display_scene_options()
                choice = input("Enter your choice (or type your response): ")
                if choice == "1":  # View next layer
                    next_layer = self.current_layer + 1
                    if next_layer <= self.get_total_layers():
                        self.current_layer = next_layer
                        self.display_subtasks_by_layer(next_layer)
                elif choice == "2":  # Quit scene
                    self.exit_scene()
                    break
                else:
                    self.evaluate_player_input(choice)
                    if self.interaction_mode == "continue":
                         continue

        return True
    
    def display_scene_options(self):
        """Display scene options only in normal mode"""
        if self.interaction_mode != "continue":
            print("\nOptions:")
            if self.current_layer < self.get_total_layers():
                print(f"1. View Layer {self.current_layer + 1}")
            print("2. Quit Scene")
    
    def _launch_scene_controller(self):
        """Launch the scene controller for the current scene"""
        if not self.current_scene:
            return
            
        # Load the scene into the scene controller
        success = self.scene_controller.load_scene(self.current_scene)
        if success:
            # Run the scene controller
            self.scene_controller.run()
    
    def exit_scene(self):
        """Exit the current scene"""
        if self.current_scene:
            scene_name = self.current_scene.get("name") or self.current_scene.get("scene_name")
            print(f"Exited scene: {scene_name}")
            self.current_scene = None  # Set current_scene to None to indicate no active scene
            print("Current scene status:", self.current_scene)  # Debugging output
             # Display available scenes again
            self.display_available_scenes()  # Show available scenes after exit
        else:
            print("You are not in any scene.")
    
    def reset_state(self, chapter_num: int, day_num: int, energy_pt: int, special_info: List[str] = None):
        """Reset the game state"""
        self.chapter_num = chapter_num
        self.day_num = day_num
        self.energy_pt = energy_pt
        self.special_info = special_info or []
        self.current_scene = None
        print(f"Game state reset to: Chapter {chapter_num}, Day {day_num}, Energy {energy_pt}")
        if special_info:
            print(f"Special info: {', '.join(special_info)}")
    
    def display_game_state(self):
        """Display the current game state"""
        print("\n=== Current Game State ===")
        print(f"Chapter: {self.chapter_num}")
        print(f"Day: {self.day_num}")
        print(f"Energy Points: {self.energy_pt}")
        if self.special_info:
            print(f"Special Info: {', '.join(self.special_info)}")
        
        if self.current_scene:
            scene_name = self.current_scene.get("name") or self.current_scene.get("scene_name")
            print(f"Current Scene: {scene_name}")
        
        print("========================\n")
    
    def display_available_scenes(self):
        """Display all available scenes"""
        available_scenes = self.get_available_scenes()
        
        print("\n=== Available Scenes ===")
        if not available_scenes:
            print("No scenes available with current state.")
        else:
            for i, scene in enumerate(available_scenes, 1):
                scene_name = scene.get("name") or scene.get("scene_name")
                print(f"{i}. {scene_name}")
        print("======================\n")
    
    def display_all_scenes(self):
        """Display all scenes and their availability"""
        print("\n=== All Scenes ===")
        for i, scene in enumerate(self.scenes, 1):
            scene_name = scene.get("name") or scene.get("scene_name")
            available = "Available" if self.is_scene_available(scene) else "Not Available"
            
            # Get time condition for display
            time_condition = scene.get("trigger_conditions", {}).get("time_condition", "Unknown")
            additional = scene.get("trigger_conditions", {}).get("additional_conditions", "None")
            
            print(f"{i}. {scene_name} - {available}")
            print(f"   Time: {time_condition}, Additional: {additional}")
        print("================\n")
    
    def add_special_info(self, info: str):
        """Add a special info to the game state"""
        if info not in self.special_info:
            self.special_info.append(info)
            print(f"Added special info: {info}")
    
    def main_loop(self):
        """Main interactive loop for the simulator"""
        print("\n=== Background Simulator ===")
        print("Welcome to the Scene Background Simulator!")
        
        while True:
            print("\nOptions:")
            print("1. Display game state")
            print("2. View available scenes")
            print("3. View all scenes")
            print("4. Enter a scene")
            print("5. Exit current scene")
            print("6. Reset game state")
            print("7. Add special info")
            print("8. Quit simulator")
            
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == "1":
                self.display_game_state()
                
            elif choice == "2":
                self.display_available_scenes()
                
            elif choice == "3":
                self.display_all_scenes()
                
            elif choice == "4":
                if self.current_scene:
                    print("You're already in a scene. Exit current scene first.")
                    continue
                    
                self.display_available_scenes()
                scene_name = input("Enter scene name to enter (or press Enter to cancel): ")
                if scene_name:
                    if self.enter_scene(scene_name):
                        # After entering the scene, display available layers
                        self.display_available_layers()
                    
            elif choice == "5":
                self.exit_scene()
                
            elif choice == "6":
                try:
                    chapter = int(input("Enter chapter number: "))
                    day = int(input("Enter day number: "))
                    energy = int(input("Enter energy points: "))
                    special = input("Enter special info (comma-separated, or press Enter for none): ")
                    
                    special_list = [s.strip() for s in special.split(",")] if special else []
                    self.reset_state(chapter, day, energy, special_list)
                except ValueError:
                    print("Please enter valid numbers for chapter, day, and energy.")
                
            elif choice == "7":
                info = input("Enter special info to add: ")
                if info:
                    self.add_special_info(info)
                
            elif choice == "8":
                print("Exiting simulator. Goodbye!")
                break

    # Additional 0417: New add functionality         
    def evaluate_player_input(self, player_input: str, root_id: str = "T1"):
        """Evaluate player input using the new evaluation system."""
        if not self.current_scene:
            print("No active scene.")
            return
        
        available_nodes = self.get_available_nodes()
        if not available_nodes:
            print("No available nodes to evaluate.")
            return
        
        # Call the evaluation
        evaluation_result = self.input_evaluator.evaluate_player_input(
            player_input,
            self.current_scene,
            available_nodes,
            self.call_llm_api
        )

        # Save the evaluation result to a file
        self.save_evaluation_result(evaluation_result)

        # Now call the _process_evaluation_result to handle the outcome
        self._process_evaluation_result(evaluation_result)

            # Reset interaction mode after processing
        if self.interaction_mode == "continue":
            self.interaction_mode = "normal"

    def save_evaluation_result(self, evaluation_result):
        """Save the evaluation result to a file in the scene folder."""
        if not self.current_scene:
            print("No current scene to save the evaluation result.")
            return

        # Create the dynamic_outputs directory if it doesn't exist
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "..", "dynamic_outputs")
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        # Generate a unique filename for the evaluation result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_result_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)

        # Save the evaluation result to the file
        with open(file_path, 'w') as f:
            json.dump(evaluation_result, f, indent=2)

        print(f"Evaluation result saved to: {file_path}")

    def _process_evaluation_result(self, result: dict):
        """Process the evaluation result and take appropriate action."""
        print(f"\nEvaluation Results:")        
        print(f"Best matching node: {result['best_node']['title']}")
        print(f"Max similarity score: {result['similarity_score']:.2f}")
        print(f"Processing stage: {result['processing_stage']}")
        
        # Display all scores
        print("\nScores for all nodes:")
        for node_id, score in result['all_scores'].items():
            print(f"Node {node_id}: {score:.2f}")

        if result['processing_stage'] == "select_existing":
            # Ensure the best_node has a similarity_score
            best_node = result['best_node']
            if 'similarity_score' not in best_node:
                best_node['similarity_score'] = result.get('similarity_score', 0)
            self.process_existing_node(best_node)
            
        elif result['processing_stage'] == "generate_new":
            if 'new_node' in result:
                self.process_new_node(result['new_node'])  # Process the newly created node
            else:
                print("New node generation failed. Continuing with current scene...")
                self.continue_interaction()
        else:
            # This is the "continue" case
            print("\nContinuing with current scene interaction...")
            self.continue_interaction()
       
    def set_interaction_mode(self, mode: str):
        """Set the interaction mode and handle any necessary state changes."""
        valid_modes = ["normal", "continue"]
        if mode not in valid_modes:
            print(f"Invalid interaction mode: {mode}")
            return
        
        self.interaction_mode = mode
        
        # Also update scene controller's mode if it exists
        if hasattr(self, 'scene_controller'):
            self.scene_controller.set_interaction_mode(mode)

    def get_available_nodes(self):
        """Get available task nodes for the current scene."""
        if self.current_scene:
            nodes = self.current_scene.get('subtasks', [])
            print("Current Scene:", self.current_scene)  # Debugging output
            print("Retrieved available nodes:", nodes)  # Debugging output
            return nodes
        return []  # Return an empty list if no current scene


    def process_existing_node(self, node):
        self.interaction_mode = "continue" 
        """Process the selected existing node with a score above 70."""
        node_title = node.get('title')
        node_id = node.get('subtask_id')
        node_score = node.get('similarity_score')  
        current_layer = node.get('layer')

        print(f"\n=== Processing Node ===")
        print(f"Node Title: {node_title}")
        print(f"Node ID: {node_id}")
        # Ensure node_score is a valid number; default to 0.0 if not
        print(f"Score: {node_score:.2f}")
        print(f"Layer: {current_layer}")

        if node_score > 70:
            print(f"\n=== Transitioning to Node ===")
            print(f"Selected node: {node_title}")
                
            print(f"Description: {node.get('description', 'No description available')}")
            print(f"NPC Reactions: {node.get('npc_reactions', 'No reactions available.')}")

            print("Player Options:")
            for option in node.get('player_options', []):
                print(f"- {option}")

            if current_layer is not None:
                # previous_layer = self.current_layer
                self.current_layer = int(current_layer)
                print(f"\n=== Layer Transition ===")
                print(f"Transitioning to Layer {self.current_layer}")
                    
                # # Display available nodes in the new layer
                # print(f"\nAvailable nodes in Layer {self.current_layer}:")
                # self.display_subtasks_by_layer(self.current_layer)
                    
                # Set interaction mode to continue
                self.set_interaction_mode("continue")
            else:
                print("\nWarning: Layer information not available in the selected node")
                self.continue_interaction()
        else:
            print(f"Node '{node_title}' does not meet the requirement (>70)")
            print("Continuing with current layer...")
            self.continue_interaction()
  

    def process_new_node(self, new_node):
        """Process the newly generated node."""
        print(f"Processing new node: {new_node['title']}")
        # Add the new node to the current scene's subtasks
        if self.current_scene:
            self.current_scene.setdefault('subtasks', []).append(new_node)
            print(f"Added new node to the current scene.")

            # Display the new node structure
            print(f"\n=== You are now in the new node: {new_node['title']} ===")
            print(f"Description: {new_node['description']}")
            print(f"Dialogue: {new_node['player_options']}")
            print(f"NPC Reactions: {new_node['npc_reactions']}")
            
            # # Show player options
            # print("Player Options:")
            # for option in new_node.get('player_options', []):
            #     print(f"- {option}")

            # Assumed layer handling
            next_layer = new_node.get('layer')
            if next_layer is not None:
                self.display_subtasks_by_layer(int(next_layer))  # Transition to display next layer's subtasks
                self.current_layer = int(next_layer)  # Update the current layer
            else:
                print("Layer information is not available in the new node.")
            
            # After showing the new node, we can exit the scene if it’s the last layer
            if self.current_layer >= self.get_total_layers():
                self.end_scene()  # Call to end the scene here

        # Save the new node to a file
        self.save_new_node_to_file(new_node)

    # Save the new node to a file
    def save_new_node_to_file(self, new_node):
        """Save the new node to a file in the dynamic_outputs folder."""
        if not self.current_scene:
            print("No current scene to save the new node.")
            return

        # Create the dynamic_outputs directory if it doesn't exist
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "..", "dynamic_outputs")
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        # Generate a unique filename for the new node
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        node_id = new_node.get('subtask_id', 'unknown')
        filename = f"new_node_{node_id}_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)

        # Save the new node to the file
        with open(file_path, 'w') as f:
            json.dump(new_node, f, indent=2)

        print(f"New node saved to: {file_path}")

    def continue_interaction(self):
        """Continue the current NPC interaction."""
        if not self.current_scene:
            print("No active scene to continue.")
            return

        self.interaction_mode = "continue"  # Set mode to continue

        # Get the current layer's subtasks
        current_layer = self.current_layer if hasattr(self, 'current_layer') else 1
        current_subtasks = self.get_subtasks_by_layer(current_layer)

        print("\n=== Continuing Current Scene ===")
        print(f"Current Layer: {current_layer}")
        
        # Display current context and options
        if current_subtasks:
            # Show the current state of interaction
            current_subtask = current_subtasks[0]  # Get the active subtask
            print(f"Current Context: {current_subtask.get('description', '')}")
            print("\nAvailable Responses:")
            for option in current_subtask.get('player_options', []):
                print(f"- {option}")
        else:
            print("No specific options available. Please provide your response.")
        
        print("\nPlease provide your response to continue the scene...")
        # Don't show additional navigation options here

    def call_llm_api(self, prompt, retries=3, delay = 5) -> Optional[Dict]:
        api_url = f"{LLM_BASE_URL}/chat/completions"  # Adjusted endpoint
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",  # Add Bearer prefix
            "Content-Type": "application/json"
        }

        print(f"LLM_BASE_URL: {LLM_BASE_URL}")
        print(f"API URL: {api_url}")

        # Update the prompt to request a JSON response
        prompt_with_format = (
            f"{prompt}\n\n"
            "Please return the response in JSON format with the following structure:\n"
            "{\n"
            "  \"evaluation\": \"<evaluation text>\",\n"
            "  \"score\": <score>,\n"
            "  \"additional_info\": \"<any additional info>\"\n"
            "}"
        )
        
        payload = {
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt_with_format}],
            "max_tokens": 1000,  # Adjust as needed
            "temperature": 0.7,   # Adjust as needed
        }
        
        for attempt in range(retries):
            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=300)  # Increased timeout
                response.raise_for_status()  # Raise an error for bad responses
                
                # Log the response for debugging
                print("API Response:", response.json())  # Log the entire response
                return response.json()  # Return the JSON response directly
            except requests.exceptions.RequestException as e:
                print(f"Error calling API: {e}")
                return None
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                return None


    # Add 04/17: Display all nodes & Visualize
    def display_all_nodes(self):
        """Display all available nodes for the current scene."""
        if self.current_scene:
            nodes = self.current_scene.get('subtasks', [])
            print("\n=== Available Nodes ===")
            if not nodes:
                print("No nodes available in the current scene.")
            else:
                for node in nodes:
                    print(f"Subtask ID: {node['subtask_id']}, Title: {node['title']}")
            print("======================\n")
        else:
            print("No current scene to display nodes from.")

    # 
    def get_subtasks_by_layer(self, layer: int) -> List[Dict]:
        """Get subtasks for a specific layer."""
        subtasks = []
        if self.current_scene:
            for subtask in self.current_scene.get('raw response', []):
                if subtask.get('layer') == layer:
                    subtasks.append(subtask)
        return subtasks

    def display_subtasks_by_layer(self, layer: int):
        """Display all subtasks for a specific layer."""
        subtasks = self.get_subtasks_by_layer(layer)
        print(f"\n=== Subtasks for Layer {layer} ===")
        if not subtasks:
            print(f"No subtasks available for Layer {layer}.")
            # Check if all layers have been processed
            if layer >= self.get_total_layers():  # Implement this method
                print("This is the final layer. Scene can be concluded.")
                self.end_scene()  # Call method to handle the ending of the scene
        else:
            print(f"Found {len(subtasks)} subtask(s) in Layer {layer}:")
            for subtask in subtasks:
                print(f"Subtask ID: {subtask['subtask_id']}, Title: {subtask['title']}")
                print(f"Description: {subtask['description']}")
                if 'player_options' in subtask:
                    print("Available Options:")
                    for option in subtask['player_options']:
                        print(f"- {option}")
                print("---")
        print("==============================\n")   

    def transition_to_layer(self, new_layer: int):
        """Handle transition to a new layer."""
        if new_layer != self.current_layer:
            print(f"\n=== Layer Transition ===")
            print(f"Moving from Layer {self.current_layer} to Layer {new_layer}")
            self.current_layer = new_layer
            return True
        return False

    def end_scene(self):
        """Handle the ending of the current scene."""
        if self.current_scene:
            print("The scene has ended. Transitioning to the next opportunity...")
            self.current_scene = None  # Reset the current scene
            # Optionally, make the next scene available, or trigger another action
        else:
            print("No active scene to end.")

    def get_total_layers(self) -> int:
        """Return the total number of layers in the current scene."""
        if self.current_scene:
            return max(subtask.get('layer', 0) for subtask in self.current_scene.get('subtasks', []))
        return 0

    def display_available_layers(self):
        """Display available layers for the current scene."""
        if self.current_scene:
            layers = set()  # Use a set to avoid duplicates
            for subtask in self.current_scene.get('subtasks', []):
                layers.add(subtask.get('layer'))
            
            print("\n=== Available Layers ===")
            if not layers:
                print("No layers available for the current scene.")
            else:
                for layer in sorted(layers):
                    print(f"Layer {layer}")
            print("======================\n")
        else:
            print("No current scene to display layers from.")

def main():
    """Entry point for the simulator"""
    simulator = BackgroundSimulator()
    simulator.main_loop()


if __name__ == "__main__":
    main()
