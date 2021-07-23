// Fetch current note content via the API and render it
function renderNote() {
    // Get rendered markdown from the frontend API
    var filePath = $('#meta-file-path').text()

    $.ajax({
        url: '/frontend-api/redered-markdown?' + $.param({path: filePath}),
        type: 'GET',
        success: function(noteContent) {
            console.log(noteContent)
            var loadedContent = JSON.parse(noteContent);
            var fileContent = loadedContent.file_content;
            var tocContent = loadedContent.toc_content;

            // Render main markdown content
            let md;
            const tm = texmath.use(katex);
            md = markdownit({
                html:true,
                highlight: function (str, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(lang, str).value;
                        } catch (__) {}
                    }

                    return ''; // use external default escaping
                }
            }).use(tm,{delimiters:'dollars',macros:{"\\RR": "\\mathbb{R}"}});

            out.innerHTML = md.render(fileContent);

            // Draw record sets & set up maps for locations
            PostNoteRender();

            // Render ToC if we have a `#toc` element on the page
            if (document.getElementById('toc')) {
                RenderToc(tocContent, md);
            }
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
}

// Render tables with record sets
function PostNoteRender() {

    _.each($('.record-set-table'), function (tableElement) {
        console.log(tableElement);
        var jsonString = $(tableElement.parentElement).find('.record-set-data')[0].innerText;
        console.log(jsonString);
        var tableData = JSON.parse(jsonString);
        console.log(tableData);
        var colString = $(tableElement).attr('data-cols');
        var columns = JSON.parse(colString);
        console.log(columns);
        $(tableElement).DataTable({
            data: tableData,
            columns: columns
        });
    });

    $('blockquote').addClass('blockquote text-center');

    for (var i = $('location').length - 1; i >= 0; i--) {
        var locationElement = $('location')[i];
        locationElement.addEventListener("click", function(ev) {

            if (typeof map !== 'undefined') {
                // Remove an old instance of the map
                // if it still exists
                map.remove();
            };

            var name = $(ev.currentTarget).find('.location-name').text();
            var lat = ev.currentTarget.getAttribute('lat');
            var lon = ev.currentTarget.getAttribute('lon');

            $('#mapModalTitle').text(name);
            $('#shorthandMapModal').modal();

            map = L.map('mapModalMap').setView([lat, lon], 11);
            L.tileLayer('http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',{
                maxZoom: 20,
                subdomains:['mt0','mt1','mt2','mt3']
            }).addTo(map);
            L.marker([lat, lon]).addTo(map);
        });
    }

    // Realign the map within the modal when the modal is shown
    // https://stackoverflow.com/a/26786149
    $('#shorthandMapModal').on('shown.bs.modal', function () {
        map.invalidateSize();
    });

    // Re-draw mermaid diagrams
    mermaid.contentLoaded();

    // Style tables properly
    $('table').addClass('table table-sm');
    $('table thead').addClass('thead-dark');
    $('table thead th').attr('scope', 'col');

    // Remove bullets from shorthand elements
    $('.todo-element').parent('li').css('list-style-type', 'none');
    $('.definition-element').parent('li').css('list-style-type', 'none');
    $('.qa-element').parent('li').css('list-style-type', 'none');

    // Scroll to element in URL if applicable
    if (window.location.hash) {
        document.getElementById(window.location.hash.substring(1)).scrollIntoView();
    }

};

// Render Table of Contents
function RenderToc(tocContent, md) {
    console.log('rendering TOC')
    toc.innerHTML = md.render(tocContent);
    // Wire click events for show / hide TOC button
    $("#showTOC").click(function(){
        $(".toc-content").toggleClass("hidden");
    });
}

$(document).ready(function() {
    // Render Links if we have a `#links` element on the page
    if (document.getElementById('links')) {
        // Wire click events for show / hide links button
        $("#showLinks").click(function(){
            $(".links-content").toggleClass("hidden");
            if ( !$(".links-content").hasClass("hidden") ) {
                renderLinks();
            }
        });
        // Re-draw the links whenever the Extnernal Links switch is changed
        $("#toggleExtLinks").change(function () {
            renderLinks();
        });
    }
});

function renderLinks() {
    console.log('rendering Links')
    var filePath = $('#meta-file-path').text()
    var includeExternalLinks = $('#toggleExtLinks').is(":checked")

    $.ajax({
        url: '/api/v1/links?' + $.param({
            note: filePath,
            include_external: includeExternalLinks,
            include_invalid: true}),
        type: 'GET',
        success: function(linksContent) {

            if (linksContent == '[]') {

                $('#links').html('<h3>No links Found</h3>')

            } else {

                var [linkElements, maxHeight] = transformLinks(linksContent);
                $('#links').height(maxHeight * 100 + 'px');
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
                        var viewURL = window.location.href.split('?')[0] + '?path=' + fullPath;
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
