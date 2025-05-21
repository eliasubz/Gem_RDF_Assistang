import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Set, List, Dict


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


def extract_column_examples_as_string(csv_path: Path, num_examples: int = 3) -> str:
    """
    Extracts up to `num_examples` unique non-empty values per column from a CSV file
    and returns a formatted string.

    Args:
        csv_path: Path to the CSV file
        num_examples: Number of examples to extract per column

    Returns:
        Formatted string with column examples
    """
    column_examples = defaultdict(set)
    delimiter = detect_csv_delimiter(csv_path)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

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

    lines = []
    for col, vals in column_examples.items():
        examples = list(vals)[:num_examples]
        lines.append(f"Analyze this column: {col} -> {', '.join(examples)}")

    return "\n".join(lines)


def load_entities(path: Path) -> List[str]:
    """
    Loads entities from a text file.

    Args:
        path: Path to the entities file

    Returns:
        List of entity strings
    """
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def save_file(content: str, filepath: Path) -> None:
    """
    Saves content to a file.

    Args:
        content: Content to save
        filepath: Path where to save the content
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def save_json(response: dict, filepath: Path) -> None:
    """
    Saves JSON response to a file.

    Args:
        response: JSON response to save
        filepath: Path where to save the JSON
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4, ensure_ascii=False)


def load_solution_entities(solution_path: Path) -> Set[str]:
    """
    Reads a solution file where each line is a valid correct entity.

    Args:
        solution_path: Path to the solution file

    Returns:
        Set of all correct entity candidates
    """
    with open(solution_path, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def compute_hit_rate(predictions: List[str], ground_truth: Set[str], top_k: int) -> int:
    """
    Computes whether any of the top-k predictions are in the ground truth set.

    Args:
        predictions: List of predicted entities
        ground_truth: Set of ground truth entities
        top_k: Number of top predictions to consider

    Returns:
        1 if there's a hit, 0 otherwise
    """
    return int(any(pred in ground_truth for pred in predictions[:top_k]))
