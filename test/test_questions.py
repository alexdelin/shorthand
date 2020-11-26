import os
import logging
import unittest

from shorthand.utils.logging import setup_logging
from shorthand.question_tools import get_questions

from utils import setup_environment
from model import ShorthandModel


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)
MODEL = ShorthandModel()


# Helper function to simplify tests
def get_question_results(question_status='all', directory_filter=None):
    return get_questions(notes_directory=CONFIG['notes_directory'],
                         question_status=question_status,
                         directory_filter=directory_filter,
                         grep_path=CONFIG['grep_path'])


class TestQuestions(unittest.TestCase):
    """Test basic search functionality of the library"""

    maxDiff = None

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

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
