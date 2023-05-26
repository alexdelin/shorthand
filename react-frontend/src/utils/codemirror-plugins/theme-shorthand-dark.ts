import { EditorView } from '@codemirror/view';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags } from '@lezer/highlight';
import { todoIncompleteTag, todoIncompleteMarkerTag,
         todoSkippedTag, todoSkippedMarkerTag,
         todoCompleteTag, todoCompleteMarkerTag,
         timestampTag, locationNameTag,
         questionTag, questionMarkerTag,
         answerTag, answerMarkerTag,
         definitionTag, definitionTermTag, definitionMarkerTag,
         todayPlaceholderTag } from './index';

// Using https://github.com/one-dark/vscode-one-dark-theme/ as reference for the colors
// const chalky = "#e5c07b", coral = "#e06c75"
// const cyan = "#56b6c2", invalid = "#ffffff"
// const malibu = "#61afef", sage = "#98c379"
// const whiskey = "#d19a66", violet = "#c678dd"
// const darkBackground = "#21252b"
const ivory = "#abb2bf"
const stone = "#7d8799"
const highlightBackground = "#2c313a"
const background = "hsl(210, 15%, 20%)"
const tooltipBackground = "#353a42"
const selection = "#434956"
const cursor = "#528bff"

// Colors from Sublime Mariana theme
const white = "hsl(0, 0%, 100%)";
const red = "hsl(357, 79%, 65%)";
const red2 = "hsl(13, 93%, 66%)";
const blue = "hsl(210, 50%, 60%)";
const blue5 = "hsl(180, 36%, 54%)";
const blue6 = "hsl(221, 12%, 69%)";
const blue7= "hsl(210, 15%, 20%)";
const white3 = "hsl(219, 28%, 88%)";
const green = "hsl(114, 31%, 68%)";
const pink = "hsl(300, 30%, 68%)";
const orange = "hsl(32, 93%, 66%)";

/**
The editor theme styles for Shorthand Dark.
*/
const shorthandDarkTheme = EditorView.theme({
    "&": {
        color: white3,
        backgroundColor: blue7
    },
    ".cm-content": {
        caretColor: cursor
    },
    ".cm-cursor, .cm-dropCursor": { borderLeft: '1.5px solid ' + orange },
    "&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection": { backgroundColor: selection + ' !important' },
    ".cm-searchMatch": {
        backgroundColor: "#72a1ff59",
        outline: "1px solid #457dff"
    },
    ".cm-searchMatch.cm-searchMatch-selected": {
        backgroundColor: "#6199ff2f"
    },
    ".cm-activeLine": { backgroundColor: 'transparent' },
    ".cm-selectionMatch": { backgroundColor: "#aafe661a" },
    "&.cm-focused .cm-matchingBracket, &.cm-focused .cm-nonmatchingBracket": {
        backgroundColor: "#bad0f847",
        outline: "1px solid #515a6b"
    },
    ".cm-gutters": {
        backgroundColor: background,
        color: stone,
        border: "none"
    },
    ".cm-activeLineGutter": {
        backgroundColor: highlightBackground
    },
    ".cm-foldPlaceholder": {
        backgroundColor: "transparent",
        border: "none",
        color: "#ddd"
    },
    ".cm-tooltip": {
        border: "none",
        backgroundColor: tooltipBackground
    },
    ".cm-tooltip .cm-tooltip-arrow:before": {
        borderTopColor: "transparent",
        borderBottomColor: "transparent"
    },
    ".cm-tooltip .cm-tooltip-arrow:after": {
        borderTopColor: tooltipBackground,
        borderBottomColor: tooltipBackground
    },
    ".cm-tooltip-autocomplete": {
        "& > ul > li[aria-selected]": {
            backgroundColor: highlightBackground,
            color: ivory
        }
    }
}, { dark: true });

/**
The highlighting style for code in the Shorthand Dark theme.
*/
const shorthandDarkHighlightStyle = HighlightStyle.define([

    { tag: [tags.heading],
      color: white,
      fontWeight: "bold" },
    { tag: tags.strong,
      fontWeight: "bold" },
    { tag: [tags.keyword, tags.attributeName],
      color: pink },
    { tag: [tags.string],
      color: green },
    { tag: [tags.comment, tags.meta],
      color: blue6 },
    { tag: [
        // tags.name,
        // tags.deleted,
        tags.character,
        tags.macroName,
        tags.function(tags.variableName),
        tags.function(tags.propertyName),
        tags.labelName,
        tags.link],
      color: blue },
    { tag: [
        tags.atom,
        tags.angleBracket,
        tags.definition(tags.function(tags.variableName))],
      color: blue5 },
    { tag: [tags.number, tags.className, tags.typeName, tags.attributeValue],
      color: orange },
    { tag: [tags.bool, tags.tagName, tags.null],
      color: red },
    { tag: [tags.operator, tags.character, tags.contentSeparator],
      color: red2 },
    { tag: [tags.derefOperator, tags.quote, tags.monospace],
      color: blue6 },
    { tag: [tags.url],
      color: pink,
      textDecoration: "underline" },

    { tag: tags.emphasis,
      fontStyle: "italic" },
    { tag: tags.strikethrough,
      textDecoration: "line-through" },
    { tag: tags.processingInstruction,
      color: blue5 },

    // Todos
    { tag: todoIncompleteTag,
      color: orange },
    { tag: todoIncompleteMarkerTag,
      color: red },
    { tag: todoSkippedTag,
      color: blue6 },
    { tag: todoSkippedMarkerTag,
      color: blue6 },
    { tag: todoCompleteTag,
      color: blue5 },
    { tag: todoCompleteMarkerTag,
      color: blue },

    // Questions & Answers
    { tag: questionTag,
      color: pink },
    { tag: questionMarkerTag,
      color: orange },
    { tag: answerTag,
      color: green },
    { tag: answerMarkerTag,
      color: blue5 },

    // Definitions
    { tag: definitionTag,
      color: orange },
    { tag: definitionTermTag,
      color: red },
    { tag: definitionMarkerTag,
      color: blue6 },

    // Locations
    { tag: locationNameTag,
      color: green },

    // Timestamps
    { tag: timestampTag,
      color: blue },

    // Today Placeholder
    { tag: todayPlaceholderTag,
      color: red },


// Original Values
    // { tag: [tags.color, tags.constant(tags.name),
    //         tags.standard(tags.name)],
    //   color: whiskey },
    // { tag: [tags.definition(tags.name), tags.separator],
    //   color: ivory },
    // { tag: [tags.typeName, tags.className, tags.number,
    //         tags.changed, tags.annotation, tags.modifier,
    //         tags.self, tags.namespace],
    //   color: chalky },
    // { tag: [tags.operator, tags.operatorKeyword, tags.url,
    //         tags.escape, tags.regexp, tags.link,
    //         tags.special(tags.string)],
    //   color: cyan },
    // { tag: tags.link,
    //   color: stone,
    //   textDecoration: "underline" },
    // { tag: tags.heading,
    //   fontWeight: "bold",
    //   color: coral },
    // { tag: [tags.atom, tags.bool,
    //         tags.special(tags.variableName)],
    //   color: whiskey },
    // { tag: [tags.processingInstruction, tags.inserted],
    //   color: sage },
    // { tag: tags.invalid,
    //   color: invalid },
]);

/**
Extension to enable the Shorthand Dark theme (both the editor theme and
the highlight style).
*/
const shorthandDark = [shorthandDarkTheme, syntaxHighlighting(shorthandDarkHighlightStyle)];

export { shorthandDark, shorthandDarkHighlightStyle, shorthandDarkTheme };
