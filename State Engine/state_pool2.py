'''
You can ignore this file for the time being.
This is a state engine that is used to manage the state of the game.
This code will:
Define major tasks as states.
Define small tasks as substates within the major task states.
Allow branch selection, where different branches (subtasks) lead to different narrative events.
Handle mission refresh, transitioning to the next major task after completing all required branches.
'''

from transitions import Machine

class GameState:
    def __init__(self, name):
        self.name = name

# Define Major Task States (Big States)
major_tasks = ["Task_A", "Task_B", "Task_C"]  # Example big states (major tasks)

# Define Branches (Small States inside Major Task)
branches = {
    "Task_A": ["A1", "A2", "A3"],
    "Task_B": ["B1", "B2"],
    "Task_C": ["C1", "C2", "C3"]
}

# Define Transitions
transitions = []

# Adding branch transitions within each major task
for task, sub_states in branches.items():
    for i in range(len(sub_states) - 1):
        transitions.append({
            'trigger': f'complete_{sub_states[i]}',
            'source': sub_states[i],
            'dest': sub_states[i + 1]
        })
    
    # Last substate in a task moves to the "mission refresh" state
    transitions.append({
        'trigger': f'complete_{sub_states[-1]}',
        'source': sub_states[-1],
        'dest': f"refresh_{task}"
    })

# Mission Refresh: Moves from refresh state to the next major task
for i in range(len(major_tasks) - 1):
    transitions.append({
        'trigger': f'refresh_{major_tasks[i]}',
        'source': f"refresh_{major_tasks[i]}",
        'dest': major_tasks[i + 1]
    })

# Final mission complete transition
transitions.append({
    'trigger': f'refresh_{major_tasks[-1]}',
    'source': f"refresh_{major_tasks[-1]}",
    'dest': "Game_Completed"
})

# Define State Machine
states = []
for task, sub_states in branches.items():
    states.extend(sub_states)
    states.append(f"refresh_{task}")

states.extend(major_tasks)
states.append("Game_Completed")

# Initialize Game State Machine
game = GameState("Task_A")
machine = Machine(model=game, states=states, transitions=transitions, initial="A1")

# Test Run
print(f"Current State: {game.state}")
game.complete_A1()
print(f"After A1: {game.state}")
game.complete_A2()
print(f"After A2: {game.state}")
game.complete_A3()
print(f"After A3 (Mission Refresh): {game.state}")
game.refresh_Task_A()
print(f"New Major Task: {game.state}")
