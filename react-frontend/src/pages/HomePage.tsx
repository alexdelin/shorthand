import { useQuery } from "react-query"
import { GetCalendarResponse, GetOpenFilesResponse, GetRecentNotesResponse } from "../types"
import { useMemo } from "react"
import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material"
import styled from "styled-components"
import FullCalendar from "@fullcalendar/react"
import listPlugin from '@fullcalendar/list'
import Tooltip from "tooltip.js"


const HomePageWrapper = styled.div`
  padding: 2rem;
`;

const StyledHeaderCell = styled.span`
  font-size: 16px;
  font-weight: bold;
`

const StyledTableCell = styled.span`
  font-size: 16px;
`


export function HomePage() {

  const { data: recentNotes } =
    useQuery<GetRecentNotesResponse, Error>(['recent-notes'], () =>
      fetch('/api/v1/recent_notes').then(res =>
        res.json()
      ),
      { placeholderData: [] }
    );

  const { data: openNotes } =
    useQuery<GetOpenFilesResponse, Error>(['open-files'], () =>
      fetch('/frontend-api/get-open-files').then(res =>
        res.json()
      ),
      { placeholderData: [] }
    );

  const { data: calendarData } = useQuery<GetCalendarResponse, Error>(['calendar'], () =>
    fetch(`/api/v1/calendar?mode=recent`).then(res =>
      res.json()
    )
  );

  const noteData = useMemo(() => {
    return recentNotes?.map((note) => {
      return {
        path: note,
        open: openNotes?.includes(note)
      }
    }).reverse();
  }, [recentNotes, openNotes]);

  const latestUpdates = useMemo(() => {

    let eventData = [];

    for (const year in calendarData) {
        for (const month in calendarData[year]) {
            for (const day in calendarData[year][month]) {
                for (const eventIndex in calendarData[year][month][day]) {

                    const event = calendarData[year][month][day][eventIndex];
                    const formattedEvent = {
                        title: event['event'],
                        start: year + '-' + month + '-' + day,
                        end: '',
                        url: '/view?path=' + event["file_path"] + '#line-number-' + event["line_number"],
                        type: event['type'],
                        textColor: 'black',
                        color: '#abeeff',
                        description: '',
                        index: 0
                    };

                    if (event.start) formattedEvent.start = event.start;
                    if (event.end) {
                      formattedEvent.end = event.end;
                    }

                    const indexLookup = {
                      section: 1,
                      incomplete_todo: 2,
                      completed_todo: 3,
                      skipped_todo: 6,
                      question: 4,
                      answer: 5,
                    }

                    const colorLookup = {
                      section: 'rgb(31, 58, 202)',  // Dark Blue
                      incomplete_todo: 'rgb(253, 225, 191)', // Orange
                      completed_todo: 'rgb(171, 225, 255)', // Light Blue
                      skipped_todo: '#c4c4c4', // Grey
                      question: '#f4b8ff', // Purple
                      answer: '#afffa3' // Green
                    }

                    if (formattedEvent.type === 'section') {
                      formattedEvent.textColor = 'white';
                    }

                    formattedEvent.color = colorLookup[formattedEvent.type];
                    formattedEvent.index = indexLookup[formattedEvent.type];

                    formattedEvent.description = `${formattedEvent.type} in ${event.file_path}<br /><br />${formattedEvent.title}`;
                    eventData.push(formattedEvent);
                }
            }
        }
    }
    console.log(eventData);
    return eventData;

  }, [calendarData]);

  return (
    <HomePageWrapper>
      <h2>Recent Notes</h2>

      { noteData?.length && 
      <Typography sx={{ fontSize: '2rem' }}>
        <TableContainer sx={{ width: 1000 }} component={Paper}>
          <Table sx={{ minWidth: 650 }} size="small">
            <TableHead sx={{ backgroundColor: 'rgba(209, 209, 209, 0.3)', fontWeight: 'bold'}}>
              <TableRow>
                <TableCell><StyledHeaderCell>Note</StyledHeaderCell></TableCell>
                <TableCell align="center"><StyledHeaderCell>Open</StyledHeaderCell></TableCell>
                <TableCell align="center"><StyledHeaderCell>Last Modified</StyledHeaderCell></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {noteData.map((note) => (
                <TableRow
                  key={note.path}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    <StyledTableCell>
                      <i className="bi bi-file-earmark-text" style={{marginRight: '0.25rem'}} />{note.path}
                    </StyledTableCell>
                  </TableCell>
                  <TableCell align="center">
                    <StyledTableCell>{note.open && <i className="bi bi-check-circle" />}</StyledTableCell>
                  </TableCell>
                  <TableCell align="center">
                    <StyledTableCell>{`never`}</StyledTableCell>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Typography>
      }

      <h2>Latest Updates</h2>

      <FullCalendar
        eventOrderStrict={true}
        plugins={[ listPlugin ]}
        displayEventTime={false}
        contentHeight={'auto'}
        initialView="listWeek"
        headerToolbar={{
          left: '',
          center: '',
          right: '',
        }}
        eventDidMount={(info) => {
          return new Tooltip(info.el, {
            title: info.event.extendedProps.description,
            html: true,
            delay: {
              show: 1000,
              hide: 100
            },
            placement: 'top',
            trigger: 'hover',
            container: 'body'
          });
        }}
        events={latestUpdates}
        eventOrder={'-start,index'}
      />

      <h2>Contributions</h2>
      Github-style graph with diffs per day

    </HomePageWrapper>
  )
}
