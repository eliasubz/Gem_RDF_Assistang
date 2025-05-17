import csv
import os
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict
from pydantic import BaseModel
import csv
import json


# Load environment variables
load_dotenv()
LLM_API_KEY = os.getenv("POPENAI_API_KEY")


# This is the JSON format for the output of the model
class entity(BaseModel):
    label: str
    iri: str
    description: str

    class Config:
        frozen = True  # makes it immutable and hashable


class Spanning_entity_output(BaseModel):
    spanning_entity_candidates: list[entity]


# === Configuration ===
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\curated_dataset"
)
# INPUT_CSV_FOLDER = r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\raw_data"
# Is the delimiter of the csvs a comma or something else?
CSV_COMMA_DELIMITER = True
OUTPUT_FOLDER = r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\curated_dataset\main_entity_selection"
# OUTPUT_FOLDER = r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\raw_data\main_entity_selection"
ENTITY_FILE = "working_memory/clean_entities.txt"
SEND_TO_API = True  # Change to True if you want to get responses from OpenAI

# Initialize client
client = OpenAI(api_key=LLM_API_KEY)

# ====== BUILDING PROMP ==========


def extract_column_examples_as_string(csv_path, num_examples=3):
    """
    Extracts up to `num_examples` unique non-empty values per column from a CSV file
    and returns a formatted string like:
    column_name -> value1, value2, value3

    Adds a blank line between each entry.
    """
    column_examples = defaultdict(set)

    with open(csv_path, newline="", encoding="utf-8") as f:
        if CSV_COMMA_DELIMITER:
            delim = ","
        else:
            delim = ";"
        reader = csv.DictReader(f, delimiter=delim)

        for row in reader:
            for col, val in row.items():
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                elif not isinstance(val, str):
                    val = str(val)
                val = val.strip()
                if val:
                    column_examples[col].add(val)

            if all(len(v) >= num_examples for v in column_examples.values()):
                break

    # Build the formatted string
    lines = []
    for col, vals in column_examples.items():
        examples = list(vals)[:num_examples]
        lines.append(f"Analyze this column: {col} -> {', '.join(examples)}")

    return "\n".join(lines)


def load_entities(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def build_prompt(csv_path, entities):
    prompt = "Imagine you are an expert in semantic web data integration.\n\n<data>\n"
    prompt += "Find candidate OAEs according to the following table:"
    prompt += "column_name -> value1, value2, value3"
    prompt += (
        "\n<csv columns>\n"
        + extract_column_examples_as_string(csv_path, 3)
        + "\n</csv columns>\n\n"
    )
    prompt += "RDF Entities:\n<rdf_entities>\n"
    prompt += "\n".join(f"- {e}" for e in entities)
    prompt += "\n<rdf_entities>\n</data>\n<Task>\n"
    prompt += "Given a list of CSV column headers and a list of RDF ontology entities, suggest:\n"
    prompt += "1. Is there one overarching entity outside of all the columns, that all columns could be linked to? A table has columns that can be mapped to entities. If we find the overarching entity (OAE) that means that the OAE can be represented with the table and that all column-entities are children notes of that OAE.\n"
    prompt += (
        "2. Give me 15 ranked candidate entities (OAEs) in an json output.\n</Task>\n"
    )
    prompt += (
        "\nHere is one example with only one candidate. I want you to return 15 of those candidates\n<Example>\n"
        + EXAMPLE1
        + "\n</Example>\n"
    )
    return prompt


def save_file(content, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def save_json(response, filepath):
    raw_json = json.loads(response.output_text)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(raw_json, f, indent=4, ensure_ascii=False)


def load_solution_entities(solution_path: str) -> set[str]:
    """
    Reads a solution file where each line is a valid correct entity.
    Returns a set of all correct entity candidates.
    """
    with open(solution_path, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def compute_hit_rate(predictions: list[str], ground_truth: set[str], top_k: int) -> int:
    """
    Computes whether any of the top-k predictions are in the ground truth set.
    Returns 1 if there's a hit, 0 otherwise.
    """
    return int(any(pred in ground_truth for pred in predictions[:top_k]))


# === Main Logic ===
def main():
    rdf_entities = load_entities(ENTITY_FILE)

    for filename in os.listdir(INPUT_CSV_FOLDER):
        if not filename.endswith(".csv"):
            continue

        csv_path = os.path.join(INPUT_CSV_FOLDER, filename)
        prompt = build_prompt(csv_path, rdf_entities)

        base_name = os.path.splitext(filename)[0]
        prompt_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_prompt.txt")
        save_file(prompt, prompt_file)

        print(f"Saved prompt: {prompt_file}")

        if SEND_TO_API:
            try:
                response = client.responses.parse(
                    model="gpt-4.1-mini-2025-04-14",
                    instructions="You are a data integration expert.",
                    input=prompt,
                    text_format=Spanning_entity_output,
                )
                response_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_response.txt")
                # raw_json = json.loads(response.output_text)
                save_json(response, response_file)
                print(f"Saved response: {response_file}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

        # Get the response from the file no matter if the response is fresh or old
        response_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_response.txt")
        with open(response_file, newline="", encoding="utf-8") as f:
            response = f.read()
        # === Compute Hit@5 and Hit@15 ===
        solution_path = os.path.join(INPUT_CSV_FOLDER, "solution", f"{base_name}.txt")
        if os.path.exists(solution_path):
            ground_truth_entities = load_solution_entities(solution_path)

            try:
                # output = Spanning_entity_output.model_validate_json(
                #     response.output_text
                # )
                output = Spanning_entity_output.model_validate_json(response)
                # print(output)

                hit5 = compute_hit_rate(
                    [e.iri for e in output.spanning_entity_candidates],
                    ground_truth_entities,
                    top_k=5,
                )
                hit15 = compute_hit_rate(
                    [e.iri for e in output.spanning_entity_candidates],
                    ground_truth_entities,
                    top_k=15,
                )

                print(f"{base_name}: Hit@5={hit5}, Hit@15={hit15}")

            except Exception as parse_error:
                print(f"Could not parse model output for {base_name}: {parse_error}")
        else:
            print(
                f"No solution file found for {base_name}, skipping hit rate evaluation."
            )


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
]

</output>
"""

LONG_EXAMPLE2 = """An example with a “Measurement” dataset all the rdf_entities were left out
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


if __name__ == "__main__":
    main()
