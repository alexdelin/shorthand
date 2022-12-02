import json

from werkzeug.exceptions import HTTPException
from flask import Blueprint, request, current_app

from shorthand import ShorthandServer
from shorthand.elements.todos import analyze_todos
from shorthand.types import JSONTOC, ACKResponse, JSONLinks, JSONSearchResults, JSONShorthandConfig, JSONShorthandConfigUpdates, JSONSubdirs, NotePath, RawNoteContent
from shorthand.utils.api import wrap_response_data, get_request_argument
from shorthand.utils.config import ShorthandConfigUpdates

shorthand_api_blueprint = Blueprint('shorthand_api_blueprint', __name__)


@shorthand_api_blueprint.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@shorthand_api_blueprint.app_errorhandler(Exception)
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
def get_server_config() -> JSONShorthandConfig:
    server = ShorthandServer(current_app.config['config_path'])
    current_app.logger.info('Returning config')
    return json.dumps(server.get_config())


@shorthand_api_blueprint.route('/api/v1/config', methods=['PUT'])
def update_server_config() -> ACKResponse:
    server = ShorthandServer(current_app.config['config_path'])
    current_app.logger.info('Updating config')
    updates_json: JSONShorthandConfigUpdates = str(request.get_data())
    updates: ShorthandConfigUpdates = json.loads(updates_json)
    server.update_config(updates)
    server.save_config()
    return 'ack'


@shorthand_api_blueprint.route('/api/v1/search', methods=['GET'])
def get_search_results() -> JSONSearchResults:
    server = ShorthandServer(current_app.config['config_path'])

    query_string = get_request_argument(request.args, name='query_string')
    case_sensitive = get_request_argument(request.args, name='case_sensitive',
                                          arg_type=bool, default=False)
    aggregate_by_file = get_request_argument(request.args,
                                             name='aggregate_by_file',
                                             arg_type=bool, default=False)

    search_results = server.search_full_text(
        query_string=query_string,
        case_sensitive=case_sensitive,
        aggregate_by_file=aggregate_by_file)
    return json.dumps(search_results)


@shorthand_api_blueprint.route('/api/v1/note', methods=['GET'])
def get_full_note() -> RawNoteContent:
    server = ShorthandServer(current_app.config['config_path'])
    path = get_request_argument(request.args, name='path', required=True)
    return server.get_note(path)


@shorthand_api_blueprint.route('/api/v1/note', methods=['POST'])
def write_updated_note():
    server = ShorthandServer(current_app.config['config_path'])

    path: NotePath = get_request_argument(request.args, name='path', required=True)
    request.get_data()
    content: RawNoteContent = request.data.decode('utf-8')

    server.update_note(path, content)
    return 'Note Updated'


@shorthand_api_blueprint.route('/api/v1/toc', methods=['GET'])
def get_toc_data() -> JSONTOC:
    server = ShorthandServer(current_app.config['config_path'])
    return json.dumps(server.get_toc())


@shorthand_api_blueprint.route('/api/v1/subdirs', methods=['GET'])
def get_subdirs_data() -> JSONSubdirs:
    server = ShorthandServer(current_app.config['config_path'])
    return json.dumps(server.get_subdirs())


@shorthand_api_blueprint.route('/api/v1/links', methods=['GET'])
def get_note_links() -> JSONLinks:
    server = ShorthandServer(current_app.config['config_path'])

    source = get_request_argument(request.args, name='source')
    target = get_request_argument(request.args, name='target')
    note = get_request_argument(request.args, name='note')
    include_external = get_request_argument(request.args,
                                            name='include_external',
                                            arg_type=bool, default=False)
    include_invalid = get_request_argument(request.args,
                                           name='include_invalid',
                                           arg_type=bool, default=False)

    return json.dumps(
        server.get_links(source=source, target=target, note=note,
                         include_external=include_external,
                         include_invalid=include_invalid))


@shorthand_api_blueprint.route('/api/v1/links/validate', methods=['GET'])
def validate_note_links() -> JSONLinks:
    server = ShorthandServer(current_app.config['config_path'])
    source = get_request_argument(request.args, name='source')
    return json.dumps(server.validate_internal_links(source=source))


@shorthand_api_blueprint.route('/api/v1/typeahead', methods=['GET'])
def get_typeahead():
    server = ShorthandServer(current_app.config['config_path'])
    query_string = get_request_argument(request.args, name='query')
    return json.dumps(
        server.get_typeahead_suggestions(
            query_string=query_string))


@shorthand_api_blueprint.route('/api/v1/stamp', methods=['GET'])
def stamp():
    server = ShorthandServer(current_app.config['config_path'])
    return server.stamp_notes()


@shorthand_api_blueprint.route('/api/v1/stamp/raw', methods=['POST'])
def stamp_raw() -> RawNoteContent:
    server = ShorthandServer(current_app.config['config_path'])
    request.get_data()
    raw_note: RawNoteContent = request.data.decode('utf-8')
    return server.stamp_raw_note(raw_note)


