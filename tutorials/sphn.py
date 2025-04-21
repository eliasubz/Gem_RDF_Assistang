from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS  # Import common namespaces

# --- Configuration ---
# !! IMPORTANT: Replace with the actual path to your downloaded SPHN ontology file !!
ONTOLOGY_FILE = "aidava-sphn.ttl"  # Or "/path/to/your/sphn_ontology.ttl"
ONTOLOGY_FORMAT = "turtle"  # Or "xml" if you downloaded the RDF/XML version

# Define the SPHN namespace
SPHN = Namespace("https://www.biomedit.ch/rdf/sphn-schema/sphn#")


# --- Helper Function to Print Resource Details ---
def print_resource_details(graph, resource_uri):
    """Prints common details (label, comment, type) for a given resource URI."""
    if not isinstance(resource_uri, URIRef):
        print(f"  Error: Expected a URIRef, got {type(resource_uri)}")
        return

    print("Outgoing edges")
    for p in g.predicates(subject=resource_uri, unique=False):
        print(p)

    print("Incoming edges")
    for p in g.predicates(object=resource_uri, unique=False):
        print(p)

    # label = graph.label(resource_uri)
    comment = graph.value(subject=resource_uri, predicate=RDFS.comment)
    # Also try skos:prefLabel which SPHN might use
    if not label:
        label = graph.value(subject=resource_uri, predicate=SKOS.prefLabel)

    types = list(graph.objects(subject=resource_uri, predicate=RDF.type))

    print(f"  URI: {resource_uri}")
    if label:
        print(f"  Label: {label}")
    if comment:
        print(f"  Comment: {comment}")
    if types:
        type_labels = [graph.label(t) or t.split("#")[-1].split("/")[-1] for t in types]
        print(f"  RDF Type(s): {', '.join(type_labels)}")
    print("-" * 20)


# --- Core Ontology Exploration Functions ---


def load_ontology(file_path, file_format="turtle"):
    """Loads the ontology file into an RDFLib Graph."""
    print(f"Loading ontology from: {file_path} (format: {file_format})")
    g = Graph()
    try:
        g.parse(file_path, format=file_format)
        # Bind the SPHN namespace for cleaner output/queries if needed
        g.bind("sphn", SPHN)
        g.bind("rdfs", RDFS)
        g.bind("owl", OWL)
        g.bind("skos", SKOS)
        print(f"Ontology loaded successfully. Contains {len(g)} triples.")
        return g
    except FileNotFoundError:
        print(f"Error: Ontology file not found at '{file_path}'")
        return None
    except Exception as e:
        print(f"Error parsing ontology file: {e}")
        return None


def get_direct_subclasses(graph, class_uri):
    """Finds direct subclasses (children) of a given class URI."""
    if not isinstance(class_uri, URIRef):
        class_uri = URIRef(class_uri)  # Ensure it's a URIRef

    subclasses = set()
    # Find subjects that have rdfs:subClassOf pointing to the given class_uri
    for sub in graph.subjects(predicate=RDFS.subClassOf, object=class_uri):
        # Avoid blank nodes and the class itself if it's self-referential in some odd way
        if isinstance(sub, URIRef) and sub != class_uri:
            subclasses.add(sub)
    return subclasses


def get_direct_superclasses(graph, class_uri):
    """Finds direct superclasses (parents) of a given class URI."""
    if not isinstance(class_uri, URIRef):
        class_uri = URIRef(class_uri)  # Ensure it's a URIRef

    superclasses = set()
    # Find objects pointed to by rdfs:subClassOf from the given class_uri
    for sup in graph.objects(subject=class_uri, predicate=RDFS.subClassOf):
        # Avoid blank nodes and owl:Thing unless explicitly desired
        if isinstance(sup, URIRef) and sup != OWL.Thing and sup != class_uri:
            superclasses.add(sup)
    return superclasses


def get_properties_with_domain(graph, class_uri):
    """
    Finds properties that explicitly list the given class_uri in their rdfs:domain.
    Note: This does NOT account for domain inheritance from superclasses.
    """
    if not isinstance(class_uri, URIRef):
        class_uri = URIRef(class_uri)

    properties = set()
    # Find subjects (properties) that have rdfs:domain pointing to the class_uri
    for prop in graph.subjects(predicate=RDFS.domain, object=class_uri):
        # Ensure it's actually defined as a property type
        if (
            (prop, RDF.type, OWL.ObjectProperty) in graph
            or (prop, RDF.type, OWL.DatatypeProperty) in graph
            or (prop, RDF.type, RDF.Property) in graph
        ):
            properties.add(prop)
    return properties


def get_properties_with_range(graph, class_uri):
    """
    Finds properties that explicitly list the given class_uri in their rdfs:range.
    Note: Does not account for range inheritance.
    """
    if not isinstance(class_uri, URIRef):
        class_uri = URIRef(class_uri)

    properties = set()
    # Find subjects (properties) that have rdfs:range pointing to the class_uri
    for prop in graph.subjects(predicate=RDFS.range, object=class_uri):
        # Ensure it's actually defined as a property type
        if (
            (prop, RDF.type, OWL.ObjectProperty) in graph
            or (prop, RDF.type, OWL.DatatypeProperty) in graph
            or (prop, RDF.type, RDF.Property) in graph
        ):
            properties.add(prop)
    return properties


