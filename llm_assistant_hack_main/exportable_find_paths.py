from collections import deque
from pathlib import Path
from rdflib import Graph

from models import Class, Property
from ontology_indexer import OntologyIndexer

FILE = Path("aidava-sphn.ttl")


def build_graph():
    g = Graph()
    g.parse(str(FILE), format="turtle")

    ontology_indexer = OntologyIndexer()

    classes: list[Class] = ontology_indexer.get_classes(
        "https://biomedit.ch/rdf/sphn-ontology/sphn#", g
    )
    properties: list[Property] = ontology_indexer.get_properties(
        "https://biomedit.ch/rdf/sphn-ontology/sphn#", g
    )

    graph_dict = {}

    for cls in classes:
        property_dict: dict[str, list[str]] = {}
        for prop in properties:
            if cls.full_uri in prop.domain:
                if prop.full_uri not in property_dict:
                    property_dict[prop.full_uri] = []
                for range_cls in prop.range:
                    if isinstance(range_cls, Class):
                        property_dict[prop.full_uri].append(range_cls.full_uri)
                    else:
                        property_dict[prop.full_uri].append(range_cls)
        graph_dict[cls.full_uri] = property_dict

    return graph_dict


def bfs_paths_with_n_hops(graph, start, n):
    queue = deque()
    queue.append((start, [(start, None)]))

    all_paths = []

    while queue:
        current, path = queue.popleft()

        if len(path) - 1 == n:
            all_paths.append(path)
            continue

        if current in graph:
            for predicate, neighbors in graph[current].items():
                for neighbor in neighbors:
                    if not any(step[0] == neighbor for step in path):  # Avoid cycles
                        queue.append((neighbor, path + [(neighbor, predicate)]))

    # Write to file
    with open("output.txt", "w", encoding="utf-8") as f:
        for i, path in enumerate(all_paths, 1):
            readable = f"{i}. {path[0][0]}"
            for node, pred in path[1:]:
                readable += f" -[{pred}]-> {node}"
            f.write(readable + "\n")

    return all_paths


def find_paths(hop_count: int, target_class: str) -> list[list[tuple[str, str | None]]]:
    graph = build_graph()
    return bfs_paths_with_n_hops(graph, target_class, hop_count)
