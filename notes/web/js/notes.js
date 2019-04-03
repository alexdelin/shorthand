function getTodoElement(text, file, startDate, endDate, line) {
    return '<tr><td class="todoText">' + text +
           '</td><td class="filePath">' + file +
           '</td><td>' + startDate +
           '</td><td>' + endDate +
           '</td><td class="lineNumber">' + line +
           '</td><td class="actionButtons">' +
                '<span class="getContext">🔎</span> ' +
                '<span class="markComlete">✅</span> ' +
                '<span class="markSkipped">⏭</span> ' +
                '<span class="editContent">✏️</span>' +
           '</td></tr>'
}

function setResultActions(resultType) {
    // Wire up show context button
    $(".getContext").click(function(ev) {
        console.log('Showing Context')
        rowElement = ev.currentTarget.parentElement.parentElement
        filePath = $(rowElement).find('.filePath')[0].innerText
        lineNumber = $(rowElement).find('.lineNumber')[0].innerText
        var contextElement = '<pre>'
        $.get('get_context', {filename: filePath, line_number: lineNumber}, function(contextResponse) {
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
            if (resultType == 'todo') {
                $(rowElement).find('.todoText')[0].innerHTML = contextElement
            } else if (resultType == 'search') {
                $(rowElement).find('.searchResult')[0].innerHTML = contextElement
            } else if (resultType == 'question') {
                $(rowElement).find('.questionText')[0].innerHTML = contextElement
            }
        });
    });

    if (resultType == 'todo') {
        // Wire up mark complete button
        $(".markComlete").click(function(ev) {
            console.log('Marking Complete')
            rowElement = ev.currentTarget.parentElement.parentElement
            todoFile = $(rowElement).find('.filePath')[0].innerText
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
            todoFile = $(rowElement).find('.filePath')[0].innerText
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
}

function fetchTodos(status) {
    console.log( "Handler for refresh content called." );
    $('#searchContent')[0].style.display = 'none'
    $('#todoContent')[0].style.display = 'block'
    $('#questionContent')[0].style.display = 'none'

    $('#todoList')[0].innerHTML = ''
    var directoryFilter = $('#directoryFilter')[0].value
    console.log(directoryFilter)
    $.get('get_todos', {status: status, directory_filter: directoryFilter},
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
            setResultActions('todo')
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

$("#stampNotes").click(function() {
    console.log( "Handler for stamp notes called." );
    $.get('stamp', {},
        function(responseData){
            alert('Stamped Notes!')
    });
});

$("#searchSubmit").click(function() {

    console.log( "Handler for search submit called." );
    $('#searchContent')[0].style.display = 'block'
    $('#todoContent')[0].style.display = 'none'
    $('#questionContent')[0].style.display = 'none'

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
                var newRowElement = '<tr><td class="searchResult">' + text +
                                    '</td><td class="filePath">' + file +
                                    '</td><td class="lineNumber">' + line +
                                    '</td><td class="actionButtons">' +
                                        '<span class="getContext">🔎</span> ' +
                                    '</td></tr>'
                searchResultElement = searchResultElement + newRowElement
            })
            $('#searchResults').append(searchResultElement)
            setResultActions('search')
    });
});

function fetchQuestions(status) {
    console.log( "Handler for search submit called." );
    $('#searchContent')[0].style.display = 'none'
    $('#todoContent')[0].style.display = 'none'
    $('#questionContent')[0].style.display = 'block'

    $('#questionList')[0].innerHTML = ''
    var directoryFilter = $('#directoryFilter')[0].value

    $.get('get_questions', {status: status, directory_filter: directoryFilter},
        function(questionData){
            var loadedData = JSON.parse(questionData)
            var questionResultElement = ''
            _.each(loadedData, function(questionResult) {
                var text = questionResult['question']
                var file = questionResult['file_path']
                var line = questionResult['line_number']
                var answer = questionResult['answer']
                var newRowElement = '<tr><td class="questionText">' + text +
                                    '</td><td class="filePath">' + file +
                                    '</td><td class="lineNumber">' + line +
                                    '</td><td>' + answer +
                                    '</td><td class="actionButtons">' +
                                        '<span class="getContext">🔎</span> ' +
                                    '</td></tr>'
                questionResultElement = questionResultElement + newRowElement
            })
            $('#questionList').append(questionResultElement)
            setResultActions('question')
    });
};

$("#fetchAll").click(function() {
    fetchQuestions('all')
});

$("#fetchAnswered").click(function() {
    fetchQuestions('answered')
});

$("#fetchUnanswered").click(function() {
    fetchQuestions('unanswered')
});

// Set up Typeahead
var searchNotes = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  // prefetch: '/typeahead/films/post_1960.json',
  remote: {
    url: '/typeahead?query=%QUERY',
    wildcard: '%QUERY'
  }
});

$('.typeahead').typeahead(null, {
  name: 'search-notes',
  // display: 'value',
  source: searchNotes
});
