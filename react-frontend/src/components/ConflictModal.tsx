import { Button } from '@mui/material';
import styled from 'styled-components';
import hljs from 'highlight.js/lib/core';
import hljsDiff from 'highlight.js/lib/languages/diff';
import 'highlight.js/styles/atom-one-light.css';
import { ReactCodeMirrorRef } from '@uiw/react-codemirror';

hljs.registerLanguage('diff', hljsDiff);

interface ConflictModalOverlayProps {
  visible: boolean
}

export const ConflictModalOverlay = styled.div`
  z-index: 11;
  position: absolute;
  margin-top: 3rem;
  height: calc(100vh - 3rem);
  width: 100%;
  background-color: #99999980;
  display: ${(props: ConflictModalOverlayProps) => (props.visible ? 'flex' : 'none')};
  justify-content: center;
  align-items: center;`

export const ConflictModalBody = styled.div`
  width: 50%;
  max-height: calc(100vh - 7rem);
  background-color: white;
  border: 1px solid #333;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  overflow: scroll;`

export const DiffPreview = styled.pre`
  background-color: #eee;
  border: 1px solid black;
  padding: 2rem;
  width: 80%;
`

export const ButtonGroup = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
  justify-content: space-evenly;
  margin-top: 2rem;
`

interface ConflictModalProps {
  visible: boolean,
  diff: string,
  hide: Function,
  saveFunction: (force: boolean) => boolean
}


export function ConflictModal(props: ConflictModalProps) {

  function doForceUpdate() {
    return props.saveFunction(true);
  }

  return (
    <ConflictModalOverlay visible={props.visible}>
      <ConflictModalBody>
        <h2><i style={{ color: 'orange', marginRight: '0.5rem' }} className='bi bi-exclamation-triangle'></i>Failed to Update Note</h2>
        The changes made could not be saved because the note has already been updated since it was opened for editing.
        <br />
        Forcing the update through will make the changes shown below:
        <DiffPreview>
          <code dangerouslySetInnerHTML={{__html: hljs.highlight(props.diff, { language: 'diff' }).value}} />
        </DiffPreview>
        To force this update to be made, click Force Update below.
        <ButtonGroup>
          <Button variant='outlined' color='info' onClick={() => {props.hide()}}>Continue Editing</Button>
          <Button variant='contained' color='error' onClick={() => {doForceUpdate()}}>Force Update</Button>
        </ButtonGroup>
      </ConflictModalBody>
    </ConflictModalOverlay>
  )
}

