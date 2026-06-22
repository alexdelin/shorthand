// Type definitions for Shorthand Core Elements

export type NoteLastModTime = string;
export type NoteContent = string;
export type NotePath = string;

export type RecentNoteWithMeta = {
  path: NotePath,
  open: boolean,
  last_modified: string
};

export type Todo = {
  display_path: string,
  end_date: string,
  file_path: NotePath,
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
};

export type CalendarEvent = {
  file_path: string,
  line_number: string,
  event: string,
  date: string,
  start?: string,
  end?: string,
  element_id: string,
  type: "section" | "incomplete_todo" | "completed_todo" | "skipped_todo" | "question" | "answer"
};

export type YearIndex = string;
export type MonthIndex = string;
export type DayIndex = string;
export type ISOFormatDate = string;

export type Calendar = {
  [key: YearIndex]: {
    [key: MonthIndex]: {
      [key: DayIndex]: CalendarEvent[]
    }
  }
};

export type DiffInfo = {
  diff_type: 'create' | 'edit' | 'move' | 'delete',
  timestamp: string,
  note_path?: NotePath,
  from_path?: NotePath,
  to_path?: NotePath,
  move_direction?: 'in' | 'out'
}
