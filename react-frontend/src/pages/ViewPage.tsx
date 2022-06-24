import { useSearchParams } from "react-router-dom";
import { useQuery } from 'react-query';
import { useLayoutEffect, useState } from 'react';
import 'highlight.js/styles/atom-one-light.css';
import 'katex/dist/katex.min.css';
import "gridjs/dist/theme/mermaid.css";
import { ViewNoteWrapper, ShorthandMarkdown,
         ShorthandTOC, ViewNoteHeader, NoteTitle } from './ViewPage.styles';
import Button from '@mui/material/Button';
import MarkdownIt from 'markdown-it';
import tm from 'markdown-it-texmath';
import mermaid from 'mermaid';
import { mermaidPlugin, highlighter as hljs } from '../utils/markdown';
import { Grid } from "gridjs";
import { GetRenderedMarkdownResponse,
         RecordSetColumns,
         RecordSetJSON } from '../types/api';


function scrollToAnchor() {
  let currentLocation = window.location.href;
  const hasAnchor = currentLocation.includes("#");
  if (hasAnchor) {
    const anchorId = `${currentLocation.substring(currentLocation.indexOf("#") + 1)}`;
    const anchor = document.getElementById(anchorId);
    if(anchor){
        anchor.scrollIntoView({ behavior: "smooth" });
    }
  }
}

const writer = MarkdownIt({
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
// })

export default function ViewPage() {

  const [ searchParams ] = useSearchParams();
  const notePath = searchParams.get('path');
  const [hasScrolled, setHasScrolled] = useState(false);
  const [tocShown, setTocShown] = useState(false);
  const [linksShown, setLinksShown] = useState(false);

  const {
    data: noteContent
  } = useQuery<GetRenderedMarkdownResponse, Error>('note-' + notePath, () =>
    fetch('http://localhost:8181/frontend-api/redered-markdown?path=' + notePath).then(res =>
      res.json()
    )
  )

  // Called once on page load
  useLayoutEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
    });
  }, []);

  // Called whenever the note content changes
  useLayoutEffect(() => {
    mermaid.contentLoaded();

    /* It's bad to do this jQuery-style DOM modification in a react app
       but for now its much easier and more readable to do things this way
       as opposed to writing plugins for markdown-it
    */

    // Initialize Record Sets
    for (const tableEl of document.querySelectorAll('.record-set')) {

      const dataEl = tableEl.querySelector(":scope > .record-set-data") as HTMLElement;
      const columnsEl = tableEl.querySelector(":scope > .record-set-columns") as HTMLElement;
      const displayEl = tableEl.querySelector(":scope > .record-set-display");

      if (dataEl === null || displayEl === null) {
        continue
      }

      const columns = JSON.parse(columnsEl.innerText) as RecordSetColumns;

      const tableData = JSON.parse(dataEl.innerText) as RecordSetJSON;
      const parsedData = tableData.map((row) => {
        const flatRow: Array<string> = []
        for (const column of columns) {
          flatRow.push(row[column].join(', '));
        }
        return flatRow;
      })

      displayEl.replaceChildren();

      new Grid({
        columns: columns,
        data: parsedData,
        pagination: {
          enabled: true,
          limit: 50
        }
      }).render(displayEl);
    }

    // Ensure we only scroll to the target id once
    if (noteContent !== undefined && !hasScrolled) {
      setTimeout(() => {
        scrollToAnchor();
        setHasScrolled(true);
      }, 500)
    }
  }, [noteContent, hasScrolled]);

  function handleTOCClick() {
    setTocShown(!tocShown);
  }

  function handleLinksClick() {
    setLinksShown(!linksShown);
  }

  if (noteContent === undefined) return <div>No note found</div>

  return (
    <ViewNoteWrapper id="ViewNoteWrapper">
      <ViewNoteHeader>
        <NoteTitle>Viewing Note: {notePath}</NoteTitle>
        <Button
          variant="text"
          onClick={handleTOCClick}
        >TOC</Button>
        <Button
          variant="text"
          onClick={handleLinksClick}
        >Links</Button>
        <Button variant="text" style={{marginRight: '1rem'}}>Edit</Button>
      </ViewNoteHeader>
      <hr style={{margin: '0'}} />
      {tocShown ? (
        <div>
          <h3 style={{marginLeft: '1.5rem'}}>Table of Contents</h3>
          <ShorthandTOC
            source={noteContent.toc_content}
          />
          <hr />
        </div>
      ) : null}
      <ShorthandMarkdown
        source={noteContent.file_content}
      />
    </ViewNoteWrapper>
  )
}

type RenderMarkdownProps = {
  source: string,
  className?: string
}

export function RenderedMarkdown(props: RenderMarkdownProps) {
  return <div className={props.className} dangerouslySetInnerHTML={{__html: writer.render(props.source)}} />
}
