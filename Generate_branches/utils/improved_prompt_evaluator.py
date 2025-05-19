class ImprovedPromptEvaluator:
    def __init__(self):
        self.RATE_SUBTASK_PROMPT = """
Rate how well the following generated subtask fits as a response to the transitioning question
and as a continuation of the narrative from the previous subtask.

Previous subtask: {previous_subtask_title}
Previous subtask description: {previous_subtask_description}

Transitioning question: {transitioning_question}

Generated subtask to rate:
Title: {generated_subtask_title}
Description: {generated_subtask_description}
Dialogue: {generated_subtask_dialogue}

Rate this generated subtask on a scale from 0 to 100, where:
- 0-25: Poor fit, illogical or inconsistent with the narrative
- 26-50: Acceptable fit but not particularly compelling
- 51-75: Good fit with the narrative and addresses the question well
- 76-100: Excellent fit, creative, compelling, and perfectly addresses the question

Provide your rating as a JSON object with these keys:
{{"rating": [0-100], "reason": "explanation"}}
"""

        self.EVALUATE_BRANCH_PROMPT = """
Evaluate whether the player's input should trigger a dynamic branch or continue
along the scripted path.

Current task: {current_task_title}
Current subtask: {current_subtask_title}
Current subtask description: {current_subtask_description}

Next scripted subtask: {next_subtask_title}
Next subtask description: {next_subtask_description}

Transitioning question: {transitioning_question}

Player's input: "{player_input}"

Evaluate on a scale of 0-100 how well the player's input aligns with proceeding to the
next scripted subtask. A low score means the player's input doesn't align well with the
scripted path and a dynamic branch should be generated instead.

Provide your evaluation as a JSON object with these keys:
{{"alignment_score": [0-100], "should_branch": true/false, "reason": "explanation"}}
"""

    def generate_rating_prompt(self, previous_subtask, generated_subtask, transitioning_question):
        return self.RATE_SUBTASK_PROMPT.format(
            previous_subtask_title=previous_subtask.get('title', ''),
            previous_subtask_description=previous_subtask.get('description', ''),
            transitioning_question=transitioning_question,
            generated_subtask_title=generated_subtask.get('title', ''),
            generated_subtask_description=generated_subtask.get('description', ''),
            generated_subtask_dialogue=generated_subtask.get('player_options', '')
        )

    def generate_branch_evaluation_prompt(self, current_task, current_subtask, next_subtask, player_input, transitioning_question):
        return self.EVALUATE_BRANCH_PROMPT.format(
            current_task_title=current_task.get('title', ''),
            current_subtask_title=current_subtask.get('title', ''),
            current_subtask_description=current_subtask.get('description', ''),
            next_subtask_title=next_subtask.get('title', ''),
            next_subtask_description=next_subtask.get('description', ''),
            transitioning_question=transitioning_question,
            player_input=player_input
        )