import { Fragment } from 'react';
import { Grid, _ } from 'gridjs-react';
import { useQuery } from 'react-query';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm'
import rehypeKatex from 'rehype-katex';
import ReactMarkdown from 'react-markdown';
import styled from 'styled-components';
import { TodosResponse, Tag } from '../types';

const StyledReactMarkdown = styled(ReactMarkdown)`
  & a {
    color: blue;
  }

  & code {
    color: #e83e8c;
  }`

const StyledTag = styled.span`
  display: inline-block;
  padding: 0.25em 0.4em;
  font-size: 75%;
  font-weight: 700;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
  color: #fff;
  background-color: #6c757d;`

type TodosGridProps = {
  status: string,
  search: string,
  directory: string,
  tags: string
}

export function TodosGrid(props: TodosGridProps) {

  const {
    data: todoData
  } = useQuery<TodosResponse, Error>('todos-' + props.status + '-' + props.directory + '-' + props.search + '-' + props.tags, () =>
    // TODO - Replace with a better library
    fetch('http://localhost:8181/api/v1/todos?status=' + props.status + '&directory_filter=' + props.directory + '&query_string=' + props.search + '&sort_by=start_date&tag=' + props.tags).then(res =>
      res.json()
    )
  )

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

  return <Grid
    data={todoData.items.map((todo) => (
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
    ]))}
    columns={props.status === 'Incomplete' ? [
      'Path', 'Todo', 'Start Date',
      'Line #', 'Actions'
    ] : [
      'Path', 'Todo', 'Start Date', 'End Date',
      'Line #', 'Actions'
    ]}
  />

}
