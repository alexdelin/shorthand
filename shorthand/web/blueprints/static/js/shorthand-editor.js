// Function to Save Note
function saveNote() {
    var filePath = $('#meta-file-path').text();
    var noteContent = editor.getValue();
    $.ajax({
        url: '/api/v1/note?' + $.param({path: filePath}),
        type: 'POST',
        contentType: 'text/plain',
        data: noteContent,
        success: function(response) {
            console.log(response);
            editor.session.getUndoManager().markClean();
            renderNote();
            validateLinks();
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText);
            showModal(loadedResponse.error);
        }
    });
}

// Function to Reload Note
function reloadNote() {
    var filePath = $('#meta-file-path').text()
    $.ajax({
        url: '/api/v1/note?' + $.param({path: filePath}),
        type: 'GET',
        success: function(noteContent) {
            console.log(noteContent);
            editor.setValue(noteContent);
            editor.clearSelection();
            editor.session.getUndoManager().markClean();
            validateLinks();
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
}

// Click handler for the save note button
$("#saveNote").click( function() {
    console.log('Save Note clicked!');
    saveNote();
});

// Click handler for the reload note button
$("#reloadNote").click( function() {
    console.log('Reload Note clicked!');
    if (editor.session.getUndoManager().isClean()) {
        reloadNote();
    } else {
        alert("can't reload note if you have pending changes");
    }
});

// Click handler for the problem warning button
$("#problemWarning").click( function() {
    console.log('Problem icon clicked');
    $('#shorthandNoteProblemModal').modal();
});

// Check if you leave the page with pending changes
window.addEventListener('beforeunload', function (e) {
    if (!editor.session.getUndoManager().isClean()) {
        // Cancel the event
        e.preventDefault(); // If you prevent default behavior in Mozilla Firefox prompt will always be shown
        // Chrome requires returnValue to be set
        e.returnValue = '';
    }
});

function validateLinks() {
    // Check the note for invalid links
    var filePath = $('#meta-file-path').text();
    $.ajax({
        url: '/api/v1/links/validate?' + $.param({source: filePath}),
        type: 'GET',
        success: function(response) {

            // Start with the warning icon hidden
            if (!$('#problemWarning').hasClass('hidden')) {
                $('#problemWarning').toggleClass('hidden');
            }
            // Start with the problem list empty
            $("#noteProblemList").html('');

            // Start with all markers removed
            var Range = ace.require('ace/range').Range;
            var markers = editor.session.getMarkers();
            var markerIds = Object.keys(editor.session.getMarkers());
            // debugger;
            for (var i = markerIds.length - 1; i >= 0; i--) {
                if (markers[markerIds[i]].clazz == 'brokenLink') {
                    console.log('removing marker');
                    editor.session.removeMarker(markers[markerIds[i]].id);
                }
            }

            var invalidLinks = JSON.parse(response);
            for (var i = invalidLinks.length - 1; i >= 0; i--) {
                // Ensure the warning icon is shown if we have
                // at least one broken link
                if ($('#problemWarning').hasClass('hidden')) {
                    $('#problemWarning').toggleClass('hidden');
                };
                var problemLine = invalidLinks[i].line_number
                var problemEl = '<li>Invalid link to ' + invalidLinks[i].target +
                                ' on line ' + problemLine + '</li>';
                $("#noteProblemList").append(problemEl);
                editor.session.addMarker(new Range(problemLine-1, 0, problemLine-1, 1), "brokenLink", "fullLine");
            }
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText);
            showModal(loadedResponse.error);
        }
    });
}
