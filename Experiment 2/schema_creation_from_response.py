import os
import json
from rdflib import Graph, URIRef, BNode, Namespace
from rdflib.namespace import RDF
import sys

# === SETUP ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Path_Finding_Logic.main import PathFinder

output_dir = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset/exp_one_hop"
csv_dir = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset"
analysis_dir = (
    "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset/analysis"
)
output_ttl_dir = os.path.join(output_dir, "rdf_schema_only")
os.makedirs(output_ttl_dir, exist_ok=True)

SPHN = Namespace("https://biomedit.ch/rdf/sphn-ontology/sphn#")
AIDAVA = Namespace("https://biomedit.ch/rdf/sphn-ontology/AIDAVA/")


# === HELPERS ===
def get_main_entity_type(analysis_file: str) -> str:
    with open(analysis_file, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line.startswith("Main Entity Type:"):
            return first_line.replace("Main Entity Type:", "").strip()
    return ""


# === MAIN LOOP ===
for file in os.listdir(output_dir):
    if not file.endswith("_response.txt"):
        continue

    base_name = file.replace("_response.txt", "")
    json_path = os.path.join(output_dir, file)
    csv_path = os.path.join(csv_dir, f"{base_name}.csv")

    if not os.path.exists(csv_path):
        print(f"[!] No CSV for {base_name}, skipping.")
        continue

    # Load analysis file and get main entity
    analysis_file = os.path.join(analysis_dir, f"{base_name}_analysis.txt")
    main_entity = get_main_entity_type(analysis_file)
    if not main_entity:
        print(f"[!] Could not determine main entity from {analysis_file}, skipping.")
        continue

    # Get paths from PathFinder
    pathfinder = PathFinder(ttl_file="aidava-sphn.ttl")
    paths = pathfinder.find_paths(hop_count=2, target_class=main_entity)

    # Load mapping JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    column_mappings = data.get("column_mappings", [])

    # Build schema graph
    g = Graph()
    g.bind("sphn", SPHN)
    g.bind("aidava", AIDAVA)

    for mapping in column_mappings:
        path_id = mapping["path"]["path_id"] - 1  # Convert from 1-indexed
        if path_id >= len(paths):
            print(f"[!] Path ID {path_id+1} out of range for {base_name}")
            continue

        path = paths[path_id]

        # Example path:
        # [('ClassA', None), ('ClassB', 'hasSomething'), ('ClassC', 'hasElse')]
        prev_node = URIRef(path[0][0])
        for class_uri, predicate in path[1:]:
            pred = URIRef(predicate)
            bnode = BNode()
            g.add((prev_node, pred, bnode))
            g.add((bnode, RDF.type, URIRef(class_uri)))
            prev_node = bnode

    # Save Turtle
    ttl_path = os.path.join(output_ttl_dir, f"{base_name}.ttl")
    g.serialize(destination=ttl_path, format="turtle")
    print(f"[✓] Schema written to: {ttl_path}")
    nt_path = os.path.join(output_ttl_dir, f"{base_name}.nt")
    g.serialize(destination=nt_path, format="nt")
    print(f"[✓] Triples also written to: {nt_path}")
