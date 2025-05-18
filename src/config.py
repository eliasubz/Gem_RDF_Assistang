import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
LLM_API_KEY = os.getenv("POPENAI_API_KEY")
SEND_TO_API = True  # Change to True if you want to get responses from OpenAI

# File Paths
BASE_DIR = Path(__file__).parent.parent
INPUT_CSV_FOLDER = BASE_DIR / "curated_dataset"
OUTPUT_FOLDER = BASE_DIR / "curated_dataset" / "main_entity_selection"
ENTITY_FILE = BASE_DIR / "working_memory" / "clean_entities.txt"


# Model Configuration
MODEL_NAME = "gpt-4.1-nano-2025-04-14"
MODEL_INSTRUCTIONS = "You are a data integration expert."
