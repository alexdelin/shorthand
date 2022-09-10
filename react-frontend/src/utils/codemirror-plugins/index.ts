// Latex parser extension
import {InlineContext, BlockContext, MarkdownConfig,
        LeafBlockParser, LeafBlock, Line, Element} from "@lezer/markdown"
import {tags as t, Tag} from "@lezer/highlight"

const LatexInlineDelim = {resolve: "Latex-inline", mark: "LatexMark"}
const LatexBlockDelim = {resolve: "Latex-block", mark: "LatexMark"}


// Define Custom Tags
// Todos
const todoIncompleteMarkerTag = Tag.define(t.name);
const todoIncompleteTag = Tag.define(t.number);
const todoSkippedMarkerTag = Tag.define(t.comment);
const todoSkippedTag = Tag.define(t.comment);
const todoCompleteMarkerTag = Tag.define(t.comment);
const todoCompleteTag = Tag.define(t.labelName);

// Questions
// Definitions
// Timestamps
const timestampMarkTag = Tag.define(t.processingInstruction);
const timestampTag = Tag.define(t.operator);

// Latex
// Today placeholder


// Shorthand Todo Extensions
class IncompleteTodoParser implements LeafBlockParser {
  nextLine() { return false }

  finish(cx: BlockContext, leaf: LeafBlock) {
    cx.addLeafElement(leaf, cx.elt("Todo-incomplete", leaf.start, leaf.start + leaf.content.length, [
      cx.elt("Todo-incomplete-marker", leaf.start, leaf.start + 3),
      ...cx.parser.parseInline(leaf.content.slice(3), leaf.start + 3)
    ]))
    return true
  }
}

class SkippedTodoParser implements LeafBlockParser {
  nextLine() { return false }

  finish(cx: BlockContext, leaf: LeafBlock) {
    cx.addLeafElement(leaf, cx.elt("Todo-skipped", leaf.start, leaf.start + leaf.content.length, [
      cx.elt("Todo-skipped-marker", leaf.start, leaf.start + 3),
      ...cx.parser.parseInline(leaf.content.slice(3), leaf.start + 3)
    ]))
    return true
  }
}

class CompleteTodoParser implements LeafBlockParser {
  nextLine() { return false }

  finish(cx: BlockContext, leaf: LeafBlock) {
    cx.addLeafElement(leaf, cx.elt("Todo-complete", leaf.start, leaf.start + leaf.content.length, [
      cx.elt("Todo-complete-marker", leaf.start, leaf.start + 3),
      ...cx.parser.parseInline(leaf.content.slice(3), leaf.start + 3)
    ]))
    return true
  }
}

export const todoPlugin: MarkdownConfig = {
  defineNodes: [{
    name: "Todo-incomplete",
    style: todoIncompleteTag
  }, {
    name: "Todo-incomplete-marker",
    style: todoIncompleteMarkerTag
  }, {
    name: "Todo-skipped",
    style: todoSkippedTag
  }, {
    name: "Todo-skipped-marker",
    style: todoSkippedMarkerTag
  }, {
    name: "Todo-complete",
    style: todoCompleteTag
  }, {
    name: "Todo-complete-marker",
    style: todoCompleteMarkerTag
  }],
  parseBlock: [{
    name: "Todo-incomplete",
    leaf(cx, leaf) {
      return /^\[[ ]?\]/.test(leaf.content) && (cx.parentType().name === "ListItem")
        ? new IncompleteTodoParser()
        : null
    },
    after: "SetextHeading"
  }, {
    name: "Todo-skipped",
    leaf(cx, leaf) {
      return /^\[S\]/.test(leaf.content) && (cx.parentType().name === "ListItem")
        ? new SkippedTodoParser()
        : null
    },
    after: "SetextHeading"
  }, {
    name: "Todo-complete",
    leaf(cx, leaf) {
      return /^\[X\]/.test(leaf.content) && (cx.parentType().name === "ListItem")
        ? new CompleteTodoParser()
        : null
    },
    after: "SetextHeading"
  }]
}

