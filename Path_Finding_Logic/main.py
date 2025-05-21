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

        # final_path = ""
        # for hops in range(hop_count):
        #     hops += 1
        #     paths = bfs_paths_with_n_hops(self.graph_dict, target_class, hops)

        #     path_string = ""
        #     for i, path in enumerate(paths, 1):
        #         output = f"{i}. "
        #         for _, (node, pred) in enumerate(path):
        #             if pred is not None:
        #                 output += f" => [{pred}] => "
        #             output += f"({node})"
        #         path_string += "\n" + output
        #     final_path += "\n" + path_string

        final_path = ""
        global_counter = 1  # Persistent counter across all hops

        for hops in range(1, hop_count + 1):  # cleaner: start at 1
            paths = bfs_paths_with_n_hops(self.graph_dict, target_class, hops)

            path_string = ""
            for path in paths:
                output = f"{global_counter}. "
                for idx, (node, pred) in enumerate(path):
                    if pred is not None:
                        output += f" => [{pred}] => "
                    output += f"({node})"
                path_string += "\n" + output
                global_counter += 1  # Increment after each full path

            final_path += "\n" + path_string

        if save_to_file:
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(path_string + "\n")

        return final_path
