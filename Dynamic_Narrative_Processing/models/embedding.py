<<<<<<< HEAD
import numpy as np
from typing import List, Dict, Tuple
import json
import os
import logging
import sys
from openai import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import networkx as nx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self, model_name: str = "text-embedding-ada-002"):
        """
        Initialize the embedding model using OpenAI's API.
        
        Args:
            model_name: Name of the OpenAI embedding model to use
        """
        self.model_name = model_name

        
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("base_url")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self.client = OpenAI(api_key=api_key, base_url=os.getenv("base_url"))
            logger.info(f"Successfully initialized OpenAI client with model: {model_name}")
            
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI client: {str(e)}")
            logger.info("Using simple word overlap as fallback")
            self.client = None
        
        self.similarity_thresholds = {
            "high": 0.8,  # T > 80: Select existing node
            "medium": 0.5  # 50 ≤ T ≤ 80: Generate new node
        }
        
        # Cache for embeddings to avoid repeated API calls
        self.embedding_cache = {}
    
    def _simple_word_overlap(self, text1: str, text2: str) -> float:
        """
        Simple word overlap similarity as fallback when API is not available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a given text using OpenAI's API.
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array containing the embedding
        """
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        if self.client is None:
            logger.warning("Using simple word overlap as fallback")
            return self._simple_word_overlap(text, text)  # Fallback to self-comparison
        
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text,
                timeout=10  # Set a timeout for the request
            )
            embedding = np.array(response['data'][0]['embedding'])
            self.embedding_cache[text] = embedding
            return embedding
            
        except Exception as e:
            logger.warning(f"Error getting embedding from OpenAI: {str(e)}")
            return self._simple_word_overlap(text, text)  # Fallback to self-comparison
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts using embeddings.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (T) between 0 and 1
        """
        if self.client is None:
            return self._simple_word_overlap(text1, text2)
        
        try:
            embedding1 = self.get_embedding(text1)
            embedding2 = self.get_embedding(text2)
            return float(np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
        except Exception as e:
            logger.warning(f"Error calculating similarity: {str(e)}")
            return self._simple_word_overlap(text1, text2)
    
    def process_stage(self, player_input: str, existing_nodes: List[Dict]) -> Tuple[str, float]:
        """
        Process player input through the three-stage system.
        
        Args:
            player_input: Player's input text
            existing_nodes: List of existing narrative nodes
            
        Returns:
            Tuple of (action, similarity_score)
            action: "select", "generate", or "continue"
            similarity_score: The highest similarity score found
        """
        max_similarity = 0.0
        most_similar_node = None
        
        for node in existing_nodes:
            similarity = self.calculate_similarity(player_input, node["content"])
            logger.debug(f"Similarity with node {node['id']}: {similarity}")
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_node = node
        
        logger.info(f"Max similarity score: {max_similarity}")
        
        if max_similarity > self.similarity_thresholds["high"]:
            return "select", max_similarity
        elif max_similarity >= self.similarity_thresholds["medium"]:
            return "generate", max_similarity
        else:
            return "continue", max_similarity
    
    def find_most_similar_node(self, player_input: str, existing_nodes: List[Dict]) -> Dict:
        """
        Find the most similar existing node to the player input.
        
        Args:
            player_input: Player's input text
            existing_nodes: List of existing narrative nodes
            
        Returns:
            The most similar node dictionary
        """
        max_similarity = 0.0
        most_similar_node = None
        
        for node in existing_nodes:
            similarity = self.calculate_similarity(player_input, node["content"])
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_node = node
        
        return most_similar_node

    def analyze_input(self, player_input: str, available_nodes: List[Dict]) -> Dict:
        """Analyze player input against available nodes."""
        if not available_nodes:
            return {
                'similarity_score': 0,
                'most_similar_node': None,
                'all_scores': []
            }
        
        # Calculate similarities with all nodes
        similarities = []
        for node in available_nodes:
            node_text = f"{node.get('title', '')} {node.get('description', '')}"
            score = self.calculate_similarity(player_input, node_text)
            similarities.append({
                'node': node,
                'score': score
            })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'similarity_score': similarities[0]['score'] if similarities else 0,
            'most_similar_node': similarities[0]['node'] if similarities else None,
            'all_scores': similarities
        }

class DemoProcessor:
    def __init__(self):
        self.embedding_model = EmbeddingModel()  # Initialize embedding model
        self.graph = nx.DiGraph()
        self.sample_nodes = []

    def load_sample_nodes(self, episode: str):
        episode_dir = os.path.join("data", f"{episode}_20250403_110320")
        
        if not os.path.exists(episode_dir):
            logger.error(f"Episode directory {episode_dir} does not exist.")
            return
        
        # Load nodes logic here...

    def process_input(self, player_input: str):
        result = self.embedding_model.analyze_input(player_input, self.sample_nodes)
        self._update_visualization(result)
        return result

    def _update_visualization(self, result):
        # Update the graph based on the result
        pass

    def visualize(self):
        # Visualization logic here...
        pass
 
||||||| 73f7c15e6
=======
import numpy as np
from typing import List, Dict, Tuple
import json
import os
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self, model_name: str = "paraphrase-MiniLM-L3-v2"):
        """
        Initialize the embedding model for similarity analysis.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model = None
        self.model_name = model_name
        
        try:
            from sentence_transformers import SentenceTransformer
            # Get the cache directory
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Try to load the model
            self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
            logger.info(f"Successfully loaded model: {model_name}")
            
        except ImportError as e:
            logger.warning(f"Could not import sentence-transformers: {str(e)}")
            logger.info("Using simple word overlap as fallback")
        except Exception as e:
            logger.warning(f"Could not load model {model_name}: {str(e)}")
            logger.info("Using simple word overlap as fallback")
        
        self.similarity_thresholds = {
            "high": 0.8,  # T > 80: Select existing node
            "medium": 0.5  # 50 ≤ T ≤ 80: Generate new node
        }
    
    def _simple_word_overlap(self, text1: str, text2: str) -> float:
        """
        Simple word overlap similarity as fallback when model is not available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a given text.
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array containing the embedding
        """
        if self.model is None:
            # Return a simple one-hot encoding as fallback
            words = text.lower().split()
            unique_words = list(set(words))
            embedding = np.zeros(len(unique_words))
            for word in words:
                if word in unique_words:
                    embedding[unique_words.index(word)] = 1
            return embedding
        
        return self.model.encode(text, convert_to_numpy=True)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (T) between 0 and 1
        """
        if self.model is None:
            return self._simple_word_overlap(text1, text2)
        
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)
        return float(np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
    
    def process_stage(self, player_input: str, existing_nodes: List[Dict]) -> Tuple[str, float]:
        """
        Process player input through the three-stage system.
        
        Args:
            player_input: Player's input text
            existing_nodes: List of existing narrative nodes
            
        Returns:
            Tuple of (action, similarity_score)
            action: "select", "generate", or "continue"
            similarity_score: The highest similarity score found
        """
        max_similarity = 0.0
        most_similar_node = None
        
        for node in existing_nodes:
            similarity = self.calculate_similarity(player_input, node["content"])
            logger.debug(f"Similarity with node {node['id']}: {similarity}")
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_node = node
        
        logger.info(f"Max similarity score: {max_similarity}")
        
        if max_similarity > self.similarity_thresholds["high"]:
            return "select", max_similarity
        elif max_similarity >= self.similarity_thresholds["medium"]:
            return "generate", max_similarity
        else:
            return "continue", max_similarity
    
    def find_most_similar_node(self, player_input: str, existing_nodes: List[Dict]) -> Dict:
        """
        Find the most similar existing node to the player input.
        
        Args:
            player_input: Player's input text
            existing_nodes: List of existing narrative nodes
            
        Returns:
            The most similar node dictionary
        """
        max_similarity = 0.0
        most_similar_node = None
        
        for node in existing_nodes:
            similarity = self.calculate_similarity(player_input, node["content"])
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_node = node
        
        return most_similar_node

    def analyze_input(self, player_input: str, available_nodes: List[Dict]) -> Dict:
        """Analyze player input against available nodes."""
        if not available_nodes:
            return {
                'similarity_score': 0,
                'most_similar_node': None,
                'all_scores': []
            }
        
        # Calculate similarities with all nodes
        similarities = []
        for node in available_nodes:
            node_text = f"{node.get('title', '')} {node.get('description', '')}"
            score = self.calculate_similarity(player_input, node_text)
            similarities.append({
                'node': node,
                'score': score
            })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'similarity_score': similarities[0]['score'] if similarities else 0,
            'most_similar_node': similarities[0]['node'] if similarities else None,
            'all_scores': similarities
        }
 
>>>>>>> fe5206a7596bb44889a38717f23363f9e0fbf95e
