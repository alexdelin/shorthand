# Shorthand Format Specification
This document defines the Shorthand "Note" format for note-taking and personal organization based on markdown.
The origin of many of the elements added here are practices that are common with pen and paper note-taking, but lack good equivalents in digital note-taking tools and personal organization tools.

This isn't meant to be an argument that this is the "best" way of organizing information, or that everyone should switch to taking notes this way. Note taking is a very personal thing that everyone has to figure out for themselves. 

## Evolution
Shorthand was developed over a period of 7 years trying to stay organized while working at startups, with the first 4 years being pen & paper focused and the next 3 years being markdown focused. 

### Pen & Paper
I was originally attracted to writing things down by hand because I liked the freedom of being able to quickly jot down things like equations or diagrams to help me think about a problem clearly.

Aside from these diagrams or equations, my notes were overwhelmingly taken in bulleted-list format, which were usually broken out into sections for specific topics or meetings, and usually were either flat lists or had shallowly-nested structure.

Even with mostly ephemeral content, I did find that I had a few things that I needed to be able to come back to later on, whether they were tasks or especially useful reference material. In these cases I would add colored tabs on the page for the thing I wanted to come back to, and color-code them based on what in particular it was. After a few months of regular use, I had a notebook that looked something like ![this](https://www.istockphoto.com/photo/colorful-bookmarks-for-documents-with-notebook-closeup-of-colour-tabs-for-bookmarks-gm937183578-256357070)

At first I kept changing the categories and colors for the tabs, but settled on this small group:
- Red: Things I had to remember to do
- Green: Open Questions that I had to remember to find the answer to
- Yellow: Definitions, explanations, designs, or other things that I would probably need to refer back to later

For such a simple system, it worked surprisingly well. I always felt confident that I was on top of what needed to either get done or figured out, and the most critical info that I needed to remember was in a place where I could get at it very quickly when I needed.

Over time, the yellow category in particular became more and more of a problem. A series of tabs sticking out from the side of a notebook is manageable when you have a dozen or so different definitions that you can look through to find one particular one, but as the number of tabs gets into the hundreds, it no longer becomes workable.

For this same reason, the red & green categories continued to be manageable for a very long time, as the number of active todos or open questions never got higher than a few dozen maximum.

The second issue with the yellow tabs came when it was time to write up formal designs for things that I had yellow tabs for in my notes. Formal designs were going to need to be done digitally, and would have no connection to my original definitions, the notes I took on the meetings about the thing being designed, or the various todos that I'd worked through in order to create or update the design. 

I really liked the idea of notes telling the complete story and being something that could be referenced later on. Having the info on a given topic split between a digital document and hand-written notes in a notebook made it hard to remember why changes were made and projects evolved the way that they did. The notes needed to be treated as a system of record rather than an ephemeral cache of in-progress todos and open questions. 

How do you easily find something that you know was a todo at some point, but was completed between 9 and 12 months ago? Or find notes on a meeting that happened maybe around 3 months ago? Or easily flip between the lists of tasks or questions you worked through while designing something and the finished design doc?

### Digital
When it became obvious that searching and retrieving past notes was more valuable than I originally realized, it was natural to switch to a digital format. I resisted this for a long time, because I had been burned by trendy note-taking or todo-tracking apps in the past, and always struggled with them either not being expressive enough to be useful or just ending up as another small "silo" that ~10% of the info I needed was in, which didn't play nicely with any of the other "silos" that my info was in. 

I already had lots of digital data scattered around in lots of different places, so I wasn't eager to add another format or location and wanted to be extremely careful about how a new one looked. A rough estimate of what I had at this point would be:
- 50% Google Docs on a Google Drive for Education (because it had free unlimited storage until Summer 2022). Of these, the breakdown of doc types was roughly:
    + 55% Drawings, which were usually very simple flowcharts that I used either for keeping track of something in my head or using as a visual aid to explain something.
    + 30% Text documents, which were typically formal documents on either projects I had worked on (like this), personal records, or old meeting notes, etc. that I used to keep in google docs.
    + 10% Presentations
    + 5% Spreadsheets
- 20% My hand-written notes mentioned above
- 15% LaTeX documents, which were often duplicates of the text documents that I had in Google Docs, for the cases where I either wanted something nicer looking to share or had a lot of math to include.
- 10% Previous personal organization / note taking apps I had tried but abandoned. Among these were:
    + Evernote
    + Wunderlist
    + Pocket Informant
    + MS OneNote
    + Notability
    + Google Keep
    + Notion
- 5% Other Misc. (usually legacy) data formats

I didn't like the idea of my personal data being scattered all over the place, and came up with a few principles that the new format should have:
- Usable for both ephemeral elements like todos and open questions, as well as long-form formal documents, designs, etc.
- Zero vendor lock-in. Getting my data out from some of the note-taking solutions I had used was a pain and I didn't want to go through that again.
- Notes should live in the simplest possible plain-text format, to make migrating to or from this format as easy as possible. Notes should just be a bunch of files stored in directories that you can organize as you see fit. There should be no database schemas or APIs to have to understand to migrate in or out of this format.

Fortunately, there are lots of people who have also thought deeply about the same problem, and many who have arrived at the same or similar principles. From even the quickest skimming of the popular options for solving this problem in 2022, it will be clear that markdown has become the widely-chosen format for those who have these concerns. It's obviously capable of meeting the barebones requirements which are needed for authoring long-form documents, and has all of the basic text and document formatting figured out in an easy to use way. 

The question is, how can you use markdown to create a todo-list app? Or create a [simple] diagramming or flowchart like in google drawings? Or a simple spreadsheet or table if you need one?

Some of these are supported in some way via markdown additions, like Github's [task list item](https://github.github.com/gfm/#task-list-items-extension-) extension, which gives you an easy way to have a list element _render_ as a task list or todo item. But how do you _get_ a list of all of your open todos if you track them this way? You can grab all of the lines that have the form `<zero-or-more-spaces><+-*> <[ ]> <text>`, but will that work well enough to be useful? Will you get a ton of false positives? 

The switch to markdown was gradual for about a month, then happened all at once. Once I wrote all my new notes in markdown for a few weeks, I decided to port everything over. Exporting from Google Docs -> Word Docs was easy, then those could be converted to markdown via pandoc and the process was basically done. I had few enough active todos that I could migrate those manually, and never bothered to migrate completed todos over. After a weekend I had everything moved over to markdown and never looked back.

## Design Principles
1. All source data should be stored in a portable human-readable format. Moving your notes should be as easy as moving a file or directory and should not require anything along the lines of writing custom DB queries, etc. Viewing the primary data source / "ground truth" should require only opening a note file with any common text editor, or even `cat` from the command line.
2. The syntax should be simple enough that anyone _can_ write notes in this format with minimal training. Notes should be readable and writable in a basic text editor (vi, notepad on windows, etc.) without any fancy tooling like syntax highlighting or macros. Obviously things like syntax highlighting should be used to make things easier, but it should still be possible for an average user to write notes without them.
3. Notes function as "plain-text databases", in that the syntax should enable **easy** retrieval of information at a later date via simple tooling. This is accomplished by inserting elements into notes which can be retrieved at a later date by finding lines or substrings within lines that match a regex pattern.
    + The _secondary_ purpose of the syntax is to allow for notes to be rendered into a nicely-displayed 
4. The de-facto "backend" for retrieving elements is `grep`. All elements which can be retrieved are defined in terms of a regex pattern which matches either a) an entire line; or b) a substring within a single line.
    + To keep the content of the notes themselves the ground truth, state should not live anywhere else besides the notes.
    + The use of `grep` results in inherently imperfect results for certain operations, because other lines (particularly in code blocks) may in rare cases match the patterns defined for elements. This is a downside, but the benefits of much simpler retrieval and a simpler implementation outweigh the downsides.
