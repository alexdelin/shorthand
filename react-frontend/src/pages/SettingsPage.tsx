import { useState } from 'react';
import { useQuery } from 'react-query';
import styled from 'styled-components';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import { GetConfigResponse, GetSubdirsResponse } from '../types';

export const SettingsPageWrapper = styled.div`
  padding: 2rem;`

export function SettingsPage() {

  const [defaultDir, setDefaultDir] = useState('');
  const [updatedDirectory, setUpdatedDirectory] = useState(false);

  let {
    data: configData
  } = useQuery<GetConfigResponse, Error>(['config'], () =>
    fetch('/api/v1/config').then(res =>
      res.json()
    )
    // ,TODO_QUERY_CONFIG
  )

  let {
    data: subdirsData
  } = useQuery<GetSubdirsResponse, Error>(['subdirs'], () =>
    fetch('/api/v1/subdirs').then(res =>
      res.json()
    )
    // ,TODO_QUERY_CONFIG
  )

  if (subdirsData === undefined) {
    subdirsData = []
  }

  // Set the default directory, but only once when the page loads
  if (configData?.default_directory &&
      configData.default_directory !== defaultDir &&
      subdirsData.includes(configData.default_directory) &&
      !updatedDirectory) {
    console.log('Setting directory!');
    setDefaultDir(configData.default_directory);
    setUpdatedDirectory(true);
  }

  const handleDefaultDirChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDefaultDir(event.target.value);
  }

  if (!configData || !subdirsData) return <div>Loading...</div>;

  return  (
    <SettingsPageWrapper>
      <h1>Settings</h1>
      <h3>User Settings</h3>
      <div>
      Default Directory:
      <TextField
        select
        name="defaultDir"
        value={defaultDir}
        onChange={handleDefaultDirChange}
        // label="Default Directory"
        size="small"
      >
        {subdirsData.map((subdir) =>
           <MenuItem key={subdir} value={subdir}>{subdir}</MenuItem>
        )}
      </TextField>
      </div>
      <h3>Server Settings</h3>
      <div>
        Notes Directory: <code>{configData.notes_directory}</code>
      </div>
      <div>
        Cache Directory: <code>{configData.cache_directory}</code>
      </div>
      <div>
        Grep Path: <code>{configData.grep_path}</code>
      </div>
      <div>
        Find Path: <code>{configData.find_path}</code>
      </div>
      <div>
        Log File: <code>{configData.log_file_path}</code>
      </div>
      <div>
        Log Level: <code>{configData.log_level}</code>
      </div>
      <div>
        Log Format: <code>{configData.log_format}</code>
      </div>
      <h3>Frontend Settings</h3>
      <div>
        View History Limit: <code>{configData.frontend.view_history_limit}</code>
      </div>
      <div>
        Map Tileserver URL: <code>{configData.frontend.map_tileserver_url}</code>
      </div>
    </SettingsPageWrapper>
  )
}
