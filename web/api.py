#!/usr/bin/env/python

'''
Shorthand Web API
'''

import os
import time
import json
import logging
from datetime import datetime

from werkzeug.exceptions import HTTPException
from flask import Flask, request, render_template, send_from_directory, abort

from shorthand.todo_tools import get_todos, mark_todo, stamp_notes
from shorthand.search_tools import search_notes, get_context, get_note
from shorthand.question_tools import get_questions
from shorthand.definition_tools import get_definitions
from shorthand.tag_tools import get_tags
from shorthand.calendar_tools import get_calendar
from shorthand.toc_tools import get_toc
from shorthand.rec_tools import get_record_sets, get_record_set
from shorthand.utils.config import get_notes_config
from shorthand.utils.logging import setup_logging
from shorthand.utils.render import get_file_content, get_rendered_markdown
from shorthand.utils.typeahead import get_typeahead_suggestions


app = Flask(__name__)

SHORTHAND_CONFIG = get_notes_config()
setup_logging(SHORTHAND_CONFIG)
log = logging.getLogger(__name__)


@app.errorhandler(Exception)
def handle_exception(e):
    '''This method is a catch-all for all errors thrown by the server
    '''

    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    return json.dumps({'error': str(e)}), 500


@app.route('/js/<path:path>', methods=['GET', 'POST'])
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>', methods=['GET', 'POST'])
def send_css(path):
    return send_from_directory('css', path)


@app.route('/img/<path:path>', methods=['GET', 'POST'])
def send_img(path):
    return send_from_directory('img', path)


@app.route('/', methods=['GET'])
def show_home_page():
    default_directory = SHORTHAND_CONFIG.get('default_directory')
    todos = get_todos(notes_directory=SHORTHAND_CONFIG['notes_directory'],
                      todo_status='incomplete',
                      directory_filter=default_directory,
                      grep_path=SHORTHAND_CONFIG.get('grep_path'))
    questions = get_questions(
                    notes_directory=SHORTHAND_CONFIG['notes_directory'],
                    question_status='unanswered',
                    directory_filter=default_directory,
                    grep_path=SHORTHAND_CONFIG.get('grep_path'))
    summary = get_calendar(SHORTHAND_CONFIG['notes_directory'])
    events = []
    for year, year_data in summary.items():
        for month, month_data in year_data.items():
            for day, day_data in month_data.items():
                for event in day_data:
                    events.append({
                            'title': event['event'],
                            'start': f'{year}-{month}-{day}',
                            'url': f'/render?path={event["file_path"]}#{event["element_id"]}'
                        })
    return render_template('home.j2', num_todos=todos['count'],
                           num_questions=questions['count'],
                           events=json.dumps(events))


