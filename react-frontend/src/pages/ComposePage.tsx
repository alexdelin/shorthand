import { useState, useEffect, useRef } from 'react';
import { useQuery } from 'react-query';
import { useQueryClient } from 'react-query';
import { useSearchParams } from "react-router-dom";
import { useBeforeunload } from 'react-beforeunload';
import styled from 'styled-components';
import { ShorthandMarkdown } from './ViewPage.styles';
import { GetRenderedMarkdownResponse } from '../types/api';
import AceEditor, { IEditorProps } from "react-ace";
import { Ace } from "ace-builds";
import "ace-builds/src-noconflict/mode-markdown";
// import "../utils/ace-plugins/mode-shorthand";
import "../utils/ace-plugins/theme-shorthand-light";
import "ace-builds/src-noconflict/ext-language_tools";
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';


const ComposePageWrapper = styled.div`
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;`

const ComposeHeader = styled.div`
  width: 100%;
  height: 3rem;
  border-bottom: 1px solid black;`

const ComposeNoteWrapper = styled.div`
  width: 100%;
  height: calc(100vh - 3rem);
  display: flex;`

interface ComposeEditorWrapperProps {
  showPreview: boolean
};

const ComposeEditorWrapper = styled.div`
  width: ${(props: ComposeEditorWrapperProps) => (props.showPreview ? '50%' : '100%')};
  height: 100%;
  display: flex;`

const ComposePreviewWrapper = styled.div`
  width: 50%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: scroll;
  border-left: 1px solid black;`

const StyledFormGroup = styled(FormGroup)`
  justify-content: flex-end;
  align-items: center;
  height: 3rem;`

const SwitchLabel = styled.span`
  margin-left: 1rem;`

const PreviewBottomMarker = styled.div`
  width: 100%;
  height: 0px;`


export function ComposePage() {

  const [ searchParams ] = useSearchParams();
  const notePath = searchParams.get('path');
  const [editorText, setEditorText] = useState('');
  const [changesSaved, setChangesSaved] = useState(true);
  const [showPreview, setShowPreview] = useState(true);
  const [scrollPreview, setScrollPreview] = useState(true);
  const aceEl = useRef<AceEditor>(null);

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

  // Have the Ace window resize when the preview is
  //   hidden / shown
  useEffect(() => {
    if (aceEl.current !== null) {
      aceEl.current.editor.resize();
    }
  }, [showPreview]);

  // Check if you leave the page with pending changes
  useBeforeunload((event) => {
    if (!changesSaved) {
      event.preventDefault();
    }
  });

  // TODO - Prevent navigation via react-router

  function saveNote(editor: Ace.Editor) {
    fetch(
      'http://localhost:8181/api/v1/note?path=' + notePath,
      {
        method: 'POST',
        body: editor.getValue()
      }
    ).then(async res => {
      if (await res.text() === 'Note Updated') {
        queryClient.invalidateQueries(`note-${notePath}`);
        setChangesSaved(true);
        // const undoMgr = editor.session.getUndoManager() as any;
        // undoMgr.markClean();
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

  function handleEditorScroll(editor: IEditorProps) {
    if (showPreview && scrollPreview) {
      if (editor.renderer.layerConfig.lastRow === editor.env.document.getLength() - 1) {
        // special case for scrolling to the bottom of the preview
        //   if the last line of source is visible
        console.log('last row visible!');
        const anchor = document.getElementById('preview-bottom-marker');
        if (anchor) {
            anchor.scrollIntoView({ behavior: "smooth" });
        }
      } else {
        const firstVisibleLine = editor.renderer.layerConfig.firstRow + 1;
        const lineNumberAnchor = `line-number-${firstVisibleLine}`;
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
          <AceEditor
            ref={aceEl}
            commands={[
              {
                name: "saveNote",
                bindKey: { win: "Ctrl-S", mac: "Command-S" },
                exec: function (editor) {
                    saveNote(editor);
                }
              },
              // TODO- Write a command to show the file finder modal
            ]}
            style={{"fontFamily": "iosevka"}}
            height="100%"
            width="100%"
            mode="shorthand"
            value={editorText}
            theme="shorthand-light"
            wrapEnabled={true}
            onChange={(value)=> handleEditorChange(value)}
            onScroll={(editor) => {handleEditorScroll(editor)}}
            fontSize={16}
            name="shorthand-compose-editor"
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
