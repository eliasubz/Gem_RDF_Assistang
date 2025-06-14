# RDF Mapping Assistant for Complex Ontological Relationships

## Objective
Given a CSV dataset and a set of ontology paths rooted in a main entity class, map each column to the most 
semantically appropriate ontology path, producing RDF triples for later use.

## Input
1. Main Entity Type: https://biomedit.ch/rdf/sphn-ontology/sphn#Measurement

2. Available Paths:
{Possible Paths}

3. CSV Data:
{Table}

## Requirements
For each CSV column:
1. Identify the most semantically appropriate path from the main entity through the ontology
2. Select exactly one optimal path for each column
3. Document your reasoning for choosing each path, including any alternatives considered
4. Handle nested relationships and complex datatypes appropriately

### Specific Instructions
Before selecting a 1-hop path, first check if any 2-hop paths that begin from the same end node as that 1-hop path offer a better option. If not, explain why they aren't better before proceeding with the 1-hop path.

## Expected Output
{Expectations of Output}

## Example Format
{Example Output}



For each column, provide:
1. Column number/name
2. The complete selected path using proper ontology notation (e.g., entity:property1/property2/property3) and
 the number of the path that is provided also in the input
3. Brief justification for the selected mapping (1-2 sentences)
4. Any data transformation required (datatype conversion, formatting, etc.)



1. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient)
2. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase)
3. (sphn:Measurement) => [sphn:hasBodySite] => (sphn:BodySite)
4. (sphn:Measurement) => [sphn:hasCode] => (sphn:Code)
5. (sphn:Measurement) => [sphn:hasCode] => (sphn:Terminology)
6. (sphn:Measurement) => [sphn:hasDataDetermination] => (sphn:DataDetermination)
7. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile)
8. (sphn:Measurement) => [sphn:hasDataProviderInstitute] => (sphn:DataProviderInstitute)
9. (sphn:Measurement) => [sphn:hasLabTest] => (sphn:LabTest)
10. (sphn:Measurement) => [sphn:hasMeasurementMethod] => (sphn:MeasurementMethod)
11. (sphn:Measurement) => [sphn:hasMedicalDevice] => (sphn:MedicalDevice)
12. (sphn:Measurement) => [sphn:hasQualitativeResultCode] => (sphn:Code)
13. (sphn:Measurement) => [sphn:hasQualitativeResultCode] => (sphn:Terminology)
14. (sphn:Measurement) => [sphn:hasQuantity] => (sphn:Quantity)
15. (sphn:Measurement) => [sphn:hasReferenceRange] => (sphn:ReferenceRange)
16. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample)
17. (sphn:Measurement) => [sphn:hasSubjectPseudoIdentifier] => (sphn:SubjectPseudoIdentifier)
18. (sphn:Measurement) => [sphn:hasDateTime] => (http://www.w3.org/2001/XMLSchema#dateTime)
19. (sphn:Measurement) => [sphn:hasFreeText] => (http://www.w3.org/2001/XMLSchema#string)
20. (sphn:Measurement) => [sphn:hasMeasurementDateTime] => (http://www.w3.org/2001/XMLSchema#dateTime)
21. (sphn:Measurement) => [sphn:hasQualitativeResult] => (http://www.w3.org/2001/XMLSchema#string)
22. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasAdministrativeGender] => (sphn:AdministrativeGender)
23. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasBirthDate] => (sphn:BirthDate)
24. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasDrugAdministrationEvent] => (sphn:DrugAdministrationEvent)
25. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasDrugPrescription] => (sphn:DrugPrescription)
26. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasPatientIdentifier] => (AIDAVA:PatientIdentifier)
27. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasProblemCondition] => (sphn:ProblemCondition)
28. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasProcedure] => (sphn:Procedure)
29. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasSubjectName] => (AIDAVA:SubjectName)
30. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasAdress] => (http://www.w3.org/2001/XMLSchema#string)
31. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [AIDAVA:hasBirthDateTime] => (http://www.w3.org/2001/XMLSchema#dateTime)
32. (sphn:Measurement) => [AIDAVA:hasPatient] => (AIDAVA:Patient) => [sphn:hasIdentifier] => (http://www.w3.org/2001/XMLSchema#string)
33. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [AIDAVA:hasPatient] => (AIDAVA:Patient)
34. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasCareHandling] => (sphn:CareHandling)
35. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasDataFile] => (sphn:DataFile)
36. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasDataProviderInstitute] => (sphn:DataProviderInstitute)
37. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasDischargeLocation] => (sphn:Location)
38. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasLocation] => (sphn:Location)
39. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasOriginLocation] => (sphn:Location)
40. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasSubjectPseudoIdentifier] => (sphn:SubjectPseudoIdentifier)
41. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasAdmissionDateTime] => (http://www.w3.org/2001/XMLSchema#dateTime)
42. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasDateTime] => (http://www.w3.org/2001/XMLSchema#dateTime)
43. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasDischargeDateTime] => (http://www.w3.org/2001/XMLSchema#dateTime)
44. (sphn:Measurement) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase) => [sphn:hasIdentifier] => (http://www.w3.org/2001/XMLSchema#string)
45. (sphn:Measurement) => [sphn:hasBodySite] => (sphn:BodySite) => [sphn:hasCode] => (sphn:Code)
46. (sphn:Measurement) => [sphn:hasBodySite] => (sphn:BodySite) => [sphn:hasCode] => (sphn:Terminology)
47. (sphn:Measurement) => [sphn:hasBodySite] => (sphn:BodySite) => [sphn:hasLaterality] => (sphn:Laterality)
48. (sphn:Measurement) => [sphn:hasBodySite] => (sphn:BodySite) => [sphn:hasFreeText] => (http://www.w3.org/2001/XMLSchema#string)
49. (sphn:Measurement) => [sphn:hasCode] => (sphn:Code) => [sphn:hasCodingSystemAndVersion] => (http://www.w3.org/2001/XMLSchema#string)
50. (sphn:Measurement) => [sphn:hasCode] => (sphn:Code) => [sphn:hasIdentifier] => (http://www.w3.org/2001/XMLSchema#string)
51. (sphn:Measurement) => [sphn:hasCode] => (sphn:Code) => [sphn:hasName] => (http://www.w3.org/2001/XMLSchema#string)
52. (sphn:Measurement) => [sphn:hasDataDetermination] => (sphn:DataDetermination) => [sphn:hasCode] => (sphn:Code)
53. (sphn:Measurement) => [sphn:hasDataDetermination] => (sphn:DataDetermination) => [sphn:hasCode] => (sphn:Terminology)
54. (sphn:Measurement) => [sphn:hasDataDetermination] => (sphn:DataDetermination) => [sphn:hasMethodCode] => (sphn:Code)
55. (sphn:Measurement) => [sphn:hasDataDetermination] => (sphn:DataDetermination) => [sphn:hasMethodCode] => (sphn:Terminology)
56. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [AIDAVA:hasPatient] => (AIDAVA:Patient)
57. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasCode] => (sphn:Code)
58. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasCode] => (sphn:Terminology)
59. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasDataProviderInstitute] => (sphn:DataProviderInstitute)
60. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasFormatCode] => (sphn:Code)
61. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasFormatCode] => (sphn:Terminology)
62. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasSubjectPseudoIdentifier] => (sphn:SubjectPseudoIdentifier)
63. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasIdentifier] => (http://www.w3.org/2001/XMLSchema#string)
64. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasName] => (http://www.w3.org/2001/XMLSchema#string)
65. (sphn:Measurement) => [sphn:hasDataFile] => (sphn:DataFile) => [sphn:hasUniformResourceIdentifier] => (http://www.w3.org/2001/XMLSchema#string)
66. (sphn:Measurement) => [sphn:hasDataProviderInstitute] => (sphn:DataProviderInstitute) => [sphn:hasCode] => (sphn:Code)
67. (sphn:Measurement) => [sphn:hasDataProviderInstitute] => (sphn:DataProviderInstitute) => [sphn:hasCode] => (sphn:Terminology)
68. (sphn:Measurement) => [sphn:hasDataProviderInstitute] => (sphn:DataProviderInstitute) => [sphn:hasName] => (http://www.w3.org/2001/XMLSchema#string)
69. (sphn:Measurement) => [sphn:hasLabTest] => (sphn:LabTest) => [sphn:hasCode] => (sphn:Code)
70. (sphn:Measurement) => [sphn:hasLabTest] => (sphn:LabTest) => [sphn:hasCode] => (sphn:Terminology)
71. (sphn:Measurement) => [sphn:hasLabTest] => (sphn:LabTest) => [sphn:hasInstrument] => (sphn:LabAnalyzer)
72. (sphn:Measurement) => [sphn:hasLabTest] => (sphn:LabTest) => [sphn:hasTestKit] => (sphn:LabAnalyzer)
73. (sphn:Measurement) => [sphn:hasMeasurementMethod] => (sphn:MeasurementMethod) => [sphn:hasCode] => (sphn:Code)
74. (sphn:Measurement) => [sphn:hasMeasurementMethod] => (sphn:MeasurementMethod) => [sphn:hasCode] => (sphn:Terminology)
75. (sphn:Measurement) => [sphn:hasMedicalDevice] => (sphn:MedicalDevice) => [sphn:hasCode] => (sphn:Code)
76. (sphn:Measurement) => [sphn:hasMedicalDevice] => (sphn:MedicalDevice) => [sphn:hasCode] => (sphn:Terminology)
77. (sphn:Measurement) => [sphn:hasMedicalDevice] => (sphn:MedicalDevice) => [sphn:hasProductCode] => (sphn:Code)
78. (sphn:Measurement) => [sphn:hasMedicalDevice] => (sphn:MedicalDevice) => [sphn:hasProductCode] => (sphn:Terminology)
79. (sphn:Measurement) => [sphn:hasMedicalDevice] => (sphn:MedicalDevice) => [sphn:hasTypeCode] => (sphn:Code)
80. (sphn:Measurement) => [sphn:hasMedicalDevice] => (sphn:MedicalDevice) => [sphn:hasTypeCode] => (sphn:Terminology)
81. (sphn:Measurement) => [sphn:hasQualitativeResultCode] => (sphn:Code) => [sphn:hasCodingSystemAndVersion] => (http://www.w3.org/2001/XMLSchema#string)
82. (sphn:Measurement) => [sphn:hasQualitativeResultCode] => (sphn:Code) => [sphn:hasIdentifier] => (http://www.w3.org/2001/XMLSchema#string)
83. (sphn:Measurement) => [sphn:hasQualitativeResultCode] => (sphn:Code) => [sphn:hasName] => (http://www.w3.org/2001/XMLSchema#string)
84. (sphn:Measurement) => [sphn:hasQuantity] => (sphn:Quantity) => [sphn:hasComparator] => (sphn:SPHNConcept)
85. (sphn:Measurement) => [sphn:hasQuantity] => (sphn:Quantity) => [sphn:hasUnit] => (sphn:Unit)
86. (sphn:Measurement) => [sphn:hasQuantity] => (sphn:Quantity) => [sphn:hasValue] => (http://www.w3.org/2001/XMLSchema#double)
87. (sphn:Measurement) => [sphn:hasQuantity] => (sphn:Quantity) => [sphn:hasValue] => (http://www.w3.org/2001/XMLSchema#string)
88. (sphn:Measurement) => [sphn:hasReferenceRange] => (sphn:ReferenceRange) => [sphn:hasLowerLimit] => (sphn:Quantity)
89. (sphn:Measurement) => [sphn:hasReferenceRange] => (sphn:ReferenceRange) => [sphn:hasQuantity] => (sphn:Quantity)
90. (sphn:Measurement) => [sphn:hasReferenceRange] => (sphn:ReferenceRange) => [sphn:hasUpperLimit] => (sphn:Quantity)
91. (sphn:Measurement) => [sphn:hasReferenceRange] => (sphn:ReferenceRange) => [sphn:hasFreeText] => (http://www.w3.org/2001/XMLSchema#string)
92. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [AIDAVA:hasPatient] => (AIDAVA:Patient)
93. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasAdministrativeCase] => (sphn:AdministrativeCase)
94. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasBodySite] => (sphn:BodySite)
95. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasCode] => (sphn:Code)
96. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasCode] => (sphn:Terminology)
97. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasDataFile] => (sphn:DataFile)
98. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasDataProviderInstitute] => (sphn:DataProviderInstitute)
99. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasFixationType] => (sphn:SPHNConcept)
100. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasMaterialTypeCode] => (sphn:Code)
101. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasMaterialTypeCode] => (sphn:Terminology)
102. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasPrimaryContainer] => (sphn:SPHNConcept)
103. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasSubjectPseudoIdentifier] => (sphn:SubjectPseudoIdentifier)
104. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasCollectionDateTime] => (http://www.w3.org/2001/XMLSchema#dateTime)
105. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasDateTime] => (http://www.w3.org/2001/XMLSchema#dateTime)
106. (sphn:Measurement) => [sphn:hasSample] => (sphn:Sample) => [sphn:hasIdentifier] => (http://www.w3.org/2001/XMLSchema#string)
107. (sphn:Measurement) => [sphn:hasSubjectPseudoIdentifier] => (sphn:SubjectPseudoIdentifier) => [sphn:hasDataProviderInstitute] => (sphn:DataProviderInstitute)
108. (sphn:Measurement) => [sphn:hasSubjectPseudoIdentifier] => (sphn:SubjectPseudoIdentifier) => [sphn:hasIdentifier] => (http://www.w3.org/2001/XMLSchema#string)
