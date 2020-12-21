#!/usr/bin/env/python

'''
Shorthand Web API
'''

import logging

from flask import Flask

from shorthand.utils.config import get_notes_config, CONFIG_FILE_LOCATION
from shorthand.utils.logging import setup_logging
from shorthand.web.blueprints.api import shorthand_api_blueprint
from shorthand.web.blueprints.ui import shorthand_ui_blueprint


app = Flask(__name__)

app.config['config_path'] = CONFIG_FILE_LOCATION
# SHORTHAND_CONFIG = get_notes_config(app.config['config_path'])

#TODO - move logging into the ShorthandServer Object
setup_logging(get_notes_config(app.config['config_path']))
log = logging.getLogger(__name__)


app.register_blueprint(shorthand_api_blueprint)
app.register_blueprint(shorthand_ui_blueprint)


if __name__ == "__main__":
    app.run(port=8181, debug=True, threaded=True)
