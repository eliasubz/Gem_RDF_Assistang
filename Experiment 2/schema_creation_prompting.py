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

from Path_Finding_Logic.main import PathFinder


# JSON output schema
class SemanticPath(BaseModel):

    source_entity: str
    target_entity: str
    predicate: str
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
    num_examples: int,
) -> str:
    """Generate the RDF mapping prompt."""
    prompt = f"""# RDF Mapping Assistant for Complex Ontological Relationships

## Objective
Given a CSV dataset and a set of ontology paths rooted in a main entity class, map each column to the most semantically appropriate ontology path, producing RDF triples for later use.

## Ontology Metadata
- **Main Entity Type**: `{main_entity}`
- **Ontology Source**: https://biomedit.ch/rdf/sphn-ontology/sphn

## Input
1. Main Entity Type: {main_entity}
2. Available Paths:
{paths}
3. CSV Data:

{extract_column_values_as_string(csv_path, num_examples)}

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


"""
    prompt += """
## Example Format
"column_mappings": [
    {
        "column_name": "entity_id",
        "path": {
            "path_id": 1
        },
        "justification": "The 'entity_id' field represents a unique identifier associated with the main observation, making this path semantically appropriate.",
        "transformation": "Ensure the ID format matches URI requirements (e.g., prefix or encode)."
    },
]

### Specific Instructions
Before selecting a 1-hop path, first check if any 2-hop paths that begin from the same end node as that 1-hop path offer a better option. If not, explain why they aren't better before proceeding with the 1-hop path.

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
            model="gpt-4.1",  # or your preferred model
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
    use_shortened_URI=True,
    num_examples=3,
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
            if use_shortened_URI:
                paths = pathfinder.find_short_string_paths(
                    hop_count=hop_count, target_class=main_entity
                )
            else:
                paths = pathfinder.find_string_paths(
                    hop_count=hop_count, target_class=main_entity
                )

        # Generate prompt
        prompt = generate_prompt(
            hop_count=hop_count,
            paths=paths,
            main_entity=main_entity,
            csv_path=csv_file,
            num_examples=num_examples,
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
    # 1. CSV directory
    base_csv_dir = (
        "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data"
    )
    # 2. Analysis directory with OAT groun truths
    base_analysis_dir = f"{base_csv_dir}/analysis"
    # 2. base output directory
    base_output_dir = f"{base_csv_dir}"

    hop_counts = [1, 2]
    example_counts = [1, 3]
    uri_combinations = [True, False]  # only one can be True per run

    for hop_count in hop_counts:
        for num_examples in example_counts:
            for short_uri in uri_combinations:

                uri_type = "short_URI" if short_uri else "long_URI"
                output_dir = f"{base_output_dir}/path_selection_gpt_{hop_count}_hop_{uri_type}_{num_examples}_smpl"

                print(
                    f"Running: hop_count={hop_count}, short_uri={short_uri}, examples={num_examples}"
                )

                process_experiment(
                    hop_count=hop_count,
                    # 4. Check this as true
                    send_to_llm=False,
                    analysis_dir=base_analysis_dir,
                    csv_dir=base_csv_dir,
                    output_dir=output_dir,
                    use_shortened_URI=short_uri,
                    num_examples=num_examples,
                )
