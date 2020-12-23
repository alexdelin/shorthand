import json

from werkzeug.exceptions import HTTPException
from flask import Blueprint, request, current_app

from shorthand import ShorthandServer
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
from shorthand.utils.config import get_notes_config
# from shorthand.utils.git import pull_repo
from shorthand.utils.api import wrap_response_data
from shorthand.frontend.typeahead import _get_typeahead_suggestions

shorthand_api_blueprint = Blueprint('shorthand_api_blueprint', __name__)


@shorthand_api_blueprint.errorhandler(Exception)
def handle_exception(e):
    '''This method is a catch-all for all errors thrown by the server
    '''

    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    return json.dumps({'error': str(e)}), 500


# ------------------------------
# --- General Notes Features ---
# ------------------------------
@shorthand_api_blueprint.route('/api/v1/config', methods=['GET'])
def get_server_config():
    server = ShorthandServer(current_app.config['config_path'])
    current_app.logger.info('Returning config')
    return json.dumps(server.get_config())


@shorthand_api_blueprint.route('/api/v1/search', methods=['GET'])
def get_search_results():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    query_string = request.args.get('query_string')
    case_sensitive = request.args.get('case_sensitive')

    search_results = _search_notes(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        query_string=query_string,
        case_sensitive=case_sensitive,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(search_results))


@shorthand_api_blueprint.route('/api/v1/note', methods=['GET'])
def get_full_note():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    path = request.args.get('path')
    return _get_note(SHORTHAND_CONFIG['notes_directory'], path)


@shorthand_api_blueprint.route('/api/v1/note', methods=['POST'])
def write_updated_note():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    path = request.args.get('path')
    request.get_data()
    content = request.data.decode('utf-8')

    _update_note(SHORTHAND_CONFIG['notes_directory'], path, content)
    return 'Note Updated'


@shorthand_api_blueprint.route('/api/v1/toc', methods=['GET'])
def get_toc_data():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])
    return json.dumps(_get_toc(SHORTHAND_CONFIG['notes_directory']))


@shorthand_api_blueprint.route('/api/v1/typeahead', methods=['GET'])
def get_typeahead():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    query_string = request.args.get('query')

    return json.dumps(_get_typeahead_suggestions(
        SHORTHAND_CONFIG['ngram_db_directory'],
        query_string))


@shorthand_api_blueprint.route('/api/v1/stamp', methods=['GET'])
def stamp():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    return _stamp_notes(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        stamp_todos=True, stamp_today=True,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))


@shorthand_api_blueprint.route('/api/v1/files', methods=['GET'])
def get_files():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

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


@shorthand_api_blueprint.route('/api/v1/record_view', methods=['POST'])
def record_file_view_api():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    relative_path = request.args.get('relative_path')
    if not relative_path:
        raise ValueError('No Relative Path Provided')
    _record_file_view(cache_directory=SHORTHAND_CONFIG['cache_directory'],
                      relative_path=relative_path,
                      history_limit=SHORTHAND_CONFIG.get('view_history_limit',
                                                         100))
    return 'ack'


@shorthand_api_blueprint.route('/api/v1/tags', methods=['GET'])
def fetch_tags():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    tags = _get_tags(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(tags))


@shorthand_api_blueprint.route('/api/v1/calendar', methods=['GET'])
def fetch_calendar():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    calendar = _get_calendar(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(calendar)


# ----------------
# --- Elements ---
# ----------------
@shorthand_api_blueprint.route('/api/v1/locations', methods=['GET'])
def get_gps_locations():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')

    locations = _get_locations(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))

    wrapped_response = wrap_response_data(locations)
    return json.dumps(wrapped_response)


@shorthand_api_blueprint.route('/api/v1/todos', methods=['GET'])
def get_current_todos():
    server = ShorthandServer(current_app.config['config_path'])

    status = request.args.get('status', 'incomplete')
    directory_filter = request.args.get('directory_filter')
    query_string = request.args.get('query_string')
    sort_by = request.args.get('sort_by')
    tag = request.args.get('tag')
    suppress_future = request.args.get('suppress_future', 'true')
    case_sensitive = request.args.get('case_sensitive', 'false')

    if directory_filter == 'ALL':
        directory_filter = None
    if tag == 'ALL':
        tag = None

    if suppress_future.lower() == 'true':
        suppress_future = True
    elif suppress_future.lower() == 'false':
        suppress_future = False
    else:
        raise ValueError(f'Invalid value "{suppress_future}"" '
                         f'for parameter "suppress_future"')

    if case_sensitive.lower() == 'true':
        case_sensitive = True
    elif case_sensitive.lower() == 'false':
        case_sensitive = False
    else:
        raise ValueError(f'Invalid value "{case_sensitive}"" '
                         f'for parameter "case_sensitive"')

    todos = server.get_todos(todo_status=status,
                             directory_filter=directory_filter,
                             query_string=query_string,
                             case_sensitive=case_sensitive, sort_by=sort_by,
                             suppress_future=suppress_future, tag=tag)
    current_app.logger.info(f'Returning {len(todos)} todo results')

    wrapped_response = wrap_response_data(todos)
    wrapped_response['meta'] = analyze_todos(todos)
    return json.dumps(wrapped_response)


@shorthand_api_blueprint.route('/api/v1/mark_todo', methods=['GET'])
def mark_todo_status():
    server = ShorthandServer(current_app.config['config_path'])

    filename = request.args.get('filename')
    line_number = int(request.args.get('line_number'))
    status = request.args.get('status')

    return server.mark_todo(filename, line_number, status)


@shorthand_api_blueprint.route('/api/v1/questions', methods=['GET'])
def fetch_questions():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    status = request.args.get('status', 'all')
    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None
    current_app.logger.info(f'Getting {status} questions in directory {directory_filter}')

    questions = _get_questions(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        question_status=status, directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    current_app.logger.info(f'Returning {len(questions)} question results')
    return json.dumps(wrap_response_data(questions))


@shorthand_api_blueprint.route('/api/v1/definitions', methods=['GET'])
def fetch_definitions():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    definitions = _get_definitions(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=directory_filter,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(definitions))


@shorthand_api_blueprint.route('/api/v1/record_sets', methods=['GET'])
def fetch_record_sets():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    record_sets = _get_record_sets(
        notes_directory=SHORTHAND_CONFIG['notes_directory'],
        directory_filter=None,
        grep_path=SHORTHAND_CONFIG.get('grep_path', 'grep'))
    return json.dumps(wrap_response_data(record_sets))


@shorthand_api_blueprint.route('/api/v1/record_set', methods=['GET'])
def fetch_record_set():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

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
