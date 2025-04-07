import json
import os
from google import genai
from google.genai import types

import numpy as np
from dotenv import load_dotenv
from kink import di

# from openai import OpenAIs
from qdrant_client import QdrantClient
from qdrant_client.fastembed_common import QueryResponse
from sentence_transformers import SentenceTransformer

# from torch import cosine_similarity

from utils.embedding_generators.llm_concept_embedding_generator import (
    LLMConceptEmbeddingGenerator,
)
from utils.embedding_generators.rdf_craft_ontology_embedding_generator import (
    RDFCraftOntologyEmbeddingGenerator,
)


load_dotenv()
LLM_MODEL = "gemini-2.0-flash"


LLM_API_KEY = os.getenv("GEM_API_KEY")
# LLM_API_KEY = GEM_API_KEY
print(LLM_API_KEY)
LLM_MODEL = "gemini-2.0-flash"

di["llm_api_key"] = LLM_API_KEY
di["llm_model"] = LLM_MODEL

di["Gemini"] = genai.Client(api_key=di["llm_api_key"])
di["GemChat"] = None
gem_chat = None


di[SentenceTransformer] = SentenceTransformer("all-MiniLM-L6-v2")


class NumpyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


def load_json(json_file_path):
    with open(json_file_path, "r") as f:
        data = json.load(f)

    return data


messages = []


def get_concepts(data, messages: list = messages, real=1):
    ABSTRACT_VIEW_SYSTEM_PROMPT = """

        You are helpful RDF mapping assistant that helps to map table and json data to RDF.

        Your task is to make guesses on the possible RDF Classes and Properties that might be used to represent the data.

        Return with following format:

        [
            "Person: A human being"
        ]

        You can return more than one concept in the array.

        JUST RETURN JSON
        """

    client = di["Gemini"]
    if real == 0:
        return """```json
[
    "AdministrativeCase: A record of an administrative case related to a patient's diagnosis and organization",
    "Patient: An individual receiving healthcare services",
    "Diagnosis: The identification of a disease or condition",
    "Organization: A healthcare provider or institution",
    "CreatedAt: The timestamp when the administrative case was created",
    "RowId: unique identifier of the record",
    "PatientId: the unique identifier of the patient",
    "DiagnosisCode: A code representing a specific diagnosis",
    "OrgCode: A code representing a specific organization",
    "OrgName: The name of the organization"
]
```"""

    messages.extend(
        [
            {
                "role": "system",
                "content": ABSTRACT_VIEW_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "data": data,
                    },
                    cls=NumpyEncoder,
                ),
            },
        ]
    )

    prompt = client.models.generate_content(
        model=di["llm_model"],
        config=types.GenerateContentConfig(
            system_instruction=ABSTRACT_VIEW_SYSTEM_PROMPT
        ),
        contents=data,
    )
    print(prompt.text)
    messages.append(
        {
            "role": "assistant",
            "content": prompt.text or "",
        }
    )
    ABSTRACT_VIEW_SYSTEM_PROMPT_PROPERTIES = """

        Now you will receive list of properties that are relevant to the concepts you provided.
        Which of these properties do you need to map the data to RDF?

        While mapping if you think you don't have enough information to map a entity fully but enough to generate URI, then set return_more to false.
        Else, return_more to true.

        Now Provide in following format:

        [
            {
                "full_uri": "http://example.com/property1",
                "return_more": true
            }
        ]

        JUST RETURN JSON ARRAY OF OBJECTS

        """
    di["GemChat"] = "hello do you see that?"

    gem_chat = di["Gemini"].chats.create(
        model=LLM_MODEL,
        history=[
            types.Content(
                role="user",
                parts=[types.Part(text=prompt.text)],
            ),
            types.Content(
                role="model",
                parts=[types.Part(text=prompt.text)],
            ),
        ],
        config=types.GenerateContentConfig(
            system_instruction=ABSTRACT_VIEW_SYSTEM_PROMPT_PROPERTIES
        ),
    )

    prompt = gem_chat.send_message(data)
    return (prompt.text, gem_chat) or ("", gem_chat)


def get_relevant_properties(data, messages: list = messages, chat=gem_chat):
    print("The data we give to our llm to get rel_properties: ", data)
    print("The messages: ", messages)
    print("Lets hope we get them")
    ABSTRACT_VIEW_SYSTEM_PROMPT = """

        Now you will receive list of properties that are relevant to the concepts you provided.
        Which of these properties do you need to map the data to RDF?

        While mapping if you think you don't have enough information to map a entity fully but enough to generate URI, then set return_more to false.
        Else, return_more to true.

        Now Provide in following format:

        [
            {
                "full_uri": "http://example.com/property1",
                "return_more": true
            }
        ]

        JUST RETURN JSON ARRAY OF OBJECTS

        """

    chat = gem_chat
    print(di["GemChat"])

    messages.extend(
        [
            {
                "role": "system",
                "content": ABSTRACT_VIEW_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": "\n".join(data),
            },
        ]
    )
    # prompt = client.models.generate_content(
    #     model=di["llm_model"],
    #     config=types.GenerateContentConfig(
    #         system_instruction=ABSTRACT_VIEW_SYSTEM_PROMPT
    #     ),
    #     contents=data,
    # )
    prompt = chat.send_message(data)
    print(prompt.text)
    messages.append(
        {
            "role": "assistant",
            "content": prompt.text or "",
        }
    )

    return prompt.text or ""


