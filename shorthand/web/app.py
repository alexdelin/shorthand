#!/usr/bin/env/python

'''
Shorthand Web API
'''

import logging

from flask import Flask

from shorthand.utils.config import get_notes_config
from shorthand.utils.logging import setup_logging
from shorthand.web.blueprints.api import shorthand_api_blueprint
from shorthand.web.blueprints.ui import shorthand_ui_blueprint


app = Flask(__name__)

SHORTHAND_CONFIG = get_notes_config()
setup_logging(SHORTHAND_CONFIG)
log = logging.getLogger(__name__)


app.register_blueprint(shorthand_api_blueprint)
app.register_blueprint(shorthand_ui_blueprint)


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
