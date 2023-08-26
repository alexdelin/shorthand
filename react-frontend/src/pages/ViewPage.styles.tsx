import styled, { css } from 'styled-components';
import { RenderedMarkdown } from './ViewPage';


export const ViewNoteWrapper = styled.div``

export const ViewNoteHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 3rem;`

export const NoteTitle = styled.h2`
  margin-right: auto;
  margin-left: 1.5rem;
  break-word: anywhere;`

export const NotePath = styled.div`
  margin-left: 1rem;
  padding-right: 1rem;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  direction: rtl;
  text-align: left;`

export const ShorthandTOC = styled(RenderedMarkdown)`
  margin: 1.5rem;
  font-family: palatino;
  font-size: 1.2rem;

  & a {
    text-decoration: none;
    color: black
  }

  & ul {
    list-style-type: decimal;
  }`

const todosCss = css`
  & .todo-element {
    display: flex;
    align-items: center;
    padding: 0.4rem;
    padding-top: 0.5rem;
    margin: 0.5rem 0rem;
    border: 1px solid black;
    border-radius: 0.5rem;
  }

  & .todo-icon {
    margin-right: 0.5rem;
  }

  & .todo-incomplete {
    background-color: rgb(252, 238, 221);
    color: rgb(138, 86, 3);
    border-color: rgb(189, 122, 16);
  }

  & .todo-incomplete .todo-icon {
    color: rgb(189, 122, 16);
  }

  & .todo-complete {
    background-color: rgb(222, 243, 255);
    color: rgb(8, 105, 160);
    border-color: rgb(8, 105, 160);
  }

  & .todo-complete .todo-icon {
    color: rgb(8, 105, 160);
  }

  & .todo-skipped {
    background-color: #dfdfdf;
    color: rgb(68, 68, 68);
    border-color: rgb(68, 68, 68);
  }

  & .todo-skipped .todo-icon {
    color: rgb(68, 68, 68);
  }

  & .todo-timestamp {
    margin-left: auto;
    display: flex;
    white-space: pre;
  }

  & .todo-timestamp i {
    padding-top: 0.1rem;
    margin-left: 0.2rem;
    margin-right: 0.1rem;
  }

  & .todo-start-date, & .todo-end-date {
    margin-left: 0.15rem;
    padding: 0.25em 0.4em;
    padding-top: 0.3rem;
    font-size: 75%;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    border-radius: 0.25rem;
    color: #6c757d;
    background-color: #fff;
  }`

const questionsAnswersCss = css`
  & .qa-element {
    display: flex;
    align-items: center;
    padding: 0.4rem;
    padding-top: 0.5rem;
    border: 1px solid black;
    border-radius: 0.5rem;
    margin: 0.5rem 0rem;
  }

  & .qa-icon {
    margin-right: 0.5rem;
  }

  & .qa-question {
    background-color: #f5d6fb;
    color: rgb(102, 2, 121);
    border-color: rgb(152, 15, 179);
  }

  & .qa-question .qa-icon {
    color: rgb(152, 15, 179);
  }

  & .qa-answer {
    background-color: #d4ffce;
    color: rgb(11, 77, 2);
    border-color: rgb(23, 143, 7);
  }

  & .qa-answer .qa-icon {
    color: rgb(23, 143, 7);
  }

  & .question-meta {
    text-align: right;
  }

  & .qa-timestamp {
    margin-left: auto;
    display: flex;
    white-space: pre;
    flex-direction: column;
    justify-content: center;
  }

  & .qa-create-date {
    margin-left: 0.15rem;
    padding: 0.25em 0.4em;
    padding-top: 0.3rem;
    font-size: 75%;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    border-radius: 0.25rem;
    color: #6c757d;
    background-color: #fff;
  }`

const definitionsCss = css`
  & .definition-element {
    display: flex;
    margin: 0.5rem 0rem;
    border: 1px solid rgb(85, 2, 2);
    border-radius: 0.5rem;
  }

  & .definition-term {
    background-color: rgb(255, 228, 228);
    color: rgb(85, 2, 2);
    padding: 0.4rem;
    padding-top: 0.5rem;
    border-radius: 0.5rem 0 0 0.5rem;
  }

  & .definition-text {
    background-color: #feffc7;
    color: rgb(86, 87, 7);
    flex-grow: 1;
    padding: 0.4rem;
    padding-top: 0.5rem;
    border-radius: 0 0.5rem 0.5rem 0;
  }`

const tableCss = css`
  & table:not(.gridjs-table) {
    width: 100%;
    margin-bottom: 1rem;
    color: #212529;
    border-collapse: collapse;
  }

  & table:not(.gridjs-table) thead {
    display: table-header-group;
    vertical-align: middle;
    border-color: inherit;
  }

  & table:not(.gridjs-table) th {
    color: #fff;
    background-color: #343a40;
    border-color: #454d55;
    vertical-align: bottom;
    border-bottom: 2px solid #dee2e6;
    padding: 0.3rem;
    text-align: inherit;
    font-weight: bold;
  }

  & table:not(.gridjs-table) td {
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
    vertical-align: middle;
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
    white-space: pre-wrap;
  }`

const latexCss = css`
  .katex-display {
      font-size: 1.25rem;
      overflow-y: hidden;
      overflow-x: scroll;
  }`

const mermaidCss = css`
  & .mermaid {
    text-align: center;
  }

  & .mermaid svg {
    max-width: 900px;
  }`

const recordSetCss = css`
  & .record-set {
    margin-right: 3px;
  }

  .record-set .record-set-data {
    display: none;
  }

  .record-set .record-set-columns {
    display: none;
  }

  table.gridjs-table {
    width: 100%;
  }`

export const ShorthandMarkdown = styled(RenderedMarkdown)`
  margin: 1.5rem;
  font-family: palatino;
  overflow-x: hidden;

  & img {
    width: 100%;
  }

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
  ${tagsCss}
  ${recordSetCss}`
