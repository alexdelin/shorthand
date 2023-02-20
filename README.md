# Shorthand
Shorthand is a note-taking and personal organization tool. Yes... another one

Its based off of the idea that taking notes in plain-text formats (markdown) is great, and simpler is better when it comes to tooling that you use every day to stay organized. 

## Why another note-taking tool?
There are already a lot of great tools out there, and Shorthand was inspired by many of them. However, most tools fall into one of these two buckets:
1. Ways to turn plain-text notes into polished documents that look great and you can share with other people
2. Easy ways to retrieve info you need from your notes

Particularly for the first bucket, there are _a lot_ of very good solutions. Even rendering basic markdown into HTML does a pretty good job. 

For the second category, there is a much more limited number of tools that **both** do a good job and are simple to understand. Even more common is for these to be workflow-specific (task managers, etc.) in which case you are forced to split out your data across multiple tools

## So, what is it?
Shorthand is both a plain text syntax (that is very close to markdown-GFM, but with a few additions) and a tool for retrieving elements from notes written in that syntax.

The idea is for notes to be both documents that can be displayed nicely, but also _plain text databases_ from which you can retrieve info (todos, definitions, etc.) later on when you need to.

### Syntax
The starting point for Shorthand's syntax is Github-flavored markdown. 

The only major restriction that Shorthand syntax adds is that long lines should **not** be broken. Many elements are defined as _lines_ that match a given pattern, and content that continues in the following lines won't be included when the element is retrieved.

#### Headings
While Markdown supports both setex (underlined) and atx headings, Shorthand only supports atx headings with no closing `#` characters at the end of the line

```
# A section
## A subsection
```

#### Todos
Just like in Github flavored markdown, Todos are structured as list elements. 
```
- [ ] Something to do
```
The character inside of the brackets indicates the state of the todo:
- None or a space: an incomplete todo
- `X`: A Completed todo
- `S`: A Skipped todo

#### Definitions
Definitions are also list elements, with the term in braces followed by the definition
```
- {Term} Definition
```

#### Tags
Tags are an optional way to assign metadata to elements, which you can specify later when searching for elements.

```
- [ ] Something to do :tag:
```

#### Timestamps
Timestamps are an optional way to keep track of when specific content was created. All timestamps are ISO 8601 format dates, and can be added to specific elements

Timestamps can be added to headings to indicate the date that a given section was created, or relates to. This is particularly useful for keeping track of things like meetings
```
# A meeting 2023-02-16
```

Todos can have timestamps for both when the todo was created, and when it was marked completed or skipped. Both timestamps are in parentheses before the content of the todo, with an arrow `->` between them for completed or skipped todos
```
- [ ] (2023-02-16) Something to do
- [X] (2023-02-16 -> 2023-02-16) Something Done
```

### Elements / Retrieval
The simplest possible way to retrieve things from a plain text file is to find lines that match a specific pattern. This is an approach that has had a well-known and easy to understand implementation for _decades_ already (`grep`).

As you may have guessed, the only "backend" for retrieving elements from notes is `grep`. No relational database, no extra added complexity, just `grep`. This has some downsides (discussed below), but for individuals or small groups of users the advantages of simplicity far outweigh the downsides. 

Because of how simple the design is, retrieval is very fast, and even more complicated features like a graph of links between notes can be built fairly easily using this approach.

### Disadvantages / Downsides
Because of the simplicity of the approach taken, there are some issues which may come up and edge cases which are explicitly not covered. Some of these are:
- Code blocks could theoretically have lines that match the patterns for elements, and will be returned as elements even though they aren't elements.
- Because the backend of shorthand is a directory of plain-text files and not a database, the backend does not provide a full set of ACID guarantees, and is not suitable for a large number of concurrent users
