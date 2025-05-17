import json
from rdflib import Graph, URIRef
import os


def extract_entity_subgraph(
    input_ttl_path: str, entity_uris: list[str], output_ttl_path: str
):
    """
    Extracts triples where any of the entities appear as subject or object,
    and saves the result to a TTL file.
    """
    g = Graph()
    g.parse(input_ttl_path, format="ttl")

    subgraph = Graph()
    for entity_uri in entity_uris:
        uri_ref = URIRef(entity_uri)

        for s, p, o in g.triples((uri_ref, None, None)):
            subgraph.add((s, p, o))
        for s, p, o in g.triples((None, None, uri_ref)):
            subgraph.add((s, p, o))

    subgraph.serialize(destination=output_ttl_path, format="turtle")
    print(f"Subgraph written to {output_ttl_path}")
    with open(output_ttl_path, "r", encoding="utf-8") as f:
        subgraph_content = f.read()
    return subgraph_content


def process_responses_and_extract_subgraphs(
    response_folder: str,
    input_ttl_path: str,
    output_subgraph_folder: str,
    top_k: int = 5,
):
    """
    Processes JSON response files, extracts top-k candidate entities, and builds subgraphs.

    Parameters:
        response_folder (str): Folder containing *_response.txt JSON files.
        input_ttl_path (str): Path to the RDF TTL file.
        output_subgraph_folder (str): Where to save extracted subgraphs.
        top_k (int): Number of top candidate entities to use for subgraph extraction.
    """
    os.makedirs(output_subgraph_folder, exist_ok=True)

    for file in os.listdir(response_folder):
        if not file.endswith("_response.txt"):
            continue

        response_path = os.path.join(response_folder, file)
        try:
            with open(response_path, encoding="utf-8") as f:
                data = json.load(f)

            candidates = data.get("spanning_entity_candidates", [])
            selected_entities = candidates[:top_k]

            base_name = os.path.splitext(file)[0].replace("_response", "")
            output_ttl = os.path.join(
                output_subgraph_folder, f"{base_name}_subgraph.ttl"
            )

            subgraph = extract_entity_subgraph(
                input_ttl_path=input_ttl_path,
                entity_uris=selected_entities,
                output_ttl_path=output_ttl,
            )

        except Exception as e:
            print(f"Error processing {file}: {e}")


process_responses_and_extract_subgraphs(
    response_folder=r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\curated_dataset\main_entity_selection",
    input_ttl_path="aidava-sphn-flat.ttl",
    output_subgraph_folder="working_memory/subgraphs",
    top_k=5,
)
