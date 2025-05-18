from storage import load_table, save_table
from utils import print_table

def execute(ast):
    t = ast.type
    if t == 'SELECT':
        columns, rows = load_table(ast.value['table'])
        if ast.value['where']:
            key, op, val = ast.value['where']
            rows = [r for r in rows if str(r.get(key)) == val]
        if ast.value['fields'] == '*':
            print_table(rows)
        else:
            print_table([{k: row[k] for k in ast.value['fields']} for row in rows])

    elif t == 'INSERT':
        columns, rows = load_table(ast.value['table'])
        if len(ast.value['values']) != len(columns):
            raise Exception("Column count does not match value count.")
        row = dict(zip(columns, ast.value['values']))
        rows.append(row)
        save_table(ast.value['table'], columns, rows)
        print("1 row inserted.")

    elif t == 'DELETE':
        columns, rows = load_table(ast.value['table'])
        before = len(rows)
        if ast.value['where']:
            key, op, val = ast.value['where']
            rows = [r for r in rows if str(r.get(key)) != val]
        save_table(ast.value['table'], columns, rows)
        print(f"{before - len(rows)} rows deleted.")

    elif t == 'UPDATE':
        columns, rows = load_table(ast.value['table'])
        count = 0
        for r in rows:
            if not ast.value['where'] or str(r.get(ast.value['where'][0])) == ast.value['where'][2]:
                r[ast.value['field']] = ast.value['value']
                count += 1
        save_table(ast.value['table'], columns, rows)
        print(f"{count} rows updated.")

    elif t == 'CREATE':
        headers = ast.value['fields']
        save_table(ast.value['table'], headers, [])
        print(f"Table '{ast.value['table'].upper()}' created with fields {headers}")
