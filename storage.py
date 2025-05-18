import os
import json

DATA_DIR = 'data'

def table_path(table_name):
    return os.path.join(DATA_DIR, f'{table_name}.json')

def load_table(table_name):
    path = table_path(table_name)
    if not os.path.exists(path):
        raise Exception(f"Table '{table_name}' does not exist.")
    with open(path, 'r') as f:
        data = json.load(f)
        return data['columns'], data['rows']

def save_table(table_name, columns, rows):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(table_path(table_name), 'w') as f:
        json.dump({'columns': columns, 'rows': rows}, f, indent=2)
