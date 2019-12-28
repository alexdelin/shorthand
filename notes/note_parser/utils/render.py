import codecs

from note_parser.todo_tools import parse_todo


def get_rendered_markdown(markdown_content):
    '''Pre-render all non-standard notes file
    elements into HTML
    '''

    html_content_lines = []
    markdown_content_lines = markdown_content.split('\n')
    is_fenced_code_block = False
    for markdown_line in markdown_content_lines:

        # Handle empty or pseudo-empty lines
        if not markdown_line.strip():
            html_content_lines.append(markdown_line)
            continue

        # Handle edges of fenced code blocks
        if markdown_line[:3] == '```':
            is_fenced_code_block = not is_fenced_code_block
            html_content_lines.append(markdown_line)
            continue

        # Handle contents of fenced code blocks
        if is_fenced_code_block:
            html_content_lines.append(markdown_line)
            continue

        # Process All to-dos
        if len(markdown_line) >= 4:
            if markdown_line.strip()[:4] in ['[ ] ', '[X] ', '[S] '] or markdown_line.strip()[:3] == '[] ':
                parsed_todo = parse_todo(markdown_line.strip())
                leading_spaces = len(markdown_line) - len(markdown_line.lstrip(' '))

                todo_element = get_todo_element(parsed_todo, leading_spaces)
                html_content_lines.append(todo_element)
                continue

        # Process Questions & Answers
        if len(markdown_line) >= 2:
            if markdown_line.strip()[:2] in ['? ', '@ ']:
                if markdown_line.strip()[:2] == '? ':
                    element_type = 'question'
                if markdown_line.strip()[:2] == '@ ':
                    element_type = 'answer'
                question_element = f'- <div class="qa-element">{element_type}: {markdown_line.strip()[2:]}</div>'
                html_content_lines.append(question_element)
                continue

        # Process Definitions

        # Catch-all for everything else
        html_content_lines.append(markdown_line)

    html_content = '\n'.join(html_content_lines)
    return html_content


def get_todo_element(todo, leading_spaces=0):
    '''Get a rendered HTML element for a todo given
    its properties
    '''

    status = todo['status']
    text = todo['todo_text']
    start = todo['start_date']
    end = todo['end_date']
    tags = todo['tags']
    tag_elements = ''.join([f'<span class="badge">{tag}</span>' for tag in tags])

    todo_element = f'- <span style="display: none;">a</span>' \
                   f'<div class="row todo-element todo-{status}">' \
                   f'<div class="col-md-8">{text}</div>' \
                   f'<div class="col-md-4 todo-meta">{tag_elements}<br />{start} -> {end}</div>' \
                   f'</div>'

    todo_element = (' ' * leading_spaces) + todo_element
    return todo_element


def get_file_content(file_path):
    '''Get the raw unmodified contents of a
    note file
    '''

    with codecs.open(file_path, mode='r', encoding="utf-8") as file_object:
        file_content = file_object.read()

    return file_content

print(get_rendered_markdown(get_file_content('/Users/alexdelin/notes/sample.note')))
