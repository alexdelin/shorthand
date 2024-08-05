import logging
from typing import Optional

from shorthand.notes import _get_note, _update_note, \
                            _validate_internal_links, _append_to_note, \
                            _create_note, _get_backlinks, _get_links
from shorthand.calendar import CalendarMode, _get_calendar
from shorthand.tags import _get_tags
from shorthand.toc import _get_toc
from shorthand.stamping import _stamp_notes, _stamp_raw_note
from shorthand.search import _search_full_text, _search_filenames, \
                             _record_file_view
from shorthand.elements.todos import _get_todos, _mark_todo
from shorthand.elements.questions import _get_questions
from shorthand.elements.definitions import _get_definitions
from shorthand.elements.locations import _get_locations
from shorthand.elements.record_sets import _get_record_sets, _get_record_set
from shorthand.frontend.typeahead import _update_ngram_database, \
                                         _get_typeahead_suggestions
from shorthand.types import InternalAbsoluteFilePath, InternalAbsolutePath, Subdir
from shorthand.utils.archive import _get_note_archive
from shorthand.utils.config import _get_notes_config, _write_config, \
                                   _modify_config
from shorthand.utils.paths import _get_subdirs
from shorthand.utils.logging import get_handler, log_level_from_string
from shorthand.utils.buffers import _new_buffer, _list_buffers, \
                                    _get_buffer_content, \
                                    _update_buffer_content, \
                                    _delete_buffer, _write_buffer
from shorthand.utils.filesystem import _create_file, _create_directory, \
                                       _move_file_or_directory, _delete_file, \
                                       _delete_directory, _upload_resource


# Set up the default module-level logger which the rest of the library
#   will inherit. This will be updated with the settings specified in the
#   config when the server object is initialized.
log = logging.getLogger(__name__)


