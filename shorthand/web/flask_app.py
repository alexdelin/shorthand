#!/usr/bin/env/python

'''
Shorthand Web API
'''

import os
import json
import logging

from flask import Flask, Blueprint, request, render_template, \
                  send_from_directory
from werkzeug.exceptions import HTTPException

from shorthand.notes import _get_note, _update_note
from shorthand.stamping import _stamp_notes
from shorthand.search import _search_notes, _filename_search, \
                                   _record_file_view
from shorthand.tags import _get_tags
from shorthand.calendar import _get_calendar
from shorthand.toc import _get_toc
from shorthand.elements.todos import _get_todos, _mark_todo, analyze_todos
from shorthand.elements.questions import _get_questions
from shorthand.elements.definitions import _get_definitions
from shorthand.elements.record_sets import _get_record_sets, _get_record_set
from shorthand.elements.locations import _get_locations
from shorthand.utils.git import pull_repo
from shorthand.utils.api import wrap_response_data
from shorthand.utils.config import get_notes_config, CONFIG_FILE_LOCATION
from shorthand.utils.logging import setup_logging
from shorthand.frontend.typeahead import _get_typeahead_suggestions
from shorthand.frontend.render import get_rendered_markdown
from shorthand.web.static_elements import static_content


app = Flask(__name__)

app.config['config_path'] = CONFIG_FILE_LOCATION
SHORTHAND_CONFIG = get_notes_config(app.config['config_path'])
setup_logging(SHORTHAND_CONFIG)
log = logging.getLogger(__name__)


shorthand_api_blueprint = Blueprint('shorthand_api_blueprint', __name__,
                                    url_prefix='/api/v1')


@shorthand_api_blueprint.errorhandler(Exception)
def handle_exception(e):
    '''This method is a catch-all for all errors thrown by the server
    '''

    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    return json.dumps({'error': str(e)}), 500


@shorthand_api_blueprint.route('/config', methods=['GET'])
def get_server_config():
    return json.dumps(SHORTHAND_CONFIG)


@shorthand_api_blueprint.route('/pull', methods=['GET', 'POST'])
def pull_notes_repo():
    return pull_repo(SHORTHAND_CONFIG['notes_directory'])


@shorthand_api_blueprint.route('/locations', methods=['GET'])
def get_gps_locations():

    directory_filter = request.args.get('directory_filter')

    locations = _get_locations(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))

    wrapped_response = wrap_response_data(locations)
    return json.dumps(wrapped_response)


@shorthand_api_blueprint.route('/files', methods=['GET'])
def get_files():

    query_string = request.args.get('query_string', None)
    prefer_recent = request.args.get('prefer_recent', 'True')
    if prefer_recent.lower() == 'false':
        prefer_recent = False
    elif prefer_recent.lower() == 'true':
        prefer_recent = True
    else:
        raise ValueError(f'Invalid value {prefer_recent} for `prefer_recent`')
    case_sensitive = request.args.get('case_sensitive', 'False')
    if case_sensitive.lower() == 'false':
        case_sensitive = False
    elif case_sensitive.lower() == 'true':
        case_sensitive = True
    else:
        raise ValueError(f'Invalid value {case_sensitive} '
                         f'for `case_sensitive`')

    files = _filename_search(
                notes_directory=SHORTHAND_CONFIG['notes_directory'],
                prefer_recent_files=prefer_recent,
                cache_directory=SHORTHAND_CONFIG['cache_directory'],
                query_string=query_string, case_sensitive=case_sensitive,
                grep_path=SHORTHAND_CONFIG['grep_path'],
                find_path=SHORTHAND_CONFIG.get('find_path', 'find'))

    return json.dumps(files)


@shorthand_api_blueprint.route('/record_view', methods=['POST'])
def record_file_view_api():

    relative_path = request.args.get('relative_path')
    if not relative_path:
        raise ValueError('No Relative Path Provided')
    _record_file_view(cache_directory=SHORTHAND_CONFIG['cache_directory'],
                      relative_path=relative_path,
                      history_limit=SHORTHAND_CONFIG.get('view_history_limit',
                                                         100))
    return 'ack'


