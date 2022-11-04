import { Fragment, useState, useEffect, useMemo } from 'react';
import { useQuery } from 'react-query';
import { useNavigate } from "react-router-dom";
import styled from 'styled-components';

// Number of files shown per "page"
const FILE_PAGE_SIZE = 10;

// Max number of matches shown per file by default
const MATCH_PAGE_SIZE = 10;

const FullTextResultsWrapper = styled.div`
  border: 1px solid #e5e7eb;
  border-radius: 0.3rem;
  background-color: #eee;

  & :last-child {
    border-bottom: none;
  }`

const FullTextFileResult = styled.div`
  border-bottom: 1px solid #e5e7eb;
  padding: 0.6rem;
  color: #4d525d;
  font-size: 1.5rem;`

const MatchList = styled.div`
  border: 1px solid #e5e7eb;
  margin-top: 0.7rem;
  border-radius: 0.3rem;
  background-color: #fff;
  font-size: 1rem;`

const FullTextMatchResult = styled.div`
  border-bottom: 1px solid #e5e7eb;
  padding: 0.6rem;
  color: #4d525d;`

const MoreFilesButton = styled.div`
  padding: 0.6rem;
  text-align: center;`

const MoreMatchesButton = styled.div`
  padding: 0.6rem;
  text-align: center;`

type AggregatedFullTextSearchMatch = {
  line_number: string,
  match_content: string
}

type AggregatedFullTextSearchResult = {
  file_path: string,
  matches: AggregatedFullTextSearchMatch[]
}

type FullTextSearchResult = {
  file_path: string,
  line_number: string,
  match_content: string
}

type FullTextSearchResponse<T extends FullTextSearchResult |
                                      AggregatedFullTextSearchResult> = {
  items: Array<T>,
  count: number
}

type FullTextSearchResultsProps = {
  query: string
}


export function FullTextSearchResults(props: FullTextSearchResultsProps) {

  const [resultCount, setResultCount] = useState(FILE_PAGE_SIZE);
  const [expandedResults, setExpandedResults] = useState<string[]>([]);
  const navigate = useNavigate();

  const { data: FullTextSearchData } =
    useQuery<FullTextSearchResponse<AggregatedFullTextSearchResult>, Error>(['fullTextSearch', { query: props.query }], () =>
    fetch('http://localhost:8181/api/v1/search' +
          '?query_string=' + props.query +
          '&aggregate_by_file=true').then(res =>
      res.json()
    )
  )

  // Reset the result count whenever the query changes
  useEffect(() => {
    setResultCount(FILE_PAGE_SIZE);
    setExpandedResults([]);
  }, [props.query]);

  function handleResultClick(event: React.MouseEvent<HTMLDivElement, MouseEvent>, notePath: string, line_number?: string) {
    event.stopPropagation();

    // Record the file view
    let recordViewUrl = `http://localhost:8181/api/v1/record_view?note_path=${notePath}`
    fetch(
      recordViewUrl,
      { method: 'POST' }
    ).then(async res => {
      if (await res.text() === 'ack') {
        // Navigate to the target page
        let viewNotePath = `/view?path=${notePath}`;
        if (line_number !== undefined) {
          viewNotePath += `#line-number-${line_number}`
        }
        navigate(viewNotePath);
      }
    })
  }

  function handleMoreFilesClick() {
    setResultCount(resultCount + FILE_PAGE_SIZE);
  }

  function handleMoreMatchesClick(event: React.MouseEvent<HTMLDivElement, MouseEvent>, filePath: string) {
    event.stopPropagation();
    setExpandedResults(expandedResults.concat([filePath]));
  }

  // Create a new array of results which we will mutate
  //   based on how many files and matches we want to show
  const trimmedResults = useMemo(() => {
    if (FullTextSearchData === undefined) return [];

    let res = FullTextSearchData.items.map((result) => {
      if (result.matches.length <= MATCH_PAGE_SIZE) {
        return {
          truncated: false,
          ...result
        }
      } else {
        if (expandedResults.includes(result.file_path)) {
          return {
            truncated: false,
            ...result
          }
        } else {
          return {
            truncated: true,
            file_path: result.file_path,
            matches: result.matches.slice(0, MATCH_PAGE_SIZE)
          }
        }
      }
    })

    if (FullTextSearchData.count > resultCount) {
      res = res.slice(0, resultCount)
    }

    return res;
  }, [FullTextSearchData, expandedResults, resultCount]);

  if (FullTextSearchData === undefined) {
    return <div>No Results</div>
  }

  const isTruncated = trimmedResults.length < FullTextSearchData.count;

  return (
    <Fragment>
      <h3>Full Text Search Results</h3>
      <FullTextResultsWrapper>
        {trimmedResults.map((result) =>
          <FullTextFileResult
            key={result.file_path}
            onClick={(e) => handleResultClick(e, result.file_path)}
          >
            {result.file_path}
            <MatchList>
              {result.matches.map((match) =>
                <FullTextMatchResult
                  key={`${result.file_path}:${match.line_number}`}
                  onClick={(e) => handleResultClick(e, result.file_path, match.line_number)}
                >
                  {match.line_number}: {match.match_content}
                </FullTextMatchResult>
              )}
              {result.truncated &&
                <MoreMatchesButton onClick={(e) => handleMoreMatchesClick(e, result.file_path)}>
                  All Matches...
                </MoreMatchesButton>
              }
            </MatchList>
          </FullTextFileResult>
        )}
        {isTruncated &&
          <MoreFilesButton onClick={handleMoreFilesClick}>
            More Notes...
          </MoreFilesButton>
        }
      </FullTextResultsWrapper>
    </Fragment>
  )
}
