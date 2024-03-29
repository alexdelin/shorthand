import { Fragment } from 'react';
import { Grid, _ } from 'gridjs-react';
import styled from 'styled-components';
import MarkdownIt from 'markdown-it';
import tm from 'markdown-it-texmath';
// import { QUERY_CONFIG } from '../pages/DefinitionsPage';

type DefinitionsGridProps = {
  directory: string,
  search: string
}

type Definition = {
  file_path: string,
  display_path: string,
  line_number: string,
  term: string,
  definition: string,
  sub_elements: string
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

function reduceSubElementIndent(sub_elements: string) {
  const rawLines = sub_elements.split('\n')
  const indentLevels = rawLines.map(line => line.length - line.trimStart().length)
  const minIndent = Math.min(...indentLevels)
  const dedentedLines = rawLines.map(line => line.slice(minIndent))
  return dedentedLines.join('\n')
}

function getDefinitionElement(definition: string, sub_elements?: string) {
  return _(<Fragment>
    <StyledDefinition
      dangerouslySetInnerHTML={{__html: writer.render(definition)}}
    />
    {sub_elements && (
      <Fragment>
        <hr />
        <StyledDefinition
          dangerouslySetInnerHTML={{__html: writer.render(reduceSubElementIndent(sub_elements))}}
        />
      </Fragment>
    )}
  </Fragment>);
}

export function DefinitionsGrid(props: DefinitionsGridProps) {

  return <Fragment>
    <Grid
      pagination={{
        limit: 50
      }}
      columns={[
        'Path', 'Term',
        {
          name: 'Definition',
          width: '60%',
          formatter: (cell: [string, string]) => {
            return getDefinitionElement(cell[0], cell[1])
          }
        }
      ]}
      server={{
        url: `/api/v1/definitions?include_sub_elements=True&directory_filter=${props.directory}&query_string=${props.search}`,
        then: (data: GetDefinitionsResponse) => data.items.map(definition => [
          `${definition.display_path}: ${definition.line_number}`,
          definition.term,
          [definition.definition, definition.sub_elements]
        ])
      }}
    />
  </Fragment>

}
