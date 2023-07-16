import { useState, Fragment } from 'react';
// import { useLocation } from "react-router-dom";
import {
  ANIMATION_LENGTH_MS, NavSidebar, NavHeader,
  NavHeaderRest, NavDivider, NavOptionList,
  NavOption, NavOptionIcon, NavOptionName,
  NavCover, NavSubOptionList, NavSubOption,
  NavSubOptionName, NavToggleIcon, ElementsIcon,
  TreeIcon, TreeSidebar, TreeSidebarInner
} from './Nav.styles';
import { FileTree } from './FileTree';

export function Nav() {

  const [isExpanded, setIsExpanded] = useState(false);
  const [coverVisible, setCoverVisible] = useState(false);
  const [elementsExpanded, setElementsExpanded] = useState(false);
  const [treeExpanded, setTreeExpanded] = useState(false);

  // const location = useLocation();

  function changeNav() {

    if (!coverVisible) {
      setCoverVisible(true);

    } else {
      // Wait until the animation is done to make the cover
      // element not display anymore
      setTimeout(() => {setCoverVisible(false)}, ANIMATION_LENGTH_MS);
    }
    // Ensure that the cover element is shown before we
    // start the animation
    setTimeout(() => {setIsExpanded(!isExpanded)}, 1);

    if (elementsExpanded) {
      setElementsExpanded(false);
    }
  }

  function collapseNav() {
    if (isExpanded) {
      changeNav()
    }
  }

  function handleElementsClick() {
    if (!isExpanded) {
      changeNav();
      setElementsExpanded(true);
    } else {
      setElementsExpanded(!elementsExpanded);
    }
  }

  function handleTreeClick() {
    if (!isExpanded) {
      changeNav();
      setTreeExpanded(true);
    } else {
      setTreeExpanded(!treeExpanded);
    }
  }

  return (
    <Fragment>
      <NavSidebar isExpanded={isExpanded}>
        <NavHeader onClick={changeNav}>
          <div>S</div><NavHeaderRest isExpanded={isExpanded}>horthand</NavHeaderRest>
        </NavHeader>
        <NavDivider></NavDivider>
        <NavOptionList isExpanded={isExpanded}>
          <li>
            <NavOption to="/home" onClick={collapseNav}>
              <NavOptionIcon className="bi bi-house-door"></NavOptionIcon>
              <NavOptionName isExpanded={isExpanded}>Home</NavOptionName>
            </NavOption>
          </li>
          <li>
            <NavOption to="/compose" onClick={collapseNav}>
              <NavOptionIcon className="bi bi-pen"></NavOptionIcon>
              <NavOptionName isExpanded={isExpanded}>Compose</NavOptionName>
            </NavOption>
          </li>
          <li>
            <TreeIcon onClick={handleTreeClick}>
              <NavOptionIcon className="bi bi-bar-chart-steps"></NavOptionIcon>
              <NavOptionName isExpanded={isExpanded}>Notes</NavOptionName>
            </TreeIcon>
          </li>
          <li>
            <ElementsIcon onClick={handleElementsClick}>
              <NavOptionIcon className="bi bi-code-square"></NavOptionIcon>
              <NavOptionName isExpanded={isExpanded}>Elements</NavOptionName>
            </ElementsIcon>
            <NavSubOptionList elementsExpanded={elementsExpanded}>
              <li>
                <NavSubOption to="/todos" onClick={collapseNav}>
                  <NavOptionIcon className="bi bi-check-square"></NavOptionIcon>
                  <NavSubOptionName>Todos</NavSubOptionName>
                </NavSubOption>
              </li>
              <li>
                <NavSubOption to="/questions" onClick={collapseNav}>
                  <NavOptionIcon className="bi bi-question-circle"></NavOptionIcon>
                  <NavSubOptionName>Questions</NavSubOptionName>
                </NavSubOption>
              </li>
              <li>
                <NavSubOption to="/links" onClick={collapseNav}>
                  <NavOptionIcon className="bi bi-link-45deg"></NavOptionIcon>
                  <NavSubOptionName>Links</NavSubOptionName>
                </NavSubOption>
              </li>
              <li>
                <NavSubOption to="/definitions" onClick={collapseNav}>
                  <NavOptionIcon className="bi bi-book"></NavOptionIcon>
                  <NavSubOptionName>Definitions</NavSubOptionName>
                </NavSubOption>
              </li>
              <li>
                <NavSubOption to="/datasets" onClick={collapseNav}>
                  <NavOptionIcon className="bi bi-table"></NavOptionIcon>
                  <NavSubOptionName>Datasets</NavSubOptionName>
                </NavSubOption>
              </li>
              <li>
                <NavSubOption to="/locations" onClick={collapseNav}>
                  <NavOptionIcon className="bi bi-pin-map-fill"></NavOptionIcon>
                  <NavSubOptionName>Locations</NavSubOptionName>
                </NavSubOption>
              </li>
            </NavSubOptionList>
          </li>
          <li>
            <NavOption to="/calendar" onClick={collapseNav}>
              <NavOptionIcon className="bi bi-calendar-week"></NavOptionIcon>
              <NavOptionName isExpanded={isExpanded}>Calendar</NavOptionName>
            </NavOption>
          </li>
          <li>
            <NavOption to="/search" onClick={collapseNav}>
              <NavOptionIcon className="bi bi-search"></NavOptionIcon>
              <NavOptionName isExpanded={isExpanded}>Search</NavOptionName>
            </NavOption>
          </li>
          <li>
            <NavOption to="/view" onClick={collapseNav}>
              <NavOptionIcon className="bi bi-file-earmark-richtext"></NavOptionIcon>
              <NavOptionName isExpanded={isExpanded}>View</NavOptionName>
            </NavOption>
          </li>
          <li>
            <NavOption to="/settings" onClick={collapseNav}>
              <NavOptionIcon className="bi bi-wrench"></NavOptionIcon>
              <NavOptionName isExpanded={isExpanded}>Settings</NavOptionName>
            </NavOption>
          </li>
        </NavOptionList>
        <NavToggleIcon className={"bi bi-arrow-bar-" + (isExpanded ? 'left' : 'right')} onClick={changeNav}></NavToggleIcon>
      </NavSidebar>
      <TreeSidebar isExpanded={isExpanded} treeExpanded={treeExpanded}>
        <TreeSidebarInner>
          <FileTree collapseFunction={collapseNav} />
        </TreeSidebarInner>
      </TreeSidebar>
      <NavCover isExpanded={isExpanded} coverVisible={coverVisible} onClick={changeNav}>
      </NavCover>
    </Fragment>
  )
}
