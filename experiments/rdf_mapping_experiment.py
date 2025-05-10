import os
import csv
from pathlib import Path
from typing import Dict, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from llm_assistant_hack_main.exportable_find_paths import find_paths


# Load environment variables
load_dotenv()
LLM_API_KEY = os.getenv("POPENAI_API_KEY")


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


def generate_prompt(
    hop_count: int,
    paths: List[str],
    main_entity: str,
    columns: List[str],
    values: List[str],
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
{chr(10).join(f"{col} -> {val}" for col, val in zip(columns, values))}

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
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # or your preferred model
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized RDF mapping expert with extensive knowledge of semantic web technologies.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return ""


def process_experiment(
    hop_count: int,
    output_file: str = "output.txt",
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

        # Create and read paths
        if main_entity:
            paths = find_paths(hop_count, main_entity)
        paths = read_paths_from_output(output_file)

        # Read CSV columns
        try:
            columns, values = read_csv_columns(str(csv_file))
        except Exception as e:
            print(f"Error reading CSV file {csv_file}: {e}")
            continue

        # Generate prompt
        prompt = generate_prompt(
            hop_count=hop_count,
            paths=paths,
            main_entity=main_entity,
            columns=columns,
            values=values,
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
                with open(response_file, "w", encoding="utf-8") as f:
                    f.write(response)


if __name__ == "__main__":
    # Example usage
    process_experiment(hop_count=2, send_to_llm=False)
