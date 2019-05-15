#!/usr/bin/env/python

'''
Note Parser Web API
'''

import os
import json

from flask import Flask, request, render_template, send_from_directory

from note_parser.todo_tools import get_todos, mark_todo, stamp_notes
from note_parser.search_tools import search_notes, get_context
from note_parser.question_tools import get_questions
from note_parser.tag_tools import get_tags
from note_parser.utils.config import get_notes_config
from note_parser.utils.render import get_file_content, get_rendered_markdown
from note_parser.utils.typeahead import get_typeahead_suggestions

app = Flask(__name__)

NOTES_CONFIG = get_notes_config()


@app.route('/', methods=['GET'])
def show_ui():

    all_directories = ['ALL']
    for subdir in os.walk(NOTES_CONFIG['notes_directory']):
        subdir_path = subdir[0][len(NOTES_CONFIG['notes_directory']) + 1:]
        if '.git' in subdir_path or not subdir_path:
            continue
        elif len(subdir_path.split('/')) > 2:
            continue
        else:
            all_directories.append(subdir_path)

    return render_template('index.j2', all_directories=all_directories)


@app.route('/js/<path:path>', methods=['GET', 'POST'])
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>', methods=['GET', 'POST'])
def send_css(path):
    return send_from_directory('css', path)


@app.route('/get_todos', methods=['GET'])
def get_current_todos():

    status = request.args.get('status')
    directory_filter = request.args.get('directory_filter')
    query_string = request.args.get('query_string')
    sort_by = request.args.get('sort_by')
    if directory_filter == 'ALL':
        directory_filter = None

    return json.dumps(get_todos(
                notes_directory=NOTES_CONFIG['notes_directory'],
                todo_status=status, directory_filter=directory_filter,
                query_string=query_string, sort_by=sort_by))


@app.route('/get_questions', methods=['GET'])
def fetch_questions():

    status = request.args.get('status', 'all')
    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    return json.dumps(get_questions(
                notes_directory=NOTES_CONFIG['notes_directory'],
                question_status=status, directory_filter=directory_filter))


@app.route('/get_tags', methods=['GET'])
def fetch_tags():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    return json.dumps(get_tags(
                notes_directory=NOTES_CONFIG['notes_directory'],
                directory_filter=directory_filter))


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


@app.route('/render', methods=['GET'])
def send_rendered_note():

    file_path = NOTES_CONFIG['notes_directory'] + request.args.get('path')
    file_content = get_file_content(file_path)
    return render_template('viewer.j2', file_content=file_content)


@app.route('/mark_todo', methods=['GET'])
def mark_todo_status():

    filename = request.args.get('filename')
    line_number = int(request.args.get('line_number'))
    status = request.args.get('status')

    # Allow Relative paths within notes dir to be specified
    if NOTES_CONFIG['notes_directory'] not in filename:
        filename = NOTES_CONFIG['notes_directory'] + filename

    return mark_todo(filename, line_number, status)


@app.route('/typeahead', methods=['GET'])
def get_typeahead():

    query_string = request.args.get('query')

    return json.dumps(get_typeahead_suggestions(
        NOTES_CONFIG['ngram_db_directory'],
        query_string))


@app.route('/stamp', methods=['GET'])
def stamp():

    return stamp_notes(NOTES_CONFIG['notes_directory'])


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
