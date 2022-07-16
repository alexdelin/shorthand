import { Fragment } from 'react';
import { useQuery } from 'react-query';
import styled from 'styled-components';


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
  color: #4d525d;`

const MatchList = styled.div`
  border: 1px solid #e5e7eb;
  margin-top: 0.7rem;
  border-radius: 0.3rem;
  background-color: #fff;`

const FullTextMatchResult = styled.div`
  border-bottom: 1px solid #e5e7eb;
  padding: 0.6rem;
  color: #4d525d;`

const MoreButton = styled.div`
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

  const { data: FullTextSearchData } =
    useQuery<FullTextSearchResponse<AggregatedFullTextSearchResult>, Error>('fullTextSearch-' + props.query, () =>
    fetch('http://localhost:8181/api/v1/search' +
          '?query_string=' + props.query +
          '&aggregate_by_file=true').then(res =>
      res.json()
    )
  )

  if (FullTextSearchData === undefined) {
    return <div>No Results</div>
  }

  return (
    <Fragment>
      <h3>Full Text Search Results</h3>
      <FullTextResultsWrapper>
        {FullTextSearchData.items.map((result) =>
          <FullTextFileResult
            key={result.file_path}
            // onClick={() => handleResultClick(result)}
          >
            {result.file_path}
            <MatchList>
              {result.matches.map((match) =>
                <FullTextMatchResult>
                  {match.line_number}: {match.match_content}
                </FullTextMatchResult>
              )}
            </MatchList>
          </FullTextFileResult>
        )}
        {/*{isTruncated &&
          <MoreButton onClick={handleMoreClick}>More...</MoreButton>
        }*/}
      </FullTextResultsWrapper>
    </Fragment>
  )
}
