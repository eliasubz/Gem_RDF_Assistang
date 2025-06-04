from rdflib import Graph, URIRef
import re
from collections import defaultdict

# Very bruteforcy way of extracting clean and meaningful entities excluding
# - All those hasProperty-style SPHN props
# - Weird CHOP-like resources
# - OBO: GENO/SO
# - SNOMED CT code
# - classes that appear in less the 4 statements as a subject

# Load graph
g = Graph()
g.parse("aidava-sphn-flat.ttl", format="ttl")


# Dictionaries to count inward and outward connections
outward_counts = defaultdict(int)
inward_counts = defaultdict(int)

# Count inward and outward links
for s, p, o in g:
    if isinstance(s, URIRef):
        if str(s) == "https://biomedit.ch/rdf/sphn-ontology/AIDAVA/OncologyDiagnosis":
            print(s, p, o)
        outward_counts[s] += 1
    if isinstance(o, URIRef):
        inward_counts[o] += 1

# Collect entities with either 3 outward or 3 inward connections
filtered_entities = set()
for entity in set(outward_counts) | set(inward_counts):
    if outward_counts[entity] >= 4:
        if (
            str(entity)
            == "https://biomedit.ch/rdf/sphn-ontology/AIDAVA/OncologyDiagnosis"
        ):
            print(outward_counts[entity])
        filtered_entities.add(entity)

print(outward_counts["https://biomedit.ch/rdf/sphn-ontology/AIDAVA/OncologyDiagnosis"])
print(outward_counts["https://biomedit.ch/rdf/sphn-ontology/sphn#OncologyDiagnosis"])


# Define what to throw into the RDF dumpster
def is_unwanted(uri: URIRef) -> bool:
    uri_str = str(uri)

    return (
        # 1. SPHN has-properties
        uri_str.startswith("https://biomedit.ch/rdf/sphn-ontology/sphn#has")
        or
        ##1.2
        uri_str.startswith("https://biomedit.ch/rdf/sphn-ontology/AIDAVA/has")
        or
        # 2. CHOP & other SPHN resources
        uri_str.startswith("https://biomedit.ch/rdf/sphn-resource/")
        or
        # 3. SNOMED CT codes
        uri_str.startswith("http://snomed.info/id/")
        or
        # 4. OBO GENO or SO codes
        re.match(r"http://purl\.obolibrary\.org/obo/(GENO|SO)_", uri_str)
        or
        # 5. HL7 ActCodes
        uri_str.startswith("http://terminology.hl7.org/CodeSystem/v3-ActCode/")
        or
        # 6. LOINC codes
        uri_str.startswith("https://loinc.org/rdf/")
        or
        # 7. DC terms license
        uri_str == "http://purl.org/dc/terms/license"
    )


# Filter and sort the good stuff
clean_entities = sorted(uri for uri in filtered_entities if not is_unwanted(uri))

# Print the results
# for e in clean_entities:
# print(e)

# Write each clean entity into a new row of a .txt file
with open("working_memory/clean_entities.txt", "w", encoding="utf-8") as file:
    for e in clean_entities:
        file.write(f"{e}\n")