@shorthand_api_blueprint.route('/todos', methods=['GET'])
def get_current_todos():

    status = request.args.get('status', 'incomplete')
    directory_filter = request.args.get('directory_filter')
    query_string = request.args.get('query_string')
    sort_by = request.args.get('sort_by')
    tag = request.args.get('tag')
    #TODO - Add Suppresss future option

    if directory_filter == 'ALL':
        directory_filter = None
    if tag == 'ALL':
        tag = None

    todos = _get_todos(notes_directory=SHORTHAND_CONFIG['notes_directory'],
                       todo_status=status, directory_filter=directory_filter,
                       query_string=query_string, sort_by=sort_by,
                       suppress_future=True, tag=tag,
                       grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    log.info(f'Returning {len(todos)} todo results')

    wrapped_response = wrap_response_data(todos)
    wrapped_response['meta'] = analyze_todos(todos)
    return json.dumps(wrapped_response)


@shorthand_api_blueprint.route('/mark_todo', methods=['GET'])
def mark_todo_status():

    filename = request.args.get('filename')
    line_number = int(request.args.get('line_number'))
    status = request.args.get('status')

    # Allow Relative paths within notes dir to be specified
    if SHORTHAND_CONFIG['notes_directory'] not in filename:
        filename = SHORTHAND_CONFIG['notes_directory'] + filename

    return _mark_todo(filename, line_number, status)


@shorthand_api_blueprint.route('/questions', methods=['GET'])
def fetch_questions():

    status = request.args.get('status', 'all')
    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None
    log.info(f'Getting {status} questions in directory {directory_filter}')

    questions = _get_questions(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        question_status=status, directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    log.info(f'Returning {len(questions)} question results')
    return json.dumps(wrap_response_data(questions))


@shorthand_api_blueprint.route('/tags', methods=['GET'])
def fetch_tags():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    tags = _get_tags(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(tags))


@shorthand_api_blueprint.route('/calendar', methods=['GET'])
def fetch_calendar():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    calendar = _get_calendar(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(calendar)


@shorthand_api_blueprint.route('/definitions', methods=['GET'])
def fetch_definitions():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    definitions = _get_definitions(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(definitions))


@shorthand_api_blueprint.route('/record_sets', methods=['GET'])
def fetch_record_sets():

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    record_sets = _get_record_sets(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=None,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(record_sets))


@shorthand_api_blueprint.route('/record_set', methods=['GET'])
def fetch_record_set():

    file_path = request.args.get('file_path')
    line_number = int(request.args.get('line_number'))
    parse = request.args.get('parse', 'true')
    if parse.lower() == 'true':
        parse = True
    elif parse.lower() == 'false':
        parse = False
    else:
        raise ValueError(f'Argument parse must be either "true" or "false", '
                         f'found "{parse}"')
    include_config = request.args.get('include_config', 'false')
    if include_config.lower() == 'true':
        include_config = True
    elif include_config.lower() == 'false':
        include_config = False
    else:
        raise ValueError(f'Argument include_config must be either "true" or '
                         f'"false", found "{include_config}"')
    parse_format = request.args.get('parse_format', 'json')

    return _get_record_set(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        file_path=file_path,
        line_number=line_number,
        parse=parse,
        parse_format=parse_format,
        include_config=include_config)


@shorthand_api_blueprint.route('/search', methods=['GET'])
def get_search_results():

    query_string = request.args.get('query_string')
    case_sensitive = request.args.get('case_sensitive')

    search_results = _search_notes(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        query_string=query_string,
        case_sensitive=case_sensitive,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(search_results))


@shorthand_api_blueprint.route('/note', methods=['GET'])
def get_full_note():

    path = request.args.get('path')
    return _get_note(SHORTHAND_CONFIG['notes_directory'], path)


@shorthand_api_blueprint.route('/note', methods=['POST'])
def write_updated_note():

    path = request.args.get('path')
    request.get_data()
    content = request.data.decode('utf-8')

    _update_note(SHORTHAND_CONFIG['notes_directory'], path, content)
    return 'Note Updated'


@shorthand_api_blueprint.route('/toc', methods=['GET'])
def get_toc_data():
    return json.dumps(_get_toc(SHORTHAND_CONFIG['notes_directory']))


@shorthand_api_blueprint.route('/typeahead', methods=['GET'])
def get_typeahead():

    query_string = request.args.get('query')

    return json.dumps(_get_typeahead_suggestions(
        SHORTHAND_CONFIG['ngram_db_directory'],
        query_string))


@shorthand_api_blueprint.route('/stamp', methods=['GET'])
def stamp():

    return _stamp_notes(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        stamp_todos=True, stamp_today=True,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))


app.register_blueprint(shorthand_api_blueprint)


shorthand_ui_blueprint = Blueprint('shorthand_ui_blueprint', __name__,
                                   static_folder='static',
                                   template_folder='templates')


@shorthand_ui_blueprint.route('/js/<path:path>', methods=['GET', 'POST'])
def send_js(path):
    return send_from_directory('static/js', path)


@shorthand_ui_blueprint.route('/css/<path:path>', methods=['GET', 'POST'])
def send_css(path):
    return send_from_directory('static/css', path)


@shorthand_ui_blueprint.route('/img/<path:path>', methods=['GET', 'POST'])
def send_img(path):
    return send_from_directory('static/img', path)


@shorthand_ui_blueprint.route('/', methods=['GET'])
def show_home_page():
    default_directory = SHORTHAND_CONFIG.get('default_directory')
    todos = _get_todos(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        todo_status='incomplete',
        directory_filter=default_directory,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    questions = _get_questions(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        question_status='unanswered',
        directory_filter=default_directory,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    summary = _get_calendar(SHORTHAND_CONFIG['notes_directory'])
    events = []
    for year, year_data in summary.items():
        for month, month_data in year_data.items():
            for day, day_data in month_data.items():
                for event in day_data:
                    formatted_event = {
                        'title': event['event'],
                        'start': f'{year}-{month}-{day}',
                        'url': f'/render?path={event["file_path"]}'
                               f'#line-number-{event["line_number"]}',
                        'type': event['type']
                    }
                    if formatted_event['type'] == 'section':
                        formatted_event['color'] = 'black'
                    elif formatted_event['type'] == 'incomplete_todo':
                        formatted_event['color'] = 'red'
                    elif formatted_event['type'] == 'completed_todo':
                        formatted_event['color'] = 'blue'
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


@shorthand_ui_blueprint.route('/todos', methods=['GET'])
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
    tags = _get_tags(SHORTHAND_CONFIG['notes_directory'],
                     grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))

    log.info('Showing the home page')
    return render_template('todos.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/questions', methods=['GET'])
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
    tags = _get_tags(SHORTHAND_CONFIG['notes_directory'],
                     grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))

    log.info('Showing the questions search page')
    return render_template('questions.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/databases', methods=['GET'])
def show_databases():
    record_sets = _get_record_sets(
                    notes_directory=SHORTHAND_CONFIG['notes_directory'],
                    grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return render_template('record_sets.j2', record_sets=record_sets,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/locations', methods=['GET'])
def show_locations():
    return render_template('locations.j2', static_content=static_content)


@shorthand_ui_blueprint.route('/glossary', methods=['GET'])
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
    tags = _get_tags(SHORTHAND_CONFIG['notes_directory'],
                     grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))

    log.info('Showing the Definitions search page')
    return render_template('glossary.j2',
                           all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/search', methods=['GET'])
def show_search_page():
    return render_template('search.j2',
                           static_content=static_content)


@shorthand_ui_blueprint.route('/render', methods=['GET'])
def send_rendered_note():

    file_path = SHORTHAND_CONFIG['notes_directory'] + request.args.get('path')
    file_content = _get_note(SHORTHAND_CONFIG['notes_directory'], file_path)
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


@shorthand_ui_blueprint.route('/editor', methods=['GET'])
def show_editor():
    file_path = SHORTHAND_CONFIG['notes_directory'] + request.args.get('path')
    file_content = _get_note(SHORTHAND_CONFIG['notes_directory'], file_path)
    return render_template('editor.j2', file_content=file_content,
                           file_path=request.args.get('path'),
                           static_content=static_content)


@shorthand_ui_blueprint.route('/calendar', methods=['GET'])
def show_calendar():
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
    return render_template('calendar.j2', all_directories=all_directories,
                           default_directory=default_directory,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/browse', methods=['GET'])
def show_browse_page():
    toc = _get_toc(SHORTHAND_CONFIG['notes_directory'])
    return render_template('browse.j2', toc=json.dumps(toc),
                           static_content=static_content)


app.register_blueprint(shorthand_ui_blueprint)


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
