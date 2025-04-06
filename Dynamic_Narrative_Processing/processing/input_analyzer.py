from typing import Dict, List, Tuple
import json
import os
import logging
from models.embedding import EmbeddingModel
from models.position_tracker import PositionTracker
from .threshold_manager import ThresholdManager
from .layer_transition import LayerTransitionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputAnalyzer:
    def __init__(self):
        """
        Initialize the input analyzer with embedding model and managers.
        """
        self.embedding_model = EmbeddingModel()
        self.position_tracker = PositionTracker()
        self.threshold_manager = ThresholdManager()
        self.layer_transition = LayerTransitionManager()
        self._load_key_questions()
    
    def _load_key_questions(self):
        """
        Load key questions for layer transitions.
        """
        try:
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            key_questions_path = os.path.join(project_root, "data", "key_questions", "key_questions.json")
            
            if os.path.exists(key_questions_path):
                with open(key_questions_path, 'r') as f:
                    self.key_questions = json.load(f)
            else:
                logger.warning(f"Key questions file not found at {key_questions_path}")
                # Default key questions if file not found
                self.key_questions = {
                    "layer1_to_layer2": {
                        "question": "What complications arise from the initial situation?",
                        "description": "Transition from initial situation to complications"
                    },
                    "layer2_to_layer3": {
                        "question": "How does the situation resolve based on these complications?",
                        "description": "Transition from complications to resolution"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error loading key questions: {str(e)}")
            raise
    
    def analyze(self, player_input: str, available_nodes: List[Dict]) -> Dict:
        """
        Analyze player input and determine appropriate action.
        
        Args:
            player_input: The player's input text
            available_nodes: List of available narrative nodes
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Calculate similarity scores with available nodes
            similarities = []
            for node in available_nodes:
                score = self.embedding_model.calculate_similarity(player_input, node["content"])
                similarities.append((node, score))
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            if not similarities:
                return {
                    "action": "continue",
                    "similarity_score": 0.0,
                    "message": "No available nodes to compare with"
                }
            
            # Get the most similar node and its score
            most_similar_node, max_similarity = similarities[0]
            
            # Determine action based on similarity score
            action, _ = self.embedding_model.process_stage(player_input, available_nodes)
            
            result = {
                "action": action,
                "similarity_score": max_similarity,
                "most_similar_node": most_similar_node if action == "select" else None,
                "all_scores": [{"node": node["id"], "score": score} for node, score in similarities]
            }
            
            # Add transition information if applicable
            if action in ["select", "generate"]:
                current_layer = most_similar_node.get("layer", 1)
                next_layer = current_layer + 1
                
                if next_layer <= 3:  # Assuming 3 layers total
                    transition_key = f"layer{current_layer}_to_layer{next_layer}"
                    if transition_key in self.key_questions:
                        result["transition"] = {
                            "from": current_layer,
                            "to": next_layer,
                            "question": self.key_questions[transition_key]["question"]
                        }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing input: {str(e)}")
            return {
                "action": "error",
                "error": str(e)
            }
    
    def process_input(self, player_input: str, episode: str, current_state: Dict) -> Dict:
        """
        Process player input through the three-stage system.
        
        Args:
            player_input: Player's input text
            episode: Current episode name
            current_state: Current game state
            
        Returns:
            Dictionary containing processing results
        """
        # Get existing nodes from current state
        existing_nodes = current_state.get("available_nodes", [])
        
        # Process through three-stage system
        action, similarity_score = self.embedding_model.process_stage(player_input, existing_nodes)
        
        result = {
            "action": action,
            "similarity_score": similarity_score,
            "current_position": self.position_tracker.get_position(),
            "current_layer": self.position_tracker.get_current_layer()
        }
        
        if action == "select":
            # Select existing node
            selected_node = self.embedding_model.find_most_similar_node(player_input, existing_nodes)
            result["selected_node"] = selected_node
            # Update position tracker
            self.position_tracker.update_position(selected_node["position"])
            
        elif action == "generate":
            # Generate new node
            current_layer = self.position_tracker.get_current_layer()
            next_layer = str(int(current_layer) + 1)
            transition_key = f"{current_layer}_to_{next_layer}"
            
            # Get key question for transition
            key_question = self.key_questions["episodes"][episode]["layer_transitions"][transition_key]["question"]
            
            # Generate new node (to be implemented in node_generator.py)
            new_node = self._generate_new_node(
                player_input,
                current_state,
                key_question,
                transition_key
            )
            
            result["generated_node"] = new_node
            # Update position tracker
            self.position_tracker.update_position(new_node["position"])
            
        else:  # action == "continue"
            # Continue current interaction
            result["message"] = "Continuing current NPC interaction"
        
        return result
    
    def _generate_new_node(self, player_input: str, current_state: Dict, 
                          key_question: str, transition_key: str) -> Dict:
        """
        Generate a new narrative node based on player input and current state.
        
        Args:
            player_input: Player's input text
            current_state: Current game state
            key_question: Key question for the transition
            transition_key: Transition identifier
            
        Returns:
            Dictionary containing the new node
        """
        # Get position range for the transition
        position_range = self.key_questions["episodes"][current_state["episode"]]["layer_transitions"][transition_key]["position_range"]
        
        # Calculate new position (S score)
        new_position = (position_range[0] + position_range[1]) / 2
        
        # Generate node content using GPT (to be implemented)
        node_content = self._generate_node_content(player_input, current_state, key_question)
        
        return {
            "content": node_content,
            "position": new_position,
            "layer": str(int(self.position_tracker.get_current_layer()) + 1),
            "is_generated": True,
            "parent_node": current_state["current_node"]["id"] if "current_node" in current_state else None
        }
    
    def _generate_node_content(self, player_input: str, current_state: Dict, 
                             key_question: str) -> str:
        """
        Generate content for a new node using GPT.
        
        Args:
            player_input: Player's input text
            current_state: Current game state
            key_question: Key question for the transition
            
        Returns:
            Generated node content
        """
        # TODO: Implement GPT-based content generation
        # This will be implemented in the node_generator.py file
        return f"Generated content based on: {player_input} and {key_question}" 