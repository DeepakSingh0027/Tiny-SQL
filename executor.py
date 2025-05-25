from storage import load_table, save_table, table_exists
from utils import print_table

def handle_select(ast):
    table_name = ast.value['table']
    if not table_exists(table_name):
        raise ValueError(f"Table '{table_name}' does not exist.")
    
    columns, rows = load_table(table_name)
    where = ast.value['where']
    fields = ast.value['fields']

    # Check WHERE field exists if WHERE is used
    if where:
        key, op, val = where
        if key not in columns:
            raise ValueError(f"Field '{key}' in WHERE clause does not exist in table '{table_name}'.")
        if op != '=':
            raise ValueError(f"Unsupported operator in WHERE clause: {op}")
        rows = [r for r in rows if str(r.get(key)) == val]

    # Check requested fields exist or handle '*'
    if fields == '*':
        print_table(rows)
    else:
        for f in fields:
            if f not in columns:
                raise ValueError(f"Field '{f}' does not exist in table '{table_name}'.")
        filtered_rows = [{k: row.get(k, "<missing>") for k in fields} for row in rows]
        print_table(filtered_rows)

def handle_insert(ast):
    table_name = ast.value['table']
    if not table_exists(table_name):
        raise ValueError(f"Table '{table_name}' does not exist.")
    
    columns, rows = load_table(table_name)
    fields = ast.value['fields']
    values = ast.value['values']

    # Check fields is list and fields exist in columns
    if not isinstance(fields, list):
        raise ValueError("INSERT fields must be a list of field names.")
    for f in fields:
        if f not in columns:
            raise ValueError(f"Field '{f}' does not exist in table '{table_name}'.")
    
    if len(values) != len(fields):
        raise ValueError("Column count does not match value count.")
    
    # Optionally: fill missing columns with None or '<missing>'
    # For now, only insert fields given
    row = {col: "<missing>" for col in columns}  # default values
    row.update(dict(zip(fields, values)))

    rows.append(row)
    save_table(table_name, columns, rows)
    print("1 row inserted.")

def handle_delete(ast):
    table_name = ast.value['table']
    if not table_exists(table_name):
        raise ValueError(f"Table '{table_name}' does not exist.")
    
    columns, rows = load_table(table_name)
    before = len(rows)
    if ast.value['where']:
        key, op, val = ast.value['where']
        if key not in columns:
            raise ValueError(f"Field '{key}' in WHERE clause does not exist in table '{table_name}'.")
        if op != '=':
            raise ValueError(f"Unsupported operator in WHERE clause: {op}")
        rows = [r for r in rows if str(r.get(key)) != val]
    else:
        # Delete all rows if no WHERE
        rows = []

    save_table(table_name, columns, rows)
    print(f"{before - len(rows)} rows deleted.")

def handle_update(ast):
    table_name = ast.value['table']
    if not table_exists(table_name):
        raise ValueError(f"Table '{table_name}' does not exist.")

    columns, rows = load_table(table_name)
    field_to_update = ast.value['field']
    if field_to_update not in columns:
        raise ValueError(f"Field '{field_to_update}' does not exist in table '{table_name}'.")

    count = 0
    where = ast.value.get('where')
    if where:
        key, op, val = where
        if key not in columns:
            raise ValueError(f"Field '{key}' in WHERE clause does not exist in table '{table_name}'.")
        if op != '=':
            raise ValueError(f"Unsupported operator in WHERE clause: {op}")

    for r in rows:
        # If no WHERE clause, update all rows
        if not where:
            r[field_to_update] = ast.value['value']
            count += 1
        else:
            # Compare as string after stripping spaces, or convert to str for safety
            row_value = str(r.get(key)).strip()
            val_str = str(val).strip()
            if row_value == val_str:
                r[field_to_update] = ast.value['value']
                count += 1

    save_table(table_name, columns, rows)
    print(f"{count} rows updated.")


def handle_create(ast):
    table_name = ast.value['table']
    if table_exists(table_name):
        raise ValueError(f"Table '{table_name}' already exists.")
    
    # ast.value['fields'] is a list of (field_name, field_type)
    fields = ast.value['fields']
    if not all(isinstance(f, tuple) and len(f) == 2 for f in fields):
        raise ValueError("CREATE fields must be a list of (field_name, field_type) tuples.")
    
    headers = [field_name for field_name, _ in fields]
    save_table(table_name, headers, [])
    print(f"Table '{table_name.upper()}' created with fields {headers}")

def execute(ast):
    t = ast.type

    if t == 'SELECT':
        handle_select(ast)
    elif t == 'INSERT':
        handle_insert(ast)
    elif t == 'DELETE':
        handle_delete(ast)
    elif t == 'UPDATE':
        handle_update(ast)
    elif t == 'CREATE':
        handle_create(ast)
    else:
        raise ValueError(f"Unsupported AST node type: {t}")
