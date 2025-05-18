# Simple AST parser for SQL
class ASTNode:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"{self.type}({self.value}, {self.children})"

def parse(tokens):
    if not tokens:
        raise Exception("Empty query")
    keyword = tokens[0][1]

    if keyword == 'SELECT':
        return parse_select(tokens)
    elif keyword == 'INSERT':
        return parse_insert(tokens)
    elif keyword == 'DELETE':
        return parse_delete(tokens)
    elif keyword == 'UPDATE':
        return parse_update(tokens)
    elif keyword == 'CREATE':
        return parse_create(tokens)
    else:
        raise Exception("Unsupported query type")

def parse_select(tokens):
    _, fields, _, table, *rest = [token[1] for token in tokens if token[0] != 'SEMICOLON']
    where = None
    if 'WHERE' in rest:
        idx = rest.index('WHERE')
        where = (rest[idx+1], rest[idx+2], rest[idx+3])
    return ASTNode('SELECT', {'fields': fields, 'table': table, 'where': where})

def parse_insert(tokens):
    tokens = [t[1] for t in tokens if t[0] != 'SEMICOLON']
    table = tokens[2]
    values = tokens[tokens.index('VALUES') + 1:]
    values = [v.strip("'") for v in values if v not in ['(', ')', ',']]
    return ASTNode('INSERT', {'table': table, 'values': values})

def parse_delete(tokens):
    tokens = [t[1] for t in tokens if t[0] != 'SEMICOLON']
    table = tokens[2]
    where = (tokens[-3], tokens[-2], tokens[-1]) if 'WHERE' in tokens else None
    return ASTNode('DELETE', {'table': table, 'where': where})

def parse_update(tokens):
    tokens = [t[1] for t in tokens if t[0] != 'SEMICOLON']
    table = tokens[1]
    field, value = tokens[3], tokens[5].strip("'")
    where = (tokens[-3], tokens[-2], tokens[-1]) if 'WHERE' in tokens else None
    return ASTNode('UPDATE', {'table': table, 'field': field, 'value': value, 'where': where})

def parse_create(tokens):
    tokens = [t[1] for t in tokens if t[0] != 'SEMICOLON']
    table = tokens[2]
    fields = tokens[4:-1:2]  # field names
    return ASTNode('CREATE', {'table': table, 'fields': fields})
