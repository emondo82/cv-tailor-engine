import os
from dotenv import load_dotenv

load_dotenv()

print("OPENAI key loaded:", bool(os.getenv("OPENAI_API_KEY")))
print("GEMINI key loaded:", bool(os.getenv("GEMINI_API_KEY")))
print("OPENAI model:", os.getenv("OPENAI_MODEL"))
print("GEMINI model:", os.getenv("GEMINI_MODEL"))
print("LLM bullet refiner enabled:", os.getenv("USE_LLM_BULLET_REFINER"))