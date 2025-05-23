import os
import json
from rdflib import Graph, URIRef, BNode, Namespace
from rdflib.namespace import RDF
import sys
import pandas as pd


solution_paths = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/gt_paths_one_hop"
response_folder = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/exp_one_hop"
analysis_dir = (
    "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/analysis"
)
model_name = "gpt_nano"
hop_count_exp = 1

# === SETUP ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Path_Finding_Logic.main import PathFinder


def get_main_entity_type(analysis_file: str) -> str:
    with open(analysis_file, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line.startswith("Main Entity Type:"):
            return first_line.replace("Main Entity Type:", "").strip()
    return ""


# === MAIN LOOP ===
for file in os.listdir(response_folder):
    if not file.endswith("_response.txt"):
        continue

    base_name = file.replace("_response.txt", "")
    json_path = os.path.join(response_folder, file)

    # Load analysis file and get main entity
    analysis_file = os.path.join(analysis_dir, f"{base_name}_analysis.txt")
    main_entity = get_main_entity_type(analysis_file)
    if not main_entity:
        print(f"[!] Could not determine main entity from {analysis_file}, skipping.")
        continue

    # Load and get solution paths
    gt_path_file = os.path.join(solution_paths, f"{base_name}.txt")

    # Load and parse the ground truth path file
    gt_dict = {}
    with open(gt_path_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                column_name, path_id = parts
                gt_dict[column_name] = int(path_id) - 1

    # Get paths from PathFinder
    pathfinder = PathFinder(ttl_file="aidava-sphn.ttl")
    paths = pathfinder.find_paths(hop_count=hop_count_exp, target_class=main_entity)
    print(paths)

    # Load mapping JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    column_mappings = data.get("column_mappings", [])
    rows = []

    for mapping in column_mappings:
        path_id = mapping["path"]["path_id"] - 1  # Convert from 1-indexed
        column_name = mapping["column_name"]

        if path_id >= len(paths):
            print(
                f"[!] Path ID {path_id+1} out of range for {base_name} with length {len(paths)}"
            )
            continue

        path_output = paths[path_id]

        print(paths)
        print(gt_dict[column_name])
        path_gt = paths[gt_dict[column_name]]
        justification = mapping["justification"]

        is_correct = int(path_id == gt_dict[column_name])
        hop_count_output = len(path_output) - 1
        hop_count = len(path_gt) - 1

        row = {
            "Column": column_name,  #
            "Model": model_name,
            "HopCount_experiment": hop_count,
            "ground truth path_id": gt_dict[column_name],
            "chosen path_id": path_id,  # You can add the predicted target class/entity if available
            "is match": is_correct,
            "first_predicate": "",
            "first_predicate_output": "",
            "first_object": "",
            "first_object_output": "",
            "second_predicate": "",
            "second_predicate_output": "",
            "second_object": "",
            "second_object_output": "",
            "third_predicate": "",
            "third_predicate_output": "",
            "third_object": "",
            "third_object_output": "",
            "HopCount": hop_count,
            "HopCountoutput": hop_count_output,
            "Notes": justification,
        }

        # Populate with output details details
        for i in range(0, len(path_gt)):
            obj_class, predicate = path_gt[i]
            if i == 1:
                row["first_predicate"] = predicate
                row["first_object"] = obj_class
            elif i == 2:
                row["second_predicate"] = predicate
                row["second_object"] = obj_class
            elif i == 3:
                row["third_predicate"] = predicate
                row["third_object"] = obj_class

        # Populate with output details details
        for i in range(0, len(path_output)):
            obj_class, predicate = path_output[i]
            if i == 1:
                row["first_predicate_output"] = predicate
                row["first_object_output"] = obj_class
            elif i == 2:
                row["second_predicate_output"] = predicate
                row["second_object_output"] = obj_class
            elif i == 3:
                row["third_predicate_output"] = predicate
                row["third_object_output"] = obj_class
        rows.append(row)

    # Save evaluation
    evaluation_dir = os.path.join(response_folder, "evaluation")
    os.makedirs(evaluation_dir, exist_ok=True)
    evaluation_file = os.path.join(evaluation_dir, f"{base_name}.csv")
    df = pd.DataFrame(rows)
    df.to_csv(evaluation_file, index=False)

    # Column	Model (Pred (not sure how to call it pred column should have a better name) 1 if path_id correct else 0)Output first_predicate  (put the predicate of the second tuple) first_predicate_output first_object (put the object of the second tuple) first_object_output second_predicate (put the object of the third tuple and so on)second_predicate_output second_object second_object_output third_predicate third_predicate_output third_object third_object_output first_object HopCount HopCountoutput Description	Notes

    # Example path:
    # [('ClassA', None), ('ClassB', 'hasSomething'), ('ClassC', 'hasElse')]
