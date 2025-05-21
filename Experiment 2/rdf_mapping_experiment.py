import os
import csv
from pathlib import Path
from typing import Dict, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import sys
import os
from pydantic import BaseModel
from typing import List
import json
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm_assistant_hack_main.main import PathFinder


# JSON output schema
class SemanticPath(BaseModel):
    source_entity: str  # e.g., "Measurement"
    target_entity: str  # e.g., "AIDAVA/Patient"
    predicate: str  # e.g., "https://biomedit.ch/rdf/sphn-ontology/AIDAVA/hasPatient"
    path_id: int  # e.g., 1 for "Path 1"


class ColumnSemanticMapping(BaseModel):
    column_name: str  # e.g., "patient_id"
    path: SemanticPath  # semantic path info
    justification: str  # explanation of path choice
    transformation: str  # transformation rule for data values


class ColumnPathSelectionOutput(BaseModel):
    column_mappings: List[ColumnSemanticMapping]


# This is the second variation of output so that we have more of a chain of though output
class ColumnReasoning(BaseModel):
    column_name: str
    justification: str  # Step-by-step reasoning for path selection
    transformation: str  # Optional: data preprocessing step
    selected_path: str  # Final path identifier (e.g., "Path 1")


class ColumnReasoningOutput(BaseModel):
    column_paths: list[ColumnReasoning]


# Load environment variables
load_dotenv()
LLM_API_KEY = os.getenv("POPENAI_API_KEY")
pathfinder = PathFinder(ttl_file="aidava-sphn.ttl")
CSV_COMMA_DELIMITER = False


def read_paths_from_output(output_file: str) -> List[str]:
    """Read paths from output.txt file."""
    with open(output_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


def get_main_entity_type(analysis_file: str) -> str:
    """Extract main entity type from analysis file."""
    with open(analysis_file, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line.startswith("Main Entity Type:"):
            return first_line.replace("Main Entity Type:", "").strip()
    return ""


def read_csv_columns(csv_file: str) -> Tuple[List[str], List[str]]:
    """Read CSV file and return headers and first row."""
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        first_row = next(reader)
        return headers, first_row


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


def generate_prompt(
    hop_count: int,
    paths: List[str],
    main_entity: str,
    csv_path: str,
) -> str:
    """Generate the RDF mapping prompt."""
    prompt = f"""# RDF Mapping Assistant for Complex Ontological Relationships

## Context
You are a specialized RDF mapping expert with extensive knowledge of semantic web technologies, ontology engineering, and data transformation. Your expertise includes understanding complex, multi-hop relationships between entities in knowledge graphs.

## Task
Transform a CSV dataset into RDF triples by mapping each column to the most appropriate path in an existing ontology. The ontology contains complex {hop_count}-hop relationships extending from the main entity represented by each row.

## Input
1. Main Entity Type: {main_entity}
2. Available Paths:

{chr(10).join(f"{i+1}. {path}" for i, path in enumerate(paths))}
3. CSV Data:
Column header names -> Column values
{extract_column_examples_as_string(csv_path, 3)}

## Requirements
For each CSV column:
1. Identify the most semantically appropriate path from the main entity through the ontology
2. Select exactly one optimal path for each column
3. Document your reasoning for choosing each path, including any alternatives considered
4. Handle nested relationships and complex datatypes appropriately

## Expected Output
For each column, provide:
1. Column number/name
2. The complete selected path using proper ontology notation (e.g., entity:property1/property2/property3) and the number of the path that is provided also in the input
3. Brief justification for the selected mapping (1-2 sentences)
4. Any data transformation required (datatype conversion, formatting, etc.)

## Example Format
Column: [column_name]
Path: [Number] [entity]:[property1]/[property2]/[property3]
Justification: [Brief explanation of why this path is appropriate]
Transformation: [Any required data processing]

## Additional Notes
- Prioritize semantic accuracy over path length
- Consider domain and range constraints of properties
- Account for cardinality constraints in the ontology
- Flag any columns that may require multiple path options
"""
    return prompt


def send_to_openai(prompt: str) -> str:
    """Send prompt to OpenAI and return the response."""
    client = OpenAI(api_key=LLM_API_KEY)

    try:
        response = client.responses.parse(
            model="gpt-4.1-nano",  # or your preferred model
            temperature=0.7,
            input=[
                {
                    "role": "system",
                    "content": "Imagine you are a specialized RDF mapping expert with extensive knowledge of semantic web technologies.",
                },
                {"role": "user", "content": prompt},
            ],
            text_format=ColumnPathSelectionOutput,
        )
        return response
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return ""


def save_json(response, filepath):
    raw_json = json.loads(response.output_text)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(raw_json, f, indent=4, ensure_ascii=False)


def process_experiment(
    hop_count: int,
    analysis_dir: str = "UM/BC/analysis",
    csv_dir: str = "UM/BC/csv",
    output_dir: str = "UM/BC/output_exp_two_hop",
    send_to_llm: bool = False,
) -> None:
    """Process the experiment for all files in the analysis directory."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read paths from output.txt

    # Process each analysis file
    for analysis_file in Path(analysis_dir).glob("*_analysis.txt"):
        # Get corresponding CSV file
        csv_file = Path(csv_dir) / f"{analysis_file.stem.replace('_analysis', '')}.csv"
        if not csv_file.exists():
            print(f"Warning: No matching CSV file found for {analysis_file}")
            continue

        # Get main entity type
        main_entity = get_main_entity_type(str(analysis_file))
        if not main_entity:
            print(f"Warning: Could not find main entity type in {analysis_file}")
            continue

        paths = ""
        if main_entity:
            paths = pathfinder.find_paths(hop_count=hop_count, target_class=main_entity)

        # Generate prompt
        prompt = generate_prompt(
            hop_count=hop_count, paths=paths, main_entity=main_entity, csv_path=csv_file
        )

        # Save prompt to output file
        output_file = (
            Path(output_dir)
            / f"{analysis_file.stem.replace('_analysis', '')}_prompt.txt"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        # If send_to_llm is True, send to OpenAI and save response
        if send_to_llm:
            response = send_to_openai(prompt)
            if response:
                response_file = (
                    Path(output_dir)
                    / f"{analysis_file.stem.replace('_analysis', '')}_response.txt"
                )
                save_json(response, response_file)


if __name__ == "__main__":
    # Example usage
    csv_dir = (
        f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset"
    )
    analysis_dir = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset/analysis"
    output_dir = f"C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/curated_dataset/exp_one_hop"
    process_experiment(
        hop_count=2,
        send_to_llm=True,
        analysis_dir=analysis_dir,
        csv_dir=csv_dir,
        output_dir=output_dir,
    )
