import os
from dotenv import load_dotenv, find_dotenv

# load env (.env file in the directory with OPENAI_API_KEY)
load_dotenv(find_dotenv())

# get OpenAI API key
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# get OpenAI API service address
# OPENAI_API_BASE = os.environ['OPENAI_API_BASE'] # not needed

# doc - models：https://platform.openai.com/docs/models
MODELS = [
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]
DEFAULT_MODEL = MODELS[0]
MODEL_TO_MAX_TOKENS = {
    "gpt-4-turbo": 4096,
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4096,
}