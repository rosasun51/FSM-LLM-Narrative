'''
This code will:
Define major tasks as states.
Define small tasks as substates within the major task states.
Allow branch selection, where different branches (subtasks) lead to different narrative events.
Handle mission refresh, transitioning to the next major task after completing all required branches.

How to Use This Code
Each major task is represented as a TaskState object with is_major_task set to True.
Sub-states represent the smaller tasks or decision points within each major task.
Transitions between states are defined using conditions (eg. "choice_a", "complete").
The StatePool class manages the collection of states and navigation between them.
'''

class TaskState:
    def __init__(self, state_id, description, is_major_task=False):
        self.state_id = state_id
        self.description = description
        self.is_major_task = is_major_task
        self.sub_states = []
        self.transitions = {}  # {condition: next_state_id}

    def add_sub_state(self, sub_state):
        self.sub_states.append(sub_state)

    def add_transition(self, condition, next_state_id):
        self.transitions[condition] = next_state_id

    def get_next_state(self, condition):
        return self.transitions.get(condition, None)

class StatePool:
    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, state):
        self.states[state.state_id] = state

    def get_state(self, state_id):
        return self.states.get(state_id, None)

    def set_current_state(self, state_id):
        self.current_state = self.get_state(state_id)

    def get_current_state(self):
        return self.current_state

    def navigate_to_next_state(self, condition):
        if self.current_state:
            next_state_id = self.current_state.get_next_state(condition)
            if next_state_id:
                self.set_current_state(next_state_id)
                return True
        return False

# Create the state pool based on the image structure
def create_task_state_pool():
    state_pool = StatePool()

    # Major tasks (large states)
    major_task_1 = TaskState("major_1", "任务1：初始任务", is_major_task=True)
    major_task_2 = TaskState("major_2", "任务2：中期任务", is_major_task=True)
    major_task_3 = TaskState("major_3", "任务3：后期任务", is_major_task=True)
    major_task_4 = TaskState("major_4", "任务4：最终任务", is_major_task=True)

    # Sub-states for major_task_1
    sub_state_1_1 = TaskState("sub_1_1", "子任务1.1：初始决策")
    sub_state_1_2 = TaskState("sub_1_2", "子任务1.2：分支A")
    sub_state_1_3 = TaskState("sub_1_3", "子任务1.3：分支B")

    # Sub-states for major_task_2
    sub_state_2_1 = TaskState("sub_2_1", "子任务2.1：中期决策")
    sub_state_2_2 = TaskState("sub_2_2", "子任务2.2：分支C")
    sub_state_2_3 = TaskState("sub_2_3", "子任务2.3：分支D")

    # Sub-states for major_task_3
    sub_state_3_1 = TaskState("sub_3_1", "子任务3.1：后期决策")
    sub_state_3_2 = TaskState("sub_3_2", "子任务3.2：分支E")
    sub_state_3_3 = TaskState("sub_3_3", "子任务3.3：分支F")

    # Sub-states for major_task_4
    sub_state_4_1 = TaskState("sub_4_1", "子任务4.1：最终决策")
    sub_state_4_2 = TaskState("sub_4_2", "子任务4.2：最终分支")

    # Add all states to the pool
    state_pool.add_state(major_task_1)
    state_pool.add_state(major_task_2)
    state_pool.add_state(major_task_3)
    state_pool.add_state(major_task_4)
    state_pool.add_state(sub_state_1_1)
    state_pool.add_state(sub_state_1_2)
    state_pool.add_state(sub_state_1_3)
    state_pool.add_state(sub_state_2_1)
    state_pool.add_state(sub_state_2_2)
    state_pool.add_state(sub_state_2_3)
    state_pool.add_state(sub_state_3_1)
    state_pool.add_state(sub_state_3_2)
    state_pool.add_state(sub_state_3_3)
    state_pool.add_state(sub_state_4_1)
    state_pool.add_state(sub_state_4_2)

    # Define transitions for major_task_1
    major_task_1.add_transition("start", "sub_1_1")
    sub_state_1_1.add_transition("choice_a", "sub_1_2")
    sub_state_1_1.add_transition("choice_b", "sub_1_3")
    sub_state_1_2.add_transition("complete", "major_2")
    sub_state_1_3.add_transition("complete", "major_2")

    # Define transitions for major_task_2
    major_task_2.add_transition("start", "sub_2_1")
    sub_state_2_1.add_transition("choice_c", "sub_2_2")
    sub_state_2_1.add_transition("choice_d", "sub_2_3")
    sub_state_2_2.add_transition("complete", "major_3")
    sub_state_2_3.add_transition("complete", "major_3")

    # Define transitions for major_task_3
    major_task_3.add_transition("start", "sub_3_1")
    sub_state_3_1.add_transition("choice_e", "sub_3_2")
    sub_state_3_1.add_transition("choice_f", "sub_3_3")
    sub_state_3_2.add_transition("complete", "major_4")
    sub_state_3_3.add_transition("complete", "major_4")

    # Define transitions for major_task_4
    major_task_4.add_transition("start", "sub_4_1")
    sub_state_4_1.add_transition("choice_g", "sub_4_2")
    sub_state_4_2.add_transition("complete", "end")

    # Set the initial state
    state_pool.set_current_state("major_1")

    return state_pool


# Visualize the state pool
def visualize_state_pool(state_pool):
    try:
        from graphviz import Digraph
        import os
    except ImportError:
        print("Please install graphviz: pip install graphviz")
        return

    # Set the path to Graphviz executable in environment
    graphviz_path = r'E:\Graphviz-12.2.1-win64\bin'
    
    # Check if the path exists
    if not os.path.exists(graphviz_path):
        print(f"Error: Graphviz path not found at {graphviz_path}")
        return
        
    # Add to PATH if it's not already there
    if graphviz_path not in os.environ["PATH"]:
        os.environ["PATH"] = graphviz_path + os.pathsep + os.environ["PATH"]

    # Verify dot executable exists
    dot_path = os.path.join(graphviz_path, 'dot.exe')
    if not os.path.exists(dot_path):
        print(f"Error: dot.exe not found at {dot_path}")
        return

    dot = Digraph(comment='Task State Machine')
    dot.engine = 'dot'  # Use the 'dot' layout algorithm
    dot.attr(rankdir='LR')  # Left to right layout

    # Add nodes
    for state_id, state in state_pool.states.items():
        shape = 'doubleoctagon' if state.is_major_task else 'rectangle'
        dot.node(state_id, f"{state_id}\n{state.description}", shape=shape)

    # Add edges (transitions)
    for state_id, state in state_pool.states.items():
        for condition, next_state_id in state.transitions.items():
            dot.edge(state_id, next_state_id, label=condition)

    # Save the visualization
    try:
        dot.render('task_state_machine', format='png', cleanup=True)
        print("Visualization saved as 'task_state_machine.png'")
    except Exception as e:
        print(f"Error saving visualization: {e}")
        print(f"Current PATH: {os.environ['PATH']}")

# Update the example usage
if __name__ == "__main__":
    state_pool = create_task_state_pool()
    
    # Add visualization
    visualize_state_pool(state_pool)
    
    # Existing simulation code
    current_state = state_pool.get_current_state()
    print(f"Current state: {current_state.state_id} - {current_state.description}")
    
    # Move through the state transitions
    state_pool.navigate_to_next_state("start")
    state_pool.navigate_to_next_state("choice_a")
    state_pool.navigate_to_next_state("complete")
    
    current_state = state_pool.get_current_state()
    print(f"Final state: {current_state.state_id} - {current_state.description}")



visualize_state_pool(state_pool)