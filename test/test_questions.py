import logging
import unittest

from shorthand.utils.logging import setup_logging
from shorthand.elements.questions import _get_questions
from shorthand.stamping import _stamp_notes

from utils import setup_environment, teardown_environment, validate_setup
from model import ShorthandModel


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)
MODEL = ShorthandModel()


# Helper function to simplify tests
def get_question_results(question_status='all', directory_filter=None,
                         stamp=False):
    return _get_questions(notes_directory=CONFIG['notes_directory'],
                          question_status=question_status,
                          directory_filter=directory_filter,
                          grep_path=CONFIG['grep_path'])


class TestQuestions(unittest.TestCase):
    """Test basic search functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_unanswered_questions(self):

        args = {
            'question_status': 'unanswered'
        }
        library_results = get_question_results(**args)
        model_results = MODEL.search_questions(**args)
        # Some extra tests to make debugging easier
        assert set(library_results[0].keys()) == set(model_results[0].keys())
        assert len(library_results) == len(model_results)
        self.assertCountEqual(library_results, model_results)

        args = {
            'question_status': 'unanswered',
            'directory_filter': 'section'
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))

    def test_get_answered_questions(self):

        args = {
            'question_status': 'answered'
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))

        args = {
            'question_status': 'answered',
            'directory_filter': 'section'
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))

    def test_get_all_questions(self):

        args = {
            'question_status': 'all'
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))

        args = {
            'question_status': 'all',
            'directory_filter': 'section'
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))


class TestStampedQuestions(unittest.TestCase):
    """Test that questions are stamped as expected"""

    maxDiff = None

    @classmethod
    def setup_class(cls):
        '''ensure that we have a clean environment
        before running any tests
        '''
        _ = setup_environment()
        _ = _stamp_notes(CONFIG['notes_directory'],
                         stamp_todos=False, stamp_today=False,
                         stamp_questions=True, stamp_answers=True,
                         grep_path=CONFIG['grep_path'])

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

    def test_get_unanswered_questions(self):

        args = {
            'question_status': 'unanswered',
            'stamp': True
        }
        library_results = get_question_results(**args)
        model_results = MODEL.search_questions(**args)
        # Some extra tests to make debugging easier
        assert set(library_results[0].keys()) == set(model_results[0].keys())
        assert len(library_results) == len(model_results)
        self.assertCountEqual(library_results, model_results)

        args = {
            'question_status': 'unanswered',
            'directory_filter': 'section',
            'stamp': True
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))

    def test_get_answered_questions(self):

        args = {
            'question_status': 'answered',
            'stamp': True
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))

        args = {
            'question_status': 'answered',
            'directory_filter': 'section',
            'stamp': True
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))

    def test_get_all_questions(self):

        args = {
            'question_status': 'all',
            'stamp': True
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))

        args = {
            'question_status': 'all',
            'directory_filter': 'section',
            'stamp': True
        }
        self.assertCountEqual(get_question_results(**args),
                              MODEL.search_questions(**args))
