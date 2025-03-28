import re
import json
import logging
from typing import TypedDict

from shorthand.elements.todos import parse_todo
from shorthand.tags import extract_tags
from shorthand.utils.rec import load_from_string
from shorthand.utils.patterns import DEFINITION_PATTERN, \
                                     INTERNAL_LINK_PATTERN, GPS_PATTERN, \
                                     IMAGE_PATTERN, CATCH_ALL_PATTERN, \
                                     QUESTION_OR_ANSWER, START_STAMP_PATTERN
from shorthand.utils.paths import parse_relative_link_path, is_external_path

todo_regex = re.compile(CATCH_ALL_PATTERN)
question_regex = re.compile(QUESTION_OR_ANSWER)
definition_regex = re.compile(DEFINITION_PATTERN)
internal_link_regex = re.compile(INTERNAL_LINK_PATTERN)
image_regex = re.compile(IMAGE_PATTERN)
gps_regex = re.compile(GPS_PATTERN)
timestamp_regex = re.compile(START_STAMP_PATTERN)
leading_whitespace_regex = re.compile(r'^[ \t]*')


log = logging.getLogger(__name__)


def rewrite_image_path(matchobj, note_path):
    '''Consumes a regex match object for an image tag
    - If the image location is external, returns the image
      tag unmodified
    - If the image location is internal, modifies the image
      location to reference the frontend endpoint used
    '''
    image_title = matchobj.group(1)
    image_target = matchobj.group(2)

    if is_external_path(image_target):
        # External image target, nothing to do
        pass
    elif image_target.startswith('/'):
        # Full path to internal target
        image_target = '/api/v1/resource?path=' + image_target
    else:
        # Relative path to internal image
        # We can't deal with this without knowing
        #     the path to the note we are rendering!
        image_target = '/api/v1/resource?path=' + \
                       parse_relative_link_path(note_path, image_target)
    return f'![{image_title}]({image_target})'


def replace_link_path(matchobj, note_path):
    '''Consumes a regex match object for a internal link
    '''
    if matchobj.group(3).endswith('.note'):
        # Links to notes go to the view page
        element = '{g1}{g2}/view?path={g3}{g5}'.format(
            g1=matchobj.group(1),
            g2=matchobj.group(2),
            g3=parse_relative_link_path(note_path, matchobj.group(3)),
            g5=matchobj.group(5))
    else:
        # Links to resources go to the download API
        element = '{g1}{g2}/api/v1/resource?path={g3}{g5}'.format(
            g1=matchobj.group(1),
            g2=matchobj.group(2),
            g3=parse_relative_link_path(note_path, matchobj.group(3)),
            g5=matchobj.group(5))
    return element


class RenderedMarkdown(TypedDict):
    file_content: str
    toc_content: str


