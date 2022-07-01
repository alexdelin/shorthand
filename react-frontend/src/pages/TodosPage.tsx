import { useState } from 'react';
import { useQuery } from 'react-query';
import "gridjs/dist/theme/mermaid.css";
import 'katex/dist/katex.min.css';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import { TodosGrid } from '../components/TodosGrid';
import { GetConfigResponse, GetTagsResponse,
         GetSubdirsResponse } from '../types';
import { TodoPageWrapper, StyledForm } from './TodosPage.styles';
import { TodosStatsSection } from '../components/TodosStats';


const TODO_REFETCH_TIME_MINUTES = 60;
const TODO_STALE_TIME_SECONDS = 30000;
export const TODO_QUERY_CONFIG = {
  // Re-Fetch every hour
  refetchInterval: 1000 * 60 * TODO_REFETCH_TIME_MINUTES,

  // How long responses are cached for
  staleTime: 1000 * TODO_STALE_TIME_SECONDS,
}


export default function TodosPage() {

  const [status, setStatus] = useState('Incomplete');
  const [search, setSearch] = useState('');
  const [directory, setDirectory] = useState('ALL');
  const [tags, setTags] = useState('ALL');
  const [showStats, setShowStats] = useState(false);
  const [updatedDirectory, setUpdatedDirectory] = useState(false);

  let {
    data: configData
  } = useQuery<GetConfigResponse, Error>('config', () =>
    fetch('http://localhost:8181/api/v1/config').then(res =>
      res.json()
    ),
    TODO_QUERY_CONFIG
  )

  let {
    data: tagsData
  } = useQuery<GetTagsResponse, Error>('tags', () =>
    fetch('http://localhost:8181/api/v1/tags').then(res =>
      res.json()
    ),
    TODO_QUERY_CONFIG
  )

  if (tagsData === undefined) {
    tagsData = {
      count: 1,
      items: ['ALL']
    }
  }

  let {
    data: subdirsData
  } = useQuery<GetSubdirsResponse, Error>('subdirs', () =>
    fetch('http://localhost:8181/api/v1/subdirs').then(res =>
      res.json()
    ),
    TODO_QUERY_CONFIG
  )

  if (subdirsData === undefined) {
    subdirsData = ['ALL']
  }

  // Set the default directory, but only once when the page loads
  if (configData?.default_directory !== undefined &&
      configData.default_directory !== directory &&
      !updatedDirectory) {
    setDirectory(configData.default_directory);
    setUpdatedDirectory(true);
  }

  const handleStatusChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setStatus(event.target.value);
  }

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setTimeout(() => {
        setSearch(event.target.value)
      },
      500
    );
  }

  const handleDirectoryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDirectory(event.target.value);
  }

  const handleTagsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setTags(event.target.value);
  }

  function handleStatsClick() {
    setShowStats(!showStats);
  }

  return (
    <TodoPageWrapper>
      <h2>Todos</h2>
      <StyledForm>
        <TextField
          id="status-select"
          name="status"
          select
          label="Status"
          value={status}
          onChange={handleStatusChange}
          size="small"
        >
          <MenuItem key="Incomplete" value="Incomplete">Incomplete</MenuItem>
          <MenuItem key="Complete" value="Complete">Complete</MenuItem>
          <MenuItem key="Skipped" value="Skipped">Skipped</MenuItem>
        </TextField>
        <TextField
          type="text"
          name="search"
          onChange={handleSearchChange}
          label="Search"
          variant="outlined"
          size="small"
        />
        <TextField
          select
          name="directory"
          value={directory}
          onChange={handleDirectoryChange}
          label="Directory"
          size="small"
        >
          <MenuItem key="ALL" value="ALL">ALL</MenuItem>
          {subdirsData.map((subdir) =>
             <MenuItem key={subdir} value={subdir}>{subdir}</MenuItem>
          )}
        </TextField>
        <TextField
          select
          name="tags"
          value={tags}
          onChange={handleTagsChange}
          label="Tag"
          size="small"
        >
          <MenuItem key="ALL" value="ALL">ALL</MenuItem>
          {tagsData.items.map((tag) =>
             <MenuItem key={tag} value={tag}>{tag}</MenuItem>
          )}
        </TextField>
        <Button
          variant="contained"
          sx={{ ml: 'auto' }}
          onClick={handleStatsClick}
        >
          Stats
        </Button>
      </StyledForm>
      {showStats ? (
        <TodosStatsSection
          status={status}
          search={search}
          directory={directory}
          tags={tags}
        />) : null}
      <TodosGrid
        status={status}
        search={search}
        directory={directory}
        tags={tags}
      />
    </TodoPageWrapper>
  )
}