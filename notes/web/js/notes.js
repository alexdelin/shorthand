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

// $("#addSubmit").click(function() {

//     console.log( "Handler for add submit called." );

//     var addLabel = $('#addLabel')[0].value;
//     var addText = $('#addText')[0].value
//     var addTraining = $('#addTraining')[0].value

//     $.ajax({
//         url: '/training/add_single',
//         data: {
//             "label": addLabel,
//             "text": addText,
//             "training_name": addTraining
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement)
//         },
//     });
// });


// $("#dedupSubmit").click(function() {

//     console.log( "Handler for dedup submit called." );

//     var dedupTraining = $('#dedupTraining')[0].value

//     $.ajax({
//         url: '/training/deduplicate',
//         data: {
//             "training_name": dedupTraining
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement)
//         },
//     });
// });


// $("#refreshSubmit").click(function() {

//     console.log( "Handler for refresh submit called." );

//     $('.training-example').remove()
//     var trainingName = $('#addTraining')[0].value

//     $.ajax({
//         url: '/training/get',
//         data: {
//             "training_name": trainingName
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement)

//             var loadedResponse = JSON.parse(response)
//             _.each(loadedResponse, function(trainingExample) {
//                 var exampleElement = '<tr class="training-example"><td>' + trainingExample['label'] + '</td><td>' + trainingExample['text'] + '</td></tr>'
//                 $('#training-example-list').append(exampleElement)
//             });
//         },
//     });
// });


// $("#extendSubmit").click(function() {

//     console.log( "Handler for extend submit called." );
//     // Remove all previous recommendations
//     $('.recommendation-row').remove()

//     var extendCorpus = $('#extendCorpus')[0].value
//     var extendImplementation = $('#extendImplementation')[0].value
//     var trainingName = $('#addTraining')[0].value
//     var extendConfidence = $('#extendConfidence')[0].value

//     $.ajax({
//         url: '/training/recommend',
//         data: {
//             "implementation_name": extendImplementation,
//             "corpus_name": extendCorpus,
//             "confidence": extendConfidence
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement)

//             // Add recommendation to table
//             loadedResponse = JSON.parse(response)
//             _.each(loadedResponse, function(recElement) {
//                 var rowElement = '<tr class="recommendation-row"><td class="recText">' + recElement['text'] + '</td><td class="recLabel">' + recElement['label'] + '</td><td class="recConfidence">' + recElement['confidence'] + '</td><td><div class="btn btn-default addExample">Add</div></td></tr>'
//                 $('#training-recommendations').append(rowElement)
//             });

//             $(".addExample").on('click', function(ev) {
//                 console.log( "Handler for add example called." );
//                 debugger;
//                 var newText = $(ev.target.parentElement.parentElement).find('.recText')[0].innerHTML
//                 var newLabel = $(ev.target.parentElement.parentElement).find('.recLabel')[0].innerHTML

//                 $.ajax({
//                     url: '/training/add_single',
//                     data: {
//                         "label": newLabel,
//                         "text": newText,
//                         "training_name": trainingName
//                     },
//                     success: function(response) {
//                         console.log(response)
//                         var newElement = '<div class="status-message">' + response + '</div>';
//                         $('#status-window').append(newElement)
//                     }
//                 });
//             });
//         },
//     });
// });


// $("#createTraining").click(function() {

//     console.log( "Handler for Create Training called." );

//     var trainingName = $('#trainingName')[0].value
//     if (trainingName.length === 0) {
//         console.log('early exit')
//         return
//     }

//     $.ajax({
//         url: '/training/create',
//         data: {
//             training_name: trainingName
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement);
//         },
//     });
// });


// $("#createImplementation").click(function() {

//     console.log( "Handler for Create Implementation called." );

//     var impName = $('#impName')[0].value
//     if (impName.length === 0) {
//         console.log('early exit')
//         return
//     }

//     var trainingName = $('#impTrainingName')[0].value
//     var modelName = $('#impModelName')[0].value

//     $.ajax({
//         url: '/implementations/create',
//         data: {
//             implementation_name: impName,
//             training_name: trainingName,
//             model_name: modelName
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement);
//         },
//     });
// });


// $("#checkStatus").click(function() {

//     console.log( "Handler for Check Status called." );
//     var implementationName = $('#implementationName')[0].getAttribute('value')

//     $.ajax({
//         url: '/implementations/list_loaded',
//         data: {},
//         success: function(response) {
//             var parsed_response = JSON.parse(response);
//             console.log(parsed_response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement);

//             if (parsed_response.indexOf(implementationName) >= 0) {
//                 var currentStatus = 'Loaded'
//             } else {
//                 var currentStatus = 'Not Loaded'
//             }
//             $('#implementationStatus')[0].innerHTML = currentStatus
//         },
//     });
// });


// $("#loadImplementation").click(function() {

//     console.log( "Handler for Load Implementation called." );
//     var implementationName = $('#implementationName')[0].getAttribute('value')

//     $.ajax({
//         url: '/implementations/load',
//         data: {
//             implementation_name: implementationName
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement);
//         },
//     });
// });


// $("#evaluate").click(function() {

//     console.log( "Handler for Evaluate called." );
//     var implementationName = $('#implementationName')[0].getAttribute('value')
//     var evalText = $('#evaluateText')[0].value;

//     $.ajax({
//         url: '/implementations/evaluate',
//         data: {
//             implementation_name: implementationName,
//             text: evalText
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement);
//         },
//     });
// });


// $("#reImplement").click(function() {

//     console.log( "Handler for Re-Implement called." );
//     var implementationName = $('#implementationName')[0].getAttribute('value');

//     $.ajax({
//         url: '/implementations/reimplement',
//         data: {
//             implementation_name: implementationName
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement);
//         },
//     });
// });


// $("#benchmark").click(function() {

//     console.log( "Handler for Benchmark called." );
//     var modelName = $('#modelName')[0].getAttribute('value');
//     var trainingName = $('#benchmarkTrainingName')[0].value

//     updateProgressBar('running');

//     $.ajax({
//         url: '/models/benchmark',
//         data: {
//             model_name: modelName,
//             training_name: trainingName
//         },
//         success: function(response) {
//             console.log(response)
//             var newElement = '<div class="status-message">' + response + '</div>';
//             $('#status-window').append(newElement);
//             drawBenchmarkResults(response)
//             updateProgressBar('done')
//         },
//         error: function(response) {
//             var errorMessage = JSON.parse(response.responseText)['error']
//             updateProgressBar('error', errorMessage)
//         }
//     })
// });
