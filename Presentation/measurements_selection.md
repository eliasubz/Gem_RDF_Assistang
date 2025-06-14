# RDF Mapping Assistant for Complex Ontological Relationships

## Objective
Given a CSV dataset and a set of `rdf_types`, identify the entity that could best serve as an overarching main entity (OAE) connecting all column-level entities in a coherent semantic structure.

## Task:
1. **Determine the Overarching Main Entity (OAE):**
   - Examine the provided column-level entity candidates and their associated RDF subgraph.
   - Identify whether a single RDF entity could represent the *row* as a whole — that is, an entity for which each column entity can be interpreted as a directly related property, attribute, or part.
   - The OAE should act as the semantic anchor or subject that binds the information from all columns.
2. **Reasoning Criteria:**
   - Think about how each column maps to candidate entities in the ontology.
   - Consider the direct relationships between these candidates and their neighbors in the RDF subgraph.
   - A strong candidate for the OAE will be one that:
     - Has direct or clearly inferred relationships with most or all of the column-level entities.
     - Can semantically contain or contextualize the data represented in the entire row.

## Input
1. CSV Data:
{Table}
2. URIs of Candidate classes you can choose from:
{Candidates}
3. All their respective properties you should base your decision on:
{Refined Candidates}

## Example Format
{Example Output}

<output>
{"overarching_spanning_entity":"https://example.com#Foo"}
</output>

       
- https://biomedit.ch/rdf/sphn-ontology/sphn#LabResult
- https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Observation
- https://biomedit.ch/rdf/sphn-ontology/sphn#Measurement
- https://biomedit.ch/rdf/sphn-ontology/AIDAVA/VitalSigns
- https://biomedit.ch/rdf/sphn-ontology/AIDAVA/DiagnosticReport
- https://biomedit.ch/rdf/sphn-ontology/sphn#LabTest
- https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Procedure
- https://biomedit.ch/rdf/sphn-ontology/sphn#SubjectPseudoIdentifier
- https://biomedit.ch/rdf/sphn-ontology/sphn#SPHNConcept
- https://biomedit.ch/rdf/sphn-ontology/sphn#ProblemCondition
- https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Condition
- https://biomedit.ch/rdf/sphn-ontology/sphn#AdministrativeCase
- https://biomedit.ch/rdf/sphn-ontology/sphn#Sample
- https://biomedit.ch/rdf/sphn-ontology/sphn#SPHNAttributeObject


### Entity: LabResult
- As subject:
  • LabResult <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/hasPatient> <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Patient>
  • LabResult sphn:hasAdministrativeCase sphn:AdministrativeCase
  • LabResult sphn:hasCode sphn:Code
  • LabResult sphn:hasCode sphn:Terminology
  • LabResult sphn:hasDataProviderInstitute sphn:DataProviderInstitute
  • LabResult sphn:hasLabTest sphn:LabTest
  • LabResult sphn:hasQualitativeResultCode sphn:Code
  • LabResult sphn:hasQualitativeResultCode sphn:Terminology
  • LabResult sphn:hasQuantitativeResult sphn:Quantity
  • LabResult sphn:hasQuantity sphn:Quantity
  • LabResult sphn:hasReferenceRange sphn:ReferenceRange
  • LabResult sphn:hasSample sphn:Sample
  • LabResult sphn:hasSubjectPseudoIdentifier sphn:SubjectPseudoIdentifier
  • LabResult sphn:hasComment xsd:string
  • LabResult sphn:hasDateTime xsd:dateTime
  • LabResult sphn:hasQualitativeResult xsd:string
  • LabResult sphn:hasReportDateTime xsd:dateTime

### Entity: Observation

### Entity: Measurement
- As subject:
  • Measurement aidava:hasPatient aidava:Patient
  • Measurement sphn:hasAdministrativeCase sphn:AdministrativeCase
  • Measurement sphn:hasBodySite sphn:BodySite
  • Measurement sphn:hasCode sphn:Code
  • Measurement sphn:hasCode sphn:Terminology
  • Measurement sphn:hasDataDetermination sphn:DataDetermination
  • Measurement sphn:hasDataFile sphn:DataFile
  • Measurement sphn:hasDataProviderInstitute sphn:DataProviderInstitute
  • Measurement sphn:hasLabTest sphn:LabTest
  • Measurement sphn:hasMeasurementMethod sphn:MeasurementMethod
  • Measurement sphn:hasMedicalDevice sphn:MedicalDevice
  • Measurement sphn:hasQualitativeResultCode sphn:Code
  • Measurement sphn:hasQualitativeResultCode sphn:Terminology
  • Measurement sphn:hasQuantity sphn:Quantity
  • Measurement sphn:hasReferenceRange sphn:ReferenceRange
  • Measurement sphn:hasSample sphn:Sample
  • Measurement sphn:hasSubjectPseudoIdentifier sphn:SubjectPseudoIdentifier
  • Measurement sphn:hasDateTime xsd:dateTime
  • Measurement sphn:hasMeasurementDateTime xsd:dateTime
  • Measurement sphn:hasQualitativeResult xsd:string

