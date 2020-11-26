// Wire click events for show / hide TOC button
$("#showTOC").click(function(){
  $(".toc-content").toggleClass("hidden");
});

// Render tables with record sets
$(document).ready(function() {

    _.each($('.record-set-table'), function (tableElement) {
        console.log(tableElement);
        var jsonString = $(tableElement.parentElement).find('.record-set-data')[0].innerText;
        console.log(jsonString)
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

});

hljs.initHighlightingOnLoad();
