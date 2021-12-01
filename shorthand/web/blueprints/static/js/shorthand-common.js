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
        success: function(responseData){
            showModal(message='Stamped Notes!', title='Updated Notes')
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
});

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

// Support for the File Finder Modal
function showFileFinder() {
    $('#shorthandFileModal').modal();
    var fileSearch = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/api/v1/files?query_string=%QUERY',
            wildcard: '%QUERY'
        }
    });

    var fullTextSearch = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/api/v1/search?query_string=%QUERY',
            wildcard: '%QUERY',
            filter: results => $.map(results.items, result => ({
                match_content: result.match_content,
                path: result.file_path + '#line-number-' + result.line_number,
                shortPath: result.file_path + '#' + result.line_number,
            }))
        }
    });

    $('#fileModalSearchBar').typeahead(
        {
            highlight: true
        }, {
            name: 'notes-files',
            limit: 10,
            source: fileSearch,
            templates: {
                header: '<h3>Notes Filenames</h3>'
            }
        }, {
            name: 'notes-full-text',
            limit: 10,
            source: fullTextSearch,
            display: 'path',
            templates: {
                header: '<h3>Notes Full Text</h3>',
                suggestion: function(data) {
                    return '<div>' + data.match_content + '<span style="float: right;">' + data.shortPath + '</span></div>';
                }
            }
        }
    );

    // Click Handler for the goto note button
    $("#goToNote").click( function() {
        console.log('Go To Note clicked!');
        var notePath = $('#fileModalSearchBar').val();
        // Log the file view
        $.ajax({
            url: '/api/v1/record_view?' + $.param({relative_path: notePath}),
            type: 'POST',
            success: function(responseData) {
                if (responseData == 'ack') {
                    window.location.href = '/render?path=' + notePath;
                }
            },
            error: function(responseData) {
                var loadedResponse = JSON.parse(responseData.responseText)
                showModal(loadedResponse.error)
            }
        });
    });

    // Set the focus to the search bar after the modal is actually visible
    $('#shorthandFileModal').on('shown.bs.modal', function (e) {
        $('#fileModalSearchBar').focus();
    })

    // Handler for the enter key
    // from https://stackoverflow.com/a/7060762
    $("#fileModalSearchBar").on('keyup', function (e) {
        if (e.key === 'Enter' || e.keyCode === 13) {
            $('#goToNote').click();
        }
    });

};

// From https://stackoverflow.com/a/16006607
function KeyPress(e) {
    var evtobj = window.event? event : e
    if (evtobj.keyCode == 84 && evtobj.ctrlKey) {
        // Show the file finder when Ctrl + T is pressed
        showFileFinder();
    };
}
document.onkeydown = KeyPress;
