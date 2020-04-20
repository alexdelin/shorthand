// Build an HTML element for a todo result from its properties
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

// Click handler for the todo search button
$("#todoSearch").click(function() {
    console.log('Todo Search clicked!')

    // Dropdown filter elements
    var todoFilter = $('#todoType')[0].value;
    var directoryFilter = $('#directoryFilter')[0].value;
    var searchFilter = $('#searchFilter')[0].value
    var tagFilter = $('#tagFilter')[0].value

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
});

// Render todo results from the raw API response (as a string)
function renderTodoResults(todoData) {
    // Clear old todos
    $('#todoList')[0].innerHTML = ''

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
    setTodoResultActions()
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

// Wire up action buttons on results
function setTodoResultActions() {

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
