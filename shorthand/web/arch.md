# Shorthand Architecture

## Config
- JSON file at `/etc/shorthand/shorthand_config.json`

## Notes Directory
- `/var/lib/shorthand/notes`
    + A bunch of `.note` files in here

## Cache Directory
- `/var/lib/shorthand/cache`
    + `recent_files.txt` - Files which were recently accessed via the file finder
    + `open_files.json` - Files which are curently "open" in the editor in the UI

## HTTP API
- Administration
    + `/api/v1/config`
        * `GET` to get the current config of the notes server
        * `PUT` to update the configuration of the notes server
- Filesystem API (New)
    + GET `/api/v1/filesystem` (toc)
    + PUT `/api/v1/filesystem/create`
    + POST `/api/v1/filesystem/move`
    + DELETE `/api/v1/filesystem/delete`
- Search API
    + `/api/v1/search/full_text`
    + `/api/v1/search/filenames`
    + `/api/v1/search/typeahead`
- Favorites API (New)
    + GET `/api/v1/favorites`
    + PUT `/api/v1/favorites`
    + DELETE `/api/v1/favorites`
- Links API
    + `/api/v1/links`
    + `/api/v1/links/validate`
- Notes API
    + GET `/api/v1/note`
    + PUT `/api/v1/note`
    + GET `/api/v1/note/toc`
    + GET `/api/v1/record_view`
    + PUT `/api/v1/record_view`
- Stamping API
    + `/api/v1/stamp`
    + `/api/v1/stamp/raw`
- Tags API
    + `/api/v1/tags`
- Calendar API
    + `/api/v1/calendar`
- Resource API
    + `/api/v1/get_resource`: Get a non-note resource from the notes directory (images, audio, video, etc.)
- Elements API
    + `/api/v1/todos`
    + `/api/v1/mark_todo`
    + `/api/v1/questions`
    + `/api/v1/definitions`
    + `/api/v1/locations`
    + `/api/v1/record_sets`
    + `/api/v1/record_set`
- Export API
    + `/api/v1/export/csv/todos`
    + `/api/v1/export/csv/questions`
    + `/api/v1/export/csv/definitions`
    + `/api/v1/export/csv/locations`
    + `/api/v1/export/csv/record_sets`
    + `/api/v1/export/csv/record_set`
- Legacy
    + `/api/v1/search` 
        * Move to Search API
    + `/api/v1/files`
        * Move to Search API
    + `/api/v1/typeahead`
        * Move to Search API
    + `/api/v1/toc`
        * Move to Filesystem API
    + `/api/v1/subdirs`
        * Move to Filesystem API


## Frontend API
- `/frontend-api/rendered-markdown`
- `/frontend-api/get-image`
- `/frontend-api/get-open-files`
- `/frontend-api/open-file`
- `/frontend-api/close-file`
- `/frontend-api/clear-open-files`


Change Open Files API to:
- GET `/api/v1/open-files`
- PUT `/api/v1/open-files`
- DELETE `/api/v1/open-files`
- DELETE `/api/v1/open-files/all`


## UI
- `/ ` - Home Page
- `/todos` -
- `/questions` -
- `/databases` -
- `/render` -
- `/editor` -
- `/calendar` -
- `/toc` -
- `/browse` -
- `/glossary` -
- `/locations` -
