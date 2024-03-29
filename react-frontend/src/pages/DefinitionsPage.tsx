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
  align-items: center;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;

  & > div:first-child,
  & > a:last-child {
    margin-left: auto;
  }`

export const RefreshIcon = styled.i`
  font-size: 1.35rem;
  display: flex;
  margin-top: 0.2rem;
  margin-bottom: 0.2rem;`

export const DownloadIcon = styled.i`
  font-size: 1.35rem;
  display: flex;
  margin-top: 0.2rem;
  margin-bottom: 0.2rem;
  margin-right: 0.2rem;`


export function DefinitionsPage() {

  console.log('rendering')

  const queryClient = useQueryClient();

  const [directory, setDirectory] = useState('ALL');
  const [search, setSearch] = useState('');
  const [updatedDirectory, setUpdatedDirectory] = useState(false);

  let {
    data: configData
  } = useQuery<GetConfigResponse, Error>(['config'], () =>
    fetch('/api/v1/config').then(res =>
      res.json()
    )
    // ,QUERY_CONFIG
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
      subdirsData.includes(configData.default_directory) &&
      !updatedDirectory) {
    setDirectory(configData.default_directory);
    setUpdatedDirectory(true);
  }

  const handleDirectoryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDirectory(event.target.value);
    queryClient.invalidateQueries(['definitions']);
  }

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setTimeout(() => {
        setSearch(event.target.value)
      },
      500
    );
  }

  function handleRefreshClick() {
    queryClient.invalidateQueries(['definitions', { directory, search }]);
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
        <TextField
          type="text"
          name="search"
          onChange={handleSearchChange}
          label="Search"
          variant="outlined"
          size="small"
        />
        <a
          href={"/api/v1/definitions/csv?directory_filter=" + directory}
          download={"definitions_" + directory + ".csv"}
        >
          <Button
            variant="outlined"
            color="secondary"
          >
            <DownloadIcon className="bi bi-download"></DownloadIcon>CSV
          </Button>
        </a>
      </StyledForm>
      <Suspense fallback={<div>Loading...</div>}>
        <DefinitionsGrid
          directory={directory}
          search={search}
        />
      </Suspense>
    </DefinitionsPageWrapper>
  )
}
