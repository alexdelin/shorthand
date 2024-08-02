from enum import StrEnum
import re
import logging
from subprocess import Popen, PIPE
from typing import Dict, List, Optional, Required, TypedDict
from datetime import datetime

from shorthand.elements.todos import _get_todos
from shorthand.elements.questions import _get_questions
from shorthand.types import DirectoryPath, ExecutablePath, RelativeDirectoryPath
from shorthand.utils.patterns import DATED_HEADING_PATTERN


dated_heading_regex = re.compile(DATED_HEADING_PATTERN)


log = logging.getLogger(__name__)


class CalendarMode(StrEnum):
    Creation = 'creation'
    Closing = 'closing'
    Recent = 'recent'
    WIP = 'wip'

class CalendarEvent(TypedDict, total=False):
    file_path: Required[str]
    line_number: Required[str]
    event: Required[str]
    date: Required[str]
    start: str
    end: str
    element_id: Required[str]
    type: Required[str]

YearIndex = str
MonthIndex = str
DayIndex = str
Calendar = Dict[YearIndex, Dict[MonthIndex, Dict[DayIndex, List[CalendarEvent]]]]


def _get_calendar(notes_directory: DirectoryPath,
                  mode: CalendarMode = CalendarMode.Recent,
                  directory_filter: Optional[RelativeDirectoryPath] = None,
                  grep_path: ExecutablePath = 'grep') -> Calendar:

    todays_date = datetime.now().isoformat()[:10]
    events: List[CalendarEvent] = []
    calendar = {}

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = ('{grep_path} -Prn "{pattern}" ' \
                   '--include="*.note" --exclude-dir=\'.*\' {dir}').format(
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
        heading_text, date = None, None
        if heading_match:
            heading_text = heading_match.group(3).strip()
            date = heading_match.group(4).strip()
        else:
            raise ValueError(f'Line {heading_raw} returned by grep did not match dated heading pattern')

        if notes_directory in file_path:
            file_path = file_path[len(notes_directory):]

        split_heading = heading_raw.split(' ', 1)
        element_id = split_heading[1].replace(' ', '-')

        parsed_heading: CalendarEvent = {
            "file_path": file_path,
            "line_number": line_number,
            "event": heading_text,
            "date": date,
            "element_id": element_id,
            "type": "section"
        }

        events.append(parsed_heading)

    # Add Incomplete Todos to the calendar view
    incomplete_todos = _get_todos(notes_directory=notes_directory,
                                 todo_status='incomplete',
                                 directory_filter=directory_filter,
                                 query_string=None, grep_path=grep_path)
    for todo in incomplete_todos:
        if todo['start_date']:
            parsed_todo: CalendarEvent = {
                "file_path": todo['file_path'],
                "line_number": todo['line_number'],
                "event": todo['todo_text'],
                "date": todo['start_date'],
                "element_id": "",
                "type": "incomplete_todo"
            }

            if mode == CalendarMode.Closing:
                break
            elif mode == CalendarMode.WIP:
                parsed_todo['start'] = todo['start_date']
                parsed_todo['end'] = todays_date
            events.append(parsed_todo)

    # Add Completed Todos to the calendar view
    completed_todos = _get_todos(notes_directory=notes_directory,
                                 todo_status='complete',
                                 directory_filter=directory_filter,
                                 query_string=None, grep_path=grep_path)
    for todo in completed_todos:
        parsed_todo: CalendarEvent = {
            "file_path": todo['file_path'],
            "line_number": todo['line_number'],
            "event": todo['todo_text'],
            "date": "",
            "element_id": "",
            "type": "completed_todo"
        }
        if mode == CalendarMode.Creation and todo['start_date']:
            parsed_todo['date'] = todo['start_date']
        elif mode == CalendarMode.Closing and todo['end_date']:
            parsed_todo['date'] = todo['end_date']
        elif mode == CalendarMode.Recent and todo['end_date']:
            parsed_todo['date'] = todo['end_date']
        elif mode == CalendarMode.WIP and todo['start_date'] and todo['end_date']:
            parsed_todo['date'] = todo['start_date']
            parsed_todo['start'] = todo['start_date']
            parsed_todo['end'] = todo['end_date']
        else:
            continue
        events.append(parsed_todo)

    # Add Skipped Todos to the calendar view
    skipped_todos = _get_todos(notes_directory=notes_directory,
                               todo_status='skipped',
                               directory_filter=directory_filter,
                               query_string=None, grep_path=grep_path)
    for todo in skipped_todos:
        parsed_todo: CalendarEvent = {
            "file_path": todo['file_path'],
            "line_number": todo['line_number'],
            "event": todo['todo_text'],
            "date": "",
            "element_id": "",
            "type": "skipped_todo"
        }
        if mode == CalendarMode.Creation and todo['start_date']:
            parsed_todo['date'] = todo['start_date']
        elif mode == CalendarMode.Closing and todo['end_date']:
            parsed_todo['date'] = todo['end_date']
        elif mode == CalendarMode.Recent and todo['end_date']:
            parsed_todo['date'] = todo['end_date']
        elif mode == CalendarMode.WIP and todo['start_date'] and todo['end_date']:
            parsed_todo['date'] = todo['start_date']
            parsed_todo['start'] = todo['start_date']
            parsed_todo['end'] = todo['end_date']
        else:
            continue
        events.append(parsed_todo)

    # Add opened questions and answers to calendar view
    questions = _get_questions(
        notes_directory=notes_directory,
        question_status='all', directory_filter=directory_filter,
        grep_path=grep_path)
    for question in questions:
        parsed_question: CalendarEvent = {
            "file_path": question['file_path'],
            "line_number": question['line_number'],
            "event": question['question'],
            "date": question['question_date'],
            "element_id": "",
            "type": "question"
        }
        parsed_answer: CalendarEvent = {
            "file_path": question['file_path'],
            "line_number": str(int(question['line_number']) + 1),
            "event": question['answer'],
            "date": question['answer_date'],
            "element_id": "",
            "type": "answer"
        }

        if mode == CalendarMode.Creation and question.get('question_date'):
            if question.get('answer_date'):
                parsed_answer['date'] = question['question_date']
                events.append(parsed_answer)
            else:
                events.append(parsed_question)

        elif mode == CalendarMode.Closing and question.get('answer_date'):
            events.append(parsed_answer)

        elif mode == CalendarMode.Recent:
            if question.get('answer_date'):
                events.append(parsed_answer)
            else:
                events.append(parsed_question)

        elif mode == CalendarMode.WIP:
            if question.get('question_date'):
                if question.get('answer_date'):
                    parsed_answer["start"] = question['question_date']
                    parsed_answer["end"] = question['answer_date']
                    events.append(parsed_answer)
                else:
                    parsed_question["start"] = question['question_date']
                    parsed_question["end"] = todays_date
                    events.append(parsed_question)

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
