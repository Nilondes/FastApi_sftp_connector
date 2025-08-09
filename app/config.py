import os
from dotenv import load_dotenv

load_dotenv(".env.dev.pg")

def get_database_url():
    return f"postgresql://" \
           f"{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}" \
           f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}" \
           f"/{os.getenv('PG_DB')}"