$('.showRec').click( function (ev) {
    var parentElement = $(ev.currentTarget.parentElement)
    var lineNumber = parentElement.find('.lineNumber').text()
    var filePath = parentElement.find('.filePath').text()
    var tableElement = parentElement.find('.record-set-table')
    ev.currentTarget.remove()
    $.ajax({
        type: 'GET',
        url: '/get_record_set',
        data: {
            file_path: filePath,
            line_number: lineNumber,
            parse: 'true',
            parse_format: 'json',
            include_config: 'true'
        },
        tableElement: tableElement,
        success: function(responseData) {

            // var loadedData = JSON.parse(responseData)
            console.log(responseData)
            var records = responseData.records
            var columns = responseData.fields
            var colConfig = []
            _.each(columns, function(column) {
                colConfig.push({title: column, data: column, defaultContent: ''})
            })
            tableElement.DataTable({
                data: records,
                columns: colConfig
            });

        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            renderError(loadedResponse.error)
        }
    });
})
