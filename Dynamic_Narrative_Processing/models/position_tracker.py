from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class PositionTracker:
    def __init__(self, save_path: str = None):
        self.save_path = save_path or os.path.join(
            os.path.dirname(__file__), '..', 'data', 'position_history.json'
        )
        self.position_history = self._load_history()
        self.current_position = self.position_history[-1]['position'] if self.position_history else 1.0
    
    def _load_history(self) -> List[Dict]:
        """Load position history from file."""
        if os.path.exists(self.save_path):
            with open(self.save_path, 'r') as f:
                return json.load(f)
        return [{'position': 1.0, 'timestamp': self._get_timestamp(), 'reason': 'Initial position'}]
    
    def _save_history(self):
        """Save position history to file."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, 'w') as f:
            json.dump(self.position_history, f, indent=2)
    
    def get_position(self) -> float:
        """Get current position score."""
        return self.current_position
    
    def update_position(self, new_position: float, reason: str):
        """Update current position score."""
        self.current_position = new_position
        self.position_history.append({
            'position': new_position,
            'timestamp': self._get_timestamp(),
            'reason': reason
        })
        self._save_history()
    
    def get_next_position(self, current_layer: int) -> float:
        """Get next position score based on current layer."""
        if current_layer == 1:
            return 1.5
        elif current_layer == 2:
            return 2.5
        else:
            return 3.0
    
    def get_layer(self, position: Optional[float] = None) -> int:
        """Get current layer based on position score."""
        pos = position or self.current_position
        if pos < 1.5:
            return 1
        elif pos < 2.5:
            return 2
        else:
            return 3
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_history(self) -> List[Dict]:
        """Get complete position history."""
        return self.position_history
    
    def reset(self):
        """Reset tracker to initial state."""
        self.current_position = 1.0
        self.position_history = [{
            'position': 1.0,
            'timestamp': self._get_timestamp(),
            'reason': 'Reset to initial position'
        }]
        self._save_history() 