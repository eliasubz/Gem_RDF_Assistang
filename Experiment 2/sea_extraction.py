import pandas as pd
from rdflib import Graph, RDF
from collections import defaultdict


def find_spanning_entity(ttl_path, csv_path):
    g = Graph()
    g.parse(ttl_path, format="ttl")

    df = pd.read_csv(csv_path).astype(str)
    all_csv_values = set(df.values.flatten())

    subject_links = defaultdict(set)
    object_links = defaultdict(set)
    all_entities = set()

    # Track types of subjects
    subject_types = defaultdict(set)

    for s, p, o in g:
        s_str, o_str = str(s), str(o)
        all_entities.update([s_str, o_str])
        subject_links[s_str].add(o_str)
        object_links[o_str].add(s_str)

        # Record rdf:type
        if p == RDF.type:
            subject_types[s_str].add(o_str)

    # Compute connectivity score
    entity_scores = {}
    for entity in all_entities:
        in_count = len(object_links.get(entity, []))
        out_count = len(subject_links.get(entity, []))
        total = in_count + out_count
        entity_scores[entity] = total

    # Most connected subject
    most_connected_entity = max(entity_scores.items(), key=lambda x: x[1])[0]
    connection_count = entity_scores[most_connected_entity]

    # Extract type (e.g., sphn:Patient)
    rdf_type_full = next(iter(subject_types.get(most_connected_entity, [])), "Unknown")

    # Check if ID in CSV
    matched_column = None
    entity_parts = most_connected_entity.split("/")
    for part in entity_parts:
        if part in all_csv_values:
            for col in df.columns:
                if part in df[col].values:
                    matched_column = col
                    break
            if matched_column:
                break

    # Output result
    print("🔍 Spanning Entity Analysis:")
    print(f"Entity Type (rdf:type): {rdf_type_full}")
    print(f"↳ IRI: {most_connected_entity}")
    print(f"↳ Total Connections (in + out): {connection_count}")
    if matched_column:
        print(f"↳ This entity's identifier appears in CSV column: {matched_column}")
    else:
        print("↳ This entity does not directly match any CSV column value.")

    return {
        "entity_type": rdf_type_full,
        "entity_iri": most_connected_entity,
        "connections": connection_count,
        "csv_column": matched_column,
    }


# Example usage
if __name__ == "__main__":
    csv_path = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/csv/table-FOLLOW-UP-csv.csv"  # replace with your CSV path
    ttl_path = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/rdf/FOLLOWUP_UM_RDF.txt"
    find_spanning_entity(ttl_path, csv_path)
