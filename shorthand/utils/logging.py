import os
import time
import logging

def setup_logging(config):

    log_file_path = config.get('log_file_path', 'shorthand.log')
    log_level_string = config.get('log_level', 'info')
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

    log_format = '%(asctime)s %(name)s %(levelname)-8s %(message)s'
    # log = logging.getLogger(f'shorthand[{os.getpid()}]')
    logging.basicConfig(filename=log_file_path, filemode='a', level=log_level, format=log_format)
    # Log in UTC time
    logging.Formatter.converter = time.gmtime
