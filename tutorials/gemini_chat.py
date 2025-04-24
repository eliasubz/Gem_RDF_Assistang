import os

from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()
LLM_API_KEY = os.getenv("GEM_API_KEY")
LLM_MODEL = "gemini-2.0-flash"


client = genai.Client(api_key=LLM_API_KEY)
chat = client.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a Beaver and only speak spanish"
    ),
)

response = chat.send_message("I have 2 dogs in my house.")
print(response.text)

response = chat.send_message("How many paws are in my house?")
print(response.text)

for message in chat.get_history():
    print(f"role - {message.role}", end=": ")
    print(message.parts[0].text)
