<<<<<<< HEAD
"""
Test script to run the demo processor with sample inputs.
"""

import os
import sys
from demo_processor import DemoProcessor

def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Initialize the processor
    processor = DemoProcessor()
    
    # Load sample nodes
    episode = "Beginning"
    processor.load_sample_nodes(episode)
    
    # Sample inputs
    sample_inputs = [
        {"text": "I want to explore the city"},
        {"text": "Let's meet with Meredith"},
        {"text": "I need to find a way to clear the virus"}
    ]
    
    # Process each input
    for input_data in sample_inputs:
        print(f"\nProcessing input: {input_data['text']}")
        result = processor.process_input(input_data['text'])
        print(f"Result: {result}")
    
    # Show final visualization
    processor.visualize()

if __name__ == "__main__":
    main() 
||||||| 73f7c15e6
=======
"""
Test script to run the demo processor with sample inputs.
"""

import os
import sys
from demo_processor import DemoProcessor

def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Initialize the processor
    processor = DemoProcessor()
    
    # Load sample nodes
    episode = "Beginning"
    processor.load_sample_nodes(episode)
    
    # Sample inputs
    sample_inputs = [
        {"text": "I want to explore the city"},
        {"text": "Let's meet with Meredith"},
        {"text": "I need to find a way to clear the virus"}
    ]
    
    # Process each input
    for input_data in sample_inputs:
        print(f"\nProcessing input: {input_data['text']}")
        result = processor.process_input(input_data['text'])
        print(f"Result: {result}")
    
    # Show final visualization
    processor.visualize()

if __name__ == "__main__":
    main() 
>>>>>>> fe5206a7596bb44889a38717f23363f9e0fbf95e
