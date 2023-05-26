import styled from 'styled-components';
import { Fragment, useState, useEffect } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { Link } from "react-router-dom";
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import InputAdornment from '@mui/material/InputAdornment';
import Autocomplete from '@mui/material/Autocomplete';
import { ANIMATION_LENGTH_MS } from './Nav.styles';
import { GetSubdirsResponse } from '../types';


type FileRowWrapperProps = {
  menuOpen: boolean
}

const FileRowWrapper = styled.div`
  display: flex;
  justify-content: space-between;
  margin-left: 1rem;
  padding-top: 0.2rem;
  padding-bottom: 0.2rem;
  ${(props: FileRowWrapperProps) => (props.menuOpen ? 'background-color: rgb(45, 50, 82);' : '')}

  &:hover {
    background-color: rgb(45, 50, 82);
  }

  &:hover > i {
    color: white;
  }`

const FileWrapper = styled(Link)`
  font-size: 1.25rem;
  text-decoration: none;
  color: white;`

const FileTreeIcon = styled.i`
  margin-right: 0.2rem;`

type FolderActionsIconProps = {
  menuOpen: boolean
}

const FolderActionsIcon = styled.i`
  margin-right: 0.6rem;
  color: ${(props: FolderActionsIconProps) => (props.menuOpen ? 'white' : 'rgb(33, 37, 61)')};`


type TOC = {
  files: string[],
  dirs: TOC[],
  path: string,
  text: string
};


type FileRowProps = {
  directory: TOC,
  file: string,
  collapseFunction: () => void,
  openMoveDialog: (sourceType: string, sourcePath: string) => void,
  openDeleteDialog: (deleteType: string, deletePath: string) => void,
}

function FileRow(props: FileRowProps) {

  const [fileMenuAnchorEl, setFileMenuAnchorEl] = useState<null | HTMLElement>(null);
  const fileMenuOpen = Boolean(fileMenuAnchorEl);

  const handleFileActionsClick = (event: React.MouseEvent<HTMLElement>) => {
    setFileMenuAnchorEl(event.currentTarget);
  };

  const handleFileMenuClose = () => {
    setFileMenuAnchorEl(null)
  }

  const handleMoveButtonClick = () => {
    setFileMenuAnchorEl(null);
    props.openMoveDialog('note', `${props.directory.path}/${props.file}`);
  };

  const handleDeleteButtonClick = () => {
    setFileMenuAnchorEl(null);
    props.openDeleteDialog('note', `${props.directory.path}/${props.file}`);
  };

  return (
    <FileRowWrapper menuOpen={fileMenuOpen}>
      <FileWrapper
        key={`${props.directory.path}/${props.file}`}
        to={`/compose?path=${props.directory.path}/${props.file}`}
        onClick={props.collapseFunction}
      >
        <FileTreeIcon className="bi bi-file-earmark-text"></FileTreeIcon>{props.file}
      </FileWrapper>
      <FolderActionsIcon menuOpen={fileMenuOpen} onClick={handleFileActionsClick} className="bi bi-three-dots"></FolderActionsIcon>
      <Menu
        id="folder-actions-menu"
        anchorEl={fileMenuAnchorEl}
        open={fileMenuOpen}
        onClose={handleFileMenuClose}
      >
        <MenuItem onClick={handleMoveButtonClick}>Rename / Move</MenuItem>
        <MenuItem onClick={handleDeleteButtonClick}>Delete</MenuItem>
      </Menu>
    </FileRowWrapper>
  )
}


type DirectoryRowWrapperProps = {
  menuOpen: boolean
}

const DirectoryRowWrapper = styled.div`
  display: flex;
  justify-content: space-between;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
  ${(props: DirectoryRowWrapperProps) => (props.menuOpen ? 'background-color: rgb(45, 50, 82);' : '')}

  &:hover {
    background-color: rgb(45, 50, 82);
  }

  &:hover > i {
    color: white;
  }`

const DirectoryNameWrapper = styled.div``

type DirectoryRowProps = {
  directory: TOC,
  openCreateDialog: (parentDir: string) => void,
  openMoveDialog: (sourceType: string, sourcePath: string) => void,
  openDeleteDialog: (deleteType: string, deletePath: string) => void,
}

