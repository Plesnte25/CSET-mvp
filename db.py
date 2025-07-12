import os, requests
from dotenv import load_dotenv; load_dotenv()

BASE = "https://api.baserow.io/api/database"
HEAD = {"Authorization": f"Token {os.environ['BASEROW_TOKEN']}"}

def baserow_post(table_id: int, payload: dict):
    url = f"{BASE}/rows/table/{table_id}/?user_field_names=true"
    r = requests.post(url, json=payload, headers=HEAD, timeout=15)
    r.raise_for_status()
    return r.json()
