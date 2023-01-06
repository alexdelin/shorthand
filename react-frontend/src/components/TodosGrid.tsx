import { Fragment, useMemo } from 'react';
import { Grid, _ } from 'gridjs-react';
import { useQuery, useMutation } from 'react-query';
import { useQueryClient } from 'react-query';
import MarkdownIt from 'markdown-it';
import tm from 'markdown-it-texmath';
import { GetTodosResponse, Tag, Todo, ShorthandApiError } from '../types';
import {
  StyledTodoText,
  StyledTag, ActionButton
} from './TodosGrid.styles';
// import { TODO_QUERY_CONFIG } from '../pages/TodosPage';

type TodosGridProps = {
  status: string,
  search: string,
  directory: string,
  tags: string,
}

type TodosQueryKey = {
  status: string,
  search: string,
  directory: string,
  tags: string,
}

type markTodoMutationProps = {
  todo: Todo,
  status: 'complete' | 'skipped',
}

const writer = MarkdownIt({}).use(
  tm,{ delimiters: 'dollars', macros: {"\\RR": "\\mathbb{R}"}
});

function getTodoElement(todoText: string, tags: Tag[]) {
  return _(<Fragment>
    <StyledTodoText
      dangerouslySetInnerHTML={{__html: writer.render(todoText)}}
    />
    {tags.map((tag) => <StyledTag>{tag}</StyledTag>)}
  </Fragment>);
}

function processDateString(dateString: string) {
  return dateString;
}

export function TodosGrid(props: TodosGridProps) {

  const queryClient = useQueryClient();

  const markTodoMutation = useMutation<string, ShorthandApiError, markTodoMutationProps>({
    mutationFn: async (input) => {
      const todo = input.todo;
      const res = await fetch(
        `http://localhost:8181/api/v1/mark_todo?filename=${todo.file_path}&line_number=${todo.line_number}&status=${input.status}`,
        { method: 'POST' }
      )
      return res.text();
    },
    onSuccess: async (data, input) => {
      console.log(`Updated todo to ${data}`);
      queryClient.invalidateQueries({
        predicate: (query) => {
          const key0 = query.queryKey[0];
          const key1 = query.queryKey[1] as TodosQueryKey;
          return query.queryKey[0] === 'todos' && (
            key1.status === props.status ||
            key1.status === input.status ||
            key1.directory === props.directory ||
            key1.search === props.search ||
            key1.tags === props.tags)
        }
      })
    },
    onError: async (error: ShorthandApiError) => {
      //TODO - build real error handling
      console.log(`Got an error from the API: ${JSON.stringify(error)}`)
    },
  })

  const {
    data: todoData
  } = useQuery<GetTodosResponse, Error>(
    ['todos', {
      status: props.status,
      directory: props.directory,
      search: props.search,
      tags: props.tags
    }], () =>

    // TODO - Replace with a better library
    fetch(`http://localhost:8181/api/v1/todos?status=${props.status}&directory_filter=${props.directory}&query_string=${props.search}&sort_by=start_date&tag=${props.tags}`).then(res =>
      res.json()
    )
    // ,TODO_QUERY_CONFIG
  )

  const elements = useMemo(() => {
    if (todoData === undefined) {
      return [];
    } else {
      return todoData.items.map((todo) => (
        props.status === 'Incomplete' ? [
          `${todo.display_path}: ${todo.line_number}`,
          getTodoElement(todo.todo_text, todo.tags),
          processDateString(todo.start_date),
          getActionButtons(todo)
        ] : [
          `${todo.display_path}: ${todo.line_number}`,
          getTodoElement(todo.todo_text, todo.tags),
          processDateString(todo.start_date),
          processDateString(todo.end_date),
          getActionButtons(todo)
      ]))
    }
  // eslint-disable-next-line
  }, [todoData, props.status]);

  function markTodo(todo: Todo, status: 'complete' | 'skipped') {
    if (todo.status === status) {
      console.log(`Todo already has status ${status}, skipping...`);
      return;
    }
    console.log(`marking todo at ${todo.file_path}:${todo.line_number}`);
    markTodoMutation.mutate({ todo, status });
  }

  function getActionButtons(todo: Todo) {
    return _(
      <div>
        <ActionButton onClick={() => markTodo(todo, 'complete')} className="bi bi-check-circle action-button"></ActionButton>
        <ActionButton onClick={() => markTodo(todo, 'skipped')} className="bi bi-slash-circle action-button"></ActionButton>
        <ActionButton className="bi bi-pencil action-button"></ActionButton>
      </div>);
  }

  if (todoData === undefined) return <div>Loading...</div>

  return <Fragment>
    <Grid
      data={elements}
      pagination={{
        enabled: true,
        limit: 50
      }}
      columns={props.status === 'Incomplete' ? [
        'Path', 'Todo', 'Start Date',
        'Actions'
      ] : [
        'Path', 'Todo', 'Start Date', 'End Date',
        'Actions'
      ]}
    />
  </Fragment>

}
