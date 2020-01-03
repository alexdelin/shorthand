import codecs

from note_parser.todo_tools import parse_todo
from note_parser.tag_tools import extract_tags


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
                todo_element = get_todo_element(markdown_line)
                html_content_lines.append(todo_element)
                continue

        # Process Questions & Answers
        if len(markdown_line) >= 2:
            if markdown_line.strip()[:2] in ['? ', '@ ']:
                question_element = get_question_element(markdown_line)
                html_content_lines.append(question_element)
                continue

        # Process Definitions

        # Process Headings for Navigation
        if markdown_line[0] == '#':
            split_heading = markdown_line.split(' ', 1)
            element_id = split_heading[1].replace(' ', '-')
            heading_html_line = f'{markdown_line}<div id="{element_id}"></div>'
            html_content_lines.append(heading_html_line)
            continue

        # Catch-all for everything else
        html_content_lines.append(markdown_line)

    html_content = '\n'.join(html_content_lines)
    return html_content


def get_todo_element(raw_todo):
    '''Get a rendered HTML element for a todo given
    its properties
    '''

    todo = parse_todo(raw_todo.strip())
    leading_spaces = len(raw_todo) - len(raw_todo.lstrip(' '))

    status = todo['status']
    text = todo['todo_text']
    start = todo['start_date']
    end = todo['end_date']
    tags = todo['tags']
    tag_elements = ''.join([f'<span class="badge">{tag}</span>' for tag in tags])
    if status == 'incomplete':
        icon = '<i class="material-icons">check_box_outline_blank</i>'
    elif status == 'complete':
        icon = '<i class="material-icons">check_box</i>'
    else:
        icon = '<i class="material-icons">indeterminate_check_box</i>'

    todo_element = f'- <span style="display: none;">a</span>' \
                   f'<div class="row todo-element todo-{status}">' \
                   f'<div class="col-md-1">{icon}</div>' \
                   f'<div class="col-md-7">{text}</div>' \
                   f'<div class="col-md-4 todo-meta">{tag_elements}<br />{start} -> {end}</div>' \
                   f'</div>'

    todo_element = (' ' * leading_spaces) + todo_element
    return todo_element


def get_question_element(raw_question):
    '''Get rendered HTML for a question given its properties
    '''

    if raw_question.strip()[:2] == '? ':
        element_type = 'question'
        icon = '<i class="material-icons">help_outline</i>'
    if raw_question.strip()[:2] == '@ ':
        element_type = 'answer'
        icon = '<i class="material-icons">subdirectory_arrow_right</i>'

    text = raw_question.strip()[2:]
    tags, text = extract_tags(text)
    tag_elements = ''.join([f'<span class="badge">{tag}</span>' for tag in tags])

    leading_spaces = len(raw_question) - len(raw_question.lstrip(' '))

    # question_element = f'- <div class="qa-element">{element_type}: {}</div>'
    question_element = f'- <span style="display: none;">a</span>' \
                       f'<div class="row qa-element qa-{element_type}">' \
                       f'<div class="col-md-1">{icon}</div>' \
                       f'<div class="col-md-9">{text}</div>' \
                       f'<div class="col-md-2 question-meta">{tag_elements}</div>' \
                       f'</div>'

    question_element = (' ' * leading_spaces) + question_element
    return question_element


def get_file_content(file_path):
    '''Get the raw unmodified contents of a
    note file
    '''

    with codecs.open(file_path, mode='r', encoding="utf-8") as file_object:
        file_content = file_object.read()

    return file_content

