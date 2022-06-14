import styled from 'styled-components';
import { RenderedMarkdown } from './ViewPage';

export const ShorthandMarkdown = styled(RenderedMarkdown)`
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
    display: block;
  }

  // Display style LaTeX
  .katex-display {
      font-size: 1.25rem;
  }

  // Todo Elements
  & .todo-element {
    padding: 5px;
    margin-left: 0px !important;
    margin-right: 0px !important;
  }

  & .todo-incomplete {
    background-color: #ffb2ab;
  }

  & .todo-complete {
    background-color: #c4c5ff;
  }

  & .todo-skipped {
    background-color: #c4c4c4;
  }

  & .todo-meta {
    text-align: right;
  }

  // Question & Answer Elements
  & .qa-element {
    padding: 5px;
    margin-left: 0px !important;
    margin-right: 0px !important;
    display: flex;
  }

  & .qa-question {
    background-color: #f4b8ff;
  }

  & .qa-answer {
    background-color: #afffa3;
  }

  & .question-meta {
    text-align: right;
  }

  // Definition Elements
  & .definition-element {
    padding: 5px;
    margin-left: 0px !important;
    margin-right: 0px !important;
  }

  & .definition-term {
    background-color: #ffd38c;
  }

  & .definition-text {
    background-color: #fbfc8d;
  }

  // Locations
  span.location-coordinates {
    color: grey;
  }

  span.location-name {
    color: blue;
  }

  // Diagrams
  .mermaid {
    text-align: center;
  }

  .mermaid svg {
    max-width: 900px;
  }`
