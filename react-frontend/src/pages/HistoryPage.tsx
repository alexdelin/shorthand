import { useState } from 'react';
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from 'react-query';
import styled from 'styled-components';

import Timeline from '@mui/lab/Timeline';
import TimelineItemOriginal from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineOppositeContent from '@mui/lab/TimelineOppositeContent';
import TimelineDot from '@mui/lab/TimelineDot';
import Typography from '@mui/material/Typography';

import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import diff from 'react-syntax-highlighter/dist/esm/languages/hljs/diff';
import plaintext from 'react-syntax-highlighter/dist/esm/languages/hljs/plaintext';
import atomOneLight from 'react-syntax-highlighter/dist/esm/styles/hljs/atom-one-light';
import { Button, Chip } from '@mui/material';

SyntaxHighlighter.registerLanguage('diff', diff);
SyntaxHighlighter.registerLanguage('plaintext', plaintext);

type DiffInfo = {
  diff_type: 'create' | 'edit' | 'move' | 'delete'
  timestamp: string
  move_direction?: 'in' | 'out'
  from_path?: string
  to_path?: string
}

type EditTimelineEntry = {
  version: string
  diffs: DiffInfo[]
}

type NoteEditTimeline = EditTimelineEntry[]

const TimelineContentLeft = styled(TimelineContent)`
  display: flex;
  flex-direction: column;
  align-items: end;
  justify-content: center;`

const TimelineContentRight = styled(TimelineOppositeContent)`
  display: flex;
  flex-direction: column;
  align-items: start;
  justify-content: center;`

const TimelineDotForIcon = styled(TimelineDot)`
  width: 1.3rem;
  height: 1.3rem;
  justify-content: center;
  align-items: center;`

const TimelineItem = styled(TimelineItemOriginal)`
  &.selected {
    background-color: #ccc;
    border: 1px solid;
    border-radius: 1rem;
  }`

const HistoryHeader = styled.div`
  height: 5rem;
  display: flex;
  align-items: center;
  padding-left: 2rem;
  padding-right: 1rem;
  justify-content: space-between;`

const HistoryContent = styled.div`
  display: flex;
  height: calc(100% - 5rem);`

const TimelineContainer = styled.div`
  width: 40%;
  height: 100%;
  overflow: scroll;
  background-color: #ddd;`

const EventViewer = styled.div`
  display: flex;
  flex-direction: column;
  padding-left: 1rem;
  padding-right: 1rem;
  width: 60%;
  height: 100%;
  overflow: scroll;`

function getLang() {
  if (navigator.languages !== undefined)
    return navigator.languages[0];
  return navigator.language;
}

function getFormattedDate(date_string: string) {
  const parsedDate = Date.parse(date_string);
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const locale = getLang();
  console.log(parsedDate);
  return Intl.DateTimeFormat(locale, {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: timezone,
  }).format(parsedDate)
}


type EventInfo = {
  key: string
  type: 'version' | 'diff' | 'current'
  notePath: string
  diffType?: 'create' | 'edit' | 'move' | 'delete'
  timestamp?: string
  moveDirection?: 'in' | 'out'
  fromPath?: string
  toPath?: string
}


