# Shorthand Architecture

## Config
- JSON file at `/etc/shorthand/shorthand_config.json`

## Notes Directory
- `/var/lib/shorthand/notes`
    + A bunch of `.note` files in here

## Cache Directory
- `/var/lib/shorthand/cache`
    + `recent_files.txt` - Files which were recently accessed via the file finder

## HTTP API
- `/api/v1/pull`
- `/api/v1/todos`
- `/api/v1/mark_todo`
- `/api/v1/questions`
- `/api/v1/tags`
- `/api/v1/calendar`
- `/api/v1/definitions`
- `/api/v1/locations`
- `/api/v1/record_sets`
- `/api/v1/record_set`
- `/api/v1/search_notes`
- `/api/v1/context`
- `/api/v1/note`
    - `GET` to get the current state of a note
    - `PUT` to update the content of a note
- `/api/v1/typeahead`
- `/api/v1/stamp`
- `/api/v1/config`
    - `GET` to get the current config of the notes server
    - `POST` to update the configuration of the notes server

## UI
- `/js/<path:path>` - Get static JS
- `/css/<path:path>` - Get static CSS
- `/img/<path:path>` -
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
