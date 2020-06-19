// Convert a list of tags to a string that contains HTML elements for each tag
function getTagsElements(tags) {
    var tagElement = ' '
    for (var i = tags.length - 1; i >= 0; i--) {
        tagElement = tagElement + '<span class="badge badge-secondary tag-badge">' + tags[i] + '</span>';
    }
    return tagElement
}

// Utility to set the result count
function setCount(count) {
    $('#resultCount').text(count)
}

// Handler for Stamping Notes
$("#stampNotes").click(function() {
    console.log( "Handler for stamp notes called." );
    $.ajax({
        url: '/api/v1/stamp',
        data: {},
        success: function(responseData){
            showModal(message='Stamped Notes!', title='Updated Notes')
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
});

$('#syncIcon').click(function() {
    $.ajax({
        url: '/api/v1/pull',
        type: 'GET',
        data: {},
        success: function(responseData) {
            var htmlMessage = '<div class="alert alert-success" role="alert">' + responseData + '</div>'
            showModal(message=htmlMessage, title='Updated Notes')
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    })
})

// Utility function to render an error in a modal
function showModal(message='None', title='Server Error') {
    $('#modalDescription').html(message)
    $('#shorthandModal').modal()
    $('#modalTitle').text(title)
}

// Collapse elements bar in the navigation
$('#elementsCollapser').click(function () {
    // Ensure the options bar is closed
    $('#optionsWrapper').removeClass('open-subicons')
    $('#optionsBar').removeClass('show')
    // Show / hide the elements bar
    $('#elementsBar').toggleClass('show')
    $('#elementsWrapper').toggleClass('open-subicons')
});

// Collapse options bar in the navigation
$('#optionsCollapser').click(function () {
    // Ensure the elements bar is closed
    $('#elementsBar').removeClass('show')
    $('#elementsWrapper').removeClass('open-subicons')
    // Show / hide the options bar
    $('#optionsBar').toggleClass('show')
    $('#optionsWrapper').toggleClass('open-subicons')
});
