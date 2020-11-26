// Function to Save Note
function saveNote() {
    var filePath = $('#meta-file-path').text()
    var noteContent = editor.getValue()
    $.ajax({
        url: '/api/v1/note?' + $.param({path: filePath}),
        type: 'POST',
        contentType: 'text/plain',
        data: noteContent,
        success: function(response) {
            console.log(response)
            editor.session.getUndoManager().markClean()
            alert(response)
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
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
            console.log(noteContent)
            editor.setValue(noteContent)
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

// Check if you leave the page with pending changes
window.addEventListener('beforeunload', function (e) {
    if (!editor.session.getUndoManager().isClean()) {
        // Cancel the event
        e.preventDefault(); // If you prevent default behavior in Mozilla Firefox prompt will always be shown
        // Chrome requires returnValue to be set
        e.returnValue = '';
    }
});

