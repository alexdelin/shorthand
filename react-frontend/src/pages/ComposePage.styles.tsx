import styled from 'styled-components';
import CodeMirror from '@uiw/react-codemirror';
import FormGroup from '@mui/material/FormGroup';


export const ComposePageWrapper = styled.div`
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;`

export const ComposeHeader = styled.div`
  width: 100%;
  height: 3rem;
  display: flex;
  flex-direction: row;
  border-bottom: 1px solid black;
  justify-content: space-between;`

export const ComposeNoteWrapper = styled.div`
  width: 100%;
  height: calc(100vh - 3rem);
  display: flex;`

interface ComposeEditorWrapperProps {
  showPreview: boolean
};

export const ComposeEditorWrapper = styled.div`
  width: ${(props: ComposeEditorWrapperProps) => (props.showPreview ? '50%' : '100%')};
  height: 100%;
  display: flex;`

export const ComposePreviewWrapper = styled.div`
  width: 50%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: scroll;
  border-left: 1px solid black;`

export const StyledFormGroup = styled(FormGroup)`
  align-items: center;
  height: 3rem;
  min-width: 37rem;
  justify-content: end;`

export const SwitchLabel = styled.span`
  margin-left: 1rem;`

export const PreviewBottomMarker = styled.div`
  width: 100%;
  height: 0px;`

export const StyledCodeMirror = styled(CodeMirror)`
  & .cm-content {
    font-family: iosevka;
  }`
