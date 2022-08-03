import { useState, useEffect, useRef } from 'react';
import { useNavigate } from "react-router-dom";
import styled from 'styled-components';
import TextField from '@mui/material/TextField';
import { FileSearchResults } from './FileSearchResults';


type FileSearchModalOverlayProps = {
  shown: boolean;
  onClick: ()=>void;
}

const FileSearchModalOverlay = styled.div`
  z-index: 11;
  position: absolute;
  height: 100vh;
  width: 100%;
  background-color: #99999980;
  display: ${(props: FileSearchModalOverlayProps) => (props.shown ? 'flex' : 'none')};
  justify-content: center;
  align-items: center;`

const FileSearchModalBody = styled.div`
  width: 50%;
  height: 38rem;
  background-color: white;
  border: 1px solid #333;
  border-radius: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  overflow: scroll;`

const FileSearchInput = styled(TextField)`
  width: 100%;
  margin-bottom: 2rem;`

export function FileSearchModal() {

  const [search, setSearch] = useState('');
  const [shown, setShown] = useState(false);
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    document.addEventListener('keydown', (e) => {
      if (e.keyCode === 84 && e.ctrlKey) {
        setShown(!shown);
        if (inputRef.current !== null) {
          inputRef.current.focus();
        }
      } else if (shown === true && e.key === "Escape") {
        setShown(false);
      }
    })
  }, [shown])

  function handleSearchChange(event: React.ChangeEvent<HTMLInputElement>) {
    setTimeout(() => {
        setSearch(event.target.value)
      },
      500
    );
  }

  function handleOverlayClick() {
    setShown(false);
  }

  function handleModalClick(e: React.MouseEvent<HTMLDivElement, MouseEvent>) {
    e.stopPropagation();
  }

  function onFileResultClick(notePath: string) {
    // Record the file view
    fetch(
      'http://localhost:8181/api/v1/record_view?note_path=' + notePath,
      { method: 'POST' }
    ).then(async res => {
      if (await res.text() === 'ack') {
        // Navigate to the target page
        const viewNotePath = `/view?path=${notePath}`;
        navigate(viewNotePath);
        setShown(false);
      }
    })
  }

  return (
    <FileSearchModalOverlay shown={shown} onClick={handleOverlayClick}>
      <FileSearchModalBody onClick={(e) => handleModalClick(e)}>
        <FileSearchInput
          type="text"
          name="noteSearch"
          onChange={handleSearchChange}
          label="Search"
          variant="outlined"
          inputRef={inputRef}
        />
        <FileSearchResults
          query={search}
          showHeader={false}
          onResultClick={onFileResultClick}
        />
      </FileSearchModalBody>
    </FileSearchModalOverlay>
  )
}
