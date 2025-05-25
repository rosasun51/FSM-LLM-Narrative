import os
import json
from pyvis.network import Network
import re

# Define paths
GENERATE_DATA_DIR = "Generate_branches/data"
MIDDLE_DATA_DIR = "Middle_data"
OUTPUT_HTML_FILE = "task_visualization.html"

def parse_filename_for_layer_and_type(filename_prefix):
    match = re.match(r"^(scripted_subtask|subtask_branches)_layer(\d+)_(.+)$", filename_prefix)
    if match:
        type_indicator = match.group(1)
        try:
            layer_number = int(match.group(2))
        except ValueError:
            # This warning is kept as it indicates a malformed filename that affects parsing.
            print(f"Warning: Could not parse layer number as integer from '{match.group(2)}' in filename prefix '{filename_prefix}'")
            return None, None, None
        unique_suffix = match.group(3)
        return type_indicator, layer_number, unique_suffix
    return None, None, None

def load_subtask_data_from_files(generate_dir, middle_dir):
    all_granular_subtasks = []
    # To collect data for creating Layer Nodes: set of (task_base_name, layer_num)
    layer_node_identifiers = set()

    if not os.path.exists(generate_dir):
        print(f"Error: Source data directory '{generate_dir}' not found.")
        return [], set()
    
    try:
        task_run_folder_names = [d for d in os.listdir(generate_dir) if os.path.isdir(os.path.join(generate_dir, d))]
    except OSError as e:
        print(f"Error accessing source data directory '{generate_dir}': {e}")
        return [], set()

    response_file_pattern = re.compile(r"(.+)_response\.json$")

    for task_run_folder_name in task_run_folder_names:
        task_run_root_path = os.path.join(generate_dir, task_run_folder_name)
        task_base_name_for_display = task_run_folder_name.split('_')[0] if '_' in task_run_folder_name else task_run_folder_name

        for dirpath, _, filenames in os.walk(task_run_root_path):
            for file_name in filenames:
                match_response = response_file_pattern.match(file_name)
                if not match_response:
                    continue
                
                original_filename_prefix = match_response.group(1)
                file_type_indicator, file_layer_num, file_unique_suffix = parse_filename_for_layer_and_type(original_filename_prefix)

                if file_type_indicator is None:
                    # This warning means the filename itself doesn't match the expected pattern.
                    print(f"Warning: Could not parse filename structure from '{original_filename_prefix}' (from file '{file_name}'). Skipping this file.")
                    continue

                is_from_scripted_file = (file_type_indicator == "scripted_subtask")
                layer_node_identifiers.add((task_base_name_for_display, file_layer_num))

                relative_subdir_in_task = os.path.relpath(dirpath, task_run_root_path)
                middle_content_path_base = os.path.join(middle_dir, task_run_folder_name, relative_subdir_in_task)
                content_json_full_path = os.path.join(middle_content_path_base, f"{original_filename_prefix}.json")

                raw_json_data_from_file = None # Store raw loaded data for potential use
                json_load_error = False
                try:
                    with open(content_json_full_path, 'r', encoding='utf-8') as f_content:
                        raw_json_data_from_file = json.load(f_content)
                except FileNotFoundError:
                    raw_json_data_from_file = {"_FILE_NOT_FOUND_": True}
                except json.JSONDecodeError as e:
                    print(f"Warning: Error decoding JSON from '{content_json_full_path}' for '{original_filename_prefix}'. Error: {str(e)[:100]}")
                    raw_json_data_from_file = {"_JSON_ERROR_DETAILS_": str(e)}
                    json_load_error = True
                
                entries_for_this_file = []

                # Case 1: Layer 1 Scripted file, potentially with "key_questions"
                if is_from_scripted_file and isinstance(raw_json_data_from_file, dict) and "key_questions" in raw_json_data_from_file and isinstance(raw_json_data_from_file.get("key_questions"), list):
                    key_questions_list = raw_json_data_from_file["key_questions"]
                    if not key_questions_list:
                        entries_for_this_file.append({
                            "id_suffix": "_empty_kq_list",
                            "label_hint": "Empty Key Questions List",
                            "tooltip_data_override": {"status": "'key_questions' list is empty.", "file_content": raw_json_data_from_file},
                            "is_generic_file_info_node": True
                        })
                    else:
                        for kq_item in key_questions_list:
                            if isinstance(kq_item, dict) and "id" in kq_item and "content" in kq_item:
                                entries_for_this_file.append({
                                    "id_suffix": f"_kq_{kq_item['id']}",
                                    "label_override": f"Key Question {kq_item['id']}",
                                    "tooltip_data_override": str(kq_item['content']), # Just the content string
                                    "is_individual_key_question": True,
                                    "kq_id_for_tooltip_header": kq_item['id'],
                                    "original_file_layer_num_for_kq": file_layer_num # Store layer number for KQ
                                })
                            else:
                                entries_for_this_file.append({
                                    "id_suffix": f"_malformed_kq_{kq_item.get('id', 'unknown')}",
                                    "label_hint": f"Malformed KQ {kq_item.get('id', 'unknown')}",
                                    "tooltip_data_override": {"status": "Malformed item in 'key_questions' list.", "item_data": kq_item},
                                    "is_generic_file_info_node": True
                                })
                # Case 2: Standard subtask(s) - list of dicts with "subtask_id", or single dict with "subtask_id"
                elif isinstance(raw_json_data_from_file, list) and all(isinstance(item, dict) and "subtask_id" in item for item in raw_json_data_from_file):
                    for item in raw_json_data_from_file:
                        entries_for_this_file.append({"subtask_data": item})
                elif isinstance(raw_json_data_from_file, dict) and "subtask_id" in raw_json_data_from_file and not json_load_error:
                     entries_for_this_file.append({"subtask_data": raw_json_data_from_file})
                # Case 3: Fallback to a generic file-level node for other cases (error, missing, or unexpected structure)
                else:
                    status_msg = "(File content missing or empty)"
                    tooltip_content = {"status": status_msg}
                    if raw_json_data_from_file is not None and "_FILE_NOT_FOUND_" in raw_json_data_from_file:
                         pass # Already set
                    elif json_load_error:
                        status_msg = "(Error decoding JSON content)"
                        tooltip_content = {"status": status_msg, "error_details": raw_json_data_from_file.get("_JSON_ERROR_DETAILS_", "Unknown")}
                    elif raw_json_data_from_file is not None: # Some other structure
                        status_msg = "(Unexpected JSON Structure for subtasks)"
                        tooltip_content = {"status": status_msg, "file_content_snippet": str(raw_json_data_from_file)[:200]+"...".strip()}
                    
                    entries_for_this_file.append({
                        "id_suffix": "_file_info",
                        "label_hint": status_msg,
                        "tooltip_data_override": tooltip_content,
                        "is_generic_file_info_node": True
                    })

                # Process the collected entries for the current file
                for entry_detail in entries_for_this_file:
                    is_individual_kq = entry_detail.get("is_individual_key_question", False)
                    is_generic_file_node = entry_detail.get("is_generic_file_info_node", False)
                    
                    # Ensure unique KQ node IDs by incorporating task_base and layer
                    if is_individual_kq:
                        kq_original_layer = entry_detail.get("original_file_layer_num_for_kq", file_layer_num)
                        node_id = f"KQ_{task_base_name_for_display}_L{kq_original_layer}_kq_{entry_detail['kq_id_for_tooltip_header']}"
                    elif is_generic_file_node:
                        node_id = original_filename_prefix + entry_detail["id_suffix"]
                    else: # Standard subtask
                        node_id = f"{original_filename_prefix}_{entry_detail['subtask_data']['subtask_id']}"
                    
                    label = ""
                    tooltip_data_for_node = None
                    kq_id_for_header = None

                    if is_individual_kq:
                        label = entry_detail["label_override"]
                        tooltip_data_for_node = entry_detail["tooltip_data_override"]
                        kq_id_for_header = entry_detail.get("kq_id_for_tooltip_header")
                    elif is_generic_file_node:
                        label = f"FILE: {original_filename_prefix[:20]}... ({entry_detail['label_hint'][:15].strip('()')}...)"
                        if len(label) > 45 : label = label[:42]+"...)"
                        tooltip_data_for_node = entry_detail["tooltip_data_override"]
                    else: # Standard subtask
                        subtask_obj = entry_detail["subtask_data"]
                        label = f"{subtask_obj.get('title', subtask_obj['subtask_id'])[:25]}"
                        if len(label) == 25 and not label.endswith("..."): label += "..."
                        tooltip_data_for_node = subtask_obj
                    
                    all_granular_subtasks.append({
                        "id": node_id,
                        "label": label, 
                        "pyvis_level": file_layer_num, # KQs and subtasks share the same pyvis_level as their original file
                        "is_from_scripted_file": is_from_scripted_file,
                        "task_base_name": task_base_name_for_display,
                        "original_file_layer_num": file_layer_num, 
                        "tooltip_data": tooltip_data_for_node, 
                        "is_generic_file_info_node": is_generic_file_node, # Covers all non-standard-subtask, non-KQ file reps
                        "is_individual_key_question": is_individual_kq,
                        "kq_id_for_tooltip_header": kq_id_for_header
                    })
                                
    if not os.path.exists(middle_dir) and any(ln[0] for ln in layer_node_identifiers): # only warn if middle_dir is expected to be used
        print(f"Warning: Middle data directory '{middle_dir}' not found. Tooltips might be missing details.")

    return all_granular_subtasks, layer_node_identifiers

