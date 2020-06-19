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

from shorthand.todo_tools import get_todos, mark_todo, analyze_todos
from shorthand.stamping import stamp_notes
from shorthand.search_tools import search_notes, get_note
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
from shorthand.utils.paths import get_relative_path, get_display_path
from shorthand.utils.git import pull_repo
from shorthand.utils.api import wrap_response_data
from shorthand.utils.edit import update_note

from static_elements import static_content


app = Flask(__name__)

SHORTHAND_CONFIG = get_notes_config()
setup_logging(SHORTHAND_CONFIG)
log = logging.getLogger(__name__)


# @app.errorhandler(Exception)
# def handle_exception(e):
#     '''This method is a catch-all for all errors thrown by the server
#     '''

#     # pass through HTTP errors
#     if isinstance(e, HTTPException):
#         return e

#     return json.dumps({'error': str(e)}), 500


@app.route('/js/<path:path>', methods=['GET', 'POST'])
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>', methods=['GET', 'POST'])
def send_css(path):
    return send_from_directory('css', path)


@app.route('/img/<path:path>', methods=['GET', 'POST'])
def send_img(path):
    return send_from_directory('img', path)


@app.route('/api/v1/pull', methods=['GET', 'POST'])
def pull_notes_repo():
    return pull_repo(SHORTHAND_CONFIG['notes_directory'])


