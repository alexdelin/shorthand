import { useState, Suspense } from 'react';
import { useQuery } from 'react-query';
import { useQueryClient } from 'react-query';
import "gridjs/dist/theme/mermaid.css";
import 'katex/dist/katex.min.css';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import { TodosGrid } from '../components/TodosGrid';
import { GetConfigResponse, GetTagsResponse,
         GetSubdirsResponse } from '../types';
import { TodoPageWrapper, StyledForm,
         RefreshIcon } from './TodosPage.styles';
import { TodosStatsSection } from '../components/TodosStats';
import { SuspenseFallback } from '../components/SuspenseFallback';


const TODO_STALE_TIME_SECONDS = 300;
const CACHE_TIME_MINUTES = 60;
export const TODO_QUERY_CONFIG = {
  // How long responses are cached for
  staleTime: 1000 * TODO_STALE_TIME_SECONDS,

  // How long Responses are kept in the cache
  //   after a todo component is no longer shown
  cacheTime: 1000 * 60 * CACHE_TIME_MINUTES,
}


export default function TodosPage() {

  const queryClient = useQueryClient();

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

  function handleRefreshClick() {
    queryClient.invalidateQueries(`todos-${status}-${directory}-${search}-${tags}`);
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
          sx={{ ml: '2rem' }}
          color="success"
          onClick={handleRefreshClick}
        >
          <RefreshIcon className="bi bi-arrow-clockwise"></RefreshIcon>
        </Button>
        <Button
          variant="contained"
          sx={{ ml: 'auto' }}
          onClick={handleStatsClick}
        >
          Stats
        </Button>
      </StyledForm>
      {showStats ? (
        <Suspense fallback={SuspenseFallback}>
          <TodosStatsSection
            status={status}
            search={search}
            directory={directory}
            tags={tags}
          />
        </Suspense>
      ) : null}
      <Suspense fallback={SuspenseFallback}>
        <TodosGrid
          status={status}
          search={search}
          directory={directory}
          tags={tags}
        />
      </Suspense>
    </TodoPageWrapper>
  )
}
