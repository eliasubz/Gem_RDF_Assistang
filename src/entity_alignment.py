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


# 3. extract raw ttl subgraph showinng all relationships of the possible main entities
with open("working_memory/subgraph.ttl") as f:
    subgraph = [line.strip() for line in f if line.strip()]

csv_headers = extract_columns("raw_data/measurements.csv")


# this is the subgraph of [entity1]:
# property->> node,
# properties:
# nodes:

# for each column mdian , simmple statistics and sample value


# 3. Build prompt for OpenAI
def build_prompt(headers, entities):
    prompt = "You are an expert in semantic web data integration. \n"
    prompt += "Given a list of CSV column headers and a list of RDF ontology entities, and five top candidtates suggest:\n"
    prompt += "1. Which of the following entites could best describe the tabular data that was provided in the csv file \n"
    # Candidates for the main entity
    prompt += "Candidates for the main entity:\n"
    prompt += "https://biomedit.ch/rdf/sphn-ontology/sphn#Measurement, https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Patient, https://biomedit.ch/rdf/sphn-ontology/AIDAVA/Observation"
    prompt += "subgraph with the direct relationships of all canidates"
    for ttl in subgraph:
        prompt += f"- {ttl}\n"
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
