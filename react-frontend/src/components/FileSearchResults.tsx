import { useQuery } from 'react-query';

type FileSearchResult = string
type FileSearchResponse = FileSearchResult[]

type FileSearchResultsProps = {
  query: string
}

export function FileSearchResults(props: FileSearchResultsProps) {

  const { data: FileSearchData } =
    useQuery<FileSearchResponse, Error>('fileSearch-' + props.query, () =>
    fetch('http://localhost:8181/api/v1/files?query_string=' + props.query
          ).then(res =>
      res.json()
    )
  )

  return (
    <div>File Search Results: {props.query} {FileSearchData}</div>
  )
}
