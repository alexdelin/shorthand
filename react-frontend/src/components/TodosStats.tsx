import { useMemo } from 'react';
import { useQuery } from 'react-query';
import { GetTodosResponse } from '../types';
import styled from 'styled-components';
import { ResponsivePie } from '@nivo/pie'

type TodosStatsProps = {
  status: string,
  search: string,
  directory: string,
  tags: string,
}

const StatsWrapper = styled.div`
  width: 100%;
  height: 30rem;`

export function TodosStatsSection(props: TodosStatsProps) {

  const {
    data: todoData
  } = useQuery<GetTodosResponse, Error>(
    'todos-' + props.status + '-' + props.directory + '-' + props.search + '-' + props.tags, () =>

    // TODO - Replace with a better library
    fetch('http://localhost:8181/api/v1/todos?status=' + props.status + '&directory_filter=' + props.directory + '&query_string=' + props.search + '&sort_by=start_date&tag=' + props.tags).then(res =>
      res.json()
    ),
    {
      // Re-Fetch every hour
      refetchInterval: 1000 * 60 * 60,

      // Cache responses for 10 seconds
      staleTime: 1000 * 10,
    }
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

  if (todoData === undefined) {
    return <div>Loading...</div>
  }

  return <StatsWrapper>
    <ResponsivePie
      data={tagData}
      margin={{ top: 40, right: 80, bottom: 80, left: 80 }}
      animate={true}
      activeOuterRadiusOffset={8}
      innerRadius={0.6}
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
  </StatsWrapper>
}
