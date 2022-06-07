import { useMemo } from 'react';
import { TodosStats } from '../types';
import styled from 'styled-components';
import { ResponsivePie } from '@nivo/pie'

type TodosStatsProps = {
  stats: TodosStats
}

const StatsWrapper = styled.div`
  width: 100%;
  height: 30rem;`

export function TodosStatsSection(props: TodosStatsProps) {

  const data = useMemo(() => {
    return Object.entries(props.stats.tag_counts).map(([key, value]) => {
      return {id: key, value: value}
    })
  }, [props.stats])
  console.log(data)

  return <StatsWrapper>
    <ResponsivePie
      data={data}
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
