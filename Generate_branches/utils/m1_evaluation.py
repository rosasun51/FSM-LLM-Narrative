'''
This file includes 4 main methods:
1. get_processing_stage(similarity_score): Determines the processing stage based on the similarity score.
2. evaluate_player_input(player_input, current_scene, available_nodes, call_llm_api): Evaluates player input and generates a new node if needed.
3. visualize_scores: Visualize all node scores and highlight the best score.
3. generate_new_node(player_input, current_scene, best_node, call_llm_api): Generates a new node using the LLM API.

The main logic of the Score Evaluation:
The code checks the similarity score calculated by the embedding model between the player's input and each available node:
If the highest score is greater than 70: The system selects an existing node.
If the score is between 50 and 70: The system generates a new node based on the LLM's evaluation prompt.
If the score is less than 50: The system continues the current NPC interaction without selecting or generating a new node.

'''

import json
import requests
from typing import Optional 
from .m1_embedding import EmbeddingEvaluator

from Generate_branches.utils.constants import (
    LLM_MODEL, 
    LLM_BASE_URL, 
    LLM_API_KEY, 
    LLM_MAX_TOKENS, 
    DEFAULT_NUM_ALTERNATIVES,
    MIN_RATING_THRESHOLD,
    NUM_LAYERS,
    ROOT_TASK_ID,
    DATA_ROOT_PATH,
    SCRIPTED_SUBTASK_FOLDER,
    SUBTASK_BRANCHES_FOLDER,
    KEY_QUESTIONS_FILE,
    BASE_DIR
)

class InputEvaluator:
    def __init__(self):
        self.embedding_evaluator = EmbeddingEvaluator()
    
    def get_processing_stage(self, similarity_score: float) -> str:
        """Determine processing stage based on similarity score."""
        if similarity_score > 70:
            return "select_existing"
        elif 50 <= similarity_score <= 70:
            return "generate_new"
        else:
            return "continue_current"    

    def evaluate_player_input(self, player_input: str, current_scene: dict, 
                            available_nodes: list, call_llm_api) -> dict:
        node_scores = []
        for node in available_nodes:
            score = self.embedding_evaluator.evaluate_node_similarity(player_input, node)
            node_scores.append((node, score))

        # Sort nodes by score
        node_scores.sort(key=lambda x: x[1], reverse=True)
        
        if not node_scores:
            return {"status": "no_nodes", "message": "No available nodes to evaluate"}

        best_node, best_score = node_scores[0]
        processing_stage = self.get_processing_stage(best_score)

        # Prepare evaluation result
        result = {
            "best_node": best_node,
            "similarity_score": best_score,
            "processing_stage": processing_stage,
            "all_scores": {node[0]['subtask_id']: node[1] for node in node_scores}
        }

        # Visualize scores before the new node generation logic
        self.visualize_scores(result['all_scores'], best_node, best_score)

        # Generate new node if score is between 50 and 70
        if 50 <= best_score <= 70:
            new_node = self.generate_new_node(player_input, current_scene, best_node, call_llm_api)
            if new_node:
                result["new_node"] = new_node

        return result
        
    def visualize_scores(self, all_scores: dict, best_node: dict, best_score: float):
        """Visualize all node scores and highlight the best score."""
        print("\n=== Scores for Available Nodes ===")
        for node_id, score in all_scores.items():
            print(f"Node ID: {node_id}, Score: {score:.2f}")
        
        print("\n=== Best Score ===")
        if best_score > 70:
            print(f"Best Node: {best_node['title']} - Score: {best_score:.2f}")
        else:
            print("No node exceeds score 70.")
    
    def generate_new_node(self, player_input: str, current_scene: dict, best_node: dict, call_llm_api, root_id: str = "T1") -> Optional[dict]:
        # Determine parent_id and layer
        parent_id = best_node.get('subtask_id', f"{root_id}.1")
        layer = best_node.get('layer', 1) + 1

        # Find the next available index for this parent (e.g., if .1.1 and .1.2 exist, next is .1.3)
        existing_ids = [node.get('subtask_id', '') for node in current_scene.get('subtasks', [])]
        next_index = 1
        while f"{parent_id}.{next_index}" in existing_ids:
            next_index += 1
        new_subtask_id = f"{parent_id}.{next_index}"
        prompt = (
            f"Player input: '{player_input}'.\n"
            f"Current scene: {current_scene.get('name')}\n"
            f"Best matching node: {best_node['title']}(ID: {parent_id})\n"
            # f"Generated layer number: {layer_number['layer_number']}\n"
            f"Generate a new node as a child of the above node, for layer {layer}.\n"
            f"Use the following ID structure: the new node's subtask_id should be '{new_subtask_id}', and its parent_id should be '{parent_id}'.\n"
            "The NPCs should only be those already in the scene description of this layer; do not create new names.\n"
            "Return the response in JSON format with the following structure, and include a 'reason' field explaining why this node was generated based on the player's input and the narrative context:\n"
            "{\n"
            "  \"subtask_id\": \"<new node id>\",\n"
            "  \"parent_id\": \"<parent node id>\",\n"
            "  \"layer\": <layer number>,\n"
            "  \"title\": \"<new node title>\",\n"
            "  \"description\": \"<new node description>\",\n"
            "  \"player_options\": [\"<option1>\", \"<option2>\", \"<option3>\"],\n"
            "  \"npc_reactions\": {\"<npc_name>\": \"<npc_reaction>\"}\n"
            "  \"reason\": \"<explanation for why this node was generated>\"\n"
            "}"
        )
        evaluation = call_llm_api(prompt)
        if evaluation is None:
            print("API call failed. No new node generated.")
            return None
            # Added debug output here
        print("Evaluation received from API:", evaluation)

        new_node_data  = evaluation.get('choices', [{}])[0].get('message', {}).get('content', '{}')
        try:
            new_node = json.loads(new_node_data )
            new_node['layer'] = best_node.get('layer', 1) + 1  # Assign the next layer based on the best node
            return new_node
        except json.JSONDecodeError:
            print(f"Error decoding JSON response, raw response: new_node_data")
            # print(f"JSON Decode Error: {e}")
            return None
