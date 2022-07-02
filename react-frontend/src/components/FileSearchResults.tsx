import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useNavigate } from "react-router-dom";
import styled from 'styled-components';


const PAGE_SIZE = 10;

const FileResultsWrapper = styled.div`
  border: 1px solid black;
  border-radius: 0.5rem;`

const FileResult = styled.div`
  border-bottom: 1px solid black;
  padding: 0.5rem;`

const MoreButton = styled.div`
  padding: 0.5rem;
  text-align: center;`

type FileSearchResult = string
type FileSearchResponse = FileSearchResult[]

type FileSearchResultsProps = {
  query: string
}

export function FileSearchResults(props: FileSearchResultsProps) {

  const [resultCount, setResultCount] = useState(PAGE_SIZE);
  const navigate = useNavigate();

  const { data: FileSearchData } =
    useQuery<FileSearchResponse, Error>('fileSearch-' + props.query, () =>
    fetch('http://localhost:8181/api/v1/files?query_string=' + props.query
          ).then(res =>
      res.json()
    ),
    { placeholderData: [] }
  )

  // Reset the result count whenever the query changes
  useEffect(() => {
    setResultCount(PAGE_SIZE);
  }, [props.query]);

  if (FileSearchData === undefined) {
    return <div>No Results</div>
  }

  function handleResultClick(notePath: string) {
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
    <div>
      <h3>File Search Results</h3>
      <FileResultsWrapper>
        {pagedResults.map((result) =>
          <FileResult key={result} onClick={() => handleResultClick(result)}>{result}</FileResult>
        )}
        {isTruncated && <MoreButton onClick={handleMoreClick}>More...</MoreButton>}
      </FileResultsWrapper>
    </div>
  )
}