function DirectoryRow(props: DirectoryRowProps) {

  const [dirMenuAnchorEl, setDirMenuAnchorEl] = useState<null | HTMLElement>(null);
  const dirMenuOpen = Boolean(dirMenuAnchorEl);

  function handleDirectoryClick(e: React.MouseEvent<HTMLDivElement, MouseEvent>) {
    // This is a hack, but there is no easier way to do it via common react patterns
    const directoryWrapperEl = e.currentTarget.parentElement?.parentElement;
    const directoryContentsNode = directoryWrapperEl?.childNodes[1] as HTMLDivElement | undefined;
    if (directoryContentsNode) {
      const classes = directoryContentsNode.classList;
      classes.toggle('collapsed');
    }
  }

  const handleDirActionsClick = (event: React.MouseEvent<HTMLElement>) => {
    setDirMenuAnchorEl(event.currentTarget);
  };

  const handleDirMenuClose = () => {
    setDirMenuAnchorEl(null);
  };

  const handleCreateButtonClick = () => {
    setDirMenuAnchorEl(null);
    if (props.directory.path === '') {
      props.openCreateDialog('/');
    } else {
      props.openCreateDialog(props.directory.path);
    }
  };

  const handleMoveButtonClick = () => {
    setDirMenuAnchorEl(null);
    props.openMoveDialog('directory', props.directory.path);
  };

  const handleDeleteButtonClick = () => {
    setDirMenuAnchorEl(null);
    props.openDeleteDialog('directory', props.directory.path);
  };

  return (
    <DirectoryRowWrapper menuOpen={dirMenuOpen}>
      <DirectoryNameWrapper onClick={handleDirectoryClick}>
        <FileTreeIcon className="bi bi-folder2"></FileTreeIcon>{props.directory.text}
      </DirectoryNameWrapper>
      <FolderActionsIcon menuOpen={dirMenuOpen} onClick={handleDirActionsClick} className="bi bi-three-dots"></FolderActionsIcon>
      <Menu
        id="folder-actions-menu"
        anchorEl={dirMenuAnchorEl}
        open={dirMenuOpen}
        onClose={handleDirMenuClose}
      >
        <MenuItem onClick={handleCreateButtonClick}>Create</MenuItem>
        {props.directory.path !== '' && (
          <MenuItem onClick={handleMoveButtonClick}>Rename / Move</MenuItem>
        )}
        {props.directory.path !== '' && (
          <MenuItem onClick={handleDeleteButtonClick}>Delete</MenuItem>
        )}
      </Menu>
    </DirectoryRowWrapper>
  )
}


const DirectoryWrapper = styled.div`
  margin-left: 1rem;
  font-size: 1.25rem;`

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

type RenderedDirectoryProps = {
  directory: TOC,
  expanded: boolean,
  collapseFunction: () => void,
  openCreateDialog: (parentDir: string) => void,
  openMoveDialog: (sourceType: string, sourcePath: string) => void,
  openDeleteDialog: (deleteType: string, deletePath: string) => void,
}

function RenderedDirectory(props: RenderedDirectoryProps) {

  return (
  <DirectoryWrapper key={props.directory.path}>
    <DirectoryRow
      directory={props.directory}
      openCreateDialog={props.openCreateDialog}
      openMoveDialog={props.openMoveDialog}
      openDeleteDialog={props.openDeleteDialog}
    />
    <DirectoryContentsWrapper className={props.expanded ? '' : 'collapsed'}>
      {props.directory.files.map(file =>
        <FileRow
          key={`${props.directory.path}/${file}`}
          directory={props.directory}
          file={file}
          collapseFunction={props.collapseFunction}
          openMoveDialog={props.openMoveDialog}
          openDeleteDialog={props.openDeleteDialog}
        />
      )}
      {props.directory.dirs.map(dir =>
        <RenderedDirectory
          key={dir.path}
          directory={dir}
          expanded={false}
          collapseFunction={props.collapseFunction}
          openCreateDialog={props.openCreateDialog}
          openMoveDialog={props.openMoveDialog}
          openDeleteDialog={props.openDeleteDialog}
        />
      )}
    </DirectoryContentsWrapper>
  </DirectoryWrapper>)
}


type CreateDialogProps = {
  createDialogOpen: boolean,
  setCreateDialogOpen: (value: boolean) => void,
  createParentDir: string
}

