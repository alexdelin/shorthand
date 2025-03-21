import logging

from shorthand.elements.questions import _get_questions
from shorthand.stamping import _stamp_notes

from utils import ShorthandTestCase, setup_environment
from model import ShorthandModel


log = logging.getLogger(__name__)
MODEL = ShorthandModel()


class TestQuestions(ShorthandTestCase, reset_per_method=False):
    """Test basic search functionality of the library"""

    def get_question_results(self, question_status='all', directory_filter=None, stamp=False):
        return _get_questions(notes_directory=self.notes_dir,
                              question_status=question_status,
                              directory_filter=directory_filter,
                              grep_path=self.grep_path)

    def test_get_unanswered_questions(self):

        args = {
            'question_status': 'unanswered',
        }
        library_results = self.get_question_results(**args)
        model_results = MODEL.search_questions(**args)
        # Some extra tests to make debugging easier
        assert set(library_results[0].keys()) == set(model_results[0].keys())
        assert len(library_results) == len(model_results)
        self.assertCountEqual(library_results, model_results)

        args = {
            'question_status': 'unanswered',
            'directory_filter': 'section'
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))

    def test_get_answered_questions(self):

        args = {
            'question_status': 'answered'
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))

        args = {
            'question_status': 'answered',
            'directory_filter': 'section'
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))

    def test_get_all_questions(self):

        args = {
            'question_status': 'all'
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))

        args = {
            'question_status': 'all',
            'directory_filter': 'section'
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))


class TestStampedQuestions(ShorthandTestCase, reset_per_method=False, stamp=True):
    """Test that questions are stamped as expected"""

    maxDiff = None

    def get_question_results(self, question_status='all', directory_filter=None, stamp=False):
        return _get_questions(notes_directory=self.notes_dir,
                              question_status=question_status,
                              directory_filter=directory_filter,
                              grep_path=self.grep_path)

    def test_get_unanswered_questions(self):

        args = {
            'question_status': 'unanswered',
            'stamp': True
        }
        library_results = self.get_question_results(**args)
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
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))

    def test_get_answered_questions(self):

        args = {
            'question_status': 'answered',
            'stamp': True
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))

        args = {
            'question_status': 'answered',
            'directory_filter': 'section',
            'stamp': True
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))

    def test_get_all_questions(self):

        args = {
            'question_status': 'all',
            'stamp': True
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))

        args = {
            'question_status': 'all',
            'directory_filter': 'section',
            'stamp': True
        }
        self.assertCountEqual(self.get_question_results(**args),
                              MODEL.search_questions(**args))
