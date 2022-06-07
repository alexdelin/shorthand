import { useState } from 'react';
import { useQuery } from 'react-query';
import "gridjs/dist/theme/mermaid.css";
import 'katex/dist/katex.min.css';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import { TodosGrid } from '../components/TodosGrid';
import { TodosStats } from '../components/TodosStats';
import { GetConfigResponse, GetTagsResponse,
         GetSubdirsResponse } from '../types';
import { TodoPageWrapper, StyledForm } from './TodosPage.styles';

export function TodosPage() {

  const [status, setStatus] = useState('Incomplete');
  const [search, setSearch] = useState('');
  const [directory, setDirectory] = useState('ALL');
  const [tags, setTags] = useState('ALL');

  let {
    data: configData
  } = useQuery<GetConfigResponse, Error>('config', () =>
    fetch('http://localhost:8181/api/v1/config').then(res =>
      res.json()
    )
  )

  let {
    data: tagsData
  } = useQuery<GetTagsResponse, Error>('tags', () =>
    fetch('http://localhost:8181/api/v1/tags').then(res =>
      res.json()
    )
  )

  if (tagsData === undefined) {
    tagsData = {
      count: 1,
      items: ['ALL'],
      meta: {}
    }
  }

  let {
    data: subdirsData
  } = useQuery<GetSubdirsResponse, Error>('subdirs', () =>
    fetch('http://localhost:8181/api/v1/subdirs').then(res =>
      res.json()
    )
  )

  if (subdirsData === undefined) {
    subdirsData = ['ALL']
  }

  if (configData?.default_directory !== undefined &&
      configData.default_directory !== directory) {
    setDirectory(configData.default_directory);
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
        <Button variant="contained">Contained</Button>
      </StyledForm>
      <TodosStats />
      <TodosGrid status={status} search={search} directory={directory} tags={tags} />
    </TodoPageWrapper>
  )
}
