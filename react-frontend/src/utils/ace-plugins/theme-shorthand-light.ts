// This theme was created from a template from:
//   https://github.com/thlorenz/brace/issues/132#issuecomment-497152397

import ace from 'brace';

// Original theme taken from https://github.com/ajaxorg/ace-builds/blob/master/src/theme-chrome.js
ace.define('ace/theme/shorthand-light', ['require', 'exports', 'module', 'ace/lib/dom'], (acequire: any, exports: any) => {

  exports.isDark = false;
  exports.cssClass = 'ace-shorthand-light';
  exports.cssText = ".ace-shorthand-light .ace_gutter {\
    background: #ebebeb;\
    color: #333;\
    overflow : hidden;\
    }\
    .ace-shorthand-light .ace_print-margin {\
    width: 1px;\
    background: #e8e8e8;\
    }\
    .ace-shorthand-light {\
    background-color: hsl(180, 9%, 98%);\
    color: black;\
    }\
    .ace-shorthand-light .ace_cursor {\
    color: black;\
    }\
    .ace-shorthand-light .ace_invisible {\
    color: rgb(191, 191, 191);\
    }\
    .ace-shorthand-light .ace_constant.ace_buildin {\
    color: rgb(88, 72, 246);\
    }\
    .ace-shorthand-light .ace_constant.ace_language {\
    color: rgb(88, 92, 246);\
    }\
    .ace-shorthand-light .ace_constant.ace_library {\
    color: rgb(6, 150, 14);\
    }\
    .ace-shorthand-light .ace_invalid {\
    background-color: rgb(153, 0, 0);\
    color: white;\
    }\
    .ace-shorthand-light .ace_fold {\
    }\
    .ace-shorthand-light .ace_punctuation.ace_definition {\
    color: hsl(180, 36%, 38%);\
    }\
    .ace-shorthand-light .ace_punctuation.ace_definition.ace_bold {\
    color: hsl(300, 30%, 48%);\
    }\
    .ace-shorthand-light .ace_punctuation.ace_definition.ace_italic {\
    color: hsl(300, 30%, 48%);\
    }\
    .ace-shorthand-light .ace_support.ace_function {\
    color: hsl(114, 31%, 38%);\
    }\
    .ace-shorthand-light .ace_support.ace_function.ace_inline {\
    color: hsl(114, 31%, 38%);\
    }\
    .ace-shorthand-light .ace_support.ace_todo.ace_incomplete {\
    color: hsl(32, 93%, 42%);\
    }\
    .ace-shorthand-light .ace_support.ace_todo.ace_incomplete.ace_start {\
    color: hsl(357, 79%, 55%);\
    }\
    .ace-shorthand-light .ace_support.ace_todo.ace_complete {\
    color: hsl(210, 13%, 45%);\
    }\
    .ace-shorthand-light .ace_support.ace_todo.ace_complete.ace_start {\
    color: hsl(210, 50%, 45%);\
    }\
    .ace-shorthand-light .ace_support.ace_todo.ace_skipped {\
    color: hsl(0, 0%, 60%);\
    }\
    .ace-shorthand-light .ace_support.ace_question.ace_start {\
    color: hsl(56, 100%, 35%);\
    }\
    .ace-shorthand-light .ace_support.ace_question {\
    color: hsl(330, 65%, 47%);\
    }\
    .ace-shorthand-light .ace_support.ace_answer.ace_start {\
    color: hsl(180, 36%, 54%);\
    }\
    .ace-shorthand-light .ace_support.ace_answer {\
    color: hsl(114, 51%, 43%);\
    }\
    .ace-shorthand-light .ace_support.ace_definition.ace_border {\
    color: hsl(0, 0%, 60%);\
    }\
    .ace-shorthand-light .ace_support.ace_definition.ace_term {\
    color: hsl(56, 100%, 35%);\
    }\
    .ace-shorthand-light .ace_support.ace_definition {\
    color: hsl(32, 93%, 42%);\
    }\
    .ace-shorthand-light .ace_support.ace_latex {\
    color: hsl(114, 31%, 38%);\
    }\
    .ace-shorthand-light .ace_support.ace_tag {\
    color: hsl(357, 79%, 55%);\
    }\
    .ace-shorthand-light .ace_support.ace_timestamp {\
    color: hsl(180, 36%, 54%);\
    }\
    .ace-shorthand-light .ace_support.ace_location {\
    color: hsl(180, 36%, 38%);\
    }\
    .ace-shorthand-light .ace_support.ace_constant {\
    color: rgb(6, 150, 14);\
    }\
    .ace-shorthand-light .ace_support.ace_type,\
    .ace-shorthand-light .ace_support.ace_class\
    .ace-shorthand-light .ace_support.ace_other {\
    color: rgb(109, 121, 222);\
    }\
    .ace-shorthand-light .ace_variable.ace_parameter {\
    font-style:italic;\
    color:#FD971F;\
    }\
    .ace-shorthand-light .ace_keyword.ace_operator {\
    color: rgb(104, 118, 135);\
    }\
    .ace-shorthand-light .ace_comment {\
    color: #236e24;\
    }\
    .ace-shorthand-light .ace_comment.ace_doc {\
    color: #236e24;\
    }\
    .ace-shorthand-light .ace_comment.ace_doc.ace_tag {\
    color: #236e24;\
    }\
    .ace-shorthand-light .ace_constant.ace_numeric {\
    color: hsl(32, 93%, 42%);\
    }\
    .ace-shorthand-light .ace_variable {\
    color: rgb(49, 132, 149);\
    }\
    .ace-shorthand-light .ace_xml-pe {\
    color: rgb(104, 104, 91);\
    }\
    .ace-shorthand-light .ace_entity.ace_name.ace_function {\
    color: #0000A2;\
    }\
    .ace-shorthand-light .ace_heading.ace_1 {\
        color: hsl(0, 79%, 60%);\
        font-weight: bold;\
    }\
    .ace-shorthand-light .ace_heading.ace_2 {\
        color: hsl(15, 93%, 56%);\
        font-weight: bold;\
    }\
    .ace-shorthand-light .ace_heading.ace_3 {\
        color: hsl(30, 79%, 55%);\
        font-weight: bold;\
    }\
    .ace-shorthand-light .ace_heading.ace_4 {\
        color: hsl(45, 79%, 50%);\
        font-weight: bold;\
    }\
    .ace-shorthand-light .ace_heading.ace_5 {\
        color: hsl(60, 89%, 45%);\
        font-weight: bold;\
    }\
    .ace-shorthand-light .ace_heading.ace_6 {\
        color: hsl(75, 89%, 45%);\
        font-weight: bold;\
    }\
    .ace-shorthand-light .ace_heading {\
    font-weight: bold;\
    }\
    .ace-shorthand-light .ace_markup.ace_list {\
    color: hsl(32, 93%, 42%);\
    }\
    .ace-shorthand-light .ace_list {\
    }\
    .ace-shorthand-light .ace_marker-layer .ace_selection {\
    background: rgb(181, 213, 255);\
    }\
    .ace-shorthand-light .ace_marker-layer .ace_step {\
    background: rgb(252, 255, 0);\
    }\
    .ace-shorthand-light .ace_marker-layer .ace_stack {\
    background: rgb(164, 229, 101);\
    }\
    .ace-shorthand-light .ace_marker-layer .ace_bracket {\
    margin: -1px 0 0 -1px;\
    border: 1px solid rgb(192, 192, 192);\
    }\
    .ace-shorthand-light .ace_marker-layer .ace_active-line {\
    background: rgba(0, 0, 0, 0.07);\
    }\
    .ace-shorthand-light .ace_gutter-active-line {\
    background-color : #dcdcdc;\
    }\
    .ace-shorthand-light .ace_marker-layer .ace_selected-word {\
    background: rgb(250, 250, 255);\
    border: 1px solid rgb(200, 200, 250);\
    }\
    .ace-shorthand-light .ace_storage,\
    .ace-shorthand-light .ace_keyword,\
    .ace-shorthand-light .ace_meta.ace_tag {\
    color: rgb(147, 15, 128);\
    }\
    .ace-shorthand-light .ace_string.ace_regex {\
    color: rgb(255, 0, 0);\
    }\
    .ace-shorthand-light .ace_string.ace_blockquote {\
    color: hsl(0, 0%, 60%);\
    }\
    .ace-shorthand-light .ace_string {\
    color: hsl(114, 31%, 38%);\
    }\
    .ace-shorthand-light .ace_string.ace_strikethrough {\
    color: hsl(23, 85%, 37%);\
    text-decoration: line-through;\
    }\
    .ace-shorthand-light .ace_string.ace_emphasis {\
    font-style: italic;\
    color: black;\
    }\
    .ace-shorthand-light .ace_string.ace_strong {\
    font-weight: bold;\
    color: black;\
    }\
    .ace-shorthand-light .ace_string.ace_strong-emphasis {\
    font-weight: bold;\
    font-style: italic;\
    color: black;\
    }\
    .ace-shorthand-light .ace_entity.ace_other.ace_attribute-name {\
    color: #994409;\
    }\
    .ace-shorthand-light .ace_indent-guide {\
    background: url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAAE0lEQVQImWP4////f4bLly//BwAmVgd1/w11/gAAAABJRU5ErkJggg==\") right repeat-y;\
    }\
    ";

  const dom = acequire('ace/lib/dom');
  dom.importCssString(exports.cssText, exports.cssClass);
});