export function HistoryPage() {

  const [ searchParams, setSearchParams ] = useSearchParams();
  const notePath = searchParams.get('path');
  const [eventInfo, setEventInfo] = useState<EventInfo | null>(null);

  const {
    data: noteEditTimeline
  } = useQuery<NoteEditTimeline, Error>(['edit-timeline', { path: notePath }], () =>
    fetch('/api/v1/edit_timeline?note_path=' + notePath).then(res =>
      res.json()
    )
  )

  function getSnapshotEl(timestamp: string) {
    if (!notePath || !timestamp) {return null;}
    return (
      <TimelineItem
        key={`version-${timestamp}`}
        className={eventInfo?.key === `version-${timestamp}` ? 'selected' : undefined}
        onClick={() => {setEventInfo({
          type: 'version',
          key: `version-${timestamp}`,
          timestamp: timestamp,
          notePath: notePath
        })}}
      >
        <TimelineSeparator>
          <TimelineConnector />
          <TimelineDotForIcon color="info">
            <i className="bi bi-copy"></i>
          </TimelineDotForIcon>
          <TimelineConnector />
        </TimelineSeparator>
        <TimelineContentLeft>
          Snapshot
          <br />
          <Typography variant="body2" color='text.secondary'>{getFormattedDate(timestamp)}</Typography>
        </TimelineContentLeft>
      </TimelineItem>
    )
  }

  function getDiffEl(diff: DiffInfo) {
    if (!notePath) { return null; }
    if (diff.diff_type === 'create') {
      return (
        <TimelineItem
          key={`diff-create-${diff.timestamp}`}
          className={eventInfo?.key === `diff-create-${diff.timestamp}` ? 'selected' : undefined}
          onClick={() => {setEventInfo({
            key: `diff-create-${diff.timestamp}`,
            type: 'diff',
            notePath: notePath,
            timestamp: diff.timestamp,
            diffType: diff.diff_type
          })}}
        >
          <TimelineContentRight>
            Note Created
            <br />
            <Typography variant="body2" color='text.secondary'>{getFormattedDate(diff.timestamp)}</Typography>
          </TimelineContentRight>
          <TimelineSeparator>
            <TimelineConnector />
            <TimelineDotForIcon color="success" variant="outlined">
              <i style={{color: "#2e7d32"}} className="bi bi-plus-lg"></i>
            </TimelineDotForIcon>
            <TimelineConnector />
          </TimelineSeparator>
          <TimelineContentLeft />
        </TimelineItem>
      );
    } else if (diff.diff_type === 'edit') {
      return (
        <TimelineItem
          key={`diff-edit-${diff.timestamp}`}
          className={eventInfo?.key === `diff-edit-${diff.timestamp}` ? 'selected' : undefined}
          onClick={() => {setEventInfo({
            key: `diff-edit-${diff.timestamp}`,
            type: 'diff',
            notePath: notePath,
            timestamp: diff.timestamp,
            diffType: diff.diff_type
          })}}
        >
          <TimelineContentRight>
            Note Edited
            <br />
            <Typography variant="body2" color='text.secondary'>{getFormattedDate(diff.timestamp)}</Typography>
          </TimelineContentRight>
          <TimelineSeparator>
            <TimelineConnector />
            <TimelineDotForIcon color="primary" variant="outlined">
              <i style={{color: "#1976d2"}} className="bi bi-file-earmark-diff"></i>
            </TimelineDotForIcon>
            <TimelineConnector />
          </TimelineSeparator>
          <TimelineContentLeft>
          </TimelineContentLeft>
        </TimelineItem>
      );
    } else if (diff.diff_type === 'move') {
      return (
        <TimelineItem
          key={`diff-move-${diff.timestamp}`}
          className={eventInfo?.key === `diff-move-${diff.timestamp}` ? 'selected' : undefined}
          onClick={() => {setEventInfo({
            key: `diff-move-${diff.timestamp}`,
            type: 'diff',
            notePath: notePath,
            timestamp: diff.timestamp,
            diffType: diff.diff_type,
            moveDirection: diff.move_direction,
            fromPath: diff.from_path,
            toPath: diff.to_path
          })}}
        >
          <TimelineContentRight>
            Note Moved
            <br />
            <Typography variant="body2" color='text.secondary'>{getFormattedDate(diff.timestamp)}</Typography>
          </TimelineContentRight>
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
          <TimelineContentLeft>
          </TimelineContentLeft>
        </TimelineItem>
      );
    } else if (diff.diff_type === 'delete') {
      return (
        <TimelineItem
          key={`diff-delete-${diff.timestamp}`}
          className={eventInfo?.key === `diff-delete-${diff.timestamp}` ? 'selected' : undefined}
          onClick={() => {setEventInfo({
            key: `diff-delete-${diff.timestamp}`,
            type: 'diff',
            notePath: notePath,
            timestamp: diff.timestamp,
            diffType: diff.diff_type
          })}}
        >
          <TimelineContentRight>
            Note Deleted
            <br />
            <Typography variant="body2" color='text.secondary'>{getFormattedDate(diff.timestamp)}</Typography>
          </TimelineContentRight>
          <TimelineSeparator>
            <TimelineConnector />
            <TimelineDotForIcon color="error" variant="outlined">
              <i style={{color: "#d32f2f"}} className="bi bi-x-lg"></i>
            </TimelineDotForIcon>
            <TimelineConnector />
          </TimelineSeparator>
          <TimelineContentLeft>
          </TimelineContentLeft>
        </TimelineItem>
      );
    } else {
      console.error('Got unexpected diff type ' + diff.diff_type);
    }
  }

  if (!noteEditTimeline) {
    return <>Loading...</>
  }

  if (!notePath) {
    return <>No Note Selected...</>
  }

  return (
    <>
      <HistoryHeader>
        <h2>History for note {notePath}</h2>
        <div>
          <Link to={`/compose?path=${notePath}`}>
            <Button>Edit</Button>
          </Link>
          <Link type='button' to={`/view?path=${notePath}`}>
            <Button>View</Button>
          </Link>
        </div>
      </HistoryHeader>

      <HistoryContent>
        <TimelineContainer>

          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <h3>Event Timeline</h3>
          </div>

          <Timeline position="left">

            <TimelineItem
              key='current'
              className={eventInfo?.key === 'current' ? 'selected' : undefined}
              onClick={() => {setEventInfo({ type: 'current', key: 'current', notePath: notePath})}}
            >
              <TimelineSeparator>
                <TimelineConnector />
                <TimelineDotForIcon color="success">
                  <i className="bi bi-file-earmark-text"></i>
                </TimelineDotForIcon>
                <TimelineConnector />
              </TimelineSeparator>
              <TimelineContentLeft>
                Current Version
              </TimelineContentLeft>
            </TimelineItem>

            {noteEditTimeline.map((entry) => {
              return (
                <>
                  {entry.diffs.map((diff) => {
                    return getDiffEl(diff);
                  })}
                  {getSnapshotEl(entry.version)}
                </>
              );
            })}

          </Timeline>
        </TimelineContainer>
        <HistoryEventViewer eventInfo={eventInfo} />
      </HistoryContent>
    </>
  )
}


