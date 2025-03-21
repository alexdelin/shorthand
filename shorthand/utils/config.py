import os
import copy
import json
import logging
from typing import Optional, Required, TypedDict

from shorthand.types import ExecutablePath, FilePath, DirectoryPath, RelativeDirectoryPath


class ShorthandFrontendConfig(TypedDict):
    view_history_limit: int
    map_tileserver_url: str

class ShorthandConfigInput(TypedDict, total=False):
    '''The minimal config which must be provided by a user
       or specified in a config file in order to produce a valid
       ShorthandConfig which can be used by the application

       Same schema as ShorthandConfig but with fewer required fields
    '''
    notes_directory: Required[DirectoryPath]
    default_directory: Optional[RelativeDirectoryPath]
    log_file_path: FilePath
    log_level: str
    log_format: str
    grep_path: ExecutablePath
    find_path: ExecutablePath
    patch_path: ExecutablePath
    frontend: ShorthandFrontendConfig
    track_edit_history: bool

class ShorthandConfig(TypedDict):
    '''The config used by the application.
       Includes the same information as the ShorthandConfigInput
       provided, but with default values used for fields which were
       omitted in the provided input
    '''
    notes_directory: DirectoryPath
    default_directory: Optional[RelativeDirectoryPath]
    log_file_path: FilePath
    log_level: str
    log_format: str
    grep_path: ExecutablePath
    find_path: ExecutablePath
    patch_path: ExecutablePath
    frontend: ShorthandFrontendConfig
    track_edit_history: bool

class ShorthandConfigUpdates(TypedDict, total=False):
    default_directory: Optional[RelativeDirectoryPath]
    log_file_path: FilePath
    log_level: str
    log_format: str
    grep_path: ExecutablePath
    find_path: ExecutablePath
    patch_path: ExecutablePath
    frontend: ShorthandFrontendConfig
    track_edit_history: bool


CONFIG_FILE_LOCATION = '/etc/shorthand/shorthand_config.json'
DEFAULT_NOTES_DIR = '/var/lib/shorthand/notes'
DEFAULT_LOG_FILE = '/var/log/shorthand/shorthand.log'
DEFAULT_LOG_FORMAT = '%(asctime)s %(name)s %(levelname)-8s %(message)s'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_GREP_PATH = 'grep'
DEFAULT_FIND_PATH = 'find'
DEFAULT_PATCH_PATH = 'patch'
DEFAULT_FRONTEND_CONFIG: ShorthandFrontendConfig = {
    'view_history_limit': 100,
    'map_tileserver_url': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
}

DEFAULT_CONFIG: ShorthandConfig = {
    "notes_directory": DEFAULT_NOTES_DIR,
    "default_directory": None,
    "log_file_path": DEFAULT_LOG_FILE,
    "log_level": DEFAULT_LOG_LEVEL,
    "log_format": DEFAULT_LOG_FORMAT,
    "grep_path": DEFAULT_GREP_PATH,
    "find_path": DEFAULT_FIND_PATH,
    "patch_path": DEFAULT_PATCH_PATH,
    "frontend": DEFAULT_FRONTEND_CONFIG,
    "track_edit_history": True
}

REQUIRED_FIELDS = ['notes_directory']


log = logging.getLogger(__name__)


def _get_notes_config(config_location: FilePath = CONFIG_FILE_LOCATION
                      ) -> ShorthandConfig:
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


def _write_config(config_location: FilePath, config: ShorthandConfig) -> None:
    '''Write the specified config into a config file
    '''

    # Check that the config is valid
    clean_config = clean_and_validate_config(config)

    # Check that the parent directory exists
    parent_dir = os.path.dirname(config_location)
    if not os.path.exists(parent_dir):
        log.warning(f'Config directory {parent_dir} ' +
                    f'does not exist, creating it')
        os.makedirs(parent_dir)

    with open(config_location, 'w') as config_file_object:
        json.dump(clean_config, config_file_object)


def _modify_config(config: ShorthandConfig, updates: ShorthandConfigUpdates
                   ) -> ShorthandConfig:
    '''Update one or more fields in the config
       Takes an original config and a dictionary of updates to make
       The updates have the same form as the regular config but
       only includes a subset of the fields
    '''

    if not isinstance(updates, dict):
        raise ValueError('Config updates must be provided as a dictionary')

    if 'notes_directory' in updates:
        raise ValueError('Cannot modify the notes directory via the API')

    new_config = copy.deepcopy(config)
    for key, value in updates.items():
        if key == 'frontend':
            continue
        elif key not in DEFAULT_CONFIG.keys():
            raise ValueError(f'Config Update has unknown field {key}')
        else:
            new_config[key] = value

    if 'frontend' in updates:
        # Validate Provided frontend updates
        if not isinstance(updates['frontend'], dict):
            raise ValueError('Frontend config must be provided ' +
                             'as a dictionary')
        for key in updates['frontend'].keys():
            if key not in DEFAULT_FRONTEND_CONFIG.keys():
                raise ValueError(f'Config update has unknown frontend ' +
                                 f'config key {key}')
        if new_config.get('frontend'):
            new_config['frontend'].update(updates['frontend'])
        else:
            new_config['frontend'] = updates['frontend']

    new_config = clean_and_validate_config(new_config)

    return new_config


