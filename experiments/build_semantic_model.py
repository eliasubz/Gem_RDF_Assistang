from rdflib import Graph, RDF, RDFS
from collections import defaultdict
from urllib.parse import urlparse

# 📘 Semantic Model:

# Procedure (P0023919393932_2023-11-15_00v2)
#   ├── hasDateTime ──> 2023-11-15T00:00:00
#   ├── hasStatusCode ──> 385658003
#   ├── hasCode ──> 60631000210103
#   ├── hasPatient ──> Patient (P0023919393932_2023-11-15_00v2)
#     ├── hasSubjectName ──> SubjectName (P0023919393932_2023-11-15_00v2)
#       ├── hasGivenName ──> Klaas
#       ├── hasFamilyName ──> Van Hooijdonk
#     ├── hasIdentifier ──> P0023919393932
#     ├── hasBirthDate ──> BirthDate (P0023919393932_2023-11-15_00v2)


def simplify_iri(iri):
    """Get the last part of the IRI for display."""
    return iri.split("#")[-1] if "#" in iri else iri.rstrip("/").split("/")[-1]


def build_semantic_model(ttl_path):
    g = Graph()
    g.parse(ttl_path, format="ttl")

    # Map subjects to their rdf:type
    types = defaultdict(set)
    for s, p, o in g.triples((None, RDF.type, None)):
        types[s].add(o)

    # Build entity relationships
    relationships = defaultdict(lambda: defaultdict(set))

    for s, p, o in g:
        if p == RDF.type:
            continue  # already handled
        relationships[s][p].add(o)

    # Determine top-level entities (not objects elsewhere)
    all_subjects = set(relationships.keys())
    all_objects = {
        o for sub in relationships.values() for objs in sub.values() for o in objs
    }
    top_entities = all_subjects - all_objects

    # Recursively render semantic tree
    def render_entity(entity, level=0, visited=None):
        if visited is None:
            visited = set()

        indent = "  " * level
        label = simplify_iri(next(iter(types[entity]), "Unknown"))
        entity_line = f"{indent}{label} ({simplify_iri(str(entity))})"
        output = [entity_line]

        if entity in visited:
            return output  # avoid circular refs
        visited.add(entity)

        for pred, targets in relationships[entity].items():
            pred_label = simplify_iri(str(pred))
            for target in targets:
                if (target, RDF.type, None) in g:
                    # Nested class
                    sub_lines = render_entity(target, level + 1, visited)
                    sub_lines[0] = (
                        f"{indent}  ├── {pred_label} ──> {sub_lines[0].strip()}"
                    )
                    output.extend(sub_lines)
                else:
                    # Literal or terminal
                    target_display = simplify_iri(str(target))
                    output.append(f"{indent}  ├── {pred_label} ──> {target_display}")

        return output

    # Start from top entities (likely Patients)
    semantic_model_lines = []
    for entity in top_entities:
        semantic_model_lines.extend(render_entity(entity))
        semantic_model_lines.append("")  # newline between entities

    return "\n".join(semantic_model_lines)


if __name__ == "__main__":
    csv_folder = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/csv"
    rdf_folder = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/rdf"
    output_folder = (
        "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/analysis"
    )
    ttl_path = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/rdf/FOLLOWUP.txt"
    model_output = build_semantic_model(ttl_path)
    print("📘 Semantic Model:\n")
    print(model_output)