def get_tooltip_html(tooltip_data, node_label_for_title, is_generic_file_info_node, is_individual_key_question, kq_id_for_header):
    node_label_html = node_label_for_title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    tooltip_html_parts = [
        f"<strong>{node_label_html}</strong><br>"
    ]

    if is_individual_key_question:
        header_text = f"Content for Key Question {kq_id_for_header if kq_id_for_header else ''}"
        tooltip_html_parts.append(f"<strong>{header_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}:</strong><br>")
        escaped_kq_content = str(tooltip_data).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "<br>")
        tooltip_html_parts.append(escaped_kq_content)
    elif is_generic_file_info_node:
        status_message = tooltip_data.get("status", "File information node.")
        tooltip_html_parts.append(f"{status_message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}<br>")
        
        details_json_str = json.dumps(tooltip_data, indent=2, ensure_ascii=False)
        details_json_str_escaped = details_json_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tooltip_html_parts.extend([
            f"<strong>Details:</strong><br>",
            f"<pre>{details_json_str_escaped}</pre>"
        ])
    else: # Standard subtask
        internal_subtask_id = tooltip_data.get("subtask_id", "N/A")
        title = tooltip_data.get("title", "(No Title provided in JSON)")
        description = tooltip_data.get("description", "(No Description provided in JSON)")
        tooltip_html_parts.extend([
            f"<strong>Internal ID:</strong> {internal_subtask_id}<br>",
            f"<strong>Title:</strong> {title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}<br>",
            f"<strong>Description:</strong> {description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}<br>"
        ])
        
        details_json_str = json.dumps(tooltip_data, indent=2, ensure_ascii=False)
        details_json_str_escaped = details_json_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tooltip_html_parts.extend([
            f"<strong>Full JSON Details:</strong><br>",
            f"<pre>{details_json_str_escaped}</pre>"
        ])
    
    return "".join(tooltip_html_parts)

