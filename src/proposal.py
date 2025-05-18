import os
from pathlib import Path
from openai import OpenAI
import logging
from typing import Optional
from examples import EXAMPLE1


from config import (
    LLM_API_KEY,
    SEND_TO_API,
    INPUT_CSV_FOLDER,
    OUTPUT_FOLDER,
    ENTITY_FILE,
    MODEL_NAME,
    MODEL_INSTRUCTIONS,
)
from models import Entity, SpanningEntityOutput
from utils import (
    extract_column_examples_as_string,
    load_entities,
    save_file,
    save_json,
    load_solution_entities,
    compute_hit_rate,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=LLM_API_KEY)


def build_prompt(csv_path: Path, entities: list[str]) -> str:
    """
    Builds the prompt for the LLM model.

    Args:
        csv_path: Path to the CSV file
        entities: List of RDF entities

    Returns:
        Formatted prompt string
    """
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
    prompt += "\nHere is one example with only one candidate. I want you to return 15 of those candidates\n<Example>\n"
    prompt += EXAMPLE1
    prompt += "\n</Example>\n"
    return prompt


def process_file(filename: str, rdf_entities: list[str]) -> Optional[tuple[int, int]]:
    """
    Process a single CSV file.

    Args:
        filename: Name of the CSV file
        rdf_entities: List of RDF entities

    Returns:
        Tuple of (hit@5, hit@15) if solution file exists, None otherwise
    """
    if not filename.endswith(".csv"):
        return None

    csv_path = Path(INPUT_CSV_FOLDER) / filename
    prompt = build_prompt(csv_path, rdf_entities)

    base_name = Path(filename).stem
    prompt_file = Path(OUTPUT_FOLDER) / f"{base_name}_prompt.txt"
    save_file(prompt, prompt_file)

    logger.info("Saved prompt: %s", prompt_file)

    if SEND_TO_API:
        try:
            response = client.responses.parse(
                model=MODEL_NAME,
                instructions=MODEL_INSTRUCTIONS,
                input=prompt,
                text_format=SpanningEntityOutput,
            )
            response_file = Path(OUTPUT_FOLDER) / f"{base_name}_response.txt"
            save_json(response, response_file)
            logger.info("Saved response: %s", response_file)
        except Exception as e:
            logger.error("Error processing %s: %s", filename, e)
            return None

    # Get the response from the file
    response_file = Path(OUTPUT_FOLDER) / f"{base_name}_response.txt"
    with open(response_file, newline="", encoding="utf-8") as f:
        response = f.read()

    # Compute Hit@5 and Hit@15
    solution_path = Path(INPUT_CSV_FOLDER) / "solution" / f"{base_name}.txt"
    if solution_path.exists():
        ground_truth_entities = load_solution_entities(solution_path)

        try:
            output = SpanningEntityOutput.model_validate_json(response)
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

            logger.info("%s: Hit@5=%d, Hit@15=%d", base_name, hit5, hit15)
            return hit5, hit15

        except Exception as parse_error:
            logger.error(
                "Could not parse model output for %s: %s", base_name, parse_error
            )
            return None
    else:
        logger.info(
            "No solution file found for %s, skipping hit rate evaluation.", base_name
        )
        return None


def main():
    """Main function to process all CSV files."""
    rdf_entities = load_entities(ENTITY_FILE)

    total_hit5 = 0
    total_hit15 = 0
    processed_files = 0

    for filename in os.listdir(INPUT_CSV_FOLDER):
        result = process_file(filename, rdf_entities)
        if result is not None:
            hit5, hit15 = result
            total_hit5 += hit5
            total_hit15 += hit15
            processed_files += 1

    if processed_files > 0:
        avg_hit5 = total_hit5 / processed_files
        avg_hit15 = total_hit15 / processed_files
        logger.info("Average Hit@5: %.2f", avg_hit5)
        logger.info("Average Hit@15: %.2f", avg_hit15)


if __name__ == "__main__":
    main()
