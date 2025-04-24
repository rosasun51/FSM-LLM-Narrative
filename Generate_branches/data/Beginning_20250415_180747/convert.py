# Failed

import json

def convert_txt_to_json(txt_file_path, json_file_path):
    with open(txt_file_path, 'r') as txt_file:
        lines = txt_file.readlines()
        
        # Parse the lines to extract layers and subtasks
        # This is a placeholder for your parsing logic
        data = {
            "layers": [],
            "subtasks": []
        }
        
        # Example parsing logic (you will need to adjust this based on your text file format)
        for line in lines:
            if line.startswith("Layer:"):
                layer_info = line.strip().split(":")[1].strip()
                data["layers"].append(layer_info)
            elif line.startswith("Subtask:"):
                subtask_info = line.strip().split(":")[1].strip()
                data["subtasks"].append(subtask_info)

    # Write the parsed data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Example usage
convert_txt_to_json("Beginning_20250415_180747_narrative.txt", "Beginning_20250415_scene_data.json")