@shorthand_api_blueprint.route('/api/v1/files', methods=['GET'])
def get_files():
    server = ShorthandServer(current_app.config['config_path'])

    query_string = get_request_argument(request.args, name='query_string')
    prefer_recent = get_request_argument(request.args, name='prefer_recent',
                                         arg_type=bool, default=True)
    case_sensitive = get_request_argument(request.args, name='case_sensitive',
                                          arg_type=bool, default=False)

    files = server.search_filenames(
                prefer_recent=prefer_recent,
                query_string=query_string, case_sensitive=case_sensitive)

    return json.dumps(files)


@shorthand_api_blueprint.route('/api/v1/record_view', methods=['POST'])
def record_file_view_api():
    server = ShorthandServer(current_app.config['config_path'])

    note_path = get_request_argument(request.args, name='note_path',
                                     required=True)
    server.record_file_view(note_path=note_path)
    return 'ack'


@shorthand_api_blueprint.route('/api/v1/tags', methods=['GET'])
def fetch_tags():
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = get_request_argument(request.args,
                                            name='directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    tags = server.get_tags(directory_filter=directory_filter)
    return json.dumps(wrap_response_data(tags))


@shorthand_api_blueprint.route('/api/v1/calendar', methods=['GET'])
def fetch_calendar():
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = get_request_argument(request.args,
                                            name='directory_filter')
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

    directory_filter = get_request_argument(request.args,
                                            name='directory_filter')

    locations = server.get_locations(directory_filter=directory_filter)
    wrapped_response = wrap_response_data(locations)
    return json.dumps(wrapped_response)


@shorthand_api_blueprint.route('/api/v1/todos', methods=['GET'])
def get_current_todos():
    server = ShorthandServer(current_app.config['config_path'])

    status = get_request_argument(request.args, name='status',
                                  default='incomplete')
    directory_filter = get_request_argument(request.args,
                                            name='directory_filter')
    query_string = get_request_argument(request.args, name='query_string')
    sort_by = get_request_argument(request.args, name='sort_by')
    tag = get_request_argument(request.args, name='tag')
    suppress_future = get_request_argument(request.args,
                                           name='suppress_future',
                                           arg_type=bool, default=True)
    case_sensitive = get_request_argument(request.args, name='case_sensitive',
                                          arg_type=bool, default=False)

    if directory_filter in ['ALL', '']:
        directory_filter = None
    if tag == 'ALL':
        tag = None

    todos = server.get_todos(todo_status=status,
                             directory_filter=directory_filter,
                             query_string=query_string,
                             case_sensitive=case_sensitive, sort_by=sort_by,
                             suppress_future=suppress_future, tag=tag)
    current_app.logger.info(f'Returning {len(todos)} todo results')

    wrapped_response = wrap_response_data(todos)
    wrapped_response['meta'] = analyze_todos(todos)

    return json.dumps(wrapped_response)


@shorthand_api_blueprint.route('/api/v1/mark_todo', methods=['POST'])
def mark_todo_status():
    server = ShorthandServer(current_app.config['config_path'])

    filename = get_request_argument(request.args, name='filename',
                                    required=True)
    line_number = get_request_argument(request.args, name='line_number',
                                       arg_type=int, default=None,
                                       required=True)
    status = get_request_argument(request.args, name='status', required=True)

    return server.mark_todo(filename, line_number, status)


@shorthand_api_blueprint.route('/api/v1/questions', methods=['GET'])
def fetch_questions():
    server = ShorthandServer(current_app.config['config_path'])

    status = get_request_argument(request.args, name='status', default='all')
    directory_filter = get_request_argument(request.args,
                                            name='directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None
    current_app.logger.info(f'Getting {status} questions in ' +
                            f'directory {directory_filter}')

    questions = server.get_questions(
        question_status=status, directory_filter=directory_filter)
    current_app.logger.info(f'Returning {len(questions)} question results')
    return json.dumps(wrap_response_data(questions))


@shorthand_api_blueprint.route('/api/v1/definitions', methods=['GET'])
def fetch_definitions():
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = get_request_argument(request.args,
                                            name='directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    definitions = server.get_definitions(directory_filter=directory_filter)
    return json.dumps(wrap_response_data(definitions))


@shorthand_api_blueprint.route('/api/v1/record_sets', methods=['GET'])
def fetch_record_sets():
    server = ShorthandServer(current_app.config['config_path'])

    directory_filter = get_request_argument(request.args,
                                            name='directory_filter')
    if directory_filter == 'ALL':
        directory_filter = None

    record_sets = server.get_record_sets(directory_filter=None)
    return json.dumps(wrap_response_data(record_sets))


@shorthand_api_blueprint.route('/api/v1/record_set', methods=['GET'])
def fetch_record_set():
    server = ShorthandServer(current_app.config['config_path'])

    file_path = get_request_argument(request.args, name='file_path',
                                     required=True)
    line_number = get_request_argument(request.args, name='line_number',
                                       arg_type=int, default=None,
                                       required=True)
    parse = get_request_argument(request.args, name='parse', arg_type=bool,
                                 default=True)
    include_config = get_request_argument(request.args, name='include_config',
                                          arg_type=bool, default=False)
    parse_format = get_request_argument(request.args, name='parse_format',
                                        default='json')

    return server.get_record_set(
        file_path=file_path,
        line_number=line_number,
        parse=parse,
        parse_format=parse_format,
        include_config=include_config)
