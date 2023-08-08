import { useState, useMemo } from 'react';
import { useQuery } from 'react-query';
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import Tooltip from 'tooltip.js';
import styled from 'styled-components';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import { GetSubdirsResponse, GetCalendarResponse } from '../types';

export const CalendarWrapper = styled.div`
  width: calc(100% - 4rem);
  padding: 2rem;
  `

export function CalendarPage() {

  const [directory, setDirectory] = useState('ALL');

  let {
    data: subdirsData
  } = useQuery<GetSubdirsResponse, Error>(['subdirs'], () =>
    fetch('/api/v1/subdirs').then(res =>
      res.json()
    )
  )

  if (subdirsData === undefined) {
    subdirsData = ['ALL']
  }

  let { data: calendarData } = useQuery<GetCalendarResponse, Error>(['calendar'], () =>
    fetch('/api/v1/calendar?directory_filter=' + directory).then(res =>
      res.json()
    )
  )

  const calendarEvents = useMemo(() => {

    let eventData = [];

    for (const year in calendarData) {
        for (const month in calendarData[year]) {
            for (const day in calendarData[year][month]) {
                for (const eventIndex in calendarData[year][month][day]) {

                    // Prep event to put on the calendar
                    const event = calendarData[year][month][day][eventIndex];
                    const formattedEvent = {
                        title: event['event'],
                        start: year + '-' + month + '-' + day,
                        url: '/render?path=' + event["file_path"] + '#line-number-' + event["line_number"],
                        type: event['type'],
                        textColor: 'black',
                        color: '#abeeff',
                        description: ''
                    };

                    const colorLookup = {
                      section: '#abeeff',  // Light Blue
                      incomplete_todo: '#ffb2ab', // Red
                      completed_todo: '#c4c5ff', // Blue
                      skipped_todo: '#c4c4c4', // Grey
                      question: '#f4b8ff', // Purple
                      answer: '#afffa3' // Green
                    }

                    formattedEvent.color = colorLookup[formattedEvent.type];

                    formattedEvent.description = `${formattedEvent.type} in ${event.file_path}<br /><br />${formattedEvent.title}`;
                    eventData.push(formattedEvent);
                }
            }
        }
    }

    return eventData

  }, [calendarData])

  const handleDirectoryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDirectory(event.target.value);
  }

  return (
    <CalendarWrapper>
      <TextField
        select
        name="directory"
        value={directory}
        onChange={handleDirectoryChange}
        label="Directory"
        size="small"
      >
        <MenuItem key="ALL" value="ALL">ALL</MenuItem>
        {subdirsData.map((subdir) =>
           <MenuItem key={subdir} value={subdir}>{subdir}</MenuItem>
        )}
      </TextField>
      <FullCalendar
        plugins={[ dayGridPlugin ]}
        initialView="dayGridMonth"
        weekends={false}
        eventDidMount={(info) => {
          var tooltip = new Tooltip(info.el, {
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
        events={calendarEvents}
      />
    </CalendarWrapper>
  )
}
