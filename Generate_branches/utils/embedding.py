import os
from sentence_transformers import SentenceTransformer
import torch

# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", token=False)

class EmbeddingEvaluator:
    def __init__(self):
        # Set the path to the local model directory relative to the current script location
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current directory of the script
        model_path = os.path.join(base_dir, '..', 'models', 'all-MiniLM-L6-v2')  # Adjust relative to the models directory

        # Print the model path for debugging
        print(f"Loading model from: {model_path}")

        # Initialize the embedding model
        self.model = SentenceTransformer(model_path)
    
    def get_similarity_score(self, text1: str, text2: str) -> float:
        # Encode the texts to get embeddings
        embedding1 = self.model.encode(text1, convert_to_tensor=True)
        embedding2 = self.model.encode(text2, convert_to_tensor=True)
        similarity = torch.nn.functional.cosine_similarity(embedding1.unsqueeze(0), embedding2.unsqueeze(0))        
        return float(similarity * 100) # Convert to percentage (0-100)
    
    def evaluate_node_similarity(self, player_input: str, node: dict) -> float:
        """Evaluate similarity between player input and a node."""
        # Compare against the description
        desc_score = self.get_similarity_score(player_input, node['description'])
        # Compare against player options
        option_scores = [self.get_similarity_score(player_input, option) for option in node['player_options']]
        # Return the highest similarity score
        return max([desc_score] + option_scores)
    
