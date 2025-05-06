from collections import deque
import json
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.term import Node

from models import Class, Property
from ontology_indexer import OntologyIndexer
import ontology_indexer

FILE = Path("aidava-sphn.ttl")

g = Graph()
g.parse(str(FILE), format="turtle")

TARGET_CLASS = "https://biomedit.ch/rdf/sphn-ontology/sphn#ProblemCondition"
TARGET_CLASS = "https://biomedit.ch/rdf/sphn-ontology/sphn#Procedure"

HOP_COUNT = 1

ontology_indexer = OntologyIndexer()

classes: list[Class] = ontology_indexer.get_classes(
    "https://biomedit.ch/rdf/sphn-ontology/sphn#", g
)
properties: list[Property] = ontology_indexer.get_properties(
    "https://biomedit.ch/rdf/sphn-ontology/sphn#", g
)

# focus_class: Class | None = None

# for cls in classes:
#     if cls.full_uri == TARGET_CLASS:
#         focus_class = cls
#         break

# if focus_class is None:
#     raise ValueError(f"Class {TARGET_CLASS} not found in ontology")


# relevant_classes: list[Class] = [
# ]
# relevant_properties: list[Property] = []

# visited_classes: set[str] = set()
# visited_properties: set[str] = set()

# queue_classes: queue.Queue[Class] = queue.Queue()

# hop_count = 0
# while hop_count < HOP_COUNT and queue_classes.qsize() > 0:
#     hop_count += 1
#     new_classes: list[Class] = []
#     new_properties: list[Property] = []
#     # For each class in the queue, get their range and domain properties
#     # then get the classes that are related to them and add them to the queue
#     # finally add the classes and properties to the relevant classes and properties
#     cls = queue_classes.get()
#     if cls.full_uri in visited_classes:
#         continue
#     visited_classes.add(cls.full_uri)
#     relevant_classes.append(cls)

#     for prop in properties:
#         if prop.domain == cls.full_uri and prop.full_uri not in visited_properties:
#             visited_properties.add(prop.full_uri)
#             relevant_properties.append(prop)
#             new_classes += [c for c in prop.range if isinstance(c, Class)]
#             new_classes += [c for c in prop.domain if isinstance(c, Class)]
#             new_properties.append(prop)
#         if prop.range == cls.full_uri and prop.full_uri not in visited_properties:
#             visited_properties.add(prop.full_uri)
#             relevant_properties.append(prop)
#             new_classes += [c for c in prop.range if isinstance(c, Class)]
#             new_classes += [c for c in prop.domain if isinstance(c, Class)]
#             new_properties.append(prop)

#     for new_class in new_classes:


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


def bfs_paths_with_n_hops(graph, start, n):
    # Each path element is a tuple (node, predicate)
    queue = deque()
    queue.append((start, [(start, None)]))  # path starts with (node, None)

    all_paths = []

    while queue:
        current, path = queue.popleft()

        if len(path) - 1 == n:
            all_paths.append(path)
            continue

        # Get neighbors if any
        if current in graph:
            for predicate, neighbors in graph[current].items():
                for neighbor in neighbors:
                    if not any(step[0] == neighbor for step in path):  # avoid cycles
                        queue.append((neighbor, path + [(neighbor, predicate)]))

    return all_paths


# Find all paths from 'A' with exactly 2 hops
paths = bfs_paths_with_n_hops(graph_dict, TARGET_CLASS, HOP_COUNT)

# Print the paths
for i, path in enumerate(paths, 1):
    readable = f"{i}. {path[0][0]}"
    for node, pred in path[1:]:
        readable += f" -[{pred}]-> {node}"
    print(readable + "\n")


with open("output.txt", "w", encoding="utf-8") as f:
    for i, path in enumerate(paths, 1):
        readable = f"{i}. {path[0][0]}"
        for node, pred in path[1:]:
            readable += f" -[{pred}]-> {node}"
        f.write(readable + "\n")
