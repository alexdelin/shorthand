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
  transition: width ${ANIMATION_LENGTH_MS}ms;
  background-color: rgb(33, 37, 41);
  color: white;
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
  transition: width ${ANIMATION_LENGTH_MS}ms, left ${ANIMATION_LENGTH_MS}ms;
  background-color: rgb(33, 37, 61);
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
  transition: width ${ANIMATION_LENGTH_MS}ms;`

export const NavDivider = styled.hr`
  width: 75%;
  border-color: #555;
  margin: 0rem;`

type NavOptionListProps = {isExpanded?: boolean};

export const NavOptionList = styled.ul`
  flex-grow: 1;
  width: ${(props: NavOptionListProps) => (props.isExpanded ? '10rem' : '3rem')};
  transition: width ${ANIMATION_LENGTH_MS}ms;
  list-style-type: none;
  padding-inline-start: 0rem;
  margin: 0rem;
  font-family: helvetica;`

export const NavOption = styled(Link)`
  padding-top: 1rem;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  text-decoration: none;
  color: white;
  justify-content: center;`

export const ElementsIcon = styled.span`
  padding-top: 1rem;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  text-decoration: none;
  color: white;
  justify-content: center;
  cursor: pointer;`

export const TreeIcon = ElementsIcon;

export const NavOptionIcon = styled.i`
  font-size: 1.5rem;
  margin-right: 1rem;
  margin-left: 1rem;`

type NavOptionNameProps = {isExpanded?: boolean};

export const NavOptionName = styled.div`
  font-size: 1.25rem;
  transition: width ${ANIMATION_LENGTH_MS}ms;
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
  transition: opacity ${ANIMATION_LENGTH_MS}ms;
  background-color: #777;
  z-index: 1;`

type NavSubOptionListProps = {elementsExpanded?: boolean};

export const NavSubOptionList = styled.ul`
  padding-left: 1rem;
  padding-top: 0.25rem;
  height: ${(props: NavSubOptionListProps) => (props.elementsExpanded ? '13.75rem' : '0rem')};
  width: ${(props: NavSubOptionListProps) => (props.elementsExpanded ? '9rem' : '0rem')};
  transition: height ${ANIMATION_LENGTH_MS}ms, width ${ANIMATION_LENGTH_MS}ms;
  overflow: hidden;
  list-style-type: none;`

export const NavSubOption = styled(Link)`
  display: flex;
  flex-wrap: nowrap;
  padding-top: 0.5rem;
  align-items: center;
  text-decoration: none;
  color: white;`

export const NavSubOptionName = styled.span`
  font-size: 1rem;`
