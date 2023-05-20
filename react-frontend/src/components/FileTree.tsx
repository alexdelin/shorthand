import styled from 'styled-components';
import { Fragment, useState } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { Link } from "react-router-dom";
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import InputAdornment from '@mui/material/InputAdornment';
import { ANIMATION_LENGTH_MS } from './Nav.styles';
import { GetSubdirsResponse } from '../types';


const DirectoryWrapper = styled.div`
  padding-left: 1rem;
  font-size: 1.25rem;
  margin: 0.25rem;
  margin-right: 0rem;`

const DirectoryRowWrapper = styled.div`
  display: flex;
  justify-content: space-between;`

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
  margin: 0.25rem;`


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
  const directoryWrapperEl = e.currentTarget.parentElement?.parentElement;
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
  openCreateDialog: (parentDir: string) => void
}

function RenderedDirectory(props: RenderedDirectoryProps) {

  const handleCreateButtonClick = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    if (props.directory.path === '') {
      props.openCreateDialog('/');
    } else {
      props.openCreateDialog(props.directory.path);
    }
  }

  return (
  <DirectoryWrapper key={props.directory.path}>
    <DirectoryRowWrapper>
      <DirectoryNameWrapper onClick={handleDirectoryClick}>
        <FileTreeIcon className="bi bi-folder2"></FileTreeIcon>{props.directory.text}
      </DirectoryNameWrapper>
      <FileTreeIcon className="bi bi-three-dots"></FileTreeIcon>
    </DirectoryRowWrapper>
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
          openCreateDialog={props.openCreateDialog}
        />
      )}
      <CreateButtonWrapper onClick={handleCreateButtonClick}>
        <FileTreeIcon className="bi bi-plus-circle-dotted"></FileTreeIcon>New
      </CreateButtonWrapper>
    </DirectoryContentsWrapper>
  </DirectoryWrapper>)
}


export function FileTree(props: FileTreeProps) {

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createParentDir, setCreateParentDir] = useState('/');
  const [createName, setCreateName] = useState('');
  const [createType, setCreateType] = useState('note');

  const queryClient = useQueryClient();

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

  const {
    data: subdirsData
  } = useQuery<GetSubdirsResponse, Error>(['subdirs'], () =>
    fetch('/api/v1/subdirs').then(res =>
      res.json()
    )
  )

  const closeCreateDialog = () => {
    setCreateDialogOpen(false);
  };

  const openCreateDialog = (parentDir: string) => {
    setCreateParentDir(parentDir);
    setCreateDialogOpen(true);
  };

  const handleCreateParentDirChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCreateParentDir(event.target.value);
  };

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCreateName(event.target.value);
  }

  const handleChangeCreateType = (event: React.MouseEvent<HTMLElement>, newCreateType: string) => {
    setCreateType(newCreateType);
  };

  const handleCreateSubmit = (event: React.MouseEvent<HTMLElement>) => {
    if (createType === 'note') {
      const newNotePath = `${createParentDir}/${createName}.note`
      fetch('/api/v1/filesystem/create?type=file&path=' + newNotePath,
        { method: 'PUT' }
      ).then(async res => {
        if (await res.text() === 'ack') {
          queryClient.invalidateQueries(['toc']);
          setCreateDialogOpen(false);
        }
      })
    } else {
      const newDirPath = `${createParentDir}/${createName}`
      fetch('/api/v1/filesystem/create?type=directory&path=' + newDirPath,
        { method: 'PUT' }
      ).then(async res => {
        if (await res.text() === 'ack') {
          queryClient.invalidateQueries(['toc']);
          queryClient.invalidateQueries(['subdirs']);
          setCreateDialogOpen(false);
        }
      })
    }
  };

  if (fileTreeData === undefined || subdirsData === undefined) return <div>Loading...</div>

  return (
    <Fragment>
      <RenderedDirectory
        directory={fileTreeData}
        expanded={true}
        collapseFunction={props.collapseFunction}
        openCreateDialog={openCreateDialog}
      />
      <Dialog open={createDialogOpen} onClose={closeCreateDialog}>
        <DialogTitle>Create</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Create new note or directory in <code>{createParentDir}</code>
          </DialogContentText>
          {/* Toggle for File or Directory */}
          <ToggleButtonGroup
            value={createType}
            exclusive
            onChange={handleChangeCreateType}
            aria-label="create type"
          >
            <ToggleButton value="note" aria-label="note">
              Note
            </ToggleButton>
            <ToggleButton value="directory" aria-label="directory">
              Directory
            </ToggleButton>
          </ToggleButtonGroup>
          <TextField
            autoFocus
            margin="dense"
            id="createInput"
            label="Name"
            type="text"
            fullWidth
            variant="standard"
            value={createName}
            onChange={handleNameChange}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  {createType === 'note' ? '.note' : '/'}
                </InputAdornment>
              ),
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={closeCreateDialog}>Cancel</Button>
          <Button onClick={(e) => {handleCreateSubmit(e)}}>Create</Button>
        </DialogActions>
      </Dialog>
    </Fragment>
  )
}
