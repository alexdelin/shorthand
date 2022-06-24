// Type definitions for interacting with
//   the Shorthand API
import * as ELEMENTS from './elements';


export type TodosStats = {
  month_counts: {
      [key: string]: number
  },
  tag_counts: {
      [key: string]: number
  },
  timeline_data: Array<Array<number>>
}

// Types for getting elements from the Shorthand API
export type GetTodosResponse = {
  items: ELEMENTS.Todo[],
  count: number,
  meta: TodosStats
}

export type GetTagsResponse = {
  items: ELEMENTS.Tag[],
  count: number
}

export type GetSubdirsResponse = ELEMENTS.Subdir[];

export type GetConfigResponse = ELEMENTS.Config;

export type GetNoteResponse = ELEMENTS.Note;

// Types for data received from the Frontend API
export type GetRenderedMarkdownResponse = {
  file_content: string,
  toc_content: string
}

// Types for passing record set data
type RecordSetColumn = string
export type RecordSetColumns = RecordSetColumn[]
type RecordJSON = { [key: string]: string[] }
export type RecordSetJSON = RecordJSON[]
