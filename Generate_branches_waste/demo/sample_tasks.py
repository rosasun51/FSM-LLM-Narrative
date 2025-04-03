"""
This module provides sample task templates that can be used to create game scenarios.
"""

from Generate_branches.models.task import Task
from Generate_branches.models.subtask import ScriptedSubTask
from Generate_branches.models.layer import Layer

# Sample locations
LOCATIONS = {
    "mansion_entrance": {
        "name": "Mansion Entrance",
        "description": "The grand entrance to the old mansion with its imposing doors."
    },
    "foyer": {
        "name": "Mansion Foyer",
        "description": "The elegant foyer with a marble floor and sweeping staircase."
    },
    "drawing_room": {
        "name": "Drawing Room",
        "description": "A cozy drawing room with antique furniture and a crackling fireplace."
    },
    "library": {
        "name": "Library",
        "description": "Walls lined with books, a large desk in the center, and a subtle smell of old paper."
    },
    "dining_room": {
        "name": "Dining Room",
        "description": "A grand dining room with a long table and ornate chandelier."
    }
}

def create_arrival_task():
    """
    Create a task for the player's arrival at the mansion.
    
    Returns:
        Task object for the arrival scene
    """
    # Create the task
    task = Task(
        task_id="arrival",
        title="Stormy Arrival",
        description="Arriving at the mansion during a thunderstorm",
        location_id="mansion_entrance",
        timestamp=0  # Start of the game
    )
    
    # Create a layer for the main path
    main_layer = Layer(
        layer_id=0,
        name="Main Path",
        description="The primary narrative path",
        priority=100
    )
    
    # Create subtasks
    intro_subtask = ScriptedSubTask(
        subtask_id="arrival_intro",
        title="Approaching the Mansion",
        description="Player approaches the mansion in the storm",
        dialogue="Rain pours down as you approach the imposing mansion. Lightning illuminates the gothic architecture momentarily. The gravel driveway crunches beneath your feet as you hurry toward the shelter of the grand entrance.",
        npc_reactions={},
        player_options=[
            "Knock on the door",
            "Look for another entrance",
            "Examine the facade of the mansion"
        ],
        layer=0,
        next_transitioning_question="How does the player approach the entrance?"
    )
    
    knocking_subtask = ScriptedSubTask(
        subtask_id="door_knocking",
        title="Knocking at the Door",
        description="Player knocks and is greeted by the butler",
        dialogue="You knock firmly on the heavy wooden door. After a moment, it creaks open to reveal an elderly butler in formal attire. 'Good evening,' he says with a slight bow. 'We've been expecting you. Please, do come in out of this dreadful weather.'",
        npc_reactions={
            "butler": "opens the door and greets you formally"
        },
        player_options=[
            "Enter and greet the butler",
            "Ask why you were expected",
            "Hesitate at the threshold"
        ],
        layer=0,
        next_transitioning_question="How does the player respond to the butler's greeting?"
    )
    
    entry_subtask = ScriptedSubTask(
        subtask_id="mansion_entry",
        title="Entering the Mansion",
        description="Player enters the mansion foyer",
        dialogue="The grand foyer opens before you, illuminated by flickering candles and a massive chandelier. The butler closes the door behind you, shutting out the storm. 'Allow me to take your coat,' he offers. 'The others are gathered in the drawing room. There has been... an incident that requires attention.'",
        npc_reactions={
            "butler": "speaks in a hushed, formal tone"
        },
        player_options=[
            "Ask about the 'incident'",
            "Ask who else is here",
            "Follow the butler to the drawing room"
        ],
        layer=0,
        next_transitioning_question="What does the player want to know about the situation?"
    )
    
    # Add subtasks to the layer
    main_layer.add_subtask(intro_subtask)
    main_layer.add_subtask(knocking_subtask)
    main_layer.add_subtask(entry_subtask)
    
    # Add the subtasks to the task
    task.add_subtask(intro_subtask)
    task.add_subtask(knocking_subtask)
    task.add_subtask(entry_subtask)
    
    return task

def create_drawing_room_task():
    """
    Create a task for the player's entry to the drawing room.
    
    Returns:
        Task object for the drawing room scene
    """
    # Create the task
    task = Task(
        task_id="drawing_room_entry",
        title="Meeting the Guests",
        description="Meeting the assembled guests in the drawing room",
        location_id="drawing_room",
        timestamp=1  # Right after arrival
    )
    
    # Create a layer for the main path
    main_layer = Layer(
        layer_id=0,
        name="Main Path",
        description="The primary narrative path",
        priority=100
    )
    
    # Create subtasks
    entry_subtask = ScriptedSubTask(
        subtask_id="drawing_room_entry",
        title="Entering the Drawing Room",
        description="Player enters the drawing room and meets the guests",
        dialogue="The butler leads you to the drawing room and opens the door. Inside, several people turn to look at you. An older gentleman in a smoking jacket stands by the fireplace. A woman in an elegant dress sits on the sofa, while Detective Morgan stands near the window, notebook in hand.",
        npc_reactions={
            "detective": "looks up from his notebook and nods in your direction"
        },
        player_options=[
            "Introduce yourself to everyone",
            "Ask why you've been called here",
            "Wait for someone to speak first"
        ],
        layer=0,
        next_transitioning_question="How does the player handle the initial meeting?"
    )
    
    introduction_subtask = ScriptedSubTask(
        subtask_id="introductions",
        title="Formal Introductions",
        description="The host introduces everyone in the room",
        dialogue="'Ah, you must be our final guest,' says the older gentleman. 'I am Lord Blackwood, the owner of this estate. Allow me to introduce everyone. This is Lady Eleanor,' he gestures to the woman, 'my dear friend Detective Morgan whom you may know, and of course, James, my faithful butler.' Lord Blackwood's expression darkens. 'I'm afraid we've gathered under unfortunate circumstances. There has been a theft of great importance.'",
        npc_reactions={
            "butler": "bows slightly at the mention of his name",
            "detective": "closes his notebook and steps forward"
        },
        player_options=[
            "Ask about the theft",
            "Ask why you were invited",
            "Offer to help with the investigation"
        ],
        layer=0,
        next_transitioning_question="How does the player respond to the news of the theft?"
    )
    
    # Add subtasks to the layer
    main_layer.add_subtask(entry_subtask)
    main_layer.add_subtask(introduction_subtask)
    
    # Add the subtasks to the task
    task.add_subtask(entry_subtask)
    task.add_subtask(introduction_subtask)
    
    return task

def get_sample_tasks():
    """
    Get a dictionary of all sample tasks.
    
    Returns:
        Dict mapping task_id to Task objects
    """
    return {
        "arrival": create_arrival_task(),
        "drawing_room_entry": create_drawing_room_task()
    } 