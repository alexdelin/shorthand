// Build an HTML element for a question result from its properties
function getDefinitionElement(term, file, display, line, definition) {
    return '<tr><td class="termText">' + term +
           '</td><td><span class="filePath" style="display: none;">' +
           file + '</span>' + '<a href="/render?path=' + file + '">' +
           display + '</a>' + '</td><td class="lineNumber">' + line +
           '</td><td>' + definition +
           '</td><td class="actionButtons">' +
               '<span class="getContext">🔎</span> ' +
           '</td></tr>';
};

// Click handler for the definition search button
$("#definitionSearch").click(function() {
    console.log('Definitions Search clicked!')

    // Dropdown filter elements
    var directoryFilter = $('#directoryFilter')[0].value;
    var searchFilter = $('#searchFilter')[0].value
    var tagFilter = $('#tagFilter')[0].value

    // Search Definitions
    console.log('searching Definitions');
    $.ajax({
        url: 'get_definitions',
        type: 'GET',
        data: {
            directory_filter: directoryFilter
        },
        success: function(definitionData){
            renderDefinitionResults(definitionData)
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            renderError(loadedResponse.error)
        }
    });
});

// Render definition results from an API response as a string
function renderDefinitionResults(definitionData) {
    // Set visibility of results containers
    $('#definitionList')[0].innerHTML = '';

    // Render new results
    var loadedData = JSON.parse(definitionData);
    var definitionResultElement = '';
    _.each(loadedData['items'], function(definitionResult) {
        var term = definitionResult['term'];
        var file = definitionResult['file_path'];
        var display = definitionResult['display_path'];
        var line = definitionResult['line_number'];
        var definition = definitionResult['definition'];
        var newRowElement = getDefinitionElement(term, file, display, line, definition)
        definitionResultElement = definitionResultElement + newRowElement;
    });
    $('#definitionList').append(definitionResultElement);
    setCount(loadedData['count']);
};
