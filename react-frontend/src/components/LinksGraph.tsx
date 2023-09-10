import { useRef, useEffect } from 'react';
import { useQuery } from 'react-query';
import Cytoscape from 'cytoscape';
import elk from 'cytoscape-elk';
import CytoscapeComponent from 'react-cytoscapejs';
import styled from 'styled-components';

Cytoscape.use(elk);

type LinkInfo = {
  internal: boolean
  line_number: string
  source: string
  target: string
  text: string
  valid: boolean
}

type GetLinksResponse = LinkInfo[]

type LinksGraphProps = {
  notePath?: string
}

type StyledCytoscapeComponentProps = {
  maxHeight: number
}

const StyledCytoscapeComponent = styled(CytoscapeComponent)`
  width: 100%;
  height: ${(props: StyledCytoscapeComponentProps) => (props.maxHeight ? props.maxHeight * 7 + 'rem' : '100%')};`

// The type any is used as a workaround for broken type definitions in the library
//     which don't allow for `text-valign` and `text-halign` to be set
const baseStyle: any = [
  {
    selector: 'node',
    css: {
      'background-color': 'data(color)',
      "label": "data(label)",
      "text-valign": "bottom",
      "text-halign": "center",
      "font-size": "5px"
    }
  }, {
    selector: 'edge',
    css: {
      'curve-style': 'bezier',
      'target-arrow-shape': 'triangle',
      'line-color': '#aaa',
      'target-arrow-color': '#aaa',
      'opacity': 0.5
    }
  }
]

export function LinksGraph(props: LinksGraphProps) {

  let endpoint = '/api/v1/links?include_external=true&include_invalid=true';
  if (props.notePath) {
    endpoint += '&note=' + props.notePath;
  }

  const { data: linksData } =
    useQuery<GetLinksResponse, Error>(['links', { path: props.notePath }], () =>
    fetch(endpoint).then(res =>
      res.json()
    )
  )

  const cyRef = useRef<Cytoscape.Core>();

  useEffect(
    () => {
      if (cyRef.current === undefined) return

      // Set up click events so that they act as links to the linked notes
      cyRef.current.on('tap', 'node', function(evt) {
        let fullPath: string = evt.target.id();
        let viewURL: string;

        // eslint-disable-next-line
        if (evt.target.data('nodeType') == 'internal') {
          viewURL = '/view?path=' + fullPath;

        // eslint-disable-next-line
        } else if (evt.target.data('nodeType') == 'invalid') {
          return;

        } else {
          viewURL = fullPath;
        }

        window.open(viewURL, '_blank')?.focus();
      });
    },
    [linksData, props.notePath]
  )

  if (!linksData) {
    return <div>No Links Data</div>
  }

  const [linkElements, maxHeight] = transformLinks(linksData, props.notePath);

  // maxHeight will be set to 0 if there is no note specified (because you are viewing all links)
  const layout = maxHeight ?
    {name: 'elk', elk: {algorithm: 'elk.layered', 'elk.direction': 'RIGHT'}} :
    {name: 'elk', elk: {algorithm: 'elk.stress'}}

  return  (
    <StyledCytoscapeComponent
      maxHeight={maxHeight}
      elements={linkElements}
      stylesheet={baseStyle}
      layout={layout}
      userZoomingEnabled={maxHeight ? false : true}
      userPanningEnabled={maxHeight ? false : true}
      cy={(cy): void => {
        cyRef.current = cy;
      }}
    />
  )
}

// -------------------
// ----- Helpers -----
// -------------------

type RawNode = {
  name: string,
  internal: boolean,
  valid: boolean
}

type LinkEdge = {
  data: {
    id: string,
    source: string,
    target: string
  }
}

type FormattedNode = {
  data: {
    id: string,
    label: string,
    color: string,
    nodeType: string
  }
}

type CytoscapeElements = Array<FormattedNode | LinkEdge>;

function transformLinks(linksData: GetLinksResponse, filePath?: string): [CytoscapeElements, number] {

  let nodes: Array<RawNode> = [];
  let edges: Array<LinkEdge> = [];
  let elements: CytoscapeElements = [];

  // Populate raw list of node names and edges
  for (const [index, link] of linksData.entries()) {
    let source: RawNode = {
      name: removeInternalLinkSections(link.source),
      internal: true,
      valid: true,
    }
    let target: RawNode = {
      name: removeInternalLinkSections(link.target),
      internal: link.internal,
      valid: link.valid
    }
    if (!nodes.includes(source)) {
      nodes.push(source);
    }
    if (!nodes.includes(target)) {
      nodes.push(target);
    }
    let edge: LinkEdge = {
      data: {
        id: 'link-' + index,
        source: source.name,
        target: target.name
      }
    }
    edges.push(edge);
  }

  // Calculate max height (in units of links)
  // Deduplicate list of objects https://stackoverflow.com/a/36744732
  const uniqueEdges = edges.filter((value, index, self) =>
    index === self.findIndex((t) => (
      t.data.source === value.data.source && t.data.target === value.data.target
    ))
  )
  let maxHeightSrc = 0;
  let maxHeightTgt = 0;
  if (filePath) {
    for (const edge of uniqueEdges) {
      if (edge.data.source.includes(filePath)) {
        maxHeightSrc += 1;
      } else if (edge.data.target.includes(filePath)) {
        maxHeightTgt += 1;
      };
    }
  }
  const maxHeight = Math.max(maxHeightSrc, maxHeightTgt);

  // Re-format nodes into the format the libarary needs
  for (const node of nodes) {
    const fullPath = node.name;
    const splitpath = fullPath.split('/');
    let filename = splitpath[splitpath.length - 1];
    let nodeColor = "#508ef2";
    let nodeType = 'internal';
    if (!node.internal) {
      nodeColor = "#70e094";
      nodeType = 'external';
      filename = decodeURI(fullPath).replace(/^https?:\/\//, '');
    }
    if (!node.valid) {
      nodeColor = '#c91a0a';
      nodeType = 'invalid';
    }
    const formattedNode: FormattedNode = {
      data: {
        id: node.name,
        label: filename,
        color: nodeColor,
        nodeType: nodeType
      }
    }
    elements.push(formattedNode);
  }

  return [elements.concat(edges), maxHeight]
}


function removeInternalLinkSections(linkTarget: string) {
  if (linkTarget.startsWith("http://") || linkTarget.startsWith("https://")) {
    return linkTarget;
  } else {
    if (linkTarget.includes('#')) {
      return linkTarget.split('#')[0];
    } else {
      return linkTarget;
    }
  }
}
