$.ajax({
  url: '/api/v1/toc',
  type: 'GET',
  success: function(responseData) {
    renderToc(JSON.parse(responseData))
  }
})

function renderToc(toc) {
  // Create root parent element
  var root_element = $('#tocRoot')[0];


  function process_subdir(dir_data, isRoot) {
    // Traverse the toc object and add nodes in a depth-first search
    var path = dir_data.path;
    var text = dir_data.text;
    var files = dir_data.files;
    var subdirs = dir_data.dirs;

    if (isRoot === true) {
      var parent_node = new TreeNode("root");
    } else {
      var parent_node = new TreeNode(text);
    }

    // Draw all subdirs in the current dir
    _.each(subdirs, function (subdir_data) {
      // Create a nested element to house the child directory
      var directory_node = process_subdir(subdir_data, false);
      parent_node.addChild(directory_node)
    });

    // Draw all files in the current dir
    _.each(files, function (file) {
      // Add a child element for a given file
      var fileNode = new TreeNode(file);
      fileNode.on("click", function () {
        window.location.href = '/render?path=' + path + '/' + file;
      })
      parent_node.addChild(fileNode)
    });

    return parent_node;
  };

  var fullTree = process_subdir(toc, true);

  TreeConfig.open_icon = '<i class="bi-chevron-down"></i>';
  TreeConfig.close_icon = '<i class="bi-chevron-right"></i>';

  var view = new TreeView(fullTree, "#tocRoot", {
    "leaf_icon": '<i class="bi-file-earmark-text-fill"></i>',
    "parent_icon": '<i class="bi-folder2-open"></i>'}
  );

  // Only expand the root node
  view.collapseAllNodes();
  view.getRoot().setExpanded(true);
  view.reload();

}
