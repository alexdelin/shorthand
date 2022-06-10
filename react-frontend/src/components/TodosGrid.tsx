import { Fragment, useMemo } from 'react';
import { Grid, _ } from 'gridjs-react';
import { useQuery } from 'react-query';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm'
import rehypeKatex from 'rehype-katex';
import { GetTodosResponse, Tag } from '../types';
import { StyledReactMarkdown, StyledTag } from './TodosGrid.styles';
import { TODO_QUERY_CONFIG } from '../pages/TodosPage';

type TodosGridProps = {
  status: string,
  search: string,
  directory: string,
  tags: string,
}

export function TodosGrid(props: TodosGridProps) {

  // const [todosLimit, setTodosLimit] = useState(100);

  const {
    data: todoData
  } = useQuery<GetTodosResponse, Error>('todos-' + props.status + '-' + props.directory + '-' + props.search + '-' + props.tags, () =>
    // TODO - Replace with a better library
    fetch('http://localhost:8181/api/v1/todos?status=' + props.status + '&directory_filter=' + props.directory + '&query_string=' + props.search + '&sort_by=start_date&tag=' + props.tags).then(res =>
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
  }, [todoData, props.status]);

  if (todoData === undefined) return <div>Loading...</div>

  function getTodoElement(todoText: string, tags: Tag[]) {
    // This is just an optimization to create
    // Todo elements with as few plugins as possible

    // If the todo has LaTeX
    if (todoText.includes('$')) {
      return _(<Fragment>
        <StyledReactMarkdown
          children={todoText}
          linkTarget="_blank"
          remarkPlugins={[remarkMath, remarkGfm]}
          rehypePlugins={[rehypeKatex]}
        />
        {tags.map((tag) => <StyledTag>{tag}</StyledTag>)}
      </Fragment>)
    }

    // If the todo has GFM strikethrough
    if (todoText.includes('~')) {
      return _(<Fragment>
        <StyledReactMarkdown
          children={todoText}
          linkTarget="_blank"
          remarkPlugins={[remarkGfm]}
        />
        {tags.map((tag) => <StyledTag>{tag}</StyledTag>)}
      </Fragment>)
    }

    // If the todo has markdown styling
    if (todoText.includes('_') ||
        todoText.includes('](') ||
        todoText.includes('`') ||
        todoText.includes('*')) {
      return _(<Fragment>
        <StyledReactMarkdown
          children={todoText}
          linkTarget="_blank"
        />
        {tags.map((tag) => <StyledTag>{tag}</StyledTag>)}
      </Fragment>)
    }

    // If the todo has a GFM link
    if (todoText.includes('www.') ||
        todoText.includes('http://') ||
        todoText.includes('https://')) {
      return _(<Fragment>
        <StyledReactMarkdown
          children={todoText}
          linkTarget="_blank"
          remarkPlugins={[remarkGfm]}
        />
        {tags.map((tag) => <StyledTag>{tag}</StyledTag>)}
      </Fragment>)
    }

    // If the todo has no markdown
    return _(<Fragment>
      <div>{todoText}</div>
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
