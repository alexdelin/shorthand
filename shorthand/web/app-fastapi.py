import logging
import os
from typing import Annotated, Dict, List, Literal, Optional, Union

from fastapi import FastAPI, Body, Response, UploadFile
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings

from shorthand import ShorthandServer
from shorthand.calendar import Calendar, CalendarMode
from shorthand.edit_history import NoteDiff, NoteDiffType, NoteVersion, NoteVersionTimestamp
from shorthand.edit_timeline import EditTimeline
from shorthand.elements.definitions import Definition
from shorthand.elements.locations import Location
from shorthand.elements.questions import QuestionStatus
from shorthand.elements.todos import Todo, TodoStatus, analyze_todos
from shorthand.frontend.render import RenderedMarkdown, get_rendered_markdown
from shorthand.notes import Link
from shorthand.search import AggregatedFullTextSearchResult, \
                             FullTextSearchResult
from shorthand.stamping import StampingChanges
from shorthand.toc import TOC
from shorthand.types import ACKResponse, CSVData, InternalAbsolutePath, \
                            NotePath, RawNoteContent, RawNoteLine, RawResourceContent, ResourcePath, \
                            Subdir
from shorthand.utils.api import WrappedResponse, wrap_response_data
from shorthand.utils.config import CONFIG_FILE_LOCATION, ShorthandConfig, \
                                   ShorthandConfigUpdates
from shorthand.utils.csv import _convert_to_csv
from shorthand.utils.paths import _is_resource_path, get_full_path


log = logging.getLogger(__name__)

STATIC_FOLDER = '../../react-frontend/build'


class Settings(BaseSettings):
    # Can override by setting env var CONFIG_PATH when running the app
    config_path: str = CONFIG_FILE_LOCATION


settings = Settings()


app = FastAPI(
    title='Shorthand API',
    summary='summary',
    description='description',
    version='0.1.0'
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)


# app.mount("/", StaticFiles(directory=f"{STATIC_FOLDER}", html=True), name="static-html")
app.mount("/static/js", StaticFiles(directory=f"{STATIC_FOLDER}/static/js"), name="static-js")
app.mount("/static/css", StaticFiles(directory=f"{STATIC_FOLDER}/static/css"), name="static-css")
app.mount("/static/media", StaticFiles(directory=f"{STATIC_FOLDER}/static/media"), name="static-media")


@app.get('/')
@app.get('/{path}')
def serve_react(path):
    if path != "" and os.path.exists(f'{STATIC_FOLDER}/{path}'):
        return FileResponse(f'{STATIC_FOLDER}/{path}')
    else:
        return FileResponse(f'{STATIC_FOLDER}/index.html')


@app.get('/api/v1/config',
    tags=['Config'],
    # summary='',
    # description=''
    )
def get_server_config() -> ShorthandConfig:
    server = ShorthandServer(settings.config_path)
    log.info('Returning config')
    return server.get_config()


@app.post('/api/v1/config', tags=['Config'], response_class=PlainTextResponse)
def update_server_config(updates: ShorthandConfigUpdates) -> ACKResponse:
    server = ShorthandServer(settings.config_path)
    log.info('Updating config')
    server.update_config(updates)
    server.save_config()
    return 'ack'


@app.get('/api/v1/search',
    tags=['Search'],
    # summary='',
    # description=''
    )
def get_search_results(
        query_string: str,
        case_sensitive: bool = False,
        aggregate_by_file: bool = False
        ) -> Union[list[FullTextSearchResult],
                   list[AggregatedFullTextSearchResult]]:
    server = ShorthandServer(settings.config_path)
    return server.search_full_text(
        query_string=query_string,
        case_sensitive=case_sensitive,
        aggregate_by_file=aggregate_by_file)


@app.get('/api/v1/note', tags=['Notes'], response_class=PlainTextResponse)
def get_full_note(path: NotePath) -> RawNoteContent:
    server = ShorthandServer(settings.config_path)
    return server.get_note(path)


@app.post('/api/v1/note', tags=['Notes'], response_class=PlainTextResponse)
def write_updated_note(path: NotePath,
                       content: Annotated[RawNoteContent, Body()]
                       ) -> ACKResponse:
    server = ShorthandServer(settings.config_path)
    server.update_note(path, content)
    return 'ack'


