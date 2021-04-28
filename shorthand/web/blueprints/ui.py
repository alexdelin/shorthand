import os
import json

from flask import request, render_template, send_from_directory, Blueprint, \
                  current_app, abort

from shorthand.notes import _get_note
from shorthand.tags import _get_tags
from shorthand.history import _get_calendar
from shorthand.toc import _get_toc
from shorthand.elements.todos import _get_todos
from shorthand.elements.questions import _get_questions
from shorthand.elements.record_sets import _get_record_sets
from shorthand.utils.config import get_notes_config
from shorthand.frontend import is_image_path
from shorthand.frontend.render import get_rendered_markdown
from shorthand.web.blueprints.static_elements import static_content


shorthand_ui_blueprint = Blueprint('shorthand_ui_blueprint', __name__,
                                   template_folder='templates')


@shorthand_ui_blueprint.route('/js/<path:path>', methods=['GET', 'POST'])
def send_js(path):
    return send_from_directory('blueprints/static/js', path)


@shorthand_ui_blueprint.route('/css/<path:path>', methods=['GET', 'POST'])
def send_css(path):
    return send_from_directory('blueprints/static/css', path)


@shorthand_ui_blueprint.route('/img/<path:path>', methods=['GET', 'POST'])
def send_img(path):
    return send_from_directory('blueprints/static/img', path)


# Frontend API Methods which should all eventually be
# replaced with proper API methods
@shorthand_ui_blueprint.route('/frontend-api/redered-markdown',
                              methods=['GET', 'POST'])
def send_processed_markdown():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])
    file_content = _get_note(SHORTHAND_CONFIG['notes_directory'],
                             request.args.get('path'))
    file_content, toc_content = get_rendered_markdown(file_content)
    return file_content


@shorthand_ui_blueprint.route('/frontend-api/get-image',
                              methods=['GET', 'POST'])
def send_image():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])
    image_path = request.args.get('path').strip('/')
    if not is_image_path(SHORTHAND_CONFIG['notes_directory'], image_path):
        abort(404)
    return send_from_directory(SHORTHAND_CONFIG['notes_directory'], image_path)


@shorthand_ui_blueprint.route('/', methods=['GET'])
def show_home_page():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])
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
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

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

    current_app.logger.info('Showing the home page')
    return render_template('todos.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/questions', methods=['GET'])
def show_questions():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

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

    current_app.logger.info('Showing the questions search page')
    return render_template('questions.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/databases', methods=['GET'])
def show_databases():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])
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
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])
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

    current_app.logger.info('Showing the Definitions search page')
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
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

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
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    file_path = SHORTHAND_CONFIG['notes_directory'] + request.args.get('path')
    file_content = _get_note(SHORTHAND_CONFIG['notes_directory'], file_path)
    return render_template('editor.j2', file_content=file_content,
                           file_path=request.args.get('path'),
                           static_content=static_content)


@shorthand_ui_blueprint.route('/calendar', methods=['GET'])
def show_calendar():
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

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
    SHORTHAND_CONFIG = get_notes_config(current_app.config['config_path'])

    toc = _get_toc(SHORTHAND_CONFIG['notes_directory'])
    return render_template('browse.j2', toc=json.dumps(toc),
                           static_content=static_content)
