"""
Narrative Management Interface

This module defines the core interfaces for the narrative management system.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel


class StoryNode(BaseModel):
    """Represents a single node in the story graph."""
    node_id: str
    content: str
    choices: List[str]
    consequences: Dict[str, str]
    metadata: Dict[str, any]


class NarrativeState(BaseModel):
    """Represents the current state of the narrative."""
    current_node: str
    story_variables: Dict[str, any]
    history: List[str]
    active_quests: List[str]


class NarrativeManager(ABC):
    """Abstract base class for narrative management."""
    
    @abstractmethod
    async def initialize_story(self) -> NarrativeState:
        """Initialize a new story state."""
        pass
    
    @abstractmethod
    async def get_current_node(self, state: NarrativeState) -> StoryNode:
        """Get the current story node."""
        pass
    
    @abstractmethod
    async def make_choice(self, state: NarrativeState, choice: str) -> NarrativeState:
        """Process a player's choice and update the narrative state."""
        pass
    
    @abstractmethod
    async def generate_context(self, state: NarrativeState) -> Dict[str, any]:
        """Generate context for NPCs and other systems."""
        pass 