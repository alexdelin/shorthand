import { Fragment } from 'react';
import { Grid, _ } from 'gridjs-react';
import { useQuery } from 'react-query';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm'
import rehypeKatex from 'rehype-katex';
import ReactMarkdown from 'react-markdown';
import styled from 'styled-components';

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

type Tag = string;

type Todo = {
  display_path: string,
  end_date: string,
  file_path: string,
  line_number: string,
  start_date: string,
  status: string,
  tags: Tag[],
  todo_text: string
}

type TodosResponse = {
  items: Todo[],
  count: number,
  meta: any
}

type TodosGridProps = {
  status: string,
  search: string,
  directory: string,
  tags: string
}

export function TodosGrid({ status, search, directory, tags }: TodosGridProps) {

  const {
    data: todoData
  } = useQuery<TodosResponse, Error>('todos-' + status + '-' + directory + '-' + search + '-' + tags, () =>
    fetch('http://localhost:8181/api/v1/todos?status=' + status + '&directory_filter=' + directory + '&query_string=' + search + '&sort_by=start_date&tag=' + tags).then(res =>
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
          remarkPlugins={[remarkMath]}
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
    data={todoData.items.map((todo: Todo) => ([
        todo.display_path,
        getTodoElement(todo.todo_text, todo.tags),
        todo.start_date,
        todo.end_date,
        todo.line_number,
        'placeholder'
    ]))}
    columns={[
      'Todo', 'Path', 'Start Date', 'End Date',
      'Line #', 'Actions'
    ]}
  />
}
