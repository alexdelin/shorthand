document.addEventListener('DOMContentLoaded', function() {

    var map = L.map('shorthand-map').setView([40.758, -73.985], 7);

    // OSM Tiles
    // L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    //     attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    // }).addTo(map);
    // Google Maps Tiles
    L.tileLayer('http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',{
        maxZoom: 20,
        subdomains:['mt0','mt1','mt2','mt3']
    }).addTo(map);

    $.ajax({
        url: '/api/v1/locations',
        type: 'GET',
        success: function(responseData) {
            loadedResponse = JSON.parse(responseData);
            console.log(loadedResponse);
            for (var i = loadedResponse.items.length - 1; i >= 0; i--) {

                var locLat = loadedResponse.items[i]['latitude']
                var locLon = loadedResponse.items[i]['longitude']
                var locName = loadedResponse.items[i]['name']
                var locPath = loadedResponse.items[i]['file_path']
                var locDisp = loadedResponse.items[i]['display_path']
                var locLine = loadedResponse.items[i]['line_number']

                var popupHtml = `${locName}<br /><br />
                                <a target="_blank" href="/render?path=${locPath}#line-number-${locLine}">
                                    ${locDisp}
                                </a><br /><br />
                                <a target="_blank" href="https://www.google.com/maps/place/${locLat},${locLon}">Google Link</a>`

                L.marker([loadedResponse.items[i]['latitude'], loadedResponse.items[i]['longitude']]).addTo(map)
                    .bindPopup(popupHtml)
                    .openPopup();
            }
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText);
            showModal(loadedResponse.error);
        }
    });

});
