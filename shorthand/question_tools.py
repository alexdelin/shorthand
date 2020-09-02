import re
import logging
from subprocess import Popen, PIPE

from shorthand.tag_tools import extract_tags
from shorthand.utils.patterns import ALL_QUESTIONS_GREP, ANSWER_PATTERN, \
                                     START_STAMP_ONLY_PATTERN, escape_for_grep
from shorthand.utils.paths import get_relative_path, get_display_path


ANSWER_REGEX = re.compile(ANSWER_PATTERN)
TIMESTAMP_REGEX = re.compile(START_STAMP_ONLY_PATTERN)


log = logging.getLogger(__name__)


def is_question_line(line_content):
    '''If a `:` character occurs before the first space,
    it's an output line (from grep) for a match
    '''
    if ':' in line_content and ' ' not in line_content.split(':')[0]:
        return True
    return False


def is_answer_line(line_content):

    if line_content.strip() == '--':
        # Grep adds these lines to separate match results
        return False, None

    split_content = line_content.split('-', 2)
    if len(split_content) < 3:
        return False, None

    line_content = split_content[-1]
    answer_match = ANSWER_REGEX.match(line_content)
    if answer_match:
        answer_text = answer_match.groups()[2]
        return True, answer_text

    return False, None


def get_questions(notes_directory, question_status='all',
                  directory_filter=None, grep_path='grep'):

    question_status = question_status.lower()

    if question_status not in ['all', 'answered', 'unanswered']:
        raise ValueError('Invalid question status ' + question_status)

    parsed_questions = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    proc = Popen(
        '{grep_path} -rn -A 1 "{pattern}" {dir}'.format(
            grep_path=grep_path,
            pattern=escape_for_grep(ALL_QUESTIONS_GREP),
            dir=search_directory),
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    for idx, output_line in enumerate(output_lines):

        # Early exits
        if not output_line.strip():
            continue
        if output_line.strip() == '--':
            continue

        if is_question_line(output_line):
            split_line = output_line.split(':', 2)
            file_path = split_line[0].strip()
            line_number = split_line[1].strip()
            question_text = split_line[2].strip()[2:]

            # Return all paths as relative paths within the notes dir
            file_path = get_relative_path(notes_directory, file_path)
            display_path = get_display_path(file_path, directory_filter)

            # Extract the date stamp from the question if present
            question_date_match = TIMESTAMP_REGEX.match(question_text)
            if question_date_match:
                question_date = question_date_match.groups()[1]
                question_text = question_date_match.groups()[4]
            else:
                question_date = None

            # Extract tags from the question
            tags, clean_text = extract_tags(question_text)
            if tags:
                question_text = clean_text

            parsed_question = {
                'file_path': file_path,
                'display_path': display_path,
                'line_number': line_number,
                'question': question_text,
                'question_date': question_date,
                'answer': None,
                'answer_date': None,
                'tags': tags
            }

            # If the next line is an answer line, add the answer
            # text as metadata to the question
            if idx < len(output_lines) - 1:
                is_answer, answer_content = is_answer_line(output_lines[idx + 1])
                if is_answer:

                    # Extract the date stamp from the answer if present
                    answer_date_match = TIMESTAMP_REGEX.match(answer_content)
                    if answer_date_match:
                        answer_date = answer_date_match.groups()[1]
                        answer_content = answer_date_match.groups()[4]
                        parsed_question['answer_date'] = answer_date

                    parsed_question['answer'] = answer_content
            else:
                is_answer = False

            if question_status == 'all':
                parsed_questions.append(parsed_question)
            elif question_status == 'answered' and is_answer:
                parsed_questions.append(parsed_question)
            elif question_status == 'unanswered' and not is_answer:
                parsed_questions.append(parsed_question)

    return parsed_questions
