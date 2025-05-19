from abc import ABC, abstractmethod

class EvaluationStrategy(ABC):
    @abstractmethod
    def evaluate(self, player_input, current_scene, available_nodes, **kwargs):
        pass

class OriginalEvaluationStrategy(EvaluationStrategy):
    def __init__(self, input_evaluator):
        self.input_evaluator = input_evaluator

    def evaluate(self, player_input, current_scene, available_nodes, **kwargs):
        return self.input_evaluator.evaluate_player_input(
            player_input,
            current_scene,
            available_nodes,
            kwargs.get('call_llm_api')
        )

class MethodIEvaluationStrategy(EvaluationStrategy):
    def __init__(self, prompt_evaluator, llm_api):
        self.prompt_evaluator = prompt_evaluator
        self.llm_api = llm_api

    def evaluate(self, player_input, current_scene, available_nodes, **kwargs):
        # Example implementation - you'll need to adapt this to your specific logic
        best_node = self.find_best_matching_node(player_input, available_nodes)
        prompt = self.prompt_evaluator.generate_branch_evaluation_prompt(
            current_task=current_scene,
            current_subtask=best_node,
            next_subtask=self.get_next_subtask(best_node),
            player_input=player_input,
            transitioning_question=best_node.get('transition_question', '')
        )
        evaluation = self.llm_api(prompt)
        # Process the evaluation result
        return self.process_llm_evaluation(evaluation, best_node)

class MethodIIEvaluationStrategy(EvaluationStrategy):
    def __init__(self, pde_classifier):
        self.classifier = pde_classifier

    def evaluate(self, player_input, current_scene, available_nodes, **kwargs):
        # Implementation using Method II's PDE classification
        pass  # You'll need to fill this in based on your specific logic

class HybridEvaluationStrategy(EvaluationStrategy):
    def __init__(self, classifier, prompt_evaluator):
        self.classifier = classifier
        self.prompt_evaluator = prompt_evaluator

    def evaluate(self, player_input, current_scene, available_nodes, **kwargs):
        # Implementation combining both methods
        pass  # You'll need to fill this in based on your specific logic