@app.get('/api/v1/resource', tags=['Resources'], response_class=FileResponse)
def get_resource(path: ResourcePath):
    server = ShorthandServer(settings.config_path)
    if _is_resource_path(server.notes_directory, path, must_exist=True):
        return FileResponse(
            path=get_full_path(server.notes_directory, path),
            filename=path.split('/')[-1])
    else:
        raise ValueError(f'Invalid resource path {path} provided')


@app.get('/api/v1/toc', tags=['Notes'])
def get_toc_data(include_resources: bool = False) -> TOC:
    server = ShorthandServer(settings.config_path)
    return server.get_toc(include_resources=include_resources)


@app.get('/api/v1/subdirs', tags=['Notes'])
def get_subdirs_data() -> List[Subdir]:
    server = ShorthandServer(settings.config_path)
    return server.get_subdirs()


@app.get('/api/v1/links', tags=['Notes'])
def get_note_links(source: Optional[NotePath] = None,
                   target: Optional[NotePath] = None,
                   note: Optional[NotePath] = None,
                   include_external: bool = False,
                   include_invalid: bool = False
                   ) -> List[Link]:
    server = ShorthandServer(settings.config_path)
    return server.get_links(source=source, target=target, note=note,
                            include_external=include_external,
                            include_invalid=include_invalid)


@app.get('/api/v1/links/validate', tags=['Notes'])
def validate_note_links(source: NotePath) -> list[Link]:
    server = ShorthandServer(settings.config_path)
    return server.validate_internal_links(source=source)


@app.get('/api/v1/typeahead', tags=['Notes'])
def get_typeahead(query: str) -> List[str]:
    server = ShorthandServer(settings.config_path)
    return server.get_typeahead_suggestions(
            query_string=query)


@app.get('/api/v1/stamp', tags=['Notes'])
def stamp() -> StampingChanges:
    server = ShorthandServer(settings.config_path)
    return server.stamp_notes()


@app.post('/api/v1/stamp/raw', tags=['Notes'], response_class=PlainTextResponse)
def stamp_raw(raw_note: Annotated[RawNoteContent, Body()]) -> RawNoteContent:
    server = ShorthandServer(settings.config_path)
    return server.stamp_raw_note(raw_note)


@app.get('/api/v1/files', tags=['Search'])
def get_files(query_string: Optional[str] = None,
              prefer_recent: bool = True,
              case_sensitive: bool = True) -> List[NotePath]:
    server = ShorthandServer(settings.config_path)
    return server.search_filenames(
        prefer_recent=prefer_recent,
        query_string=query_string, case_sensitive=case_sensitive)


@app.post('/api/v1/record_view', tags=['Notes'], response_class=PlainTextResponse)
def record_file_view_api(note_path: NotePath) -> ACKResponse:
    server = ShorthandServer(settings.config_path)
    server.record_file_view(note_path=note_path)
    return 'ack'


# Needs Typing
@app.get('/api/v1/tags', tags=['Elements'])
def fetch_tags(directory_filter: Optional[Subdir] = None
               ) -> WrappedResponse[str]:
    server = ShorthandServer(settings.config_path)
    if directory_filter == 'ALL':
        directory_filter = None
    tags = server.get_tags(directory_filter=directory_filter)
    return wrap_response_data(tags)


# Needs Typing
@app.get('/api/v1/calendar')
def fetch_calendar(mode: CalendarMode = 'recent',
                   directory_filter: Optional[Subdir] = None
                   ) -> Calendar:
    server = ShorthandServer(settings.config_path)
    if directory_filter == 'ALL':
        directory_filter = None
    return server.get_calendar(mode=mode, directory_filter=directory_filter)


@app.get('/api/v1/locations', tags=['Elements'])
def get_gps_locations(directory_filter: Optional[Subdir]
                      ) -> WrappedResponse[Location]:
    server = ShorthandServer(settings.config_path)
    locations = server.get_locations(directory_filter=directory_filter)
    return wrap_response_data(locations)


