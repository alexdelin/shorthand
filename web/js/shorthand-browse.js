$.ajax({
  url: '/toc',
  type: 'GET',
  success: function(responseData) {
    renderToc(JSON.parse(responseData))
  }
})

function renderToc(toc) {
  // Create root parent element
  var root_element = $('#tocRoot')[0];

  function process_subdir(dir_data, element, isRoot) {
    // Traverse the toc object and add nodes in a depth-first search
    var path = dir_data.path;
    var text = dir_data.text;
    var files = dir_data.files;
    var subdirs = dir_data.dirs;

    // Draw all subdirs in the current dir
    _.each(subdirs, function (subdir_data) {
      var subdir_text = subdir_data.text;
      // Create a nested element to house the child directory
      var newElement = $('<div class="alert alert-primary toc-entry" role="alert">' + subdir_text + '</div>');
      if (!isRoot) {
        newElement.addClass('hidden');
      }
      element.append(newElement[0]);
      var child_element = $(element).children().last();
      process_subdir(subdir_data, child_element, false);
    });

    // Draw all files in the current dir
    _.each(files, function (file) {
      // Add a child element for a given file
      var newElement = $('<div class="alert alert-danger" role="alert"><a href="/render?path=' + path + '/' + file + '">' + file + '</a></div>');
      if (!isRoot) {
        newElement.addClass('hidden');
      }
      element.append(newElement[0]);
    });

  };

  process_subdir(toc, root_element, true)

  $('.toc-entry').click(function(ev) {
    console.log('clicked element');
    console.log(ev.currentTarget);
    $(ev.currentTarget).children().toggleClass('hidden');
    ev.stopPropagation();
  })

}
