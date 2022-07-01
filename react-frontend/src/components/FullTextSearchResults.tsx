import { useQuery } from 'react-query';

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

type FullTextSearchResponse<T extends FullTextSearchResult | AggregatedFullTextSearchResult> = {
  items: Array<T>,
  count: number
}

type FullTextSearchResultsProps = {
  query: string
}

export function FullTextSearchResults(props: FullTextSearchResultsProps) {

  const { data: FullTextSearchData } =
    useQuery<FullTextSearchResponse<AggregatedFullTextSearchResult>, Error>('fullTextSearch-' + props.query, () =>
    fetch('http://localhost:8181/api/v1/search?query_string=' + props.query +
          '&aggregate_by_file=true').then(res =>
      res.json()
    )
  )

  return (
    <div>Full Text Search Results: {props.query} {FullTextSearchData}</div>
  )
}