def extract_column_names(json_path: str) -> str:
    """
    Extracts column names from a metadata JSON file and formats them for LLM input.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        str: A formatted string listing column names.
    """
    # Load the metadata JSON
    with open(json_path, "r", encoding="utf-8") as file:
        meta_data = json.load(file)

    # Extract the column names
    column_names = meta_data.get("references", [])

    if not column_names:
        return "No column names found in metadata."

    # Format the column names for better LLM understanding
    formatted_columns = ", ".join(column_names)
    return f"The dataset '{meta_data.get('name', 'Unknown Dataset')}' contains the following columns: {formatted_columns}."


import re


def clean_and_load_json(concepts: str):
    """
    Cleans a JSON-like string by removing triple backticks and loading it as a Python object.

    Args:
        concepts (str): The JSON string wrapped in triple backticks.

    Returns:
        list: A Python list parsed from the JSON string.
    """
    # Use regex to remove the triple backticks and optional "json" label
    cleaned_json = re.sub(r"```json|```", "", concepts).strip()

    # Convert the cleaned string into a Python object
    return json.loads(cleaned_json)


# Example input
concepts_string = """```json
[
    "AdministrativeCase: A record or instance of an administrative case, potentially related to a patient and their diagnosis within an organization.",
    "Patient: An individual receiving healthcare services, identified by a patient ID.",
    "Diagnosis: A medical diagnosis identified by a diagnosis code.",
    "Organization: A healthcare organization or institution, identified by an organization code and name."
]
```"""

# Convert to a Python list
concepts_list = clean_and_load_json(concepts_string)

# Print the result
print(concepts_list)


MAX_RETRIES = 3


def main(json_file_path):

    qdrant = QdrantClient(":memory:")
    data = load_json(json_file_path)

    classes = data.get("classes", [])
    properties = data.get("properties", [])
    individual = data.get("individuals", [])

    classes_metadata = [
        {
            "label": (
                _cls["label"][0].get("value", "")
                if "label" in _cls and len(_cls["label"]) > 0
                else ""
            ),
            "description": (
                _cls["description"][0].get("value", "")
                if "description" in _cls and len(_cls["description"]) > 0
                else ""
            ),
            "full_uri": _cls["full_uri"],
        }
        for _cls in classes
    ]
    print(classes_metadata[:5])

    properties_metadata = [
        {
            "label": (
                prop["label"][0].get("value", "")
                if "label" in prop and len(prop["label"]) > 0
                else ""
            ),
            "description": (
                prop["description"][0].get("value", "")
                if "description" in prop and len(prop["description"]) > 0
                else ""
            ),
            "full_uri": prop["full_uri"],
        }
        for prop in properties
    ]
    print(properties_metadata[:5])

    print("\nFirst 5 Classes:")
    for cls in classes[:5]:  # Get first 5 classes
        print(json.dumps(cls, indent=4))

    # Print first 5 properties
    print("\nFirst 5 Properties:")
    for prop in properties[:5]:  # Get first 5 properties
        print(json.dumps(prop, indent=4))

    qdrant.add(
        "classes",
        [str(_cls) for _cls in classes],
        classes_metadata,
    )

    qdrant.add(
        "properties",
        [str(prop) for prop in properties],
        properties_metadata,
    )

    # example_csv_metadata = load_json("meta_data.json")
    example_csv_metadata = extract_column_names("meta_data.json")

    concepts = None
    print(example_csv_metadata)

    for _ in range(MAX_RETRIES):
        concepts, gem_chat = get_concepts(example_csv_metadata, real=1)

        print(concepts)

        if concepts and concepts != "":
            try:
                clean_and_load_json(concepts)
            except Exception:
                continue
            break

    else:
        raise Exception("Failed to get concepts")

    # concepts_arr: list[str] = json.loads(concepts)
    concepts_arr = concepts
    relevant_concepts: list[QueryResponse] = []

    for concept_str in concepts_arr:
        search_results: list[QueryResponse] = qdrant.query(
            "classes",
            concept_str,
        )

        if search_results:
            relevant_concepts.append(search_results[0])

    relevant_concepts_full_uris = [
        concept.metadata["full_uri"] for concept in relevant_concepts
    ]

    relevant_classes = [
        _cls for _cls in classes if _cls["full_uri"] in relevant_concepts_full_uris
    ]

    relevant_properties = [
        _prop
        for _prop in properties
        if any(_cls["full_uri"] in _prop["domain"] for _cls in relevant_classes)
        or any(_cls["full_uri"] in _prop["range"] for _cls in relevant_classes)
    ]

    possible_props_for_relevant_classes = [
        prop["full_uri"]
        for prop in relevant_properties
        if any(_cls["full_uri"] in prop["domain"] for _cls in relevant_classes)
    ]

    properties_arr = None

    for _ in range(MAX_RETRIES):
        properties_arr = get_relevant_properties(
            possible_props_for_relevant_classes, chat=gem_chat
        )

        print(properties_arr)

        if properties_arr and properties_arr != "":
            try:
                # json.loads(properties_arr)
                clean_and_load_json(properties_arr)
            except Exception:
                continue
            break

    else:
        raise Exception("Failed to get properties")

    with open("relevant_classes.json", "w") as f:
        json.dump(relevant_classes, f, indent=4)

    with open("relevant_properties.json", "w") as f:
        json.dump(relevant_properties, f, indent=4)


if __name__ == "__main__":
    json_file_path = "ontology.json"
    main(json_file_path)
