import json

from flask import request, render_template, send_from_directory, Blueprint, \
                  current_app, abort, Response

from shorthand import ShorthandServer
from shorthand.utils.config import _get_notes_config
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


# Frontend API Methods which should all eventually be
# replaced with proper API methods
@shorthand_ui_blueprint.route('/frontend-api/redered-markdown',
                              methods=['GET', 'POST'])
def send_processed_markdown():
    server = ShorthandServer(current_app.config['config_path'])
    note_path = request.args.get('path')
    file_content = server.get_note(note_path)
    file_content, toc_content = get_rendered_markdown(file_content, note_path)
    resp = Response(json.dumps({
        'file_content': file_content,
        'toc_content': toc_content
    }))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@shorthand_ui_blueprint.route('/frontend-api/get-image',
                              methods=['GET', 'POST'])
def send_image():
    SHORTHAND_CONFIG = _get_notes_config(current_app.config['config_path'])
    image_path = request.args.get('path').strip('/')
    if not is_image_path(SHORTHAND_CONFIG['notes_directory'], image_path):
        abort(404)
    return send_from_directory(SHORTHAND_CONFIG['notes_directory'], image_path)


@shorthand_ui_blueprint.route('/', methods=['GET'])
def show_home_page():
    server = ShorthandServer(current_app.config['config_path'])
    default_directory = server.get_config().get('default_directory')
    todos = server.get_todos(
        todo_status='incomplete',
        directory_filter=default_directory)
    questions = server.get_questions(
        question_status='unanswered',
        directory_filter=default_directory)
    summary = server.get_calendar()
    events = []
    colors = {
        'section': 'black',
        'incomplete_todo': 'red',
        'completed_todo': 'blue',
        'skipped_todo': 'grey',
        'question': 'purple',
        'answer': 'green',
    }
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
                    if formatted_event['type'] in colors.keys():
                        formatted_event['color'] = colors[formatted_event['type']]
                    events.append(formatted_event)

    return render_template('home.j2', num_todos=len(todos),
                           num_questions=len(questions),
                           events=json.dumps(events),
                           static_content=static_content)


@shorthand_ui_blueprint.route('/todos', methods=['GET'])
def show_todos_page():
    server = ShorthandServer(current_app.config['config_path'])

    all_directories = ['ALL'] + server.get_subdirs()
    default_directory = server.get_config().get('default_directory')
    tags = server.get_tags()

    current_app.logger.info('Showing the home page')
    return render_template('todos.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/questions', methods=['GET'])
def show_questions():
    server = ShorthandServer(current_app.config['config_path'])

    all_directories = ['ALL'] + server.get_subdirs()
    default_directory = server.get_config().get('default_directory')
    tags = server.get_tags()

    current_app.logger.info('Showing the questions search page')
    return render_template('questions.j2', all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/links', methods=['GET'])
def show_links():
    return render_template('links.j2', static_content=static_content)


@shorthand_ui_blueprint.route('/databases', methods=['GET'])
def show_databases():
    server = ShorthandServer(current_app.config['config_path'])
    record_sets = server.get_record_sets()
    return render_template('record_sets.j2', record_sets=record_sets,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/locations', methods=['GET'])
def show_locations():
    return render_template('locations.j2', static_content=static_content)


@shorthand_ui_blueprint.route('/glossary', methods=['GET'])
def show_glossary():
    server = ShorthandServer(current_app.config['config_path'])
    all_directories = ['ALL'] + server.get_subdirs()
    default_directory = server.get_config().get('default_directory')
    tags = server.get_tags()

    current_app.logger.info('Showing the Definitions search page')
    return render_template('glossary.j2',
                           all_directories=all_directories,
                           default_directory=default_directory, tags=tags,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/render', methods=['GET'])
def send_rendered_note():
    return render_template('viewer.j2', static_content=static_content,
                           file_path=request.args.get('path'))


@shorthand_ui_blueprint.route('/editor', methods=['GET'])
def show_editor():
    return render_template('editor.j2', file_path=request.args.get('path'),
                           static_content=static_content)


@shorthand_ui_blueprint.route('/calendar', methods=['GET'])
def show_calendar():
    server = ShorthandServer(current_app.config['config_path'])

    all_directories = ['ALL'] + server.get_subdirs()
    default_directory = server.get_config().get('default_directory')
    return render_template('calendar.j2', all_directories=all_directories,
                           default_directory=default_directory,
                           static_content=static_content)


@shorthand_ui_blueprint.route('/browse', methods=['GET'])
def show_browse_page():
    server = ShorthandServer(current_app.config['config_path'])

    toc = server.get_toc()
    return render_template('browse.j2', toc=json.dumps(toc),
                           static_content=static_content)
