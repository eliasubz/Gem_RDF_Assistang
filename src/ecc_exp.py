import csv
import os
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()
LLM_API_KEY = os.getenv("POPENAI_API_KEY")

# === Configuration ===
INPUT_CSV_FOLDER = (
    r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\curated_dataset"
)
OUTPUT_FOLDER = r"C:\Users\elias\Documents\ANI\Bachelor_Baby\llm_assistant\curated_dataset\main_entity_selection"
ENTITY_FILE = "working_memory/clean_entities.txt"
SEND_TO_API = True  # Change to True if you want to get responses from OpenAI

# Initialize client
client = OpenAI(api_key=LLM_API_KEY)

import csv
from collections import defaultdict


import csv
from collections import defaultdict


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


def load_entities(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def build_prompt(csv_path, entities):
    prompt = "You are an expert in semantic web data integration.\n"
    prompt += "Given a list of CSV column headers and a list of RDF ontology entities, suggest:\n"
    prompt += "1. Is there one overarching entity outside of all the columns, that all columns could be linked to? If yes, which entity out of the RDF Entities could that be?\n"
    prompt += "2. Give me 15 candidate entities in an array.\n\n"
    prompt += "CSV file with three example values:"
    prompt += "\n" + extract_column_examples_as_string(csv_path, 3) + "\n\n"
    prompt += "RDF Entities:\n"
    prompt += "\n".join(f"- {e}" for e in entities)
    return prompt


def save_file(content, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


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
                response = client.responses.create(
                    model="gpt-4.1",
                    instructions="You are a data integration expert.",
                    input=prompt,
                )
                response_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_response.txt")
                save_file(response.output_text, response_file)
                print(f"Saved response: {response_file}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    main()
