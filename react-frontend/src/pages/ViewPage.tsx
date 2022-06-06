import { useSearchParams } from "react-router-dom";
import { useQuery } from 'react-query';
import { Fragment } from 'react';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm'
// import { remarkMermaid } from 'remark-mermaidjs';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import ReactMarkdown from 'react-markdown';
import styled from 'styled-components';
import 'highlight.js/styles/atom-one-light.css';

const StyledReactMarkdown = styled(ReactMarkdown)`
  padding: 1.5rem;
  font-family: palatino;

  // Table Styling
  & table {
    width: 100%;
    margin-bottom: 1rem;
    color: #212529;
    border-collapse: collapse;
  }

  & table thead {
    display: table-header-group;
    vertical-align: middle;
    border-color: inherit;
  }

  & table th {
    color: #fff;
    background-color: #343a40;
    border-color: #454d55;
    vertical-align: bottom;
    border-bottom: 2px solid #dee2e6;
    padding: 0.3rem;
    text-align: inherit;
    font-weight: bold;
  }

  & table td {
    word-wrap: break-word;
    padding: 0.3rem;
    vertical-align: top;
    border-top: 1px solid #dee2e6;
    display: table-cell;
  }

  // Quote Styling
  & blockquote {
    font-size: 1.25rem;
  }

  // Link Styling
  & a {
    color: blue;
  }

  // Inline Code
  & code {
    padding: 0.2em 0.4em;
    margin: 0;
    font-size: 85%;
    background-color: rgba(27,31,35,.05);
    border-radius: 3px;
  }

  // Code Blocks
  & pre code {
    font-size: 100%;
    border-color: black;
    border: 1px solid #bbb;
    padding: 15px;
    border-radius: 5px;
    background-color: #fafafa;
  }`

type GetNoteResponse = string;

export function ViewPage() {

  const [searchParams, setSearchParams] = useSearchParams();
  const notePath = searchParams.get('path');

  const {
    data: noteContent
  } = useQuery<GetNoteResponse, Error>('note-' + notePath, () =>
    fetch('http://localhost:8181/api/v1/note?path=' + notePath).then(res =>
      res.text()
    )
  )

  if (noteContent === undefined) return <div>No note found</div>

  return (
    <Fragment>
      <h2>Viewing Note: {notePath}</h2>
      <StyledReactMarkdown
          children={noteContent}
          linkTarget="_blank"
          remarkPlugins={[remarkMath, remarkGfm]}
          rehypePlugins={[rehypeKatex, [rehypeHighlight, {subset: false, ignoreMissing: true}]]}
        />
    </Fragment>
  )
}
