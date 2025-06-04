import csv
import os
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict
from pydantic import BaseModel
import csv
import json
from examples import EXAMPLE_CREATION


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


# === Prerequisite ===
# base/solution folder that holds the correct entity

# === Configuration ===
experiment = "\\gpt"
experiment = "\\mini"
experiment = "\\nano"
# experiment = ""
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\Data\raw_data"
)
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\Data\curated_dataset"
)
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\Data\combined"
)
# Change this depending on the model
OUTPUT_FOLDER = os.path.join(
    INPUT_CSV_FOLDER, "main_entity_candidate_creation" + experiment
)
SEND_TO_API = True  # Change to True if you want to get responses from OpenAI
ENTITY_FILE = "working_memory/clean_entities.txt"


# Create the folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(INPUT_CSV_FOLDER, exist_ok=True)

print(f"Output will be saved to: {OUTPUT_FOLDER}")


# Initialize client
client = OpenAI(api_key=LLM_API_KEY) if SEND_TO_API else None

# ====== BUILDING PROMP ==========


def detect_csv_delimiter(file_path, num_lines=5):
    """
    Detect whether the CSV file uses ';' or ',' as delimiter.
    Checks the first `num_lines` of the file.
    """
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        sample = [csvfile.readline() for _ in range(num_lines)]
        semicolon_count = sum(line.count(";") for line in sample)
        comma_count = sum(line.count(",") for line in sample)

        if semicolon_count > comma_count:
            return ";"
        else:
            return ","


def extract_column_values_as_string(csv_path, num_examples=3):
    """
    Extracts up to `num_examples` unique non-empty values per column from a CSV file
    and returns a Markdown table string:

    ### CSV Data (Preview)

    | Column Name | Example Values          |
    |-------------|-------------------------|
    | patient_id  | 129342KW, 98765XY, ...  |
    | id          | L3335, L3336, L3337     |
    | ...         | ...                     |
    """
    column_examples = defaultdict(set)

    with open(csv_path, newline="", encoding="utf-8") as f:
        delim = detect_csv_delimiter(csv_path)
        reader = csv.DictReader(f, delimiter=delim)

        for row in reader:
            for col, val in row.items():
                if val and val.strip():
                    column_examples[col].add(val.strip())
            # Stop if we have enough examples for all columns
            if all(len(v) >= num_examples for v in column_examples.values()):
                break

    # Build markdown table string
    lines = []
    lines.append("### CSV Data (Preview)\n")
    lines.append("| Column Name | Example Values |")
    lines.append("|-------------|----------------|")

    for col, vals in column_examples.items():
        examples = list(vals)[:num_examples]
        example_str = ", ".join(examples)
        lines.append(f"| {col} | {example_str} |")

    return "\n".join(lines)


def extract_column_examples_as_string(csv_path, num_examples=1):
    """
    Extracts up to `num_examples` unique non-empty values per column from a CSV file
    and returns a formatted string like:
    column_name -> value1, value2, value3

    Adds a blank line between each entry.
    """
    column_examples = defaultdict(set)

    with open(csv_path, newline="", encoding="utf-8") as f:

        delim = detect_csv_delimiter(csv_path)
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

    prompt = f"""# RDF Mapping Assistant for Complex Ontological Relationships
    
## Objective
Given a CSV dataset and a set of rdf_types, choose 15 candidates to act as a mainentity connecting all column entity.

## Ontology Metadata
- **Ontology Source**: https://biomedit.ch/rdf/sphn-ontology/sphn

## Input

1. CSV Data:

{extract_column_values_as_string(csv_path, 3)}


2. Possible Classes:
{"\n".join(f"- {e}" for e in entities)}

## Task:

1. Analyze whether there is a single overarching entity (OAE) that could represent the entire table. The OAE is a conceptual class or entity that all individual column-level entities could be associated with as sub-properties, attributes, or relations. In other words, the table rows could be instances of this overarching entity, and the columns would correspond to its features or components.

2. Based on the list of ontology entities, suggest 15 ranked candidate OAEs in descending order of relevance or appropriateness.

## Additional Notes
- Prioritize semantic accuracy over path length
- Consider domain and range constraints of properties
- Account for cardinality constraints in the ontology
- Flag any columns that may require multiple path options


   
## Example Format
{EXAMPLE_CREATION}
        """

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
    # Initialize lists to store Hit@k values
    hit1_scores = []
    hit5_scores = []
    hit15_scores = []

    for filename in os.listdir(INPUT_CSV_FOLDER):

        if not filename.endswith(".csv"):
            continue

        csv_path = os.path.join(INPUT_CSV_FOLDER, filename)
        prompt = build_prompt(csv_path, rdf_entities)

        base_name = os.path.splitext(filename)[0]
        prompt_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_prompt.txt")
        save_file(prompt, prompt_file)

        if SEND_TO_API:
            try:
                response = client.responses.parse(
                    model="gpt-4.1-nano",
                    instructions="You are a data integration expert.",
                    input=prompt,
                    text_format=Spanning_entity_output,
                )
                response_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_response.txt")
                # raw_json = json.loads(response.output_text)
                save_json(response, response_file)
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
                hit1 = compute_hit_rate(
                    [e.iri for e in output.spanning_entity_candidates],
                    ground_truth_entities,
                    top_k=1,
                )
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
                # Store results
                hit1_scores.append(hit1)
                hit5_scores.append(hit5)
                hit15_scores.append(hit15)
                print(f"{base_name}: Hit@1={hit1}, Hit@5={hit5}, Hit@15={hit15}")

            except Exception as parse_error:
                print(f"Could not parse model output for {base_name}: {parse_error}")
        else:
            print(
                f"No solution file found for {base_name}, skipping hit rate evaluation."
            )
    print("Done")
    # Compute average hit rates
    avg_hit1 = sum(hit1_scores) / len(hit1_scores) if hit1_scores else 0
    avg_hit5 = sum(hit5_scores) / len(hit5_scores) if hit5_scores else 0
    avg_hit15 = sum(hit15_scores) / len(hit15_scores) if hit15_scores else 0

    # Print or save the results
    print(f"Average Hit@1: {avg_hit1:.2f}")
    print(f"Average Hit@5: {avg_hit5:.2f}")
    print(f"Average Hit@15: {avg_hit15:.2f}")


if __name__ == "__main__":
    main()
