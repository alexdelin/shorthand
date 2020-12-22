import logging

from shorthand.utils.config import get_notes_config, write_config, \
    modify_config
from shorthand.utils.logging import get_handler


class ShorthandServer(object):
    '''Main Shorthand Server API
       This implementation exposes a nicer API than calling
       the underlying functions directly and manages basic
       configuration transparently
    '''

    def __init__(self, config_path):
        '''Initialize the server with the configuration
           in the specified file
        '''
        # super(ShorthandServer, self).__init__()
        self.config_path = config_path
        self.reload_config()
        self.log = logging.getLogger(__name__)
        log_handler = get_handler(self.config)
        self.log.addHandler(log_handler)

    # -------------------------
    # --- Config Management ---
    # -------------------------
    def get_config(self):
        '''Get the current server configuration
        '''
        return self.config

    def reload_config(self):
        '''Reload the config from the config file
        '''
        self.config = get_notes_config(self.config_path)

    def update_config(self, updates):
        '''Update one or more fields in the configuration
           Note: This does not save the updated config to disk
        '''
        self.config = modify_config(self.config, updates)

    def save_config(self):
        '''Save the current config to the config file
        '''
        write_config(self.config_path, self.config)

    def check_config_init(self):
        '''Validate that config is present
        '''
        if not self.config:
            raise ValueError('Shorthand Server is not yet '
                             'initialized with config')

    # -------------
    # --- Todos ---
    # -------------
    def get_todos(todo_status='incomplete', directory_filter=None,
                  query_string=None, case_sensitive=False, sort_by=None,
                  suppress_future=True, tag=None):
        pass

    def mark_todo(filename, line_number, status):
        pass

    # -----------------
    # --- Questions ---
    # -----------------
    def get_questions(question_status='all', directory_filter=None):
        pass

    # -------------------
    # --- Definitions ---
    # -------------------
    def get_definitions(directory_filter=None):
        pass

    # -----------------
    # --- Locations ---
    # -----------------
    def get_locations(directory_filter=None):
        pass

    # -------------------
    # --- Record Sets ---
    # -------------------
    def _get_record_sets(directory_filter=None):
        pass

    def get_record_set(file_path, line_number, parse=True,
                       parse_format='json', include_config=False):
        pass

    # Calendar
    def get_calendar(directory_filter=None):
        pass

    # Notes
    def get_note(file_path):
        raise NotImplementedError

    def update_note(file_path, content):
        pass

    def append_to_note():
        raise NotImplementedError

    def create_note():
        raise NotImplementedError

    # Stamping
    def stamp_notes(stamp_todos=True, stamp_today=True, stamp_questions=True,
                    stamp_answers=True):
        pass

    # Tags
    def get_tags(directory_filter=None):
        pass

    # TOC
    def get_toc(directory_filter=None):
        pass

    # Typeahead
    def update_ngram_database():
        pass

    def get_typeahead_suggestions(query_string, limit=10):
        pass
