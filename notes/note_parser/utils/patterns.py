'''
Regular Expression Library used by Noteparser.
Patterns that begin with `"` characters are meant to be used with `grep`
via the command line
'''

CATCH_ALL_PATTERN = r'"\(^\\s*\)\(\[ \]\|\[\]\|\[X\]\|\[S\]\)"'
VALID_INCOMPLETE_PATTERN = r'"\[ \] ([1-2]\\d\{3\}-\\d\{2\}-\\d\{2\})"'
VALID_COMPLETE_PATTERN = r'"\[[XS]\] ([1-2]\\d\{3\}-\\d\{2\}-\\d\{2\} -> [1-2]\\d\{3\}-\\d\{2\}-\\d\{2\})"'

UNFINISHED_UNSTAMPED_PATTERN = r'(^\s*)(\[ ?\]) (?!\([1-2]\d{3}\-\d{2}\-\d{2}\))'
FINISHED_START_STAMPED_PATTERN = r'(^\s*)(\[)([XS])(\] )(\()([1-2]\d{3}\-\d{2}\-\d{2})(\)) '
FINISHED_UNSTAMPED_PATTERN = r'(^\s*)(\[)([XS])(\] )(?!(\([1-2]\d{3}\-\d{2}\-\d{2}\)|\([1-2]\d{3}\-\d{2}\-\d{2} -> [1-2]\d{3}\-\d{2}\-\d{2}\)))'

SKIPPED_PREFIX_GREP = r'"\(^\\s*\)\(\[S\]\)"'
INCOMPLETE_PREFIX_GREP = r'"\(^\\s*\)\(\[ \]\|\[\]\)"'
COMPLETE_PREFIX_GREP = r'"\(^\\s*\)\(\[X\]\)"'

START_STAMP_ONLY_PATTERN = r'(\()([1-2]\d{3}\-\d{2}\-\d{2})(\))( )(.*)'
START_END_STAMP_ONLY_PATTERN = r'(\()([1-2]\d{3}\-\d{2}\-\d{2})( -> )([1-2]\d{3}\-\d{2}\-\d{2})(\))( )(.*)'

ALL_QUESTIONS_GREP = r'"\(^\\s*\)\(\?\)"'
ANSWER_PATTERN = r'(^\s*)(@ )(.*)'

TODAY_GREP = r'"\\\today"'
TODAY_LINE_PATTERN = r'(.*)(\\today)(.*)'

TAG_PATTERN = r':\w*:'

def escape_for_grep(input_pattern):
    pass
