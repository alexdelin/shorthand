// Latex parser extension
import {BlockContext, MarkdownConfig,
        LeafBlockParser, LeafBlock} from "@lezer/markdown"
import {tags as t, Tag} from "@lezer/highlight"

const LatexInlineDelim = {resolve: "Latex-inline", mark: "LatexMark"}
const LatexBlockDelim = {resolve: "Latex-block", mark: "LatexMark"}


// Define Custom Tags
// Todos
export const todoIncompleteMarkerTag = Tag.define(t.name);
export const todoIncompleteTag = Tag.define(t.number);
export const todoSkippedMarkerTag = Tag.define(t.comment);
export const todoSkippedTag = Tag.define(t.comment);
export const todoCompleteMarkerTag = Tag.define(t.comment);
export const todoCompleteTag = Tag.define(t.labelName);

// Questions
export const questionTag = Tag.define(t.comment);
export const questionMarkerTag = Tag.define(t.name);
export const answerTag = Tag.define(t.comment);
export const answerMarkerTag = Tag.define(t.name);

// Definitions
export const definitionTag = Tag.define(t.name);
export const definitionTermTag = Tag.define(t.name);
export const definitionMarkerTag = Tag.define(t.processingInstruction);

// Timestamps
export const timestampMarkTag = Tag.define(t.processingInstruction);
export const timestampTag = Tag.define(t.operator);

// Latex
export const latexInlineTag = Tag.define(t.character);
export const latexBlockTag = Tag.define(t.character);
export const latexMarkTag = Tag.define(t.processingInstruction);

// Today placeholder
export const todayPlaceholderTag = Tag.define(t.comment);

// Locations
export const locationMarkTag = Tag.define(t.processingInstruction);
export const locationNameTag = Tag.define(t.name);
export const locationLatLonTag = Tag.define(t.number);


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

class QuestionParser implements LeafBlockParser {
  nextLine() { return false }

  finish(cx: BlockContext, leaf: LeafBlock) {
    cx.addLeafElement(leaf, cx.elt("Question", leaf.start, leaf.start + leaf.content.length, [
      cx.elt("Question-marker", leaf.start, leaf.start + 2),
      ...cx.parser.parseInline(leaf.content.slice(2), leaf.start + 2)
    ]))
    return true
  }
}

class AnswerParser implements LeafBlockParser {
  nextLine() { return false }

  finish(cx: BlockContext, leaf: LeafBlock) {
    cx.addLeafElement(leaf, cx.elt("Answer", leaf.start, leaf.start + leaf.content.length, [
      cx.elt("Answer-marker", leaf.start, leaf.start + 1),
      ...cx.parser.parseInline(leaf.content.slice(1), leaf.start + 1)
    ]))
    return true
  }
}

export const questionPlugin: MarkdownConfig = {
  defineNodes: [{
    name: "Question",
    style: questionTag
  }, {
    name: "Question-marker",
    style: questionMarkerTag
  }, {
    name: "Answer",
    style: answerTag
  }, {
    name: "Answer-marker",
    style: answerMarkerTag
  }],
  parseBlock: [{
    name: "Question",
    leaf(cx, leaf) {
      return /^\? /.test(leaf.content) && (cx.parentType().name === "ListItem")
        ? new QuestionParser()
        : null
    },
    after: "SetextHeading"
  }, {
    name: "Answer",
    leaf(cx, leaf) {
      return /^@ /.test(leaf.content) && (cx.parentType().name === "ListItem")
        ? new AnswerParser()
        : null
    },
    after: "SetextHeading"
  }]
}

class DefinitionParser implements LeafBlockParser {
  nextLine() { return false }

  finish(cx: BlockContext, leaf: LeafBlock) {
    const termLength = leaf.content.indexOf('}') - 1;
    const termEndIndex = leaf.start + termLength + 2;
    cx.addLeafElement(leaf, cx.elt("Definition", leaf.start, leaf.start + leaf.content.length, [
      cx.elt("Definition-marker", leaf.start, leaf.start + 1),
      cx.elt("Definition-term", leaf.start + 1, leaf.start + termLength + 1),
      cx.elt("Definition-marker", leaf.start + termLength + 1, termEndIndex),
      ...cx.parser.parseInline(leaf.content.slice(termLength + 3), termEndIndex + 1)
    ]))
    return true
  }
}

export const definitionPlugin: MarkdownConfig = {
  defineNodes: [{
    name: "Definition",
    style: definitionTag
  }, {
    name: "Definition-term",
    style: definitionTermTag
  }, {
    name: "Definition-marker",
    style: definitionMarkerTag
  }],
  parseBlock: [{
    name: "Definition",
    leaf(cx, leaf) {
      return /^\{[\p{L}\-_+&*:()/' \w]*?\} /u.test(leaf.content) && (cx.parentType().name === "ListItem")
        ? new DefinitionParser()
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
        if (
          (
            ![40, 49, 50 /* `(,1,2` */].includes(next) &&
                    (next !== 32 ||
                      cx.char(pos + 1) !== 45 ||
                      cx.char(pos + 2) !== 62 ||
                      cx.char(pos + 3) !== 32
                    )
          ) || (
            !(match = /^( -> )?(\(?)\b((-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9]))\b(\)?)/.exec(cx.slice(pos, cx.end)))
          )
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

// An extension that highlights
// ISO 8604 date stamps for element metadata
export const todayPlaceholderPlugin: MarkdownConfig = {
  defineNodes: [{
    name: "TodayPlaceholder",
    style: todayPlaceholderTag
  }],
  parseInline: [
    {
      name: "TodayPlaceholder",
      parse(cx, next, pos) {
        let match: RegExpMatchArray | null
        if (next !== 92 /* `\` */ ||
           !(match = /^\\today/.exec(cx.slice(pos, cx.end)))
        ) {
          return -1
        }

        return cx.addElement(cx.elt("TodayPlaceholder", pos, pos + match[0].length,
          []
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
    style: latexInlineTag
  }, {
    name: "Latex-block",
    style: latexBlockTag
  },{
    name: "LatexMark",
    style: latexMarkTag
  }],
  parseInline: [
    {
      name: "Latex-inline",
      parse(cx, next, pos) {
        // let match: RegExpMatchArray | null
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
    style: locationLatLonTag
  },{
    name: "Location-longitude",
    style: locationLatLonTag
  },{
    name: "Location-name",
    style: locationNameTag
  },{
    name: "Location-delimiter",
    style: locationMarkTag
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
