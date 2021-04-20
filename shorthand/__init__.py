import logging

from shorthand.notes import _get_note, _update_note, \
                            _validate_internal_links, _append_to_note, \
                            _create_note, _get_backlinks, _get_links
from shorthand.calendar import _get_calendar
from shorthand.tags import _get_tags
from shorthand.stamping import _stamp_notes
from shorthand.elements.todos import _get_todos, _mark_todo
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
        self.log = logging.getLogger(__name__)

        self.config_path = config_path
        self.reload_config()
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

    # ---------------------------
    # --- Utilities for Notes ---
    # ---------------------------

    # Notes
    def get_note(self, note_path):
        return _get_note(notes_directory=self.config['notes_directory'],
                         path=note_path)

    def update_note(self, note_path, content):
        return _update_note(notes_directory=self.config['notes_directory'],
                            file_path=note_path, content=content)

    def append_to_note(self, note_path, content, blank_lines=1):
        return _append_to_note(notes_directory=self.config['notes_directory'],
                               note_path=note_path, content=content,
                               blank_lines=blank_lines)

    def create_note(self, note_path, content=None):
        return _create_note(notes_directory=self.config['notes_directory'],
                            note_path=note_path, content=content)

    def validate_internal_links(self):
        return _validate_internal_links(
            notes_directory=self.config['notes_directory'],
            grep_path=self.config['grep_path'])

    def get_backlinks(self, note_path):
        return _get_backlinks(notes_directory=self.config['notes_directory'],
                              note_path=note_path,
                              grep_path=self.config['grep_path'])

    def get_links(self, source=None, target=None, include_external=False,
                  include_invalid=False):
        return _get_links(notes_directory=self.config['notes_directory'],
                          source=source, target=target,
                          include_external=include_external,
                          include_invalid=include_invalid,
                          grep_path=self.config['grep_path'])

    # Stamping
    def stamp_notes(self, stamp_todos=True, stamp_today=True,
                    stamp_questions=True, stamp_answers=True):
        return _stamp_notes(notes_directory=self.config['notes_directory'],
                            stamp_todos=stamp_todos, stamp_today=stamp_today,
                            stamp_questions=stamp_questions,
                            stamp_answers=stamp_answers,
                            grep_path=self.config['grep_path'])

    # Calendar
    def get_calendar(self, directory_filter=None):
        return _get_calendar(notes_directory=self.config['notes_directory'],
                             directory_filter=directory_filter,
                             grep_path=self.config['grep_path'])

    # Tags
    def get_tags(self, directory_filter=None):
        return _get_tags(notes_directory=self.config['notes_directory'],
                         directory_filter=directory_filter,
                         grep_path=self.config['grep_path'])

    # TOC
    def get_toc(self, directory_filter=None):
        pass

    # Typeahead
    def update_ngram_database(self):
        pass

    def get_typeahead_suggestions(self, query_string, limit=10):
        pass

    # ----------------
    # --- Elements ---
    # ----------------

    # Todos
    def get_todos(self, todo_status='incomplete', directory_filter=None,
                  query_string=None, case_sensitive=False, sort_by=None,
                  suppress_future=True, tag=None):
        return _get_todos(notes_directory=self.config['notes_directory'],
                          todo_status=todo_status,
                          directory_filter=directory_filter,
                          query_string=query_string,
                          case_sensitive=case_sensitive, sort_by=sort_by,
                          suppress_future=suppress_future, tag=tag,
                          grep_path=self.config['grep_path'])

    def mark_todo(self, note_path, line_number, status):
        return _mark_todo(notes_directory=self.config['notes_directory'],
                          note_path=note_path, line_number=line_number,
                          status=status)

    # Questions
    def get_questions(question_status='all', directory_filter=None):
        pass

    # Definitions
    def get_definitions(directory_filter=None):
        pass

    # Locations
    def get_locations(directory_filter=None):
        pass

    # Record Sets
    def _get_record_sets(directory_filter=None):
        pass

    def get_record_set(file_path, line_number, parse=True,
                       parse_format='json', include_config=False):
        pass
