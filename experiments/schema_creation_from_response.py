import os
import json
import pandas as pd
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import RDF, XSD
from llm_assistant_hack_main.main import PathFinder


# Define input/output directories
output_dir = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset/exp_one_hop"
csv_dir = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset"
analysis_dir = (
    "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset/analysis"
)
hop_count = 2
output_ttl_dir = os.path.join(output_dir, "rdf_output")
os.makedirs(output_ttl_dir, exist_ok=True)

# SPHN namespace
SPHN = Namespace("https://biomedit.ch/rdf/sphn-ontology/sphn#")
AIDAVA = Namespace("https://biomedit.ch/rdf/sphn-ontology/AIDAVA/")


def get_main_entity_type(analysis_file: str) -> str:
    """Extract main entity type from analysis file."""
    with open(analysis_file, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line.startswith("Main Entity Type:"):
            return first_line.replace("Main Entity Type:", "").strip()
    return ""


# Process each response file
for file in os.listdir(output_dir):
    if not file.endswith("_response.txt"):
        continue

    base_name = file.replace("_response.txt", "")
    json_path = os.path.join(output_dir, file)
    csv_path = os.path.join(csv_dir, f"{base_name}.csv")

    pathfinder = PathFinder(ttl_file="aidava-sphn.ttl")
    analysis_file = os.path.join(analysis_dir, f"{base_name}_analysis.txt")
    main_entity = get_main_entity_type(str(analysis_file))
    if not main_entity:
        print(f"Warning: Could not find main entity type in {analysis_file}")
        continue

    paths = ""
    if main_entity:
        paths = pathfinder.find_paths(hop_count=hop_count, target_class=main_entity)
    print(paths)
    if not os.path.exists(csv_path):
        print(f"CSV for {base_name} not found. Skipping.")
        continue

    # Load JSON mapping and CSV
    with open(json_path, encoding="utf-8") as f:
        print(json_path)
        json_data = json.load(f)

    column_mappings = json_data.get("column_mappings", [])

    df = pd.read_csv(csv_path, sep=";")

    g = Graph()
    g.bind("sphn", SPHN)
    g.bind("aidava", AIDAVA)

    for idx, row in df.iterrows():
        subj = BNode()  # Could be URIRef if you have a subject ID
        for mapping in column_mappings:
            col = mapping["column_name"]
            path = mapping["path"]
            predicate = URIRef(path["predicate"])
            value = row[col]

            target = path["target_entity"]

            if target.startswith("http://www.w3.org/2001/XMLSchema#"):
                # Treat as literal
                dtype = getattr(XSD, target.split("#")[-1], XSD.string)
                g.add((subj, predicate, Literal(value, datatype=dtype)))
            else:
                # Treat as resource
                obj_uri = URIRef(f"https://biomedit.ch/resource/{col}/{value}")
                g.add((subj, predicate, obj_uri))
                g.add((obj_uri, RDF.type, URIRef(target)))

        g.add((subj, RDF.type, URIRef(path["source_entity"])))

    # Output to Turtle file
    ttl_path = os.path.join(output_ttl_dir, f"{base_name}.ttl")
    g.serialize(destination=ttl_path, format="turtle")
    print(f"Generated: {ttl_path}")
