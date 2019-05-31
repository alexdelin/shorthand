import os

from note_parser.question_tools import get_questions

from utils import setup_environment


CONFIG = setup_environment()


class TestQuestions(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_all_questions(self):
        pass

    def test_get_unanswered_questions(self):
        pass

    def test_get_answered_questions(self):
        pass

    def test_invalid_question_request(self):
        pass
