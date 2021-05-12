import json

from werkzeug.exceptions import HTTPException
from flask import Blueprint, request, current_app

from shorthand import ShorthandServer
from shorthand.search import _filename_search, \
                                   _record_file_view
from shorthand.elements.todos import analyze_todos
from shorthand.utils.config import get_notes_config
from shorthand.utils.api import wrap_response_data

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
    server = ShorthandServer(current_app.config['config_path'])

    query_string = request.args.get('query_string')
    case_sensitive = request.args.get('case_sensitive')

    search_results = server.search_notes(
        query_string=query_string,
        case_sensitive=case_sensitive)
    return json.dumps(wrap_response_data(search_results))


@shorthand_api_blueprint.route('/api/v1/note', methods=['GET'])
def get_full_note():
    server = ShorthandServer(current_app.config['config_path'])
    path = request.args.get('path')
    return server.get_note(path)


@shorthand_api_blueprint.route('/api/v1/note', methods=['POST'])
def write_updated_note():
    server = ShorthandServer(current_app.config['config_path'])

    path = request.args.get('path')
    request.get_data()
    content = request.data.decode('utf-8')

    server.update_note(path, content)
    return 'Note Updated'


@shorthand_api_blueprint.route('/api/v1/toc', methods=['GET'])
def get_toc_data():
    server = ShorthandServer(current_app.config['config_path'])
    return json.dumps(server.get_toc())


@shorthand_api_blueprint.route('/api/v1/links', methods=['GET'])
def get_note_links():
    server = ShorthandServer(current_app.config['config_path'])

    source = request.args.get('source')
    target = request.args.get('target')
    #TODO - Implement a better way to extract these from the request
    include_external = request.args.get('include_external')
    include_invalid = request.args.get('include_invalid')

    return json.dumps(server.get_links(source=source, target=target,
                                       include_external=include_external,
                                       include_invalid=include_invalid))


@shorthand_api_blueprint.route('/api/v1/links/validate', methods=['GET'])
def validate_note_links():
    server = ShorthandServer(current_app.config['config_path'])
    return json.dumps(server.validate_internal_links())


@shorthand_api_blueprint.route('/api/v1/typeahead', methods=['GET'])
def get_typeahead():
    server = ShorthandServer(current_app.config['config_path'])
    query_string = request.args.get('query')
    return json.dumps(server.get_typeahead_suggestions(
        query_string=query_string))


@shorthand_api_blueprint.route('/api/v1/stamp', methods=['GET'])
def stamp():
    server = ShorthandServer(current_app.config['config_path'])
    return server.stamp_notes(stamp_todos=True, stamp_today=True,
                              stamp_questions=True, stamp_answers=True)


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
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    tags = server.get_tags(directory_filter=directory_filter)
    return json.dumps(wrap_response_data(tags))


@shorthand_api_blueprint.route('/api/v1/calendar', methods=['GET'])
def fetch_calendar():
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    calendar = server.get_calendar(directory_filter=directory_filter)
    return json.dumps(calendar)


# ----------------
# --- Elements ---
# ----------------
@shorthand_api_blueprint.route('/api/v1/locations', methods=['GET'])
def get_gps_locations():
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')

    locations = server.get_locations(directory_filter=directory_filter)
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
    server = ShorthandServer(current_app.config['config_path'])

    status = request.args.get('status', 'all')
    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None
    current_app.logger.info(f'Getting {status} questions in directory {directory_filter}')

    questions = server.get_questions(
        question_status=status, directory_filter=directory_filter,)
    current_app.logger.info(f'Returning {len(questions)} question results')
    return json.dumps(wrap_response_data(questions))


@shorthand_api_blueprint.route('/api/v1/definitions', methods=['GET'])
def fetch_definitions():
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    definitions = server.get_definitions(directory_filter=directory_filter)
    return json.dumps(wrap_response_data(definitions))


@shorthand_api_blueprint.route('/api/v1/record_sets', methods=['GET'])
def fetch_record_sets():
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = request.args.get('directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    record_sets = server.get_record_sets(directory_filter=None)
    return json.dumps(wrap_response_data(record_sets))


@shorthand_api_blueprint.route('/api/v1/record_set', methods=['GET'])
def fetch_record_set():
    server = ShorthandServer(current_app.config['config_path'])

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

    return server.get_record_set(
        file_path=file_path,
        line_number=line_number,
        parse=parse,
        parse_format=parse_format,
        include_config=include_config)
