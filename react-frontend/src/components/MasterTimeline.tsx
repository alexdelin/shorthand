import { useQuery } from "react-query";
import styled from "styled-components";
import { DiffInfo, GetMasterEditTimelineResponse } from "../types";
import { useMemo, useState } from "react";
import { ResponsiveCalendar } from "@nivo/calendar";
import { getDateString, getDateTimeString } from "../utils/dates";
import { Timeline, TimelineConnector, TimelineContent, TimelineItem, timelineItemClasses, TimelineSeparator } from "@mui/lab";
import { TimelineDotForIcon } from "../pages/HistoryPage";
import { Typography } from "@mui/material";


const PREVIOUS_YEARS_TO_SHOW = 2

const MasterTimelineWrapper = styled.div`
  width: 100%;
  height: 30rem;
`


function getDiffEl(diff: DiffInfo) {
  if (diff.diff_type === 'create') {
    return (
      <TimelineItem
        key={`diff-create-${diff.timestamp}`}
      >
        <TimelineSeparator>
          <TimelineConnector />
          <TimelineDotForIcon color="success" variant="outlined">
            <i style={{color: "#2e7d32"}} className="bi bi-plus-lg"></i>
          </TimelineDotForIcon>
          <TimelineConnector />
        </TimelineSeparator>
        <TimelineContent>
          Created {diff.note_path}
          <br />
          <Typography variant="body2" color='text.secondary'>{getDateTimeString(diff.timestamp)}</Typography>
        </TimelineContent>
      </TimelineItem>
    );
  } else if (diff.diff_type === 'edit') {
    return (
      <TimelineItem
        key={`diff-edit-${diff.timestamp}`}
      >
        <TimelineSeparator>
          <TimelineConnector />
          <TimelineDotForIcon color="primary" variant="outlined">
            <i style={{color: "#1976d2"}} className="bi bi-file-earmark-diff"></i>
          </TimelineDotForIcon>
          <TimelineConnector />
        </TimelineSeparator>
        <TimelineContent>
          Edited {diff.note_path}
          <br />
          <Typography variant="body2" color='text.secondary'>{getDateTimeString(diff.timestamp)}</Typography>
        </TimelineContent>
      </TimelineItem>
    );
  } else if (diff.diff_type === 'move') {
    return (
      <TimelineItem
        key={`diff-move-${diff.timestamp}`}
      >
        <TimelineSeparator>
          <TimelineConnector />
          <TimelineDotForIcon color="grey" variant="outlined">
            { diff.move_direction === 'out'
              ? <i style={{color: "rgb(147, 147, 147)"}} className="bi bi-box-arrow-right"></i>
              : <i style={{color: "rgb(147, 147, 147)"}} className="bi bi-box-arrow-in-right"></i>
            }
          </TimelineDotForIcon>
          <TimelineConnector />
        </TimelineSeparator>
        <TimelineContent>
          Moved {diff.from_path} To {diff.to_path}
          <br />
          <Typography variant="body2" color='text.secondary'>{getDateTimeString(diff.timestamp)}</Typography>
        </TimelineContent>
      </TimelineItem>
    );
  } else if (diff.diff_type === 'delete') {
    return (
      <TimelineItem
        key={`diff-delete-${diff.timestamp}`}
      >
        <TimelineSeparator>
          <TimelineConnector />
          <TimelineDotForIcon color="error" variant="outlined">
            <i style={{color: "#d32f2f"}} className="bi bi-x-lg"></i>
          </TimelineDotForIcon>
          <TimelineConnector />
        </TimelineSeparator>
        <TimelineContent>
          Deleted {diff.note_path}
          <br />
          <Typography variant="body2" color='text.secondary'>{getDateTimeString(diff.timestamp)}</Typography>
        </TimelineContent>
      </TimelineItem>
    );
  } else {
    console.error('Got unexpected diff type ' + diff.diff_type);
  }
}


export function MasterTimeline() {

  const { data: masterEditTimeline } =
    useQuery<GetMasterEditTimelineResponse, Error>(['master-edit-timeline'], () =>
      fetch(`/api/v1/master_edit_timeline`).then(res =>
        res.json()
      ),
      { placeholderData: {} }
    );

  const [selectedDate, setSelectedDate] = useState<string | undefined>(undefined);

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

    if (!masterEditTimeline[selectedDate]) {return [];}

    const diffs = masterEditTimeline[selectedDate].diffs;
    return diffs;

  }, [masterEditTimeline, selectedDate])


  return (
    <>
      <MasterTimelineWrapper>
        <ResponsiveCalendar
          data={masterTimeline}
          from={`${new Date().getFullYear() - PREVIOUS_YEARS_TO_SHOW}-01-02`}
          to={new Date()}
          emptyColor="#ebedf0"
          // colors={[ '#ddeeeb', '#b0dfd8', '#77d5c5', '#5ed0bd', '#3bc9b1']} // Original
          // colors={[ '#cbe0dd', '#a7d2cd', '#81c4bd', '#55b6ad', '#02a79e']} // Teal
          // colors={[ '#b1a3d8', '#927fcd', '#705cc0', '#4a3bb4', '#021aa7']} // Blue
          colors={[ '#9be9a8', '#40c463', '#30a14e', '#216e39']} // Github
          margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
          yearSpacing={40}
          monthSpacing={10}
          monthBorderColor="#ffffff"
          dayBorderWidth={2}
          dayBorderColor="#ffffff"
          onClick={(day) => {
            setSelectedDate(day.day)
          }}
          maxValue={10}
        />
      </MasterTimelineWrapper>

      {selectedDate && visibleChanges && Boolean(visibleChanges.length) && <>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <h3>Changes on {getDateString(selectedDate)}</h3>
        </div>
        <Timeline
          // position="left"
          sx={{
            [`& .${timelineItemClasses.root}:before`]: {
              flex: 0,
              padding: 0,
            },
          }}
        >
          {visibleChanges.map((diff) => {
            return getDiffEl(diff);
          })}
        </Timeline>
        {/*<ul>
          {visibleChanges.map((change) => {
            return <li key={change.timestamp + change.diff_type}>{change.diff_type + ' ' + change.note_path + ' - ' + getDateTimeString(change.timestamp)}</li>
          })}
        </ul>*/}
        </>
      }
    </>
  )
}
