import { useState, Suspense } from 'react';
import { useQuery } from 'react-query';
import { useQueryClient } from 'react-query';
import styled from 'styled-components';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import { QuestionsGrid } from '../components/QuestionsGrid';
import { GetSubdirsResponse,
         GetConfigResponse } from '../types';
import { SuspenseFallback } from '../components/SuspenseFallback';


export const QuestionsPageWrapper = styled.div`
  padding: 1rem;`

export const StyledForm = styled.form`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;

  & .MuiTextField-root {
    margin-left: 2rem;
  }`

export const RefreshIcon = styled.i`
  font-size: 1.35rem;
  display: flex;
  margin-top: 0.2rem;
  margin-bottom: 0.2rem;`


export function QuestionsPage() {

  const queryClient = useQueryClient();

  const [directory, setDirectory] = useState('ALL');
  const [status, setStatus] = useState('ALL');
  const [updatedDirectory, setUpdatedDirectory] = useState(false);

  let {
    data: configData
  } = useQuery<GetConfigResponse, Error>(['config'], () =>
    fetch('/api/v1/config').then(res =>
      res.json()
    )
  )

  let {
    data: subdirsData
  } = useQuery<GetSubdirsResponse, Error>(['subdirs'], () =>
    fetch('/api/v1/subdirs').then(res =>
      res.json()
    )
    // ,QUERY_CONFIG
  )

  if (subdirsData === undefined) {
    subdirsData = ['ALL']
  }

  // Set the default directory, but only once when the page loads
  if (configData?.default_directory &&
      configData.default_directory !== directory &&
      !updatedDirectory) {
    setDirectory(configData.default_directory);
    setUpdatedDirectory(true);
  }

  const handleDirectoryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDirectory(event.target.value);
    queryClient.invalidateQueries(['questions']);
  }

  const handleStatusChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setStatus(event.target.value);
  }

  function handleRefreshClick() {
    queryClient.invalidateQueries(['questions', { directory }]);
  }

  return (
    <QuestionsPageWrapper>
      <h2>Definitions</h2>
      <StyledForm>
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
          name="status"
          value={status}
          onChange={handleStatusChange}
          label="Status"
          size="small"
        >
          <MenuItem key="ALL" value="ALL">ALL</MenuItem>
          <MenuItem key="Unanswered" value="Unanswered">Unanswered</MenuItem>
          <MenuItem key="Answered" value="Answered">Answered</MenuItem>
        </TextField>
        <Button
          variant="contained"
          sx={{ ml: '2rem' }}
          color="success"
          onClick={handleRefreshClick}
        >
          <RefreshIcon className="bi bi-arrow-clockwise"></RefreshIcon>
        </Button>
      </StyledForm>
      <Suspense fallback={SuspenseFallback}>
        <QuestionsGrid
          directory={directory}
          status={status}
        />
      </Suspense>
    </QuestionsPageWrapper>
  )
}
