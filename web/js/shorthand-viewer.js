

// Wire click events for show / hide TOC button
$("#showTOC").click(function(){
  $(".toc-content").toggleClass("hidden");
});

// Render tables with record sets
$(document).ready(function() {

    _.each($('.record-set-table'), function (tableElement) {
        console.log(tableElement);
        var jsonString = $(tableElement.parentElement).find('.record-set-data')[0].innerText;
        console.log(jsonString)
        var tableData = JSON.parse(jsonString);
        console.log(tableData);
        var colString = $(tableElement).attr('data-cols');
        var columns = JSON.parse(colString);
        console.log(columns);
        $(tableElement).DataTable({
            data: tableData,
            columns: columns
        });
    });

    $('blockquote').addClass('blockquote text-center');

});

hljs.initHighlightingOnLoad();
