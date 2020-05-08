$('.showRec').click( function (ev) {
    var parentElement = $(ev.currentTarget.parentElement.parentElement.parentElement)
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
            showModal(loadedResponse.error)
        }
    });
})


$('.getCsv').click( function (ev) {
    var parentElement = $(ev.currentTarget.parentElement.parentElement)
    var lineNumber = parentElement.find('.lineNumber').text()
    var filePath = parentElement.find('.filePath').text()
    $.ajax({
        type: 'GET',
        url: '/get_record_set',
        data: {
            file_path: filePath,
            line_number: lineNumber,
            parse: 'true',
            parse_format: 'csv'
        },
        success: function(responseData) {
            downloadFile('record_set.csv', responseData)
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText)
            showModal(loadedResponse.error)
        }
    });
})


// Utility function to download a text file. Taken from:
// https://stackoverflow.com/a/18197341
function downloadFile(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}
