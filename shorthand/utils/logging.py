import time
import logging

from shorthand.utils.config import DEFAULT_LOG_FILE, DEFAULT_LOG_LEVEL, \
                                   DEFAULT_LOG_FORMAT


def get_default_logger():
    log = logging.getLogger('shorthand')
    log.setLevel(DEFAULT_LOG_LEVEL)
    default_handler = logging.FileHandler(DEFAULT_LOG_FILE)
    default_handler.setLevel(DEFAULT_LOG_LEVEL)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    formatter.converter = time.gmtime
    default_handler.setFormatter(formatter)
    log.addHandler(default_handler)
    return log


def log_level_from_string(log_level_string):
    if log_level_string.lower() == 'debug':
        log_level = logging.DEBUG
    elif log_level_string.lower() in ['warn', 'warning']:
        log_level = logging.WARNING
    elif log_level_string.lower() == 'error':
        log_level = logging.ERROR
    elif log_level_string.lower() == 'critical':
        log_level = logging.CRITICAL
    else:
        log_level = logging.INFO
    return log_level


def get_handler(config):
    log_file_path = config.get('log_file_path', 'shorthand.log')
    log_level_string = config.get('log_level', 'info')
    log_level = log_level_from_string(log_level_string)

    fh = logging.FileHandler(log_file_path)
    fh.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)-8s %(message)s')
    formatter.converter = time.gmtime
    fh.setFormatter(formatter)
    return fh