### Entity: LabTest
- As subject:
  • LabTest sphn:hasCode sphn:Code
  • LabTest sphn:hasCode sphn:Terminology
  • LabTest sphn:hasInstrument sphn:LabAnalyzer
  • LabTest sphn:hasTestKit sphn:LabAnalyzer

### Entity: Procedure

### Entity: SubjectPseudoIdentifier
- As subject:
  • SubjectPseudoIdentifier sphn:hasDataProviderInstitute sphn:DataProviderInstitute
  • SubjectPseudoIdentifier sphn:hasIdentifier xsd:string

### Entity: SPHNConcept

### Entity: ProblemCondition
- As subject:
  • ProblemCondition <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/hasPatient> <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Patient>
  • ProblemCondition <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/interprets> sphn:Measurement
  • ProblemCondition sphn:hasAdministrativeCase sphn:AdministrativeCase
  • ProblemCondition sphn:hasBodySite sphn:BodySite
  • ProblemCondition sphn:hasCode sphn:Code
  • ProblemCondition sphn:hasCode sphn:Terminology
  • ProblemCondition sphn:hasDataFile sphn:DataFile
  • ProblemCondition sphn:hasDataProviderInstitute sphn:DataProviderInstitute
  • ProblemCondition sphn:hasRelativeTemporalityCode sphn:Code
  • ProblemCondition sphn:hasRelativeTemporalityCode sphn:Terminology
  • ProblemCondition sphn:hasStatusCode sphn:Code
  • ProblemCondition sphn:hasStatusCode sphn:Terminology
  • ProblemCondition sphn:hasSubjectPseudoIdentifier sphn:SubjectPseudoIdentifier
  • ProblemCondition sphn:hasDateTime xsd:dateTime
  • ProblemCondition sphn:hasRecordDateTime xsd:dateTime

### Entity: Condition
- As subject:
  • Condition <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/hasConditionCode> sphn:Code
  • Condition sphn:hasFreeText xsd:string
  • Condition sphn:hasOnsetDateTime xsd:dateTime

### Entity: AdministrativeCase
- As subject:
  • AdministrativeCase <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/hasPatient> <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Patient>
  • AdministrativeCase sphn:hasCareHandling sphn:CareHandling
  • AdministrativeCase sphn:hasDataFile sphn:DataFile
  • AdministrativeCase sphn:hasDataProviderInstitute sphn:DataProviderInstitute
  • AdministrativeCase sphn:hasDischargeLocation sphn:Location
  • AdministrativeCase sphn:hasLocation sphn:Location
  • AdministrativeCase sphn:hasOriginLocation sphn:Location
  • AdministrativeCase sphn:hasSubjectPseudoIdentifier sphn:SubjectPseudoIdentifier
  • AdministrativeCase sphn:hasAdmissionDateTime xsd:dateTime
  • AdministrativeCase sphn:hasDateTime xsd:dateTime
  • AdministrativeCase sphn:hasDischargeDateTime xsd:dateTime
  • AdministrativeCase sphn:hasIdentifier xsd:string

### Entity: Sample
- As subject:
  • Sample <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/hasPatient> <https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Patient>
  • Sample sphn:hasAdministrativeCase sphn:AdministrativeCase
  • Sample sphn:hasBodySite sphn:BodySite
  • Sample sphn:hasCode sphn:Code
  • Sample sphn:hasCode sphn:Terminology
  • Sample sphn:hasDataFile sphn:DataFile
  • Sample sphn:hasDataProviderInstitute sphn:DataProviderInstitute
  • Sample sphn:hasFixationType sphn:SPHNConcept
  • Sample sphn:hasMaterialTypeCode sphn:Code
  • Sample sphn:hasMaterialTypeCode sphn:Terminology
  • Sample sphn:hasPrimaryContainer sphn:SPHNConcept
  • Sample sphn:hasSubjectPseudoIdentifier sphn:SubjectPseudoIdentifier
  • Sample sphn:hasCollectionDateTime xsd:dateTime
  • Sample sphn:hasDateTime xsd:dateTime
  • Sample sphn:hasIdentifier xsd:string

### Entity: SPHNAttributeObject