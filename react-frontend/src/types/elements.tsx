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
  default_directory: string,
  log_file_path: string,
  log_level: string,
  grep_path: string,
  find_path: string,
  patch_path: string,
  frontend: FrontendConfig,
  log_format: string
}

export type CalendarEvent = {
  file_path: string,
  line_number: string,
  event: string,
  date: string,
  start?: string,
  end?: string,
  element_id: string,
  type: "section" | "incomplete_todo" | "completed_todo" | "skipped_todo" | "question" | "answer"
}

type YearIndex = string
type MonthIndex = string
type DayIndex = string

export type Calendar = {
  [key: YearIndex]: {
    [key: MonthIndex]: {
      [key: DayIndex]: CalendarEvent[]
    }
  }
}