function CreateDialog(props: CreateDialogProps) {
  /* Dialog for Creating a new note or directory
  */

  const [createType, setCreateType] = useState('note');
  const [createName, setCreateName] = useState('');

  const queryClient = useQueryClient();

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCreateName(event.target.value);
  }

  const handleChangeCreateType = (event: React.MouseEvent<HTMLElement>, newCreateType: string) => {
    setCreateType(newCreateType);
  };

  const closeCreateDialog = () => {
    props.setCreateDialogOpen(false);
  };

  const handleCreateSubmit = () => {
    if (createType === 'note') {
      const newNotePath = `${props.createParentDir}/${createName}.note`
      fetch('/api/v1/filesystem/create?type=file&path=' + newNotePath,
        { method: 'PUT' }
      ).then(async res => {
        if (await res.text() === 'ack') {
          queryClient.invalidateQueries(['toc']);
          closeCreateDialog();
        }
      })
    } else {
      const newDirPath = `${props.createParentDir}/${createName}`
      fetch('/api/v1/filesystem/create?type=directory&path=' + newDirPath,
        { method: 'PUT' }
      ).then(async res => {
        if (await res.text() === 'ack') {
          queryClient.invalidateQueries(['toc']);
          queryClient.invalidateQueries(['subdirs']);
          closeCreateDialog();
        }
      })
    }
  };

  return (
    <Dialog open={props.createDialogOpen} onClose={closeCreateDialog}>
      <DialogTitle>Create</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Create new note or directory in <code>{props.createParentDir}</code>
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
        <Button onClick={handleCreateSubmit}>Create</Button>
      </DialogActions>
    </Dialog>
  );
}


type MoveDialogProps = {
  moveDialogOpen: boolean,
  setMoveDialogOpen: (value: boolean) => void,
  moveSourceType: string,
  moveSourcePath: string
}

function MoveDialog(props: MoveDialogProps) {
  /* Dialog for Moving or renaming a note or directory
  */

  const [moveDestinationName, setMoveDestinationName] = useState('');
  const [moveDestinationDir, setMoveDestinationDir] = useState<null | string>(null);

  const queryClient = useQueryClient();

  useEffect(() => {
    const sourceFilename = props.moveSourcePath.split('/').slice(-1)[0];
    var sourceDirname = props.moveSourcePath.split('/').slice(0,-1).join('/');
    if (sourceDirname === '') {
      sourceDirname = '/'
    }
    setMoveDestinationName(sourceFilename);
    setMoveDestinationDir(sourceDirname);
  }, [props.moveSourcePath])

  const {
    data: subdirsData
  } = useQuery<GetSubdirsResponse, Error>(['subdirs'], () =>
    fetch('/api/v1/subdirs').then(async res => {
        const response = await res.json() as string[]
        response.push('/')
        return response
      }
    )
  )

  const closeMoveDialog = () => {
    props.setMoveDialogOpen(false);
  };

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMoveDestinationName(event.target.value);
  }

  const handleMoveSubmit = () => {
    const destinationPath = `${moveDestinationDir === '/' ? '' : moveDestinationDir}/${moveDestinationName}`;
    console.log(`Moving ${props.moveSourcePath} to ${destinationPath}`);
    fetch(`/api/v1/filesystem/move?source=${props.moveSourcePath}&destination=${destinationPath}`,
      { method: 'POST' }
    ).then(async res => {
      if (await res.text() === 'ack') {
        queryClient.invalidateQueries(['toc']);
        if (props.moveSourceType === 'directory') {
          queryClient.invalidateQueries(['subdirs']);
        }
        closeMoveDialog();
      }
    })
  };

  if (subdirsData === undefined) return <div>Loading...</div>

  return (
    <Dialog sx={{overflowY: 'show'}} open={props.moveDialogOpen} onClose={closeMoveDialog}>
      <DialogTitle>Rename / Move</DialogTitle>
      <DialogContent>
        <DialogContentText sx={{mb: '1rem'}}>
          Rename or Move {props.moveSourceType} <code>{props.moveSourcePath}</code>
        </DialogContentText>
        <Autocomplete
          disablePortal
          id="destinationDir"
          options={subdirsData}
          value={moveDestinationDir}
          onChange={(event: any, newValue: string | null) => {
            setMoveDestinationDir(newValue);
          }}
          renderInput={(params) =>
            <TextField {...params} label="Move To" />
          }
        />
        <TextField
          autoFocus
          margin="dense"
          id="destinationName"
          label="Name"
          type="text"
          fullWidth
          variant="standard"
          value={moveDestinationName}
          onChange={handleNameChange}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={closeMoveDialog}>Cancel</Button>
        <Button onClick={handleMoveSubmit}>Apply</Button>
      </DialogActions>
    </Dialog>
  );
}


