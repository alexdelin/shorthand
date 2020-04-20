// Build an HTML element for a question result from its properties
function getQuestionElement(text, file, line, answer) {
    return '<tr><td class="questionText">' + text +
           '</td><td class="filePath">' + file +
           '</td><td class="lineNumber">' + line +
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
    $.get('get_questions',
        {
            status: questionFilter,
            directory_filter: directoryFilter
        },
        function(questionData){
            renderQuestionResults(questionData)
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
        var line = questionResult['line_number'];
        var answer = questionResult['answer'];
        var newRowElement = getQuestionElement(text, file, line, answer)
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

    // Wire up edit button
    $(".editContent").click(function() {
        console.log('Editing Context')
    });

}
