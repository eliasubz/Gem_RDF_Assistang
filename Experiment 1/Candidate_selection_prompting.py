import os
import json
import csv
from rdflib import Graph, URIRef
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict
from pydantic import BaseModel
from get_subgraph import summarize_entity_subgraphs
from examples import EXAMPLE_SELECTION


load_dotenv()
LLM_API_KEY = os.getenv("POPENAI_API_KEY")


# === Configuration ===
# Folder for curated dataset
# 1. Choose Input folder
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\Data\curated_dataset"
)
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\Data\combined"
)
# 2. Choose Experiment
experiment = "no_refinement\\nano"
experiment = "mini_no_refinement"
experiment = "nano_no_refinement"
experiment = "gpt_no_refinement"
experiment = "mini_no_refinement"
# 3. Review (False) old experiments or conduct (True) new ones
SEND_TO_API = False


CANDIDATE_CREATION_RESPONSES_FOLDER = os.path.join(
    INPUT_CSV_FOLDER, "selection_exp"  # + experiment
)
print(CANDIDATE_CREATION_RESPONSES_FOLDER)
OUTPUT_FOLDER = os.path.join(CANDIDATE_CREATION_RESPONSES_FOLDER, experiment)


# Create the folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
print(f"Output will be saved to: {OUTPUT_FOLDER}\n")


RDF_TTL_PATH = "aidava-sphn-flat.ttl"
TOP_K_LIST = [5, 10, 15]

# Initialize client
client = OpenAI(api_key=LLM_API_KEY) if SEND_TO_API else None


def load_clean_entities(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def load_ground_truths(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


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


def extract_column_examples_as_string(csv_path, num_examples=3):
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
                # Ensure value is a string
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                elif not isinstance(val, str):
                    val = str(val)
                val = val.strip()
                if val:
                    column_examples[col].add(val)

            if all(len(v) >= num_examples for v in column_examples.values()):
                break

    # Build the string output with extra spacing
    lines = []
    for col, vals in column_examples.items():
        examples = list(vals)[:num_examples]
        lines.append(f"{col} -> {', '.join(examples)}")

    return "\n".join(lines)


def build_prompt(csv_path, rdf_candidates, subgraph_lines):

    prompt = f""" 
# RDF Mapping Assistant for Complex Ontological Relationships

## Objective
Given a CSV dataset and a set of `rdf_types`, identify and rank 15 candidate entities that could serve as an overarching main entity (OAE) connecting all column-level entities in a coherent semantic structure.

## Ontology Metadata
- **Ontology Source**: https://biomedit.ch/rdf/sphn-ontology/sphn

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

3. **Output Format:**
   - Provide a ranked list of the 15 best-fitting candidate OAEs in descending order of suitability.
   - For the top 3 candidates, include a brief justification explaining why the entity is a strong semantic fit.


## Input

1. CSV Data:
{extract_column_values_as_string(csv_path, 3)}

2. URIs of Candidate classes you can choose from:

{"\n".join(f"- {e}" for e in rdf_candidates)}



## Additional Notes
- Prioritize semantic accuracy over path length
- Consider domain and range constraints of properties
- Account for cardinality constraints in the ontology
- Flag any columns that may require multiple path options

## Example Format
{EXAMPLE_SELECTION}
       

"""
    # 3. All their respective properties you should base your decision on:

    # {subgraph_lines}

    return prompt


class Spanning_entity_output(BaseModel):
    overarching_spanning_entity: str


def call_llm(prompt):

    response = client.responses.parse(
        model="gpt-4.1-nano",
        instructions="You are a data integration expert.",
        input=prompt,
        text_format=Spanning_entity_output,
    )
    print(response.output_text)
    return response.output_text


def load_solution_entities(solution_path: str) -> set[str]:
    """
    Reads a solution file where each line is a valid correct entity.
    Returns a set of all correct entity candidates.
    """
    with open(solution_path, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def evaluate_accuracy(results):
    correct = sum(
        1
        for r in results
        if r["llm_prediction"] and r["llm_prediction"] in r["ground_truth"]
    )
    return correct / len(results) if results else 0.0


def save_file(content, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def main():

    results = {k: [] for k in TOP_K_LIST}

    for idx, filename in enumerate(os.listdir(CANDIDATE_CREATION_RESPONSES_FOLDER)):
        if not filename.endswith("_response.txt"):
            continue
        with open(
            os.path.join(CANDIDATE_CREATION_RESPONSES_FOLDER, filename),
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        # Remove '_response' from filename but keep '.txt'
        base_name = os.path.splitext(filename)[0].replace("_response", "")

        csv_path = os.path.join(INPUT_CSV_FOLDER, base_name + ".csv")

        # Get solution
        solution_path = os.path.join(INPUT_CSV_FOLDER, "solution", f"{base_name}.txt")
        ground_truth_entity = load_solution_entities(solution_path)
        candidates = data.get("spanning_entity_candidates", [])
        iris = [entry["iri"] for entry in candidates]

        for top_k in TOP_K_LIST:
            print("\nGround Truth: ", ground_truth_entity)
            selected = iris[:top_k]

            subgraph_lines = summarize_entity_subgraphs(RDF_TTL_PATH, selected)
            prompt = build_prompt(csv_path, selected, subgraph_lines)
            prompt_file = os.path.join(
                OUTPUT_FOLDER, f"{base_name}_k{top_k}_prompt.txt"
            )
            response_file = os.path.join(
                OUTPUT_FOLDER, f"{base_name}_k{top_k}_response.txt"
            )
            save_file(prompt, prompt_file)

            try:
                if SEND_TO_API:
                    llm_response = call_llm(prompt)

                    save_file(llm_response, response_file)

            except Exception as e:
                print(f"Error for {filename} with top_k={top_k}: {e}")
                continue
            try:
                with open(response_file, encoding="utf-8") as f:
                    data = json.load(f)
                    llm_response = data.get("overarching_spanning_entity", [])
                print(f"[{filename} | top_k={top_k}] \nLLM pred.: {llm_response}\n")
                results[top_k].append(
                    {
                        "llm_prediction": llm_response,
                        "ground_truth": ground_truth_entity,
                    }
                )
            except Exception as e:
                print("Response file couldnt be opened maybe it doesnt exist yet", e)

    # Show final accuracies
    for k in TOP_K_LIST:
        acc = evaluate_accuracy(results[k])
        print(f"\n✅ Accuracy with top-{k} entity subgraphs: {acc:.2%}")


if __name__ == "__main__":
    main()
