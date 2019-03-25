$("#refreshContent").click(function() {

    console.log( "Handler for refresh content called." );
    $('#searchResults')[0].innerHTML = ''

    $.get('get_todos', {status: "incomplete"},
        function(todoData){
            var loadedData = JSON.parse(todoData)
            var todoListElement = ''
            _.each(loadedData, function(todoResult) {
                var text = todoResult['match_content']
                var file = todoResult['file_path']
                var line = todoResult['line_number']
                var newRowElement = '<tr><td>' + text + '</td><td>' + file + '</td><td>' + line + '</td></tr>'
                todoListElement = todoListElement + newRowElement
            })
            $('#searchResults').append(todoListElement)
    });
});
