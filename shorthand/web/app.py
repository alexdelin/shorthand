#!/usr/bin/env/python

'''
Shorthand Web API
'''

import logging

from flask import Flask

from shorthand.utils.config import get_notes_config, CONFIG_FILE_LOCATION
from shorthand.utils.logging import setup_logging, get_handler
from shorthand.web.blueprints.api import shorthand_api_blueprint
from shorthand.web.blueprints.ui import shorthand_ui_blueprint


def create_app(config_path):

    config = get_notes_config(config_path)
    setup_logging(config)

    app = Flask(__name__)

    app.config['config_path'] = config_path
    app.logger = logging.getLogger(__name__)
    handler = get_handler(config)
    app.logger.addHandler(handler)

    app.register_blueprint(shorthand_api_blueprint)
    app.register_blueprint(shorthand_ui_blueprint)
    return app


if __name__ == "__main__":
    app = create_app(CONFIG_FILE_LOCATION)
    app.run(port=8181, debug=True, threaded=True)
