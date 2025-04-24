from rdflib import Graph, URIRef


def extract_entity_subgraph(input_ttl_path, entity_uris):
    """
    Extracts all triples where the given entity appears as subject or object,
    and writes them to a new TTL file.

    Parameters:
        input_ttl_path (str): Path to the input Turtle (.ttl) file.
        entity_uri (str): URI of the entity to extract the subgraph for.
        output_ttl_path (str): Path to save the extracted subgraph TTL file.
    """
    output_ttl_path = "working_memory/subgraph.ttl"
    g = Graph()
    g.parse(input_ttl_path, format="ttl")

    subgraph = Graph()

    for entity_uri in entity_uris:
        entity = URIRef(entity_uri)

        # Triples where entity is subject
        for s, p, o in g.triples((entity, None, None)):
            subgraph.add((s, p, o))

        # Triples where entity is object
        for s, p, o in g.triples((None, None, entity)):
            subgraph.add((s, p, o))

        # Optionally: Add labels or related resources if needed

    # Serialize to TTL
    subgraph.serialize(destination=output_ttl_path, format="turtle")
    print(f"Subgraph with entity '{entity_uris}' written to '{output_ttl_path}'")


extract_entity_subgraph(
    input_ttl_path="aidava-sphn-flat.ttl",
    entity_uris=[
        "https://biomedit.ch/rdf/sphn-ontology/sphn#Measurement",
        "https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Patient",
        "https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Observation",
    ],
)
