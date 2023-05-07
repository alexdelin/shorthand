import styled from 'styled-components';
import { Fragment, useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from "react-router-dom";
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
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

const CreateButtonWrapper = styled.div`
  padding-left: 1rem;
  font-size: 1.25rem;
  margin: 0.25rem;
  width: 35rem;`


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

function handleCreateClick(e: React.MouseEvent<HTMLDivElement, MouseEvent>) {
}

type RenderedDirectoryProps = {
  directory: TOC,
  expanded: boolean,
  collapseFunction: () => void,
  openCreateBackdrop: (parentDir: string) => void
}

function RenderedDirectory(props: RenderedDirectoryProps) {

  const handleCreateButtonClick = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    if (props.directory.path === '') {
      props.openCreateBackdrop('/');
    } else {
      props.openCreateBackdrop(props.directory.path);
    }
  }

  return (
  <DirectoryWrapper key={props.directory.path}>
    <DirectoryNameWrapper onClick={handleDirectoryClick}>
      <FileTreeIcon className="bi bi-folder2"></FileTreeIcon>{props.directory.text}
    </DirectoryNameWrapper>
    <DirectoryContentsWrapper className={props.expanded ? '' : 'collapsed'}>
      {props.directory.files.map(file =>
        <FileWrapper
          key={`${props.directory.path}/${file}`}
          to={`/compose?path=${props.directory.path}/${file}`}
          onClick={props.collapseFunction}
        >
          <FileTreeIcon className="bi bi-file-earmark-text"></FileTreeIcon>{file}
        </FileWrapper>
      )}
      {props.directory.dirs.map(dir =>
        <RenderedDirectory
          directory={dir}
          expanded={false}
          collapseFunction={props.collapseFunction}
          openCreateBackdrop={props.openCreateBackdrop}
        />
       )}
      <CreateButtonWrapper onClick={handleCreateButtonClick}>
        <FileTreeIcon className="bi bi-plus-circle-dotted"></FileTreeIcon>New
      </CreateButtonWrapper>
    </DirectoryContentsWrapper>
  </DirectoryWrapper>)
}


export function FileTree(props: FileTreeProps) {

  const [createBackdropOpen, setCreateBackdropOpen] = useState(false);
  const [createParentDir, setCreateParentDir] = useState('/');

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

  const closeCreateBackdrop = () => {
    setCreateBackdropOpen(false);
  };

  const openCreateBackdrop = (parentDir: string) => {
    setCreateParentDir(parentDir);
    setCreateBackdropOpen(true);
  };

  if (fileTreeData === undefined) return <div>Loading...</div>

  return (
    <Fragment>
      <RenderedDirectory
        directory={fileTreeData}
        expanded={true}
        collapseFunction={props.collapseFunction}
        openCreateBackdrop={openCreateBackdrop}
      />
      <Dialog open={createBackdropOpen} onClose={closeCreateBackdrop}>
        <DialogTitle>Create</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Create new file or directory in {createParentDir}
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="createInput"
            label="File Name"
            type="text"
            fullWidth
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={closeCreateBackdrop}>Cancel</Button>
          <Button onClick={closeCreateBackdrop}>Create</Button>
        </DialogActions>
      </Dialog>
    </Fragment>
  )
}
