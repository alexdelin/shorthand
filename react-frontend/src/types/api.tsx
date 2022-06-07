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

export type GetNoteResponse = string;
