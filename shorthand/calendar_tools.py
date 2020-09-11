import re
import logging
from subprocess import Popen, PIPE

from shorthand.todo_tools import get_todos
from shorthand.question_tools import get_questions
from shorthand.utils.patterns import DATED_HEADING_PATTERN


dated_heading_regex = re.compile(DATED_HEADING_PATTERN)


log = logging.getLogger(__name__)


def get_calendar(notes_directory, directory_filter=None, grep_path='grep'):

    events = []
    calendar = {}

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = '{grep_path} -Prn "{pattern}" '\
                   '--include="*.note" {dir}'.format(
                        grep_path=grep_path,
                        pattern=DATED_HEADING_PATTERN,
                        dir=search_directory)

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    # Create events from parsed headings
    for line in output_lines:

        if not line.strip():
            continue

        split_line = line.split(':', 2)
        file_path = split_line[0]
        line_number = split_line[1]
        heading_raw = split_line[2]

        heading_match = dated_heading_regex.match(heading_raw)
        if not heading_match:
            print('NO MATCH FOUND?!?!')
        else:
            heading_text = heading_match.group(3).strip()
            date = heading_match.group(4).strip()

        if notes_directory in file_path:
            file_path = file_path[len(notes_directory):]

        split_heading = heading_raw.split(' ', 1)
        element_id = split_heading[1].replace(' ', '-')

        parsed_heading = {
            "file_path": file_path,
            "line_number": line_number,
            "event": heading_text,
            "date": date,
            "element_id": element_id,
            "type": "section"
        }

        events.append(parsed_heading)

    # Add Incomplet Todos to the calendar view
    completed_todos = get_todos(notes_directory=notes_directory,
                                todo_status='incomplete',
                                directory_filter=directory_filter,
                                query_string=None, grep_path=grep_path)
    for todo in completed_todos:
        parsed_todo = {
            "file_path": todo['file_path'],
            "line_number": todo['line_number'],
            "event": todo['todo_text'],
            "date": todo['start_date'],
            "element_id": "",
            "type": "incomplete_todo"
        }
        events.append(parsed_todo)

    # Add Completed Todos to the calendar view
    completed_todos = get_todos(notes_directory=notes_directory,
                                todo_status='complete',
                                directory_filter=directory_filter,
                                query_string=None, grep_path=grep_path)
    for todo in completed_todos:
        parsed_todo = {
            "file_path": todo['file_path'],
            "line_number": todo['line_number'],
            "event": todo['todo_text'],
            "date": todo['end_date'],
            "element_id": "",
            "type": "completed_todo"
        }
        events.append(parsed_todo)

    # Add Skipped Todos to the calendar view
    skipped_todos = get_todos(notes_directory=notes_directory,
                              todo_status='skipped',
                              directory_filter=directory_filter,
                              query_string=None, grep_path=grep_path)
    for todo in skipped_todos:
        parsed_todo = {
            "file_path": todo['file_path'],
            "line_number": todo['line_number'],
            "event": todo['todo_text'],
            "date": todo['end_date'],
            "element_id": "",
            "type": "skipped_todo"
        }
        events.append(parsed_todo)

    # Add opened questions and answers to calendar view
    questions = get_questions(
        notes_directory=notes_directory,
        question_status='ALL', directory_filter=directory_filter,
        grep_path=grep_path)
    for question in questions:
        if question.get('question_date'):
            parsed_question = {
                "file_path": question['file_path'],
                "line_number": question['line_number'],
                "event": question['question'],
                "date": question['question_date'],
                "element_id": "",
                "type": "question"
            }
            events.append(parsed_question)
        if question.get('answer_date'):
            parsed_answer = {
                "file_path": question['file_path'],
                "line_number": str(int(question['line_number']) + 1),
                "event": question['answer'],
                "date": question['answer_date'],
                "element_id": "",
                "type": "answer"
            }
            events.append(parsed_answer)

    # Create Calendar from events
    for event in events:
        event_date = event['date']
        if not event_date:
            continue

        event_year = event_date[:4]
        event_month = event_date[5:7]
        event_day = event_date[8:]

        calendar.setdefault(event_year, {})
        calendar[event_year].setdefault(event_month, {})
        calendar[event_year][event_month].setdefault(event_day, [])
        calendar[event_year][event_month][event_day].append(event)

    return calendar
