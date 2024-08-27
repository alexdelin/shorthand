import { Link } from "react-router-dom";
import styled from 'styled-components';

// Constants
export const ANIMATION_LENGTH_MS = 500;

type NavSidebarSCProps = {
  isExpanded: boolean
}

type TreeSidebarSCProps = {
  isExpanded: boolean,
  treeExpanded: boolean
}

export const NavSidebar = styled.div`
  width: ${(props: NavSidebarSCProps) => (props.isExpanded ? '15rem' : '5rem')};
  height: 100vh;
  z-index: 10;
  position: absolute;
  top: 0;
  left: 0;
  float: left;
  overflow: hidden;
  transition: all ${ANIMATION_LENGTH_MS}ms;
  background-color: rgb(33, 37, 41);
  color: whitesmoke;
  display: flex;
  flex-direction: column;
  align-items: center;`

export const TreeSidebar = styled.div`
  width: ${(props: TreeSidebarSCProps) => (props.isExpanded && props.treeExpanded ? '25rem' : '0rem')};
  height: 100vh;
  z-index: 10;
  position: absolute;
  top: 0;
  left: ${(props: TreeSidebarSCProps) => (props.isExpanded ? '15rem' : '5rem')};;
  float: left;
  overflow-y: scroll;
  overflow-x: hidden;
  transition: all ${ANIMATION_LENGTH_MS}ms;
  background-color: midnightblue;
  color: white;
  display: flex;
  flex-direction: column;
  scrollbar-width: none;  /* Hide Scrollbars - Firefox */
  -ms-overflow-style: none;  /* Hide Scrollbars - IE 10+ */

  &::-webkit-scrollbar {
    display: none;  /* Hide Scrollbars - Safari and Chrome */
  }`

export const TreeSidebarInner = styled.div`
  width: 25rem;
  height: 100%;`

export const NavHeader = styled.a`
  font-size: 2.25rem;
  font-family: georgia;
  font-style: italic;
  display: flex;
  align-items: baseline;
  margin-top: 0.3rem;`

type NavHeaderRestProps = {isExpanded?: boolean};

export const NavHeaderRest = styled.div`
  width: ${(props: NavHeaderRestProps) => (props.isExpanded ? '9.5rem' : '0rem')};
  overflow: hidden;
  transition: all ${ANIMATION_LENGTH_MS}ms;`

export const NavDivider = styled.hr`
  width: 75%;
  border-color: #555;
  margin: 0rem;
  margin-bottom: 0.5rem;`

export const NavOptionList = styled.ul`
  flex-grow: 1;
  width: 100%;
  transition: all ${ANIMATION_LENGTH_MS}ms;
  list-style-type: none;
  padding-inline-start: 0rem;
  margin: 0rem;
  font-family: helvetica;`

export const NavOption = styled(Link)`
  padding-top: 0.7rem;
  padding-bottom: 0.5rem;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  text-decoration: none;
  color: whitesmoke;
  justify-content: center;`

type TreeLiProps = {isExpanded?: boolean};

export const TreeLi = styled.li`
  ${(props: TreeLiProps) => (props.isExpanded ? 'background-color: midnightblue;' : '')}
  transition: all ${ANIMATION_LENGTH_MS}ms;`

export const ElementsLi = styled.li`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;`

type ElementsIconProps = {isSelected?: boolean};

export const ElementsIcon = styled.span`
  ${(props: ElementsIconProps) => (props.isSelected ? 'background-color: royalblue;' : '')}
  padding-top: 0.7rem;
  padding-bottom: 0.5rem;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  text-decoration: none;
  color: whitesmoke;
  justify-content: center;
  cursor: pointer;
  width: 100%;
  transition: all ${ANIMATION_LENGTH_MS}ms;`

export const TreeIcon = ElementsIcon;

type NavOptionItemProps = {isSelected?: boolean};

export const NavOptionItem = styled.li`
  ${(props: NavOptionItemProps) => (props.isSelected ? 'background-color: royalblue;' : '')}
  transition: all ${ANIMATION_LENGTH_MS}ms;`

export const NavOptionIcon = styled.i`
  font-size: 1.5rem;
  margin-right: 1rem;
  margin-left: 1rem;`

type NavOptionNameProps = {isExpanded?: boolean};

export const NavOptionName = styled.div`
  font-size: 1.25rem;
  transition: all ${ANIMATION_LENGTH_MS}ms;
  overflow: hidden;
  width: ${(props: NavOptionNameProps) => (props.isExpanded ? '6.25rem' : '0rem')};`

type NavCoverProps = {
  isExpanded?: boolean,
  coverVisible?: boolean
};

export const NavToggleIcon = styled.i`
  font-size: 2rem;
  margin-right: 1.5rem;
  margin-left: auto;
  margin-bottom: 0.5rem;`

export const NavCover = styled.div`
  width: 100%;
  height: 100vh;
  position: absolute;
  display: ${(props: NavCoverProps) => (props.coverVisible ? 'block' : 'none')};
  opacity: ${(props: NavCoverProps) => (props.isExpanded ? '70%' : '0%')};
  transition: all ${ANIMATION_LENGTH_MS}ms;
  background-color: #777;
  z-index: 3;`

type NavSubOptionListProps = {
  elementsExpanded?: boolean
  elementsSelected: boolean
  calendarSelected: boolean
};

export const NavSubOptionList = styled.ul`
  height: ${(props: NavSubOptionListProps) => (props.elementsExpanded ? '13.75rem' : '0rem')};
  width: 100%;
  transition: all ${ANIMATION_LENGTH_MS}ms;
  overflow: hidden;
  list-style-type: none;
  padding-top: ${(props: NavSubOptionListProps) => (props.elementsExpanded && props.elementsSelected ? '0.5rem' : '0rem')};
  padding-bottom: ${(props: NavSubOptionListProps) => (props.elementsExpanded && props.calendarSelected ? '0.2rem' : '0rem')};
  padding-left: 0rem;`

export const NavSubOption = styled(Link)`
  display: flex;
  flex-wrap: nowrap;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
  align-items: center;
  text-decoration: none;
  color: whitesmoke;
  justify-content: left;
  width: 75%;
  padding-left: 25%;`

export const NavSubOptionName = styled.span`
  font-size: 1rem;`
