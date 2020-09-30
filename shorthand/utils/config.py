import os
import json
import logging


CONFIG_FILE_LOCATION = '/etc/shorthand/shorthand_config.json'
DEFAULT_CACHE_DIR = '/var/lib/shorthand/cache'
DEFAULT_LOG_FILE = '/var/log/shorthand/shorthand.log'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_GREP_PATH = 'grep'
DEFAULT_FIND_PATH = 'find'
DEFAULT_FRONTEND_CONFIG = {}

log = logging.getLogger(__name__)


def get_notes_config(config_location=CONFIG_FILE_LOCATION):
    '''Get notes config from the file path specified
    returns the loaded, cleaned, and validated config
    '''

    if '~' in config_location:
        config_location = os.path.expanduser(config_location)

    if not os.path.exists(config_location):
        raise ValueError(f'Config file {config_location} does not exist')

    with open(config_location, 'r') as env_config_file:
        notes_config = json.load(env_config_file)

    notes_config = clean_and_validate_config(notes_config)

    return notes_config


def clean_and_validate_config(config):
    '''Clean and validate values from the config file as needed
    Return the config if there are no issues, and raise an error
    if an issue is found
    '''

    # TODO - Ensure that no unknown fields are present in the config

    # Ensure that required fields are present in the config
    required_fields = ['notes_directory']
    for field in required_fields:
        if field not in config.keys():
            raise ValueError(f'Missing required field "{field}"')

    # Ensure that the notes directory and cache directory
    # paths have no trailing `/`
    notes_dir = config['notes_directory']
    config['notes_directory'] = notes_dir.rstrip('/')

    cache_dir = config.get('cache_directory', '')
    if cache_dir:
        config['cache_directory'] = cache_dir.rstrip('/')
    else:
        log.info(f'No cache directory specified, falling back to '
                 f'default of {DEFAULT_CACHE_DIR}')
        config['cache_directory'] = DEFAULT_CACHE_DIR

    # Check config values that point to directories that must exist
    directory_fields = ['notes_directory', 'cache_directory']
    for field in directory_fields:
        if not os.path.exists(config[field]):
            raise ValueError(f'Directory {config[field]} specified for '
                             f'field {field} does not exist')

    # Validate logging config
    log_file_path = config.get('log_file_path')
    if log_file_path:
        log_file_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_file_dir):
            log.warn(f'Directory {log_file_dir} does not exist, creating it')
            os.mkdirs(log_file_path)
    else:
        log.info(f'No log file path specified, falling back to '
                 f'default of "{DEFAULT_LOG_FILE}"')
        config['log_file_path'] = DEFAULT_LOG_FILE

    log_level = config.get('log_level')
    if log_level:
        if log_level.upper() not in ['NOTSET', 'DEBUG', 'INFO',
                                     'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError(f'Invalid log level "{log_level}" specified')
        config['log_level'] = log_level.upper()
    else:
        log.info(f'No log level specified, falling back to '
                 f'default of "{DEFAULT_LOG_LEVEL}"')
        config['log_level'] = DEFAULT_LOG_LEVEL

    # Validate default directory
    default_dir = config.get('default_directory')
    if default_dir:
        if not os.path.exists(f'{config["notes_directory"]}/{default_dir}'):
            raise ValueError(f'Default directory {default_dir} does not '
                             f'exist within notes directory')
    else:
        config['default_directory'] = None

    # Validate paths to utilities
    grep_path = config.get('grep_path')
    if not grep_path:
        log.info(f'Grep path not specified, falling back to '
                 f'default of {DEFAULT_GREP_PATH}')
        grep_path = DEFAULT_GREP_PATH
    # Check for the grep path as the full path to an executable
    if os.path.isfile(grep_path):
        if not os.access(grep_path, os.X_OK):
            raise ValueError(f'Grep at {grep_path} is not executable')
        else:
            log.debug(f'Found grep executable at {grep_path}')
    else:
        # Check for the grep path as an executable name within our system path
        grep_found = False
        for path in os.environ["PATH"].split(os.pathsep):
            grep_executable = os.path.join(path, grep_path)
            if os.path.isfile(grep_executable):
                if os.access(grep_executable, os.X_OK):
                    grep_path = grep_executable
                    config['grep_path'] = grep_path
                    grep_found = True
                    log.debug(f'Found grep executable at {grep_path}')
                    break
                else:
                    raise ValueError(f'Grep at {grep_executable} is '
                                     f'not executable')
        if not grep_found:
            raise ValueError(f'Grep executable specified as {grep_path} '
                             f'could not be located')

    find_path = config.get('find_path')
    if not find_path:
        log.info(f'Find path not specified, falling back to '
                 f'default of {DEFAULT_FIND_PATH}')
        find_path = DEFAULT_FIND_PATH
    # Check for the find path as the full path to an executable
    if os.path.isfile(find_path):
        if not os.access(find_path, os.X_OK):
            raise ValueError(f'Find at {find_path} is not executable')
        else:
            log.debug(f'Found find executable at {find_path}')
    else:
        # Check for the find path as an executable name within our system path
        find_found = False
        for path in os.environ["PATH"].split(os.pathsep):
            find_executable = os.path.join(path, find_path)
            if os.path.isfile(find_executable):
                if os.access(find_executable, os.X_OK):
                    find_path = find_executable
                    config['find_path'] = find_path
                    find_found = True
                    log.debug(f'Found find executable at {find_path}')
                    break
                else:
                    raise ValueError(f'Find at {find_executable} is '
                                     f'not executable')
        if not find_found:
            raise ValueError(f'Find executable specified as {find_path} '
                             f'could not be located')

    # TODO - Validate frontend config
    frontend_config = config.get('frontend')
    if not frontend_config:
        config['frontend'] = DEFAULT_FRONTEND_CONFIG
    else:
        if not isinstance(frontend_config, dict):
            raise ValueError('Frontend config must be specified as a dict')

    return config
