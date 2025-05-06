import os
import pandas as pd
from rdflib import Graph, RDF, Literal
from collections import defaultdict


def find_spanning_entity(g, df):
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

    # Extract type
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

    return {
        "entity_type": rdf_type_full,
        "entity_iri": most_connected_entity,
        "connections": connection_count,
        "csv_column": matched_column,
    }


def get_column_mappings(g, df):
    column_mappings = {}

    # Build a type map (subject -> rdf:type)
    subject_types = defaultdict(set)
    for s, p, o in g.triples((None, RDF.type, None)):
        subject_types[str(s)].add(str(o))

    for column in df.columns:
        values = df[column].dropna().astype(str).unique()
        subject_info_map = defaultdict(
            lambda: {
                "predicates": set(),
                "type": set(),
                "incoming": set(),
                "matched_values": set(),
            }
        )

        for value in values:
            lit = Literal(value)
            for s, p, o in g.triples((None, None, lit)):
                s_str, p_str = str(s), str(p)
                subject_info = subject_info_map[s_str]
                subject_info["predicates"].add(p_str)
                subject_info["type"].update(subject_types.get(s_str, set()))
                subject_info["matched_values"].add(value)

                # Also get incoming triples where this subject is object
                for ss, pp, _ in g.triples((None, None, s)):
                    subject_info["incoming"].add((str(ss), str(pp)))

        column_mappings[column] = subject_info_map

    return column_mappings


def find_entity_connections(g, main_entity, predicate):
    """Find all connections between the main entity and a specific predicate."""
    connections = []

    # Find direct connections where main entity is subject
    for s, p, o in g.triples((None, None, None)):
        if str(s) == main_entity and str(p) == predicate:
            connections.append(("direct", str(o)))
        # Find connections where main entity is object
        elif str(o) == main_entity and str(p) == predicate:
            connections.append(("inverse", str(s)))

    return connections


def process_csv_file(csv_path, ttl_path, output_folder):
    # Load RDF TTL file
    g = Graph()
    g.parse(ttl_path, format="ttl")

    # Load CSV
    df = pd.read_csv(csv_path)

    # Get spanning entity information
    spanning_info = find_spanning_entity(g, df)

    # Get column mappings
    column_mappings = get_column_mappings(g, df)

    # Generate output filename
    csv_filename = os.path.splitext(os.path.basename(csv_path))[0]
    output_file_path = os.path.join(output_folder, f"{csv_filename}_analysis.txt")

    with open(output_file_path, "w", encoding="utf-8") as f_out:
        # Write spanning entity information
        f_out.write(f"Main Entity Type: {spanning_info['entity_type']}\n")
        f_out.write(f"Main Entity IRI: {spanning_info['entity_iri']}\n")
        f_out.write(f"Total Connections: {spanning_info['connections']}\n\n")

        # Write column mappings with enriched semantic context
        f_out.write("Column Mappings and Semantic Context:\n")
        for column, subjects in column_mappings.items():
            f_out.write(f"\nColumn: {column}\n")
            if not subjects:
                f_out.write("  ↳ No match found in RDF\n")
                continue

            for subj, info in subjects.items():
                f_out.write(f"  Subject: {subj}\n")
                f_out.write(
                    f"    ↳ rdf:type(s): {', '.join(info['type']) or 'Unknown'}\n"
                )
                f_out.write(
                    f"    ↳ Matched Value(s): {', '.join(info['matched_values'])}\n"
                )
                for predicate in info["predicates"]:
                    f_out.write(f"    ↳ Predicate: {predicate}\n")

                if info["incoming"]:
                    f_out.write(f"    ↳ Incoming triples:\n")
                    for src, pred in info["incoming"]:
                        f_out.write(f"      ← {pred} ← {src}\n")

    print(f"✅ Analysis saved to: {output_file_path}")
    return output_file_path


def process_csv_folder(csv_folder, rdf_folder, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get all CSV files in the folder
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]

    for csv_file in csv_files:
        # Construct paths
        csv_path = os.path.join(csv_folder, csv_file)
        # Assuming RDF file has same name but different extension
        rdf_file = os.path.splitext(csv_file)[0] + ".txt"
        rdf_path = os.path.join(rdf_folder, rdf_file)

        if os.path.exists(rdf_path):
            print(f"\nProcessing {csv_file}...")
            process_csv_file(csv_path, rdf_path, output_folder)
        else:
            print(f"⚠️ No matching RDF file found for {csv_file}")


if __name__ == "__main__":
    # Example usage
    csv_folder = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/csv"
    rdf_folder = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/rdf"
    output_folder = (
        "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/analysis"
    )

    process_csv_folder(csv_folder, rdf_folder, output_folder)
