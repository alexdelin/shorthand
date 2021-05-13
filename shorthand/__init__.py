import logging

from shorthand.notes import _get_note, _update_note, \
                            _validate_internal_links, _append_to_note, \
                            _create_note, _get_backlinks, _get_links
from shorthand.history import _get_calendar
from shorthand.tags import _get_tags
from shorthand.toc import _get_toc
from shorthand.stamping import _stamp_notes
from shorthand.search import _search_notes
from shorthand.elements.todos import _get_todos, _mark_todo
from shorthand.elements.questions import _get_questions
from shorthand.elements.definitions import _get_definitions
from shorthand.elements.locations import _get_locations
from shorthand.elements.record_sets import _get_record_sets, _get_record_set
from shorthand.frontend.typeahead import _update_ngram_database, \
                                         _get_typeahead_suggestions
from shorthand.utils.config import get_notes_config, write_config, \
                                   modify_config
from shorthand.utils.paths import _get_subdirs
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

    def get_links(self, source=None, target=None, note=None,
                  include_external=False, include_invalid=False):
        return _get_links(notes_directory=self.config['notes_directory'],
                          source=source, target=target, note=note,
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

    # Search
    def search_notes(query_string, case_sensitive=False):
        return _search_notes(notes_directory=self.config['notes_directory'],
                             query_string=query_string,
                             case_sensitive=case_sensitive,
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
        return _get_toc(notes_directory=self.config['notes_directory'],
                        directory_filter=directory_filter)

    # Typeahead
    def update_ngram_database(self):
        return _update_ngram_database(
            notes_directory=self.config['notes_directory'],
            ngram_db_dir=self.config['cache_directory'])

    def get_typeahead_suggestions(self, query_string, limit=10):
        return _get_typeahead_suggestions(
            ngram_db_dir=self.config['cache_directory'],
            query_string=query_string, limit=limit)

    #
    def get_subdirs(self, max_depth=2, exclude_hidden=True):
        return _get_subdirs(notes_directory=self.config['notes_directory'],
                            max_depth=max_depth, exclude_hidden=exclude_hidden)

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
    def get_questions(self, question_status='all', directory_filter=None):
        return _get_questions(notes_directory=self.config['notes_directory'],
                              question_status=question_status,
                              directory_filter=directory_filter,
                              grep_path=self.config['grep_path'])

    # Definitions
    def get_definitions(self, directory_filter=None):
        return _get_definitions(notes_directory=self.config['notes_directory'],
                                directory_filter=directory_filter,
                                grep_path=self.config['grep_path'])

    # Locations
    def get_locations(self, directory_filter=None):
        return _get_locations(notes_directory=self.config['notes_directory'],
                              directory_filter=directory_filter,
                              grep_path=self.config['grep_path'])

    # Record Sets
    def get_record_sets(self, directory_filter=None):
        return _get_record_sets(notes_directory=self.config['notes_directory'],
                                directory_filter=directory_filter,
                                grep_path=self.config['grep_path'])

    def get_record_set(self, file_path, line_number, parse=True,
                       parse_format='json', include_config=False):
        return _get_record_set(notes_directory=self.config['notes_directory'],
                               file_path=file_path, line_number=line_number,
                               parse=parse, parse_format=parse_format,
                               include_config=include_config)
