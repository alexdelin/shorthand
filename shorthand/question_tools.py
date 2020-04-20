import re
import logging
from subprocess import Popen, PIPE

from shorthand.utils.patterns import ALL_QUESTIONS_GREP, ANSWER_PATTERN, \
                                       escape_for_grep


ANSWER_REGEX = re.compile(ANSWER_PATTERN)


log = logging.getLogger(__name__)


def is_question_line(line_content):
    # If a `:` character occurs before the first space,
    # it's an output line for a match
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
            if notes_directory in file_path:
                file_path = file_path[len(notes_directory):]

            parsed_question = {
                'file_path': file_path,
                'line_number': line_number,
                'question': question_text,
                'answer': None
            }

            # If the next line is an answer line, add the answer
            # text as metadata to the question
            if idx < len(output_lines) - 1:
                is_answer, answer_content = is_answer_line(output_lines[idx + 1])
                if is_answer:
                    parsed_question['answer'] = answer_content
            else:
                is_answer = False

            if question_status == 'all':
                parsed_questions.append(parsed_question)
            elif question_status == 'answered' and is_answer:
                parsed_questions.append(parsed_question)
            elif question_status == 'unanswered' and not is_answer:
                parsed_questions.append(parsed_question)

    return {
        "items": parsed_questions,
        "count": len(parsed_questions)
    }
