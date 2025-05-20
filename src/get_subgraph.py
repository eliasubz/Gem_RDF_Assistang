from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, XSD

SPHN = Namespace("https://biomedit.ch/rdf/sphn-ontology/sphn#")
AIDAVA = Namespace("https://biomedit.ch/rdf/sphn-ontology/AIDAVA#")


def summarize_entity_subgraphs(input_ttl_path, entity_uris):
    g = Graph()
    g.parse(input_ttl_path, format="ttl")

    summary = []

    for uri in entity_uris:
        entity = URIRef(uri)
        entity_label = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
        entity_section = [f"### Entity: {entity_label}"]

        # Triples where entity is subject
        subject_triples = list(g.triples((entity, None, None)))
        if subject_triples:
            entity_section.append("- As subject:")
            for _, p, o in subject_triples:
                if str(p) == "http://www.w3.org/2000/01/rdf-schema#subClassOf":
                    continue

                entity_section.append(f"  • {entity_label} {shorten(p)} {shorten(o)}")

        # Triples where entity is object
        object_triples = list(g.triples((None, None, entity)))
        if object_triples:
            entity_section.append("- As object:")
            for s, p, _ in object_triples:
                entity_section.append(f"  • {shorten(s)} {shorten(p)} {entity_label}")

        summary.append("\n".join(entity_section))

    return "\n\n".join(summary)


def shorten(uri):
    """Shortens full URIs into prefixed names if possible."""
    if isinstance(uri, URIRef):
        uri = str(uri)
    if uri.startswith(SPHN):
        return f"sphn:{uri.replace(SPHN, '')}"
    elif uri.startswith(AIDAVA):
        return f"aidava:{uri.replace(AIDAVA, '')}"
    elif uri.startswith(str(XSD)):
        return f"xsd:{uri.replace(str(XSD), '')}"
    return f"<{uri}>"


# # Example usage:
# text_summary = summarize_entity_subgraphs(
#     input_ttl_path="aidava-sphn-flat.ttl",
#     entity_uris=[
#         "https://biomedit.ch/rdf/sphn-ontology/sphn#Measurement",
#         "https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Patient",
#         "https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Observation",
#     ],
# )

# print(text_summary)
