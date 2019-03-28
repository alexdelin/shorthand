#!/usr/bin/env/python

'''
Note Parser Web API
'''

import os
import json

from flask import Flask, request, render_template, send_from_directory

from note_parser.todo_tools import get_todos, mark_todo, stamp_notes
from note_parser.search_tools import search_notes, get_context
from note_parser.utils.config import get_notes_config

app = Flask(__name__)

NOTES_CONFIG = get_notes_config()


@app.route('/', methods=['GET'])
def show_ui():

    all_directories = ['ALL'] + [subdir for subdir in os.listdir(NOTES_CONFIG['notes_directory']) if os.path.isdir(NOTES_CONFIG['notes_directory'] + '/' + subdir)]

    return render_template('index.j2', all_directories=all_directories)


@app.route('/js/<path:path>', methods=['GET', 'POST'])
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>', methods=['GET', 'POST'])
def send_css(path):
    return send_from_directory('css', path)


@app.route('/get_todos', methods=['GET'])
def get_current_todos():
    """Main Route that displays the documentation"""

    status = request.args.get('status')
    directory_filter = request.args.get('directory_filter')
    print(directory_filter)
    if directory_filter == 'ALL':
        directory_filter = None

    print(directory_filter)

    return json.dumps(get_todos(
                notes_directory=NOTES_CONFIG['notes_directory'],
                todo_status=status, directory_filter=directory_filter))


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

    # Allow Relative paths within notes dir to be specified
    if NOTES_CONFIG['notes_directory'] not in filename:
        filename = NOTES_CONFIG['notes_directory'] + filename

    return json.dumps(get_context(filename, line_number, width))


@app.route('/mark_todo', methods=['GET'])
def mark_todo_status():

    filename = request.args.get('filename')
    line_number = int(request.args.get('line_number'))
    status = request.args.get('status')

    # Allow Relative paths within notes dir to be specified
    if NOTES_CONFIG['notes_directory'] not in filename:
        filename = NOTES_CONFIG['notes_directory'] + filename

    return mark_todo(filename, line_number, status)


@app.route('/stamp', methods=['GET'])
def stamp():

    return stamp_notes(NOTES_CONFIG['notes_directory'])


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