@app.get('/api/v1/todos', tags=['Elements'])
def get_current_todos(status: TodoStatus = 'incomplete',
                      directory_filter: Optional[Subdir] = None,
                      query_string: Optional[str] = None,
                      sort_by: Optional[str] = None,
                      tag: Optional[str] = None,
                      suppress_future: bool = True,
                      case_sensitive: bool = False
                      ) -> WrappedResponse[Todo]:
    server = ShorthandServer(settings.config_path)

    if directory_filter in ['ALL', '']:
        directory_filter = None
    if tag == 'ALL':
        tag = None

    todos = server.get_todos(todo_status=status.lower(),
                             directory_filter=directory_filter,
                             query_string=query_string,
                             case_sensitive=case_sensitive, sort_by=sort_by,
                             suppress_future=suppress_future, tag=tag)
    log.info(f'Returning {len(todos)} todo results')

    wrapped_response = wrap_response_data(todos)
    wrapped_response['meta'] = analyze_todos(todos)

    return wrapped_response


@app.post('/api/v1/mark_todo', tags=['Elements'], response_class=PlainTextResponse)
def mark_todo_status(filename: NotePath, line_number: int,
                     status: TodoStatus) -> RawNoteLine:
    server = ShorthandServer(settings.config_path)
    return server.mark_todo(note_path=filename, line_number=line_number,
                            status=status)


# Needs Typing
@app.get('/api/v1/questions', tags=['Elements'])
def fetch_questions(status: QuestionStatus = 'all',
                    directory_filter: Optional[Subdir] = None
                    ) -> WrappedResponse[dict]:
    server = ShorthandServer(settings.config_path)

    if directory_filter == 'ALL':
        directory_filter = None
    log.info(f'Getting {status} questions in ' +
                            f'directory {directory_filter}')

    questions = server.get_questions(
        question_status=status, directory_filter=directory_filter)
    log.info(f'Returning {len(questions)} question results')
    return wrap_response_data(questions)


@app.get('/api/v1/definitions', tags=['Elements'])
def fetch_definitions(directory_filter: Optional[Subdir] = None,
                      query_string: Optional[str] = None,
                      case_sensitive: bool = False,
                      search_term_only: bool = True,
                      include_sub_elements: bool = False
                      ) -> WrappedResponse[Definition]:
    server = ShorthandServer(settings.config_path)

    if directory_filter == 'ALL':
        directory_filter = None

    definitions = server.get_definitions(
        directory_filter=directory_filter,
        query_string=query_string,
        case_sensitive=case_sensitive,
        search_term_only=search_term_only,
        include_sub_elements=include_sub_elements)
    return wrap_response_data(definitions)


@app.get('/api/v1/definitions/csv', tags=['Elements'], response_class=PlainTextResponse)
def fetch_definitions_csv(response: Response,
                          directory_filter: Optional[Subdir] = None
                          ) -> CSVData:
    server = ShorthandServer(settings.config_path)

    if directory_filter == 'ALL':
        directory_filter = None

    definitions = server.get_definitions(directory_filter=directory_filter,
                                         include_sub_elements=True)

    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment'
    return _convert_to_csv(definitions)


# Needs Typing
@app.get('/api/v1/record_sets', tags=['Elements'])
def fetch_record_sets(directory_filter: Optional[Subdir] = None
                      ) -> WrappedResponse[dict]:
    server = ShorthandServer(settings.config_path)

    if directory_filter == 'ALL':
        directory_filter = None

    record_sets = server.get_record_sets(directory_filter=directory_filter)
    return wrap_response_data(record_sets)


# Needs Typing
@app.get('/api/v1/record_set', tags=['Elements'])
def fetch_record_set(file_path: NotePath, line_number: int,
                     parse: bool = True, include_config: bool = False,
                     parse_format: str = 'json') -> Dict:
    server = ShorthandServer(settings.config_path)
    return server.get_record_set(
        file_path=file_path,
        line_number=line_number,
        parse=parse,
        parse_format=parse_format,
        include_config=include_config)


