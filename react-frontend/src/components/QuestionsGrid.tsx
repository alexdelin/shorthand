import { Fragment, useMemo } from 'react';
import { Grid, _ } from 'gridjs-react';
import styled from 'styled-components';
import { useQuery } from 'react-query';
import MarkdownIt from 'markdown-it';
import tm from 'markdown-it-texmath';
import { NoteLink, StyledTag } from './TodosGrid.styles';
// import { QUERY_CONFIG } from '../pages/DefinitionsPage';

type QuestionsGridProps = {
  directory: string
  status: string
}

type Question = {
  file_path: string,
  display_path: string,
  line_number: string,
  question: string,
  question_date: string,
  answer: string,
  answer_date: string,
  tags: Array<string>
}

type GetQuestionsResponse = {
  count: number,
  items: Array<Question>
}

export const StyledQuestion = styled.div`
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

function getQuestionElement(question: string, tags: string[]) {
  return _(<Fragment>
    <StyledQuestion
      dangerouslySetInnerHTML={{__html: writer.render(question)}}
    />
    {tags.map((tag) => <StyledTag>{tag}</StyledTag>)}
  </Fragment>);
}

function getQuestionLink(question: Question) {
    return _(
      <NoteLink
        target='_blank'
        rel='noreferrer'
        href={`/view?path=${question.file_path}#line-number-${question.line_number}`}
      >
        {question.display_path}<br />Line {question.line_number}
      </NoteLink>
    );
  }

export function QuestionsGrid(props: QuestionsGridProps) {

  const {
    data: questionsData
  } = useQuery<GetQuestionsResponse, Error>(
    ['questions', { directory: props.directory, status: props.status }], () =>

    // TODO - Replace with a better library
    fetch(`/api/v1/questions?status=${props.status}&directory_filter=${props.directory}`).then(res =>
      res.json()
    )
    // ,QUERY_CONFIG
  )

  const elements = useMemo(() => {
    if (questionsData === undefined) {
      return [];
    } else {
      return questionsData.items.map((question) => (
        [getQuestionLink(question),
          getQuestionElement(question.question, question.tags),
          question.answer ? getQuestionElement(question.answer, []) : '']
      ))
    }
  // eslint-disable-next-line
  }, [questionsData]);

  if (questionsData === undefined) return <div>Loading...</div>

  return <Fragment>
    <Grid
      data={elements}
      pagination={{
        limit: 50
      }}
      columns={['Path', 'Question', 'Answer']}
    />
  </Fragment>

}
