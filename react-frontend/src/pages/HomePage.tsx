import styled from "styled-components"
import { RecentNotes } from "../components/RecentNotes"
import { LatestUpdates } from "../components/LatestUpdates"
import { MasterTimeline } from "../components/MasterTimeline"


const HomePageWrapper = styled.div`
  padding: 2rem;
  display: flex;
`;

const SidePanel = styled.div`
  width: 50%;
`


export function HomePage() {

  return (
    <HomePageWrapper>
      <SidePanel>

        <h2>Recent Notes</h2>
        <RecentNotes />

        <h2>Latest Updates</h2>
        <LatestUpdates />

      </SidePanel>
      <SidePanel style={{paddingLeft: '2rem'}}>

        <h2>All Changes</h2>
        <MasterTimeline />

      </SidePanel>

    </HomePageWrapper>
  )
}
