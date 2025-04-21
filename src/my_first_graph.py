import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

# Load data
df = pd.read_csv("measurements.csv")

# Namespaces
AIDAVA = Namespace("https://rdf.aidava.eu/resource/")
UCUM = Namespace("https://biomedit.ch/rdf/sphn-resource/ucum/")
ICD10 = Namespace("https://biomedit.ch/rdf/sphn-resource/icd-10-gm/")
SPHN = Namespace("https://biomedit.ch/rdf/sphn-ontology/sphn#")
AIDAVA_ONT = Namespace("https://biomedit.ch/rdf/sphn-ontology/AIDAVA/")

# Create graph
g = Graph()
g.bind("aidava", AIDAVA)
g.bind("ucum", UCUM)
g.bind("icd-10", ICD10)
g.bind("sphn", SPHN)
g.bind("aidava-ont", AIDAVA_ONT)

# Iterate through rows and build RDF triples
for _, row in df.iterrows():
    row_id = str(row["row_id"])
    patient_id = str(row["patient_id"])
    measurement_uri = AIDAVA[f"measurement/{row_id}"]
    quantity_uri = AIDAVA[f"measurement/quantity/{row_id}"]

    # Measurement
    g.add((measurement_uri, RDF.type, SPHN.Measurement))
    g.add((measurement_uri, AIDAVA_ONT.hasPatient, AIDAVA[f"patient/{patient_id}"]))
    g.add((measurement_uri, SPHN.hasCode, ICD10[str(row["measurement_code"])]))
    g.add(
        (
            measurement_uri,
            SPHN.hasMeasurementDateTime,
            Literal(row["measurement_date"], datatype=XSD.dateTime),
        )
    )
    g.add((measurement_uri, SPHN.hasQuantity, quantity_uri))

    # Quantity
    g.add((quantity_uri, RDF.type, SPHN.Quantity))
    g.add((quantity_uri, SPHN.hasUnit, UCUM[str(row["measurement_unit"])]))
    g.add(
        (
            quantity_uri,
            SPHN.hasValue,
            Literal(float(row["measurement_value"]), datatype=XSD.double),
        )
    )

# Serialize
g.serialize(destination="output.ttl", format="turtle")
print("RDF knowledge graph written to output.ttl")
