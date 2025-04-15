import json
import os
import sys
from typing import Dict, List, Optional, Union, Tuple

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
        
    def load_scenes(self, json_path: str) -> List[Dict]:
        """Load scenes from the JSON file"""
        try:
            # Handle relative paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            absolute_path = os.path.join(base_dir, json_path)
            
            if not os.path.exists(absolute_path):
                # Try with different path
                absolute_path = os.path.join(base_dir, "..", "data", "Scripted_tasks.json")
            
            with open(absolute_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading scene data: {e}")
            return []
    
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
            
        # Enter the scene
        self.current_scene = scene
        self.energy_pt -= 1
        
        scene_display_name = scene.get("name") or scene.get("scene_name")
        print(f"Entered scene: {scene_display_name}")
        print(f"Energy points: {self.energy_pt}")
        return True
    
    def exit_scene(self):
        """Exit the current scene"""
        if self.current_scene:
            scene_name = self.current_scene.get("name") or self.current_scene.get("scene_name")
            print(f"Exited scene: {scene_name}")
            self.current_scene = None
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
                    self.enter_scene(scene_name)
                
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
                
            else:
                print("Invalid choice. Please enter a number from 1 to 8.")


def main():
    """Entry point for the simulator"""
    simulator = BackgroundSimulator()
    simulator.main_loop()


if __name__ == "__main__":
    main()
