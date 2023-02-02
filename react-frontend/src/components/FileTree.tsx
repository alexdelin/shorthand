import styled from 'styled-components';
import { useQuery } from 'react-query';
import { ANIMATION_LENGTH_MS } from './Nav.styles';


const DirectoryWrapper = styled.div`
  padding-left: 1rem;
  font-size: 1.25rem;
  margin: 0.2rem;`
const FileWrapper = styled.div`
  padding-left: 1rem;
  font-size: 1.25rem;
  margin: 0.2rem;`
const FileTreeIcon = styled.i`
  margin-right: 0.2rem;`


type TOC = {
  files: string[],
  dirs: TOC[],
  path: string,
  text: string
};

function renderDirectory(directory: TOC) {
  return (
  <DirectoryWrapper>
    <FileTreeIcon className="bi bi-folder2"></FileTreeIcon>{directory.text}
    {directory.files.map(file =>
      <FileWrapper><FileTreeIcon className="bi bi-file-earmark-text"></FileTreeIcon>{file}</FileWrapper>
    )}
    {directory.dirs.map(dir => renderDirectory(dir))}
  </DirectoryWrapper>)
}

export function FileTree() {

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

  return renderDirectory(fileTreeData)
}
