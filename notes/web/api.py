#!/usr/bin/env/python

'''
Note Parser Web API
'''

import json

from flask import Flask, request  # , render_template, send_from_directory

from note_parser.todo_tools import get_todos  # , mark_todo
from note_parser.search_tools import search_notes, get_context
from note_parser.utils.config import get_notes_config

app = Flask(__name__)

NOTES_CONFIG = get_notes_config()


@app.route('/get_todos/<path:path>', methods=['GET'])
def get_current_todos(path):
    """Main Route that displays the documentation"""

    return json.dumps(get_todos(
                notes_directory=NOTES_CONFIG['notes_directory'],
                todo_status=path))


@app.route('/search', methods=['GET'])
def get_search_results():

    query_string = request.args.get('query_string')
    case_sensitive = request.args.get('case_sensitive')

    return json.dumps(search_notes(
                notes_directory=NOTES_CONFIG['notes_directory'],
                query_string=query_string,
                case_sensitive=case_sensitive))


@app.route('/get_context', methods=['GET'])
def get_line_context():

    filename = request.args.get('filename')
    line_number = int(request.args.get('line_number'))
    width = int(request.args.get('width', 5))

    return json.dumps(get_context(filename, line_number, width))


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
