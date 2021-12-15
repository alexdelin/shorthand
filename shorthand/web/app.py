#!/usr/bin/env/python

'''
Shorthand Web API
'''

import logging

from flask import Flask

from shorthand.utils.config import get_notes_config, CONFIG_FILE_LOCATION
from shorthand.utils.logging import get_handler
from shorthand.web.blueprints.api import shorthand_api_blueprint
from shorthand.web.blueprints.ui import shorthand_ui_blueprint


def create_app(config_path):

    config = get_notes_config(config_path)

    logger = logging.getLogger('shorthand-flask')
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()
    handler = get_handler(config)
    logger.addHandler(handler)

    wz_logger = logging.getLogger('werkzeug')
    wz_logger.addHandler(handler)

    app = Flask(__name__)
    app.config['config_path'] = config_path
    app.logger = logger
    app.register_blueprint(shorthand_api_blueprint)
    app.register_blueprint(shorthand_ui_blueprint)
    app.logger.warning(f'created app with handlers: {app.logger.handlers}')
    return app


if __name__ == "__main__":
    app = create_app(CONFIG_FILE_LOCATION)
    app.run(port=8181, debug=True, threaded=True)
