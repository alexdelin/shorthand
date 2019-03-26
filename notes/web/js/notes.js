function getTodoElement(text, file, startDate, endDate, line) {
    return '<tr><td class="todoText">' + text +
           '</td><td class="todoFile">' + file +
           '</td><td>' + startDate +
           '</td><td>' + endDate +
           '</td><td class="todoLine">' + line +
           '</td><td class="actionButtons">' +
                '<span class="getContext">🔎</span> ' +
                '<span class="markComlete">✅</span> ' +
                '<span class="markSkipped">⏭</span> ' +
                '<span class="editContent">✏️</span>' +
           '</td></tr>'
}

function setResultActions() {
    // Wire up show context button
    $(".getContext").click(function(ev) {
        console.log('Showing Context')
        rowElement = ev.currentTarget.parentElement.parentElement
        todoFile = $(rowElement).find('.todoFile')[0].innerText
        todoLine = $(rowElement).find('.todoLine')[0].innerText
        var contextElement = '<pre>'
        $.get('get_context', {filename: todoFile, line_number: todoLine}, function(contextResponse) {
            var loadedContext = JSON.parse(contextResponse)
            console.log(loadedContext)
            _.each(loadedContext['before'], function (beforeLine) {
                contextElement += beforeLine + '\n'
            });
            contextElement += loadedContext['line'] + '\n'
            _.each(loadedContext['after'], function (afterLine) {
                contextElement += afterLine + '\n'
            });
            contextElement += '</pre>'
            console.log(contextElement)
            $(rowElement).find('.todoText')[0].innerHTML = contextElement
        });
    });

    // Wire up mark complete button
    $(".markComlete").click(function(ev) {
        console.log('Marking Complete')
        rowElement = ev.currentTarget.parentElement.parentElement
        todoFile = $(rowElement).find('.todoFile')[0].innerText
        todoLine = $(rowElement).find('.todoLine')[0].innerText
        $.get(
            'mark_todo',
            {
                filename: todoFile,
                line_number: todoLine,
                status: 'complete'
            },
            function(contextResponse) {
                rowElement.style.display = 'none'
        });
    });

    // Wire up mark skipped button
    $(".markSkipped").click(function(ev) {
        console.log('Marking Skipped')
        rowElement = ev.currentTarget.parentElement.parentElement
        todoFile = $(rowElement).find('.todoFile')[0].innerText
        todoLine = $(rowElement).find('.todoLine')[0].innerText
        $.get(
            'mark_todo',
            {
                filename: todoFile,
                line_number: todoLine,
                status: 'skipped'
            },
            function(contextResponse) {
                rowElement.style.display = 'none'
        });
    });

    // Wire up edit button
    $(".editContent").click(function() {
        console.log('Editing Context')
    });
}

function fetchTodos(status) {
    console.log( "Handler for refresh content called." );
    $('#todoList')[0].innerHTML = ''
    $.get('get_todos', {status: status},
        function(todoData){
            var loadedData = JSON.parse(todoData)
            var todoListElement = ''
            _.each(loadedData, function(todoResult) {
                var text = todoResult['todo_text']
                var file = todoResult['file_path']
                var startDate = todoResult['start_date']
                var endDate = todoResult['end_date']
                var line = todoResult['line_number']
                var newRowElement = getTodoElement(text, file, startDate, endDate, line)
                todoListElement = todoListElement + newRowElement
            })
            $('#todoList').append(todoListElement)
            setResultActions()
    });
}

$("#fetchIncomplete").click(function() {
    fetchTodos('incomplete')
});

$("#fetchComplete").click(function() {
    fetchTodos('complete')
});

$("#fetchSkipped").click(function() {
    fetchTodos('skipped')
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
