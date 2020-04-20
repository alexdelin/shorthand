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
                                '<span class="getContext">🔎</span> ' +
                            '</td></tr>'
        searchResultElement = searchResultElement + newRowElement
    })
    $('#searchResults').append(searchResultElement)
    setCount(loadedData['count'])
    setResultActions('search')
}
