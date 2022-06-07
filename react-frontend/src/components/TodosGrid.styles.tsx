import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';

export const StyledReactMarkdown = styled(ReactMarkdown)`
  & a {
    color: blue;
  }

  & code {
    color: #e83e8c;
  }`

export const StyledTag = styled.span`
  display: inline-block;
  padding: 0.25em 0.4em;
  font-size: 75%;
  font-weight: 700;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
  color: #fff;
  background-color: #6c757d;`
