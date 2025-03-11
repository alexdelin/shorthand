import { useState, useEffect, useRef, forwardRef } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { Link, useSearchParams } from "react-router-dom";
import { useBeforeunload } from 'react-beforeunload';
import { ShorthandMarkdown } from './ViewPage.styles';
import { GetRenderedMarkdownResponse } from '../types/api';
import { SuspenseFallback } from '../components/SuspenseFallback';
import { ReactCodeMirrorRef } from '@uiw/react-codemirror';
import { markdown, markdownLanguage } from '@codemirror/lang-markdown';
import { languages } from '@codemirror/language-data';
import { indentUnit } from '@codemirror/language'
import { EditorView, keymap } from "@codemirror/view";
import { selectSubwordBackward, selectSubwordForward
         } from '@codemirror/commands';
import { shorthandDark } from '../utils/codemirror-plugins/theme-shorthand-dark';
import Switch from '@mui/material/Switch';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Button from '@mui/material/Button';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import { latexPlugin, locationPlugin, todoPlugin,
         timestampPlugin, questionPlugin, definitionPlugin,
         todayPlaceholderPlugin
         } from '../utils/codemirror-plugins';
import { ComposePageWrapper, ComposeHeader, ComposeNoteWrapper,
         ComposeEditorWrapper, ComposePreviewWrapper,
         StyledFormGroup, SwitchLabel, PreviewBottomMarker,
         StyledCodeMirror } from './ComposePage.styles';

const FILE_NAME_LENGTH_LIMIT = 15;

