import os
import json
import logging


CONFIG_FILE_LOCATION = '/etc/shorthand/shorthand_config.json'
log = logging.getLogger(__name__)


def get_notes_config(config_location=CONFIG_FILE_LOCATION):

    if '~' in config_location:
        config_location = os.path.expanduser(config_location)

    with open(config_location, 'r') as env_config_file:
        notes_config = json.load(env_config_file)

    # TODO - Validate contents of notes config

    # Ensure that the notes directory path has no trailing `/`
    notes_dir = notes_config['notes_directory']
    notes_config['notes_directory'] = notes_dir.rstrip('/')

    return notes_config
