import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useNavigate } from "react-router-dom";
import styled from 'styled-components';


const PAGE_SIZE = 10;

const FileResultsWrapper = styled.div`
  width: 100%;`

const FileResultsList = styled.div`
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 0.3rem;

  & :last-child {
    border-bottom: none;
  }`

const FileResult = styled.div`
  border-bottom: 1px solid #e5e7eb;
  padding: 0.6rem;
  color: #4d525d;`

const MoreButton = styled.div`
  padding: 0.6rem;
  text-align: center;`

type FileSearchResult = string
type FileSearchResponse = FileSearchResult[]

interface FileSearchResultsProps {
  query: string;
  showHeader?: boolean;
  onResultClick?: (notePath: string) => void;
}

export function FileSearchResults({query, showHeader=true, onResultClick}: FileSearchResultsProps) {

  const [resultCount, setResultCount] = useState(PAGE_SIZE);
  const navigate = useNavigate();

  const { data: FileSearchData } =
    useQuery<FileSearchResponse, Error>('fileSearch-' + query, () =>
    fetch('http://localhost:8181/api/v1/files?query_string=' + query
          ).then(res =>
      res.json()
    ),
    { placeholderData: [] }
  )

  // Reset the result count whenever the query changes
  useEffect(() => {
    setResultCount(PAGE_SIZE);
  }, [query]);

  if (FileSearchData === undefined) {
    return <div>No Results</div>
  }

  function handleResultClick(notePath: string) {
    if (onResultClick !== undefined) {
      // Call a result click handler if provided
      onResultClick(notePath);
    } else {
      // Else, fall back to the default
      // Record the file view
      fetch(
        'http://localhost:8181/api/v1/record_view?note_path=' + notePath,
        { method: 'POST' }
      ).then(async res => {
        if (await res.text() === 'ack') {
          // Navigate to the target page
          const viewNotePath = `/view?path=${notePath}`;
          navigate(viewNotePath);
        }
      })
    }
  }

  function handleMoreClick() {
    setResultCount(resultCount + PAGE_SIZE);
  }

  let pagedResults = FileSearchData;
  let isTruncated = false;
  if (FileSearchData.length > resultCount) {
    pagedResults = FileSearchData.slice(0, resultCount)
    isTruncated = true;
  }

  return (
    <FileResultsWrapper>
      {showHeader && <h3>Notes</h3>}
      <FileResultsList>
        {pagedResults.map((result) =>
          <FileResult
            key={result}
            onClick={() => handleResultClick(result)}
          >
            {result}
          </FileResult>
        )}
        {isTruncated &&
          <MoreButton onClick={handleMoreClick}>More...</MoreButton>
        }
      </FileResultsList>
    </FileResultsWrapper>
  )
}