5. Lines are a first-class citizen in the syntax and should never be broken for display purposes (arbitrary line length rules, etc.). Breaking lines at arbitrary lengths makes parsing markup files artificially difficult and makes it impossible to reliably retrieve entire elements via `grep` or similar tools. A large single element should be put on a single line wherever possible to make parsing and later retrieval easier.
6. Note format notes are explicitly designed to store information in the simplest way possible. Features are based on recording information such that the source can be written, read, and parsed as easily as possible, even if doing so is naïve. There will be some cases where content within notes is incorrectly identified as an element like a todo or a question, and this is expected (although very rare). However, the format is simple enough that these issues will be obvious and can very easily be fixed. ~~Rendering a note into a display version is a second-class consideration compared to storing information clearly and supporting easy retrieval of elements. The need to render files written in other markup languages into display formats creates a number of unnecessary elements and increases the complexity of the format in a way that does more damage than good.~~
7. The language should be as minimal as possible. Markup languages have defined lots of different ways of doing the same few things, with most markup languages supporting multiple options for each based on arbitrary personal preferences of users. Shorthand's note format is closer to the C-style idea that a language should provide one way and **only one way** to do everything. Some elements have syntaxes that are more restricted than markdown in order to a) make parsing these elemetns as simple as possible; and b) ensure that the elements are always self-contained on a single line

### Notes vs. Resources
The primary version of all shorthand data is a single directory on disk. The contents of this directory, as you may expect, are just sub-directories and a bunch of files on disk. For the files present, there is a special distinction between files with a `.note` extension, and everything else. The files with the `.note` extension are termed "Notes", while everything else is a "Resource". These two categories will have separate APIs, and the core functionality is only geared to work against notes. 

