from openai import OpenAI
import json
import os
import openai
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()
LLM_API_KEY = os.getenv("POPENAI_API_KEY")

client = OpenAI(api_key=LLM_API_KEY)

prompt = "Provid valid JSON output. Provide a ranked list of the top ten candidates for entities that could be connected to all columns."
prompt += "Ranking them on spanning ability. Provide one column 'name' and a column 'slope_kilometers."

openai.api_key = LLM_API_KEY


class Spanning_entity_output(BaseModel):
    spanning_entity_candidates: list[str]


response = client.responses.parse(
    model="gpt-4.1-nano-2025-04-14",
    # text={"format": {"type": "json_object"}},
    input=[
        {"role": "system", "content": "Provide output in valid JSON"},
        {"role": "user", "content": prompt},
    ],
    text_format=Spanning_entity_output,
)

if response.status == "completed":
    # In this case the model has either successfully finished generating the JSON object according to your schema, or the model generated one of the tokens you provided as a "stop token"
    print(response.output_text)
