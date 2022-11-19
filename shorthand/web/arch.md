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
- General Notes Features
    + `/api/v1/search` 
    + `/api/v1/note`
        * `GET` to get the current state of a note
        * `PUT` to update the content of a note
    + `/api/v1/toc`
    + `/api/v1/subdirs`
    + `/api/v1/links`
    + `/api/v1/links/validate`
    + `/api/v1/typeahead`
    + `/api/v1/stamp`
    + `/api/v1/files`
    + `/api/v1/record_view`
    + `/api/v1/tags`
    + `/api/v1/calendar`
- Elements
    + `/api/v1/todos`
    + `/api/v1/locations`
    + `/api/v1/mark_todo`
    + `/api/v1/questions`
    + `/api/v1/definitions`
    + `/api/v1/record_sets`
    + `/api/v1/record_set`
    + `/api/v1/locations`


## Frontend API
- `/frontend-api/redered-markdown`
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
