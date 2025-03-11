import { Link, useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from 'react-query';
import React, { useLayoutEffect, useState, Suspense, useRef, useEffect } from 'react';
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
import ReactToPrint from 'react-to-print';
import { LinksGraph } from '../components/LinksGraph';
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
  html: true,
  linkify: true,
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

// Remember old renderer, if overridden, or proxy to default renderer
var defaultRender = writer.renderer.rules.link_open || function(tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options);
};

writer.renderer.rules.link_open = function (tokens: any, idx, options, env, self) {
  // If you are sure other plugins can't add `target` - drop check below
  var aIndex = tokens[idx].attrIndex('target');

  if (aIndex < 0) {
    tokens[idx].attrPush(['target', '_blank']); // add new attribute
  } else {
    tokens[idx].attrs[aIndex][1] = '_blank';    // replace value of existing attr
  }

  // pass token to default renderer.
  return defaultRender(tokens, idx, options, env, self);
};

export default function ViewPage() {

  const [ searchParams, setSearchParams ] = useSearchParams();
  const notePath = searchParams.get('path');
  const [tocShown, setTocShown] = useState(false);
  const [linksShown, setLinksShown] = useState(false);
  const renderedMarkdownRef = useRef(null);

  const queryClient = useQueryClient();

  const { data: openFiles } =
    useQuery<string[], Error>(['open-files'], () =>
      fetch('/frontend-api/get-open-files')
        .then(async res => res.json()),
      {cacheTime: 10 * 60 * 1000, refetchOnWindowFocus: false}
    )

  const {
    data: noteContent
  } = useQuery<GetRenderedMarkdownResponse, Error>(['note', { path: notePath }], () =>
    fetch('/frontend-api/rendered-markdown?path=' + notePath).then(res =>
      res.json()
    )
  )

  // Handle the file in the URL path param not being open
  if (openFiles && notePath && !openFiles.includes(notePath)) {
    // Open the file in the URL path via the API
    fetch(
      '/frontend-api/open-file?path=' + notePath,
      { method: 'POST' }
    ).then(async res => {
      if (await res.text() === 'ack') {
        queryClient.invalidateQueries(['open-files']);
      }
    })
  }

  // Handle having no URL path param
  useEffect(() => {
    if (!notePath) {
      if (openFiles && openFiles.length) {
        console.log('Setting Open File');
        const targetFile = openFiles[openFiles.length - 1];
        setSearchParams({path: targetFile});
      }
    }
  // eslint-disable-next-line
  }, [openFiles])

  // Record a view for the file being viewed
  useEffect(() => {
    fetch(
      '/api/v1/record_view?note_path=' + notePath,
      { method: 'POST' }
    )
  }, [notePath])

  function handleTOCClick() {
    setTocShown(!tocShown);
  }

  function handleLinksClick() {
    setLinksShown(!linksShown);
  }

  if (!notePath || !noteContent) return <div>No note found</div>

  return (
    <ViewNoteWrapper id="ViewNoteWrapper">
      <ViewNoteHeader>
        <NoteTitle>Viewing Note: {notePath}</NoteTitle>
        <Button
          variant="text"
          onClick={handleTOCClick}
        >
          <i style={{marginRight: '0.3rem'}} className='bi bi-list-ol'></i>
          TOC
        </Button>
        <Button
          variant="text"
          onClick={handleLinksClick}
        >
          <i style={{marginRight: '0.3rem'}} className='bi bi-link-45deg'></i>
          Links
        </Button>
        <Link to={`/compose?path=${notePath}`}>
          <Button
            variant="text"
          >
            <i style={{marginRight: '0.3rem'}} className='bi bi-pencil'></i>
            Edit
          </Button>
        </Link>
        <Link to={`/history?path=${notePath}`}>
          <Button
            variant="text"
          >
            <i style={{marginRight: '0.3rem'}} className='bi bi-clock-history'></i>
            History
          </Button>
        </Link>
        <ReactToPrint
          documentTitle={notePath || 'Unknown Note'}
          trigger={() =>
            <Button
              variant="text"
              style={{marginRight: '1rem'}}
            >
              <i style={{marginRight: '0.3rem'}} className='bi bi-printer'></i>
              Print
            </Button>}
          content={() => renderedMarkdownRef.current}
        />
      </ViewNoteHeader>
      <hr style={{margin: '0'}} />
      {linksShown ? (
        <div>
          <h3 style={{marginLeft: '1.5rem'}}>Links</h3>
          <Suspense fallback={<div>Loading...</div>}>
            <LinksGraph notePath={notePath} />
          </Suspense>
          <hr />
        </div>
      ) : null}
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
        ref={renderedMarkdownRef}
      />
    </ViewNoteWrapper>
  )
}

type RenderMarkdownProps = {
  source: string,
  className?: string
}

export const RenderedMarkdown = React.forwardRef((props: RenderMarkdownProps, ref: React.ForwardedRef<HTMLDivElement>) => {

  const [hasScrolled, setHasScrolled] = useState(false);

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
          // enabled: true,
          limit: 50
        }
      }).render(displayEl);
    }

    // Initialize Locations
    // TODO - Add popover modal for each location
    // for (const locationEl of document.querySelectorAll('location')) {
    // }

    // Ensure we only scroll to the target id once
    if (props.source !== undefined && !hasScrolled) {
      setTimeout(() => {
        scrollToAnchor();
        setHasScrolled(true);
      }, 500)
    }
  }, [props.source, hasScrolled]);

  return <div ref={ref} className={props.className} dangerouslySetInnerHTML={{__html: writer.render(props.source ? props.source : '')}} />
})
