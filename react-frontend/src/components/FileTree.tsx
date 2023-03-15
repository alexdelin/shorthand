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
  flex-wrap: nowrap;
  // max-height: 1000rem;
  // transition: max-height ${ANIMATION_LENGTH_MS}ms;

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

type FileTreeProps = {
  collapseFunction: () => void
}


function handleDirectoryClick(e: React.MouseEvent<HTMLDivElement, MouseEvent>) {
  // This is a hack, but there is no easier way to do it via common react patterns
  const directoryWrapperEl = e.currentTarget.parentElement;
  const directoryContentsNode = directoryWrapperEl?.childNodes[1] as HTMLDivElement | undefined;
  if (directoryContentsNode) {
    const classes = directoryContentsNode.classList;
    classes.toggle('collapsed');
  }
}

function renderDirectory(directory: TOC, expanded: boolean, collapseFunction: () => void) {
  return (
  <DirectoryWrapper key={directory.path}>
    <DirectoryNameWrapper onClick={handleDirectoryClick}>
      <FileTreeIcon className="bi bi-folder2"></FileTreeIcon>{directory.text}
    </DirectoryNameWrapper>
    <DirectoryContentsWrapper className={expanded ? '' : 'collapsed'}>
      {directory.files.map(file =>
        <FileWrapper
          key={`${directory.path}/${file}`}
          to={`/compose?path=${directory.path}/${file}`}
          onClick={collapseFunction}
        >
          <FileTreeIcon className="bi bi-file-earmark-text"></FileTreeIcon>{file}
        </FileWrapper>
      )}
      {directory.dirs.map(dir => renderDirectory(dir, false, collapseFunction))}
    </DirectoryContentsWrapper>
  </DirectoryWrapper>)
}


export function FileTree(props: FileTreeProps) {

  const {
    data: fileTreeData
  } = useQuery<TOC, Error>(
    ['toc'], () =>

    // TODO - Replace with a better library
    fetch(`/api/v1/toc`).then(res =>
      res.json()
    ),
    {cacheTime: 10 * 60 * 1000, refetchOnWindowFocus: false}
  )

  if (fileTreeData === undefined) return <div>Loading...</div>

  return renderDirectory(fileTreeData, true, props.collapseFunction)
}
