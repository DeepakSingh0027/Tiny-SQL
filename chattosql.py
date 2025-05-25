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
        r'where (\w+) (is|equals|equals to|contains|=) (\w+)',
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
                'equals to': '=',
                'contains':'=',
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
    # Match phrases like "id to 1, name = deepak and order to cake into orders"
    m = re.match(fr'{insert_syns} (.+?) (into|in|inside) (\w+)', query)
    if m:
        fields_values_raw = m.group(2)
        table = m.group(3)

        # Normalize separators
        fields_values_raw = fields_values_raw.replace(' and ', ', ')
        
        # Match field-value pairs like "id to 1", "name = deepak", "order equals to cake", etc.
        pairs = re.findall(r'(\w+)\s*(=|to|is|equals|equals to)\s*\'?(\w+)\'?', fields_values_raw)

        fields = []
        values = []

        for field, _, value in pairs:
            fields.append(field)
            values.append(value)

        fields_str = ','.join(fields)
        values_str = ','.join(f"'{v}'" if not v.isdigit() else v for v in values)

        return f"INSERT INTO {table}({fields_str}) VALUES ({values_str});"


    # Rule 5: Create synonyms
    create_syns = r'(create|make)'
    m = re.match(fr'{create_syns} table (\w+) (with attribute|with|having) ([\w ,and]+)', query)
    if m:
        table = m.group(2)
        raw_fields = clean_fields(m.group(4))
        field_list = ', '.join([f"{field.strip()} VARCHAR" for field in raw_fields.split(',')])
        return f"CREATE TABLE {table} ({field_list});"


    # Rule 6: Update synonyms
    update_syns = r'(update|change|modify|replace)'
    m = re.search(fr'{update_syns} (\w+)\s+(set|change|replace)?\s*(\w+)\s*(=|to|equals|equals to)\s*\'?(\w+)\'?.*?(where|whose)?\s*(\w+)?\s*(is|equals|=)?\s*\'?(\w+)\'?', query)
    if m:
        table = m.group(2)
        field = m.group(4)
        value = m.group(6)
        where_clause = ''
        if m.group(7) and m.group(8) and m.group(10):
            where_field = m.group(8)
            where_value = m.group(10)
            where_clause = f" WHERE {where_field} = '{where_value}'"
        return f"UPDATE {table} SET {field} = '{value}'{where_clause};"


    # Rule 7: Delete synonyms
    delete_syns = r'(delete|remove)'
    # Covers variations like "from orders", "orders", "where", "whose", and flexible condition operators
    m = re.match(fr'{delete_syns} (from )?(\w+)( (where|whose) (\w+) (is|=|equals|equals to) ?\'?(\w+)\'?)?', query)
    if m:
        table = m.group(2)
        where_clause = ''
        if m.group(5) and m.group(6) and m.group(7) and m.group(8):
            where_field = m.group(6)
            operator_word = m.group(7)
            value = m.group(8)
            op_map = {
                'is': '=',
                '=': '=',
                'equals': '=',
                'equals to': '='
            }
            operator = op_map.get(operator_word, '=')
            where_clause = f" WHERE {where_field} {operator} '{value}'"
        return f"DELETE FROM {table}{where_clause};"


    return nl_query  # fallback, treat as raw SQL
