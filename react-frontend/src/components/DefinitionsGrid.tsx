import { Fragment, useMemo } from 'react';
import { Grid, _ } from 'gridjs-react';
import styled from 'styled-components';
import { useQuery, useMutation } from 'react-query';
import { useQueryClient } from 'react-query';
import MarkdownIt from 'markdown-it';
import tm from 'markdown-it-texmath';
import { GetTodosResponse, Tag, Todo, ShorthandApiError } from '../types';
import {
  StyledTodoText,
  StyledTag, ActionButton
} from './TodosGrid.styles';
import { QUERY_CONFIG } from '../pages/DefinitionsPage';

type DefinitionsGridProps = {
  directory: string
}

type DefinitionsQueryKey = {
  directory: string
}

type Definition = {
  file_path: string,
  display_path: string,
  line_number: string,
  term: string,
  definition: string
}

type GetDefinitionsResponse = {
  count: number,
  items: Array<Definition>
}

export const StyledDefinition = styled.div`
  display: inline;
  line-height: 1.3rem;

  & p {
    display: inline;
  }

  & a {
    color: blue;
  }

  & code {
    color: #e83e8c;
  }`

const writer = MarkdownIt({}).use(
  tm,{ delimiters: 'dollars', macros: {"\\RR": "\\mathbb{R}"}
});

function getDefinitionElement(definition: string) {
  return _(<Fragment>
    <StyledDefinition
      dangerouslySetInnerHTML={{__html: writer.render(definition)}}
    />
  </Fragment>);
}

export function DefinitionsGrid(props: DefinitionsGridProps) {

  const queryClient = useQueryClient();

  const {
    data: definitionsData
  } = useQuery<GetDefinitionsResponse, Error>(
    ['definitions', { directory: props.directory }], () =>

    // TODO - Replace with a better library
    fetch(`http://localhost:8181/api/v1/definitions?&directory_filter=${props.directory}`).then(res =>
      res.json()
    ),
    QUERY_CONFIG
  )

  const elements = useMemo(() => {
    if (definitionsData === undefined) {
      return [];
    } else {
      return definitionsData.items.map((definition) => (
        [`${definition.display_path}: ${definition.line_number}`,
          definition.term,
          getDefinitionElement(definition.definition)]
      ))
    }
  // eslint-disable-next-line
  }, [definitionsData]);


  if (definitionsData === undefined) return <div>Loading...</div>

  return <Fragment>
    <Grid
      data={elements}
      pagination={{
        enabled: true,
        limit: 50
      }}
      columns={['Path', 'Term', 'Definition']}
    />
  </Fragment>

}
