import { useQuery } from "react-query"
import { GetCalendarResponse, GetMasterEditTimelineResponse, GetOpenFilesResponse, GetRecentNotesResponse } from "../types"
import { useMemo, useState } from "react"
import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material"
import styled from "styled-components"
import FullCalendar from "@fullcalendar/react"
import listPlugin from '@fullcalendar/list'
import { ResponsiveCalendar } from "@nivo/calendar"
import { NoteLink } from "../components/TodosGrid.styles"
import { getDateString, getDateTimeString } from "../utils/dates"


const PREVIOUS_YEARS_TO_SHOW = 2


const HomePageWrapper = styled.div`
  padding: 2rem;
  display: flex;
`;

const SidePanel = styled.div`
  width: 50%;
`

const StyledHeaderCell = styled.span`
  font-size: 16px;
  font-weight: bold;
`

const StyledTableCell = styled.span`
  font-size: 16px;
`

const LatestUpdatesWrapper = styled.div`
  width: 100%;
`

const MasterTimelineWrapper = styled.div`
  width: 100%;
  height: 30rem;
`


export function HomePage() {

  const { data: recentNotes } =
    useQuery<GetRecentNotesResponse, Error>(['recent-notes'], () =>
      fetch('/api/v1/recent_notes').then(res =>
        res.json()
      ),
      { placeholderData: [] }
    );

  const { data: calendarData } = 
    useQuery<GetCalendarResponse, Error>(['homepage-calendar'], () =>
      fetch(`/api/v1/calendar?mode=recent`).then(res =>
        res.json()
      ),
      { placeholderData: {} }
    );

  const { data: masterEditTimeline } = 
    useQuery<GetMasterEditTimelineResponse, Error>(['master-edit-timeline'], () =>
      fetch(`/api/v1/master_edit_timeline`).then(res =>
        res.json()
      ),
      { placeholderData: {} }
    );

  const [selectedDate, setSelectedDate] = useState<string | undefined>(undefined);

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
    return eventData;

  }, [calendarData]);


  const masterTimeline = useMemo(() => {
    
    if (!masterEditTimeline) { return []; }

    let timeline = [];
    for (const [date, summary] of Object.entries(masterEditTimeline)) {
      timeline.push({
        day: date,
        value: summary.count
      })
    }

    return timeline

  }, [masterEditTimeline]);


  const visibleChanges = useMemo(() => {
    if (selectedDate === undefined || masterEditTimeline === undefined) {
      return [];
    }

    const diffs = masterEditTimeline[selectedDate].diffs;
    return diffs;

  }, [masterEditTimeline, selectedDate])


  return (
    <HomePageWrapper>
      <SidePanel>

        <h2>Recent Notes</h2>
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

        <h2>Latest Updates</h2>
        <LatestUpdatesWrapper>
          <FullCalendar
            eventOrderStrict={true}
            plugins={[ listPlugin ]}
            displayEventTime={false}
            contentHeight={'auto'}
            initialView="listWeek"
            headerToolbar={false}
            events={latestUpdates}
            eventOrder={'-start,index'}
          />
        </LatestUpdatesWrapper>

      </SidePanel>
      <SidePanel style={{paddingLeft: '2rem'}}>

        <h2>All Changes</h2>
        <MasterTimelineWrapper>
          <ResponsiveCalendar
            data={masterTimeline}
            from={`${new Date().getFullYear() - PREVIOUS_YEARS_TO_SHOW}-01-02`}
            to={new Date()}
            emptyColor="#eeeeee"
            colors={[ '#c4e4df', '#bae2dc', '#b0dfd8', '#83d7c9', '#77d5c5', '#6dd3c2', '#5ed0bd', '#4ecdb8']}
            margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
            yearSpacing={40}
            // monthSpacing={10}
            monthBorderColor="#ffffff"
            dayBorderWidth={2}
            dayBorderColor="#ffffff"
            onClick={(day) => {
              setSelectedDate(day.day)
            }}
          />
        </MasterTimelineWrapper>

        {Boolean(visibleChanges.length) && <>
          <span>Changes on {selectedDate}</span>
          <ul>
            {visibleChanges.map((change) => {
              return <li>{change.diff_type + ' ' + change.note_path + ' - ' + getDateTimeString(change.timestamp)}</li>
            })}
          </ul>
          </>
        }

      </SidePanel>

    </HomePageWrapper>
  )
}
