import styled from 'styled-components';
import { useQuery } from 'react-query';
import { Link } from "react-router-dom";
import { ANIMATION_LENGTH_MS } from './Nav.styles';


const DirectoryWrapper = styled.div`
  padding-left: 1rem;
  font-size: 1.25rem;
  margin: 0.25rem;
  width: 35rem;`
const DirectoryNameWrapper = styled.div``
const DirectoryContentsWrapper = styled.div`
  overflow: hidden;
  display: flex;
  flex-direction: column;
  // height: auto;
  transition: height ${ANIMATION_LENGTH_MS}ms;

  & .collapsed {
    height: 0rem;
  }`
const FileWrapper = styled(Link)`
  padding-left: 1rem;
  font-size: 1.25rem;
  margin: 0.2rem;
  text-decoration: none;
  color: white;`
const FileTreeIcon = styled.i`
  margin-right: 0.2rem;`


type TOC = {
  files: string[],
  dirs: TOC[],
  path: string,
  text: string
};

function handleDirectoryClick(e: any) { // React.MouseEvent<HTMLDivElement, MouseEvent>) {
  // This is a hack, but there is no easier way to do it via common react patterns
  e.currentTarget.parentElement.childNodes[1].classList.toggle('collapsed')
}

function renderDirectory(directory: TOC, expanded: boolean, collapseFunction: any) {
  return (
  <DirectoryWrapper>
    <DirectoryNameWrapper onClick={handleDirectoryClick}>
      <FileTreeIcon className="bi bi-folder2"></FileTreeIcon>{directory.text}
    </DirectoryNameWrapper>
    <DirectoryContentsWrapper className={expanded ? '' : 'collapsed'}>
      {directory.files.map(file =>
        <FileWrapper to={`/compose?path=${directory.path}/${file}`}>
          <FileTreeIcon className="bi bi-file-earmark-text"></FileTreeIcon>{file}
        </FileWrapper>
      )}
      {directory.dirs.map(dir => renderDirectory(dir, false, collapseFunction))}
    </DirectoryContentsWrapper>
  </DirectoryWrapper>)
}

export function FileTree(collapseFunction: any) {

  const {
    data: fileTreeData
  } = useQuery<TOC, Error>(
    ['toc'], () =>

    // TODO - Replace with a better library
    fetch(`http://localhost:8181/api/v1/toc`).then(res =>
      res.json()
    )
  )

  if (fileTreeData === undefined) return <div>Loading...</div>

  return renderDirectory(fileTreeData, true, collapseFunction)
}
