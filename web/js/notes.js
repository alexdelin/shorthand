function getTagsElements(tags) {
    var tagElement = ' '
    _.each(tags, function (tag) {
        tagElement = tagElement + '<span class="badge badge-secondary">' + tag + '</span>';
    });
    return tagElement
}

function getTodoElement(text, filePath, displayPath, startDate, endDate, line, tags, idx) {
    return '<tr><td class="todoText"><div id="todo-' + idx + '">' + text + getTagsElements(tags) +
           '</div></td><td class="filePath" path="' + filePath + '">' +
           '<a href="/render?path=' + filePath + '">' + displayPath + '</a>' +
           '</td><td>' + startDate +
           '</td><td>' + endDate +
           '</td><td class="lineNumber">' + line +
           '</td><td class="actionButtons">' +
                '<span class="getContext"><i class="material-icons action-button">search</i></span> ' +
                '<span class="markComlete"><i class="material-icons action-button">check_box</i></span> ' +
                '<span class="markSkipped"><i class="material-icons action-button">skip_next</i></span> ' +
                '<span class="editContent"><i class="material-icons action-button">edit</i></span>' +
           '</td></tr>'
}

function setResultActions(resultType) {
    // Wire up show context button
    $(".getContext").click(function(ev) {
        console.log('Showing Context')
        rowElement = ev.currentTarget.parentElement.parentElement
        filePath = $(rowElement).find('.filePath')[0].innerText
        lineNumber = $(rowElement).find('.lineNumber')[0].innerText
        var contextElement = '<pre><code class="markdown">'
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
            contextElement += '</code></pre>'
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
            todoFile = $(rowElement).find('.filePath')[0].getAttribute('path')
            todoLine = $(rowElement).find('.lineNumber')[0].innerText
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
            todoFile = $(rowElement).find('.filePath')[0].getAttribute('path')
            todoLine = $(rowElement).find('.lineNumber')[0].innerText
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

function setCount(count) {
    $('#resultCount')[0].innerHTML = count
}

function renderTodoResults(todoData) {
    // Set visibility of results containers
    $('#todoList')[0].innerHTML = ''
    $('#searchContent')[0].style.display = 'none'
    $('#todoContent')[0].style.display = 'block'
    $('#questionContent')[0].style.display = 'none'

    // Render new results
    var loadedData = JSON.parse(todoData)
    var todoListElement = ''
    var todoIdx = 1
    _.each(loadedData['items'], function(todoResult) {
        var text = todoResult['todo_text']
        var filePath = todoResult['file_path']
        var displayPath = todoResult['display_path']
        var startDate = todoResult['start_date']
        var endDate = todoResult['end_date']
        var line = todoResult['line_number']
        var tags = todoResult['tags']
        var newRowElement = getTodoElement(text, filePath, displayPath, startDate, endDate, line, tags, todoIdx)
        todoListElement = todoListElement + newRowElement
        todoIdx = todoIdx + 1
    })
    $('#todoList').append(todoListElement)
    // Update count of todos returned
    setCount(loadedData['count'])
    // Wire up actions for button on each todo
    setResultActions('todo')
    // Render markdown in todos returned
    _.each($('.todoText'), function (elem) {
        console.log(elem);
        var todoMd = $(elem).find('div')[0].innerHTML
        var targetElem = $(elem).find('div')[0]
        const tm = texmath.use(katex);
        md = markdownit({html:true}).use(tm,{delimiters:'dollars',macros:{"\\RR": "\\mathbb{R}"}});
        targetElem.innerHTML = md.render(todoMd);
    });
}

$("#stampNotes").click(function() {
    console.log( "Handler for stamp notes called." );
    $.get('stamp', {},
        function(responseData){
            alert('Stamped Notes!')
    });
});

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

function renderQuestionResults(questionData) {
    // Set visibility of results containers
    $('#questionList')[0].innerHTML = ''
    $('#searchContent')[0].style.display = 'none'
    $('#todoContent')[0].style.display = 'none'
    $('#questionContent')[0].style.display = 'block'

    // Render new results
    var loadedData = JSON.parse(questionData)
    var questionResultElement = ''
    _.each(loadedData['items'], function(questionResult) {
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
    setCount(loadedData['count'])
    setResultActions('question')
}

// Set up Typeahead
var searchNotes = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  remote: {
    url: '/typeahead?query=%QUERY',
    wildcard: '%QUERY'
  }
});

$('.typeahead').typeahead(null, {
  name: 'search-notes',
  source: searchNotes
});

function setDropdownViz(menu) {

    var newValue = $('#' + menu)[0].value;
    var todoFilter = $('#todoType')[0];
    var questionFilter = $('#questionType')[0];

    if (menu === 'resultType') {
        if (newValue === 'To-Dos') {
            // Show options for ToDos
            questionFilter.style.display = "none";
            todoFilter.style.display = "block";
        } else if (newValue === 'Questions') {
            // Show options for Questions
            questionFilter.style.display = "block";
            todoFilter.style.display = "none";
        } else if (newValue === 'Everything') {
            // Show options for Everything
            questionFilter.style.display = "none";
            todoFilter.style.display = "none";
        }
    }
}

$("#masterSearch").click(function() {
    console.log('Master Search clicked!')

    // Dropdown filter elements
    var resultFilter = $('#resultType')[0].value;
    var todoFilter = $('#todoType')[0].value;
    var questionFilter = $('#questionType')[0].value;
    var directoryFilter = $('#directoryFilter')[0].value;
    var searchFilter = $('#searchFilter')[0].value
    var tagFilter = $('#tagFilter')[0].value

    if (resultFilter === 'Everything') {
        // Do a full-text search
        console.log('searching Everything');
        $.get('search', {query_string: searchFilter},
            function(searchData){
                renderSearchResults(searchData)
        });
    } else if (resultFilter === 'To-Dos') {
        // Search To-Dos
        console.log('searching To-Dos');
        $.get('get_todos',
            {
                status: todoFilter,
                directory_filter: directoryFilter,
                query_string: searchFilter,
                sort_by: 'start_date',
                tag: tagFilter
            },
            function(todoData){
                renderTodoResults(todoData)
        });
    } else if (resultFilter === 'Questions') {
        // Search Questions
        console.log('searching Questions');
        $.get('get_questions',
            {
                status: questionFilter,
                directory_filter: directoryFilter
            },
            function(questionData){
                renderQuestionResults(questionData)
        });
    } else {
        // Should never get here
        alert('Something went wrong!');
    }

});


