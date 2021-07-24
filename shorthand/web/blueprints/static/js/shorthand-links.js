$(document).ready(function() {
    renderLinks();
    // Re-draw the links whenever the External Links switch is changed
    $("#toggleExtLinks").change(function () {
        renderLinks();
    });
});

function renderLinks() {
    console.log('rendering Links')
    var includeExternalLinks = $('#toggleExtLinks').is(":checked")

    $.ajax({
        url: '/api/v1/links?' + $.param({
            include_external: includeExternalLinks,
            include_invalid: true}),
        type: 'GET',
        success: function(linksContent) {

            if (linksContent == '[]') {

                $('#links').html('<h3>No links Found</h3>')

            } else {

                var [linkElements, maxHeight] = transformLinks(linksContent);
                // $('#links').height(maxHeight * 100 + 'px');
                var cy = cytoscape({
                    container: document.getElementById('links'),
                    elements: linkElements,
                    userZoomingEnabled: false,
                    userPanningEnabled: false,
                    style: [
                        {
                            selector: 'node',
                            style: {
                                'background-color': 'data(color)',
                                "label": "data(label)",
                                "text-valign": "bottom",
                                "text-halign": "center",
                                "font-size": "5px"
                            }
                        },
                        {
                            selector: 'edge',
                            style: {
                                'curve-style': 'bezier',
                                'target-arrow-shape': 'triangle',
                                'line-color': '#aaa',
                                'target-arrow-color': '#aaa',
                                'opacity': 0.5
                            }
                        }
                    ],
                    layout: {
                        name: 'klay'
                    }
                });

                // Set up click events so that they act as links to the linked notes
                cy.on('tap', 'node', function(evt) {
                    var fullPath = evt.target.id();

                    if (evt.target.data('nodeType') == 'internal') {
                        var viewURL = '/render?path=' + fullPath;
                    } else if (evt.target.data('nodeType') == 'invalid') {
                        return;
                    } else {
                        var viewURL = fullPath;
                    }
                    window.open(viewURL, '_blank').focus();
                });
            }
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
}

function transformLinks(linksContent) {
    linksContent = JSON.parse(linksContent);

    var nodes = [];
    var formattedNodes = [];
    var edges = [];

    // Populate raw list of node names and edges
    for (var i = linksContent.length - 1; i >= 0; i--) {
        var source = {
            name: removeInternalLinkSections(linksContent[i].source),
            internal: true,
            valid: true,
        }
        var target = {
            name: removeInternalLinkSections(linksContent[i].target),
            internal: linksContent[i].internal,
            valid: linksContent[i].valid
        }
        if (!nodes.includes(source)) {
            nodes.push(source);
        }
        if (!nodes.includes(target)) {
            nodes.push(target);
        }
        var edge = {
            data: {
                id: 'link-' + i,
                source: source.name,
                target: target.name
            }
        }
        edges.push(edge);
    }

    // Calculate max height (in units of links)
    var filePath = $('#meta-file-path').text();
    var maxHeightSrc = 0;
    var maxHeightTgt = 0;
    for (var i = edges.length - 1; i >= 0; i--) {
        console.log(edges[i]["data"]["source"]);
        console.log(edges[i]["data"]["target"]);
        if (edges[i]["data"]["source"].includes(filePath)) {
            maxHeightSrc += 1;
        } else if (edges[i]["data"]["target"].includes(filePath)) {
            maxHeightTgt += 1;
        };
    }
    var maxHeight = Math.max(maxHeightSrc, maxHeightTgt);

    // Re-format nodes into the format the libarary needs
    for (var i = nodes.length - 1; i >= 0; i--) {
        var fullPath = nodes[i]["name"];
        var splitpath = fullPath.split('/');
        var filename = splitpath[splitpath.length - 1];
        var nodeColor = "#508ef2";
        var nodeType = 'internal'
        if (!nodes[i]["internal"]) {
            nodeColor = "#70e094";
            nodeType = 'external';
            filename = decodeURI(fullPath).replace(/^https?:\/\//, '');
        }
        if (!nodes[i]["valid"]) {
            nodeColor = '#c91a0a';
            nodeType = 'invalid';
        }
        formattedNodes.push({
            data: {
                id: nodes[i]["name"],
                label: filename,
                color: nodeColor,
                nodeType: nodeType
            }
        });
    }

    return [formattedNodes.concat(edges), maxHeight]
}

function removeInternalLinkSections(linkTarget) {
    if (linkTarget.startsWith("http://") || linkTarget.startsWith("https://")) {
        return linkTarget
    } else {
        if (linkTarget.includes('#')) {
            return linkTarget.split('#')[0]
        } else {
            return linkTarget
        }
    }
}
