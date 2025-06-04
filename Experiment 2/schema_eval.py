import os
import json
from rdflib import Graph, URIRef, BNode, Namespace
from rdflib.namespace import RDF
import sys
import pandas as pd


solution_paths = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/gt_paths_two_hop"
response_folder = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/exp_one_hop"
response_folder = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/path_selection_two_hop_short_URI"
analysis_dir = (
    "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/analysis"
)
model_name = "gpt_nano"
hop_count_exp = 2
CHECK_ALL_GT_IDS = False


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
def eval_folder(response_folder, CHECK_ALL_GT_IDS, path_dic, full_hop_count):
    for file in os.listdir(response_folder):
        if not file.endswith("_response.txt"):
            continue

        base_name = file.replace("_response.txt", "")
        json_path = os.path.join(response_folder, file)

        # Load analysis file and get main entity
        analysis_file = os.path.join(analysis_dir, f"{base_name}_analysis.txt")
        main_entity = get_main_entity_type(analysis_file)
        if not main_entity:
            print(
                f"[!] Could not determine main entity from {analysis_file}, skipping."
            )
            continue

        # Load and get solution paths
        gt_path_file = os.path.join(solution_paths, f"{base_name}.txt")

        # # Load and parse the ground truth path file
        # gt_dict = {}
        # with open(gt_path_file, "r") as f:
        #     for line in f:
        #         parts = line.strip().split()
        #         if len(parts) == 2:
        #             column_name, path_id = parts
        #             print(column_name, " and ", path_id)
        #             gt_dict[column_name] = int(path_id) - 1
        gt_dict = {}
        with open(gt_path_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:  # Ensure there's at least a column name and one ID
                    column_name = parts[0]
                    # Join all parts after the column name, then split by comma
                    # and convert each part to an integer, subtracting 1 for 0-indexing.
                    path_ids_str = " ".join(parts[1:]).split(",")

                    # Filter out any empty strings that might result from splitting (e.g., "79, 8," -> ["79", " 8", ""])
                    parsed_path_ids = [
                        int(p.strip()) - 1 for p in path_ids_str if p.strip()
                    ]

                    # Store the list of parsed path IDs in the dictionary
                    gt_dict[column_name] = parsed_path_ids

                    # Optional: for debugging or verification
                    # print(f"Parsed '{column_name}': {gt_dict[column_name]}")
                else:
                    print(
                        f"Warning: Skipping malformed line in ground truth file: '{line.strip()}' - Expected at least a column name and a path ID."
                    )

        # Get paths from PathFinder
        # pathfinder = PathFinder(ttl_file="aidava-sphn.ttl")
        # paths = pathfinder.find_paths(hop_count=hop_count_exp, target_class=main_entity)
        paths = path_dic[main_entity][full_hop_count]

        # Load mapping JSON
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        column_mappings = data.get("column_mappings", [])
        rows = []

        for mapping in column_mappings:
            predicted_path_id = mapping["path"]["path_id"] - 1  # Convert from 1-indexed
            column_name = mapping["column_name"]

            if predicted_path_id >= len(paths):
                print(
                    f"[!] Path ID {predicted_path_id+1} out of range for {base_name} with length {len(paths)}"
                )
                continue

            path_output = paths[predicted_path_id]

            # print(paths)

            gt_path_ids = gt_dict[column_name]

            gt_paths_for_column = paths[gt_dict[column_name][0]]
            justification = mapping["justification"]
            if CHECK_ALL_GT_IDS:
                # Check if the predicted_path_id is present in ANY of the ground truth IDs
                is_correct = int(predicted_path_id in gt_path_ids)
            else:
                is_correct = int(predicted_path_id == gt_path_ids[0])

            hop_count_output = len(path_output) - 1
            hop_count = len(gt_paths_for_column) - 1

            row = {
                "Column": column_name,  #
                "Model": model_name,
                "ground truth path_id": gt_dict[column_name],
                "chosen path_id": predicted_path_id,  # You can add the predicted target class/entity if available
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
            for i in range(0, len(gt_paths_for_column)):
                obj_class, predicate = gt_paths_for_column[i]
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
        if CHECK_ALL_GT_IDS:
            evaluation_dir = os.path.join(response_folder, "evaluation")
        else:
            evaluation_dir = os.path.join(response_folder, "evaluation_strict")
        os.makedirs(evaluation_dir, exist_ok=True)
        evaluation_file = os.path.join(evaluation_dir, f"{base_name}.csv")
        df = pd.DataFrame(rows)

        df.to_csv(evaluation_file, index=False)

        # Column	Model (Pred (not sure how to call it pred column should have a better name) 1 if path_id correct else 0)Output first_predicate  (put the predicate of the second tuple) first_predicate_output first_object (put the object of the second tuple) first_object_output second_predicate (put the object of the third tuple and so on)second_predicate_output second_object second_object_output third_predicate third_predicate_output third_object third_object_output first_object HopCount HopCountoutput Description	Notes

        # Example path:
        # [('ClassA', None), ('ClassB', 'hasSomething'), ('ClassC', 'hasElse')]


def build_path_dictionary(analysis_dir, ttl_file):

    print("Building Path dictionary")

    # Initialize pathfinder once
    pathfinder = PathFinder(ttl_file=ttl_file)

    # Dictionary to hold paths by entity and hop count
    entity_paths = {}

    # Iterate over analysis files
    for filename in os.listdir(analysis_dir):
        if filename.endswith("_analysis.txt"):
            analysis_file = os.path.join(analysis_dir, filename)

            # Extract main entity
            main_entity = get_main_entity_type(analysis_file)

            # Initialize dict for entity if not already there
            if main_entity not in entity_paths:
                entity_paths[main_entity] = {1: [], 2: []}

            # Get 1-hop and 2-hop paths
            onehop_paths = pathfinder.find_paths(hop_count=1, target_class=main_entity)
            twohop_paths = pathfinder.find_paths(hop_count=2, target_class=main_entity)

            # Store them
            entity_paths[main_entity][1].extend(onehop_paths)
            entity_paths[main_entity][2].extend(twohop_paths)

    return entity_paths


if __name__ == "__main__":
    base_csv_dir = (
        "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data"
    )

    base_analysis_dir = f"{base_csv_dir}/analysis"
    base_csv_dir = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/path_selection"
    base_output_dir = f"{base_csv_dir}"

    hop_counts = [1, 2]
    example_counts = [1, 3]
    uri_combinations = [True, False]  # only one can be True per run
    check_all_gt_ids = [True, False]

    # Get entity path ditionary
    path_dic = build_path_dictionary(base_analysis_dir, "aidava-sphn.ttl")
    for check_id in check_all_gt_ids:
        for hop_count in hop_counts:
            if hop_count == 1:
                solution_paths = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/gt_paths_one_hop"
            else:
                solution_paths = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data/gt_paths_two_hop"
            for num_examples in example_counts:
                for short_uri in uri_combinations:

                    uri_type = "short_URI" if short_uri else "long_URI"
                    ### CHANGE HERE
                    output_dir = f"{base_output_dir}/path_selection_spec_instr_{hop_count}_hop_{uri_type}_{num_examples}_smpl"
                    output_dir = f"{base_output_dir}/path_selection_gpt_{hop_count}_hop_{uri_type}_{num_examples}_smpl"
                    output_dir = f"{base_output_dir}/path_selection_mini_{hop_count}_hop_{uri_type}_{num_examples}_smpl"
                    print(
                        f"Running_eval: hop_count={hop_count}, short_uri={short_uri}, examples={num_examples}"
                    )

                    eval_folder(output_dir, check_id, path_dic, hop_count)

    # eval_folder(test, False)
