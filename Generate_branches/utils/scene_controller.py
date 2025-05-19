import json
import os
import sys
import glob
from typing import Dict, List, Optional, Union, Tuple

class SceneController:

    # Pass the BackgroundSimulator Reference to ensure that the SceneController has a reference to the BackgroundSimulator so it can call the evaluate_player_input method. You can modify the SceneController constructor to accept this reference:
    def __init__(self, background_simulator):
        """Initialize the scene controller with a reference to the simulator"""
        self.background_simulator = background_simulator
        self.scene = None
        self.current_layer = 0
        self.subtasks = []
        self.current_subtask = None
        self.interaction_mode = "normal"
        
    def load_scene(self, scene: Dict) -> bool:
        """Load a scene and its subtasks"""
        self.scene = scene
        self.current_layer = 0
        self.subtasks = []
        self.current_subtask = None
        
        # Get scene name (some use 'name', others use 'scene_name')
        scene_name = scene.get("name") or scene.get("scene_name")
        if not scene_name:
            print("Error: Scene has no name")
            return False
            
        # Try to find the scene folder in data
        scene_folders = self._find_scene_folders(scene_name)
        if not scene_folders:
            print(f"Error: Could not find data folder for scene '{scene_name}'")
            return False
            
        # Load subtasks from the folder
        scene_folder = scene_folders[0]  # Use the first matching folder
        subtasks = self._load_subtasks(scene_folder)
        if not subtasks:
            print(f"Error: No subtasks found for scene '{scene_name}'")
            return False
            
        # Sort subtasks by layer
        self.subtasks = sorted(subtasks, key=lambda x: x.get("layer", 0))
        
        # Display scene environment
        self._display_environment()
        
        return True
    
    def _find_scene_folders(self, scene_name: str) -> List[str]:
        """Find folders that match the scene name"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            
            # Replace spaces with underscores and remove special characters
            clean_name = scene_name.replace(" ", "_")
            
            # Look for folders that start with the scene name
            matching_folders = []
            for folder in os.listdir(data_dir):
                folder_path = os.path.join(data_dir, folder)
                if os.path.isdir(folder_path) and folder.startswith(clean_name):
                    matching_folders.append(folder_path)
                    
            return matching_folders
        except Exception as e:
            print(f"Error finding scene folders: {e}")
            return []
    
    def _load_subtasks(self, scene_folder: str) -> List[Dict]:
        """Load all subtask layers from a scene folder"""
        try:
            # Find the scripted subtask folder
            scripted_folders = [
                folder for folder in os.listdir(scene_folder) 
                if os.path.isdir(os.path.join(scene_folder, folder)) and "scripted_subtask" in folder.lower()
            ]
            
            if not scripted_folders:
                print(f"Error: No scripted subtask folder found in {scene_folder}")
                return []
                
            scripted_folder = os.path.join(scene_folder, scripted_folders[0])
            
            # Find all layer JSON files
            layer_files = glob.glob(os.path.join(scripted_folder, "scripted_subtask_layer*.json"))
            
            subtasks = []
            for layer_file in layer_files:
                try:
                    with open(layer_file, 'r') as file:
                        data = json.load(file)
                        
                        # Extract the subtask from the raw_response
                        # The raw_response might be in ```json format or just a JSON string
                        if "raw_response" in data:
                            raw_response = data["raw_response"]
                            
                            # Remove json code block markers if present
                            if raw_response.startswith("```json"):
                                raw_response = raw_response[7:].strip()
                            if raw_response.endswith("```"):
                                raw_response = raw_response[:-3].strip()
                                
                            # Parse the JSON
                            subtask = json.loads(raw_response)
                            
                            # Add some data from the layer file
                            subtask["layer_file"] = os.path.basename(layer_file)
                            
                            # Add the key questions from task_info if available
                            if "task_info" in data and "key_questions" in data["task_info"]:
                                subtask["key_questions"] = data["task_info"]["key_questions"]
                                
                            subtasks.append(subtask)
                            
                except Exception as e:
                    print(f"Error parsing subtask file {layer_file}: {e}")
                    
            return subtasks
                    
        except Exception as e:
            print(f"Error loading subtasks: {e}")
            return []
    
    def _display_environment(self):
        """Display the scene environment description"""
        if not self.scene:
            return
            
        print("\n=== Scene Environment ===")
        environment = self.scene.get("environment", "No environment description available.")
        print(environment)
        print("========================\n")
    
    def display_subtask(self, layer: Optional[int] = None):
        """Display a specific layer's subtask or the current one"""
        if layer is not None:
            # Find the subtask for the specified layer
            for subtask in self.subtasks:
                if subtask.get("layer") == layer:
                    self.current_subtask = subtask
                    self.current_layer = layer
                    break
            else:
                print(f"Error: No subtask found for layer {layer}")
                return
        elif not self.current_subtask:
            # If no layer specified and no current subtask, use the first one
            if self.subtasks:
                self.current_subtask = self.subtasks[0]
                self.current_layer = self.current_subtask.get("layer", 1)
            else:
                print("Error: No subtasks available")
                return
        
        subtask = self.current_subtask
        
        print(f"\n=== Subtask (Layer {subtask.get('layer', 'Unknown')}) ===")
        print(f"Title: {subtask.get('title', 'Untitled')}")
        print(f"\nDescription: {subtask.get('description', 'No description')}")
        print("\nDialogue:")
        print(subtask.get('dialogue', 'No dialogue'))
        
        # Display NPC reactions if any
        npc_reactions = subtask.get('npc_reactions', {})
        if npc_reactions:
            print("\nNPC Reactions:")
            for npc, reaction in npc_reactions.items():
                print(f"- {npc}: {reaction}")
        
        # Display player options if any
        player_options = subtask.get('player_options', [])
        if player_options:
            print("\nPlayer Options:")
            for i, option in enumerate(player_options, 1):
                print(f"{i}. {option}")
        
        # Display key questions
        key_questions = subtask.get('key_questions', [])
        if key_questions:
            print("\nKey Questions:")
            for question in key_questions:
                print(f"- {question.get('english', '')}")
        
        print("============================\n")

        # Allow player to input their choice as text    # Allow player to input their choice as text
        player_input = input("\nEnter your choice (or type your response): ")
        
        # Add the current layer information to the input context
        input_context = {
            'input': player_input,
            'current_layer': self.current_layer,
            'current_subtask': self.current_subtask
        }
        
        # Pass the input with context to the background simulator
        self.background_simulator.evaluate_player_input(player_input)
    
    def set_interaction_mode(self, mode: str):
        """Set the interaction mode and handle any necessary state changes."""
        valid_modes = ["normal", "continue"]
        if mode not in valid_modes:
            print(f"Invalid interaction mode: {mode}")
            return
        
        self.interaction_mode = mode
        if mode == "continue":
            # Clear any pending navigation options
            print("\n" * 2)  # Add some space for clarity
            
    def has_next_layer(self) -> bool:
        """Check if there's a next layer available"""
        if not self.subtasks:
            return False
            
        next_layer = self.current_layer + 1
        return any(subtask.get("layer") == next_layer for subtask in self.subtasks)
    
    def has_previous_layer(self) -> bool:
        """Check if there's a previous layer available"""
        if not self.subtasks or self.current_layer <= 1:
            return False
            
        prev_layer = self.current_layer - 1
        return any(subtask.get("layer") == prev_layer for subtask in self.subtasks)
    
    def display_layer_options(self):
        """Display options for the current layer"""
        if self.interaction_mode != "normal":
            return []  # Return empty options in continue mode
        
        options = []
        
        if self.has_next_layer():
            options.append(f"View Layer {self.current_layer + 1}")
            
        if self.has_previous_layer():
            options.append(f"Go back to Layer {self.current_layer - 1}")
            
        options.append("Quit Scene")
        
        print("\nOptions:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
            
        return options
    
    def handle_input(self, choice: str, options: List[str]) -> bool:
        """Handle user input for layer navigation
        
        Returns:
            bool: True to continue, False to exit the scene
        """
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(options):
                print("Invalid choice")
                return True
                
            selected = options[idx]
            
            if "View Layer" in selected:
                next_layer = self.current_layer + 1
                self.display_subtask(next_layer)
                return True
                
            elif "Go back to Layer" in selected:
                prev_layer = self.current_layer - 1
                self.display_subtask(prev_layer)
                return True
                
            elif "Quit Scene" in selected:
                print("Exiting scene...")
                return False
                
        except ValueError:
            print("Please enter a valid number")
            
        return True
    
    def run(self):
        """Main loop for the scene controller"""
        if not self.scene:
            print("Error: No scene loaded")
            return
            
        # Display the first subtask
        self.display_subtask(1)
        
        # Main interaction loop
        running = True
        while running:
            options = self.display_layer_options()
            choice = input("\nEnter your choice (or type your response): ")
            if not options:  # No options to display, wait for player input
                player_input = input("\nEnter your response: ")
                self.background_simulator.evaluate_player_input(player_input)
            else:
                choice = input("\nEnter your choice (or type your response): ")
                
                # Handle player input
                if choice.isdigit():
                    running = self.handle_input(choice, options)
                else:
                    # Pass the input back to the BackgroundSimulator for evaluation
                    self.background_simulator.evaluate_player_input(choice)

def main():
    """For testing purposes only"""
    # This would be called from sys_controller in practice
    pass

if __name__ == "__main__":
    main()
