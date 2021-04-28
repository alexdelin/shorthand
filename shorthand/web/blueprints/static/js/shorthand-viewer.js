// Wire click events for show / hide TOC button
$("#showTOC").click(function(){
  $(".toc-content").toggleClass("hidden");
});

// Fetch current note content via the API and render it
function renderNote() {
    // Get rendered markdown from the frontend API
    var filePath = $('#meta-file-path').text()

    $.ajax({
        url: '/frontend-api/redered-markdown?' + $.param({path: filePath}),
        type: 'GET',
        success: function(noteContent) {
            console.log(noteContent)
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

            out.innerHTML = md.render(noteContent);

            // Draw record sets & set up maps for locations
            PostNoteRender();

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
