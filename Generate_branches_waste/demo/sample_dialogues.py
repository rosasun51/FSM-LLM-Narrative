"""
This module provides sample dialogue templates for NPCs in the game.
These templates can be used for scripted responses or as examples for LLM generation.
"""

# Character-specific dialogue templates
BUTLER_DIALOGUES = {
    "greeting": [
        "Good evening. Welcome to Blackwood Manor.",
        "Welcome, sir/madam. We've been expecting you.",
        "Ah, our final guest has arrived. Please, do come in."
    ],
    "formal_response": [
        "Very good, sir/madam.",
        "As you wish.",
        "Certainly. I shall attend to that right away."
    ],
    "secretive": [
        "I'm afraid I'm not at liberty to discuss that matter.",
        "Lord Blackwood has instructed me not to speak of such things.",
        "Some secrets of this house are not mine to share."
    ],
    "helpful": [
        "Perhaps I can be of assistance with that.",
        "Allow me to help you with that, sir/madam.",
        "I believe I may know something that could aid you."
    ]
}

DETECTIVE_DIALOGUES = {
    "investigative": [
        "Interesting. That detail could be significant to the case.",
        "I've been noting similar inconsistencies in my investigation.",
        "Let me add that to my notes. It might connect to other evidence."
    ],
    "skeptical": [
        "I'm not entirely convinced by that explanation.",
        "That account doesn't align with the evidence I've gathered.",
        "Something doesn't quite add up there."
    ],
    "revelation": [
        "I've made a breakthrough in the case. Look at this evidence.",
        "My investigation has uncovered something you should see.",
        "This might change our understanding of what happened here."
    ],
    "professional": [
        "In my years as a detective, I've learned to trust the evidence.",
        "Let's approach this methodically and examine all the facts.",
        "We need to separate speculation from verifiable evidence."
    ]
}

LORD_BLACKWOOD_DIALOGUES = {
    "authoritative": [
        "This is my house, and I expect my rules to be followed.",
        "I've made my decision on the matter, and it is final.",
        "The Blackwood family has always maintained certain standards."
    ],
    "hospitable": [
        "Please make yourself comfortable. My home is your home.",
        "Can I offer you a drink? I have an excellent whiskey in my collection.",
        "I want all my guests to feel welcome at Blackwood Manor."
    ],
    "worried": [
        "This theft has greatly disturbed the peace of my household.",
        "I fear there may be more at stake than just the stolen item.",
        "These events trouble me deeply. The timing is... suspicious."
    ],
    "reminiscing": [
        "This house has been in my family for seven generations.",
        "In my younger days, this place was always full of guests and laughter.",
        "The history of the Blackwoods is intertwined with this estate's secrets."
    ]
}

LADY_ELEANOR_DIALOGUES = {
    "charming": [
        "How delightful to meet a new face in this dreary old house.",
        "You must tell me all about yourself. I find new acquaintances fascinating.",
        "Perhaps you and I could have a private conversation later."
    ],
    "observant": [
        "I couldn't help but notice the peculiar way the butler reacted to that news.",
        "Did you see how Lord Blackwood's expression changed when that was mentioned?",
        "The detective seems particularly interested in that part of the house."
    ],
    "mysterious": [
        "Some things in this house are best left undisturbed.",
        "I've heard whispers of the Blackwood family secrets for years.",
        "There are hidden passages in these walls that few know about."
    ],
    "concerned": [
        "I worry about dear Lord Blackwood. This affair has affected him greatly.",
        "These events remind me of another tragedy that befell this house years ago.",
        "We must be careful. I fear not everyone here has honest intentions."
    ]
}

# General dialogue templates that can be used by any character
GENERAL_DIALOGUES = {
    "surprise": [
        "Good heavens! That's most unexpected.",
        "Well, I never would have anticipated such a development.",
        "This comes as quite a shock, I must say."
    ],
    "agreement": [
        "Yes, I believe you're quite right about that.",
        "Indeed, that aligns with my understanding as well.",
        "Your assessment seems accurate from what I can tell."
    ],
    "disagreement": [
        "I'm afraid I must disagree with that assessment.",
        "That's not how I perceive the situation at all.",
        "I have a rather different view on that matter."
    ],
    "confusion": [
        "I'm not sure I follow your meaning.",
        "Could you perhaps clarify what you're suggesting?",
        "The connection escapes me, I'm afraid."
    ],
    "suspicion": [
        "Something about that explanation doesn't quite ring true.",
        "I have my doubts about the full story being told here.",
        "There seems to be more than meets the eye in this situation."
    ]
}

def get_dialogue(character_id, dialogue_type):
    """
    Get a list of possible dialogues for a character and type.
    
    Args:
        character_id: ID of the character (butler, detective, etc.)
        dialogue_type: Type of dialogue (greeting, skeptical, etc.)
        
    Returns:
        List of dialogue templates or empty list if not found
    """
    dialogue_map = {
        "butler": BUTLER_DIALOGUES,
        "detective": DETECTIVE_DIALOGUES,
        "lord_blackwood": LORD_BLACKWOOD_DIALOGUES,
        "lady_eleanor": LADY_ELEANOR_DIALOGUES
    }
    
    # Get character-specific dialogues if available
    if character_id in dialogue_map:
        character_dialogues = dialogue_map[character_id]
        if dialogue_type in character_dialogues:
            return character_dialogues[dialogue_type]
    
    # Fall back to general dialogues
    if dialogue_type in GENERAL_DIALOGUES:
        return GENERAL_DIALOGUES[dialogue_type]
    
    return [] 