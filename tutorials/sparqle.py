from rdflib import Graph

# Load the flattened TTL file
g = Graph()
g.parse("aidava-sphn-flat.ttl", format="ttl")

# Your (corrected) SPARQL query
query = """
PREFIX : <https://biomedit.ch/rdf/sphn-ontology/sphn#>
PREFIX ex2: <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/>
SELECT DISTINCT ?s ?o
WHERE {
:AdministrativeGender (:|!:)* ?s .
?s <http://www.w3.org/2000/01/rdf-schema#range> ?o .
?o (:|!:)* :ProblemCondition .
}"""

results = g.query(query)

# Print the results
print("Lets print every row")
for row in results:
    print(f"{row.s} --> {row.o}")
