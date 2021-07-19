'''
A model to use for testing shorthand functionality
This model works by computing _expected_ results for test runs
    which can then be compared to the results returned by the system
This model relies on the raw structured elements in the file
`results_unstamped.py`
'''

import os
import shlex
import copy
from datetime import datetime

from shorthand.utils.paths import get_display_path, get_full_path

from results_unstamped import ALL_INCOMPLETE_TODOS, ALL_SKIPPED_TODOS, \
                              ALL_COMPLETE_TODOS, ALL_QUESTIONS, ALL_LINKS


class ShorthandModel(object):
    """The shorthand model base class"""

    def __init__(self):
        super(ShorthandModel, self).__init__()

    def search_todos(self, notes_directory=None, todo_status='incomplete',
                     directory_filter=None, query_string=None,
                     case_sensitive=False, sort_by=None,
                     suppress_future=False, stamp=False, tag=None):

        # Get base todos
        if todo_status == 'incomplete':
            todos = copy.deepcopy(ALL_INCOMPLETE_TODOS['items'])
        elif todo_status == 'skipped':
            todos = copy.deepcopy(ALL_SKIPPED_TODOS['items'])
        elif todo_status == 'complete':
            todos = copy.deepcopy(ALL_COMPLETE_TODOS['items'])
        else:
            raise ValueError('Invalid todo status ' + todo_status)

        # Apply directory filter
        if directory_filter:
            filtered_todos = []
            for todo in todos:
                if directory_filter in todo['file_path']:
                    filtered_todos.append(todo)
            todos = filtered_todos

        # Apply query string
        if query_string:
            components = shlex.split(query_string)
            filtered_todos = []
            for todo in todos:
                if not case_sensitive:
                    if all([component.lower() in todo['todo_text'].lower()
                            for component in components]):
                        filtered_todos.append(todo)
                else:
                    if all([component in todo['todo_text']
                            for component in components]):
                        filtered_todos.append(todo)
            todos = filtered_todos

        # Apply sort
        if sort_by:
            todos = sorted(todos,
                           key=lambda k: k[sort_by] if k[sort_by] else '',
                           reverse=True)

        # Apply suppress future
        if suppress_future:
            filtered_todos = []
            for todo in todos:
                if todo['start_date']:
                    if todo['start_date'] > datetime.now().isoformat()[:10]:
                        continue
                filtered_todos.append(todo)
            todos = filtered_todos

        # Emulate Stamping
        if stamp:
            for todo in todos:
                if not todo['start_date']:
                    todo['start_date'] = datetime.now().isoformat()[:10]
                if todo_status in ['skipped', 'complete']:
                    if not todo['end_date']:
                        todo['end_date'] = datetime.now().isoformat()[:10]

        # Add display path
        for todo in todos:
            todo['display_path'] = get_display_path(todo['file_path'],
                                                    directory_filter)

        # Tag Filtering
        if tag:
            todos = [todo for todo in todos
                     if tag in todo['tags']]

        # Sort tags
        for todo in todos:
            todo['tags'].sort()

        return todos

    def search_questions(self, question_status='all', directory_filter=None,
                         stamp=False):

        # Filter on question status
        questions = ALL_QUESTIONS['items']
        if question_status == 'all':
            pass
        elif question_status == 'answered':
            filtered_questions = []
            for question in questions:
                if question['answer']:
                    filtered_questions.append(question)
            questions = filtered_questions
        elif question_status == 'unanswered':
            filtered_questions = []
            for question in questions:
                if not question['answer']:
                    filtered_questions.append(question)
            questions = filtered_questions
        else:
            raise ValueError('Invalid question status ' + question_status)

        # Apply directory filter
        if directory_filter:
            filtered_questions = []
            for question in questions:
                if directory_filter in question['file_path']:
                    filtered_questions.append(question)
            questions = filtered_questions

        # Add display path
        for question in questions:
            question['display_path'] = get_display_path(question['file_path'],
                                                        directory_filter)

        # Emulate Stamping
        if stamp:
            for question in questions:
                if not question['question_date']:
                    question['question_date'] = datetime.now().isoformat()[:10]
                if question['answer']:
                    if not question['answer_date']:
                        question['answer_date'] = datetime.now().isoformat()[:10]

        return questions

    def get_links(self, notes_directory, source=None, target=None, note=None,
                  include_external=False, include_invalid=False, flatten=True,
                  grep_path=None):

        links = ALL_LINKS

        # Filter for source
        if source:
            links = [link for link in links
                     if link['source'] == source]

        # Filter for target
        if target:
            links = [link for link in links
                     if link['target'].split('#')[0] == target]

        # Filter for note
        if note:
            links = [link for link in links
                     if link['target'].split('#')[0] == note
                     or link['source'] == note]

        # Filter for internal only vs. external
        if not include_external:
            links = [link for link in links if link['target'][0] == '/']

        # Split into valid and invalid links
        split_links = {'valid': [], 'invalid': []}
        for link in links:
            target_exists = os.path.exists(get_full_path(notes_directory,
                                           link['target'].split('#')[0]))
            if link['target'][0] != '/' or target_exists:
                split_links['valid'].append(link)
            else:
                split_links['invalid'].append(link)
        links = split_links

        # Filter for valid internal targets
        if not include_invalid:
            del links['invalid']

        # Flatten Links if needed
        if flatten:
            links = links['valid'] + links.get('invalid', [])

        return links

    def get_backlinks(self, notes_directory, note_path, grep_path='grep'):
        return self.get_links(notes_directory=notes_directory,
                              target=note_path, include_external=False,
                              include_invalid=False, grep_path=grep_path)
