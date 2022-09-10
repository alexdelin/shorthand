import { useState, useEffect, useRef } from 'react';
import { useQuery } from 'react-query';
import { useQueryClient } from 'react-query';
import { useSearchParams } from "react-router-dom";
import { useBeforeunload } from 'react-beforeunload';
import { ShorthandMarkdown } from './ViewPage.styles';
import { GetRenderedMarkdownResponse } from '../types/api';
import { ReactCodeMirrorRef } from '@uiw/react-codemirror';
import { markdown, markdownLanguage } from '@codemirror/lang-markdown';
import { languages } from '@codemirror/language-data';
import { EditorView, keymap } from "@codemirror/view";
import { selectSubwordBackward, selectSubwordForward
         } from '@codemirror/commands';
import { shorthandDark } from '../utils/codemirror-plugins/theme-shorthand-dark';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import { latexPlugin, locationPlugin, todoPlugin,
         timestampPlugin
         } from '../utils/codemirror-plugins';
import { ComposePageWrapper, ComposeHeader, ComposeNoteWrapper,
         ComposeEditorWrapper, ComposePreviewWrapper,
         StyledFormGroup, SwitchLabel, PreviewBottomMarker,
         StyledCodeMirror } from './ComposePage.styles';


export function ComposePage() {

  const [ searchParams ] = useSearchParams();
  const notePath = searchParams.get('path');
  const [editorText, setEditorText] = useState('');
  const [changesSaved, setChangesSaved] = useState(true);
  const [showPreview, setShowPreview] = useState(true);
  const [scrollPreview, setScrollPreview] = useState(true);
  const editorRef = useRef<ReactCodeMirrorRef>(null);

  const queryClient = useQueryClient();

  const {
    data: renderedMarkdown
  } = useQuery<GetRenderedMarkdownResponse, Error>('note-' + notePath, () =>
    fetch('http://localhost:8181/frontend-api/redered-markdown?path=' + notePath).then(res =>
      res.json()
    )
  )

  const {
    data: rawNote
  } = useQuery<string, Error>('raw-note-' + notePath, () =>
    fetch('http://localhost:8181/api/v1/note?path=' + notePath
    ).then(async res => {
      return res.text();
    }
    )
  )

  // Update the editor content exactly once when the page
  //   loads for the first time
  useEffect(() => {
    if (rawNote !== undefined && rawNote !== editorText) {
      setEditorText(rawNote);
    }
  // eslint-disable-next-line
  }, []);

  // Check if you leave the page with pending changes
  useBeforeunload((event) => {
    if (!changesSaved) {
      event.preventDefault();
    }
  });

  // TODO - Prevent navigation via react-router

  function saveNote() {

    if (!editorRef || !editorRef.current || !editorRef.current.view) {
      return false
    }

    fetch(
      'http://localhost:8181/api/v1/note?path=' + notePath,
      {
        method: 'POST',
        body: editorRef.current.view.state.doc.toString()
      }
    ).then(async res => {
      if (await res.text() === 'Note Updated') {
        queryClient.invalidateQueries(`note-${notePath}`);
        setChangesSaved(true);
      }
    })

    return false;
  }

  function handleEditorChange(value: string) {
    setEditorText(value);
    if (changesSaved) {
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

  if (renderedMarkdown === undefined) return <div>No note found</div>

  return (
    <ComposePageWrapper>
      <ComposeHeader>
        <StyledFormGroup row={true}>
          <SwitchLabel>Show Preview</SwitchLabel>
          <Switch
            checked={showPreview}
            onChange={handleShowPreviewChange}
          />
          <SwitchLabel>Auto-scroll Preview</SwitchLabel>
          <Switch
            checked={showPreview && scrollPreview}
            onChange={handleScrollPreviewChange}
            disabled={!showPreview}
          />
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
                  timestampPlugin
                ]
              }),
              EditorView.lineWrapping,
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
            ref={editorRef}
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
