import styled from 'styled-components';
import { FileTree } from '../components/FileTree';


const TreeWrapper = styled.div`
  background-color: rgb(33, 37, 61);
  color: white;
  width: min(35rem, 100vw);
  height: 100%;
  overflow: scroll;
  line-height: 2rem;

  & i {
    color: white;
  }`


export function MobileNotesPage() {
  return (
  <TreeWrapper>
    <FileTree collapseFunction={()=>{}} />
  </TreeWrapper>
  )
}