def clean_and_validate_config(config: ShorthandConfigInput | ShorthandConfig) -> ShorthandConfig:
    '''Clean and validate values from the config file as needed
    Return the config if there are no issues, and raise an error
    if an issue is found
    '''

    #TODO - Set up logging immediately, so later errors will
    #       be logged correctly

    # Ensure that no unknown fields are present in the config
    for field in config.keys():
        if field not in DEFAULT_CONFIG.keys():
            raise ValueError(f'Config includes unknown field "{field}"')

    # Ensure that required fields are present in the config
    for field in REQUIRED_FIELDS:
        if field not in config.keys():
            raise ValueError(f'Missing required field "{field}"')

    # Validation for tracking edit history
    if 'track_edit_history' not in config:
        config['track_edit_history'] = DEFAULT_CONFIG['track_edit_history']
    if not isinstance(config['track_edit_history'], bool):
        raise ValueError('track_edit_history must be a boolean value')

    # Ensure that the notes directory and cache directory
    # paths have no trailing `/`
    notes_dir = config['notes_directory']
    config['notes_directory'] = notes_dir.rstrip('/')

    # Check config values that point to directories that must exist
    directory_fields = ['notes_directory']
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
            os.makedirs(log_file_path)
    else:
        log.info(f'No log file path specified, falling back to '
                 f'default of "{DEFAULT_LOG_FILE}"')
        config['log_file_path'] = DEFAULT_LOG_FILE

    log_level = config.get('log_level')
    if log_level:
        if log_level.upper() not in ['DEBUG', 'INFO', 'WARNING', 'WARN',
                                     'ERROR', 'CRITICAL']:
            raise ValueError(f'Invalid log level "{log_level}" specified')
        config['log_level'] = log_level.upper()
    else:
        log.info(f'No log level specified, falling back to '
                 f'default of "{DEFAULT_LOG_LEVEL}"')
        config['log_level'] = DEFAULT_LOG_LEVEL

    log_format = config.get('log_format')
    if log_format:
        if not isinstance(log_format, str):
            raise ValueError('log_format must be specified as a string')
        pass
    else:
        log.info(f'No log format specified, falling back to '
                 f'default of "{DEFAULT_LOG_FORMAT}"')
        config['log_format'] = DEFAULT_LOG_FORMAT

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

    patch_path = config.get('patch_path')
    if not patch_path:
        log.info(f'Patch path not specified, falling back to ' + \
                 f'default of {DEFAULT_PATCH_PATH}')
        patch_path = DEFAULT_PATCH_PATH
    # Check for the patch path as the full path to an executable
    if os.path.isfile(patch_path):
        if not os.access(patch_path, os.X_OK):
            raise ValueError(f'Patch at {patch_path} is not executable')
        else:
            log.debug(f'Found patch executable at {patch_path}')
    else:
        # Check for the patch path as an executable name within our system path
        patch_found = False
        for path in os.environ["PATH"].split(os.pathsep):
            patch_executable = os.path.join(path, patch_path)
            if os.path.isfile(patch_executable):
                if os.access(patch_executable, os.X_OK):
                    patch_path = patch_executable
                    config['patch_path'] = patch_path
                    patch_found = True
                    log.debug(f'Found patch executable at {patch_path}')
                    break
                else:
                    raise ValueError(f'Patch at {patch_executable} is ' + \
                                     f'not executable')
        if not patch_found:
            raise ValueError(f'Patch executable specified as {patch_path} ' + \
                             f'could not be located')

    # Validate frontend config
    frontend_config = config.get('frontend')
    if 'frontend' not in config.keys():
        # Frontend config is missing completely
        config['frontend'] = DEFAULT_FRONTEND_CONFIG

    elif not isinstance(frontend_config, dict):
        raise ValueError('Frontend config must be specified as a dict')

    else:
        # Check that there are no extra / unexpected fields
        # in the frontend config
        for field in frontend_config:
            if field not in DEFAULT_FRONTEND_CONFIG.keys():
                raise ValueError(f'Unknown field "{field}" in frontend config')

        # Validate the view history limit
        view_history_limit = frontend_config.get('view_history_limit')
        if 'view_history_limit' not in frontend_config.keys():
            config['frontend']['view_history_limit'] = \
                DEFAULT_FRONTEND_CONFIG['view_history_limit']
        else:
            if isinstance(view_history_limit, int):
                if view_history_limit < 0:
                    raise ValueError('View History Limit must be '
                                     'at least zero')
            elif isinstance(view_history_limit, str):
                try:
                    config['frontend']['view_history_limit'] = \
                        int(view_history_limit)
                except ValueError:
                    raise ValueError(f"Can't convert view history limit "
                                     f'value of "{view_history_limit}" to an '
                                     f'integer')

        # Validate the map tileserver URL
        map_tileserver_url = frontend_config.get('map_tileserver_url')
        if 'map_tileserver_url' not in frontend_config.keys():
            config['frontend']['map_tileserver_url'] = \
                DEFAULT_FRONTEND_CONFIG['map_tileserver_url']
        else:
            if not isinstance(map_tileserver_url, str):
                raise ValueError('Map Tileserver URL must be a string')
            if map_tileserver_url[:7] != 'http://' and \
                    map_tileserver_url[:8] != 'https://':
                raise ValueError('Map Tileserver URL must be a valid URL')

    return config
