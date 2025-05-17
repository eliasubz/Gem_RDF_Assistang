EXAMPLE1 = """An example with a “Measurement” dataset all the rdf_entities were left out
<input> 
<csv columns>
Analyze this column: row_id -> 2, 4, 1
Analyze this column: patient_id -> PAT00001, PAT00002, PAT00003
Analyze this column: measurement_code -> Z99.89, E11.9, R50.9
Analyze this column: measurement_value -> 56.48, 81.12, 101.93
Analyze this column: measurement_unit -> mm[Hg], mg/dL, /minn
Analyze this column: measurement_date -> 2025-02-17, 2025-01-27, 2025-02-19
</csv columns>
<rdf_entities>
…
</rdf_entities>
<Task>
Now choose and rank 15 of those rdf_entities that could connect/link/subsume all the columns by beeing an entity that has properties that can link to all columns.
<Task>
</input> 
<internal>
We are given a tabular dataset and want to map it to a semantic structure.
The goal is to find one overarching RDF entity (OAE) that connects or subsumes all column values as its attributes or related properties.
<Table_analysis>
row_id : Row identifier, internal index (not semantically meaningful)
Patient_id: eferences a Patient or Subject
Measurement_code: Code of a measured entity (e.g., blood pressure)
Measurement_value: The numerical result of a measurement
Measurement_unit: Unit of the measurement (e.g., mmHg)
Measurement_date: Time at which measurement occurred
</Table_analysis>
<Central Concept>
measurement_code, measurement_value, measurement_unit, and measurement_date — clearly all part of a measurement.
patient_id — identifies who the measurement was taken from.
Therefore, Measurement is the main event or OAE being described.
<Subgraph Reasoning>
:measurement_001 a sphn:Measurement ;
    sphn:hasPatient :patient_001 ;
    sphn:hasCode :Z99.89 ;
    sphn:hasValue "56.48"^^xsd:float ;
    sphn:hasUnit :mmHg ;
    sphn:hasDate "2025-02-17"^^xsd:date .
</Subgraph Reasoning>
<output>
[
  {
    "label": "Measurement",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#Measurement",
    "description": "A quantitative or qualitative measurement made on a subject, typically involving a numeric result."
  },
  {
    "label": "Observation",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#Observation",
    "description": "A measurement or assertion made about a patient."
  },
  {
    "label": "Clinical Finding",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#ClinicalFinding",
    "description": "An observed or measured characteristic relevant to clinical care."
  },
  {
    "label": "Lab Test",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#LabTest",
    "description": "A test conducted in a laboratory setting, producing measurable or observable outcomes."
  },
  {
    "label": "Vital Sign",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#VitalSign",
    "description": "Clinical measurements that indicate the state of a patient's essential bodily functions."
  },
  {
    "label": "Procedure",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#Procedure",
    "description": "An act of care provided to a patient to achieve a specific health outcome."
  },
  {
    "label": "Patient Event",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#PatientEvent",
    "description": "An event that occurs during the course of clinical care involving the patient."
  },
  {
    "label": "Specimen Analysis",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#SpecimenAnalysis",
    "description": "The analysis performed on a biological specimen collected from a patient."
  },
  {
    "label": "Encounter",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#Encounter",
    "description": "An interaction between a patient and healthcare provider(s) for the purpose of providing healthcare service(s)."
  },
  {
    "label": "Health Care Service",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#HealthCareService",
    "description": "A medical, surgical, or other healthcare service provided to a patient."
  },
  {
    "label": "Activity",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#Activity",
    "description": "A clinically relevant action or behavior involving or performed by the patient."
  },
  {
    "label": "Result",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#Result",
    "description": "An outcome derived from a clinical or laboratory procedure or observation."
  },
  {
    "label": "Quantitative Observation",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#QuantitativeObservation",
    "description": "An observation that results in a numeric or quantifiable outcome."
  },
  {
    "label": "Diagnostic Report",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#DiagnosticReport",
    "description": "A report that communicates diagnostic findings derived from observations and procedures."
  },
  {
    "label": "Medical Record Entry",
    "iri": "https://biomedit.ch/rdf/sphn-ontology/sphn#MedicalRecordEntry",
    "description": "An entry in a patient’s medical record documenting observations, diagnoses, procedures, or treatments."
  }
]

</output>
"""