// An extension that highlights
// ISO 8604 date stamps for element metadata
export const timestampPlugin: MarkdownConfig = {
  defineNodes: [{
    name: "Timestamp",
    style: timestampTag
  }, {
    name: "Timestamp-mark",
    style: timestampMarkTag
  }],
  parseInline: [
    {
      name: "Timestamp",
      parse(cx, next, pos) {
        let match: RegExpMatchArray | null
        if (![40, 49, 50 /* `(,1,2` */].includes(next) &&
            (next !== 32 ||
              cx.char(pos + 1) !== 45 ||
              cx.char(pos + 2) !== 62 ||
              cx.char(pos + 3) !== 32
            ) ||
            !(match = /^( -> )?(\(?)\b((-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9]))\b(\)?)/.exec(cx.slice(pos, cx.end)))
        ) {
          return -1
        }

        const arrowStart = pos;
        const arrowEnd = arrowStart + (match[1] || '').length;
        const openParenthesesStart = arrowEnd;
        const openParenthesesEnd = openParenthesesStart + (match[2] || '').length;
        const timestampStart = openParenthesesEnd;
        const timestampEnd = timestampStart + (match[3] || '').length;
        const closeParenthesesStart = timestampEnd;
        const closeParenthesesEnd = closeParenthesesStart + (match[7] || '').length;

        return cx.addElement(cx.elt("Timestamp", pos, pos + match[0].length,
          [
            cx.elt("Timestamp-mark", arrowStart, arrowEnd),
            cx.elt("Timestamp-mark", openParenthesesStart, openParenthesesEnd),
            cx.elt("Timestamp-mark", closeParenthesesStart, closeParenthesesEnd),
          ]
        ))
      }
    }
  ]
}

/// An extension that implements
/// Latex syntax using `$` and `$$` delimiters.
export const latexPlugin: MarkdownConfig = {
  defineNodes: [{
    name: "Latex-inline",
    style: t.character
  }, {
    name: "Latex-block",
    style: t.character
  },{
    name: "LatexMark",
    style: t.processingInstruction
  }],
  parseInline: [
    {
      name: "Latex-inline",
      parse(cx, next, pos) {
        let match: RegExpMatchArray | null
        if (next !== 36 /* '$' */ ||
            (next === 36 && cx.char(pos + 1) === 36) ||
            (next === 36 && cx.char(pos - 1) === 36)) {
            // !(match = /^[^\$]+\$/.exec(cx.slice(pos + 1, cx.end)))) {
          return -1
        }
        return cx.addDelimiter(LatexInlineDelim, pos, pos + 1, true, true)
      }
    },
    {
      name: "Latex-block",
      parse(cx, next, pos) {
        if (next !== 36 /* '$' */ || cx.char(pos + 1) !== 36) return -1
        return cx.addDelimiter(LatexBlockDelim, pos, pos + 2, true, true)
      },
      after: "Superscript",
      // before: "Superscript"
    },
  ]
}

/// An extension that implements
/// Shorthand Location syntax.
export const locationPlugin: MarkdownConfig = {
  defineNodes: [{
    name: "Location-lattitude",
    style: t.number
  },{
    name: "Location-longitude",
    style: t.number
  },{
    name: "Location-name",
    style: t.name
  },{
    name: "Location-delimiter",
    style: t.processingInstruction
  }],
  parseInline: [
    {
      name: "Location",
      parse(cx, next, pos) {
        let match: RegExpMatchArray | null
        if (next !== 71 /* 'G' */ ||
            cx.char(pos + 1) !== 80 /* 'P' */ ||
            cx.char(pos + 2) !== 83 /* 'S' */ ||
            cx.char(pos + 3) !== 91 /* '[' */ ||
            !(match = /^(-?1?\d{1,2}\.\d{3,6})(, ?)(-?1?\d{1,2}\.\d{3,6})(, ?)?([\w ]+)?\]/.exec(cx.slice(pos + 4, cx.end)))
        ) {
          return -1
        }
        return cx.addElement(cx.elt("Location-delimiter", pos, pos + 4 + match[0].length,
          [
            cx.elt("Location-lattitude",
                   pos + 4,
                   pos + 4 + match[1].length),
            cx.elt("Location-longitude",
                   pos + 4 + match[1].length + match[2].length,
                   pos + 4 + match[1].length + match[2].length + match[3].length),
            cx.elt("Location-name",
                   pos + 4 + match[1].length + match[2].length + match[3].length + match[4].length,
                   pos + 3 + match[0].length),
        ]))
      },
      before: "Link"
    }
  ]
}
