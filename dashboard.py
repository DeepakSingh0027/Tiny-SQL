from flask import Flask, render_template, request, jsonify
from lexer import tokenize
from parser import parse
from executor import execute
import io
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_query', methods=['POST'])
def run_query():
    query = request.form['query']

    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()

    try:
        tokens = tokenize(query)
        ast = parse(tokens)
        execute(ast)  # Should perform semantic checks (types, unknown fields, etc.)
        output = mystdout.getvalue()
        success = True
    except Exception as e:
        output = f"Error: {str(e)}"
        success = False

    sys.stdout = old_stdout

    return jsonify({'success': success, 'output': output})

if __name__ == '__main__':
    app.run(debug=True)