@app.put('/api/v1/filesystem/create', tags=['Filesystem'], response_class=PlainTextResponse)
def filesystem_create(path: InternalAbsolutePath,
                      type: Literal['file', 'directory'] = 'file'
                      ) -> ACKResponse:
    server = ShorthandServer(settings.config_path)

    if type == 'file':
        server.create_file(path)
    elif type == 'directory':
        server.create_directory(path)
    else:
        raise ValueError(f'Got unknown resource type {type}')
    return 'ack'


@app.post('/api/v1/filesystem/move', tags=['Filesystem'], response_class=PlainTextResponse)
def filesystem_move(source: InternalAbsolutePath,
                    destination: InternalAbsolutePath) -> ACKResponse:
    server = ShorthandServer(settings.config_path)
    server.move_file_or_directory(source, destination)
    return 'ack'


@app.delete('/api/v1/filesystem/delete', tags=['Filesystem'], response_class=PlainTextResponse)
def filesystem_delete(path: InternalAbsolutePath,
                      type: Literal['file', 'directory'] = 'file',
                      recursive: bool = False
                      ) -> ACKResponse:
    server = ShorthandServer(settings.config_path)

    if type == 'file':
        server.delete_file(path)
    elif type == 'directory':
        server.delete_directory(path, recursive)
    else:
        raise ValueError(f'Got unknown resource type {resource_type}')
    return 'ack'


@app.post('/api/v1/filesystem/upload', tags=['Filesystem'], response_class=PlainTextResponse)
def filesystem_upload(directory: Subdir, file: UploadFile) -> ACKResponse:
    server = ShorthandServer(settings.config_path)

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if not file or file.filename == '':
        raise ValueError('No selected file')

    server.upload_resource(f'{directory}/{file.filename}', file.file.read())
    return 'ack'


@app.get('/api/v1/archive', tags=['Notes'])
def get_archive(response: Response) -> bytes:
    server = ShorthandServer(settings.config_path)
    return Response(
        content=server.get_note_archive(),
        media_type="application/x-xz",
        headers={'Content-Disposition': 'attachment'}
    )


@app.get('/api/v1/edit_timeline', tags=['History'])
def get_edit_timeline(note_path: NotePath) -> EditTimeline:
    server = ShorthandServer(settings.config_path)
    return server.get_edit_timeline(note_path=note_path)


@app.get('/api/v1/note_version', tags=['History'], response_class=PlainTextResponse)
def get_note_version(note_path: NotePath, timestamp: NoteVersionTimestamp
                     ) -> NoteVersion:
    server = ShorthandServer(settings.config_path)
    return server.get_note_version(note_path=note_path,
                                   version_timestamp=timestamp)


@app.get('/api/v1/note_diff', tags=['History'], response_class=PlainTextResponse)
def get_edit_diff(note_path: NotePath, timestamp: NoteVersionTimestamp,
                  diff_type: NoteDiffType) -> NoteDiff:
    server = ShorthandServer(settings.config_path)
    return server.get_note_diff(note_path=note_path,
                                timestamp=timestamp,
                                diff_type=diff_type)

# Needs Typing
@app.get('/frontend-api/rendered-markdown', tags=['Frontend'])
def send_processed_markdown(path: NotePath) -> RenderedMarkdown:
    server = ShorthandServer(settings.config_path)
    file_content = server.get_note(path)
    return get_rendered_markdown(file_content, path)


@app.get('/frontend-api/get-open-files', tags=['Frontend'])
def send_get_open_files() -> List[NotePath]:
    server = ShorthandServer(settings.config_path)
    return server.get_open_files()


@app.post('/frontend-api/open-file', tags=['Frontend'], response_class=PlainTextResponse)
def call_open_file(path: NotePath) -> ACKResponse:
    server = ShorthandServer(settings.config_path)
    return server.open_file(path)


@app.post('/frontend-api/close-file', tags=['Frontend'], response_class=PlainTextResponse)
def call_close_file(path: NotePath) -> ACKResponse:
    server = ShorthandServer(settings.config_path)
    return server.close_file(path)


@app.post('/frontend-api/clear-open-files', tags=['Frontend'], response_class=PlainTextResponse)
def call_clear_open_files() -> ACKResponse:
    server = ShorthandServer(settings.config_path)
    return server.clear_open_files()

