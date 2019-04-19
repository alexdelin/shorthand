# Noteparser Format Specification
This document defines the "Note" format for note-taking and personal organization based roughly on markdown.
The origin of many of the elements added here are practices that are common with pen and paper note-taking, but lack good equivalents in digital note-taking tools and personal organization tools.

## Design Principles
1. All source data should be stored in a portable human-readable format. Moving your notes should be as easy as moving a directory and should not require knowing any additional query language. Viewing the primary data source should require only opening a note file with any common text editor.
2. The syntax should be simple enough that anyone can write notes in this format with minimal training. Notes should be readable and writable in a basic text editor without any fancy tooling like syntax highlighting or macros.
3. Note format notes are explicitly designed to **not** be rendered into a web page or other display format. The need to render files written in other markup languages into display formats creates a number of unnecessary elements and increases the complexity of the format in a way that does more damage than good.
4. The syntax should be based on how to best accurately capture and retrieve information at a later date, not just blindly implement fancy new features.
5. The language should be as minimal as possible. Markup languages have defined lots of different ways of doing the same few things, with most markup languages supporting multiple options for each. Note format adopts the C-style idea that a language should provide one way and **only one way** to do everything.

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

#### Bold
#### Italics
#### Underline
#### Strikethrough

### Lists
#### Itemized Lists
#### Enumerated lists

### Quotes

### Code Samples

### Questions

### ToDos

### Tags
