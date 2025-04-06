# Player Input Processing and Dynamic Node Generation

## Key Features

This is the second part of the FSM-LLM-Narrative system. It implements dynamic narrative progression based on player input:

1. **Input Processing Pipeline**:
   - Player input is analyzed using embedding models for similarity scoring (T)
   - Three-stage processing based on similarity thresholds:
     - T > 80: Select existing node, update middle layer
     - 50 ≤ T ≤ 80: Generate new node, update middle layer
     - T < 50: Continue current NPC interaction

2. **Node Generation System**:
   - New nodes are generated based on:
     - Player input
     - Current state
     - Layer transition key questions
   - Position score (S) determines node placement between current and next layer
   - One-directional progression enforced (prior nodes become unselectable)

3. **Key Components**:
   - Embedding models for similarity analysis
   - Layer-specific key questions for transitions
   - Position tracking system (S score)
   - Dynamic node generation with LLM

### Directory Structure for Part 2

```
Dynamic_narrative_processing/
├── data/
│   ├── key_questions/         # Layer transition questions
│   ├── player_inputs/         # Processed player inputs
│   └── generated_nodes/       # Dynamically generated nodes
├── models/
│   ├── embedding.py           # Similarity analysis
│   ├── node_generator.py      # Dynamic node generation
│   └── position_tracker.py    # S score management
├── processing/
│   ├── input_analyzer.py      # Input processing pipeline
│   ├── threshold_manager.py   # T score management
│   └── layer_transition.py    # Layer progression logic
└── utils/
    ├── scoring.py            # Score calculation utilities
    └── validation.py         # Input validation
```

## Development Guidelines

When extending the project:

1. Maintain the hierarchical structure for subtasks
2. Document new features in the README.md

## License

[MIT License](LICENSE)

## Contact

For questions or suggestions, please open an issue on GitHub.

---

Happy storytelling!
