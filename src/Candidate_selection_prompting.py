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
# === Prerequisite ===
# base/solution folder that holds the correct entity

# === Configuration ===
# Folder for curated dataset
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\curated_dataset"
)
# Raw data
# INPUT_CSV_FOLDER = r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\raw_data"
# Change this depending on the model
experiment = "/nano"
experiment = ""
OUTPUT_FOLDER = os.path.join(
    INPUT_CSV_FOLDER, "main_entity_candidate_selection" + experiment
)
SEND_TO_API = False  # Change to True if you want to get responses from OpenAI
# INPUT_CSV_FOLDER = r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\raw_data"ENTITY_FILE = "working_memory/clean_entities.txt"
CANDIDATE_CREATION_RESPONSES_FOLDER = os.path.join(
    INPUT_CSV_FOLDER, "main_entity_candidate_creation" + experiment
)


# Create the folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
print(f"Output will not be saved to: {OUTPUT_FOLDER}\n")


# GROUND_TRUTH_PATH = "curated_dataset/solution"

RDF_TTL_PATH = "aidava-sphn-flat.ttl"
TOP_K_LIST = [5, 15]

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
    prompt = (
        "You are an expert in semantic web data integration.\n"
        "Given a list of CSV column headers and a list of RDF ontology entities, and top candidates:\n"
        "1. Which of the following entities could best describe the tabular data provided in the CSV file?\n"
        "Candidates for the main entity:\n"
        "Subgraph with the direct relationships of all candidates:\n"
        "Think about all the relations of the candidates and which entity could best fit all columns in their direct neighbourhood."
        "So if all the columns fit into the relations it is a vrey good fit"
    )
    prompt += "CSV Columns:\n"
    prompt += "\n" + extract_column_examples_as_string(csv_path, 3) + "\n\n"
    prompt += "All entities you can choose from: "
    prompt += "\n".join(f"- {e}" for e in rdf_candidates)
    prompt += "\n\nTheir respective subgraphs:"
    prompt += subgraph_lines
    prompt += (
        "\nHere is one example with only one candidate. I want you to return 15 of those candidates\n<Example>\n"
        + EXAMPLE_SELECTION
        + "\n</Example>\n"
    )

    return prompt


class Spanning_entity_output(BaseModel):
    overarching_spanning_entity: str


def call_llm(prompt):
    response = client.responses.parse(
        model="gpt-4.1-nano-2025-04-14",
        instructions="You are a data integration expert.",
        input=prompt,
        text_format=Spanning_entity_output,
    )
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
        print("\nGround Truth: ", ground_truth_entity)
        candidates = data.get("spanning_entity_candidates", [])
        iris = [entry["iri"] for entry in candidates]

        for top_k in TOP_K_LIST:
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
                print(f"[{filename} | top_k={top_k}] \n LLM pred.: {llm_response}\n")
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