@app.route('/todos', methods=['GET'])
def show_todos_page():

    all_directories = ['ALL']
    for subdir in os.walk(SHORTHAND_CONFIG['notes_directory']):
        subdir_path = subdir[0][len(SHORTHAND_CONFIG['notes_directory']) + 1:]
        if '.git' in subdir_path or not subdir_path:
            continue
        elif len(subdir_path.split('/')) > 2:
            continue
        else:
            all_directories.append(subdir_path)
    default_directory = SHORTHAND_CONFIG.get('default_directory')
    tags = get_tags(SHORTHAND_CONFIG['notes_directory'],
                    grep_path=SHORTHAND_CONFIG.get('grep_path'))

    log.info('Showing the home page')
    return render_template('todos.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags)


@app.route('/questions', methods=['GET'])
def show_questions():

    all_directories = ['ALL']
    for subdir in os.walk(SHORTHAND_CONFIG['notes_directory']):
        subdir_path = subdir[0][len(SHORTHAND_CONFIG['notes_directory']) + 1:]
        if '.git' in subdir_path or not subdir_path:
            continue
        elif len(subdir_path.split('/')) > 2:
            continue
        else:
            all_directories.append(subdir_path)
    default_directory = SHORTHAND_CONFIG.get('default_directory')
    tags = get_tags(SHORTHAND_CONFIG['notes_directory'],
                    grep_path=SHORTHAND_CONFIG.get('grep_path'))

    log.info('Showing the questions search page')
    return render_template('questions.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags)


@app.route('/get_todos', methods=['GET'])
def get_current_todos():

    status = request.args.get('status')
    directory_filter = request.args.get('directory_filter')
    query_string = request.args.get('query_string')
    sort_by = request.args.get('sort_by')
    tag = request.args.get('tag')

    if directory_filter == 'ALL':
        directory_filter = None
    if tag == 'ALL':
        tag = None

    todos = get_todos(notes_directory=SHORTHAND_CONFIG['notes_directory'],
                      todo_status=status, directory_filter=directory_filter,
                      query_string=query_string, sort_by=sort_by,
                      suppress_future=True, tag=tag, grep_path=SHORTHAND_CONFIG.get('grep_path'))
    log.info(f'Returning {len(todos)} todo results')
    return json.dumps(todos)


@app.route('/get_questions', methods=['GET'])
def fetch_questions():

    status = request.args.get('status', 'all')
    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None
    log.info(f'Getting {status} questions in directory {directory_filter}')

    questions = get_questions(
                    notes_directory=SHORTHAND_CONFIG['notes_directory'],
                    question_status=status, directory_filter=directory_filter,
                    grep_path=SHORTHAND_CONFIG.get('grep_path'))
    log.info(f'Returning {len(questions)} question results')
    return json.dumps(questions)


@app.route('/get_tags', methods=['GET'])
def fetch_tags():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    return json.dumps(get_tags(
                notes_directory=SHORTHAND_CONFIG['notes_directory'],
                directory_filter=directory_filter,
                grep_path=SHORTHAND_CONFIG.get('grep_path')))


@app.route('/get_calendar', methods=['GET'])
def fetch_calendar():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    return json.dumps(get_calendar(
                notes_directory=SHORTHAND_CONFIG['notes_directory'],
                directory_filter=directory_filter),
                grep_path=SHORTHAND_CONFIG.get('grep_path'))


@app.route('/get_definitions', methods=['GET'])
def fetch_definitions():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    return json.dumps(get_definitions(
                notes_directory=SHORTHAND_CONFIG['notes_directory'],
                directory_filter=directory_filter),
                grep_path=SHORTHAND_CONFIG.get('grep_path'))


@app.route('/get_record_sets', methods=['GET'])
def fetch_record_sets():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    return json.dumps(get_record_sets(
                notes_directory=SHORTHAND_CONFIG['notes_directory'],
                directory_filter=None),
                grep_path=SHORTHAND_CONFIG.get('grep_path'))


@app.route('/get_record_set', methods=['GET'])
def fetch_record_set():

    file_path = request.args.get('file_path')
    line_number = int(request.args.get('line_number'))
    parse = request.args.get('parse', 'true')
    if parse.lower() == 'true':
        parse = True
    elif parse.lower() == 'false':
        parse = False
    else:
        abort(500, f'Argument parse must be either "true" or "false", found "{parse}"')
    parse_format = request.args.get('parse_format', 'json')

    return get_record_set(
                file_path=file_path,
                line_number=line_number,
                parse=parse,
                parse_format=parse_format)


@app.route('/search', methods=['GET'])
def get_search_results():

    query_string = request.args.get('query_string')
    case_sensitive = request.args.get('case_sensitive')

    return json.dumps(search_notes(
                notes_directory=SHORTHAND_CONFIG['notes_directory'],
                query_string=query_string,
                case_sensitive=case_sensitive,
                grep_path=SHORTHAND_CONFIG.get('grep_path')))


@app.route('/get_context', methods=['GET'])
def get_line_context():

    filename = request.args.get('filename')
    line_number = int(request.args.get('line_number'))
    width = int(request.args.get('width', 5))

    # Allow Relative paths within notes dir to be specified
    if SHORTHAND_CONFIG['notes_directory'] not in filename:
        filename = SHORTHAND_CONFIG['notes_directory'] + filename

    return json.dumps(get_context(filename, line_number, width))


@app.route('/get_note', methods=['GET'])
def get_full_note():

    path = request.args.get('path')

    if SHORTHAND_CONFIG['notes_directory'] not in path:
        path = SHORTHAND_CONFIG['notes_directory'] + path

    return get_note(path)


@app.route('/render', methods=['GET'])
def send_rendered_note():

    file_path = SHORTHAND_CONFIG['notes_directory'] + request.args.get('path')
    file_content = get_file_content(file_path)
    file_content, toc_content = get_rendered_markdown(file_content)
    file_content = file_content.replace("\\", "\\\\")
    file_content = file_content.replace('\n', '\\n')
    file_content = file_content.replace("'", "\\'")
    toc_content = toc_content.replace("\\", "\\\\")
    toc_content = toc_content.replace('\n', '\\n')
    toc_content = toc_content.replace("'", "\\'")
    return render_template('viewer.j2', file_content=file_content, toc_content=toc_content)


@app.route('/calendar', methods=['GET'])
def show_calendar():

    summary = get_calendar(SHORTHAND_CONFIG['notes_directory'])
    events = []
    for year, year_data in summary.items():
        for month, month_data in year_data.items():
            for day, day_data in month_data.items():
                for event in day_data:
                    events.append({
                            'title': event['event'],
                            'start': f'{year}-{month}-{day}',
                            'url': f'/render?path={event["file_path"]}#{event["element_id"]}'
                        })

    return render_template('calendar.j2', events=json.dumps(events))


@app.route('/chart', methods=['GET'])
def show_chart():

    summary = get_calendar(SHORTHAND_CONFIG['notes_directory'])
    timeline_data = []
    for year, year_data in summary.items():
        for month, month_data in year_data.items():
            for day, day_data in month_data.items():
                timeline_data.append([
                    int(datetime.strptime(
                        f'{year}-{month}-{day}T12:00:00',
                        '%Y-%m-%dT%H:%M:%S').strftime("%s")) * 1000,
                    len(day_data)
                    ])
    timeline_data = sorted(timeline_data, key=lambda x: x[0])

    return render_template('chart.j2', summary=json.dumps(timeline_data))


@app.route('/toc', methods=['GET'])
def get_toc_data():
    return json.dumps(get_toc(SHORTHAND_CONFIG['notes_directory']))


@app.route('/browse', methods=['GET'])
def show_browse_page():
    toc = get_toc(SHORTHAND_CONFIG['notes_directory'])
    return render_template('browse.j2', toc=json.dumps(toc))


@app.route('/mark_todo', methods=['GET'])
def mark_todo_status():

    filename = request.args.get('filename')
    line_number = int(request.args.get('line_number'))
    status = request.args.get('status')

    # Allow Relative paths within notes dir to be specified
    if SHORTHAND_CONFIG['notes_directory'] not in filename:
        filename = SHORTHAND_CONFIG['notes_directory'] + filename

    return mark_todo(filename, line_number, status)


@app.route('/typeahead', methods=['GET'])
def get_typeahead():

    query_string = request.args.get('query')

    return json.dumps(get_typeahead_suggestions(
        SHORTHAND_CONFIG['ngram_db_directory'],
        query_string))


@app.route('/stamp', methods=['GET'])
def stamp():

    return stamp_notes(
                notes_directory=SHORTHAND_CONFIG['notes_directory'],
                stamp_todos=True, stamp_today=True,
                grep_path=SHORTHAND_CONFIG.get('grep_path'))


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
