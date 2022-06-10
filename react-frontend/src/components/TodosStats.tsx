import { useMemo } from 'react';
import { useQuery } from 'react-query';
import { GetTodosResponse } from '../types';
import styled from 'styled-components';
import { ResponsivePie } from '@nivo/pie'
import { ResponsiveCalendar } from '@nivo/calendar'
import { TODO_QUERY_CONFIG } from '../pages/TodosPage';

const PREVIOUS_YEARS_TO_SHOW = 1;

type TodosStatsProps = {
  status: string,
  search: string,
  directory: string,
  tags: string,
}

const StatsWrapper = styled.div`
  width: 100%;
  height: 30rem;
  display: flex;`

const TagChartWrapper = styled.div`
  width: 40%;
  height: 100%;`

const CalendarWrapper = styled.div`
  width: 60%;
  height: 100%;`

export function TodosStatsSection(props: TodosStatsProps) {

  const {
    data: todoData
  } = useQuery<GetTodosResponse, Error>(
    'todos-' + props.status + '-' + props.directory + '-' + props.search + '-' + props.tags, () =>

    // TODO - Replace with a better library
    fetch('http://localhost:8181/api/v1/todos?status=' + props.status + '&directory_filter=' + props.directory + '&query_string=' + props.search + '&sort_by=start_date&tag=' + props.tags).then(res =>
      res.json()
    ),
    TODO_QUERY_CONFIG
  )

  const tagData = useMemo(() => {
    if (todoData === undefined) {
      return [];
    } else {
      return Object.entries(todoData.meta.tag_counts).map(([key, value]) => {
        return {id: key, value: value}
      })
    }
  }, [todoData])

  const calendarData = useMemo(() => {

    if (todoData === undefined) {
      return [];
    }

    const cutoffDate = `${new Date().getFullYear() - PREVIOUS_YEARS_TO_SHOW}-01-01`;

    const dayCounts: {[key: string]: number} = {};

    for (const todo of todoData.items) {

      const todoDate = (props.status.toLowerCase() === "incomplete")
        ? todo.start_date
        : todo.end_date

      if (todoDate < cutoffDate) {
        continue
      }

      if (dayCounts.hasOwnProperty(todoDate)) {
        dayCounts[todoDate] += 1
      } else {
        dayCounts[todoDate] = 1
      }
    }

    return Object.entries(dayCounts).map(([key, value]) => {
      return {
        day: key,
        value: value
      }
    })
  }, [todoData, props.status])

  if (todoData === undefined) {
    return <div>Loading...</div>
  }

  return <StatsWrapper>
    <TagChartWrapper>
      <ResponsivePie
        data={tagData}
        margin={{ top: 40, right: 80, bottom: 80, left: 80 }}
        animate={true}
        sortByValue={true}
        activeOuterRadiusOffset={8}
        innerRadius={0.5}
        padAngle={0.5}
        cornerRadius={5}
        arcLinkLabelsColor={{
            from: 'color',
        }}
        arcLinkLabelsThickness={3}
        arcLinkLabelsTextColor={{
            from: 'color',
            modifiers: [['darker', 1.2]],
        }}
      />
    </TagChartWrapper>
    <CalendarWrapper>
      <ResponsiveCalendar
          data={calendarData}
          from={`${new Date().getFullYear() - PREVIOUS_YEARS_TO_SHOW}-01-02`}
          to={new Date()}
          emptyColor="#eeeeee"
          colors={[ '#c4e4df', '#bae2dc', '#b0dfd8', '#83d7c9', '#77d5c5', '#6dd3c2', '#5ed0bd', '#4ecdb8']}
          margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
          yearSpacing={40}
          monthBorderColor="#ffffff"
          dayBorderWidth={2}
          dayBorderColor="#ffffff"
      />
    </CalendarWrapper>
  </StatsWrapper>
}