def populate_network(net, granular_subtasks_list, layer_node_identifiers_set):
    nodes_added_to_graph = set() # To prevent adding the same node ID twice
    
    # Store Key Question node IDs for linking
    task_layer_to_kq_node_id = {}

    # 1. Create Layer Nodes
    # Sort layer identifiers for consistent processing (task name, then layer num)
    sorted_layer_identifiers = sorted(list(layer_node_identifiers_set), key=lambda x: (x[0], x[1]))
    task_to_layer_nodes = {}

    for task_base, layer_num in sorted_layer_identifiers:
        layer_node_id = f"LAYER_NODE_{task_base}_L{layer_num}"
        if layer_node_id not in nodes_added_to_graph:
            net.add_node(layer_node_id, 
                         label=f"{task_base} - Layer {layer_num}", 
                         level=layer_num, # This sets the hierarchical level
                         shape="diamond", 
                         color="#FFD700", # Gold for layer nodes
                         size=25,
                         font={"size": 16, "face": "Verdana", "bold": True})
            nodes_added_to_graph.add(layer_node_id)
        if task_base not in task_to_layer_nodes:
            task_to_layer_nodes[task_base] = []
        task_to_layer_nodes[task_base].append((layer_num, layer_node_id))

    # 2. Create Granular Subtask Nodes (including Key Questions)
    for subtask_detail in granular_subtasks_list:
        node_id = subtask_detail["id"]
        if node_id in nodes_added_to_graph:
            continue
        
        label = subtask_detail["label"]
        tooltip = get_tooltip_html(subtask_detail["tooltip_data"], label, subtask_detail["is_generic_file_info_node"], subtask_detail["is_individual_key_question"], subtask_detail.get("kq_id_for_tooltip_header"))
        
        shape = "box" 
        color = "#ADD8E6" # Light blue for Key Questions and scripted subtasks by default

        if subtask_detail["is_individual_key_question"]:
            # Key Question specific appearance
            shape = "box" 
            color = "#A7C7E7" # Periwinkle blue for Key Questions (example)
            # Store its ID for linking
            task_base = subtask_detail["task_base_name"]
            kq_layer = subtask_detail["original_file_layer_num"]
            task_layer_to_kq_node_id[(task_base, kq_layer)] = node_id
        elif subtask_detail["is_generic_file_info_node"]:
            color = "#D3D3D3" # Grey for generic file-level nodes
            shape = "ellipse" 
        elif not subtask_detail["is_from_scripted_file"]: # Branched subtasks (green nodes)
            shape = "dot"
            color = "#90EE90" # Light green for branched (dot)
        # Else, it's a scripted subtask (that isn't a KQ or generic file node), keep default shape/color from above

        net.add_node(node_id, 
                     label=label, 
                     title=tooltip, 
                     level=subtask_detail["pyvis_level"], # granular nodes are at the same level as their layer node
                     shape=shape, 
                     color=color,
                     font={"size": 10, "face": "Arial"})
        nodes_added_to_graph.add(node_id)

    # 3. Create Layer-to-Layer Edges (Diamond to Diamond)
    for task_base, layers in task_to_layer_nodes.items():
        # Sort layers by number to connect them sequentially
        sorted_layers = sorted(layers, key=lambda x: x[0]) 
        for i in range(len(sorted_layers) - 1):
            source_layer_node_id = sorted_layers[i][1]
            target_layer_node_id = sorted_layers[i+1][1]
            net.add_edge(source_layer_node_id, target_layer_node_id, color="#555555", width=3, dashes=False)

    # 4. Create Edges: Layer Node -> KQ Node -> Granular Subtasks
    for subtask_detail in granular_subtasks_list:
        granular_node_id = subtask_detail["id"]
        task_base = subtask_detail["task_base_name"]
        file_layer = subtask_detail["original_file_layer_num"]
        
        parent_layer_node_id = f"LAYER_NODE_{task_base}_L{file_layer}"
        kq_node_id_for_layer = task_layer_to_kq_node_id.get((task_base, file_layer))

        if subtask_detail["is_individual_key_question"]:
            # Edge from Layer Node to this Key Question Node
            if parent_layer_node_id in nodes_added_to_graph and granular_node_id in nodes_added_to_graph:
                net.add_edge(parent_layer_node_id, granular_node_id, color="#B0B0B0", width=1.5, arrows="to", length=50)
        elif not subtask_detail["is_generic_file_info_node"]: 
            # This is a granular subtask (green node or other non-KQ, non-file node)
            # Edge from KQ Node to this Granular Subtask
            if kq_node_id_for_layer and kq_node_id_for_layer in nodes_added_to_graph and granular_node_id in nodes_added_to_graph:
                net.add_edge(kq_node_id_for_layer, granular_node_id, color="#C0C0C0", width=1, arrows="to", length=50)
            # Fallback: if no KQ node for this layer, connect directly from Layer Node (maintains some connectivity)
            elif parent_layer_node_id in nodes_added_to_graph and granular_node_id in nodes_added_to_graph:
                print(f"Warning: KQ Node not found for layer {file_layer} of task {task_base}. Connecting subtask '{granular_node_id}' directly to Layer Node '{parent_layer_node_id}'.")
                net.add_edge(parent_layer_node_id, granular_node_id, color="#E0E0E0", width=1, dashes=True, arrows="to", length=50) # Dashed line for fallback
        # Generic file info nodes are not typically connected further from layer nodes unless they are KQs (handled above)