def get_rendered_markdown(markdown_content, note_path) -> RenderedMarkdown:
    '''Pre-render all non-standard notes file
       elements into HTML

       markdown_content: Raw unprocessed note content
       note_path: Relative path within the notes directory
                  of the markdown file being rendered
    '''

    html_content_lines = []
    toc_content_lines = []
    markdown_content_lines = markdown_content.split('\n')
    is_fenced_code_block = False
    is_diagram_block = False
    is_rec_data_block = False
    is_equation_block = False
    rec_data_lines = []

    for idx, markdown_line in enumerate(markdown_content_lines):

        line_number = idx + 1
        # Add whitespace at the beginning of the span line to
        # match the content line indent level
        span_whitespace = ''
        leading_whitespace_match = leading_whitespace_regex.match(markdown_line)
        if leading_whitespace_match:
            span_whitespace = leading_whitespace_match.group(0)

        line_span = f'{span_whitespace}<span id="line-number-{line_number}"></span>'

        # Grab everything for record sets
        if markdown_line.strip()[:3] != '```' and is_rec_data_block:
            rec_data_lines.append(markdown_line)
            html_content_lines.append(line_span)
            continue

        # Special handling for diagram blocks
        if is_diagram_block and '```' not in markdown_line:
            if not markdown_line.strip():
                # Skip empty lines
                continue
            else:
                # Get rid of any indentation so it doesn't trip up the
                # Markdown parser into creating new paragraphs which
                # mess up mermaid
                html_content_lines.append(markdown_line.strip())
                continue

        # Handle empty or pseudo-empty lines
        if not markdown_line.strip():
            html_content_lines.append(markdown_line)
            continue

        # Handle edges of fenced code blocks
        if markdown_line.strip()[:3] == '```':

            # Special handling for record sets
            if markdown_line.strip()[:11] == '```rec-data':
                is_rec_data_block = True
                continue
            elif is_rec_data_block:
                is_rec_data_block = False
                record_set = load_from_string('\n'.join(rec_data_lines))
                record_set_data = json.dumps(list(record_set.all()))
                column_config = json.dumps(record_set.get_fields())
                record_set_name = record_set.get_config().get(
                    'rec', {}).get('name')
                if record_set_name:
                    html_content_lines.append(f'##### Record Set: ' +
                                              f'{record_set_name}')
                record_set_html = (
                    f'<div class="record-set">' +
                    f'<div class="record-set-data">{record_set_data}</div>' +
                    f'<div class="record-set-columns">{column_config}</div>' +
                    f'<div class="record-set-display"></div>' +
                    f'</div>')
                html_content_lines.append(record_set_html)
                html_content_lines.append(line_span)
                rec_data_lines = []
                continue

            is_fenced_code_block = not is_fenced_code_block
            html_content_lines.append(markdown_line)
            continue

        # Handle contents of fenced code blocks
        if is_fenced_code_block:
            html_content_lines.append(markdown_line)
            continue

        # Process internal links
        markdown_line = internal_link_regex.sub(
            lambda match: replace_link_path(match, note_path),
            markdown_line)

        # Process internal images
        markdown_line = image_regex.sub(
            lambda match: rewrite_image_path(match, note_path),
            markdown_line)

        if gps_regex.search(markdown_line):
            markdown_line = gps_regex.sub(
                '<location lat="\\g<2>" lon="\\g<4>">' +
                '<span class="location-name"><i class="bi-geo-fill"></i>\\g<6></span>' +
                '(<span class="location-coordinates">\\g<2>, \\g<4></span>)' +
                '</location>',
                markdown_line)

        # Process All to-dos
        if len(markdown_line) >= 6:
            if todo_regex.match(markdown_line):
                html_content_lines.append(line_span)
                todo_element = get_todo_element(markdown_line)
                html_content_lines.append(todo_element)
                continue

        # Process Questions & Answers
        if len(markdown_line) >= 2:
            if question_regex.match(markdown_line):
                html_content_lines.append(line_span)
                question_element = get_question_element(markdown_line)
                html_content_lines.append(question_element)
                continue

        # Process Definitions
        definition_match = definition_regex.match(markdown_line)
        if definition_match:
            html_content_lines.append(line_span)
            definition_element = get_definition_element(definition_match,
                                                        markdown_line)
            html_content_lines.append(definition_element)
            continue

        # Process Headings for Navigation
        if markdown_line[0] == '#':
            split_heading = markdown_line.split(' ', 1)
            heading_level = len(split_heading[0])
            element_id = split_heading[1].replace(' ', '-')
            heading_div = f'<span id="{element_id}"></span>'
            toc_markdown_line = (f'{"  " * (heading_level - 1)}- ' +
                                 f'[{split_heading[1]}](#{element_id})')
            html_content_lines.append(line_span)
            html_content_lines.append(heading_div)
            html_content_lines.append(markdown_line)
            toc_content_lines.append(toc_markdown_line)
            continue

        # Special handling for markdown tables
        if markdown_line.lstrip()[0] == '|':
            # Adding span tags into a table will break it, so we exclude them
            html_content_lines.append(markdown_line)
            continue

        # Handle edges of equation blocks
        if not is_equation_block and markdown_line.strip().startswith('$$') \
                and not markdown_line.strip().endswith('$$'):
            is_equation_block = True
            html_content_lines.append(markdown_line)
            continue
        elif is_equation_block and not markdown_line.strip().startswith('$$') \
                and markdown_line.strip().endswith('$$'):
            is_equation_block = False
            html_content_lines.append(markdown_line)
            continue
        elif is_equation_block and not markdown_line.strip().endswith('$$'):
            html_content_lines.append(markdown_line)
            continue

        # Catch-all for everything else
        html_content_lines.append(line_span)
        html_content_lines.append(markdown_line)

    html_content = '\n'.join(html_content_lines)
    toc_content = '\n'.join(toc_content_lines)

    return {
        'file_content': html_content,
        'toc_content': toc_content
    }


