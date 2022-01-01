import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

WORK_ROOT = os.getenv("WORK_ROOT")
SOURCE_DIR =  os.getenv(os.path.join(WORK_ROOT, "source"))
RIOT_TOKEN =  os.getenv("RIOT_TOKEN")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")