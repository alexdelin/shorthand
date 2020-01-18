import os
import json

CONFIG_FILE_LOCATION = '/etc/apps/shorthand/shorthand_config.json'


def get_notes_config(config_location=CONFIG_FILE_LOCATION):

    if '~' in config_location:
        config_location = os.path.expanduser(config_location)

    with open(config_location, 'r') as env_config_file:
        notes_config = json.load(env_config_file)

    return notes_config
