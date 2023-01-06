import logging
import unittest
from datetime import datetime

from shorthand.elements.todos import _get_todos
from shorthand.elements.questions import _get_questions
from shorthand.stamping import _stamp_notes, _stamp_raw_note
from shorthand.notes import _get_note

from utils import setup_environment, teardown_environment, validate_setup, \
                  setup_logging
from model import ShorthandModel


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)
MODEL = ShorthandModel()


class TestStamping(unittest.TestCase):
    """Test stamping functionality"""

    @classmethod
    def setup_class(self):
        '''ensure that we have a clean environment
        before running any tests
        '''
        _ = setup_environment()
        response = _stamp_notes(CONFIG['notes_directory'],
                                stamp_todos=True, stamp_today=True,
                                stamp_questions=True, stamp_answers=True,
                                grep_path=CONFIG['grep_path'])
        assert response.keys()

    @classmethod
    def teardown_class(self):
        '''Ensure that we don't leave stamped
        notes around after the tests are run
        '''
        teardown_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_todos_stamped(self):
        incomplete_todos = _get_todos(
            notes_directory=CONFIG['notes_directory'],
            todo_status='incomplete',
            grep_path=CONFIG['grep_path'])

        for todo in incomplete_todos:
            assert todo.get('start_date')
            assert not todo.get('end_date')

        complete_todos = _get_todos(
            notes_directory=CONFIG['notes_directory'],
            todo_status='complete',
            grep_path=CONFIG['grep_path'])
        skipped_todos = _get_todos(
            notes_directory=CONFIG['notes_directory'],
            todo_status='skipped',
            grep_path=CONFIG['grep_path'])

        for todo in complete_todos + skipped_todos:
            assert todo.get('start_date')
            assert todo.get('end_date')

    def test_today_replaced(self):
        sample_note_path = CONFIG['notes_directory'] + '/todos.note'
        content = _get_note(CONFIG['notes_directory'], sample_note_path)
        assert '\\today' not in content

    def test_questions_stamped(self):

        unanswered_qs = _get_questions(
            notes_directory=CONFIG['notes_directory'],
            question_status='unanswered',
            grep_path=CONFIG['grep_path'])

        for question in unanswered_qs:
            assert question.get('question_date')
            assert not question.get('answer_date')

        answered_qs = _get_questions(
            notes_directory=CONFIG['notes_directory'],
            question_status='answered',
            grep_path=CONFIG['grep_path'])

        for question in answered_qs:
            assert question.get('question_date')
            assert question.get('answer_date')

    def test_restamp(self):
        changes = _stamp_notes(CONFIG['notes_directory'],
                               stamp_todos=True, stamp_today=True,
                               stamp_questions=True, stamp_answers=True,
                               grep_path=CONFIG['grep_path'])
        assert not changes

    def test_stamp_raw_note(self):
        unstamped_note = \
'''# Test Raw Note \\today
- [] An unstamped Todo :tag:
    + ? A question
        * @ An Answer
- [X] A completed Todo
Some text to keep'''
        stamped_note = _stamp_raw_note(unstamped_note)
        assert stamped_note == \
'''# Test Raw Note {date}
- [ ] ({date}) An unstamped Todo :tag:
    + ? ({date}) A question
        * @ ({date}) An Answer
- [X] ({date} -> {date}) A completed Todo
Some text to keep'''.format(date=datetime.now().isoformat()[:10])