def get_todo_element(raw_todo):
    '''Get a rendered HTML element for a todo given
    its properties
    '''

    todo = parse_todo(raw_todo.strip()[2:])
    leading_spaces = len(raw_todo) - len(raw_todo.lstrip(' '))

    status = todo['status']
    text = todo['todo_text']
    start = todo['start_date']
    end = todo['end_date']
    tags = todo['tags']
    tag_elements = ''.join([f'<span class="tag">{tag}</span>'
                            for tag in tags])
    if status == 'incomplete':
        icon = '<i class="bi-square"></i>'
    elif status == 'complete':
        icon = '<i class="bi-check-square-fill"></i>'
    else:
        icon = '<i class="bi-dash-square-fill"></i>'

    todo_timestamp = f'<div class="todo-start-date">{start}</div>'
    if end:
        todo_timestamp += (f' <i class="bi-arrow-right"></i>' +
                           f' <div class="todo-end-date">{end}</div>')

    todo_element = (f'- <span style="display: none;">a</span>' +
                    f'<div class="todo-element todo-{status}">' +
                    f'<div class="todo-icon">{icon}</div>' +
                    f'<div class="todo-text">{text}{tag_elements}</div>' +
                    f'<div class="todo-timestamp">{todo_timestamp}</div>' +
                    f'</div>')

    todo_element = (' ' * leading_spaces) + todo_element
    return todo_element


def get_question_element(raw_question):
    '''Get rendered HTML for a question given its properties
    '''

    if raw_question.strip()[2] == '?':
        element_type = 'question'
        icon = '<i class="bi-question-octagon"></i>'
    elif raw_question.strip()[2] == '@':
        element_type = 'answer'
        icon = '<i class="bi-arrow-return-right"></i>'
    else:
        log.error(f'Got invalid question {raw_question}')
        return ''

    text = raw_question.strip()[4:]
    tags, text = extract_tags(text)
    timestamp, text = extract_timestamp(text)
    tag_elements = ''.join([f'<span class="tag">{tag}</span>'
                            for tag in tags])

    leading_spaces = len(raw_question) - len(raw_question.lstrip(' '))

    question_element = (f'- <span style="display: none;">a</span>' +
                        f'<div class="qa-element qa-{element_type}">' +
                        f'<div class="qa-icon">{icon}</div>' +
                        f'<div class="qa-text">{text}{tag_elements}</div>' +
                        f'<div class="qa-timestamp"><div class="qa-create-date">{timestamp}</div></div>' +
                        f'</div>')

    question_element = (' ' * leading_spaces) + question_element
    return question_element


def get_definition_element(definition_match, markdown_line):
    term = definition_match.group(3)
    term = term.strip().strip('{}')
    tags, definition = extract_tags(definition_match.group(4))
    tag_elements = ''.join([f'<span class="tag">{tag}</span>'
                            for tag in tags])

    leading_spaces = len(markdown_line) - len(markdown_line.lstrip(' '))

    element = (f'- <span style="display: none;">a</span>' +
               f'<div class="definition-element">' +
               f'<div class="definition-term">{term}</div>' +
               f'<div class="definition-text">{definition}{tag_elements}</div>' +
               f'</div>')

    element = (' ' * leading_spaces) + element
    return element


def extract_timestamp(text):

    timestamp = None

    timestamp_match = timestamp_regex.search(text)
    if timestamp_match:
        timestamp = timestamp_match.group(0).strip('()')
        text = timestamp_regex.sub('', text)
        return timestamp, text
    else:
        return timestamp, text

