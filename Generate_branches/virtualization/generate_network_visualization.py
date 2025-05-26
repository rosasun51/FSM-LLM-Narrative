import os
import json
from pyvis.network import Network
import re
from collections import defaultdict 

# Define paths
GENERATE_DATA_DIR = "Generate_branches/data"
MIDDLE_DATA_DIR = "Middle_data"
SCRIPTED_TASKS_FILE = os.path.join(GENERATE_DATA_DIR, "Scripted_tasks.json") 
OUTPUT_HTML_FILE = "task_visualization.html"

# --- Helper function to create HTML tooltips ---
def create_html_tooltip(data, title_prefix=""):
    """Creates an HTML string for node tooltips."""
    if isinstance(data, str): # For simple string content like key questions
        escaped_content = data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "<br>")
        return f"<strong>{title_prefix.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</strong><br>{escaped_content}"

    html_parts = []
    if title_prefix:
        html_parts.append(f"<strong>{title_prefix.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</strong><br><br>")

    if isinstance(data, dict):
        for key, value in data.items():
            key_html = str(key).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if isinstance(value, (dict, list)):
                # Pretty print JSON for complex types, then escape
                value_str = json.dumps(value, indent=2, ensure_ascii=False)
                value_html = value_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "<br>")
                html_parts.append(f"<strong>{key_html}:</strong><br><pre>{value_html}</pre><br>")
            else:
                value_html = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "<br>")
                html_parts.append(f"<strong>{key_html}:</strong> {value_html}<br>")
    elif isinstance(data, list):
        # Pretty print JSON for lists, then escape
        value_str = json.dumps(data, indent=2, ensure_ascii=False)
        value_html = value_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "<br>")
        html_parts.append(f"<pre>{value_html}</pre>")
    else: # Fallback for other data types
        html_parts.append(str(data).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    
    return "".join(html_parts)

# --- New function to load scripted tasks ---
def load_scripted_tasks(file_path):
    """Loads the main task definitions from Scripted_tasks.json."""
    if not os.path.exists(file_path):
        print(f"Error: Scripted tasks file '{file_path}' not found.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tasks_raw = json.load(f)
        
        valid_tasks = []
        if not isinstance(tasks_raw, list):
            print(f"Warning: Content of {file_path} is not a list. Skipping task loading.")
            return []
            
        for i, task_data in enumerate(tasks_raw):
            if not isinstance(task_data, dict):
                print(f"Warning: Item at index {i} in {file_path} is not a dictionary. Skipping this item.")
                continue

            task_name = task_data.get("name") or task_data.get("scene_name") # Try 'name', then 'scene_name'
            
            if task_name and isinstance(task_name, str):
                # If 'scene_name' was used, we might want to add it as 'name' for consistency downstream
                if "name" not in task_data and "scene_name" in task_data:
                    task_data["name"] = task_name 
                valid_tasks.append(task_data)
            else:
                print(f"Warning: Skipping task at index {i} in {file_path} due to missing or invalid 'name' or 'scene_name'. Task data snippet: {str(task_data)[:100]}")
        return valid_tasks
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading '{file_path}': {e}")
        return []

# --- New data loading logic for scripted subtasks and branches ---
def load_all_layer_data(generate_dir, task_names_from_scripted_json):
    all_tasks_data = defaultdict(lambda: defaultdict(lambda: {"scripted_subtasks": [], "subtask_branches": []}))
    
    if not os.path.exists(generate_dir):
        print(f"Error: Generate data directory '{generate_dir}' not found. Cannot load layer data.")
        return all_tasks_data
   
    response_file_pattern = re.compile(r"^(scripted_subtask|subtask_branches)_layer(\d+)_(.+?)_response\.json$")

    # Map canonical task names (from Scripted_tasks.json) to their folder names in generate_dir
    task_name_to_folder_name_map = {}

    # Helper to normalize names for comparison (lowercase, remove spaces and underscores)
    def normalize_task_name_for_matching(name_str):
        if not isinstance(name_str, str):
            return ""
        return name_str.lower().replace(" ", "").replace("_", "")

    # Create a map of normalized canonical names to original canonical names
    normalized_to_canonical_map = {
        normalize_task_name_for_matching(name): name for name in task_names_from_scripted_json
    }
    
    # Regex to extract base name (part before a _YYYYMMDD_HHMMSS timestamp like pattern)
    base_name_regex = re.compile(r"(.+?)_(\d{8})_(\d{6})$")

    try:
        potential_task_folders = [d for d in os.listdir(generate_dir) if os.path.isdir(os.path.join(generate_dir, d))]
        
        for folder_name_in_fs in potential_task_folders:
            base_name_from_folder_fs = folder_name_in_fs # Default to full name
            match = base_name_regex.match(folder_name_in_fs)
            if match:
                base_name_from_folder_fs = match.group(1) # Extracted base name, e.g., "Meet_with_Meredith_Stout"
            
            normalized_base_from_folder = normalize_task_name_for_matching(base_name_from_folder_fs)

            if normalized_base_from_folder in normalized_to_canonical_map:
                original_canonical_name = normalized_to_canonical_map[normalized_base_from_folder]
                if original_canonical_name not in task_name_to_folder_name_map:
                    task_name_to_folder_name_map[original_canonical_name] = folder_name_in_fs
                else:
                    print(f"Warning: Duplicate canonical task name '{original_canonical_name}' found in '{generate_dir}'. Using first occurrence.")

        # --- DIAGNOSTIC PRINT 1 --- 
        print(f"DIAGNOSTIC: task_name_to_folder_name_map = {json.dumps(task_name_to_folder_name_map, indent=2)}")

        # After attempting to map all folders, check which canonical tasks didn't get a mapping
        # and issue warnings for them.
        for canonical_name_iter in task_names_from_scripted_json:
            if canonical_name_iter not in task_name_to_folder_name_map:
                 print(f"Warning: No data folder successfully mapped in '{generate_dir}' for task '{canonical_name_iter}'. Subtask data for this task will be missing.")

    except OSError as e:
        print(f"Error accessing generate_dir '{generate_dir}': {e}")
        return all_tasks_data

    for canonical_task_name, task_run_folder_name in task_name_to_folder_name_map.items():
        task_run_root_path = os.path.join(generate_dir, task_run_folder_name)
        # --- DIAGNOSTIC PRINT 2 (part a) --- 
        print(f"DIAGNOSTIC: Processing task folder: '{task_run_root_path}' for canonical task: '{canonical_task_name}'")

        # Expected subfolder prefixes
        # These correspond to the type of data they hold and part of the filename pattern
        data_type_subfolders = {
            "Scripted_subtask": "scripted_subtasks",  # Folder prefix: key for all_tasks_data
            "Subtask_branches": "subtask_branches"    # Folder prefix: key for all_tasks_data
        }

        try:
            # List immediate subdirectories within the task_run_root_path
            # e.g., ['Scripted_subtask_20250415_180747', 'Subtask_branches_20250415_180747', ...]
            potential_typed_subfolders = [d for d in os.listdir(task_run_root_path) if os.path.isdir(os.path.join(task_run_root_path, d))]
        except OSError as e:
            print(f"Warning: Could not list directories in '{task_run_root_path}'. Error: {e}. Skipping layer data for this task.")
            continue

        for typed_subfolder_name in potential_typed_subfolders:
            current_data_category = None # This will be "scripted_subtasks" or "subtask_branches"
            expected_file_prefix_in_regex = "" # This will be "scripted_subtask" or "subtask_branches"

            if typed_subfolder_name.startswith("Scripted_subtask"):
                current_data_category = data_type_subfolders["Scripted_subtask"]
                expected_file_prefix_in_regex = "scripted_subtask"
            elif typed_subfolder_name.startswith("Subtask_branches"):
                current_data_category = data_type_subfolders["Subtask_branches"]
                expected_file_prefix_in_regex = "subtask_branches"
            else:
                # This subdirectory is not one of the types we're looking for (e.g., could be task_chain or other files/dirs)
                continue 

            specific_type_dir_path = os.path.join(task_run_root_path, typed_subfolder_name)
            # --- DIAGNOSTIC PRINT 2 (part b) --- (Adjusted context)
            print(f"DIAGNOSTIC: Identified typed subfolder: '{specific_type_dir_path}' for category: '{current_data_category}'")

            try:
                filenames_in_typed_dir = [f for f in os.listdir(specific_type_dir_path) if os.path.isfile(os.path.join(specific_type_dir_path, f))]
            except OSError as e:
                print(f"Warning: Could not list files in '{specific_type_dir_path}'. Error: {e}. Skipping this subfolder.")
                continue

            for file_name in filenames_in_typed_dir:
                # --- DIAGNOSTIC PRINT 3 (part a) --- 
                print(f"DIAGNOSTIC: Checking file: '{file_name}' in dirpath: '{specific_type_dir_path}'")
                match = response_file_pattern.match(file_name)
                
                if match:
                    # --- DIAGNOSTIC PRINT 3 (part b) --- 
                    print(f"DIAGNOSTIC: YES - Pattern matched for '{file_name}'. Regex Type: {match.group(1)}, Layer: {match.group(2)}, Suffix: {match.group(3)}")
                    
                    # Validate that the file's prefix matches the folder type we are in
                    if match.group(1) != expected_file_prefix_in_regex:
                        print(f"Warning: File prefix '{match.group(1)}' from regex in '{file_name}' does not match expected folder type prefix '{expected_file_prefix_in_regex}'. Skipping file.")
                        continue
                else:
                    # --- DIAGNOSTIC PRINT 3 (part b) --- 
                    print(f"DIAGNOSTIC: NO - Pattern did NOT match for '{file_name}'.")
                    continue # Skip if not a response file or pattern mismatch (e.g. the .json file not ending with _response.json)
                
                # file_type_indicator = match.group(1) # "scripted_subtask" or "subtask_branches" (from regex)
                try:
                    layer_num = int(match.group(2))
                except ValueError:
                    print(f"Warning: Could not parse layer number from filename '{file_name}' in '{specific_type_dir_path}'. Skipping.")
                    continue

                content_json_full_path = os.path.join(specific_type_dir_path, file_name)

                # --- DIAGNOSTIC PRINT 4 --- 
                print(f"DIAGNOSTIC: Attempting to load content from (response file itself): '{content_json_full_path}'")

                loaded_content = None
                if not os.path.exists(content_json_full_path): # Should always exist if listed by os.listdir
                    print(f"Warning: Content file '{content_json_full_path}' (previously listed) now not found. Skipping.")
                    continue 
                
                try:
                    with open(content_json_full_path, 'r', encoding='utf-8') as f_content:
                        loaded_content = json.load(f_content)
                except json.JSONDecodeError as e:
                    print(f"Warning: Error decoding JSON from '{content_json_full_path}'. Error: {str(e)[:100]}. Skipping this content.")
                    continue
                except Exception as e:
                    print(f"Warning: Could not read/process content file '{content_json_full_path}'. Error: {e}. Skipping this content.")
                    continue

                if loaded_content is None:
                    continue

                # Add loaded content to the correct part of all_tasks_data
                # current_data_category is "scripted_subtasks" or "subtask_branches"
                if current_data_category == "scripted_subtasks":
                    if isinstance(loaded_content, list):
                        all_tasks_data[canonical_task_name][layer_num]["scripted_subtasks"].extend(loaded_content)
                    elif isinstance(loaded_content, dict): 
                        all_tasks_data[canonical_task_name][layer_num]["scripted_subtasks"].append(loaded_content)
                    else:
                        print(f"Warning: Unexpected data type for scripted_subtask in {content_json_full_path}. Expected list or dict, got {type(loaded_content)}.")
                
                elif current_data_category == "subtask_branches":
                    branches_to_add = []
                    if isinstance(loaded_content, list):
                        branches_to_add = loaded_content
                    elif isinstance(loaded_content, dict) and "subtask_branches" in loaded_content and isinstance(loaded_content["subtask_branches"], list):
                        branches_to_add = loaded_content["subtask_branches"]
                    elif isinstance(loaded_content, dict) and "subtask_id" in loaded_content: 
                         branches_to_add = [loaded_content]
                    else:
                        print(f"Warning: Unexpected data type or structure for subtask_branches in {content_json_full_path}. Data: {str(loaded_content)[:100]}...")

                    processed_branches = []
                    seen_branch_ids_for_layer = set() # Uniqueness check per layer, per file
                    for branch in branches_to_add:
                        if not isinstance(branch, dict) or "subtask_id" not in branch:
                            print(f"Warning: Skipping malformed branch in {content_json_full_path}: {str(branch)[:100]}")
                            continue
                        
                        branch_id_for_uniqueness = branch["subtask_id"] 
                        if branch_id_for_uniqueness not in seen_branch_ids_for_layer:
                            processed_branches.append(branch)
                            seen_branch_ids_for_layer.add(branch_id_for_uniqueness)
                    
                    all_tasks_data[canonical_task_name][layer_num]["subtask_branches"].extend(processed_branches)

    return all_tasks_data

# --- New network population logic ---
def populate_network_new(net, scripted_tasks, all_layer_data):
    nodes_added = set() # To prevent adding the same node ID twice globally
    pyvis_level_counter = 0 # Increment for each major element (Task, KQ, LayerHub, End) for vertical spacing

    # Sort scripted_tasks by their original order in the JSON if that's desired,
    # or by name if consistency across runs is more important than input order.
    # Assuming original order is fine.

    for task_index, task in enumerate(scripted_tasks):
        task_name = task.get("name")
        if not task_name:
            print(f"Warning: Skipping task at index {task_index} due to missing 'name'.")
            continue

        # --- 1. Task Node ---
        task_node_id = f"TASK_{task_name.replace(' ', '_').upper()}" # Ensure unique and clean ID
        if task_node_id in nodes_added: # Should ideally not happen if task names are unique
             task_node_id += f"_idx{task_index}" # Make unique if names clash
        
        task_tooltip = create_html_tooltip(task, title_prefix=f"Task: {task_name}")
        net.add_node(task_node_id, label=task_name, title=task_tooltip, level=pyvis_level_counter,
                     shape="box", color="#4CAF50", size=20, 
                     font={"size": 14, "face": "Verdana", "bold": True})
        nodes_added.add(task_node_id)
        
        last_connected_node_in_main_chain = task_node_id
        pyvis_level_counter += 1

        key_questions = task.get("key_questions")
        if key_questions is None: # Handles 'null' from JSON
            key_questions = [] 
        elif not isinstance(key_questions, list):
            print(f"Warning: 'key_questions' for task '{task_name}' is not a list. Found: {type(key_questions)}. Treating as empty.")
            key_questions = []

        # Sort key questions by 'id' field if possible, assuming 'id' is numeric or string convertible to int
        try:
            # Ensure 'id' exists and is not None before trying to convert to int
            key_questions_sorted = sorted(
                [kq for kq in key_questions if kq and kq.get('id') is not None], 
                key=lambda kq: int(kq['id'])
            )
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not sort key questions by ID for task '{task_name}' due to non-integer or missing IDs. Using original order. Error: {e}")
            key_questions_sorted = key_questions # Use original order if sorting fails

        task_specific_layer_data = all_layer_data.get(task_name, defaultdict(lambda: {"scripted_subtasks": [], "subtask_branches": []}))

        for kq_index, kq_item in enumerate(key_questions_sorted):
            kq_id = kq_item.get("id", f"autoID_{kq_index}")
            kq_content = kq_item.get("content", "N/A")

            # --- 2. Key Question Node ---
            kq_node_id = f"KQ_{task_name.replace(' ', '_').upper()}_KQID_{str(kq_id).replace(' ', '_')}"
            if kq_node_id in nodes_added: kq_node_id += f"_idx{kq_index}"

            kq_label = f"KQ {kq_id}: {str(kq_content)[:35]}{'...' if len(str(kq_content)) > 35 else ''}"
            # kq_tooltip_text = f"Task: {task_name}\\nKey Question ID: {kq_id}\\n\\n{kq_content}" # Old way, create_html_tooltip is better
            kq_tooltip = create_html_tooltip(kq_item, title_prefix=f"Key Question {kq_id} (for Task: {task_name})")

            net.add_node(kq_node_id, label=kq_label, title=kq_tooltip, level=pyvis_level_counter,
                         shape="box", color="#A7C7E7", font={"size": 11}) # Periwinkle blue
            nodes_added.add(kq_node_id)
            net.add_edge(last_connected_node_in_main_chain, kq_node_id, color="#AAAAAA", width=2)
            last_connected_node_in_main_chain = kq_node_id
            pyvis_level_counter += 1
            
            # --- 3. Layer Hub Node (associated with this KQ) ---
            data_layer_num = kq_index + 1 # Layer 1 for first KQ, Layer 2 for second, etc.

            layer_hub_node_id = f"LAYERHUB_{task_name.replace(' ', '_').upper()}_L{data_layer_num}"
            if layer_hub_node_id in nodes_added: layer_hub_node_id += f"_idx{kq_index}"

            net.add_node(layer_hub_node_id, label=f"{task_name} - Layer {data_layer_num}", 
                         level=pyvis_level_counter, shape="diamond", color="#FFD700", size=25,
                         font={"size": 16, "face": "Verdana", "bold": True},
                         title=f"Hub for Layer {data_layer_num} items of Task: {task_name}")
            nodes_added.add(layer_hub_node_id)
            net.add_edge(last_connected_node_in_main_chain, layer_hub_node_id, color="#888888", width=2.5)
            last_connected_node_in_main_chain = layer_hub_node_id
            
            child_pyvis_level = pyvis_level_counter + 0.5

            layer_items = task_specific_layer_data.get(data_layer_num, {"scripted_subtasks": [], "subtask_branches": []})

            # Scripted Subtasks for this layer
            for s_idx, scripted_item in enumerate(layer_items.get("scripted_subtasks", [])):
                s_id_val = scripted_item.get("subtask_id", scripted_item.get("id", f"autoS_{s_idx}"))
                s_node_id = f"SCRIPTED_{task_name.replace(' ', '_').upper()}_L{data_layer_num}_ID_{str(s_id_val).replace(' ', '_')}"
                if s_node_id in nodes_added: s_node_id += f"_sidx{s_idx}"
                
                s_label = str(scripted_item.get('title', s_id_val))[:40]
                if len(str(scripted_item.get('title', s_id_val))) > 40: s_label += "..."
                s_tooltip = create_html_tooltip(scripted_item, title_prefix=f"Scripted: {scripted_item.get('title', s_id_val)} (Layer {data_layer_num})")
                
                net.add_node(s_node_id, label=s_label, title=s_tooltip, level=child_pyvis_level,
                             shape="box", color="#ADD8E6", font={"size": 10}) # Light Blue
                nodes_added.add(s_node_id)
                net.add_edge(layer_hub_node_id, s_node_id, color="#C0C0C0", width=1, length=100)

            # Subtask Branches for this layer
            for b_idx, branch_item in enumerate(layer_items.get("subtask_branches", [])):
                b_id_val = branch_item.get("subtask_id", f"autoB_{b_idx}")
                b_node_id = f"BRANCH_{task_name.replace(' ', '_').upper()}_L{data_layer_num}_ID_{str(b_id_val).replace('.', '_').replace(' ', '_')}"
                if b_node_id in nodes_added: b_node_id += f"_bidx{b_idx}"

                b_label = str(branch_item.get('title', b_id_val))[:40]
                if len(str(branch_item.get('title', b_id_val))) > 40: b_label += "..."
                b_tooltip = create_html_tooltip(branch_item, title_prefix=f"Branch: {branch_item.get('title', b_id_val)} (Layer {data_layer_num})")

                net.add_node(b_node_id, label=b_label, title=b_tooltip, level=child_pyvis_level,
                             shape="dot", color="#90EE90", size=12, font={"size": 10}) # Light Green
                nodes_added.add(b_node_id)
                net.add_edge(layer_hub_node_id, b_node_id, color="#D0D0D0", width=1, length=120)

            pyvis_level_counter += 1

        # --- 4. Scene End State Node ---
        end_state_ref = task.get("scene_end_state_reference", "No end state defined.")
        end_node_id = f"END_{task_name.replace(' ', '_').upper()}"
        if end_node_id in nodes_added: end_node_id += f"_idx{task_index}"

        end_tooltip = create_html_tooltip(end_state_ref, title_prefix=f"End State: {task_name}")
        net.add_node(end_node_id, label=f"{task_name} - End", title=end_tooltip,
                     level=pyvis_level_counter,
                     shape="ellipse", color="#E91E63", size=15, font={"size": 12})
        nodes_added.add(end_node_id)
        net.add_edge(last_connected_node_in_main_chain, end_node_id, color="#AAAAAA", width=2, dashes=True)
        
        pyvis_level_counter += 2

PYVIS_OPTIONS = """
    var options = {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "levelSeparation": 200,
          "nodeSpacing": 120,
          "treeSpacing": 180,
          "blockShifting": true,
          "edgeMinimization": true,
          "parentCentralization": false,
          "direction": "UD",
          "sortMethod": "hierarchical"
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200,
        "navigationButtons": true,
        "keyboard": true
      },
      "physics": {
        "enabled": false
      },
      "nodes": {
        "borderWidth": 1,
        "borderWidthSelected": 2,
        "font": { "size": 11, "face": "Arial" }
      },
      "edges": {
        "smooth": {
            "enabled": true,
            "type": "cubicBezier",
            "forceDirection": "vertical",
            "roundness": 0.4
         },
         "arrows": {
           "to": { "enabled": true, "scaleFactor": 0.7 }
         }
      }
    }
    """

def main():
    # 1. Load Scripted Tasks (main tasks, KQs, end states)
    scripted_tasks = load_scripted_tasks(SCRIPTED_TASKS_FILE)
    if not scripted_tasks:
        print(f"No scripted tasks loaded from '{SCRIPTED_TASKS_FILE}'. Visualization might be empty or incomplete.")
        # return # Optionally exit if no main tasks

    task_names_from_json = [task['name'] for task in scripted_tasks if isinstance(task, dict) and 'name' in task]

    # 2. Load Layer-Specific Data (scripted subtasks, branches)
    all_layer_data = load_all_layer_data(GENERATE_DATA_DIR, task_names_from_json)
    
    if not all_layer_data and task_names_from_json:
        print(f"Warning: No layer-specific data (scripted subtasks, branches) loaded. Check '{GENERATE_DATA_DIR}'. The graph will show Tasks, KQs, and End States only.")

    net = Network(height="95vh", width="100%", directed=True, notebook=False,
                  bgcolor="#F0F0F0", font_color="black", # Lighter background
                  select_menu=True, 
                  filter_menu=True   
                  )

    # 3. Populate the network with the new structure
    populate_network_new(net, scripted_tasks, all_layer_data)
    
    net.set_options(PYVIS_OPTIONS)
    # For debugging layout, uncomment:
    # net.show_buttons(filter_=['layout', 'interaction', 'nodes', 'edges']) 

    try:
        net.show(OUTPUT_HTML_FILE, notebook=False)
        abs_output_path = os.path.abspath(OUTPUT_HTML_FILE)
        print(f"Visualization generated: {abs_output_path}")
        print("Structure: Task -> KQ -> Layer Hub (with Scripted/Branch children) -> ... -> End State")
    except Exception as e:
        print(f"Error generating or saving HTML file: {e}")

if __name__ == "__main__":
    main() 