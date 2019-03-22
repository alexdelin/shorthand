import re
from datetime import datetime
from subprocess import Popen, PIPE
from note_parser.utils.patterns import CATCH_ALL_PATTERN, \
        VALID_INCOMPLETE_PATTERN, VALID_COMPLETE_PATTERN, \
        UNFINISHED_UNSTAMPED_PATTERN, FINISHED_START_STAMPED_PATTERN, \
        FINISHED_UNSTAMPED_PATTERN


