// Click handler for the save note button
$("#saveNote").click( function() {
    console.log('Save Note clicked!')
    var filePath = $('#meta-file-path').text()
    var noteContent = editor.getValue()
    $.ajax({
        url: 'update_note?path=' + filePath,
        type: 'POST',
        contentType: 'text/plain',
        data: noteContent,
        success: function(response) {
            console.log(response)
            alert(response)
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
});

// Click handler for the reload note button
$("#reloadNote").click( function() {
    console.log('Reload Note clicked!')
    var filePath = $('#meta-file-path').text()
    $.ajax({
        url: 'get_note',
        type: 'GET',
        data: {
            path: filePath
        },
        success: function(noteContent) {
            console.log(noteContent)
            editor.setValue(noteContent)
            debugger;
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
});
