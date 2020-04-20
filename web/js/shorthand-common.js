// Convert a list of tags to a string that contains HTML elements for each tag
function getTagsElements(tags) {
    var tagElement = ' '
    _.each(tags, function (tag) {
        tagElement = tagElement + '<span class="badge badge-secondary">' + tag + '</span>';
    });
    return tagElement
}

// Utility to set the result count
function setCount(count) {
    $('#resultCount')[0].innerHTML = count
}

// Handler for Stamping Notes
$("#stampNotes").click(function() {
    console.log( "Handler for stamp notes called." );
    $.get('stamp', {},
        function(responseData){
            alert('Stamped Notes!')
    });
});
