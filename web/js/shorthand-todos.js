// Build an HTML element for a todo result from its properties
function getTodoElement(text, filePath, displayPath, startDate, endDate, line, tags, idx) {
    return '<tr><td class="todoText"><div id="todo-' + idx + '">' + text + getTagsElements(tags) +
           '</div></td><td class="filePath" path="' + filePath + '">' +
           '<a href="/render?path=' + filePath + '#line-number-' + line + '">' + displayPath + '</a>' +
           '</td><td>' + startDate +
           '</td><td>' + endDate +
           '</td><td class="lineNumber">' + line +
           '</td><td class="actionButtons">' +
                '<span class="getContext"><img src="/img/eye-24.svg"></span> ' +
                '<span class="markComlete"><img src="/img/check-circle-24.svg"></span> ' +
                '<span class="markSkipped"><img src="/img/skip-24.svg"></span> ' +
                '<span class="editContent"><img src="/img/pencil-24.svg"></span>' +
           '</td></tr>'
}

// Click handler for the todo search button
$("#todoSearch").click( function() {
    console.log('Todo Search clicked!')

    // Dropdown filter elements
    var todoFilter = $('#todoType')[0].value;
    var directoryFilter = $('#directoryFilter')[0].value;
    var searchFilter = $('#searchFilter')[0].value
    var tagFilter = $('#tagFilter')[0].value

    // Search To-Dos
    console.log('searching To-Dos');
    $.ajax({
        url: '/api/v1/todos',
        type: 'GET',
        data: {
            status: todoFilter,
            directory_filter: directoryFilter,
            query_string: searchFilter,
            sort_by: 'start_date',
            tag: tagFilter
        },
        success: function(todoData) {
            renderTodoResults(todoData)
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
});

// Render todo results from the raw API response (as a string)
function renderTodoResults(todoData) {
    // Clear old todos
    $('#todoList').html('')

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
        var todoMd = $(elem).find('div')[0].innerHTML
        var targetElem = $(elem).find('div')[0]
        const tm = texmath.use(katex);
        md = markdownit({html:true}).use(tm,{delimiters:'dollars',macros:{"\\RR": "\\mathbb{R}"}});
        targetElem.innerHTML = md.render(todoMd);
    });

    // Render the month timeline
    console.log(loadedData['meta']['timeline_data'])
    Highcharts.chart('timelineChart', {
        chart: {type: 'column'},
        title: {text: 'Todo Age'},
        subtitle: {text: 'Distribution of Todos by creation date'},
        tooltip: {valueDecimals: 2},
        xAxis: {type: 'datetime'},
        series: [{
            data: loadedData['meta']['timeline_data'],
            lineWidth: 1,
            name: 'Todos per month'
        }]
    });

    // Transform data for tag pie chart
    var tagSeriesData = [];
    _.each(_.keys(loadedData['meta']['tag_counts']), function(tag){
        tagSeriesData.push({
            name: tag,
            y: loadedData['meta']['tag_counts'][tag]
        })
    })

    // Render the tag pie chart
    Highcharts.chart('tagChart', {
        chart: {type: 'pie'},
        title: {text: 'Tags'},
        tooltip: {pointFormat: 'Todos: <b>{point.y}</b>'},
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.y}'
                }
            }
        },
        series: [{
            data: tagSeriesData,
            name: 'Todos per tag',
            events: {
                click: function (event) {
                    // Get the name of the clicked data point
                    var tagValue = event.point.name;
                    // Get the current tag filter value from the dropdown
                    var currentTag = $('#tagFilter').val();
                    if (currentTag == tagValue) {
                        // If you clicked on a tag that is already selected
                        // as the filter, clear the tag filter
                        $('#tagFilter').val('ALL');
                    } else {
                        // If you clicked on a tag that is not currently selected
                        // for filtering, set the value of the tag dropdown to be
                        // the clicked tag
                        $('#tagFilter').val(tagValue);
                    }
                    // Refresh the search results
                    $('#todoSearch').click();
                }
            }
        }]
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
        $.ajax({
            url: '/api/v1/context',
            type: 'GET',
            data: {
                filename: filePath,
                line_number: lineNumber
            },
            success: function(contextResponse) {
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
            },
            error: function(responseData) {
                var loadedResponse = JSON.parse(responseData.responseText)
                showModal(loadedResponse.error)
            }
        });
    });

    // Wire up mark complete button
    $(".markComlete").click(function(ev) {
        console.log('Marking Complete');
        rowElement = ev.currentTarget.parentElement.parentElement;
        todoFile = $(rowElement).find('.filePath')[0].getAttribute('path');
        todoLine = $(rowElement).find('.lineNumber')[0].innerText;
        $.ajax({
            url: '/api/v1/mark_todo',
            type: 'GET',
            data: {
                filename: todoFile,
                line_number: todoLine,
                status: 'complete'
            },
            success: function(markTodoResponse) {
                $("#todoSearch").click();
            },
            error: function(responseData) {
                var loadedResponse = JSON.parse(responseData.responseText)
                showModal(loadedResponse.error)
            }
        });
    });

    // Wire up mark skipped button
    $(".markSkipped").click(function(ev) {
        console.log('Marking Skipped')
        rowElement = ev.currentTarget.parentElement.parentElement
        todoFile = $(rowElement).find('.filePath')[0].getAttribute('path')
        todoLine = $(rowElement).find('.lineNumber')[0].innerText
        $.ajax({
            url: '/api/v1/mark_todo',
            type: 'GET',
            data: {
                filename: todoFile,
                line_number: todoLine,
                status: 'skipped'
            },
            success: function(contextResponse) {
                $("#todoSearch").click();
            }
        });
    });

    // Wire up edit button
    $(".editContent").click(function() {
        console.log('Editing Context')
    });

}

// Click handler for the show stats button
$("#showStats").click( function() {
    console.log('Show Stats clicked!')
    $('#statsContainer').toggleClass('hidden')
});
