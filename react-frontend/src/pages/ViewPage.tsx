import { useSearchParams } from "react-router-dom";
import { useQuery } from 'react-query';
import { Fragment } from 'react';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm'
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/atom-one-light.css';
import { GetNoteResponse } from '../types';
import { StyledReactMarkdown } from './ViewPage.styles';


export function ViewPage() {

  const [ searchParams ] = useSearchParams();
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
