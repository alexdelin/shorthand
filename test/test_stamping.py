import logging
import unittest
from datetime import datetime

from shorthand.elements.todos import _get_todos
from shorthand.elements.questions import _get_questions
from shorthand.stamping import _stamp_notes, _stamp_raw_note
from shorthand.notes import _get_note

from utils import setup_environment, teardown_environment, validate_setup
from model import ShorthandModel


log = logging.getLogger(__name__)
MODEL = ShorthandModel()


class TestStamping(unittest.TestCase):
    """Test stamping functionality"""

    @classmethod
    def setup_class(cls):
        '''ensure that we have a clean environment
        before running any tests
        '''
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']

        # Stamp notes before running tests
        response = _stamp_notes(cls.notes_dir,
                                stamp_todos=True, stamp_today=True,
                                stamp_questions=True, stamp_answers=True,
                                grep_path=cls.grep_path)
        assert response.keys()

    @classmethod
    def teardown_class(cls):
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
            notes_directory=self.notes_dir,
            todo_status='incomplete',
            grep_path=self.grep_path)

        for todo in incomplete_todos:
            assert todo.get('start_date')
            assert not todo.get('end_date')

        complete_todos = _get_todos(
            notes_directory=self.notes_dir,
            todo_status='complete',
            grep_path=self.grep_path)
        skipped_todos = _get_todos(
            notes_directory=self.notes_dir,
            todo_status='skipped',
            grep_path=self.grep_path)

        for todo in complete_todos + skipped_todos:
            assert todo.get('start_date')
            assert todo.get('end_date')

    def test_today_replaced(self):
        sample_note_path = self.notes_dir + '/todos.note'
        content = _get_note(self.notes_dir, sample_note_path)
        assert '\\today' not in content

    def test_questions_stamped(self):

        unanswered_qs = _get_questions(
            notes_directory=self.notes_dir,
            question_status='unanswered',
            grep_path=self.grep_path)

        for question in unanswered_qs:
            assert question.get('question_date')
            assert not question.get('answer_date')

        answered_qs = _get_questions(
            notes_directory=self.notes_dir,
            question_status='answered',
            grep_path=self.grep_path)

        for question in answered_qs:
            assert question.get('question_date')
            assert question.get('answer_date')

    def test_restamp(self):
        changes = _stamp_notes(self.notes_dir,
                               stamp_todos=True, stamp_today=True,
                               stamp_questions=True, stamp_answers=True,
                               grep_path=self.grep_path)
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
