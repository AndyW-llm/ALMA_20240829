import os
from dotenv import load_dotenv

dotenv_path = os.path.abspath("./secrets.env")
if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path)
    DEFAULT_OAI_KEY = os.getenv('OAI_API_KEY', None)
else:
    print('[get_oai_key.py] Could not find secrets file at:\n', dotenv_path)
    DEFAULT_OAI_KEY="Your OpenAI API Key"