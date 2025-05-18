import os
import json
import csv
from rdflib import Graph, URIRef
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict
from pydantic import BaseModel
from get_subgraph import summarize_entity_subgraphs


load_dotenv()
OPENAI_API_KEY = os.getenv("POPENAI_API_KEY")
# Initialize client
client = OpenAI(api_key=OPENAI_API_KEY)

GROUND_TRUTH_PATH = "curated_dataset/solution"
RESPONSES_FOLDER = "curated_dataset/main_entity_selection"
RDF_TTL_PATH = "aidava-sphn-flat.ttl"
CLEAN_ENTITIES_PATH = "working_memory/clean_entities.txt"
# === Configuration ===
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\curated_dataset"
)


TOP_K_LIST = [5, 15]


from rdflib import Graph, URIRef


def extract_subgraph(entity_uris, ttl_path):
    g = Graph()
    g.parse(ttl_path, format="ttl")

    subgraph = Graph()
    for uri in entity_uris:
        ref = URIRef(uri)
        for s, p, o in g.triples((ref, None, None)):
            subgraph.add((s, p, o))
        for s, p, o in g.triples((None, None, ref)):
            subgraph.add((s, p, o))

    return [
        line.strip()
        for line in subgraph.serialize(format="turtle").splitlines()
        if line.strip()
    ]


def load_clean_entities(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def load_ground_truths(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def extract_column_examples_as_string(csv_path, num_examples=3):
    """
    Extracts up to `num_examples` unique non-empty values per column from a CSV file
    and returns a formatted string like:
    column_name -> value1, value2, value3

    Adds a blank line between each entry.
    """
    column_examples = defaultdict(set)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")  # ← Set correct delimiter
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


def build_prompt(csv_path, entities, subgraph_lines):
    prompt = (
        "You are an expert in semantic web data integration.\n"
        "Given a list of CSV column headers and a list of RDF ontology entities, and five top candidates:\n"
        "1. Which of the following entities could best describe the tabular data provided in the CSV file?\n"
        "Candidates for the main entity:\n"
        "Subgraph with the direct relationships of all candidates:\n"
    )
    for ttl in subgraph_lines:
        prompt += f"- {ttl}\n"
    prompt += "CSV Columns:\n"
    prompt += "\n" + extract_column_examples_as_string(csv_path, 3) + "\n\n"
    prompt += "\nRDF Entities:\n"
    for e in entities:
        prompt += f"- {e}\n"
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


def main():
    rdf_entities = load_clean_entities(CLEAN_ENTITIES_PATH)

    results = {k: [] for k in TOP_K_LIST}

    for idx, filename in enumerate(os.listdir(RESPONSES_FOLDER)):
        if not filename.endswith("_response.txt"):
            continue
        with open(os.path.join(RESPONSES_FOLDER, filename), encoding="utf-8") as f:
            data = json.load(f)

        # Remove '_response' from filename but keep '.txt'
        base_name = os.path.splitext(filename)[0].replace("_response", "")

        csv_path = os.path.join(INPUT_CSV_FOLDER, base_name + ".csv")

        # Get solution
        solution_path = os.path.join(INPUT_CSV_FOLDER, "solution", f"{base_name}.txt")
        ground_truth_entities = load_solution_entities(solution_path)
        candidates = data.get("spanning_entity_candidates", [])
        iris = [entry["iri"] for entry in candidates]

        for top_k in TOP_K_LIST:
            selected = iris[:top_k]
            print(selected, "\nI hope this orked!!!")
            subgraph_lines = summarize_entity_subgraphs(RDF_TTL_PATH, selected)
            prompt = build_prompt(csv_path, rdf_entities, subgraph_lines)
            try:
                llm_response = call_llm(prompt)
                print(f"[{filename} | top_k={top_k}] LLM predicted: {llm_response}")
                results[top_k].append(
                    {
                        "llm_prediction": llm_response,
                        "ground_truth": ground_truth_entities,
                    }
                )
            except Exception as e:
                print(f"Error for {filename} with top_k={top_k}: {e}")
                continue

    # Show final accuracies
    for k in TOP_K_LIST:
        acc = evaluate_accuracy(results[k])
        print(f"\n✅ Accuracy with top-{k} entity subgraphs: {acc:.2%}")


if __name__ == "__main__":
    main()
