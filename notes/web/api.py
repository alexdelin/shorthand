#!/usr/bin/env/python

'''
Note Parser Web API
'''

import json

from flask import Flask  # , request, render_template, send_from_directory

from note_parser.todo_tools import get_todos  # , mark_todo
from note_parser.utils.config import get_notes_config

app = Flask(__name__)

NOTES_CONFIG = get_notes_config()


@app.route('/get_todos/<path:path>', methods=['GET'])
def get_current_todos(path):
    """Main Route that displays the documentation"""

    return json.dumps(get_todos(
                notes_directory=NOTES_CONFIG['notes_directory'],
                todo_status=path))


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
