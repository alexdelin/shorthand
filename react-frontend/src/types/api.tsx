// Type definitions for interacting with
//   the Shorthand API
import * as ELEMENTS from './elements';

export type TodosResponse = {
  items: ELEMENTS.Todo[],
  count: number,
  meta: any
}

export type TagsResponse = {
  items: ELEMENTS.Tag[],
  count: number,
  meta: any
}

export type SubdirsResponse = ELEMENTS.Subdir[];

export type ConfigResponse = ELEMENTS.Config;

export type GetNoteResponse = string;
