import csv
import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
LLM_API_KEY = os.getenv("OPENAI_API_KEY")

# 1. Load pre-filtered RDF entities from previous step (assume they're in a file or list)
with open("working_memory/clean_entities.txt") as f:
    rdf_entities = [line.strip() for line in f if line.strip()]


# 2. Load CSV and extract column headers
def extract_columns(csv_path):
    with open(csv_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)  # Assumes first row = headers
    return headers


print(subgraph)
exit()

csv_headers = extract_columns("raw_data/measurements.csv")


# 3. Build prompt for OpenAI
def build_prompt(headers, entities):
    prompt = "You are an expert in semantic web data integration. \n"
    prompt += "Given a list of CSV column headers and a list of RDF ontology entities, suggest:\n"
    prompt += "1. Is there one overarching entity oustide of all the columns, that all columns could be linked to? If yes which entity out of the RDF Entities could that be?\n"
    prompt += "2. Give me 5 canditate entities in an array.\n"

    prompt += "CSV Columns:\n"
    for h in headers:
        prompt += f"- {h}\n"
    prompt += "\nRDF Entities:\n"
    for e in entities:  # Limit to top 50 for brevity
        prompt += f"- {e}\n"
    return prompt


query_prompt = build_prompt(csv_headers, rdf_entities)


# print(os.getenv("OPENAI_API_KEY")
# print(query_prompt)
# exit()
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("POPENAI_API_KEY"),
)

response = client.responses.create(
    model="gpt-4.1-nano",
    instructions="You are a data integration expert.",
    input=query_prompt,
)

# 5. Output response
print(response)
print(response.output_text)
