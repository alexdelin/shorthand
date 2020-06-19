// Build an HTML element for a question result from its properties
function getQuestionElement(text, file, display, line, answer) {
    return '<tr><td class="questionText">' + text +
           '</td><td><span class="filePath" style="display: none;">' +
           file + '</span>' + '<a href="/render?path=' + file + '">' +
           display + '</a>' + '</td><td class="lineNumber">' + line +
           '</td><td>' + answer +
           '</td><td class="actionButtons">' +
               '<span class="getContext">🔎</span> ' +
           '</td></tr>';
};

// Click handler for the question search button
$("#questionSearch").click(function() {
    console.log('Question Search clicked!')

    // Dropdown filter elements
    var questionFilter = $('#questionType')[0].value;
    var directoryFilter = $('#directoryFilter')[0].value;
    var searchFilter = $('#searchFilter')[0].value
    var tagFilter = $('#tagFilter')[0].value

    // Search Questions
    console.log('searching Questions');
    $.ajax({
        url: '/api/v1/questions',
        type: 'GET',
        data: {
            status: questionFilter,
            directory_filter: directoryFilter
        },
        success: function(questionData){
            renderQuestionResults(questionData)
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
});

// Render question results from an API response as a string
function renderQuestionResults(questionData) {
    // Set visibility of results containers
    $('#questionList')[0].innerHTML = '';

    // Render new results
    var loadedData = JSON.parse(questionData);
    var questionResultElement = '';
    _.each(loadedData['items'], function(questionResult) {
        var text = questionResult['question'];
        var file = questionResult['file_path'];
        var display = questionResult['display_path'];
        var line = questionResult['line_number'];
        var answer = questionResult['answer'];
        var newRowElement = getQuestionElement(text, file, display, line, answer)
        questionResultElement = questionResultElement + newRowElement;
    });
    $('#questionList').append(questionResultElement);
    setCount(loadedData['count']);
    setQuestionResultActions();
};

// Wire up action buttons on results
function setQuestionResultActions() {

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
                _.each(loadedContext['before'], function (beforeLine) {
                    contextElement += beforeLine + '\n'
                });
                contextElement += loadedContext['line'] + '\n'
                _.each(loadedContext['after'], function (afterLine) {
                    contextElement += afterLine + '\n'
                });
                contextElement += '</code></pre>'
                $(rowElement).find('.questionText')[0].innerHTML = contextElement
            },
            error: function(responseData) {
                var loadedResponse = JSON.parse(responseData.responseText)
                showModal(loadedResponse.error)
            }
        });
    });

    // Wire up edit button
    $(".editContent").click(function() {
        console.log('Editing Context')
    });

}
