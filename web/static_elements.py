'''Static Elements which are re-used in lots of places
'''

HEADER_HTML = '''<div class="row top-gutter">
            <div class="col-md-12"></div>
        </div>

        <div class="row title-bar">
            <div class="col-md-7" id="title-wrapper">
                <h1 id="notes-title">Notes</h1>
            </div>
            <div class="col-md-1 icon-wrapper"><a href="/"><img class="svg-icon" src="/img/home-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper" id="elementsWrapper"><a id="elementsCollapser" href="#"><img class="svg-icon" src="/img/code-square-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper"><a href="/calendar"><img class="svg-icon" src="/img/calendar-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper"><a href="/search"><img class="svg-icon" src="/img/search-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper" id="optionsWrapper"><a id="optionsCollapser" href="#"><img class="svg-icon" src="/img/tools-24.svg"></a></div>
        </div>

        <!-- Elements Bar -->
        <div class="row title-bar elements-bar collapse" id="elementsBar">
            <div class="col-md-7"></div>
            <div class="col-md-1 icon-wrapper"><a href="/todos"><img class="svg-icon" src="/img/tasklist-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper"><a href="/questions"><img class="svg-icon" src="/img/question-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper"><a href="/glossary"><img class="svg-icon" src="/img/book-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper"><a href="/databases"><img class="svg-icon" src="/img/database-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper"><a href="/locations"><img class="svg-icon" src="/img/globe-24.svg"></a></div>
        </div>

        <!-- Options Bar -->
        <div class="row options-bar collapse" id="optionsBar">
            <div class="col-md-10"></div>
            <div class="col-md-1 icon-wrapper"><a id="syncIcon" href="#"><img class="svg-icon" src="/img/sync-24.svg"></a></div>
            <div class="col-md-1 icon-wrapper"><a href="#"><img class="svg-icon" src="/img/settings-24.svg"></a></div>
        </div>'''

MODAL_BLOCK = '''<div id="modalWrapper">
  <div class="modal fade" id="shorthandModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="modalTitle">Server Error</h5>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div id="modalDescription" class="modal-body">
          placeholder
        </div>
      </div>
    </div>
  </div>
</div>'''

COMMON_IMPORTS = '''<!-- Common Resources for all pages -->
    <link rel="stylesheet" type="text/css" href="/css/shorthand-common.css">
    <link rel="stylesheet" type="text/css" href="/css/bootstrap.min.css">
    <script type="text/javascript" src="/js/jquery-3.3.1.min.js"></script>
    <script type="text/javascript" src="/js/shorthand-common.js" defer></script>
    <script type="text/javascript" src="/js/bootstrap.js" defer></script>'''

static_content = {
    'modal_block': MODAL_BLOCK,
    'header_html': HEADER_HTML,
    'common_imports': COMMON_IMPORTS
}
