import styled from 'styled-components';


export const TodoPageWrapper = styled.div`
  padding: 1rem;`

export const StyledForm = styled.form`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;

  & .MuiTextField-root {
    margin-left: 2rem;
  }

  & .MuiTextField-root:first-child {
    margin-left: auto;
  }`

export const RefreshIcon = styled.i`
  font-size: 1.35rem;
  display: flex;
  margin-top: 0.2rem;
  margin-bottom: 0.2rem;`
