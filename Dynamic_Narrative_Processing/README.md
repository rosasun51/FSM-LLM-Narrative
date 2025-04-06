# Dynamic Narrative Processing System

This is the second part of the FSM-LLM-Narrative system that implements dynamic narrative progression based on player input. It processes player responses and dynamically selects or generates narrative nodes based on similarity analysis and layer transitions.

## Overview

The Dynamic Narrative Processing system implements:

1. **Three-Stage Input Processing Pipeline**:
   - Player input analysis using embedding models for similarity scoring (T)
   - Three-stage processing based on similarity thresholds:
     - T > 80: Select existing node, update middle layer
     - 50 ≤ T ≤ 80: Generate new node, update middle layer
     - T < 50: Continue current NPC interaction

2. **Dynamic Node Generation and Selection**:
   - Processes each player response from JSON input files
   - Uses embedding models to calculate similarity scores (T) with existing nodes
   - Generates new nodes based on:
     - Player input
     - Current state
     - Layer transition key questions
   - Position score (S) determines node placement between current and next layer
   - One-directional progression enforced (prior nodes become unselectable)

3. **Layer Transition Management**:
   - Uses key questions from JSON files for each layer transition
   - Maintains narrative coherence through position tracking
   - Enforces one-directional progression through the narrative

## Directory Structure

```
Dynamic_Narrative_Processing/
├── data/
│   ├── key_questions/         # Layer transition questions (Q1, Q2, etc.)
│   ├── player_inputs/         # Processed player responses
│   └── generated_nodes/       # Dynamically generated nodes
├── models/
│   ├── embedding.py           # Similarity analysis and T score calculation
│   ├── node_generator.py      # Dynamic node generation with GPT
│   └── position_tracker.py    # S score management and layer tracking
├── processing/
│   ├── input_analyzer.py      # Three-stage input processing pipeline
│   ├── threshold_manager.py   # T score threshold management
│   └── layer_transition.py    # Layer progression and key question handling
├── utils/
│   ├── scoring.py            # Score calculation utilities
│   └── validation.py         # Input validation
├── demo/
│   ├── demo_processor.py     # Demo visualization of processing
│   └── input_simulator.py    # Simulated player input generator
└── tests/
    ├── test_embedding.py     # Embedding model tests
    ├── test_generation.py    # Node generation tests
    └── test_processing.py    # Processing pipeline tests
```

## Integration with Generate_branches

The system works in parallel with Generate_branches:
1. Generate_branches creates the initial narrative structure and task nodes
2. Dynamic_Narrative_Processing processes player input and:
   - Selects existing nodes based on similarity (T > 80)
   - Generates new nodes when needed (50 ≤ T ≤ 80)
   - Continues current interaction (T < 50)
3. Both systems share common data structures and interfaces

## Key Features

### Similarity Analysis (T Score)
- Uses embedding models to calculate similarity scores between player input and existing nodes
- Implements three-stage processing based on T score thresholds
- Supports multiple embedding models and similarity metrics

### Position Tracking (S Score)
- Tracks narrative progression through position scores
- Determines node placement between layers
- Enforces one-directional progression

### Dynamic Node Generation
- Generates new nodes based on player input and context
- Uses layer-specific key questions for coherence
- Maintains narrative structure while allowing dynamic expansion

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv Dynamic_Narrative_Processing_env
source Dynamic_Narrative_Processing_env/bin/activate  # On Unix
Dynamic_Narrative_Processing_env\Scripts\activate     # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```


## Usage

### Processing Player Input
```python
from processing.input_analyzer import InputAnalyzer
from models.embedding import EmbeddingModel

analyzer = InputAnalyzer()
result = analyzer.process_input(player_input)
```

### Generating New Nodes
```python
from models.node_generator import NodeGenerator
from models.position_tracker import PositionTracker

generator = NodeGenerator()
tracker = PositionTracker()
new_node = generator.generate_node(player_input, current_state, tracker.get_position())
```

### Running the Demo
```bash
cd Dynamic_Narrative_Processing
python demo/run_demo.py 
```

## Testing

Run all tests:
```bash
python -m pytest tests/
```

Run specific test suite:
```bash
python -m pytest tests/test_embedding.py
python -m pytest tests/test_generation.py
python -m pytest tests/test_processing.py
```

## License

[MIT License](LICENSE)

## Contact

For questions or suggestions, please open an issue on GitHub.

---

Happy storytelling!