type HistoryEventViewerProps = {
  eventInfo: EventInfo | null
}

export function HistoryEventViewer(props: HistoryEventViewerProps) {

  let url: string | null = null;
  if (props.eventInfo) {
    if (props.eventInfo.type === 'current') {
      url = `/api/v1/note?path=${props.eventInfo.notePath}`;
    }
    else if (props.eventInfo.type === 'diff' && props.eventInfo.timestamp) {
      url = `/api/v1/note_diff?note_path=${props.eventInfo.notePath}` +
            `&timestamp=${encodeURIComponent(props.eventInfo.timestamp)}` +
            `&diff_type=${props.eventInfo.diffType}`;
    }
    else if (props.eventInfo.type === 'version' && props.eventInfo.timestamp) {
      url = `/api/v1/note_version?note_path=${props.eventInfo.notePath}` +
            `&timestamp=${encodeURIComponent(props.eventInfo.timestamp)}`;
    }
  }

  const {
    data: editHistoryEvent
  } = useQuery<string | undefined, Error>(['edit-history-event', { url: url }], () => {
    if (url === null) {return undefined;}
    return fetch(url).then(res => res.text())
  })

  if (!props.eventInfo) {
    return (
      <EventViewer>
        <h3>Details for Selected Event</h3>

        Select an event on the left to view details
      </EventViewer>
    );
  }

  return (
    <EventViewer>
      <h3>Details for Selected Event</h3>

      Event Type: {props.eventInfo.type} {props.eventInfo.type === 'diff' && `(${props.eventInfo.diffType})`}
      <br />
      Note Path: {props.eventInfo.notePath}
      <br />
      {props.eventInfo.timestamp && `Timestamp: ${getFormattedDate(props.eventInfo.timestamp)}`}

      { props.eventInfo.moveDirection === 'in' && (<>
          <br />
          <span>
            Moved From:&nbsp;
            <Link to={`/history?path=${props.eventInfo.fromPath}`}>
              {props.eventInfo.fromPath}
            </Link>
          </span>
      </>)}

      { props.eventInfo.moveDirection === 'out' && (<>
          <br />
          <span>
            Moved To:&nbsp;
            <Link style={{display: 'contents'}} to={`/history?path=${props.eventInfo.toPath}`}>
              {props.eventInfo.toPath}
            </Link>
          </span>
      </>)}

      { !editHistoryEvent && <>Select an event to view details</> }
      { (props.eventInfo.type === 'version' || props.eventInfo.type === 'current')
        && editHistoryEvent
        && <SyntaxHighlighter
              language="plaintext"
              showLineNumbers={true}
              wrapLongLines={true}
              style={atomOneLight}
              customStyle={{overflowX: 'visible'}}
           >
            {editHistoryEvent}
           </SyntaxHighlighter>
      }
      { props.eventInfo.type === 'diff'
        && editHistoryEvent
        && <SyntaxHighlighter
              language="diff"
              showLineNumbers={true}
              wrapLongLines={true}
              style={atomOneLight}
              customStyle={{overflowX: 'visible'}}
           >
            {editHistoryEvent}
           </SyntaxHighlighter>
      }
    </EventViewer>
  )
}
