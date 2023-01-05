import { useState, Suspense } from 'react';
import { useQuery } from 'react-query';
import { useQueryClient } from 'react-query';
import styled from 'styled-components';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import { DefinitionsGrid } from '../components/DefinitionsGrid';
import { GetSubdirsResponse,
         GetConfigResponse } from '../types';
import { SuspenseFallback } from '../components/SuspenseFallback';


// const STALE_TIME_SECONDS = 300;
// const CACHE_TIME_MINUTES = 60;
// export const QUERY_CONFIG = {
//   // How long responses are cached for
//   staleTime: 1000 * STALE_TIME_SECONDS,

//   // How long Responses are kept in the cache
//   //   after a definitions component is no longer shown
//   cacheTime: 1000 * 60 * CACHE_TIME_MINUTES,
// }


export const DefinitionsPageWrapper = styled.div`
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


export function DefinitionsPage() {

  const queryClient = useQueryClient();

  const [directory, setDirectory] = useState('ALL');
  const [updatedDirectory, setUpdatedDirectory] = useState(false);

  let {
    data: configData
  } = useQuery<GetConfigResponse, Error>(['config'], () =>
    fetch('http://localhost:8181/api/v1/config').then(res =>
      res.json()
    )
    // ,QUERY_CONFIG
  )

  let {
    data: subdirsData
  } = useQuery<GetSubdirsResponse, Error>(['subdirs'], () =>
    fetch('http://localhost:8181/api/v1/subdirs').then(res =>
      res.json()
    )
    // ,QUERY_CONFIG
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

  const handleDirectoryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDirectory(event.target.value);
    queryClient.invalidateQueries(['definitions']);
  }

  function handleRefreshClick() {
    queryClient.invalidateQueries(['definitions', { directory }]);
  }

  return (
    <DefinitionsPageWrapper>
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
        <DefinitionsGrid
          directory={directory}
        />
      </Suspense>
    </DefinitionsPageWrapper>
  )
}
