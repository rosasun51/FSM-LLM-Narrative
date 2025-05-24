from sys_controller import BackgroundSimulator
from config import EVALUATION_METHOD

def test_evaluation_methods():
    simulator = BackgroundSimulator()

    # Test original method
    EVALUATION_METHOD = "original"
    simulator.switch_evaluation_strategy(EVALUATION_METHOD)
    simulator.evaluate_player_input("Test input for original method")

    # Test Method I
    EVALUATION_METHOD = "method_i"
    simulator.switch_evaluation_strategy(EVALUATION_METHOD)
    simulator.evaluate_player_input("Test input for Method I")

    # Test Method II
    EVALUATION_METHOD = "method_ii"
    simulator.switch_evaluation_strategy(EVALUATION_METHOD)
    simulator.evaluate_player_input("Test input for Method II")

    # Test Hybrid method
    EVALUATION_METHOD = "hybrid"
    simulator.switch_evaluation_strategy(EVALUATION_METHOD)
    simulator.evaluate_player_input("Test input for Hybrid method")

if __name__ == "__main__":
    test_evaluation_methods()