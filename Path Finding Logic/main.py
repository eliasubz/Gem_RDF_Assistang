from collections import deque
from pathlib import Path
from rdflib import Graph
from .models import Class, Property
from .ontology_indexer import OntologyIndexer


class PathFinder:
    def __init__(self, ttl_file: Path):
        self.graph = Graph()
        self.graph.parse(str(ttl_file), format="turtle")
        self.ontology_indexer = OntologyIndexer()
        self.classes = self.ontology_indexer.get_classes(
            "https://biomedit.ch/rdf/sphn-ontology/sphn#", self.graph
        )
        self.properties = self.ontology_indexer.get_properties(
            "https://biomedit.ch/rdf/sphn-ontology/sphn#", self.graph
        )
        self.graph_dict = self._build_graph_dict()

    def _build_graph_dict(self) -> dict[str, dict[str, list[str]]]:
        graph_dict = {}
        for cls in self.classes:
            property_dict = {}
            for prop in self.properties:
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

    def find_paths(self, hop_count: int, target_class: str, save_to_file: bool = False):
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
                            if not any(step[0] == neighbor for step in path):
                                queue.append((neighbor, path + [(neighbor, predicate)]))
            return all_paths

        paths = bfs_paths_with_n_hops(self.graph_dict, target_class, hop_count)

        if save_to_file:
            with open("output.txt", "w", encoding="utf-8") as f:
                for i, path in enumerate(paths, 1):
                    readable = f"{i}. {path[0][0]}"
                    for node, pred in path[1:]:
                        readable += f" -[{pred}]-> {node}"
                    f.write(readable + "\n")

        return paths
