$("#refreshContent").click(function() {

    console.log( "Handler for refresh content called." );
    $('#todoList')[0].innerHTML = ''

    $.get('get_todos', {status: "incomplete"},
        function(todoData){
            var loadedData = JSON.parse(todoData)
            var todoListElement = ''
            _.each(loadedData, function(todoResult) {
                var text = todoResult['todo_text']
                var file = todoResult['file_path']
                var startDate = todoResult['start_date']
                var endDate = todoResult['end_date']
                var line = todoResult['line_number']
                var newRowElement = '<tr><td>' + text + '</td><td>' + file + '</td><td>' + startDate + '</td><td>' + endDate + '</td><td>' + line + '</td></tr>'
                todoListElement = todoListElement + newRowElement
            })
            $('#todoList').append(todoListElement)
    });
});


$("#searchSubmit").click(function() {

    console.log( "Handler for search submit called." );
    $('#searchResults')[0].innerHTML = ''
    var queryString = $('#searchQuery')[0].value

    $.get('search', {query_string: queryString},
        function(searchData){
            var loadedData = JSON.parse(searchData)
            var searchResultElement = ''
            _.each(loadedData, function(searchResult) {
                var text = searchResult['match_content']
                var file = searchResult['file_path']
                var line = searchResult['line_number']
                var newRowElement = '<tr><td>' + text + '</td><td>' + file + '</td><td>' + line + '</td></tr>'
                searchResultElement = searchResultElement + newRowElement
            })
            $('#searchResults').append(searchResultElement)
    });
});
