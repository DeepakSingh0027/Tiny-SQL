class ASTNode:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"{self.type}({self.value}, {self.children})"


def parse(tokens):
    if not tokens:
        raise ValueError("Empty query")
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
        raise ValueError("Unsupported query type")


def parse_select(tokens):
    # SELECT fields FROM table [WHERE condition]
    tokens = [t for t in tokens if t[0] != 'SEMICOLON']
    # expect format: SELECT fields FROM table WHERE ... (optional)

    if tokens[1][0] == 'STAR':
        fields = '*'
        idx_from = 2
    else:
        # collect comma separated fields till 'FROM'
        fields = []
        i = 1
        while tokens[i][1] != 'FROM':
            if tokens[i][0] == 'COMMA':
                i += 1
                continue
            fields.append(tokens[i][1])
            i += 1
        idx_from = i

    if tokens[idx_from][1] != 'FROM':
        raise ValueError("Expected FROM keyword")

    table = tokens[idx_from + 1][1]

    # check for WHERE clause
    where = None
    if len(tokens) > idx_from + 2 and tokens[idx_from + 2][1] == 'WHERE':
        # where condition format: WHERE key OP value
        key = tokens[idx_from + 3][1]
        op = tokens[idx_from + 4][1]
        val = tokens[idx_from + 5][1]
        if tokens[idx_from + 5][0] == 'STRING':
            val = val.strip("'")
        where = (key, op, val)

    return ASTNode('SELECT', {'fields': fields, 'table': table, 'where': where})


def parse_insert(tokens):
    # INSERT INTO table (fields) VALUES (values)
    tokens = [t for t in tokens if t[0] != 'SEMICOLON']
    # Format: INSERT INTO table (field1, field2) VALUES (value1, value2)

    if tokens[1][1] != 'INTO':
        raise ValueError("Expected INTO after INSERT")

    table = tokens[2][1]

    # parse fields inside parentheses after table name
    if tokens[3][0] != 'LPAREN':
        raise ValueError("Expected '(' after table name")

    # fields between LPAREN and RPAREN
    fields = []
    i = 4
    while tokens[i][0] != 'RPAREN':
        if tokens[i][0] == 'COMMA':
            i += 1
            continue
        fields.append(tokens[i][1])
        i += 1

    # next token after RPAREN should be VALUES
    i += 1
    if tokens[i][1] != 'VALUES':
        raise ValueError("Expected VALUES keyword")

    # next token should be LPAREN for values
    i += 1
    if tokens[i][0] != 'LPAREN':
        raise ValueError("Expected '(' before values")

    # values between LPAREN and RPAREN
    i += 1
    values = []
    while tokens[i][0] != 'RPAREN':
        if tokens[i][0] == 'COMMA':
            i += 1
            continue
        val = tokens[i][1]
        if tokens[i][0] == 'STRING':
            val = val.strip("'")
        values.append(val)
        i += 1

    if len(values) != len(fields):
        raise ValueError("Column count does not match value count")
    
    return ASTNode('INSERT', {'table': table, 'fields': fields, 'values': values})


def parse_delete(tokens):
    # DELETE FROM table WHERE condition (optional)
    tokens = [t for t in tokens if t[0] != 'SEMICOLON']
    if tokens[1][1] != 'FROM':
        raise ValueError("Expected FROM after DELETE")
    table = tokens[2][1]

    where = None
    if len(tokens) > 3 and tokens[3][1] == 'WHERE':
        key = tokens[4][1]
        op = tokens[5][1]
        val = tokens[6][1]
        if tokens[6][0] == 'STRING':
            val = val.strip("'")
        where = (key, op, val)

    return ASTNode('DELETE', {'table': table, 'where': where})


def parse_update(tokens):
    # UPDATE table SET field = value WHERE condition (optional)
    tokens = [t for t in tokens if t[0] != 'SEMICOLON']

    table = tokens[1][1]

    if tokens[2][1] != 'SET':
        raise ValueError("Expected SET keyword after table name")

    field = tokens[3][1]

    if tokens[4][0] != 'OP' or tokens[4][1] != '=':
        raise ValueError("Expected '=' after field name")

    value = tokens[5][1]
    if tokens[5][0] == 'STRING':
        value = value.strip("'")

    where = None
    if len(tokens) > 6 and tokens[6][1] == 'WHERE':
        key = tokens[7][1]
        op = tokens[8][1]
        val = tokens[9][1]
        if tokens[9][0] == 'STRING':
            val = val.strip("'")
        where = (key, op, val)

    return ASTNode('UPDATE', {'table': table, 'field': field, 'value': value, 'where': where})


def parse_create(tokens):
    # CREATE TABLE table (field type, field type, ...)
    tokens = [t for t in tokens if t[0] != 'SEMICOLON']

    if tokens[1][1] != 'TABLE':
        raise ValueError("Expected TABLE keyword after CREATE")

    table = tokens[2][1]

    if tokens[3][0] != 'LPAREN':
        raise ValueError("Expected '(' after table name")

    fields = []
    i = 4
    # parse fields and types till RPAREN
    while tokens[i][0] != 'RPAREN':
        if tokens[i][0] == 'COMMA':
            i += 1
            continue
        field_name = tokens[i][1]
        field_type = tokens[i+1][1]
        fields.append((field_name, field_type))
        i += 2

    return ASTNode('CREATE', {'table': table, 'fields': fields})