Resources are still useful for providing things like images, audio, video, or other things you may want to be stored alongside your notes. However, storing your notes with a file extension other than `.note` will cause problems or result in you not finding the content you expect when using the Notes APIs.

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
Because all letters are valid leading characters, roman numerals can also be used for other styling options
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
Indented code blocks are not valid syntax

### List Extensions
Some extended markdown syntaxes, such as GFM, support additional variations of list items. In these cases, a list item that matches a pattern is treated as a different element entirely, as opposed to just a text item within the list.

Two important things to note about list extensions are:
1. List extensions only work in _itemized lists_, not _enumerated lists_
2. All elements produced via list extensions are always a single line. Line breaks cannot be inserted within them the way that they can be with other markdown elements.

#### ToDos

```notes
# Unstamped
- [] An incomplete to-do item
- [X] Another incomplete thing
- [S] An item which is no longer needed and has been skipped
- [X] An item which has been completed
```

#### Questions + Answers
Recording answered and unanswered questions are a natural part of any note-taking, and an important feature that most who take notes with a pen and paper will have a special process (colored tabs, etc.) for. Question and answer pairs are a good abstraction for individual bits of new information that should be cataloged for later retrieval, as well as current unknown which have to be figured out and addressed in the future

The simplest form of a question is any list item starting with a question mark and a space (`- ? foo`).
Because questions and their answers are intrinsically tied together, answers must be stored in predictable locations relative to the question that they are attached to. The easiest place to put an answer is on the following line, indicated by an at-sign followed by a space then the text of the answer (`- @ bar`). Questions that are followed by **any other line** are considered to have no answer tied to them and be in an "unanswered" state.
The indentation of the answer is for readability purposes only and does not have any functional impact.
```notes
- ? What is the meaning of life
    + @ 23
```
Unanswered and Answered questions side-by-side
```notes
- ? Does P = NP
- ? Another question
    + @ with an answer
```

### Definitions
```notes
- {Term} Definition
```

### Metadata
Metadata can be added to list extensions to make tracking them easier and more useful

#### Timestamps
ToDo Question, and Answer elements can include a start timestamp and an end timestamp.
Generally these timestamps are placed in parentheses right before the content of the element, and are of the format either `(creation)` or `(start -> end)`.
The start timestamp indicates the date when the element was created, and the end timestamp (for todos) indicates when the state of the element was changed to either completed or skipped.
```notes
# Stamped
[ ] (2019-05-14) An open todo which lists the date that it was created
[S] (2019-05-15 -> 2019-05-17) A skipped todo that lists the date it was created and the date that it was marked skipped
[X] (2019-05-16 -> 2019-05-20) A completed todo that lists the date it was created and the date it was marked completed
```

In addition to timestamps added to list elements, you can also add timestamps to headings. This is particularly useful when you have a section that represents a specific event, and you want to record the date of the event. 
```notes
## Weekly Client Meeting 2019-15-18
```

##### Stamping
Timestamps can be annoying to type out manually every time that you create a new todo or complete an existing one. For this reason, there is a stamping feature that will identify any missing timestamps and add them automatically with the current date. 

###### Today Placeholder
In addition to adding timestamps to elements, the stamping feature will also replace instances of the string `\today` with the current date. This can be used as a convenience feature for quickly dating elements when authoring notes. For example, the dated section example above could be written as:
```notes
## Weekly Client Meeting \today
```

#### Priority (Not Implemented)
Priority of a ToDo is indicated in braces `{priority}` right after the timestamp block and before the text of the todo item.
Priority is represented by a single digit number `1-9` with `1` being the highest priority and `9` being the lowest priority. Any ToDos with no priority listed have an implicit priority level of `5`
```notes
[ ] (2019-05-14) {1} An extremely important thing to do
[ ] (2019-05-15) {5} Something _significantly_ less important, but which also has to be done
```

#### Tags
Tags are metadata fields that can be applied to any item for easier retireval later on
```notes
Somethings that I want to find in the future :topic:
```
The element above will be tagged with the tag `topic`

### Links
The link format used is exactly the same as used in markdown, but all link targets must be specified inline. The basic link format is:
```notes
[Link Title](Link Target)
```

Links are classified into two basic categories, External Links and Internal Links.

#### External Links
An external link is any link with a target of an external URL. Shorthand will not do any validation, so all external links are considered valid
```notes
[New York Times](https://nytimes.com)
```

#### Internal Links
Internal Links are links with a target of other notes within the notes directory, such as:
```notes
[Link Title](/path/to/note.note)
```
Specific sections within the target note can be specified by adding `#Section` to the end of the target URL.

Links to internal documents can be specified as either an absolute path (`/path/to/note.note`) or a relative path (`to/note.note`) from the path of the source note.

Unlike external links, internal links are classified based on whether or not the target of the link is a note that actually exists. In cases where a section is specified in a link target, the section is **not** validated.

### Images
### Diagrams (Mermaid)
### Locations
### Databases

## Unsupported Elements
### Comments
