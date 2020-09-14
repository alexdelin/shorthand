function renderSearchResults(searchData) {
    // Set visibility of results containers
    $('#searchResults')[0].innerHTML = ''
    $('#searchContent')[0].style.display = 'block'
    $('#todoContent')[0].style.display = 'none'
    $('#questionContent')[0].style.display = 'none'

    // Render new results
    var loadedData = JSON.parse(searchData)
    var searchResultElement = ''
    _.each(loadedData['items'], function(searchResult) {
        var text = searchResult['match_content']
        var file = searchResult['file_path']
        var line = searchResult['line_number']
        var newRowElement = '<tr><td class="searchResult">' + text +
                            '</td><td class="filePath">' + file +
                            '</td><td class="lineNumber">' + line +
                            '</td><td class="actionButtons">' +
                                '<span class="editButton">Edit - Placeholder</span> ' +
                            '</td></tr>'
        searchResultElement = searchResultElement + newRowElement
    })
    $('#searchResults').append(searchResultElement)
    setCount(loadedData['count'])
    setResultActions('search')
}

function showFileFinder() {
    $('#shorthandFileModal').modal();
    var taTest = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/api/v1/files?query_string=%QUERY',
            wildcard: '%QUERY'
        }
    });

    $('#fileModalSearchBar').typeahead(null, {
        name: 'notes-files',
        highlight: true,
        limit: 10,
        source: taTest,
    });

    // Click Handler for the goto note button
    $("#goToNote").click( function() {
        console.log('Go To Note clicked!');
        var notePath = $('#fileModalSearchBar').val();
        // Log the file view
        $.ajax({
            url: '/api/v1/record_view?' + $.param({relative_path: notePath}),
            type: 'POST',
            success: function(responseData) {
                if (responseData == 'ack') {
                    window.location.href = '/render?path=' + notePath;
                }
            },
            error: function(responseData) {
                var loadedResponse = JSON.parse(responseData.responseText)
                showModal(loadedResponse.error)
            }
        });
    });

    // Set the focus to the search bar after the modal is actually visible
    $('#shorthandFileModal').on('shown.bs.modal', function (e) {
        $('#fileModalSearchBar').focus();
    })

    // Handler for the enter key
    // from https://stackoverflow.com/a/7060762
    $("#fileModalSearchBar").on('keyup', function (e) {
        if (e.key === 'Enter' || e.keyCode === 13) {
            $('#goToNote').click();
        }
    });

};

// From https://stackoverflow.com/a/16006607
function KeyPress(e) {
    var evtobj = window.event? event : e
    if (evtobj.keyCode == 84 && evtobj.ctrlKey) {
        showFileFinder();
    };
}
document.onkeydown = KeyPress;
