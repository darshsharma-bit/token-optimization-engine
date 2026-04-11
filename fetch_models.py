import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
)
models = response.json().get('data', [])
free_models = [m['id'] for m in models if ':free' in m['id']]
print("Free Models:", free_models[:10])