class ShorthandServer(object):
    '''Main Shorthand Server API

       This implementation exposes a nicer API than calling
       the underlying functions directly and manages basic
       configuration transparently.

       The ShorthandServer is meant to be instantiated on a
       machine with local access to the notes directory, and
       all requests will be processed against the local filesystem.

       The API exposed by the server abstracts away the location
       of the notes directory. Only relative paths within the notes
       directory should be provided to or returned from the server.
    '''

    def __init__(self, config_path):
        '''Initialize the server with the configuration
           in the specified file
        '''
        self.log = log

        self.config_path = config_path
        self.reload_config()

    def setup_logging(self):
        '''Setup logging handlers to match what is specified in config
        '''
        self.log.setLevel(log_level_from_string(self.config['log_level']))
        if self.log.handlers:
            for h in self.log.handlers:
                h.close()
            self.log.handlers.clear()
        log_handler = get_handler(self.config)
        self.log.addHandler(log_handler)

    # -------------------------
    # --- Config Management ---
    # -------------------------
    def get_config(self):
        '''Get the current server configuration
        '''
        self.log.debug('returned config')
        return self.config

    def reload_config(self):
        '''Reload the config from the config file
        '''
        self.config = _get_notes_config(self.config_path)
        self.setup_logging()

    def update_config(self, updates):
        '''Update one or more fields in the configuration
           Note: This does not save the updated config to disk
        '''
        self.config = _modify_config(self.config, updates)
        self.setup_logging()

    def save_config(self):
        '''Save the current config to the config file
        '''
        _write_config(self.config_path, self.config)

    def check_config_init(self):
        '''Validate that config is present
        '''
        if not self.config:
            raise ValueError('Shorthand Server is not yet ' +
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

    def validate_internal_links(self, source=None):
        return _validate_internal_links(
            notes_directory=self.config['notes_directory'],
            source=source, grep_path=self.config['grep_path'])

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

    def stamp_raw_note(self, raw_note, stamp_todos=True, stamp_today=True,
                       stamp_questions=True, stamp_answers=True):
        return _stamp_raw_note(raw_note=raw_note, stamp_todos=stamp_todos,
                               stamp_today=stamp_today,
                               stamp_questions=stamp_questions,
                               stamp_answers=stamp_answers)

    # Search
    def search_full_text(self, query_string, case_sensitive=False,
                         aggregate_by_file=False):
        return _search_full_text(
            notes_directory=self.config['notes_directory'],
            query_string=query_string, case_sensitive=case_sensitive,
            aggregate_by_file=aggregate_by_file,
            grep_path=self.config['grep_path'])

    def search_filenames(self, prefer_recent=True, query_string=None,
                         case_sensitive=False):
        return _search_filenames(
                notes_directory=self.config['notes_directory'],
                prefer_recent_files=prefer_recent,
                query_string=query_string, case_sensitive=case_sensitive,
                grep_path=self.config['grep_path'],
                find_path=self.config['find_path'])

    def record_file_view(self, note_path):
        return _record_file_view(
            notes_directory=self.config['notes_directory'],
            note_path=note_path,
            history_limit=self.config['frontend']['view_history_limit'])

    # Calendar
    def get_calendar(self, mode: CalendarMode = CalendarMode.Recent,
                     directory_filter=None):
        return _get_calendar(notes_directory=self.config['notes_directory'],
                             mode=mode,
                             directory_filter=directory_filter,
                             grep_path=self.config['grep_path'])

    # Tags
    def get_tags(self, directory_filter=None):
        return _get_tags(notes_directory=self.config['notes_directory'],
                         directory_filter=directory_filter,
                         grep_path=self.config['grep_path'])

    # TOC
    def get_toc(self, include_resources=False):
        return _get_toc(notes_directory=self.config['notes_directory'],
                        include_resources=include_resources)

    # Typeahead
    def update_ngram_database(self):
        return _update_ngram_database(
            notes_directory=self.config['notes_directory'])

    def get_typeahead_suggestions(self, query_string, limit=10):
        return _get_typeahead_suggestions(
            notes_directory=self.config['notes_directory'],
            query_string=query_string, limit=limit)

    # Subdirs
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
    def get_definitions(self, directory_filter=None,
                        query_string: Optional[str] = None,
                        case_sensitive: bool = False,
                        search_term_only: bool = True,
                        include_sub_elements: bool = False):
        return _get_definitions(notes_directory=self.config['notes_directory'],
                                directory_filter=directory_filter,
                                query_string=query_string,
                                case_sensitive=case_sensitive,
                                search_term_only=search_term_only,
                                grep_path=self.config['grep_path'],
                                include_sub_elements=include_sub_elements)

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

    # ---------------
    # --- Buffers ---
    # ---------------
    def new_buffer(self):
        return _new_buffer(notes_directory=self.config['notes_directory'])

    def list_buffers(self):
        return _list_buffers(notes_directory=self.config['notes_directory'])

    def get_buffer_content(self, buffer_id: str):
        return _get_buffer_content(
            notes_directory=self.config['notes_directory'],
            buffer_id=buffer_id)

    def update_buffer_content(self, buffer_id: str, content: str):
        return _update_buffer_content(
            notes_directory=self.config['notes_directory'],
            buffer_id=buffer_id, content=content)

    def delete_buffer(self, buffer_id: str):
        return _delete_buffer(notes_directory=self.config['notes_directory'],
                              buffer_id=buffer_id)

    def write_buffer(self, notes_directory: str, buffer_id: str,
                     note_path: str):
        return _write_buffer(notes_directory=self.config['notes_directory'],
                             buffer_id=buffer_id, note_path=note_path)

    # ------------------------
    # --- Filesystem Utils ---
    # ------------------------
    def create_file(self, file_path: InternalAbsoluteFilePath):
        return _create_file(notes_directory=self.config['notes_directory'],
                            file_path=file_path)

    def create_directory(self, directory_path: Subdir):
        return _create_directory(notes_directory=self.config['notes_directory'],
                                 directory_path=directory_path)

    def upload_resource(self, resource_path, content):
        return _upload_resource(notes_directory=self.config['notes_directory'],
                                path=resource_path,
                                content=content)

    def move_file_or_directory(self, source: InternalAbsolutePath,
                               destination: InternalAbsolutePath):
        return _move_file_or_directory(
            notes_directory=self.config['notes_directory'],
            source=source, destination=destination)

    def delete_file(self, file_path: InternalAbsoluteFilePath):
        return _delete_file(notes_directory=self.config['notes_directory'],
                            file_path=file_path)

    def delete_directory(self, directory_path: Subdir,
                         recursive: bool = False):
        return _delete_directory(
            notes_directory=self.config['notes_directory'],
            directory_path=directory_path, recursive=recursive)

    def get_note_archive(self):
        return _get_note_archive(notes_directory=self.config['notes_directory'])
