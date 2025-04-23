from rdflib import Graph, URIRef, RDFS
from collections import deque

# Load the graph
g = Graph()
g.parse("aidava-sphn-flat.ttl", format="ttl")

start = URIRef("https://biomedit.ch/rdf/sphn-ontology/sphn#AdministrativeGender")
end = URIRef("https://biomedit.ch/rdf/sphn-ontology/sphn#ProblemCondition")


def find_paths(graph, start_node, target_node, max_depth=5):
    paths = []
    visited = set()
    queue = deque([(start_node, [start_node])])

    while queue:
        current, path = queue.popleft()
        if current == target_node:
            paths.append(path)
            continue
        if len(path) > max_depth:
            continue

        for p, o in graph.predicate_objects(current):
            if o not in path:
                queue.append((o, path + [p, o]))
        for s, p in graph.subject_predicates(current):
            if s not in path:
                queue.append((s, path + [p, s]))
    return paths


# Query logic:
results = []
for s, o in g.subject_objects(RDFS.range):
    # s = property, o = its range
    if URIRef(o) == end or list(find_paths(g, URIRef(o), end)):
        paths_to_s = find_paths(g, start, s)
        paths_from_o = find_paths(g, o, end)
        results.append((s, o, paths_to_s, paths_from_o))

# Print results
for s, o, paths_to_s, paths_from_o in results:
    print(f"\n🔗 Property: {s}")
    print(f"   ↪ Range: {o}")
    if paths_to_s:
        print("   🧭 Shortest path(s) from :AdministrativeGender to property:")
        for path in paths_to_s[:3]:  # Show only top 3 shortest
            print("     " + " → ".join(str(x) for x in path))
    else:
        print("   🧭 No path from :AdministrativeGender to this property.")

    if paths_from_o:
        print("   🧭 Shortest path(s) from range to :ProblemCondition:")
        for path in paths_from_o[:3]:
            print("     " + " → ".join(str(x) for x in path))
    else:
        print("   🧭 No path from range to :ProblemCondition.")
