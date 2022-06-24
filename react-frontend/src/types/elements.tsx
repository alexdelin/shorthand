// Type definitions for Shorthand Core Elements

export type Note = string;

export type Todo = {
  display_path: string,
  end_date: string,
  file_path: string,
  line_number: string,
  start_date: string,
  status: string,
  tags: Tag[],
  todo_text: string
}

export type Tag = string;

export type Subdir = string;

export type FrontendConfig = {
  view_history_limit: number,
  map_tileserver_url: string
}

export type Config = {
  notes_directory: string,
  cache_directory: string,
  default_directory: string,
  log_file_path: string,
  log_level: string,
  grep_path: string,
  find_path: string,
  frontend: FrontendConfig,
  log_format: string
}
