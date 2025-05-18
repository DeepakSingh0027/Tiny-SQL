from lexer import tokenize
from parser import parse
from executor import execute

def main():
    print("Welcome to TinySQL CLI. Type 'exit;' to quit.")
    while True:
        query = input("tinySQL> ").strip()
        if query.lower() in ['exit', 'exit;']:
            break
        try:
            tokens = tokenize(query)
            ast = parse(tokens)
            execute(ast)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