@app.route('/', methods=['GET'])
def show_home_page():
    default_directory = SHORTHAND_CONFIG.get('default_directory')
    todos = get_todos(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        todo_status='incomplete',
        directory_filter=default_directory,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    questions = get_questions(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        question_status='unanswered',
        directory_filter=default_directory,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    summary = get_calendar(SHORTHAND_CONFIG['notes_directory'])
    events = []
    for year, year_data in summary.items():
        for month, month_data in year_data.items():
            for day, day_data in month_data.items():
                for event in day_data:
                    formatted_event = {
                        'title': event['event'],
                        'start': f'{year}-{month}-{day}',
                        'url': f'/render?path={event["file_path"]}#line-number-{event["line_number"]}',
                        'type': event['type']
                    }
                    if formatted_event['type'] == 'section':
                        formatted_event['color'] = 'blue'
                    elif formatted_event['type'] == 'completed_todo':
                        formatted_event['color'] = 'red'
                    elif formatted_event['type'] == 'skipped_todo':
                        formatted_event['color'] = 'grey'
                    elif formatted_event['type'] == 'question':
                        formatted_event['color'] = 'purple'
                    elif formatted_event['type'] == 'answer':
                        formatted_event['color'] = 'green'
                    events.append(formatted_event)

    return render_template('home.j2', num_todos=len(todos),
                           num_questions=len(questions),
                           events=json.dumps(events),
                           static_content=static_content)


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
                    grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))

    log.info('Showing the home page')
    return render_template('todos.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


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
                    grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))

    log.info('Showing the questions search page')
    return render_template('questions.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@app.route('/databases', methods=['GET'])
def show_databases():
    record_sets = get_record_sets(
                    notes_directory=SHORTHAND_CONFIG['notes_directory'],
                    grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return render_template('record_sets.j2', record_sets=record_sets,
                           static_content=static_content)


@app.route('/api/v1/todos', methods=['GET'])
def get_current_todos():

    status = request.args.get('status', 'incomplete')
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
                      suppress_future=True, tag=tag,
                      grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    log.info(f'Returning {len(todos)} todo results')

    wrapped_response = wrap_response_data(todos)
    wrapped_response['meta'] = analyze_todos(todos)
    return json.dumps(wrapped_response)


@app.route('/api/v1/mark_todo', methods=['GET'])
def mark_todo_status():

    filename = request.args.get('filename')
    line_number = int(request.args.get('line_number'))
    status = request.args.get('status')

    # Allow Relative paths within notes dir to be specified
    if SHORTHAND_CONFIG['notes_directory'] not in filename:
        filename = SHORTHAND_CONFIG['notes_directory'] + filename

    return mark_todo(filename, line_number, status)


@app.route('/api/v1/questions', methods=['GET'])
def fetch_questions():

    status = request.args.get('status', 'all')
    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None
    log.info(f'Getting {status} questions in directory {directory_filter}')

    questions = get_questions(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        question_status=status, directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    log.info(f'Returning {len(questions)} question results')
    return json.dumps(wrap_response_data(questions))


@app.route('/api/v1/tags', methods=['GET'])
def fetch_tags():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    tags = get_tags(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(tags))


@app.route('/api/v1/calendar', methods=['GET'])
def fetch_calendar():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    calendar = get_calendar(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(calendar)


@app.route('/glossary', methods=['GET'])
def show_glossary():
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
                    grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))

    log.info('Showing the Definitions search page')
    return render_template('glossary.j2',
                           all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@app.route('/api/v1/definitions', methods=['GET'])
def fetch_definitions():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    definitions = get_definitions(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(definitions))


@app.route('/api/v1/record_sets', methods=['GET'])
def fetch_record_sets():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    record_sets = get_record_sets(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=None,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(record_sets))


@app.route('/api/v1/record_set', methods=['GET'])
def fetch_record_set():

    file_path = request.args.get('file_path')
    line_number = int(request.args.get('line_number'))
    parse = request.args.get('parse', 'true')
    if parse.lower() == 'true':
        parse = True
    elif parse.lower() == 'false':
        parse = False
    else:
        raise ValueError(f'Argument parse must be either "true" or "false", found "{parse}"')
    include_config = request.args.get('include_config', 'false')
    if include_config.lower() == 'true':
        include_config = True
    elif include_config.lower() == 'false':
        include_config = False
    else:
        raise ValueError(f'Argument include_config must be either "true" or "false", found "{include_config}"')
    parse_format = request.args.get('parse_format', 'json')

    return get_record_set(
        file_path=file_path,
        line_number=line_number,
        parse=parse,
        parse_format=parse_format,
        include_config=include_config)


@app.route('/search', methods=['GET'])
def show_search_page():
    return render_template('search.j2',
                           static_content=static_content)


@app.route('/api/v1/search', methods=['GET'])
def get_search_results():

    query_string = request.args.get('query_string')
    case_sensitive = request.args.get('case_sensitive')

    search_results = search_notes(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        query_string=query_string,
        case_sensitive=case_sensitive,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(search_results))


@app.route('/api/v1/note', methods=['GET'])
def get_full_note():

    path = request.args.get('path')
    return get_note(SHORTHAND_CONFIG['notes_directory'], path)


@app.route('/api/v1/note', methods=['POST'])
def write_updated_note():

    path = request.args.get('path')
    request.get_data()
    content = request.data.decode('utf-8')

    update_note(SHORTHAND_CONFIG['notes_directory'], path, content)
    return 'Note Updated'


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
    return render_template('viewer.j2', file_content=file_content,
                           toc_content=toc_content,
                           static_content=static_content,
                           file_path=request.args.get('path'))


@app.route('/editor', methods=['GET'])
def show_editor():
    file_path = SHORTHAND_CONFIG['notes_directory'] + request.args.get('path')
    file_content = get_file_content(file_path)
    return render_template('editor.j2', file_content=file_content,
                           file_path=request.args.get('path'),
                           static_content=static_content)


@app.route('/calendar', methods=['GET'])
def show_calendar():

    summary = get_calendar(SHORTHAND_CONFIG['notes_directory'])
    events = []
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

                for event in day_data:
                    formatted_event = {
                        'title': event['event'],
                        'start': f'{year}-{month}-{day}',
                        'url': f'/render?path={event["file_path"]}#line-number-{event["line_number"]}',
                        'type': event['type']
                    }
                    if formatted_event['type'] == 'section':
                        formatted_event['color'] = 'blue'
                    elif formatted_event['type'] == 'completed_todo':
                        formatted_event['color'] = 'red'
                    elif formatted_event['type'] == 'skipped_todo':
                        formatted_event['color'] = 'grey'
                    elif formatted_event['type'] == 'question':
                        formatted_event['color'] = 'purple'
                    elif formatted_event['type'] == 'answer':
                        formatted_event['color'] = 'green'
                    events.append(formatted_event)

    timeline_data = sorted(timeline_data, key=lambda x: x[0])

    return render_template('calendar.j2', events=json.dumps(events),
                           summary=json.dumps(timeline_data),
                           static_content=static_content)


@app.route('/api/v1/toc', methods=['GET'])
def get_toc_data():
    return json.dumps(get_toc(SHORTHAND_CONFIG['notes_directory']))


@app.route('/browse', methods=['GET'])
def show_browse_page():
    toc = get_toc(SHORTHAND_CONFIG['notes_directory'])
    return render_template('browse.j2', toc=json.dumps(toc),
                           static_content=static_content)


@app.route('/api/v1/typeahead', methods=['GET'])
def get_typeahead():

    query_string = request.args.get('query')

    return json.dumps(get_typeahead_suggestions(
        SHORTHAND_CONFIG['ngram_db_directory'],
        query_string))


@app.route('/api/v1/stamp', methods=['GET'])
def stamp():

    return stamp_notes(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        stamp_todos=True, stamp_today=True,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
