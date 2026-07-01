import { useQuery } from "react-query";
import styled from "styled-components";
import { GetRecentNotesResponse } from "../types";
import { useMemo } from "react";
import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material";
import { NoteLink } from "./TodosGrid.styles";
import { getDateTimeString } from "../utils/dates";


const StyledHeaderCell = styled.span`
  font-size: 16px;
  font-weight: bold;
`

const StyledTableCell = styled.span`
  font-size: 16px;
`

export function RecentNotes() {

  const { data: recentNotesData } =
    useQuery<GetRecentNotesResponse, Error>(['recent-notes'], () =>
      fetch('/api/v1/recent_notes').then(res =>
        res.json()
      ),
      { placeholderData: [] }
    );

  const recentNotes = useMemo(() => {
    if (!recentNotesData) {return [];}
    return recentNotesData.reverse().slice(0, 10);
  }, [recentNotesData])

  return <>
    { recentNotes?.length &&
      <Typography sx={{ fontSize: '2rem' }}>
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} size="small">
            <TableHead sx={{ backgroundColor: 'rgba(209, 209, 209, 0.3)', fontWeight: 'bold'}}>
              <TableRow>
                <TableCell><StyledHeaderCell>Note</StyledHeaderCell></TableCell>
                <TableCell align="center"><StyledHeaderCell>Open</StyledHeaderCell></TableCell>
                <TableCell align="center"><StyledHeaderCell>Last Modified</StyledHeaderCell></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentNotes.map((note) => (
                <TableRow
                  key={note.path}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    <StyledTableCell>
                      <NoteLink
                        target='_blank'
                        rel='noreferrer'
                        href={`/compose?path=${note.path}`}
                      >
                        <i className="bi bi-file-earmark-text" style={{marginRight: '0.25rem'}} />{note.path}
                      </NoteLink>
                    </StyledTableCell>
                  </TableCell>
                  <TableCell align="center">
                    <StyledTableCell>{note.open && <i className="bi bi-check-circle" style={{color: 'green'}} />}</StyledTableCell>
                  </TableCell>
                  <TableCell align="center">
                    <StyledTableCell>{getDateTimeString(note.last_modified)}</StyledTableCell>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Typography>
    }
  </>
}
