import { useRef, useEffect } from 'react';
import { useQuery } from 'react-query';
import Cytoscape from 'cytoscape';
import klay from 'cytoscape-klay';
import CytoscapeComponent from 'react-cytoscapejs';


Cytoscape.use(klay);

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
  notePath: string | null
}

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

  const { data: linksData } =
    useQuery<GetLinksResponse, Error>(['links', { path: props.notePath }], () =>
    fetch('http://localhost:8181/api/v1/links?note=' + props.notePath +
          '&include_external=true&include_invalid=true').then(res =>
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

  if (props.notePath === null || linksData === undefined) {
    return <div>No Links Data</div>
  }

  const [linkElements, maxHeight] = transformLinks(linksData, props.notePath);

  return  (
    <CytoscapeComponent
      elements={linkElements}
      style={{ width: '100%', height: maxHeight * 7 + 'rem' }}
      stylesheet={baseStyle}
      layout={{name: 'klay'}}
      userZoomingEnabled={false}
      userPanningEnabled={false}
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

function transformLinks(linksData: GetLinksResponse, filePath: string): [CytoscapeElements, number] {

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
    for (const edge of uniqueEdges) {
        if (edge.data.source.includes(filePath)) {
            maxHeightSrc += 1;
        } else if (edge.data.target.includes(filePath)) {
            maxHeightTgt += 1;
        };
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
