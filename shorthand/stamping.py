import re
import logging
from datetime import datetime
from subprocess import Popen, PIPE

from shorthand.utils.patterns import CATCH_ALL_PATTERN, \
    VALID_INCOMPLETE_PATTERN, VALID_COMPLETE_PATTERN, \
    UNFINISHED_UNSTAMPED_PATTERN, FINISHED_START_STAMPED_PATTERN, \
    FINISHED_UNSTAMPED_PATTERN, TODAY_GREP, TODAY_LINE_PATTERN, \
    ALL_QUESTIONS, UNSTAMPED_QUESTION, STAMPED_QUESTION, \
    ANSWER_PATTERN, UNSTAMPED_ANSWER, STAMPED_ANSWER


log = logging.getLogger(__name__)


def _stamp_notes(notes_directory, stamp_todos=True, stamp_today=True,
                 stamp_questions=True, stamp_answers=True,
                 grep_path='grep'):
    '''Stamp notes for the purpose of inserting date stamps
    as a convenience feature. This function makes the following
    replacements:

    --- Incomplete Todos ---
        [] This is a sample :tag:
        [ ] (2020-01-01) This is a sample :tag:
        --or--
        [ ] This is a sample :tag:
        [ ] (2020-01-01) This is a sample :tag:

    --- Complete Todos ---
        [X] (2020-01-01) This is a sample :tag:
        [X] (2020-01-01 -> 2020-01-02) This is a sample :tag:
        --or--
        [X] This is a sample :tag:
        [X] (2020-01-02 -> 2020-01-02) This is a sample :tag:

    --- Skipped Todos ---
        [S] (2020-01-01) This is a sample :tag:
        [S] (2020-01-01 -> 2020-01-02) This is a sample :tag:
        --or--
        [S] This is a sample :tag:
        [S] (2020-01-02 -> 2020-01-02) This is a sample :tag:

    --- Date Placeholders ---
        ## This is a subsection \today
        ## This is a subsection 2020-01-01

    --- Questions ---
        ? This is a sample
        ? (2020-01-01) This is a sample

    --- Answers ---
        @ This is a sample
        @ (2020-01-01) This is a sample

    This function returns a changes object of the form:
    {
        "/file/path/1": [
            {
                "type": "incomplete_todo",
                "line_number": 51,
                "before": "[] This is a sample",
                "after": "[ ] (2020-01-01) This is a sample",
            }
        ],
        "/file/path/2": [
            {
                "type": "date_placeholder",
                "line_number": 37,
                "before": "## Section \today",
                "after": "## Section 2020-01-01",
            }
        ]
    }
    '''

    log.info('Stamping notes')
    changes = {}

    # Stamp start and end dates for todo elements
    if stamp_todos:
        grep_command = '{grep_path} -Pr "{pattern}" '\
                       '--include="*.note" --exclude-dir=\'.*\' {directory} |'\
                       '{grep_path} -Pv "{filter_1}" | '\
                       '{grep_path} -Pv "{filter_2}"'.format(
                            grep_path=grep_path,
                            pattern=CATCH_ALL_PATTERN,
                            directory=notes_directory,
                            filter_1=VALID_INCOMPLETE_PATTERN,
                            filter_2=VALID_COMPLETE_PATTERN)

        log.debug(f'running grep command "{grep_command}" '
                  f'to get todos to stamp')

        proc = Popen(grep_command,
                     stdout=PIPE, stderr=PIPE,
                     shell=True)
        output, err = proc.communicate()

        output_lines = output.decode().split('\n')
        matched_filenames = [line.split(':')[0] for line in output_lines
                             if line.strip()]
        matched_filenames = list(set(matched_filenames))
        if matched_filenames:
            log.info(f'Found unstamped todos in files '
                     f'{", ".join(matched_filenames)}')

        # Compile regexes for replacing lines
        unfinished_unstamped_regex = re.compile(
            UNFINISHED_UNSTAMPED_PATTERN)
        finished_start_stamped_regex = re.compile(
            FINISHED_START_STAMPED_PATTERN)
        finished_unstamped_regex = re.compile(
            FINISHED_UNSTAMPED_PATTERN)

        for filename in matched_filenames:
            log.debug(f'Stamping todos in file {filename}')
            with open(filename, 'r') as file_object:

                stamped_content = []

                for line_number, line in enumerate(file_object):

                    if unfinished_unstamped_regex.match(line):
                        # unfinished unstamped
                        log.info(f'Found unstamped unfinished todo "{line}"')
                        new_line = unfinished_unstamped_regex.sub(
                            '\\g<1>[ ] ({timestamp}) '.format(
                                timestamp=datetime.now().isoformat()[:10]),
                            line)
                        log.info(f'Writing stamped unfinished '
                                 f'todo "{new_line.rstrip()}"')
                        stamped_content.append(new_line)

                        change_details = {
                            "type": "incomplete_todo",
                            "line_number": line_number + 1,
                            "before": line.rstrip(),
                            "after": new_line.rstrip(),
                        }
                        changes.setdefault(filename, [])
                        changes[filename].append(change_details)

                    elif finished_start_stamped_regex.match(line):
                        # finished with start stamped
                        log.info(f'Found unstamped finished todo "{line}"')
                        new_line = finished_start_stamped_regex.sub(
                            '\\g<1>[\\g<3>] (\\g<6> -> {timestamp_2}) '.format(
                                timestamp_2=datetime.now().isoformat()[:10]),
                            line)
                        log.info(f'Writing stamped finished '
                                 f'todo "{new_line.rstrip()}"')
                        stamped_content.append(new_line)

                        change_details = {
                            "type": "finished_todo",
                            "line_number": line_number + 1,
                            "before": line.rstrip(),
                            "after": new_line.rstrip(),
                        }
                        changes.setdefault(filename, [])
                        changes[filename].append(change_details)

                    elif finished_unstamped_regex.match(line):
                        # finished unstamped
                        log.info(f'Found unstamped finished todo "{line}"')
                        new_line = finished_unstamped_regex.sub(
                            '\\g<1>[\\g<3>] ({timestamp}'
                            ' -> {timestamp}) '.format(
                                timestamp=datetime.now().isoformat()[:10]),
                            line)
                        log.info(f'Writing stamped finished '
                                 f'todo "{new_line.rstrip()}"')
                        stamped_content.append(new_line)

                        change_details = {
                            "type": "finished_todo",
                            "line_number": line_number + 1,
                            "before": line.rstrip(),
                            "after": new_line.rstrip(),
                        }
                        changes.setdefault(filename, [])
                        changes[filename].append(change_details)

                    else:
                        # no to-dos -or- correctly formatted already
                        stamped_content.append(line)

            with open(filename, 'w') as write_file_object:
                log.debug(f'Saving changes in file {filename}')
                write_file_object.write(''.join(stamped_content))

    # Replace placeholders for `\today` helper
    if stamp_today:
        today_grep_command = '{grep_path} -r {pattern} --include="*.note" ' \
                             '--exclude-dir=\'.*\' {directory}'.format(
                                grep_path=grep_path,
                                pattern=TODAY_GREP,
                                directory=notes_directory)

        log.debug(f'running grep command "{grep_command}" '
                  f'to get `\\today`s to replace')
        today_proc = Popen(today_grep_command,
                           stdout=PIPE, stderr=PIPE,
                           shell=True)
        today_output, err = today_proc.communicate()

        today_output_lines = today_output.decode().split('\n')
        today_matched_filenames = [line.split(':')[0]
                                   for line in today_output_lines
                                   if line.strip()]
        today_matched_filenames = list(set(today_matched_filenames))

        today_placeholder_regex = re.compile(TODAY_LINE_PATTERN)

        for filename in today_matched_filenames:
            log.debug(f'Replacing today placeholder in {filename}')
            with open(filename, 'r') as file_object:

                stamped_content = []

                for line_number, line in enumerate(file_object):

                    if today_placeholder_regex.match(line):
                        # Today placeholder
                        log.info(f'Found today placeholder "{line}"')
                        new_line = today_placeholder_regex.sub(
                            '\\g<1>{timestamp}\\g<3>'.format(
                                timestamp=datetime.now().isoformat()[:10]),
                            line)
                        log.info(f'Replaced today placeholder '
                                 f'"{new_line.rstrip()}"')
                        stamped_content.append(new_line)

                        change_details = {
                            "type": "date_placeholder",
                            "line_number": line_number + 1,
                            "before": line.rstrip(),
                            "after": new_line.rstrip(),
                        }
                        changes.setdefault(filename, [])
                        changes[filename].append(change_details)

                    else:
                        # no today placeholders
                        stamped_content.append(line)

            with open(filename, 'w') as write_file_object:
                log.debug(f'Saving changes in file {filename}')
                write_file_object.write(''.join(stamped_content))

    # Stamp Questions
    if stamp_questions:

        unstamped_questions_grep_command = '{grep_path} -Pr '\
                        '"{question_pattern}" --include="*.note" '\
                        '--exclude-dir=\'.*\' {directory} | {grep_path} -Pv '\
                        '"{stamped_question_pattern}"'.format(
                            grep_path=grep_path,
                            question_pattern=ALL_QUESTIONS,
                            stamped_question_pattern=STAMPED_QUESTION,
                            directory=notes_directory)

        log.debug(f'running grep command "{unstamped_questions_grep_command}" '
                  f'to get unstamped questions')
        questions_proc = Popen(unstamped_questions_grep_command,
                               stdout=PIPE, stderr=PIPE,
                               shell=True)

        questions_output, err = questions_proc.communicate()
        questions_output_lines = questions_output.decode().split('\n')
        questions_matched_filenames = [line.split(':')[0]
                                       for line in questions_output_lines
                                       if line.strip()]
        questions_matched_filenames = list(set(questions_matched_filenames))

        unstamped_question_regex = re.compile(UNSTAMPED_QUESTION)

        for filename in questions_matched_filenames:
            log.info(f'Stamping questions in {filename}')
            with open(filename, 'r') as file_object:

                stamped_content = []

                for line_number, line in enumerate(file_object):

                    if unstamped_question_regex.match(line):
                        # unstamped question
                        log.info(f'Found unstamped question "{line}"')
                        new_line = unstamped_question_regex.sub(
                            '\\g<1>? ({timestamp}) '.format(
                                timestamp=datetime.now().isoformat()[:10]),
                            line)
                        log.info(f'Writing stamped question '
                                 f'"{new_line.rstrip()}"')
                        stamped_content.append(new_line)

                        change_details = {
                            "type": "question",
                            "line_number": line_number + 1,
                            "before": line.rstrip(),
                            "after": new_line.rstrip(),
                        }
                        changes.setdefault(filename, [])
                        changes[filename].append(change_details)

                    else:
                        # no today placeholders
                        stamped_content.append(line)

            with open(filename, 'w') as write_file_object:
                log.debug(f'Saving changes in file {filename}')
                write_file_object.write(''.join(stamped_content))

    # Stamp Answers
    if stamp_answers:

        unstamped_answers_grep_command = '{grep_path} -Pr "{answer_pattern}" '\
                        '--include="*.note" --exclude-dir=\'.*\' '\
                        '{directory} | '\
                        '{grep_path} -Pv "{stamped_answer_pattern}"'.format(
                            grep_path=grep_path,
                            answer_pattern=ANSWER_PATTERN,
                            stamped_answer_pattern=STAMPED_ANSWER,
                            directory=notes_directory)

        log.debug(f'running grep command "{unstamped_answers_grep_command}" '
                  f'to get unstamped answers')
        answers_proc = Popen(unstamped_answers_grep_command,
                             stdout=PIPE, stderr=PIPE,
                             shell=True)

        answers_output, err = answers_proc.communicate()
        answers_output_lines = answers_output.decode().split('\n')
        answers_matched_filenames = [line.split(':')[0]
                                     for line in answers_output_lines
                                     if line.strip()]
        answers_matched_filenames = list(set(answers_matched_filenames))

        unstamped_answer_regex = re.compile(UNSTAMPED_ANSWER)

        for filename in answers_matched_filenames:
            log.info(f'Stamping answers in {filename}')
            with open(filename, 'r') as file_object:

                stamped_content = []

                for line_number, line in enumerate(file_object):

                    if unstamped_answer_regex.match(line):
                        # unstamped answer
                        log.info(f'Found unstamped answer "{line}"')
                        new_line = unstamped_answer_regex.sub(
                            '\\g<1>@ ({timestamp}) '.format(
                                timestamp=datetime.now().isoformat()[:10]),
                            line)
                        log.info(f'Writing stamped answer '
                                 f'"{new_line.rstrip()}"')
                        stamped_content.append(new_line)

                        change_details = {
                            "type": "answer",
                            "line_number": line_number + 1,
                            "before": line.rstrip(),
                            "after": new_line.rstrip(),
                        }
                        changes.setdefault(filename, [])
                        changes[filename].append(change_details)

                    else:
                        # no today placeholders
                        stamped_content.append(line)

            with open(filename, 'w') as write_file_object:
                log.debug(f'Saving changes in file {filename}')
                write_file_object.write(''.join(stamped_content))

    return changes
