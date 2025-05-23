from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import XSD
from rdflib import Graph, RDF, RDFS, OWL, Namespace


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
        predicates = list(g.triples((None, RDFS.domain, entity)))
        if predicates:
            entity_section.append("- As subject:")
            for predicate, _, _ in predicates:
                objects = list(g.triples((predicate, RDFS.range, None)))
                for _, _, obj in objects:
                    entity_section.append(
                        f"  • {entity_label} {shorten(predicate)} {shorten(obj)}"
                    )

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