// Boilerpalte from: https://mui.com/material-ui/react-snackbar/
const Alert = forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref,
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export function ComposePage() {
  console.log('rendering...')

  const [ searchParams, setSearchParams ] = useSearchParams();
  const notePath = searchParams.get('path');
  const [editorText, setEditorText] = useState('');
  const [changesSaved, setChangesSaved] = useState(true);
  const [showPreview, setShowPreview] = useState(false);
  const [scrollPreview, setScrollPreview] = useState(true);
  const [selectedTab, setSelectedTab] = useState(notePath);
  const editorRef = useRef<ReactCodeMirrorRef>(null);
  const [saveSnackbarOpen, setSaveSnackbarOpen] = useState(false);
  const [noChagesSnackbarOpen, setNoChangesSnackbarOpen] = useState(false);

  const queryClient = useQueryClient();

  const { data: renderedMarkdown } =
    useQuery<GetRenderedMarkdownResponse, Error>(['note', { path: notePath }], () => {
      if (!notePath) return {file_content:'', toc_content: ''};
      return fetch('/frontend-api/rendered-markdown?path=' + notePath)
        .then(async res => res.json())},
      {cacheTime: 10 * 60 * 1000, refetchOnWindowFocus: false}
    )

  const { data: rawNote } =
    useQuery<string, Error>(['raw-note', { path: notePath }], () => {
      if (!notePath) return '';
      return fetch('/api/v1/note?path=' + notePath)
        .then(async res => res.text())},
      {cacheTime: 10 * 60 * 1000, refetchOnWindowFocus: false}
    )

  const { data: openFiles } =
    useQuery<string[], Error>(['open-files'], () =>
      fetch('/frontend-api/get-open-files')
        .then(async res => res.json()),
      {cacheTime: 10 * 60 * 1000, refetchOnWindowFocus: false}
    )

  // Handle the file in the URL path param not being an open file
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
        setSelectedTab(targetFile);
        setSearchParams({path: targetFile});
      }
    }
  // eslint-disable-next-line
  }, [openFiles])

  // Update the editor content exactly once when the page
  //   loads for the first time, or you change to a different note
  useEffect(() => {
    if (rawNote !== undefined && rawNote !== editorText) {
      setSelectedTab(notePath);
      setEditorText(rawNote);
      setChangesSaved(true);
    }
  // eslint-disable-next-line
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
        console.log('Updating editor content');
        setEditorText(stampedNoteContent);
      }

      fetch(
        '/api/v1/note?path=' + notePath,
        {
          method: 'POST',
          body: stampedNoteContent
        }
      ).then(async res => {
        if (await res.text() === 'ack') {
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

  function handleEditorScroll() {

    if (showPreview && scrollPreview) {
      const cm = editorRef.current;

      if (cm === null || !cm.view || !cm.editor) {
        return
      }

      // Getting first and last visible lines
      // https://discuss.codemirror.net/t/how-to-get-currently-visible-line-s/4807/5
      const rect = cm.editor.getBoundingClientRect();
      const topVisibleLineBlock = cm.view.lineBlockAtHeight(rect.top - cm.view.documentTop);
      const bottomVisibleLineBlock = cm.view.lineBlockAtHeight(rect.bottom - cm.view.documentTop);

      const topLine = cm.view.state.doc.lineAt(topVisibleLineBlock.from).number
      const bottomLine = cm.view.state.doc.lineAt(bottomVisibleLineBlock.from).number
      const lastLine = cm.view.state.doc.lines;

      if (bottomLine === lastLine) {
        // special case for scrolling to the bottom of the preview
        //   if the last line of source is visible
        const anchor = document.getElementById('preview-bottom-marker');
        if (anchor) {
            anchor.scrollIntoView({ behavior: "smooth" });
        }
      } else {
        const lineNumberAnchor = `line-number-${topLine}`;
        const anchor = document.getElementById(lineNumberAnchor);
        if (anchor) {
            anchor.scrollIntoView({ behavior: "smooth" });
        }
      }
    }
  }

  const handleShowPreviewChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setShowPreview(event.target.checked);
  };

  const handleScrollPreviewChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setScrollPreview(event.target.checked);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    if (changesSaved) {
      setSelectedTab(newValue);
      setSearchParams({path: newValue});
    } else {
      alert('Please save changes before switching notes');
    }
  };

  function handleCloseTabClick(file: string, event: React.MouseEvent<HTMLSpanElement, MouseEvent>) {
    // Prevent handleTabChange from being called after this
    event.stopPropagation();
    event.preventDefault();

    // Special handling for closing the currently open file
    if (notePath === file) {
      if (changesSaved) {
        if (openFiles === undefined) {
          console.log('Cannot close file because openFiles is undefined');
          return;
        }
        if (openFiles && openFiles.length === 1) {
          console.log('Cannot close the only open file');
          return;
        }
        const openTabIndex = openFiles.indexOf(file);
        const newOpenTabIndex = openTabIndex - 1 >= 0 ? openTabIndex - 1 : openTabIndex + 1;
        const newOpenTab = openFiles[newOpenTabIndex];
        setSelectedTab(newOpenTab);
        setSearchParams({path: newOpenTab});
      } else {
        alert('Please save changes before closing');
        return;
      }
    }

    // Close file via the API
    fetch(
      '/frontend-api/close-file?path=' + file,
      {
        method: 'POST'
      }
    ).then(async res => {
      if (await res.text() === 'ack') {
        // Refresh list of tabs
        queryClient.invalidateQueries(['open-files']);
      }
    })
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

  if (renderedMarkdown === undefined) return <div>No note found</div>;

  if ((!selectedTab) || (openFiles && selectedTab && !openFiles.includes(selectedTab))) return <SuspenseFallback />;

  return (
    <ComposePageWrapper>
      <ComposeHeader>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          {openFiles && openFiles.map((file) => {
            if (file !== null) {
              const splitPath = file.split('/');
              const fullFileName = splitPath[splitPath.length -1];
              const trimmedFileName = fullFileName.length > FILE_NAME_LENGTH_LIMIT ? fullFileName.slice(0, 15) + '...' : fullFileName;
              return (
                <Tab
                  key={file}
                  value={file}
                  label={
                    <span title={fullFileName}>{trimmedFileName}
                      <span
                        onClick={(e) => {
                          handleCloseTabClick(file, e);
                        }}
                      > <i className="bi bi-x-circle-fill"></i> </span>
                    </span>}
                />);
            } else {
              return false;
            }
          })}
        </Tabs>
        <StyledFormGroup row={true}>
          <Button
            variant="text"
            onClick={saveNote}
          >
            <i style={{marginRight: '0.3rem'}} className='bi bi-floppy'></i>
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

          <SwitchLabel>Show Preview</SwitchLabel>
          <Switch
            checked={showPreview}
            onChange={handleShowPreviewChange}
          />

          <SwitchLabel>Auto-scroll</SwitchLabel>
          <Switch
            checked={showPreview && scrollPreview}
            onChange={handleScrollPreviewChange}
            disabled={!showPreview}
          />

          { changesSaved ?
            <>
              <Link to={`/view?path=${notePath}`} >
                <Button variant="text">
                  <i style={{marginRight: '0.3rem'}} className='bi bi-file-earmark-richtext'></i>
                  View
                </Button>
              </Link>
              <Link to={`/history?path=${notePath}`}>
                <Button variant="text">
                  <i style={{marginRight: '0.3rem'}} className='bi bi-clock-history'></i>
                  History
                </Button>
              </Link>
            </> : <>
              <Button variant="text" onClick={() => alert('Save changes before navigating')}>
                <i style={{marginRight: '0.3rem'}} className='bi bi-file-earmark-richtext'></i>
                View
              </Button>
              <Button variant="text" onClick={() => alert('Save changes before navigating')}>
                <i style={{marginRight: '0.3rem'}} className='bi bi-clock-history'></i>
                History
              </Button>
            </>
          }

        </StyledFormGroup>
      </ComposeHeader>
      <ComposeNoteWrapper>
        <ComposeEditorWrapper showPreview={showPreview}>
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
            onScrollCapture={handleEditorScroll}
            onChange={handleEditorChange}
            ref={editorRef}
            tabIndex={4}
          />
        </ComposeEditorWrapper>
        {showPreview &&
          <ComposePreviewWrapper>
            <ShorthandMarkdown source={renderedMarkdown.file_content} />
            <PreviewBottomMarker id="preview-bottom-marker" />
          </ComposePreviewWrapper>
        }
      </ComposeNoteWrapper>
    </ComposePageWrapper>
  )
}
