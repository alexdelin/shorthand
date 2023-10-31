import Button from '@mui/material/Button';
import "gridjs/dist/theme/mermaid.css";
import 'highlight.js/styles/atom-one-light.css';
import 'katex/dist/katex.min.css';
import { Suspense, useRef, useState, useEffect } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { useSearchParams } from "react-router-dom";
import { LinksGraph } from '../components/LinksGraph';
import {
    NotePath, ShorthandMarkdown,
    ShorthandTOC, ViewNoteHeader, ViewNoteWrapper
} from '../pages/ViewPage.styles';
import { GetRenderedMarkdownResponse } from '../types/api';


export function MobileViewPage() {

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
    fetch('/frontend-api/redered-markdown?path=' + notePath).then(res =>
      res.json()
    )
  )

  // Handle the file in the URL path param not being the
  // most recently opened file
  if (openFiles && notePath &&
      openFiles[openFiles.length - 1] !== notePath) {
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

  function handleTOCClick() {
    setTocShown(!tocShown);
  }

  function handleLinksClick() {
    setLinksShown(!linksShown);
  }

  if (!noteContent || !notePath) return <div>No note found</div>

  return (
    <ViewNoteWrapper id="ViewNoteWrapper">
      <ViewNoteHeader>
        {/*
        `&lrm;` needed here to make the left-side ellipsis work
        with a leading character of `/`. See https://stackoverflow.com/a/27961022
        */}
        <NotePath>&lrm;{notePath}</NotePath>
        <div style={{display: 'flex'}}>
          <Button
            variant="text"
            onClick={handleTOCClick}
          >
            TOC
          </Button>
          <Button
            variant="text"
            onClick={handleLinksClick}
          >
            Links
          </Button>
        </div>
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
