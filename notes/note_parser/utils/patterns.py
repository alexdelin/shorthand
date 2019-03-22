CATCH_ALL_PATTERN = r'"\(^\\s*\)\(\[ \]\|\[\]\|\[X\]\|\[S\]\)"'
VALID_INCOMPLETE_PATTERN = r'"\[ \] ([1-2]\\d\{3\}-\\d\{2\}-\\d\{2\})"'
VALID_COMPLETE_PATTERN = r'"\[[XS]\] ([1-2]\\d\{3\}-\\d\{2\}-\\d\{2\} -> [1-2]\\d\{3\}-\\d\{2\}-\\d\{2\})"'

UNFINISHED_UNSTAMPED_PATTERN = r'(^\s*)(\[ \]|\[\]) (?!\([1-2]\d{3}\-\d{2}\-\d{2}\))'
FINISHED_START_STAMPED_PATTERN = r'(^\s*)(\[)([XS])(\] )(\()([1-2]\d{3}\-\d{2}\-\d{2})(\)) '
FINISHED_UNSTAMPED_PATTERN = r'(^\s*)(\[)([XS])(\] )(?!(\([1-2]\d{3}\-\d{2}\-\d{2}\)|\([1-2]\d{3}\-\d{2}\-\d{2} -> [1-2]\d{3}\-\d{2}\-\d{2}\)))'

SKIPPED_PREFIX_GREP = r'"\(^\\s*\)\(\[S\]\)"'
INCOMPLETE_PREFIX_GREP = r'"\(^\\s*\)\(\[ \]\|\[\]\)"'
COMPLETE_PREFIX_GREP = r'"\(^\\s*\)\(\[X\]\)"'


def escape_for_grep(input_pattern):
    pass
