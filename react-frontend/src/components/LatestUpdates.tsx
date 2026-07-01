import { useQuery } from "react-query";
import styled from "styled-components";
import { GetCalendarResponse } from "../types";
import { useMemo } from "react";
import FullCalendar from "@fullcalendar/react";
import listPlugin from '@fullcalendar/list'


const LatestUpdatesWrapper = styled.div`
  width: 100%;
`


export function LatestUpdates() {

  const { data: calendarData } =
    useQuery<GetCalendarResponse, Error>(['homepage-calendar'], () =>
      fetch(`/api/v1/calendar?mode=recent`).then(res =>
        res.json()
      ),
      { placeholderData: {} }
    );

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


  return (
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
  )
}
