# Shorthand Format Specification
This document defines the "Note" format for note-taking and personal organization based roughly on markdown.
The origin of many of the elements added here are practices that are common with pen and paper note-taking, but lack good equivalents in digital note-taking tools and personal organization tools.

## Design Principles
1. All source data should be stored in a portable human-readable format. Moving your notes should be as easy as moving a directory and should not require knowing any additional query language. Viewing the primary data source should require only opening a note file with any common text editor.
2. The syntax should be simple enough that anyone can write notes in this format with minimal training. Notes should be readable and writable in a basic text editor without any fancy tooling like syntax highlighting or macros.
3. Note format notes are explicitly designed to **not** be rendered into a web page or other display format. The need to render files written in other markup languages into display formats creates a number of unnecessary elements and increases the complexity of the format in a way that does more damage than good.
4. The syntax should be based on how to best accurately capture and retrieve information at a later date, not just blindly implement fancy new features.
5. The language should be as minimal as possible. Markup languages have defined lots of different ways of doing the same few things, with most markup languages supporting multiple options for each. Note format adopts the C-style idea that a language should provide one way and **only one way** to do everything.
6. Lines should be broken as infrequently as possible. Breaking lines at arbitrary lengths makes parsing markup files artificially difficult and causes more problems than it is worth. A large single element should be put on a single line wherever possible to make parsing and later retrieval easier.

## Syntax Definition

### Headings
Of all markup languages, markdown and org-mode provide the simplest syntax for headings, which is one or more instances of a special charater followed by a space then the title of the heading. Markdown uses the special character `#` while org-mode uses the special character `*`. The special character `#` is used in Note format because it has already been the most widely accepted

#### Valid Headings
```notes
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

#### Invalid headings
Other formats and styles of headings such as the ones shown below are **not supported**

Adding an additional special character at the end of the heading
```
# Heading 1 #
```
Using any other special character
```
* Heading 1
```
Underlining
```
Heading 1
=========
```

### Text Emphasis
While text emphasis is not strictly necessary, it is one of the basic tools that help people convey information more effectively in digital formats, and is a major convenience tool to have available.
The markdown syntax for text emphasis is by far the most common, but org mode has the most options and appears to be the best designed.

#### Bold
```notes
Something **bold**
```
#### Italics
```notes
Something _italicized_
```
#### Underline
Not supported

#### Strikethrough
```notes
~~Text struck through~~
```

### Lists
#### Itemized Lists
The format for itemized (unordered lists) is exactly the same as markdown.
```notes
- A bullet point
- Another point
    + A sub-element
    + Something else at the second level
        * Something even deeper
```

#### Enumerated lists
The format for enumerated lists is an expansion of the basic form used by most most markup languages.
```notes
1. A standard markdown list element
2) Some other styling options
C. Letters as well
    a. Upper and lower case supported
        1) can nest arbitrarily deeply
```
Becaues all letters are valid leading characters, roman numerals can also be used for other sytling options
```notes
I) The first thing
II) The second thing
III) Third
    i. A sub point
    ii. another one
IV) Number four
```

### Quotes
The quote syntax in markdown is used unchanged. Quotes are lines which lead with a `>` character

```notes
Some regular text

> A quote from a very reliable source
```

### Code Samples
Code samples are unchanged from markdown, but **only** fenced code blocks are allowed. Code blocks can be fenced with 3 of either tildes or backticks
~~~notes
```format
# code goes here
def something():
    return True
```
~~~

### Questions + Answers
Recording answered and unanswered questions are a natural part of any note-taking, and an important feature that most who take notes with a pen and paper will have a special process (colored tabs, etc.) for. Question and answer pairs are a good abstraction for individual bits of new information that should be cataloged for later retrieval, as well as current unknown which have to be figured out and addressed in the future

The simplest form of a question is any string of text following a question mark and a space (`? foo`).
Because questions and their answers are intrinsically tied together, answers must be stored in predictable locations. The easiest place to put an answer is on the following line, indicated by an at-sign followed by a space then the text of the answer. Questions that are followed by **any other line** are considered to have no answer tied to them and be in an "unanswered" state.
The indentation of the answer is for readability purposes only and does not have any functional impact.
```notes
? What is the meaning of life
    @ 23
```
Unanswered and Answered questions side-by-side
```notes
? Does P = NP
? Another question
    @ with an answer
```

### ToDos
```notes
# Unstamped
[] An incomplete to-do item
[ ] Another incomplete thing
[S] An item which is no longer needed and has been skipped
[X] An item which has been completed
```

#### Metadata
Metadata can be added to todos to make tracking them easier and more useful

##### Timestamps
ToDo items can include a start timestamp and an end timestamp.
Generally these timestamps are placed in parentheses right after the opening `[ ]` and are of the format `(start -> end)`
The start timestamp indicates the
```notes
# Stamped
[ ] (2019-05-14) An open todo which lists the date that it was created
[S] (2019-05-15 -> 2019-05-17) A skipped todo that lists the date it was created and the date that it was marked skipped
[X] (2019-05-16 -> 2019-05-20) A completed todo that lists the date it was created and the date it was marked completed
```

##### Priority
Priority of a ToDo is indicated in braces `{priority}` right after the timestamp block and before the text of the todo item.
Priority is represented by a single digit number `1-9` with `1` being the highest priority and `9` being the lowest priority. Any ToDos with no priority listed have an implicit priority level of `5`
```notes
[ ] (2019-05-14) {1} An extremely important thing to do
[ ] (2019-05-15) {5} Something _significantly_ less important, but which also has to be done
```

### Tags
Tags are meteadata fields that can be applied to any item for easier retireval later on
```notes
Somethings that I want to find in the future :topic:
```
The element above will be tagged with the tag `topic`

### Definitions
```notes
{Term} Definition
```

## Unsupported Elements
### Fancy Links
Lots of other markup formats provide nice ways to format notes, which are useful for when you render notes into other formats for presentation
```notes
[Link Title](https://www.link-target.com/page.html)
```
### Comments
### Images