def get_property_details(graph, property_uri):
    """Gets domain, range, label, comment for a property URI."""
    if not isinstance(property_uri, URIRef):
        property_uri = URIRef(property_uri)

    details = {
        "uri": property_uri,
        "label": graph.label(property_uri)
        or graph.value(subject=property_uri, predicate=SKOS.prefLabel),
        "comment": graph.value(subject=property_uri, predicate=RDFS.comment),
        "types": list(graph.objects(subject=property_uri, predicate=RDF.type)),
        "domains": list(graph.objects(subject=property_uri, predicate=RDFS.domain)),
        "ranges": list(graph.objects(subject=property_uri, predicate=RDFS.range)),
    }
    return details


def find_all_classes(graph):
    """Finds all named OWL Classes and RDFS Classes in the graph."""
    classes = set()
    for s in graph.subjects(predicate=RDF.type, object=OWL.Class):
        if isinstance(s, URIRef):
            classes.add(s)
    for s in graph.subjects(predicate=RDF.type, object=RDFS.Class):
        if isinstance(s, URIRef):
            classes.add(s)
    # Filter out OWL built-ins if desired
    classes = {c for c in classes if not str(c).startswith(str(OWL))}
    return classes


def find_all_properties(graph):
    """Finds all named OWL ObjectProperties and DatatypeProperties."""
    properties = set()
    for s in graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty):
        if isinstance(s, URIRef):
            properties.add(s)
    for s in graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty):
        if isinstance(s, URIRef):
            properties.add(s)
    # Also include basic rdf:Property? Maybe not necessary if OWL is used consistently.
    # for s in graph.subjects(predicate=RDF.type, object=RDF.Property):
    #     if isinstance(s, URIRef):
    #         properties.add(s)
    return properties


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Load the ontology
    g = load_ontology(ONTOLOGY_FILE, ONTOLOGY_FORMAT)

    if g:
        # 2. Define some example SPHN URIs to explore
        #    (Replace these with others if you like)
        admin_case_uri = SPHN.AdministrativeCase
        print(admin_case_uri)
        consent_uri = SPHN.Consent
        procedure_uri = SPHN.Procedure
        bodysite_uri = SPHN.BodySite
        has_admin_case_prop_uri = SPHN.hasAdministrativeCase  # Example property

        # print(g.all_nodes)
        print(g.__class__)
        for s, p, o in g.predicates(object=SPHN.Unit):
            print()
            print(s, p, o)
        # 3. Demonstrate the functions
        # Create a Graph
        h = Graph()

        # Parse in an RDF file hosted on the Internet
        h.parse("http://www.w3.org/People/Berners-Lee/card")
        print(h.serialize(format="turtle"))

        print("\n=== Example: Exploring AdministrativeCase ===")
        print("Admin URI: ", admin_case_uri)

        print_resource_details(g, admin_case_uri)

        g.absolutize()

        print(f"\nDirect Superclasses of {g.label(admin_case_uri)}:")
        superclasses = get_direct_superclasses(g, admin_case_uri)
        if superclasses:
            for sup in sorted(superclasses):
                print_resource_details(g, sup)
        else:
            print("  None found (or only owl:Thing).")

        print(f"\nDirect Subclasses of {g.label(admin_case_uri)}:")
        subclasses = get_direct_subclasses(g, admin_case_uri)
        if subclasses:
            for sub in sorted(subclasses):
                print_resource_details(g, sub)
        else:
            print("  None found.")

        print(f"\nProperties with explicit rdfs:domain = {g.label(admin_case_uri)}:")
        props_domain = get_properties_with_domain(g, admin_case_uri)
        if props_domain:
            for prop in sorted(props_domain):
                print_resource_details(g, prop)
        else:
            print(
                "  None found (check superclasses or OWL restrictions for inherited properties)."
            )

        print(f"\nProperties with explicit rdfs:range = {g.label(admin_case_uri)}:")
        props_range = get_properties_with_range(g, admin_case_uri)
        if props_range:
            for prop in sorted(props_range):
                print_resource_details(g, prop)
        else:
            print("  None found.")

        print("\n=== Example: Exploring hasAdministrativeCase Property ===")
        prop_details = get_property_details(g, has_admin_case_prop_uri)
        print(f"Details for: {prop_details.get('label') or has_admin_case_prop_uri}")
        print(f"  URI: {prop_details['uri']}")
        print(f"  Comment: {prop_details.get('comment', 'N/A')}")
        print(f"  Types: {[g.label(t) or t for t in prop_details.get('types', [])]}")
        print(
            f"  Explicit Domains: {[g.label(d) or d for d in prop_details.get('domains', [])]}"
        )
        print(
            f"  Explicit Ranges: {[g.label(r) or r for r in prop_details.get('ranges', [])]}"
        )
        print("-" * 20)

        # --- Optional: List all classes/properties (can be long!) ---
        # print("\n=== Listing All Found Classes (Sample) ===")
        # all_classes = find_all_classes(g)
        # print(f"Found {len(all_classes)} classes.")
        # for cls_uri in sorted(list(all_classes))[:15]: # Print first 15 sorted
        #     print(f" - {g.label(cls_uri) or cls_uri}")

        # print("\n=== Listing All Found Properties (Sample) ===")
        # all_props = find_all_properties(g)
        # print(f"Found {len(all_props)} properties.")
        # for prop_uri in sorted(list(all_props))[:15]: # Print first 15 sorted
        #     print(f" - {g.label(prop_uri) or prop_uri}")

    else:
        print("Could not load ontology. Exiting.")
