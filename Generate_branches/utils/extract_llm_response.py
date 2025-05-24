import os
import json
import argparse

def extract_and_save_response(json_file_path):
    """
    Extracts the content associated with a "raw_response" key from a JSON file,
    parses it if it's a JSON string (stripping markdown fences if present),
    and saves it as a structured JSON to a new file with '_response' appended to the original filename.
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        response_data = data.get("raw_response")

        if response_data is None:
            print(f"Warning: No 'raw_response' key found in {json_file_path}, or its value is null. Skipping.")
            return

        base, ext = os.path.splitext(json_file_path)
        output_file_path = f"{base}_response{ext}"

        processed_response_for_dumping = None
        if isinstance(response_data, str):
            cleaned_string = response_data.strip()
            # Check for and remove markdown code block fences
            if cleaned_string.startswith("```json"):
                cleaned_string = cleaned_string[len("```json"):].strip()
            elif cleaned_string.startswith("```"):
                cleaned_string = cleaned_string[len("```"):].strip()
            
            if cleaned_string.endswith("```"):
                cleaned_string = cleaned_string[:-len("```")]
            
            # After potentially stripping fences, try to parse
            try:
                processed_response_for_dumping = json.loads(cleaned_string)
            except json.JSONDecodeError as e_inner_decode:
                print(f"Error: The content of 'raw_response' in {json_file_path} (after attempting to strip markdown) is a string, but it's not valid JSON. Original string snippet: '{response_data[:100]}...'. Details: {e_inner_decode}. Skipping this file.")
                return
        elif isinstance(response_data, (dict, list)):
            processed_response_for_dumping = response_data
        else:
            print(f"Warning: The content of 'raw_response' in {json_file_path} is neither a JSON string nor a direct dictionary/list. Type: {type(response_data)}. Skipping this file.")
            return

        with open(output_file_path, 'w') as outfile:
            json.dump(processed_response_for_dumping, outfile, indent=2)
        print(f"Successfully extracted, parsed, and saved structured response to {output_file_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}")
    except Exception as e:
        print(f"An unexpected error occurred with {json_file_path}: {e}")

def process_task_folder(task_folder_path):
    """
    Processes a single task folder, looking for JSON files.
    """
    print(f"Processing task folder: {task_folder_path}")
    if not os.path.isdir(task_folder_path):
        print(f"Error: {task_folder_path} is not a valid directory.")
        return

    for item in os.listdir(task_folder_path):
        item_path = os.path.join(task_folder_path, item)
        if os.path.isfile(item_path) and item.endswith('.json') and not item.endswith('_response.json'):
            extract_and_save_response(item_path)
        elif os.path.isdir(item_path):
            # Recursively process subdirectories like 'Scripted_subtask_...' or 'Subtask_branches_...'
            process_task_folder(item_path)


def main():
    parser = argparse.ArgumentParser(description="Extracts LLM responses from JSON files in specified task folders.")
    parser.add_argument("data_folder_path", type=str, help="Path to the main 'data' folder.")
    parser.add_argument("--task", type=str, help="Specify a single task folder name to process (e.g., 'Beginning_20250415_180747'). If not provided, all task folders will be processed.")

    args = parser.parse_args()

    data_path = args.data_folder_path

    if not os.path.isdir(data_path):
        print(f"Error: The provided data folder path '{data_path}' does not exist or is not a directory.")
        return

    if args.task:
        # Process a single specified task folder
        task_folder_full_path = os.path.join(data_path, args.task)
        if os.path.isdir(task_folder_full_path):
            process_task_folder(task_folder_full_path)
        else:
            print(f"Error: Task folder '{args.task}' not found in '{data_path}'.")
    else:
        # Process all task folders in the data directory
        for task_folder_name in os.listdir(data_path):
            task_folder_full_path = os.path.join(data_path, task_folder_name)
            if os.path.isdir(task_folder_full_path):
                # We are interested in folders like 'Beginning_20250415_180747'
                # and not files like 'Scripted_tasks.json' at the root of data_path
                process_task_folder(task_folder_full_path)

if __name__ == "__main__":
    main() 