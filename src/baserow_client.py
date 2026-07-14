"""Helpers for pushing cleaned WMS data to a Baserow table."""
import os, time
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.baserow.io/api/database"


def get_token() -> str:
    token = os.getenv("BASEROW_API_TOKEN")
    if not token:
        raise EnvironmentError("BASEROW_API_TOKEN not set in environment/.env")
    return token


def push_row(table_id: int | str, payload: dict):
    url = f"{BASE_URL}/rows/table/{table_id}/?user_field_names=true"
    headers = {"Authorization": f"Token {get_token()}"}
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()


def push_dataframe(table_id: int | str, data: pd.DataFrame):
    """Pushes each row of a DataFrame to Baserow, retrying once on rate limit."""
    url = f"{BASE_URL}/rows/table/{table_id}/"
    headers = {"Authorization": f"Token {get_token()}", "Content-Type": "application/json"}

    for _, row in data.iterrows():
        payload = {"fields": {col: row[col] for col in data.columns}}
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code == 429:
            time.sleep(2)
            r = requests.post(url, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
