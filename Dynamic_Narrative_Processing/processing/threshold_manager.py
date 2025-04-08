<<<<<<< HEAD
from typing import Dict
import json
import os

class ThresholdManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'threshold_config.json'
        )
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load threshold configuration."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            'high_threshold': 80,
            'medium_threshold': 50,
            'low_threshold': 0
        }
    
    def _save_config(self):
        """Save threshold configuration."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_threshold_category(self, score: float) -> str:
        """Categorize score into high, medium, or low similarity."""
        if score >= self.config['high_threshold']:
            return 'high_similarity'
        elif score >= self.config['medium_threshold']:
            return 'medium_similarity'
        else:
            return 'low_similarity'
    
    def update_thresholds(self, high: int, medium: int):
        """Update threshold values."""
        self.config['high_threshold'] = high
        self.config['medium_threshold'] = medium
        self._save_config()
    
    def get_thresholds(self) -> Dict:
        """Get current threshold values."""
        return self.config
    
    def validate_score(self, score: float) -> bool:
        """Validate if score is within acceptable range."""
        return 0 <= score <= 100
    
    def get_action(self, score: float) -> str:
        """Get recommended action based on score."""
        if score >= self.config['high_threshold']:
            return 'select_existing'
        elif score >= self.config['medium_threshold']:
            return 'generate_new'
        else:
            return 'continue' 
||||||| 73f7c15e6
=======
from typing import Dict
import json
import os

class ThresholdManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'threshold_config.json'
        )
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load threshold configuration."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            'high_threshold': 80,
            'medium_threshold': 50,
            'low_threshold': 0
        }
    
    def _save_config(self):
        """Save threshold configuration."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_threshold_category(self, score: float) -> str:
        """Categorize score into high, medium, or low similarity."""
        if score >= self.config['high_threshold']:
            return 'high_similarity'
        elif score >= self.config['medium_threshold']:
            return 'medium_similarity'
        else:
            return 'low_similarity'
    
    def update_thresholds(self, high: int, medium: int):
        """Update threshold values."""
        self.config['high_threshold'] = high
        self.config['medium_threshold'] = medium
        self._save_config()
    
    def get_thresholds(self) -> Dict:
        """Get current threshold values."""
        return self.config
    
    def validate_score(self, score: float) -> bool:
        """Validate if score is within acceptable range."""
        return 0 <= score <= 100
    
    def get_action(self, score: float) -> str:
        """Get recommended action based on score."""
        if score >= self.config['high_threshold']:
            return 'select_existing'
        elif score >= self.config['medium_threshold']:
            return 'generate_new'
        else:
            return 'continue' 
>>>>>>> fe5206a7596bb44889a38717f23363f9e0fbf95e
