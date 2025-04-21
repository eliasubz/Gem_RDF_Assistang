from rdflib import Graph, RDF, RDFS, OWL, Namespace

SPHN = Namespace("https://www.biomedit.ch/rdf/sphn-schema/sphn#")

# Create a graph
g = Graph()

# Load your ontology (replace 'your_file.ttl' with your actual file path)
g.parse("aidava-sphn.ttl", format="turtle")
property_types = [
    RDF.Property,
    OWL.ObjectProperty,
    OWL.DatatypeProperty,
    OWL.AnnotationProperty,
    SPHN.Unit,
]

# Collect defined predicates
defined_properties = set()

for ptype in property_types:
    for s in g.subjects(RDF.type, ptype):
        defined_properties.add(s)

# Print all unique predicates
for pred in defined_properties:
    print(pred)


# Define namespaces if needed (adjust prefix as your ontology uses it)
# EX = Namespace("http://your-ontology-namespace#")  # change this!

# SPARQL query to find properties with range hasUnit
query = """
SELECT ?property WHERE {
    ?property rdfs:range ?range .
    FILTER (?range = <https://www.biomedit.ch/rdf/sphn-schema/sphn#hasQuantity>)
}
"""

# Bind rdfs so the query knows about it
g.bind("rdfs", "https://www.biomedit.ch/rdf/sphn-schema/sphn#")

# Execute the query
results = g.query(query)

# Print results
for row in results:
    print("----------")
    print(row.property)

properties_ending_with_Unit = g.predicates(object=SPHN.Unit)
print("Those are unit predicates: ", properties_ending_with_Unit)
# all properties that have an object of value/Unit. -> hasUnit, value is not a class.
# all Nodes that have hasUnit or hasValue.