PYVIS_OPTIONS = """
    var options = {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "levelSeparation": 250, 
          "nodeSpacing": 110, 
          "treeSpacing": 160,
          "blockShifting": true,
          "edgeMinimization": true,
          "parentCentralization": true,
          "direction": "UD", 
          "sortMethod": "hierarchical" 
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200
      },
      "physics": {
        "enabled": false 
      },
      "nodes": {
        "borderWidth": 1,
        "borderWidthSelected": 2,
        "font": { "size": 11 }
      },
      "edges": {
        "smooth": {
            "enabled": true,
            "type": "dynamic", 
            "roundness": 0.5
         }
      }
    }
    """

def main():
    all_granular_subtasks_list, layer_node_identifiers = load_subtask_data_from_files(GENERATE_DATA_DIR, MIDDLE_DATA_DIR)

    if not all_granular_subtasks_list and not layer_node_identifiers:
        print(f"No task data found or processed. Please check your JSON files in '{MIDDLE_DATA_DIR}' and their corresponding '_response.json' triggers in '{GENERATE_DATA_DIR}'.")
        return

    net = Network(height="90vh", width="100%", directed=True, notebook=False,
                  bgcolor="#FFFFFF", font_color="black", 
                  select_menu=False, 
                  filter_menu=False  
                  )

    populate_network(net, all_granular_subtasks_list, layer_node_identifiers)
    net.set_options(PYVIS_OPTIONS)

    try:
        net.show(OUTPUT_HTML_FILE, notebook=False)
        abs_output_path = os.path.abspath(OUTPUT_HTML_FILE)
        print(f"Visualization generated: {abs_output_path}")
        print(f"Structure: Task Layers (diamonds) connect sequentially. Subtasks (various shapes) connect to their parent Layer.")
    except Exception as e:
        print(f"Error generating or saving HTML file: {e}")

if __name__ == "__main__":
    main() 