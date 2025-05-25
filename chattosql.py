import re

def chat_to_sql(nl_query):
    query = nl_query.lower().strip()
    query = query.rstrip('.?')

    # Helper: clean fields string into comma separated fields
    def clean_fields(fields_str):
        # Cut off everything after ' of ' (with spaces to avoid partial matches)
        if ' of ' in fields_str:
            fields_str = fields_str.split(' of ')[0].strip()
        
        fields = [f.strip() for f in re.split(r',|and', fields_str) if f.strip()]
        return ','.join(fields)


    # Helper: extract table name after keywords 'from', 'all', or 'in'
    def extract_table(q):
        pattern = r'\b(from|all|in|of)\b\s+(\w+)'
        match = re.search(pattern, q, re.IGNORECASE)
        if match:
            return match.group(2)
        return None

    select_syns = r'(could you show me|please show|please display|please list|please fetch|get me|could you display|show me|show|display|list|fetch|get)'

    # Rule 1: Select all from table (detect table name anywhere after keywords)
    m = re.match(fr'{select_syns} all', query)
    if m:
        table = extract_table(query)
        if table:
            return f"SELECT * FROM {table};"

    # Rule 2: Select specific fields from table (detect table name anywhere after keywords)
    m = re.match(fr'{select_syns}\s+([\w ,and]+)', query)
    if m:
        fields = clean_fields(m.group(2))
        table = extract_table(query)
        if table:
            return f"SELECT {fields} FROM {table};"

    # Rule 3: Select with condition: where ... is/equals/above/below/greater than/less than
    cond_patterns = [
        r'where (\w+) (is|equals|=) (\w+)',
        r'where (\w+) (above|greater than|>) (\w+)',
        r'where (\w+) (below|less than|<) (\w+)',
        r'where (\w+) (>=) (\w+)',
        r'where (\w+) (<=) (\w+)',
        r'where (\w+) (<>|!=) (\w+)'
    ]
    for pattern in cond_patterns:
        m = re.search(pattern, query)
        if m:
            key, op_word, val = m.group(1), m.group(2), m.group(3)
            op_map = {
                'is': '=',
                'equals': '=',
                '=': '=',
                'above': '>',
                'greater than': '>',
                '>': '>',
                'below': '<',
                'less than': '<',
                '<': '<',
                '>=': '>=',
                '<=': '<=',
                '<>': '<>',
                '!=': '<>'
            }
            op = op_map[op_word]
            # Remove condition phrase from query to parse base select
            base_query = re.sub(pattern, '', query).strip()
            # Extract table and fields from base_query
            m2 = re.match(fr'{select_syns} ([\w ,and]+)?', base_query)
            if m2:
                fields_raw = m2.group(1) or '*'
                fields = clean_fields(fields_raw) if fields_raw != '*' else '*'
                table = extract_table(base_query)
                if table:
                    return f"SELECT {fields} FROM {table} WHERE {key} {op} {val};"

    # Rule 4: Insert synonyms
    insert_syns = r'(add|insert|put)'
    m = re.match(fr'{insert_syns} into (\w+) values? \((.+)\)', query)
    if m:
        table = m.group(2)
        values = m.group(3)
        return f"INSERT INTO {table} VALUES ({values});"

    # Rule 5: Create synonyms
    create_syns = r'(create|make)'
    m = re.match(fr'{create_syns} table (\w+) (with|having) ([\w ,and]+)', query)
    if m:
        table = m.group(2)
        fields = clean_fields(m.group(4))
        return f"CREATE TABLE {table} ({fields});"

    # Rule 6: Update synonyms
    update_syns = r'(update|change|modify)'
    m = re.match(fr'{update_syns} (\w+) set (\w+) = \'?(\w+)\'?( where (\w+) = \'?(\w+)\'?)?', query)
    if m:
        table = m.group(2)
        field = m.group(3)
        value = m.group(4)
        where_clause = ''
        if m.group(5):
            where_field = m.group(6)
            where_value = m.group(7)
            where_clause = f" WHERE {where_field} = '{where_value}'"
        return f"UPDATE {table} SET {field} = '{value}'{where_clause};"

    # Rule 7: Delete synonyms
    delete_syns = r'(delete|remove)'
    m = re.match(fr'{delete_syns} (from )?(\w+)( where (\w+) = \'?(\w+)\')?', query)
    if m:
        table = m.group(2)
        where_clause = ''
        if m.group(4):
            where_field = m.group(4)
            where_value = m.group(5)
            where_clause = f" WHERE {where_field} = '{where_value}'"
        return f"DELETE FROM {table}{where_clause};"

    return nl_query  # fallback, treat as raw SQL
