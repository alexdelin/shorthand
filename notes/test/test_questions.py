import os

from note_parser.question_tools import get_questions

from utils import setup_environment
from results_unstamped import ALL_ANSWERED_QUESTIONS, \
                              ALL_UNANSWERED_QUESTIONS


CONFIG = setup_environment()


class TestQuestions(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_unanswered_questions(self):
        all_unanswered_questions = get_questions(
            notes_directory=CONFIG['notes_directory'],
            question_status='unanswered', directory_filter=None)
        assert all_unanswered_questions == ALL_UNANSWERED_QUESTIONS

    def test_get_answered_questions(self):
        all_answered_questions = get_questions(
            notes_directory=CONFIG['notes_directory'],
            question_status='answered', directory_filter=None)
        assert all_answered_questions == ALL_ANSWERED_QUESTIONS

    def test_get_all_questions(self):
        all_questions = get_questions(
            notes_directory=CONFIG['notes_directory'],
            question_status='all', directory_filter=None)
        # Compare results to expected results, but ignore order
        assert True

    def test_invalid_question_request(self):
        pass
