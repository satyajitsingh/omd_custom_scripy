import json
import pandas as pd
import requests
from pathlib import Path

# Load config
config_path = Path(__file__).parents[1] / "config" / "input_config.json"
with open(config_path) as f:
    config = json.load(f)

HOST = config["host"]
HEADERS = {
    "Authorization": config["auth_token"],
    "Content-Type": "application/json"
}

# Load Excel file
data_path = Path(__file__).parents[1] / "data" / "metadata.xlsx"
df = pd.read_excel(data_path)

# Helpers
def get_entity(entity, name):
    url = f"{HOST}/v1/{entity}?name={name}"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else None

def post_entity(entity, payload):
    url = f"{HOST}/v1/{entity}"
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code not in (200, 201):
        print(f"Error creating {entity}: {response.text}")
    return response.json()

def get_or_create(entity, payload, name_field='name'):
    existing = get_entity(entity, payload[name_field])
    if existing:
        return existing
    return post_entity(entity, payload)

# Loop through each row
for _, row in df.iterrows():
    service_payload = {
        "name": row["service_name"],
        "description": row["Service_description"],
        "serviceType": "CustomDatabase"
    }
    service = get_or_create("services/databaseServices", service_payload)

    db_payload = {
        "name": row["database_name"],
        "description": row["database_descriptiion"],
        "service": {"id": service["id"], "type": "databaseService"}
    }
    database = get_or_create("databases", db_payload)

    schema_payload = {
        "name": row["schema_name"],
        "description": row["schecma_description"],
        "database": {"id": database["id"], "type": "database"}
    }
    schema = get_or_create("databaseSchemas", schema_payload)

    table_payload = {
        "name": row["table_name"],
        "description": row["table_description"],
        "databaseSchema": {"id": schema["id"], "type": "databaseSchema"},
        "columns": [{
            "name": row["column_name"],
            "dataType": row["column_type"],
            "description": row["column_description"]
        }]
    }
    table = get_or_create("tables", table_payload)

    print(f"Processed table: {row['table_name']}")

