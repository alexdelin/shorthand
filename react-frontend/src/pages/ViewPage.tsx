import { useSearchParams } from "react-router-dom";
import { useQuery } from 'react-query';
import { Fragment, useLayoutEffect, useMemo } from 'react';
import 'highlight.js/styles/atom-one-light.css';
import { ShorthandMarkdown } from './ViewPage.styles';
import MarkdownIt from 'markdown-it';
import tm from 'markdown-it-texmath';
import mermaid from 'mermaid';
import { mermaidPlugin, highlighter as hljs } from '../utils/markdown';


type GetRenderedMarkdownResponse = {
  file_content: string,
  toc_content: string
}

export function ViewPage() {

  const [ searchParams ] = useSearchParams();
  const notePath = searchParams.get('path');

  const writer = useMemo(() => {
    return MarkdownIt({
      html:true,
      highlight: function (str, lang) {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return hljs.highlight(str, { language: lang }).value;
          } catch (__) {}
        }

        return ''; // use external default escaping
      }
    }).use(tm,{delimiters:'dollars',macros:{"\\RR": "\\mathbb{R}"}
    }).use(mermaidPlugin);
  }, [])

  // Initialize once on page load
  useLayoutEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
    });
  }, []);

  const {
    data: noteContent
  } = useQuery<GetRenderedMarkdownResponse, Error>('note-' + notePath, () =>
    fetch('http://localhost:8181/frontend-api/redered-markdown?path=' + notePath).then(res =>
      res.json()
    )
  )

  useLayoutEffect(() => {
    mermaid.contentLoaded();
    // console.log(writer)
  });

  if (noteContent === undefined) return <div>No note found</div>

  return (
    <Fragment>
      <h2>Viewing Note: {notePath}</h2>
      <ShorthandMarkdown
        source={noteContent.file_content}
        writer={writer}
      />
    </Fragment>
  )
}

type RenderMarkdownProps = {
  source: string,
  writer: MarkdownIt,
  className?: string
}

export function RenderedMarkdown(props: RenderMarkdownProps) {
  return <div className={props.className} dangerouslySetInnerHTML={{__html: props.writer.render(props.source)}} />
}
