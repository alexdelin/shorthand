// Load the calendar data on page load
document.addEventListener('DOMContentLoaded', function() {
    reloadCalendar();
});


// Basic method to re-load the data in the calendar view
function reloadCalendar() {
    var selectedDir = $('#directoryFilter').val()
    $.ajax({
        url: '/api/v1/calendar?' + $.param({directory_filter: selectedDir}),
        type: 'GET',
        success: function(responseData) {
            parseCalendarResponse(responseData);
        },
        error: function(responseData) {
            var loadedResponse = JSON.parse(responseData.responseText);
            showModal(loadedResponse.error);
        }
    });
};


// Parse the raw data returned by the API, and provide
// the needed data to the calendar and chart
function parseCalendarResponse(responseData) {

    // Transform data to the format we need for the chart and calendar
    var eventData = []
    var chartData = []

    calendarData = JSON.parse(responseData)
    for (var year in calendarData) {
        for (var month in calendarData[year]) {
            for (var day in calendarData[year][month]) {

                // Prep data point to go on the chart
                var timestamp = Date.parse(year + "-" + month + "-" + day + "T00:00:00");
                var eventCount = calendarData[year][month][day].length;
                chartData.push([
                    timestamp, eventCount
                ]);

                for (var eventIndex in calendarData[year][month][day]) {
                    // Prep event to put on the calendar
                    var event = calendarData[year][month][day][eventIndex];
                    var formattedEvent = {
                        title: event['event'],
                        start: year + '-' + month + '-' + day,
                        url: '/render?path=' + event["file_path"] + '#line-number-' + event["line_number"],
                        type: event['type'],
                        textColor: 'black'
                    };
                    if (formattedEvent['type'] == 'section') {
                        formattedEvent['color'] = '#abeeff' // Light Blue
                        formattedEvent['textColor'] = 'black'
                    } else if (formattedEvent['type'] == 'incomplete_todo') {
                        formattedEvent['color'] = '#ffb2ab' // Red
                    } else if (formattedEvent['type'] == 'completed_todo') {
                        formattedEvent['color'] = '#c4c5ff' // Blue
                    } else if (formattedEvent['type'] == 'skipped_todo') {
                        formattedEvent['color'] = '#c4c4c4' // Grey
                    } else if (formattedEvent['type'] == 'question') {
                        formattedEvent['color'] = '#f4b8ff' // Purple
                    } else if (formattedEvent['type'] == 'answer') {
                        formattedEvent['color'] = '#afffa3' // Green
                    };
                    formattedEvent['description'] = formattedEvent['type'] + ' in ' + event['file_path'] + '<br /><br />' + formattedEvent['title']
                    eventData.push(formattedEvent);
                }
            }
        }
    }

    chartData = chartData.sort(function(a, b) { return a[0] - b[0]; });

    drawCalendar(eventData);
    drawChart(chartData);
}


function drawCalendar(eventData) {

    // Clear out the existing calendar
    $('#calendar').html('')

    // Draw Calendar
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        eventDidMount: function(info) {
            var tooltip = new Tooltip(info.el, {
                title: info.event.extendedProps.description,
                html: true,
                delay: {
                    show: 1000,
                    hide: 100
                },
                placement: 'top',
                trigger: 'hover',
                container: 'body'
            });
        },
        events: eventData
    });
    calendar.render();
};


function drawChart(chartData) {
    // Draw the productivity chart using the parsed chart data
    Highcharts.chart('productivityChart', {
        chart: {zoomType: 'x', type: 'column'},
        title: {text: 'Daily Productivity'},
        subtitle: {text: 'Meetings / sections created per day'},
        tooltip: {valueDecimals: 2},
        xAxis: {type: 'datetime'},
        series: [{
            data: chartData,
            lineWidth: 1,
            name: 'Sections per day'
        }]
    });
};


// Re-draw the calendar whenever the directory filter is changed
$("#directoryFilter").change(function () {
    reloadCalendar();
});
