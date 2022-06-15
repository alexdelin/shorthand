import styled, { css } from 'styled-components';
import { RenderedMarkdown } from './ViewPage';


const todosCss = css`
  & .todo-element {
    display: flex;
    padding: 5px;
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
  }`

const questionsAnswersCss = css`
  & .qa-element {
    padding: 5px;
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
  }`

const definitionsCss = css`
  & .definition-element {
    display: flex;
    padding: 5px;
  }

  & .definition-term {
    background-color: #ffd38c;
  }

  & .definition-text {
    background-color: #fbfc8d;
  }`

const tableCss = css`
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
  }`

const locationsCss = css`
  & span.location-coordinates {
    color: grey;
  }

  & span.location-name {
    color: blue;
  }`

const tagsCss = css`
  & span.tag {
    margin-left: 0.15rem;
    padding: 0.25em 0.4em;
    font-size: 75%;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 0.25rem;
    color: #fff;
    background-color: #6c757d;
  }`

const quotesCss = css`
  & blockquote {
    font-size: 1.25rem;
  }`

const linksCss = css`
  & a {
    color: blue;
  }`

const codeCss = css`
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
  }`

const latexCss = css`
  .katex-display {
      font-size: 1.25rem;
  }`

const mermaidCss = css`
  & .mermaid {
    text-align: center;
  }

  & .mermaid svg {
    max-width: 900px;
  }`

export const ShorthandMarkdown = styled(RenderedMarkdown)`
  padding: 1.5rem;
  font-family: palatino;

  // Core elements
  ${tableCss}
  ${quotesCss}
  ${linksCss}
  ${codeCss}

  // Plugins
  ${latexCss}
  ${mermaidCss}

  // Elements
  ${todosCss}
  ${questionsAnswersCss}
  ${definitionsCss}
  ${locationsCss}
  ${tagsCss}`
