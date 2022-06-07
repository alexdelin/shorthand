import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';

export const StyledReactMarkdown = styled(ReactMarkdown)`
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
