// Type definitions for interacting with
//   the Shorthand API
import * as ELEMENTS from './elements';


export type TodosStats = {
  month_counts: any,
  tag_counts: any,
  timeline_data: any
}

export type GetTodosResponse = {
  items: ELEMENTS.Todo[],
  count: number,
  meta: TodosStats
}

export type GetTagsResponse = {
  items: ELEMENTS.Tag[],
  count: number,
  meta: any
}

export type GetSubdirsResponse = ELEMENTS.Subdir[];

export type GetConfigResponse = ELEMENTS.Config;

export type GetNoteResponse = string;
