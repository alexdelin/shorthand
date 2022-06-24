import { Fragment, useMemo } from 'react';
import { Grid, _ } from 'gridjs-react';
import { useQuery } from 'react-query';
import MarkdownIt from 'markdown-it';
import tm from 'markdown-it-texmath';
import { GetTodosResponse, Tag } from '../types';
import {
  StyledTodoText,
  StyledTag
} from './TodosGrid.styles';
import { TODO_QUERY_CONFIG } from '../pages/TodosPage';

type TodosGridProps = {
  status: string,
  search: string,
  directory: string,
  tags: string,
}

const writer = MarkdownIt({}).use(
  tm,{ delimiters: 'dollars', macros: {"\\RR": "\\mathbb{R}"}
});


export function TodosGrid(props: TodosGridProps) {

  const {
    data: todoData
  } = useQuery<GetTodosResponse, Error>(`todos-${props.status}-${props.directory}-${props.search}-${props.tags}`, () =>
    // TODO - Replace with a better library
    fetch(`http://localhost:8181/api/v1/todos?status=${props.status}&directory_filter=${props.directory}&query_string=${props.search}&sort_by=start_date&tag=${props.tags}`).then(res =>
      res.json()
    ),
    TODO_QUERY_CONFIG
  )

  const elements = useMemo(() => {
    if (todoData === undefined) {
      return [];
    } else {
      return todoData.items.map((todo) => (
        props.status === 'Incomplete' ? [
          todo.display_path,
          getTodoElement(todo.todo_text, todo.tags),
          todo.start_date,
          todo.line_number,
          'placeholder'
        ] : [
          todo.display_path,
          getTodoElement(todo.todo_text, todo.tags),
          todo.start_date,
          todo.end_date,
          todo.line_number,
          'placeholder'
      ]))
    }
  // eslint-disable-next-line
  }, [todoData, props.status]);

  if (todoData === undefined) return <div>Loading...</div>

  function getTodoElement(todoText: string, tags: Tag[]) {
    return _(<Fragment>
      <StyledTodoText
        dangerouslySetInnerHTML={{__html: writer.render(todoText)}}
      />
      {tags.map((tag) => <StyledTag>{tag}</StyledTag>)}
    </Fragment>);
  }

  return <Fragment>
    <Grid
      data={elements}
      pagination={{
        enabled: true,
        limit: 50
      }}
      columns={props.status === 'Incomplete' ? [
        'Path', 'Todo', 'Start Date',
        'Line #', 'Actions'
      ] : [
        'Path', 'Todo', 'Start Date', 'End Date',
        'Line #', 'Actions'
      ]}
    />
  </Fragment>

}
