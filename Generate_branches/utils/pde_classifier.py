class PDEClassifier:
    CLASSIFICATION_PROMPT = """
Classify the following player input into one of these categories:
1. Game Action [verb][object] - Direct actions that affect the game state
2. NPC Dialogue - Conversational input directed at non-player characters
3. Narrative Query - Questions about the story or world
4. Meta Command - Commands not related to the game world

Player input: "{player_input}"

Context:
- Current scene: {current_scene}
- Current task: {current_task}
- Player's role: {player_role}
- Game objectives: {game_objectives}

Return your classification as a JSON object:
{{
  "category": "Game Action|NPC Dialogue|Narrative Query|Meta Command",
  "details": "Additional information about the classification",
  "should_progress": true|false,
  "reason": "Explanation for the classification and progression decision"
}}
"""

    def generate_classification_prompt(self, player_input, current_scene, current_task, player_role, game_objectives):
        return self.CLASSIFICATION_PROMPT.format(
            player_input=player_input,
            current_scene=current_scene,
            current_task=current_task,
            player_role=player_role,
            game_objectives=game_objectives
        )