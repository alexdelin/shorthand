import styled from 'styled-components';
import { useState, useEffect, useRef, forwardRef } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { useSearchParams } from "react-router-dom";
import { ReactCodeMirrorRef } from '@uiw/react-codemirror';
import { useBeforeunload } from 'react-beforeunload';
import CodeMirror from '@uiw/react-codemirror';
import Button from '@mui/material/Button';
import Snackbar from '@mui/material/Snackbar';
import Switch from '@mui/material/Switch';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import FormGroup from '@mui/material/FormGroup';
import { markdown, markdownLanguage } from '@codemirror/lang-markdown';
import { languages } from '@codemirror/language-data';
import { indentUnit } from '@codemirror/language'
import { EditorView, keymap } from "@codemirror/view";
import { selectSubwordBackward, selectSubwordForward
         } from '@codemirror/commands';
import { shorthandDark } from '../utils/codemirror-plugins/theme-shorthand-dark';
import { latexPlugin, locationPlugin, todoPlugin,
         timestampPlugin, questionPlugin, definitionPlugin,
         todayPlaceholderPlugin
         } from '../utils/codemirror-plugins';


const ComposePageWrapper = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;`


const ComposeHeader = styled.div`
  width: 100%;
  height: 3rem;
  display: flex;
  flex-direction: row;
  border-bottom: 1px solid black;
  align-items: center;
  justify-content: space-between;`


const NotePath = styled.div`
  margin-left: 1rem;
  padding-right: 1rem;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  direction: rtl;
  text-align: left;`


const StyledFormGroup = styled(FormGroup)`
  align-items: center;
  height: 3rem;`


const ComposeNoteWrapper = styled.div`
  width: 100%;
  height: calc(100% - 3rem);
  display: flex;`


const StyledCodeMirror = styled(CodeMirror)`
  & .cm-content {
    font-family: iosevka;
  }`


// Boilerpalte from: https://mui.com/material-ui/react-snackbar/
const Alert = forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref,
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});


export function MobileComposePage() {

  const [ searchParams, setSearchParams ] = useSearchParams();
  const notePath = searchParams.get('path');

  const [editorText, setEditorText] = useState('');
  const [changesSaved, setChangesSaved] = useState(true);
  const [saveSnackbarOpen, setSaveSnackbarOpen] = useState(false);
  const [noChagesSnackbarOpen, setNoChangesSnackbarOpen] = useState(false);

  const editorRef = useRef<ReactCodeMirrorRef>(null);

  const queryClient = useQueryClient();

  const { data: rawNote } =
    useQuery<string, Error>(['raw-note', { path: notePath }], () =>
      fetch('/api/v1/note?path=' + notePath)
        .then(async res => res.text()),
      {cacheTime: 10 * 60 * 1000, refetchOnWindowFocus: false}
    )

  const { data: openFiles } =
    useQuery<string[], Error>(['open-files'], () =>
      fetch('/frontend-api/get-open-files')
        .then(async res => res.json()),
      {cacheTime: 10 * 60 * 1000, refetchOnWindowFocus: false}
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
  }, [openFiles])

  // Update the editor content exactly once when the page
  //   loads for the first time, or you change to a different note
  useEffect(() => {
    if (rawNote !== undefined && rawNote !== editorText) {
      setEditorText(rawNote);
      setChangesSaved(true);
    }
  }, [notePath, rawNote]);

  // Check if you leave the page with pending changes
  useBeforeunload((event) => {
    if (!changesSaved) {
      event.preventDefault();
    }
  });

  // TODO - Prevent navigation via react-router
  //        if there are unsaved changes

  function saveNote() {

    if (!editorRef || !editorRef.current || !editorRef.current.view) {
      return false
    }

    // Early exit for no changes
    if (changesSaved) {
      console.log('No changes, skipping save');
      showNoChangesSnackbar();
      return false;
    }

    const currentNoteContent = editorRef.current.view.state.doc.toString();
    const currentCursorPosition = editorRef.current?.view?.state.selection.ranges[0].from;
    let contentGetsStamped = false;

    fetch(
      '/api/v1/stamp/raw',
      {
        method: 'POST',
        body: currentNoteContent
      }
    ).then(async res => {

      const stampedNoteContent = await res.text();
      if (stampedNoteContent !== currentNoteContent) {
        contentGetsStamped = true;
        setEditorText(stampedNoteContent);
      }

      fetch(
        '/api/v1/note?path=' + notePath,
        {
          method: 'POST',
          body: stampedNoteContent
        }
      ).then(async res => {
        if (await res.text() === 'Note Updated') {
          queryClient.invalidateQueries(['note', { path: notePath }]);
          queryClient.invalidateQueries(['raw-note', { path: notePath }]);
          setChangesSaved(true);
          showSaveSnackbar();
          if (currentCursorPosition && contentGetsStamped) {
            console.log('setting cursor position to ' + currentCursorPosition);
            editorRef.current?.view?.dispatch({
              selection: {
                anchor: currentCursorPosition,
                head: currentCursorPosition,
              },
            });
          }
        }
      })

    })

    return false;
  }

  function handleEditorChange(value: string) {
    if (changesSaved && value !== rawNote) {
      setChangesSaved(false);
    }
  }

  const showSaveSnackbar = () => {
    setSaveSnackbarOpen(true);
  };

  const showNoChangesSnackbar = () => {
    setNoChangesSnackbarOpen(true);
  };

  const handleSaveSnackbarClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setSaveSnackbarOpen(false);
  };

  const handleNoChangesSnackbarClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setNoChangesSnackbarOpen(false);
  };

  return (
    <ComposePageWrapper>
      <ComposeHeader>
        {/*
        `&lrm;` needed here to make the left-side ellipsis work
        with a leading character of `/`. See https://stackoverflow.com/a/27961022
        */}
        <NotePath>&lrm;{notePath}</NotePath>
        <StyledFormGroup row={true}>
          <Button
            variant="text"
            onClick={saveNote}
          >
            Save
          </Button>
          <Snackbar
            open={saveSnackbarOpen}
            autoHideDuration={1000}
            onClose={handleSaveSnackbarClose}
            sx={{ marginTop: '2rem' }}
            anchorOrigin={{vertical: 'top', horizontal: 'right'}}
           >
            <Alert onClose={handleSaveSnackbarClose} severity="success" sx={{ width: '100%' }}>
              Note Updated
            </Alert>
          </Snackbar>
          <Snackbar
            open={noChagesSnackbarOpen}
            autoHideDuration={1000}
            onClose={handleNoChangesSnackbarClose}
            sx={{ marginTop: '2rem' }}
            anchorOrigin={{vertical: 'top', horizontal: 'right'}}
           >
            <Alert onClose={handleNoChangesSnackbarClose} severity="info" sx={{ width: '100%' }}>
              No Changes To Save
            </Alert>
          </Snackbar>
        </StyledFormGroup>
      </ComposeHeader>
      <ComposeNoteWrapper>
        <StyledCodeMirror
          value={editorText}
          height="100%"
          style={{fontSize: '18px', width: '100%'}}
          theme={shorthandDark}

          extensions={[
            markdown({
              base: markdownLanguage,
              codeLanguages: languages,
              extensions: [
                latexPlugin,
                locationPlugin,
                todoPlugin,
                timestampPlugin,
                questionPlugin,
                definitionPlugin,
                todayPlaceholderPlugin
              ]
            }),
            EditorView.lineWrapping,
            indentUnit.of('    '),
            keymap.of([
              {
                key: 'Mod-s',
                preventDefault: true,
                run: saveNote,
              },

              // TODO- These don't get picked up,
              //       so bump priority
              {
                mac: 'Ctrl-Shift-ArrowLeft',
                preventDefault: true,
                run: selectSubwordBackward,
              },
              {
                mac: 'Ctrl-Shift-ArrowRight',
                preventDefault: true,
                run: selectSubwordForward,
              },

              // TODO- Add this
              // {
              //   key: "Shift-Ctrl-Up",
              //   run: addCursorToPrevLine,
              // }, {
              //   key: "Shift-Ctrl-Down",
              //   run: addCursorToNextLine,
              // }

            ])
          ]}
          onChange={handleEditorChange}
          ref={editorRef}
          tabIndex={4}
        />
      </ComposeNoteWrapper>
    </ComposePageWrapper>
  )
}
