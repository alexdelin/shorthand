import json

from flask import request, render_template, send_from_directory, Blueprint, \
                  current_app, abort, Response

from shorthand import ShorthandServer
from shorthand.utils.config import _get_notes_config
from shorthand.utils.api import get_request_argument
from shorthand.frontend import is_image_path, get_open_files, open_file, \
                               close_file, clear_open_files
from shorthand.frontend.render import get_rendered_markdown


shorthand_ui_blueprint = Blueprint('shorthand_ui_blueprint', __name__)


@shorthand_ui_blueprint.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

# Frontend API Methods which should all eventually be
# replaced with proper API methods
@shorthand_ui_blueprint.route('/frontend-api/redered-markdown',
                              methods=['GET', 'POST'])
def send_processed_markdown():
    server = ShorthandServer(current_app.config['config_path'])
    note_path = request.args.get('path')
    file_content = server.get_note(note_path)
    file_content, toc_content = get_rendered_markdown(file_content, note_path)
    return json.dumps({
        'file_content': file_content,
        'toc_content': toc_content
    })


@shorthand_ui_blueprint.route('/frontend-api/get-image',
                              methods=['GET', 'POST'])
def send_image():
    SHORTHAND_CONFIG = _get_notes_config(current_app.config['config_path'])
    image_path = request.args.get('path').strip('/')
    if not is_image_path(SHORTHAND_CONFIG['notes_directory'], image_path):
        abort(404)
    return send_from_directory(SHORTHAND_CONFIG['notes_directory'], image_path)


@shorthand_ui_blueprint.route('/frontend-api/get-open-files', methods=['GET'])
def send_get_open_files():
    SHORTHAND_CONFIG = _get_notes_config(current_app.config['config_path'])
    open_files = get_open_files(SHORTHAND_CONFIG['cache_directory'],
                                SHORTHAND_CONFIG['notes_directory'])
    return json.dumps(open_files)


@shorthand_ui_blueprint.route('/frontend-api/open-file', methods=['POST'])
def call_open_file():
    SHORTHAND_CONFIG = _get_notes_config(current_app.config['config_path'])
    path = get_request_argument(request.args, name='path')
    return open_file(SHORTHAND_CONFIG['cache_directory'],
                     SHORTHAND_CONFIG['notes_directory'],
                     path)

@shorthand_ui_blueprint.route('/frontend-api/close-file', methods=['POST'])
def call_close_file():
    SHORTHAND_CONFIG = _get_notes_config(current_app.config['config_path'])
    path = get_request_argument(request.args, name='path')
    return close_file(SHORTHAND_CONFIG['cache_directory'],
                      path)

@shorthand_ui_blueprint.route('/frontend-api/clear-open-files', methods=['POST'])
def call_clear_open_files():
    SHORTHAND_CONFIG = _get_notes_config(current_app.config['config_path'])
    return clear_open_files(SHORTHAND_CONFIG['cache_directory'])
