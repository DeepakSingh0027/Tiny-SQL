import re

TOKEN_SPEC = [
    ('NUMBER',   r'\d+(\.\d*)?'),
    ('STRING',   r'\'[^\']*\''),  # string literals in single quotes
    ('COMMA',    r','),           # keep commas for parsing
    ('SEMICOLON',r';'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('OP',       r'=|<>|<|>|<=|>='),
    ('STAR',     r'\*'),
    ('IDENT',    r'[A-Za-z_][A-Za-z0-9_]*'),
    ('SKIP',     r'[ \t]+'),      # skip spaces and tabs
    ('NEWLINE',  r'\n'),          # skip newlines
]

TOKEN_RE = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC), re.IGNORECASE)

def tokenize(query):
    tokens = []
    for match in TOKEN_RE.finditer(query):
        kind = match.lastgroup
        value = match.group()
        if kind == 'STRING':
            value = value.strip("'")
        if kind not in ['SKIP', 'NEWLINE']:
            tokens.append((kind, value.upper() if kind == 'IDENT' else value))
    return tokens
