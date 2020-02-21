import os
import json

CONFIG_FILE_LOCATION = '/etc/shorthand/shorthand_config.json'


def get_notes_config(config_location=CONFIG_FILE_LOCATION):

    if '~' in config_location:
        config_location = os.path.expanduser(config_location)

    with open(config_location, 'r') as env_config_file:
        notes_config = json.load(env_config_file)

    # Ensure that the notes directory path has no trailing `/`
    notes_config['notes_directory'] = notes_config['notes_directory'].rstrip('/')

    return notes_config
