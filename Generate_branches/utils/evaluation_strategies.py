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
        print("Evaluating using Method I...")
        # Your Method I evaluation code here
        return {"method": "Method I", "result": "Evaluation result from Method I"}

class MethodIIEvaluationStrategy(EvaluationStrategy):
    def __init__(self, pde_classifier):
        self.classifier = pde_classifier

    def evaluate(self, player_input, current_scene, available_nodes, **kwargs):
        # Method II evaluation logic using PDE classification
        print("Evaluating using Method II...")
        # Your Method II evaluation code here
        return {"method": "Method II", "result": "Evaluation result from Method II"}

class HybridEvaluationStrategy(EvaluationStrategy):
    def __init__(self, classifier, prompt_evaluator):
        self.classifier = classifier
        self.prompt_evaluator = prompt_evaluator

    def evaluate(self, player_input, current_scene, available_nodes, **kwargs):
        # Hybrid evaluation logic combining both methods
        print("Evaluating using Hybrid method...")
        # Your hybrid evaluation code here
        return {"method": "Hybrid", "result": "Evaluation result from Hybrid method"}