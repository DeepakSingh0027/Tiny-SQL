import os
import json

DATA_DIR = 'data'

def table_path(table_name):
    return os.path.join(DATA_DIR, f'{table_name}.json')

def table_exists(table_name):
    return os.path.exists(table_path(table_name))

def load_table(table_name):
    path = table_path(table_name)
    if not os.path.exists(path):
        raise ValueError(f"Table '{table_name}' does not exist.")
    with open(path, 'r') as f:
        data = json.load(f)
        # columns should be list of (name, type) tuples, e.g. [("id", "INT"), ("name", "TEXT")]
        columns = data.get('columns')
        rows = data.get('rows', [])
        return columns, rows

def save_table(table_name, columns, rows):
    """
    columns: list of tuples [(field_name, field_type), ...]
    rows: list of dictionaries or lists matching columns
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(table_path(table_name), 'w') as f:
        json.dump({'columns': columns, 'rows': rows}, f, indent=2)