type DeleteDialogProps = {
  deleteDialogOpen: boolean,
  setDeleteDialogOpen: (value: boolean) => void,
  deletePath: string,
  deleteType: string
}

function DeleteDialog(props: DeleteDialogProps) {
  /* Dialog for Deleting a note or **empty** directory
  */

  const queryClient = useQueryClient();

  const closeDeleteDialog = () => {
    props.setDeleteDialogOpen(false);
  };

  const handleDeleteSubmit = () => {
    if (props.deleteType === 'note') {
      fetch('/api/v1/filesystem/delete?type=file&path=' + props.deletePath,
        { method: 'DELETE' }
      ).then(async res => {
        if (await res.text() === 'ack') {
          queryClient.invalidateQueries(['toc']);
          closeDeleteDialog();
        }
      })
    } else {
      fetch('/api/v1/filesystem/delete?type=directory&path=' + props.deletePath,
        { method: 'DELETE' }
      ).then(async res => {
        if (await res.text() === 'ack') {
          queryClient.invalidateQueries(['toc']);
          queryClient.invalidateQueries(['subdirs']);
          closeDeleteDialog();
        }
      })
    }
  };

  return (
    <Dialog open={props.deleteDialogOpen} onClose={closeDeleteDialog}>
      <DialogTitle>Delete</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Are you sure you want to delete the {props.deleteType} at path <code>{props.deletePath}</code>
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={closeDeleteDialog}>Cancel</Button>
        <Button color='error' onClick={handleDeleteSubmit}>Delete</Button>
      </DialogActions>
    </Dialog>
  );
}


const FileTreeWrapper = styled.div`
  width: 35rem;`

type FileTreeProps = {
  collapseFunction: () => void
}

export function FileTree(props: FileTreeProps) {
  /* The main File Tree component. This one stores and manages
     the state of all of the dialogs for creating, modifying,
     and deleting elements from the file tree
  */

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createParentDir, setCreateParentDir] = useState('/');

  const [moveDialogOpen, setMoveDialogOpen] = useState(false);
  const [moveSourceType, setMoveSourceType] = useState('note');
  const [moveSourcePath, setMoveSourcePath] = useState('');

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteType, setDeleteType] = useState('note');
  const [deletePath, setDeletePath] = useState('')

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

  const openCreateDialog = (parentDir: string) => {
    setCreateParentDir(parentDir);
    setCreateDialogOpen(true);
  };

  const openMoveDialog = (sourceType: string, sourcePath: string) => {
    setMoveSourceType(sourceType);
    setMoveSourcePath(sourcePath);
    setMoveDialogOpen(true);
  }

  const openDeleteDialog = (deleteType: string, deletePath: string) => {
    setDeleteType(deleteType);
    setDeletePath(deletePath);
    setDeleteDialogOpen(true);
  }

  if (fileTreeData === undefined) return <div>Loading...</div>

  return (
    <Fragment>
      <FileTreeWrapper>
        <RenderedDirectory
          directory={fileTreeData}
          expanded={true}
          collapseFunction={props.collapseFunction}
          openCreateDialog={openCreateDialog}
          openMoveDialog={openMoveDialog}
          openDeleteDialog={openDeleteDialog}
        />
      </FileTreeWrapper>
      <CreateDialog
        createDialogOpen={createDialogOpen}
        setCreateDialogOpen={setCreateDialogOpen}
        createParentDir={createParentDir}
      />
      <MoveDialog
        moveDialogOpen={moveDialogOpen}
        setMoveDialogOpen={setMoveDialogOpen}
        moveSourceType={moveSourceType}
        moveSourcePath={moveSourcePath}
      />
      <DeleteDialog
        deleteDialogOpen={deleteDialogOpen}
        setDeleteDialogOpen={setDeleteDialogOpen}
        deletePath={deletePath}
        deleteType={deleteType}
      />
    </Fragment>
  )
}
